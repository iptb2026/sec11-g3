# ==== LAYER 2: Identity & Access ====
from sqlalchemy import BigInteger, Column, Date, DateTime, Enum, ForeignKey, String, TIMESTAMP
from sqlalchemy.sql import func

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    mobile_number = Column(String(30), nullable=True)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    role_id = Column(BigInteger, ForeignKey("roles.id"), nullable=False)
    account_status = Column(Enum("ACTIVE", "LOCKED", "DISABLED"), default="ACTIVE")
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
