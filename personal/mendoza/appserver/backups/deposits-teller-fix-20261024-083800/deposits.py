# ==== LAYER 4: Transactions ====
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import add_audit_log, snapshot_model
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.account import Account
from app.models.deposit import Deposit
from app.models.user import User
from app.schemas.deposit import DepositCreate, DepositOut
from app.routers.notifications import create_and_send_notification

router = APIRouter(prefix="/deposits", tags=["Layer 4 - Deposits"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=DepositOut, status_code=status.HTTP_201_CREATED)
def create_deposit(deposit: DepositCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    # .with_for_update() locks this account row until the commit below, so a
    # second request touching the same account has to wait its turn instead
    # of reading a stale balance and silently overwriting this change.
    account = db.query(Account).filter(Account.id == deposit.account_id).with_for_update().first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")

    if deposit.deposited_by_user_id is not None:
        user = db.query(User).filter(User.id == deposit.deposited_by_user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="deposited_by_user_id does not exist")

    existing = db.query(Deposit).filter(Deposit.reference_number == deposit.reference_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="reference_number already exists")

    new_deposit = Deposit(**deposit.model_dump())
    db.add(new_deposit)

    # This is the actual point of a deposit: money enters the account.
    account.available_balance += deposit.amount
    account.ledger_balance += deposit.amount

    owner_id = account.customer_id
    db.flush()
    add_audit_log(db, actor_username, "CREATE", "Deposit", new_deposit.id, new_value=snapshot_model(new_deposit), request=request)
    db.commit()
    db.refresh(new_deposit)
    if owner_id is not None:
        create_and_send_notification(
            owner_id,
            "Deposit successful",
            f"Your deposit of {new_deposit.amount} was successful. "
            f"Reference: {new_deposit.reference_number}",
            "DEPOSIT",
        )
    return new_deposit


@router.get("/", response_model=list[DepositOut])
def list_deposits(db: Session = Depends(get_db)):
    return db.query(Deposit).order_by(Deposit.id.desc()).all()


@router.get("/{deposit_id}", response_model=DepositOut)
def get_deposit(deposit_id: int, db: Session = Depends(get_db)):
    deposit = db.query(Deposit).filter(Deposit.id == deposit_id).first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")
    return deposit


@router.put("/{deposit_id}")
def update_deposit(deposit_id: int):
    raise HTTPException(
        status_code=405,
        detail="Deposit records are read-only and cannot be edited"
    )


@router.delete("/{deposit_id}", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
def delete_deposit(deposit_id: int):
    raise HTTPException(
        status_code=405,
        detail="Deposit records are read-only and cannot be deleted"
    )
