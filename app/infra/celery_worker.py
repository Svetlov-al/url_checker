from celery import Celery
from celery.schedules import crontab


app = Celery(__name__, broker='redis://redis/0', backend='redis://redis/0')

app.autodiscover_tasks()

app.conf.accept_content = ['json']
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.timezone = 'Europe/Moscow'
app.conf.broker_connection_retry_on_startup = True
app.conf.celery_task_acks_late = True
app.conf.task_acks_late = True

# => Словарь для определения отложенных задач
app.conf.beat_schedule = {
    "reset_keys_limit": {
        "task": "app.infra.tasks.reset_keys_limit",  # Задача обновления лимита ключей
        "schedule": crontab(hour="0", minute="0"),  # Каждый день в полночь
    },
    "vt_validate": {
        "task": "app.infra.tasks.vt_validate",  # Задача проверки валидности ссылок для Virus Total
        "schedule": crontab(hour="*", minute="0"),  # Каждый час ровно в начале часа
    },
    "ae_validate": {
        "task": "app.infra.tasks.ae_validate",  # Задача проверки валидности ссылок для Abusive Experience
        "schedule": crontab(hour="*", minute="0"),  # Каждый час ровно в начале часа
    },
}


@app.task
def debug():
    return {"Success": "Celery is Working"}
