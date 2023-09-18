from datetime import datetime, timezone
import os
import logging
from . import Task
from homeautomation import notifications
from sentry_sdk.crons import monitor
import subprocess


LOGGER = logging.getLogger(__name__)


class NotifyDiskUsage(Task):
	title = "Notify On Disk Usage"
	frequency = 300

	NOTIFY_FREQUENCY = 8 * 60 * 60  # 2 hours
	LIMIT = 70

	_last_notified = None

	def __init__(self, db):
		super().__init__()

	def _get_usage(self):
		output = subprocess.run(["df", "/", "--output=pcent"], capture_output=True, check=True).stdout.decode()
		output = int(output.split("\n")[1].strip().replace("%", ""))

		return output

	@monitor(monitor_slug="notify_disk_usage")
	def do_task(self):
		now = datetime.now(timezone.utc)
		usage = self._get_usage()

		if usage > self.LIMIT and (self._last_notified is None or (now - self._last_notified).total_seconds() > self.NOTIFY_FREQUENCY):
			LOGGER.warning("Limit exceeded, notifying: %s (%s)", usage, self._last_notified)
			notifications.send("Disk is getting full", "Usage is " + str(usage) + "%")
			self._last_notified = now
		else:
			LOGGER.info("Disk usage is nominal at %s %", usage)
