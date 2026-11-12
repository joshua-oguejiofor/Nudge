import os

from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = 587
    SMTP_USER = os.getenv("SMTP_USER")
    TO_USER = os.getenv("TO_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SECRET_KEY = os.getenv('SECRET_KEY')
    CELERY_BROKER = os.getenv("CELERY_BROKER")
    CELERY_BACKEND = os.getenv("CELERY_BACKEND")
    
    


settings = Settings()