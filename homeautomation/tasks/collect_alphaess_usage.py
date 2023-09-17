from openpower.alphaess import AlphaESS
from datetime import datetime, timezone
import os
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from . import Task
from homeautomation.models.alphaess import *
from sentry_sdk.crons import monitor


class CollectAlphaESSUsage(Task):
	title = "Collect AlphaESS Usage Data"
	frequency = 30  # seconds
	_api = None
	_system_id = None


	def __init__(self, db):
		super().__init__()

		self._db = db

	def _get_api(self):
		if self._api is None:
			self._api = AlphaESS(
				app_id=os.environ.get("ALPHAESS_APP_ID"),
				app_secret=os.environ.get("ALPHAESS_APP_SECRET")
			)
		return self._api

	def _get_system_id(self):
		if self._system_id is None:
			if os.environ.get("ALPHAESS_SYSTEM_ID") is not None:
				self._system_id = os.environ.get("ALPHAESS_SYSTEM_ID")
			else:
				systems = self._get_api().list_systems()
				assert len(systems) > 0, "No system ID specified and system list is empty"
				self._system_id = systems[0]["sysSn"]
		return self._system_id

	def _save_to_db(self, data):
		with Session(self._db) as session:
			session.add(data)
			session.commit()

	@monitor(monitor_slug="collect_alphaess_usage")
	def do_task(self):
		usage = self._get_api().for_device(self._get_system_id()).get_realtime_power_usage()
		data = AlphaESSUsage(
			recorded_at=datetime.now(timezone.utc),
			solar_power=usage["ppv"],
			grid_power=usage["pgrid"],
			battery_power=usage["pbat"],
			load=usage["pload"],
			charge_level=usage["soc"]
		)
		print(datetime.now(timezone.utc), " ALPHAESS =", usage["pgrid"], " , ", usage["pload"])
		self._save_to_db(data)
