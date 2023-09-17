from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class AlphaESSUsage(Base):
	__tablename__ = "alphaess_usage"

	recorded_at: Mapped[datetime] = mapped_column(primary_key=True)
	solar_power: Mapped[int]
	grid_power: Mapped[int]
	battery_power: Mapped[int]
	load: Mapped[int]
	charge_level: Mapped[float]
