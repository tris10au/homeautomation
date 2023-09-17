from threading import Thread
from sentry_sdk import capture_exception
import time
import traceback


class Task(Thread):
	keep_running = True

	def __init__(self):
		super().__init__()
		self.daemon = True
		self.name = self.title


	def run(self):
		errors = 0
		while self.keep_running and errors < 5:
			try:
				self.do_task()
				errors -= 1
				if errors < 0:
					errors = 0
				time.sleep(self.frequency)
			except Exception as exc:
				capture_exception(exc)
				traceback.print_exception(exc)
				errors += 1
				time.sleep(20 * errors)
