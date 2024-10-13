from infra.celery.celery_worker import celery_app


@celery_app.task()
def debug():
    return {"Success": "Celelry is Working"}
