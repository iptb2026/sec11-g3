# ==== LAYER 1: Foundation & Reference Data ====
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.audit import add_audit_log, snapshot_model
from app.core.db_utils import commit_or_409
from app.database.session import get_db
from app.models.fee_type import FeeType
from app.models.role import Role
from app.models.user import User
from app.schemas.fee_type import FeeTypeCreate, FeeTypeOut
from app.core.security import get_current_user

router = APIRouter(
    prefix="/fee-types",
    tags=["Layer 1 - Fee Types"],
    dependencies=[Depends(get_current_user)]
)

INTERNAL_TRANSFER_FEE_CODE = "INTERNAL_TRANSFER"


def _require_admin(username: str, db: Session) -> None:
    user = db.query(User).filter(User.username == username).first()
    role = db.query(Role).filter(Role.id == user.role_id).first() if user else None
    if not user or user.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active")
    if not role or role.role_code != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")


@router.post("/", response_model=FeeTypeOut, status_code=status.HTTP_201_CREATED)
def create_fee_type(fee_type: FeeTypeCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if fee_type.fee_code.strip().upper() == INTERNAL_TRANSFER_FEE_CODE:
        _require_admin(actor_username, db)
    existing = db.query(FeeType).filter(FeeType.fee_code == fee_type.fee_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="fee_code already exists")
    new_fee_type = FeeType(**fee_type.model_dump())
    db.add(new_fee_type)
    try:
        db.flush()
        add_audit_log(db, actor_username, "CREATE", "FeeType", new_fee_type.id, new_value=snapshot_model(new_fee_type), request=request)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Fee type code already exists")
    db.refresh(new_fee_type)
    return new_fee_type

@router.get("/", response_model=list[FeeTypeOut])
def list_fee_types(db: Session = Depends(get_db)):
    return db.query(FeeType).order_by(FeeType.id.desc()).all()

@router.get("/{fee_type_id}", response_model=FeeTypeOut)
def get_fee_type(fee_type_id: int, db: Session = Depends(get_db)):
    fee_type = db.query(FeeType).filter(FeeType.id == fee_type_id).first()
    if not fee_type:
        raise HTTPException(status_code=404, detail="Fee type not found")
    return fee_type

@router.put("/{fee_type_id}", response_model=FeeTypeOut)
def update_fee_type(fee_type_id: int, data: FeeTypeCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    fee_type = db.query(FeeType).filter(FeeType.id == fee_type_id).first()
    if not fee_type:
        raise HTTPException(status_code=404, detail="Fee type not found")
    if (
        fee_type.fee_code == INTERNAL_TRANSFER_FEE_CODE
        or data.fee_code.strip().upper() == INTERNAL_TRANSFER_FEE_CODE
    ):
        _require_admin(actor_username, db)
    if fee_type.fee_code == INTERNAL_TRANSFER_FEE_CODE:
        if data.fee_code != INTERNAL_TRANSFER_FEE_CODE:
            raise HTTPException(status_code=400, detail="The internal transfer fee code cannot be changed")
    duplicate = (
        db.query(FeeType)
        .filter(FeeType.fee_code == data.fee_code, FeeType.id != fee_type_id)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="fee_code already exists")
    old_values = snapshot_model(fee_type)
    for field, value in data.model_dump().items():
        setattr(fee_type, field, value)
    add_audit_log(db, actor_username, "UPDATE", "FeeType", fee_type.id, old_value=old_values, new_value=snapshot_model(fee_type), request=request)
    db.commit()
    db.refresh(fee_type)
    return fee_type


@router.delete("/{fee_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fee_type(fee_type_id: int, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    fee_type = db.query(FeeType).filter(FeeType.id == fee_type_id).first()

    if not fee_type:
        raise HTTPException(status_code=404, detail="Fee type not found")
    if fee_type.fee_code == INTERNAL_TRANSFER_FEE_CODE:
        raise HTTPException(status_code=400, detail="The internal transfer fee policy cannot be deleted")

    old_values = snapshot_model(fee_type)
    add_audit_log(db, actor_username, "DELETE", "FeeType", fee_type.id, old_value=old_values, request=request)
    db.delete(fee_type)

    commit_or_409(
        db,
        "Cannot delete this fee type — one or more accounts or transactions still reference it"
    )