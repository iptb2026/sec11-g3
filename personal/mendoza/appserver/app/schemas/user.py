# ==== LAYER 2: Identity & Access ====
from datetime import date, datetime
from typing import Optional, Literal, Union

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[Union[date, str]] = None
    role_id: int
    account_status: Literal["ACTIVE", "LOCKED", "DISABLED"] = "ACTIVE"


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[Union[date, str]] = None
    role_id: Optional[int] = None
    account_status: Optional[str] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[date] = None
    role_id: int
    account_status: str
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
