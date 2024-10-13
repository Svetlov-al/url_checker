# broker_url = settings.redis_url # noqa
# result_backend = broker_url # noqa
accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'
timezone = 'Europe/Moscow'
broker_connection_retry_on_startup = True
CELERY_TASK_ACKS_LATE = True

# Планирование задач
beat_schedule = {}

CELERY_BEAT_SCHEDULE = beat_schedule
"""Запуск рабочего процесса Celery celery -A celery_worker.celery_app worker
--loglevel=info.

Запуск Celery Beat celery -A celery_worker.celery_app beat
--loglevel=info

 Запуск flower с базовой аутентификацией celery -A celery_worker flower
--basic_auth=user:password

"""
