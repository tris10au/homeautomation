from .base import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class AmberPrice(Base):
	__tablename__ = "amber_pricing"

	recorded_at: Mapped[datetime] = mapped_column(primary_key=True)
	start: Mapped[datetime]
	end: Mapped[datetime]
	purchase_price: Mapped[float]
	sell_price: Mapped[float]
	spot_price: Mapped[float]
	sell_descriptor: Mapped[str] = mapped_column(String(512))
	purchase_descriptor: Mapped[str] = mapped_column(String(512))
	estimated: Mapped[bool]
	renewables: Mapped[float]
	spike: Mapped[str] = mapped_column(String(512))
	tariff: Mapped[str] = mapped_column(String(512))
