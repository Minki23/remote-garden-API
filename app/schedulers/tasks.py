from app.core.celery.celery_app import celery_app
from app.models.enums import ScheduleActionType
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.schedulers.tasks.run_scheduled_action")
def run_scheduled_action(garden_id: int, action: ScheduleActionType):
    logger.info(f"Running scheduled action: {action} for garden {garden_id}")
    # Dispatch MQTT or call service layer logic


@celery_app.task(name="app.schedulers.tasks.demo_log")
def demo_log():
    logger.info("DEMO_LOG: Cyclic test task is running!")
