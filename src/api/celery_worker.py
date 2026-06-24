from celery import Celery
from os import getenv

celery_app = Celery(
    "celery_worker",
    broker=getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
    include=["api.core.text_analysis.ebook_processing", "api.core.anki"],
)
