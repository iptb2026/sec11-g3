# ==== LAYER 4: Transactions ====
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import add_audit_log, snapshot_model
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.account import Account
from app.models.ledger_entry import LedgerEntry
from app.models.transfer import Transfer
from app.schemas.transfer import TransferCreate, TransferOut
from app.routers.notifications import create_and_send_notification

router = APIRouter(prefix="/transfers", tags=["Layer 4 - Transfers"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=TransferOut, status_code=status.HTTP_201_CREATED)
def create_transfer(transfer: TransferCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if transfer.source_account_id == transfer.destination_account_id:
        raise HTTPException(status_code=400, detail="source and destination accounts must be different")

    # Lock both accounts for the duration of this transaction so a
    # simultaneous transfer touching either one can't read a stale balance.
    # Locking order matters: always lock the lower id first, or two transfers
    # running in opposite directions at the same time (A->B and B->A) could
    # each be waiting on the row the other one is holding — a deadlock.
    first_id, second_id = sorted([transfer.source_account_id, transfer.destination_account_id])
    accounts_by_id = {
        a.id: a
        for a in db.query(Account).filter(Account.id.in_([first_id, second_id])).with_for_update().all()
    }
    source = accounts_by_id.get(transfer.source_account_id)
    destination = accounts_by_id.get(transfer.destination_account_id)

    if not source:
        raise HTTPException(status_code=400, detail="source_account_id does not exist")
    if not destination:
        raise HTTPException(status_code=400, detail="destination_account_id does not exist")

    existing = db.query(Transfer).filter(Transfer.transfer_reference == transfer.transfer_reference).first()
    if existing:
        raise HTTPException(status_code=400, detail="transfer_reference already exists")

    if source.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Source account is {source.status}, cannot transfer")

    if source.available_balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    new_transfer = Transfer(
        **transfer.model_dump(),
        status="SUCCESS",
        completed_at=datetime.utcnow(),
    )
    db.add(new_transfer)

    # Move the money: debit source, credit destination — both accounts,
    # same request, same commit.
    source.available_balance -= transfer.amount
    source.ledger_balance -= transfer.amount
    destination.available_balance += transfer.amount
    destination.ledger_balance += transfer.amount

    db.add_all([
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
    ])

    source_owner_id = source.customer_id
    destination_owner_id = destination.customer_id
    db.flush()
    add_audit_log(db, actor_username, "CREATE", "Transfer", new_transfer.id, new_value=snapshot_model(new_transfer), request=request)
    db.commit()
    db.refresh(new_transfer)
    create_and_send_notification(
        source_owner_id,
        "Transfer successful",
        f"Your transfer of {new_transfer.amount} was successful. "
        f"Reference: {new_transfer.transfer_reference}",
        "TRANSFER_SENT",
    ) if source_owner_id is not None else None
    if destination_owner_id is not None and destination_owner_id != source_owner_id:
        create_and_send_notification(
            destination_owner_id,
            "Money received",
            f"You received {new_transfer.amount} from a transfer. "
            f"Reference: {new_transfer.transfer_reference}",
            "TRANSFER_RECEIVED",
        )
    elif destination_owner_id is not None:
        create_and_send_notification(
            destination_owner_id,
            "Transfer completed",
            f"Your transfer of {new_transfer.amount} between your accounts "
            f"was successful. Reference: {new_transfer.transfer_reference}",
            "TRANSFER",
        )
    return new_transfer


@router.get("/", response_model=list[TransferOut])
def list_transfers(db: Session = Depends(get_db)):
    return db.query(Transfer).order_by(Transfer.id.desc()).all()


@router.get("/{transfer_id}", response_model=TransferOut)
def get_transfer(transfer_id: int, db: Session = Depends(get_db)):
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
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
