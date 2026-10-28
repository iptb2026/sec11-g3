# ==== LAYER 4: Transactions ====
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import add_audit_log, snapshot_model
from app.core.access import get_actor_scope, require_admin_or_staff
from app.core.ref_gen import generate_reference
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.account import Account
from app.models.bank import Bank
from app.models.fee_record import FeeRecord
from app.models.fee_type import FeeType
from app.models.interbank_transfer import InterbankTransfer
from app.models.ledger_entry import LedgerEntry
from app.routers.notifications import create_and_send_notification
from app.schemas.interbank_transfer import (
    InterbankTransferCreate,
    InterbankTransferStatusUpdate,
    InterbankTransferOut,
)

router = APIRouter(prefix="/interbank-transfers", tags=["Layer 4 - Interbank Transfers"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=InterbankTransferOut, status_code=status.HTTP_201_CREATED)
def create_interbank_transfer(transfer: InterbankTransferCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    actor, role_code, _ = get_actor_scope(actor_username, db)
    # Lock the source account row for the duration of this transaction — see
    # the same note in deposits.py / withdrawals.py.
    source = db.query(Account).filter(Account.id == transfer.source_account_id).with_for_update().first()
    if not source:
        raise HTTPException(status_code=400, detail="source_account_id does not exist")
    if role_code == "CUSTOMER" and source.customer_id != actor.id:
        raise HTTPException(status_code=403, detail="Source account does not belong to you")

    bank = db.query(Bank).filter(Bank.id == transfer.target_bank_id).first()
    if not bank:
        raise HTTPException(status_code=400, detail="target_bank_id does not exist")

    fee_type = db.query(FeeType).filter(FeeType.fee_code == "PESONET").first()
    if not fee_type:
        raise HTTPException(status_code=500, detail="PESONET fee policy is not configured")

    transfer_fee = Decimal(str(fee_type.fixed_amount))
    total_debit = transfer.amount + transfer_fee

    if source.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Source account is {source.status}, cannot transfer")

    if source.available_balance < total_debit:
        raise HTTPException(status_code=400, detail="Insufficient balance to cover amount + transfer fee")

    for _ in range(5):
        ref = generate_reference("IBT")
        if not db.query(InterbankTransfer).filter(InterbankTransfer.reference_number == ref).first():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate a unique interbank reference — please retry")

    for _ in range(5):
        fee_ref = generate_reference("FEE")
        if not db.query(FeeRecord).filter(FeeRecord.transaction_reference == fee_ref).first():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate a unique fee reference — please retry")

    # Unlike an internal `transfer`, the destination bank is external — we
    # can only debit our own side. The transfer starts PROCESSING (not
    # SUCCESS) because settlement with the other bank isn't instant; use
    # PUT /interbank-transfers/{id}/status to move it to SUCCESS/FAILED later.
    new_transfer = InterbankTransfer(
        **transfer.model_dump(),
        reference_number=ref,
        transfer_fee=transfer_fee,
        status="PROCESSING",
    )
    db.add(new_transfer)

    source.available_balance -= total_debit
    source.ledger_balance -= total_debit

    fee_record = FeeRecord(
        account_id=source.id,
        fee_type_id=fee_type.id,
        transaction_reference=fee_ref,
        amount_charged=transfer_fee,
        remarks=f"Interbank transfer fee for {ref}",
    )
    db.add(fee_record)

    balance_after_amount = source.available_balance + transfer_fee
    db.add_all([
        LedgerEntry(
            account_id=source.id,
            transaction_reference=ref,
            transaction_type="INTERBANK_DEBIT",
            debit_amount=transfer.amount,
            credit_amount=0,
            balance_after=balance_after_amount,
            transaction_date=datetime.utcnow(),
        ),
        LedgerEntry(
            account_id=source.id,
            transaction_reference=fee_ref,
            transaction_type="FEE",
            debit_amount=transfer_fee,
            credit_amount=0,
            balance_after=source.available_balance,
            transaction_date=datetime.utcnow(),
        ),
    ])

    owner_id = source.customer_id
    db.flush()
    add_audit_log(db, actor_username, "CREATE", "InterbankTransfer", new_transfer.id, new_value=snapshot_model(new_transfer), request=request)
    db.commit()
    db.refresh(new_transfer)
    if owner_id is not None:
        create_and_send_notification(
            owner_id,
            "Interbank transfer submitted",
            f"Your interbank transfer of {new_transfer.amount} has been submitted "
            f"and is being processed. Reference: {new_transfer.reference_number}",
            "INTERBANK_PROCESSING",
        )
    return new_transfer


@router.get("/", response_model=list[InterbankTransferOut])
def list_interbank_transfers(actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    _, _, account_ids = get_actor_scope(actor_username, db)
    query = db.query(InterbankTransfer)
    if account_ids is not None:
        query = query.filter(InterbankTransfer.source_account_id.in_(account_ids))
    return query.order_by(InterbankTransfer.id.desc()).all()


@router.get("/{transfer_id}", response_model=InterbankTransferOut)
def get_interbank_transfer(transfer_id: int, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    _, _, account_ids = get_actor_scope(actor_username, db)
    query = db.query(InterbankTransfer).filter(InterbankTransfer.id == transfer_id)
    if account_ids is not None:
        query = query.filter(InterbankTransfer.source_account_id.in_(account_ids))
    transfer = query.first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Interbank transfer not found")
    return transfer


@router.put("/{transfer_id}/status", response_model=InterbankTransferOut)
def update_interbank_transfer_status(
    transfer_id: int, data: InterbankTransferStatusUpdate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Moves a PROCESSING transfer to its final settlement status (SUCCESS/FAILED/REVERSED)."""
    require_admin_or_staff(actor_username, db)
    transfer = db.query(InterbankTransfer).filter(
        InterbankTransfer.id == transfer_id
    ).with_for_update().first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Interbank transfer not found")

    if transfer.status == data.status:
        return transfer
    if transfer.status != "PROCESSING" or data.status not in {"SUCCESS", "FAILED", "REVERSED"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot change interbank transfer from {transfer.status} to {data.status}",
        )

    old_values = snapshot_model(transfer)
    previous_status = transfer.status
    source_account = db.query(Account).filter(
        Account.id == transfer.source_account_id
    ).with_for_update().first()
    if not source_account:
        raise HTTPException(status_code=409, detail="Source account no longer exists")
    owner_id = source_account.customer_id if source_account else None

    if data.status in {"FAILED", "REVERSED"}:
        refund_amount = transfer.amount + (transfer.transfer_fee or Decimal("0.00"))
        source_account.available_balance += refund_amount
        source_account.ledger_balance += refund_amount
        db.add(LedgerEntry(
            account_id=source_account.id,
            transaction_reference=transfer.reference_number,
            transaction_type="REVERSAL",
            debit_amount=0,
            credit_amount=refund_amount,
            balance_after=source_account.available_balance,
            transaction_date=datetime.utcnow(),
        ))

    transfer.status = data.status
    if data.status in ("SUCCESS", "FAILED", "REVERSED"):
        transfer.completed_at = datetime.utcnow()

    add_audit_log(db, actor_username, "UPDATE", "InterbankTransfer", transfer.id, old_value=old_values, new_value=snapshot_model(transfer), request=request)
    db.commit()
    db.refresh(transfer)
    if owner_id is not None and previous_status != data.status and data.status in ("SUCCESS", "FAILED", "REVERSED"):
        title = {
            "SUCCESS": "Interbank transfer successful",
            "FAILED": "Interbank transfer failed",
            "REVERSED": "Interbank transfer reversed",
        }[data.status]
        create_and_send_notification(
            owner_id,
            title,
            f"Your interbank transfer of {transfer.amount} is now "
            f"{transfer.status.lower()}. Reference: {transfer.reference_number}",
            f"INTERBANK_{transfer.status}",
        )
    return transfer


@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interbank_transfer(transfer_id: int, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Interbank transfers are immutable; use FAILED or REVERSED to refund funds."""
    require_admin_or_staff(actor_username, db)
    transfer = db.query(InterbankTransfer).filter(InterbankTransfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="Interbank transfer not found")

    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Interbank transfers are immutable; update status to FAILED or REVERSED to refund funds.",
    )
