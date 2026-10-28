from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.role import Role
from app.models.user import User


def get_actor_scope(username: str, db: Session):
    actor = db.query(User).filter(User.username == username).first()
    if not actor or actor.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active")

    role = db.query(Role).filter(Role.id == actor.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role is not recognized")
    if role.role_code not in {"ADMIN", "STAFF", "CUSTOMER"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role is not authorized")

    account_ids = (
        db.query(Account.id).filter(Account.customer_id == actor.id)
        if role.role_code == "CUSTOMER"
        else None
    )
    return actor, role.role_code, account_ids


def require_admin_or_staff(username: str, db: Session) -> None:
    _, role_code, _ = get_actor_scope(username, db)
    if role_code not in {"ADMIN", "STAFF"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator or staff access required",
        )


def require_admin(username: str, db: Session) -> None:
    _, role_code, _ = get_actor_scope(username, db)
    if role_code != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )
