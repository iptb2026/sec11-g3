# ==== LAYER 2: Identity & Access ====

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import check_password, create_token, oauth2_scheme
from app.core.audit import add_audit_log
from app.database.session import get_db
from app.models.session import UserSession
from app.models.user import User
from app.schemas.auth import Token

router = APIRouter(
    prefix="/auth",
    tags=["Layer 2 - Auth"]
)


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    if not user or not check_password(
        form_data.password,
        user.hashed_password
    ):
        add_audit_log(
            db=db,
            actor_username=form_data.username,
            action_type="LOGIN_FAILED",
            entity_name="User",
            entity_id=user.id if user else None,
            new_value={"username": form_data.username},
            request=request,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.account_status != "ACTIVE":
        add_audit_log(
            db=db,
            actor_username=user.username,
            action_type="LOGIN_BLOCKED",
            entity_name="User",
            entity_id=user.id,
            new_value={"reason": "Account is not active"},
            request=request,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )

    token = create_token(user.username)

    expires_at = (
        datetime.utcnow()
        + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    new_session = UserSession(
        user_id=user.id,
        jwt_token=token,
        ip_address=(
            request.client.host
            if request.client
            else None
        ),
        user_agent=request.headers.get("user-agent"),
        expires_at=expires_at,
    )

    db.add(new_session)

    user.last_login_at = datetime.utcnow()

    add_audit_log(
        db=db,
        actor_username=user.username,
        action_type="LOGIN_SUCCESS",
        entity_name="User",
        entity_id=user.id,
        request=request,
    )

    db.commit()

    return Token(
        access_token=token,
        token_type="bearer"
    )


@router.post("/logout")
def logout(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    session = (
        db.query(UserSession)
        .filter(
            UserSession.jwt_token == token,
            UserSession.revoked_at.is_(None)
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active session not found"
        )

    session.revoked_at = datetime.utcnow()

    actor = db.query(User).filter(User.id == session.user_id).first()
    add_audit_log(
        db=db,
        actor_username=actor.username if actor else "",
        action_type="LOGOUT",
        entity_name="UserSession",
        entity_id=session.user_id,
        request=request,
    )

    db.commit()

    return {
        "message": "Successfully logged out"
    }
