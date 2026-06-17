from celery import Celery

celery_app = Celery(
    "celery_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["api.core.text_analysis.ebook_processing", "api.core.anki"],
)
