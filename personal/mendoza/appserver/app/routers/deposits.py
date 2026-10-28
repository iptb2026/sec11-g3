# ==== LAYER 4: Transactions ====
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import add_audit_log, snapshot_model
from app.core.access import get_actor_scope, require_admin_or_staff
from app.core.security import get_current_user
from app.core.ref_gen import generate_reference
from app.database.session import get_db
from app.models.account import Account
from app.models.ledger_entry import LedgerEntry
from app.models.deposit import Deposit
from app.models.user import User
from app.schemas.deposit import DepositCreate, DepositOut
from app.routers.notifications import create_and_send_notification

router = APIRouter(prefix="/deposits", tags=["Layer 4 - Deposits"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=DepositOut, status_code=status.HTTP_201_CREATED)
def create_deposit(deposit: DepositCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin_or_staff(actor_username, db)
    # .with_for_update() locks this account row until the commit below, so a
    # second request touching the same account has to wait its turn instead
    # of reading a stale balance and silently overwriting this change.
    actor, role_code, _ = get_actor_scope(actor_username, db)
    account = db.query(Account).filter(Account.id == deposit.account_id).with_for_update().first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")
    if role_code == "CUSTOMER" and account.customer_id != actor.id:
        raise HTTPException(status_code=403, detail="You may only deposit to your own account")

    if deposit.deposited_by_user_id is not None:
        user = db.query(User).filter(User.id == deposit.deposited_by_user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="deposited_by_user_id does not exist")
    else:
        teller = db.query(User).filter(User.username == actor_username).first()
        if not teller:
            raise HTTPException(status_code=401, detail="Logged-in teller account not found")
        deposit = deposit.model_copy(update={"deposited_by_user_id": teller.id})

    # Auto-generate a unique reference number — retry on collision.
    for _ in range(5):
        ref = generate_reference("DEP")
        if not db.query(Deposit).filter(Deposit.reference_number == ref).first():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate unique reference — please retry")

    new_deposit = Deposit(**deposit.model_dump(), reference_number=ref)
    db.add(new_deposit)

    # This is the actual point of a deposit: money enters the account.
    account.available_balance += deposit.amount
    account.ledger_balance += deposit.amount

    db.add(LedgerEntry(
        account_id=account.id,
        transaction_reference=new_deposit.reference_number,
        transaction_type="DEPOSIT",
        debit_amount=0,
        credit_amount=new_deposit.amount,
        balance_after=account.available_balance,
        transaction_date=new_deposit.transaction_date,
    ))

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
def list_deposits(actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    _, _, account_ids = get_actor_scope(actor_username, db)
    query = db.query(Deposit)
    if account_ids is not None:
        query = query.filter(Deposit.account_id.in_(account_ids))
    return query.order_by(Deposit.id.desc()).all()


@router.get("/{deposit_id}", response_model=DepositOut)
def get_deposit(deposit_id: int, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    _, _, account_ids = get_actor_scope(actor_username, db)
    query = db.query(Deposit).filter(Deposit.id == deposit_id)
    if account_ids is not None:
        query = query.filter(Deposit.account_id.in_(account_ids))
    deposit = query.first()
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
