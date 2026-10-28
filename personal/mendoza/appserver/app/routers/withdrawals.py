# ==== LAYER 4: Transactions ====
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import add_audit_log, snapshot_model
from app.core.access import get_actor_scope
from app.core.security import get_current_user
from app.core.ref_gen import generate_reference
from app.database.session import get_db
from app.models.account import Account
from app.models.ledger_entry import LedgerEntry
from app.models.user import User
from app.models.withdrawal import Withdrawal
from app.models.withdrawal_limit import WithdrawalLimit
from app.schemas.withdrawal import WithdrawalCreate, WithdrawalOut
from app.routers.notifications import create_and_send_notification

router = APIRouter(prefix="/withdrawals", tags=["Layer 4 - Withdrawals"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=WithdrawalOut, status_code=status.HTTP_201_CREATED)
def create_withdrawal(withdrawal: WithdrawalCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    # Lock the account row for the duration of this transaction — without
    # this, two withdrawals submitted at nearly the same moment could both
    # read the same starting balance and one of their deductions would be
    # silently lost (a "lost update").
    actor, role_code, _ = get_actor_scope(actor_username, db)
    account = db.query(Account).filter(Account.id == withdrawal.account_id).with_for_update().first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")
    if role_code == "CUSTOMER" and account.customer_id != actor.id:
        raise HTTPException(status_code=403, detail="You may only withdraw from your own account")

    if withdrawal.approved_by_user_id is not None:
        user = db.query(User).filter(User.id == withdrawal.approved_by_user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="approved_by_user_id does not exist")

    if account.status != "ACTIVE":
        raise HTTPException(status_code=400, detail=f"Account is {account.status}, cannot withdraw")

    if account.available_balance < withdrawal.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # If this account has a daily withdrawal limit (Layer 3), enforce it.
    # Also locked, for the same reason as the account row above.
    limit = db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id == account.id).with_for_update().first()
    if limit and (limit.daily_used_amount + withdrawal.amount) > limit.daily_limit_amount:
        raise HTTPException(status_code=400, detail="This withdrawal would exceed the daily withdrawal limit")

    # Auto-generate a unique reference number — retry on collision.
    for _ in range(5):
        ref = generate_reference("WDL")
        if not db.query(Withdrawal).filter(Withdrawal.reference_number == ref).first():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate unique reference — please retry")

    new_withdrawal = Withdrawal(**withdrawal.model_dump(), reference_number=ref)
    db.add(new_withdrawal)

    account.available_balance -= withdrawal.amount
    account.ledger_balance -= withdrawal.amount

    db.add(LedgerEntry(
        account_id=account.id,
        transaction_reference=new_withdrawal.reference_number,
        transaction_type="WITHDRAWAL",
        debit_amount=new_withdrawal.amount,
        credit_amount=0,
        balance_after=account.available_balance,
        transaction_date=new_withdrawal.transaction_date,
    ))

    if limit:
        limit.daily_used_amount += withdrawal.amount

    owner_id = account.customer_id
    db.flush()
    add_audit_log(db, actor_username, "CREATE", "Withdrawal", new_withdrawal.id, new_value=snapshot_model(new_withdrawal), request=request)
    db.commit()
    db.refresh(new_withdrawal)
    if owner_id is not None:
        create_and_send_notification(
            owner_id,
            "Withdrawal successful",
            f"Your withdrawal of {new_withdrawal.amount} was successful. "
            f"Reference: {new_withdrawal.reference_number}",
            "WITHDRAWAL",
        )
    return new_withdrawal


@router.get("/", response_model=list[WithdrawalOut])
def list_withdrawals(actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    _, _, account_ids = get_actor_scope(actor_username, db)
    query = db.query(Withdrawal)
    if account_ids is not None:
        query = query.filter(Withdrawal.account_id.in_(account_ids))
    return query.order_by(Withdrawal.id.desc()).all()


@router.get("/{withdrawal_id}", response_model=WithdrawalOut)
def get_withdrawal(withdrawal_id: int, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    _, _, account_ids = get_actor_scope(actor_username, db)
    query = db.query(Withdrawal).filter(Withdrawal.id == withdrawal_id)
    if account_ids is not None:
        query = query.filter(Withdrawal.account_id.in_(account_ids))
    withdrawal = query.first()
    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    return withdrawal


@router.put("/{withdrawal_id}")
def update_withdrawal(withdrawal_id: int):
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Withdrawal records are immutable; use a reversal transaction for corrections."
    )


@router.delete("/{withdrawal_id}", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
def delete_withdrawal(withdrawal_id: int):
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Withdrawal records are immutable and cannot be deleted."
    )
