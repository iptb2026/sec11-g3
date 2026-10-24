from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.database.session import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, default="INFO")

    is_read = Column(Boolean, nullable=False, default=False, index=True)

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    read_at = Column(DateTime, nullable=True)
