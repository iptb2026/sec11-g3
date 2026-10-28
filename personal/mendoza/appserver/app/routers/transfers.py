# ==== LAYER 4: Transactions ====
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.audit import add_audit_log, snapshot_model
from app.core.config import settings
from app.core.ref_gen import generate_idempotent_reference, generate_reference
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.account import Account
from app.models.fee_record import FeeRecord
from app.models.fee_type import FeeType
from app.models.ledger_entry import LedgerEntry
from app.models.notification import Notification
from app.models.role import Role
from app.models.transfer import Transfer
from app.models.user import User
from app.schemas.transfer import (
    CustomerTransferAccount,
    RecipientPreview,
    RecipientPreviewRequest,
    TransferCreate,
    TransferOut,
)
from app.routers.notifications import manager, notification_payload

router = APIRouter(prefix="/transfers", tags=["Layer 4 - Transfers"], dependencies=[Depends(get_current_user)])

INTERNAL_TRANSFER_FEE_CODE = "INTERNAL_TRANSFER"
INTERNAL_TRANSFER_FEE_REMARKS = "Customer internal transfer fee"


def _transfer_fee_record_remarks(transfer_reference: str) -> str:
    return f"{INTERNAL_TRANSFER_FEE_REMARKS}: {transfer_reference}"


def _load_internal_transfer_fee(db: Session) -> FeeType:
    fee_type = (
        db.query(FeeType)
        .filter(FeeType.fee_code == INTERNAL_TRANSFER_FEE_CODE)
        .with_for_update()
        .first()
    )
    if not fee_type:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Internal transfer fee is not configured. Ask an administrator to open Fee Types.",
        )
    if Decimal(str(fee_type.percentage_rate or 0)) != Decimal("0.00"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal transfer fee configuration must use a fixed amount.",
        )
    return fee_type


def _fee_reference(db: Session) -> str:
    for _ in range(5):
        reference = generate_reference("FEE")
        if not db.query(FeeRecord).filter(FeeRecord.transaction_reference == reference).first():
            return reference
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate a unique transfer fee reference — please retry.",
    )


