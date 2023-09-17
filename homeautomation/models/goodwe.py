from .base import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class GoodweEvent(Base):
	__tablename__ = "goodwe_events"

	recorded_at: Mapped[datetime] = mapped_column(primary_key=True)
	export_limit: Mapped[int]
	changed: Mapped[bool]
