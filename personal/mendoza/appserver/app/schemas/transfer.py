# ==== LAYER 4: Transactions ====
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TransferCreate(BaseModel):
    source_account_id: int = Field(gt=0)
    destination_account_id: Optional[int] = Field(default=None, gt=0)
    destination_account_number: Optional[str] = Field(default=None, min_length=1, max_length=30)
    amount: Decimal = Field(gt=0)
    remarks: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_has_cent_precision(cls, value: Decimal) -> Decimal:
        if value != value.quantize(Decimal("0.01")):
            raise ValueError("amount must have no more than two decimal places")
        return value

    @field_validator("destination_account_number")
    @classmethod
    def normalize_destination_account_number(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if value is not None else None


class TransferOut(BaseModel):
    id: int
    source_account_id: int
    destination_account_id: int
    transfer_reference: str
    amount: Decimal
    fee_amount: Decimal = Decimal("0.00")
    total_debit: Decimal = Decimal("0.00")
    transfer_type: str
    remarks: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerTransferAccount(BaseModel):
    id: int
    account_number: str
    available_balance: Decimal
    currency_code: str

    class Config:
        from_attributes = True


class RecipientPreviewRequest(BaseModel):
    source_account_id: int
    destination_account_number: str = Field(min_length=1, max_length=30)

    @field_validator("destination_account_number")
    @classmethod
    def normalize_destination_account_number(cls, value: str) -> str:
        return value.strip()


class RecipientPreview(BaseModel):
    account_number: str
    customer_name: str
    currency_code: str
    transfer_fee: Decimal
