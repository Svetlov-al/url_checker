from celery import Celery


app = Celery(__name__, broker='redis://redis/0', backend='redis://redis/0')

app.autodiscover_tasks()

app.conf.accept_content = ['json']
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.timezone = 'Europe/Moscow'
app.conf.broker_connection_retry_on_startup = True
app.conf.celery_task_acks_late = True
app.conf.task_acks_late = True
app.conf.beat_schedule = {}


@app.task
def debug():
    return {"Success": "Celery is Working"}
