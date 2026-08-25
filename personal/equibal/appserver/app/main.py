from fastapi import FastAPI

from app.core.config import settings
from app.database.session import Base, engine

# Ensure models are imported so SQLAlchemy knows about all tables
from app import models  # noqa: F401

# ==== LAYER 1: Foundation & Reference Data ====
from app.routers import roles, account_types, banks, fee_types

# ==== LAYER 2: Identity & Access ====
from app.routers import users, auth, sessions, audit_logs

# ==== LAYER 3: Account Configuration ====
from app.routers import accounts, withdrawal_limits, interest_policies

# Creates tables if they don't already exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# ==== LAYER 1: Foundation & Reference Data ====
app.include_router(roles.router)
app.include_router(account_types.router)
app.include_router(banks.router)
app.include_router(fee_types.router)

# ==== LAYER 2: Identity & Access ====
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(audit_logs.router)

# ==== LAYER 3: Account Configuration ====
app.include_router(accounts.router)
app.include_router(withdrawal_limits.router)
app.include_router(interest_policies.router)

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}
