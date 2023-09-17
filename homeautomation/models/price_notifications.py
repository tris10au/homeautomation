from .base import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from enum import Enum


class NotificationType(Enum):
	NEGATIVE = "NEG"


class PriceNotification(Base):
	__tablename__ = "price_notifications"

	recorded_at: Mapped[datetime] = mapped_column(primary_key=True)
	notification_type: Mapped[NotificationType]
	price: Mapped[float]
