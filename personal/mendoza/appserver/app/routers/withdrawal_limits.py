# ==== LAYER 3: Account Configuration ====
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import add_audit_log, snapshot_model
from app.core.access import get_actor_scope, require_admin_or_staff
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.account import Account
from app.models.withdrawal_limit import WithdrawalLimit
from app.schemas.withdrawal_limit import WithdrawalLimitCreate, WithdrawalLimitUpdate, WithdrawalLimitOut

router = APIRouter(prefix="/withdrawal-limits", tags=["Layer 3 - Withdrawal Limits"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=WithdrawalLimitOut, status_code=status.HTTP_201_CREATED)
def create_withdrawal_limit(data: WithdrawalLimitCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin_or_staff(actor_username, db)
    account = db.query(Account).filter(Account.id == data.account_id).first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")

    # account_id is UNIQUE on this table — one account has at most one withdrawal_limits row.
    existing = db.query(WithdrawalLimit).filter(WithdrawalLimit.account_id == data.account_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="This account already has a withdrawal limit")

    new_limit = WithdrawalLimit(**data.model_dump())
    db.add(new_limit)
    db.flush()
    add_audit_log(db, actor_username, "CREATE", "WithdrawalLimit", new_limit.id, new_value=snapshot_model(new_limit), request=request)
    db.commit()
    db.refresh(new_limit)
    return new_limit


@router.get("/", response_model=list[WithdrawalLimitOut])
def list_withdrawal_limits(actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    _, _, account_ids = get_actor_scope(actor_username, db)
    query = db.query(WithdrawalLimit)
    if account_ids is not None:
        query = query.filter(WithdrawalLimit.account_id.in_(account_ids))
    return query.order_by(WithdrawalLimit.id.desc()).all()


@router.get("/{limit_id}", response_model=WithdrawalLimitOut)
def get_withdrawal_limit(limit_id: int, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    _, _, account_ids = get_actor_scope(actor_username, db)
    query = db.query(WithdrawalLimit).filter(WithdrawalLimit.id == limit_id)
    if account_ids is not None:
        query = query.filter(WithdrawalLimit.account_id.in_(account_ids))
    limit = query.first()
    if not limit:
        raise HTTPException(status_code=404, detail="Withdrawal limit not found")
    return limit


@router.put("/{limit_id}", response_model=WithdrawalLimitOut)
def update_withdrawal_limit(limit_id: int, data: WithdrawalLimitUpdate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin_or_staff(actor_username, db)
    limit = db.query(WithdrawalLimit).filter(WithdrawalLimit.id == limit_id).first()
    if not limit:
        raise HTTPException(status_code=404, detail="Withdrawal limit not found")

    old_values = snapshot_model(limit)
    limit.daily_limit_amount = data.daily_limit_amount
    limit.last_reset_date = data.last_reset_date

    add_audit_log(db, actor_username, "UPDATE", "WithdrawalLimit", limit.id, old_value=old_values, new_value=snapshot_model(limit), request=request)
    db.commit()
    db.refresh(limit)
    return limit


@router.delete("/{limit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_withdrawal_limit(limit_id: int, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    require_admin_or_staff(actor_username, db)
    limit = db.query(WithdrawalLimit).filter(WithdrawalLimit.id == limit_id).first()
    if not limit:
        raise HTTPException(status_code=404, detail="Withdrawal limit not found")

    add_audit_log(db, actor_username, "DELETE", "WithdrawalLimit", limit.id, old_value=snapshot_model(limit), request=request)
    db.delete(limit)
    db.commit()
