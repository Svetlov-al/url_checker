from .celery_worker import app


@app.task
def vt_validate(topic: str = 'links', batch_size: int = 1, max_attempts: int = 5):
    return None
