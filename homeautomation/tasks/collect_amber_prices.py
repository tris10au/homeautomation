from openpower.amber import Amber
from datetime import datetime, timezone
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from . import Task
from homeautomation.models.amber import *
from sentry_sdk.crons import monitor


class CollectAmberPrices(Task):
	title = "Collect Amber Price Data"
	frequency = 5 * 60  # 5 mins
	_api = None
	_site_id = None


	def __init__(self, db):
		super().__init__()
		
		self._db = db

	def _get_api(self):
		if self._api is None:
			self._api = Amber(
				token=os.environ.get("AMBER_TOKEN")
			)
		return self._api

	def _get_site_id(self):
		if self._site_id is None:
			if os.environ.get("AMBER_SITE_ID") is not None:
				self._site_id = os.environ.get("AMBER_SITE_ID")
			else:
				systems = [s for s in self._get_api().list_sites() if s["status"] == "active"]
				assert len(systems) > 0, "No site ID specified and site list is empty"
				self._site_id = systems[0]["id"]
		return self._site_id

	def _save_to_db(self, data):
		with Session(self._db) as session:
			session.add(data)
			session.commit()

	def update_frequency(self, end_time):
		delta = int((end_time - datetime.now(timezone.utc)).total_seconds())

		if delta > (5 * 60 + 30) or delta <= 0:  # 5 mins
			self.frequency = 5 * 60
		else:
			self.frequency = delta + 5  # Offset to make sure it captures the new price

		print("frequency = ", self.frequency)

	@monitor(monitor_slug="collect_amber_prices")
	def do_task(self):
		usage = self._get_api().for_site(self._get_site_id()).get_current_prices(previous=0, next=0)

		general = [s for s in usage if s["channelType"] == "general"][0]
		feed_in = [s for s in usage if s["channelType"] == "feedIn"][0]

		data = AmberPrice(
			recorded_at=datetime.now(timezone.utc),
			start=datetime.fromisoformat(general["startTime"]),
			end=datetime.fromisoformat(general["endTime"]),
			purchase_price=general["perKwh"],
			sell_price=feed_in["perKwh"],
			spot_price=general["spotPerKwh"],
			purchase_descriptor=general["descriptor"],
			sell_descriptor=feed_in["descriptor"],
			estimated=general["estimate"],
			renewables=general["renewables"],
			spike=general["spikeStatus"],
			tariff=general["tariffInformation"]["period"] if "tariffInformation" in general else None
		)

		print(datetime.now(timezone.utc), " AMBER =", general["perKwh"], feed_in["perKwh"])

		self._save_to_db(data)
		self.update_frequency(datetime.fromisoformat(general["endTime"]))
