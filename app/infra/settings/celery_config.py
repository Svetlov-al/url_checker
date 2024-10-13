accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'
timezone = 'Europe/Moscow'
broker_connection_retry_on_startup = True
CELERY_TASK_ACKS_LATE = True

# Планирование задач
beat_schedule = {}

CELERY_BEAT_SCHEDULE = beat_schedule
