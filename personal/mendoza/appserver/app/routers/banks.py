# ==== LAYER 1: Foundation & Reference Data ====
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.audit import add_audit_log, snapshot_model
from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.bank import Bank
from app.schemas.bank import BankCreate, BankOut
from app.core.security import get_current_user

router = APIRouter(
    prefix="/banks",
    tags=["Layer 1 - Banks"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=BankOut, status_code=status.HTTP_201_CREATED)
def create_bank(bank: BankCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Bank).filter(Bank.bank_code == bank.bank_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="bank_code already exists")
    new_bank = Bank(**bank.model_dump())
    db.add(new_bank)
    db.flush()
    add_audit_log(db, actor_username, "CREATE", "Bank", new_bank.id, new_value=snapshot_model(new_bank), request=request)
    db.commit()
    db.refresh(new_bank)
    return new_bank

@router.get("/", response_model=list[BankOut])
def list_banks(db: Session = Depends(get_db)):
    return db.query(Bank).order_by(Bank.id.desc()).all()

@router.get("/{bank_id}", response_model=BankOut)
def get_bank(bank_id: int, db: Session = Depends(get_db)):
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    return bank

@router.put("/{bank_id}", response_model=BankOut)
def update_bank(bank_id: int, data: BankCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    old_values = snapshot_model(bank)
    for field, value in data.model_dump().items():
        setattr(bank, field, value)
    add_audit_log(db, actor_username, "UPDATE", "Bank", bank.id, old_value=old_values, new_value=snapshot_model(bank), request=request)
    db.commit()
    db.refresh(bank)
    return bank

@router.delete("/{bank_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bank(bank_id: int, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(status_code=404, detail="Bank not found")
    old_values = snapshot_model(bank)
    add_audit_log(db, actor_username, "DELETE", "Bank", bank.id, old_value=old_values, request=request)
    db.delete(bank)
    commit_or_409(db, "Cannot delete this bank — one or more interbank transfers still reference it")