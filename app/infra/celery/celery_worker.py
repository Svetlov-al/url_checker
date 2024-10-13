from celery import Celery


celery_app = Celery('tasks')
celery_app.config_from_object('celery_config')


@celery_app.task
def test_task() -> None:
    print("hello from celery")
