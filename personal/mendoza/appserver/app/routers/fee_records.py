# ==== LAYER 5: Financial Records & Ledger ====
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit import add_audit_log, snapshot_model
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.account import Account
from app.models.fee_record import FeeRecord
from app.models.fee_type import FeeType
from app.schemas.fee_record import FeeRecordCreate, FeeRecordOut

router = APIRouter(prefix="/fee-records", tags=["Layer 5 - Fee Records"], dependencies=[Depends(get_current_user)])


@router.post("/", response_model=FeeRecordOut, status_code=status.HTTP_201_CREATED)
def create_fee_record(fee: FeeRecordCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    # Lock the account row — see the same note in deposits.py / withdrawals.py.
    account = db.query(Account).filter(Account.id == fee.account_id).with_for_update().first()
    if not account:
        raise HTTPException(status_code=400, detail="account_id does not exist")

    fee_type = db.query(FeeType).filter(FeeType.id == fee.fee_type_id).first()
    if not fee_type:
        raise HTTPException(status_code=400, detail="fee_type_id does not exist")

    new_fee = FeeRecord(**fee.model_dump())
    db.add(new_fee)

    # Unlike a withdrawal, a fee is allowed to push the balance negative —
    # banks charge maintenance/overdraft fees regardless of available funds.
    account.available_balance -= fee.amount_charged
    account.ledger_balance -= fee.amount_charged

    db.flush()
    add_audit_log(db, actor_username, "CREATE", "FeeRecord", new_fee.id, new_value=snapshot_model(new_fee), request=request)
    db.commit()
    db.refresh(new_fee)
    return new_fee


@router.get("/", response_model=list[FeeRecordOut])
def list_fee_records(db: Session = Depends(get_db)):
    return db.query(FeeRecord).order_by(FeeRecord.id.desc()).all()


@router.get("/{fee_id}", response_model=FeeRecordOut)
def get_fee_record(fee_id: int, db: Session = Depends(get_db)):
    fee = db.query(FeeRecord).filter(FeeRecord.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found")
    return fee


@router.put("/{fee_id}", response_model=FeeRecordOut)
def update_fee_record(fee_id: int, data: FeeRecordCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """NOTE: does not re-adjust the account balance for the amount difference."""
    fee = db.query(FeeRecord).filter(FeeRecord.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found")

    old_values = snapshot_model(fee)
    for field, value in data.model_dump().items():
        setattr(fee, field, value)

    add_audit_log(db, actor_username, "UPDATE", "FeeRecord", fee.id, old_value=old_values, new_value=snapshot_model(fee), request=request)
    db.commit()
    db.refresh(fee)
    return fee


@router.delete("/{fee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fee_record(fee_id: int, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """NOTE: does not reverse the account balance change."""
    fee = db.query(FeeRecord).filter(FeeRecord.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found")

    add_audit_log(db, actor_username, "DELETE", "FeeRecord", fee.id, old_value=snapshot_model(fee), request=request)
    db.delete(fee)
    db.commit()
