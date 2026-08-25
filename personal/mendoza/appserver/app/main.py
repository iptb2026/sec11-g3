from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import Base, engine

from app.routers import (
    roles,
    account_types,
    banks,
    fee_types,
    users,
    auth,
    sessions,
    audit_logs,
    accounts,
    withdrawal_limits,
    interest_policies,
    deposits,
    withdrawals,
    transfers,
    interbank_transfers,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# ==== LAYER 1 ====
app.include_router(roles.router)
app.include_router(account_types.router)
app.include_router(banks.router)
app.include_router(fee_types.router)

# ==== LAYER 2 ====
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(audit_logs.router)

# ==== LAYER 3 ====
app.include_router(accounts.router)
app.include_router(withdrawal_limits.router)
app.include_router(interest_policies.router)

# ==== LAYER 4 ====
app.include_router(deposits.router)
app.include_router(withdrawals.router)
app.include_router(transfers.router)
app.include_router(interbank_transfers.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "app": settings.APP_NAME
    }


@app.get("/hello", tags=["Hello"])
def hello_name():
    return {
        "message": "Hello from FastAPI!"
    }