def _load_actor(username: str, db: Session) -> tuple[User, str]:
    actor = db.query(User).filter(User.username == username).first()
    if not actor or actor.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active")

    role = db.query(Role).filter(Role.id == actor.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role is not recognized")

    if role.role_code not in {"ADMIN", "STAFF", "CUSTOMER"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Transfers are not available for this role")
    return actor, role.role_code


def _transfer_matches(
    existing: Transfer,
    source_id: int,
    destination_id: int,
    transfer: TransferCreate,
) -> bool:
    return (
        existing.source_account_id == source_id
        and existing.destination_account_id == destination_id
        and existing.amount == transfer.amount
        and (existing.remarks or "") == (transfer.remarks or "")
    )


def _replay_idempotent_transfer(
    existing: Transfer,
    source_id: int,
    destination_id: int,
    transfer: TransferCreate,
    actor: User,
    role_code: str,
    db: Session,
) -> Transfer:
    if role_code == "CUSTOMER":
        source_owner_id = db.query(Account.customer_id).filter(Account.id == source_id).scalar()
        if source_owner_id != actor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Source account does not belong to you")

    if not _transfer_matches(existing, source_id, destination_id, transfer):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This transfer request key was already used for a different request",
        )
    fee_record = (
        db.query(FeeRecord)
        .filter(FeeRecord.remarks == _transfer_fee_record_remarks(existing.transfer_reference))
        .first()
    )
    existing.fee_amount = Decimal(str(fee_record.amount_charged)) if fee_record else Decimal("0.00")
    existing.total_debit = existing.amount + existing.fee_amount
    return existing


@router.get("/customer-accounts", response_model=list[CustomerTransferAccount])
def list_customer_transfer_accounts(
    actor_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    actor, role_code = _load_actor(actor_username, db)
    if role_code != "CUSTOMER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer access required")

    return (
        db.query(Account)
        .filter(Account.customer_id == actor.id, Account.status == "ACTIVE")
        .order_by(Account.id.asc())
        .all()
    )


@router.post("/recipient-preview", response_model=RecipientPreview)
def preview_transfer_recipient(
    data: RecipientPreviewRequest,
    actor_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    actor, role_code = _load_actor(actor_username, db)
    if role_code != "CUSTOMER":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer access required")

    source = (
        db.query(Account)
        .filter(Account.id == data.source_account_id, Account.customer_id == actor.id)
        .first()
    )
    if not source:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Source account does not belong to you")
    if source.status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source account is not active")

    destination = db.query(Account).filter(Account.account_number == data.destination_account_number).first()
    if not destination or destination.status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient account not found or unavailable")
    if source.id == destination.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot transfer to the same account")
    if source.currency_code != destination.currency_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Accounts must use the same currency")
    fee_type = _load_internal_transfer_fee(db)

    recipient = db.query(User).filter(User.id == destination.customer_id).first()
    recipient_role = db.query(Role).filter(Role.id == recipient.role_id).first() if recipient else None
    if (
        not recipient
        or recipient.account_status != "ACTIVE"
        or not recipient_role
        or recipient_role.role_code != "CUSTOMER"
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient account not found or unavailable")

    return RecipientPreview(
        account_number=destination.account_number,
        customer_name=" ".join(filter(None, [recipient.first_name, recipient.middle_name, recipient.last_name])),
        currency_code=destination.currency_code,
        transfer_fee=Decimal(str(fee_type.fixed_amount or 0)),
    )


@router.post("/", response_model=TransferOut, status_code=status.HTTP_201_CREATED)
def create_transfer(
    transfer: TransferCreate,
    request: Request,
    actor_username: str = Depends(get_current_user),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
):
    actor, role_code = _load_actor(actor_username, db)

    if (transfer.destination_account_id is None) == (transfer.destination_account_number is None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide exactly one destination account ID or account number",
        )
    if transfer.destination_account_number == "":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Recipient account number is required")
    if role_code == "CUSTOMER" and (
        not idempotency_key or len(idempotency_key) < 8 or len(idempotency_key) > 128 or any(c.isspace() for c in idempotency_key)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid Idempotency-Key header is required for customer transfers",
        )

    if role_code == "CUSTOMER":
        ref = generate_idempotent_reference("TRF", actor.username, idempotency_key, settings.SECRET_KEY)
    else:
        ref = None

    destination_id = (
        db.query(Account.id).filter(Account.id == transfer.destination_account_id).scalar()
        if transfer.destination_account_id is not None
        else db.query(Account.id).filter(Account.account_number == transfer.destination_account_number).scalar()
    )
    if destination_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Destination account does not exist")

    if transfer.source_account_id == destination_id:
        raise HTTPException(status_code=400, detail="source and destination accounts must be different")

    if ref:
        existing = db.query(Transfer).filter(Transfer.transfer_reference == ref).first()
        if existing:
            return _replay_idempotent_transfer(
                existing, transfer.source_account_id, destination_id, transfer, actor, role_code, db
            )

    # Lock both accounts for the duration of this transaction so a
    # simultaneous transfer touching either one can't read a stale balance.
    # Locking order matters: always lock the lower id first, or two transfers
    # running in opposite directions at the same time (A->B and B->A) could
    # each be waiting on the row the other one is holding — a deadlock.
    first_id, second_id = sorted([transfer.source_account_id, destination_id])
    accounts_by_id = {
        a.id: a
        for a in (
            db.query(Account)
            .filter(Account.id.in_([first_id, second_id]))
            .order_by(Account.id.asc())
            .with_for_update()
            .all()
        )
    }
    source = accounts_by_id.get(transfer.source_account_id)
    destination = accounts_by_id.get(destination_id)

    if not source:
        raise HTTPException(status_code=400, detail="source_account_id does not exist")
    if not destination:
        raise HTTPException(status_code=400, detail="destination_account_id does not exist")

    if role_code == "CUSTOMER" and source.customer_id != actor.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Source account does not belong to you")

    if ref:
        existing = (
            db.query(Transfer)
            .filter(Transfer.transfer_reference == ref)
            .with_for_update()
            .first()
        )
        if existing:
            return _replay_idempotent_transfer(
                existing, source.id, destination.id, transfer, actor, role_code, db
            )

    if role_code == "CUSTOMER":
        recipient = db.query(User).filter(User.id == destination.customer_id).first()
        recipient_role = db.query(Role).filter(Role.id == recipient.role_id).first() if recipient else None
        if (
            not recipient
            or recipient.account_status != "ACTIVE"
            or not recipient_role
            or recipient_role.role_code != "CUSTOMER"
        ):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recipient account is not eligible")
        fee_type = _load_internal_transfer_fee(db)
        fee_amount = Decimal(str(fee_type.fixed_amount or 0))
    else:
        fee_type = None
        fee_amount = Decimal("0.00")

    if source.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Source account is {source.status}, cannot transfer")
    if destination.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Destination account is {destination.status}, cannot receive transfers")
    if source.currency_code != destination.currency_code:
        raise HTTPException(status_code=400, detail="Accounts must use the same currency")

    total_debit = transfer.amount + fee_amount
    if source.available_balance < total_debit:
        raise HTTPException(
            status_code=400,
            detail=(
                "Insufficient balance to cover transfer amount and fee"
                if fee_amount > 0
                else "Insufficient balance"
            ),
        )

    if not ref:
        for _ in range(5):
            ref = generate_reference("TRF")
            if not db.query(Transfer).filter(Transfer.transfer_reference == ref).first():
                break
        else:
            raise HTTPException(status_code=500, detail="Could not generate a unique transfer reference — please retry")

    transfer_values = transfer.model_dump(exclude={"destination_account_number"})
    transfer_values["destination_account_id"] = destination.id
    new_transfer = Transfer(
        **transfer_values,
        transfer_reference=ref,
        transfer_type="INTERNAL",
        status="SUCCESS",
        completed_at=datetime.utcnow(),
    )
    new_transfer.fee_amount = fee_amount
    new_transfer.total_debit = total_debit
    db.add(new_transfer)

    # Move the money: debit source, credit destination — both accounts,
    # same request, same commit.
    source.available_balance -= transfer.amount
    source.ledger_balance -= transfer.amount
    destination.available_balance += transfer.amount
    destination.ledger_balance += transfer.amount

    ledger_entries = [
        LedgerEntry(
            account_id=source.id,
            transaction_reference=new_transfer.transfer_reference,
            transaction_type="TRANSFER_DEBIT",
            debit_amount=new_transfer.amount,
            credit_amount=0,
            balance_after=source.available_balance,
            transaction_date=new_transfer.completed_at,
        ),
        LedgerEntry(
            account_id=destination.id,
            transaction_reference=new_transfer.transfer_reference,
            transaction_type="TRANSFER_CREDIT",
            debit_amount=0,
            credit_amount=new_transfer.amount,
            balance_after=destination.available_balance,
            transaction_date=new_transfer.completed_at,
        ),
    ]

    fee_record = None
    if fee_type and fee_amount > 0:
        fee_reference = _fee_reference(db)
        source.available_balance -= fee_amount
        source.ledger_balance -= fee_amount
        fee_record = FeeRecord(
            account_id=source.id,
            fee_type_id=fee_type.id,
            transaction_reference=fee_reference,
            amount_charged=fee_amount,
            remarks=_transfer_fee_record_remarks(new_transfer.transfer_reference),
        )
        db.add(fee_record)
        ledger_entries.append(
            LedgerEntry(
                account_id=source.id,
                transaction_reference=fee_reference,
                transaction_type="FEE",
                debit_amount=fee_amount,
                credit_amount=0,
                balance_after=source.available_balance,
                transaction_date=new_transfer.completed_at,
            )
        )
    db.add_all(ledger_entries)

    source_owner_id = source.customer_id
    destination_owner_id = destination.customer_id
    source_owner = db.query(User).filter(User.id == source_owner_id).first()
    destination_owner = db.query(User).filter(User.id == destination_owner_id).first()
    source_owner_name = (
        " ".join(filter(None, [source_owner.first_name, source_owner.middle_name, source_owner.last_name]))
        if source_owner
        else "MyBank customer"
    )
    destination_owner_name = (
        " ".join(filter(None, [destination_owner.first_name, destination_owner.middle_name, destination_owner.last_name]))
        if destination_owner
        else "MyBank customer"
    )
    notifications = []
    if source_owner_id is not None:
        source_notification = Notification(
            user_id=source_owner_id,
            title="Transfer sent",
            message=(
                f"Your transfer of {new_transfer.amount} to {destination_owner_name} was successful. "
                f"Reference: {new_transfer.transfer_reference}"
            ),
            notification_type="TRANSFER_SENT",
        )
        db.add(source_notification)
        notifications.append(source_notification)

    if destination_owner_id is not None and destination_owner_id != source_owner_id:
        recipient_notification = Notification(
            user_id=destination_owner_id,
            title="Money received",
            message=(
                f"You received {new_transfer.amount} from {source_owner_name}. "
                f"Reference: {new_transfer.transfer_reference}"
            ),
            notification_type="TRANSFER_RECEIVED",
        )
        db.add(recipient_notification)
        notifications.append(recipient_notification)
    elif destination_owner_id is not None:
        own_transfer_notification = Notification(
            user_id=destination_owner_id,
            title="Transfer completed",
            message=(
                f"Your transfer of {new_transfer.amount} between your accounts was successful. "
                f"Reference: {new_transfer.transfer_reference}"
            ),
            notification_type="TRANSFER",
        )
        db.add(own_transfer_notification)
        notifications.append(own_transfer_notification)

    try:
        db.flush()
        transfer_audit_values = snapshot_model(new_transfer)
        transfer_audit_values["fee_amount"] = str(fee_amount)
        transfer_audit_values["total_debit"] = str(total_debit)
        add_audit_log(
            db,
            actor_username,
            "CREATE",
            "Transfer",
            new_transfer.id,
            new_value=transfer_audit_values,
            request=request,
        )
        if fee_record:
            add_audit_log(
                db,
                actor_username,
                "CREATE",
                "FeeRecord",
                fee_record.id,
                new_value=snapshot_model(fee_record),
                request=request,
            )
        db.commit()
    except IntegrityError:
        db.rollback()
        if role_code == "CUSTOMER":
            existing = db.query(Transfer).filter(Transfer.transfer_reference == ref).first()
            if existing:
                return _replay_idempotent_transfer(
                    existing, transfer.source_account_id, destination_id, transfer, actor, role_code, db
                )
        raise
    db.refresh(new_transfer)
    for notification in notifications:
        db.refresh(notification)
        manager.send_from_sync_endpoint(
            notification.user_id,
            notification_payload(notification),
        )
    return new_transfer


@router.get("/", response_model=list[TransferOut])
def list_transfers(
    actor_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    actor, role_code = _load_actor(actor_username, db)
    query = db.query(Transfer)
    if role_code == "CUSTOMER":
        account_ids = db.query(Account.id).filter(Account.customer_id == actor.id)
        query = query.filter(
            Transfer.source_account_id.in_(account_ids)
            | Transfer.destination_account_id.in_(account_ids)
        )
    return query.order_by(Transfer.id.desc()).all()


@router.get("/{transfer_id}", response_model=TransferOut)
def get_transfer(
    transfer_id: int,
    actor_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    actor, role_code = _load_actor(actor_username, db)
    query = db.query(Transfer).filter(Transfer.id == transfer_id)
    if role_code == "CUSTOMER":
        account_ids = db.query(Account.id).filter(Account.customer_id == actor.id)
        query = query.filter(
            Transfer.source_account_id.in_(account_ids)
            | Transfer.destination_account_id.in_(account_ids)
        )
    transfer = query.first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfer


@router.put("/{transfer_id}", response_model=TransferOut)
def update_transfer(transfer_id: int, data: TransferCreate, db: Session = Depends(get_db)):
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Transfers are immutable and cannot be edited."
    )



@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transfer(transfer_id: int, db: Session = Depends(get_db)):
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Transfers are immutable and cannot be deleted."
    )
