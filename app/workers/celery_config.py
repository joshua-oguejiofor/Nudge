import logging

from celery import Celery
from celery.schedules import crontab

from app.config import settings

logger = logging.getLogger(__name__)


celery_app = Celery(
    "nudge",
    broker= settings.CELERY_BROKER,
    backend= settings.CELERY_BACKEND,    
)

celery_app.conf.imports = "app.workers.tasks"


celery_app.conf.update(
    task_serializer='json',          # Serializes task payload data into JSON format
    result_serializer='json',        # Serializes task return values into JSON format
    accept_content=['json'],         # Restricts accepted content types to JSON for security
    timezone="Africa/Lagos",         # Sets the local timezone for periodic tasks (Celery Beat)
    enable_utc=True,                 # Enables UTC as the standard base timezone for internal datetimes
    broker_connection_retry_on_startup=True, # Automatically retries connecting to the broker (Redis) when the worker starts
    result_expires=3600,             # Time in seconds (1 hour) before task results expire in the backend
    task_ignore_result=True,         # Disables storing task return values to save memory/storage since results aren't needed
    worker_prefetch_multiplier=1,    # Limits each worker process to fetching only 1 task at a time for fair task distribution
    task_time_limit=120,             # Hard time limit (120 seconds) after which a runaway task is forcefully killed
    task_soft_time_limit=100,        # Soft time limit that raises a SoftTimeLimitExceeded exception to allow graceful cleanup before the hard limit
    task_acks_late=True,             # Acknowledges tasks after execution finishes rather than when picked up, ensuring safety if a worker crashes

)

celery_app.conf.beat_schedule = {
    "remember to complete your task today":{
        "task": "send_todo_reminders_task",
        "schedule": crontab(hour="*/6"),
        
    }
}



