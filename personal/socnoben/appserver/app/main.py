from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import Base, engine

# ==== LAYER 1: Foundation & Reference Data ====
from app.routers import roles, account_types, banks, fee_types

# ==== LAYER 2: Identity & Access ====
from app.routers import users, auth, sessions, audit_logs

# ==== LAYER 3: Account Configuration ====
from app.routers import accounts, withdrawal_limits, interest_policies

# ==== LAYER 4: Transactions ====
from app.routers import deposits, withdrawals, transfers, interbank_transfers

# ==== LAYER 5: Financial Records & Ledger ====
from app.routers import fee_records, interest_records, ledger_entries

# Creates tables if they don't already exist
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Database initialization deferred (connection error: {e})")
    

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

all_routers = [
    roles.router, account_types.router, banks.router, fee_types.router,
    users.router, auth.router, sessions.router, audit_logs.router,
    accounts.router, withdrawal_limits.router, interest_policies.router,
    deposits.router, withdrawals.router, transfers.router, interbank_transfers.router,
    fee_records.router, interest_records.router, ledger_entries.router
]

for r in all_routers:
    app.include_router(r)
    app.include_router(r, prefix="/socnoben")


@app.get("/", tags=["Health"])
@app.get("/socnoben", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}



