from decimal import Decimal

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.audit import add_audit_log, snapshot_model
from app.database.session import Base, SessionLocal, engine
from app.models.fee_type import FeeType

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
    fee_records,
    interest_records,
    ledger_entries,
    notifications,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    openapi_url="/openapi.json",
    swagger_ui_parameters={"url": "/mendoza/openapi.json"},
)


@app.on_event("startup")
def ensure_internal_transfer_fee():
    db = SessionLocal()
    try:
        fee_type = db.query(FeeType).filter(FeeType.fee_code == "INTERNAL_TRANSFER").first()
        if fee_type:
            return

        fee_type = FeeType(
            fee_code="INTERNAL_TRANSFER",
            fee_name="Customer Internal Transfer",
            fee_description="Fixed fee charged when a customer sends money to another MyBank customer.",
            fixed_amount=Decimal("5.00"),
            percentage_rate=Decimal("0.00"),
        )
        db.add(fee_type)
        db.flush()
        add_audit_log(
            db,
            "system",
            "CREATE",
            "FeeType",
            fee_type.id,
            new_value=snapshot_model(fee_type),
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        if not db.query(FeeType).filter(FeeType.fee_code == "INTERNAL_TRANSFER").first():
            raise
    finally:
        db.close()


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

# ==== LAYER 5 ====
app.include_router(fee_records.router)
app.include_router(interest_records.router)
app.include_router(ledger_entries.router)
app.include_router(notifications.router)

@app.middleware("http")
async def handle_mendoza_prefix(request: Request, call_next):
    path = request.scope.get("path", "")
    if path == "/mendoza":
        request.scope["path"] = "/"
    elif path.startswith("/mendoza/"):
        request.scope["path"] = path[len("/mendoza"):]
    return await call_next(request)

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