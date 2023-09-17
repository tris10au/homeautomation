from datetime import datetime, timezone
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from . import Task
from homeautomation.models.amber import *
from homeautomation.models.alphaess import *
from homeautomation.models.goodwe import *
import homeautomation.notifications
from sentry_sdk.crons import monitor


class ControlGoodweInverter(Task):
	title = "Control Goodwe Inverter"
	frequency = 30
	_api = None
	_site_id = None


	TIME_WINDOW = 300
	FEED_IN_CUTOFF = -300
	PRICE_CUTOFF = 0.0
	MIN_CHANGE_TIME = 4 * 60  # 4 mins
	ON_EXPORT_LIMIT = 5000

	def __init__(self, db):
		super().__init__()
		
		self._db = db

	def _get_api(self):
		if self._api is None:
			self._api = None
		return None

	def _get_site_id(self):
		if self._site_id is None:
			pass
		return self._site_id

	def _save_to_db(self, data):
		with Session(self._db) as session:
			session.add(data)
			session.commit()

	def _get_feed_in_data(self):
		sql = text("""
			SELECT AVG(grid_power) AS ans FROM (
				SELECT grid_power FROM
				alphaess_usage WHERE
				(UTC_TIMESTAMP() - recorded_at) <= {time_window}
			) x
		""".format(time_window=self.TIME_WINDOW))

		with self._db.connect() as connection:
			return float(connection.execute(sql).one()[0] or 0)

	def _get_solar_price(self):
		sql = text("""
			SELECT sell_price FROM amber_pricing
			ORDER BY recorded_at DESC LIMIT 1
		""")

		with self._db.connect() as connection:
			return float(connection.execute(sql).one()[0] or 0)

	def _should_inverter_be_on(self, feed_in_avg, solar_price):
		if solar_price <= self.PRICE_CUTOFF:
			return 2

		if feed_in_avg > self.FEED_IN_CUTOFF:
			return 3

		return False

	def _get_last_changed(self):
		sql = text("""
			SELECT recorded_at, export_limit FROM goodwe_events
			WHERE changed = 1 ORDER BY recorded_at DESC
			LIMIT 1
		""")

		with self._db.connect() as connection:
			return connection.execute(sql).first()

	def _get_export_limit(self, should_be_on):
		if should_be_on:
			return self.ON_EXPORT_LIMIT
		else:
			return 0

	def _control_inverter(self, should_be_on, is_change):
		if should_be_on == 1:
			pass  # Ignore as just a periodic update
		elif should_be_on == 2:
			notifications.send("Turning inverter ON", "Solar prices are good")
		elif should_be_on == 3:
			notifications.send("Turning inverter ON", "Solar prices are bad but your usage is high")
		else:
			notifications.send("Turning inverter OFF", "Solar prices are negative and usage is low")

	def _save_to_db(self, data):
		with Session(self._db) as session:
			session.add(data)
			session.commit()

	@monitor(monitor_slug="control_goodwe_inverter")
	def do_task(self):
		now = datetime.now(timezone.utc)
		feed_in = self._get_feed_in_data()
		solar_price = self._get_solar_price()
		last_change = self._get_last_changed()
		last_change_delta = None if last_change is None else (now - last_change[0].replace(tzinfo=timezone.utc)).total_seconds()
		can_change = last_change is None or last_change_delta > self.MIN_CHANGE_TIME
		was_on = last_change is None or last_change[1] == self.ON_EXPORT_LIMIT
		should_be_on = self._should_inverter_be_on(feed_in, solar_price)
		is_change = can_change and (bool(was_on) != bool(should_be_on) or last_change is None)

		if not is_change and last_change_delta > 1 * 60 * 60:  # 1 hour
			should_be_on = 1

		if is_change:
			print("last_change=", last_change)
			print("last_change_delta=", last_change_delta)
			print("can_change=", can_change)
			print("was_on=", was_on)
			print("should_be_on=", should_be_on)
			print("is_change=", is_change)
			print(now, "GOODWE", " =", "Updating inverter to", should_be_on, "last change_delta =", last_change_delta, last_change)
			self._control_inverter(should_be_on, is_change)
			event = GoodweEvent(
				recorded_at=now,
				export_limit=self._get_export_limit(should_be_on),
				changed=is_change and should_be_on != 1
			)

			self._save_to_db(event)		
		else:
			print(now, "GOODWE", " =", "No change", should_be_on)
