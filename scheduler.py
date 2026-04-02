import logging
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from macro_brief import run_brief

logging.basicConfig(
stream=sys.stdout,
level=logging.INFO,
format=”%(asctime)s [%(levelname)s] %(message)s”,
)

scheduler = BlockingScheduler(timezone=“America/Denver”)  # MST/MDT

# 6:00 AM Mountain Time every day

scheduler.add_job(
run_brief,
CronTrigger(hour=6, minute=0, timezone=“America/Denver”),
name=“macro_brief_daily”,
misfire_grace_time=300,   # allow up to 5 min late start
coalesce=True,
)

if **name** == “**main**”:
logging.info(“Scheduler started – brief fires daily at 06:00 MST/MDT”)
try:
scheduler.start()
except (KeyboardInterrupt, SystemExit):
logging.info(“Scheduler stopped.”)
