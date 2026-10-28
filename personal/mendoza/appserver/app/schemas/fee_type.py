# ==== LAYER 1: Foundation & Reference Data ====
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class FeeTypeCreate(BaseModel):
    fee_code: str
    fee_name: str
    fee_description: Optional[str] = None
    fixed_amount: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    percentage_rate: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)

    @model_validator(mode="after")
    def internal_transfer_fee_is_fixed(self):
        if self.fee_code.strip().upper() == "INTERNAL_TRANSFER":
            if self.fee_code != "INTERNAL_TRANSFER":
                raise ValueError("The internal transfer fee code must be uppercase and exact")
            if self.percentage_rate != 0:
                raise ValueError("The internal transfer fee must be a fixed amount")
        return self

class FeeTypeOut(BaseModel):
    id: int
    fee_code: str
    fee_name: str
    fee_description: Optional[str] = None
    fixed_amount: Decimal
    percentage_rate: Decimal
    created_at: datetime

    class Config:
        from_attributes = True