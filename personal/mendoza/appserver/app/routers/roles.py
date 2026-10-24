# ==== LAYER 1: Foundation & Reference Data ====
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.audit import add_audit_log, snapshot_model
from app.core.db_utils import commit_or_409
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleOut

router = APIRouter(
    prefix="/roles",
    tags=["Layer 1 - Roles"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Role).filter(Role.role_code == role.role_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="role_code already exists")

    new_role = Role(**role.model_dump())
    db.add(new_role)
    db.flush()
    add_audit_log(db, actor_username, "CREATE", "Role", new_role.id, new_value=snapshot_model(new_role), request=request)
    db.commit()
    db.refresh(new_role)
    return new_role

@router.get("/", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).order_by(Role.id.desc()).all()

@router.get("/{role_id}", response_model=RoleOut)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/{role_id}", response_model=RoleOut)
def update_role(role_id: int, role_data: RoleCreate, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    old_values = snapshot_model(role)
    for field, value in role_data.model_dump().items():
        setattr(role, field, value)
    add_audit_log(db, actor_username, "UPDATE", "Role", role.id, old_value=old_values, new_value=snapshot_model(role), request=request)
    db.commit()
    db.refresh(role)
    return role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(role_id: int, request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    old_values = snapshot_model(role)
    add_audit_log(db, actor_username, "DELETE", "Role", role.id, old_value=old_values, request=request)
    db.delete(role)
    commit_or_409(db, "Cannot delete this role — one or more users still reference it")