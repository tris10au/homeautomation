from threading import Thread
from sentry_sdk import capture_exception
import time
import logging
import traceback


LOGGER = logging.getLogger(__name__)


class Task(Thread):
	keep_running = True

	def __init__(self):
		super().__init__()
		self.daemon = True
		self.name = self.title


	def run(self):
		errors = 0
		while self.keep_running and errors < 10:
			try:
				self.do_task()
				errors -= 1
				if errors < 0:
					errors = 0
				time.sleep(self.frequency)
			except Exception as exc:
				capture_exception(exc)

				LOGGER.exception("An exception occured during the task '%s', count = %s", self.title, errors)
				errors += 1
				time.sleep(20 + (2 ** errors))
