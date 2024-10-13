from celery import Celery


celery_app = Celery('tasks', broker='redis://redis/0', backend='redis://redis/0')

celery_app.conf.broker_connection_retry_on_startup = True
celery_app.autodiscover_tasks(['infra.celery.tasks'])
