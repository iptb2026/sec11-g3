# ==== LAYER 2: Identity & Access ====

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.audit import add_audit_log, snapshot_model
from app.core.access import get_actor_scope, require_admin

from app.core.db_utils import commit_or_409
from app.core.security import get_current_user, hash_password
from app.database.session import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate


router = APIRouter(
    prefix="/users",
    tags=["Layer 2 - Users"],
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: UserCreate,
    request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    require_admin(actor_username, db)
    role = db.query(Role).filter(
        Role.id == user.role_id
    ).first()

    if not role:
        raise HTTPException(
            status_code=400,
            detail="role_id does not exist"
        )

    existing = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="username already in use"
        )

    data = user.model_dump(
        exclude={"password"}
    )

    new_user = User(
        **data,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.flush()
    add_audit_log(db, actor_username, "CREATE", "User", new_user.id, new_value=snapshot_model(new_user), request=request)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get(
    "/",
    response_model=list[UserOut]
)
def list_users(
    actor_username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    actor, role_code, _ = get_actor_scope(actor_username, db)
    query = db.query(User)
    if role_code == "CUSTOMER":
        query = query.filter(User.id == actor.id)
    return query.order_by(User.id.desc()).all()


@router.get(
    "/{user_id}",
    response_model=UserOut
)
def get_user(
    user_id: int,
    actor_username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    actor, role_code, _ = get_actor_scope(actor_username, db)
    query = db.query(User).filter(User.id == user_id)
    if role_code == "CUSTOMER":
        query = query.filter(User.id == actor.id)
    user = query.first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.put(
    "/{user_id}",
    response_model=UserOut
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    require_admin(actor_username, db)
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user_data.role_id is not None:
        role = db.query(Role).filter(
            Role.id == user_data.role_id
        ).first()

        if not role:
            raise HTTPException(
                status_code=400,
                detail="role_id does not exist"
            )

    # Check for username conflict with other users
    if user_data.username:
        existing = db.query(User).filter(
            User.id != user_id,
            User.username == user_data.username
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="username already in use"
            )

    data = user_data.model_dump(
        exclude_unset=True,
        exclude={"password"}
    )

    # Sanitize empty strings to None for optional fields
    for opt_field in ["email", "mobile_number", "middle_name", "date_of_birth"]:
        if opt_field in data and (data[opt_field] == "" or data[opt_field] is None):
            data[opt_field] = None

    if "date_of_birth" in data and isinstance(data["date_of_birth"], str):
        if data["date_of_birth"].strip():
            from datetime import date
            try:
                data["date_of_birth"] = date.fromisoformat(data["date_of_birth"].strip())
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format for date_of_birth. Use YYYY-MM-DD.")
        else:
            data["date_of_birth"] = None

    if "account_status" in data and data["account_status"]:
        status_val = data["account_status"].upper()
        if status_val not in ["ACTIVE", "LOCKED", "DISABLED"]:
            raise HTTPException(status_code=400, detail="account_status must be ACTIVE, LOCKED, or DISABLED")
        data["account_status"] = status_val

    old_values = snapshot_model(user)
    for field, value in data.items():
        setattr(user, field, value)

    if user_data.password and user_data.password.strip():
        user.hashed_password = hash_password(user_data.password.strip())

    add_audit_log(db, actor_username, "UPDATE", "User", user.id, old_value=old_values, new_value=snapshot_model(user), request=request)
    db.commit()
    db.refresh(user)

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
    user_id: int,
    request: Request, actor_username: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    require_admin(actor_username, db)
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    old_values = snapshot_model(user)
    add_audit_log(db, actor_username, "DELETE", "User", user.id, old_value=old_values, request=request)
    db.delete(user)

    commit_or_409(
        db,
        "Cannot delete this user — related sessions, accounts, or audit logs still reference it"
    )
