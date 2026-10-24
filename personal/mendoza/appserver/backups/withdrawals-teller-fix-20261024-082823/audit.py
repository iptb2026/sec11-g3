from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def add_audit_log(
    db: Session,
    actor_username: str,
    action_type: str,
    entity_name: str,
    entity_id: int | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None,
    request: Request | None = None,
):
    """Add an audit entry to the current transaction. The caller commits it."""
    actor = (
        db.query(User)
        .filter(User.username == actor_username)
        .first()
    )

    # Never record password fields or password hashes.
    sensitive_fields = {"password", "hashed_password", "token", "jwt_token"}

    def clean(value):
        if value is None:
            return None
        safe = {
            key: item
            for key, item in value.items()
            if key.lower() not in sensitive_fields
        }
        return jsonable_encoder(safe)

    log = AuditLog(
        user_id=actor.id if actor else None,
        action_type=action_type,
        entity_name=entity_name,
        entity_id=entity_id,
        old_value=clean(old_value),
        new_value=clean(new_value),
        ip_address=(
            request.client.host
            if request and request.client
            else None
        ),
        user_agent=(
            request.headers.get("user-agent")
            if request
            else None
        ),
    )

    db.add(log)
    return log


def snapshot_model(instance):
    """Return safe, JSON-compatible column values from a SQLAlchemy model."""
    from sqlalchemy import inspect as sa_inspect

    if instance is None:
        return None

    sensitive_fields = {
        "password", "hashed_password", "token", "jwt_token",
        "access_token", "refresh_token",
    }

    values = {}
    mapper = sa_inspect(instance).mapper

    for column in mapper.column_attrs:
        name = column.key
        if name.lower() in sensitive_fields:
            continue
        values[name] = getattr(instance, name)

    return jsonable_encoder(values)
