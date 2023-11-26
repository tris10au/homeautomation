import os
import logging
from homeautomation.tasks.collect_alphaess_usage import CollectAlphaESSUsage
from homeautomation.tasks.collect_amber_prices import CollectAmberPrices
from homeautomation.tasks.control_goodwe_inverter import ControlGoodweInverter
from homeautomation.tasks.notify_negative_prices import NotifyPriceChanges
from homeautomation.tasks.notify_on_disk_usage import NotifyDiskUsage
from homeautomation.models.base import Base
from sqlalchemy import create_engine
import sentry_sdk


SENTRY_DSN = os.environ.get("SENTRY_DSN")

sentry_sdk.init(
    dsn=SENTRY_DSN,

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

logging.basicConfig(
	format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
	level=logging.INFO,
	encoding="utf-8"
)
LOGGER = logging.getLogger(__name__)

engine = create_engine(os.environ.get("DSN"))
Base.metadata.create_all(engine)

tasks = [
	CollectAlphaESSUsage,
	CollectAmberPrices,
#	ControlGoodweInverter,
	NotifyPriceChanges,
	NotifyDiskUsage
]

threads = []

LOGGER.info("Starting all tasks")

for task in tasks:
	runnable = task(engine)
	runnable.start()
	threads.append(runnable)

for thread in threads:
	thread.join()
