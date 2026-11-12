import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.email_server import send_otp_email, send_todo_reminder
from app.extensions import db
from app.main import app
from app.model import Todo
from app.utility import TaskPriority

from .celery_config import celery_app

logger = logging.getLogger(__name__)



@celery_app.task(
    name="send_todo_reminders_task",  
    autoretry_for=(Exception,),  
    retry_backoff=True,
    retry_jitter=True, 
    max_retries=3,
    )
def send_todo_reminders_task():
    try:
        with app.app_context():
            
            todo_list = None
            todos = db.session.scalars(
                select(Todo)
                .options(selectinload(Todo.user))
                .where(
                    Todo.priority.in_([TaskPriority.URGENT, TaskPriority.HIGH])
                )
            ).all()
            
            if todos:
                todo_list = [
                    {
                    "title": todo.title,
                    "priority": todo.priority,
                    "completed": todo.completed 
                
                } for todo in todos]
            
            send_todo_reminder(todo_list)
    except Exception:
        logger.exception("Failed to send email task.")
        raise 


@celery_app.task(
    name="send_otp",   
    autoretry_for=(Exception,), 
    retry_backoff=True, 
    retry_jitter=True,
    max_retries=3,)
def send_otp_task(otp, subject):
    try:
        send_otp_email(otp, subject)
    except Exception:
        logger.exception("Failed to send otp task.")
        raise
