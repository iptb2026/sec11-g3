from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class InterestRecordCreate(BaseModel):
    account_id: int
    policy_id: int
    amount_credited: Decimal = Field(gt=0)


class InterestRecordOut(BaseModel):
    id: int
    account_id: int
    policy_id: int
    amount_credited: Decimal
    balance_before: Decimal
    balance_after: Decimal
    credited_at: datetime

    class Config:
        from_attributes = True
