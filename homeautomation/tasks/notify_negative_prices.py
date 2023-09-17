from datetime import datetime, timezone
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from . import Task
from homeautomation.models.amber import *
from homeautomation.models.alphaess import *
from homeautomation.models.price_notifications import *
from homeautomation import notifications
from sentry_sdk.crons import monitor


class NotifyPriceChanges(Task):
	title = "Notify Price Changes"
	frequency = 30

	NOTIFY_FREQUENCY = 2 * 60 * 60  # 2 hours

	def __init__(self, db):
		super().__init__()
		
		self._db = db

	def _save_to_db(self, data):
		with Session(self._db) as session:
			session.add(data)
			session.commit()

	def _get_grid_price(self):
		sql = text("""
			SELECT purchase_price FROM amber_pricing
			ORDER BY recorded_at DESC LIMIT 1
		""")

		with self._db.connect() as connection:
			return float(connection.execute(sql).one()[0])

	def _get_last_notified(self):
		sql = text("""
			SELECT recorded_at, price FROM price_notifications
			ORDER BY recorded_at DESC
			LIMIT 1
		""")

		with self._db.connect() as connection:
			return connection.execute(sql).first()

	def _save_to_db(self, data):
		with Session(self._db) as session:
			session.add(data)
			session.commit()

	@monitor(monitor_slug="notify_negative_prices")
	def do_task(self):
		now = datetime.now(timezone.utc)
		price = self._get_grid_price()
		last_notified = self._get_last_notified()
		last_notified_delta = None if last_notified is None else (now - last_notified[0].replace(tzinfo=timezone.utc)).total_seconds()

		if price <= 0 and (last_notified_delta is None or last_notified_delta > self.NOTIFY_FREQUENCY):
			notifications.send("Use more power!", "Grid prices are negative: " + str(round(price, 1)) + "c per kWh")
			print(now, "NEGPRICE =", "Price is negative")

			event = PriceNotification(
				recorded_at=now,
				notification_type=NotificationType.NEGATIVE,
				price=price
			)

			self._save_to_db(event)
		else:
			print(now, "NEGPRICE =", "Price is not negative or not changed")



