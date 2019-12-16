from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from .settings import CELERY_BROKER_URL

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundoonotes.settings')
app = Celery("fundoonotes", broker=CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {'add-every-30-seconds': {'task': 'notes.tasks.email', 'schedule': 30.0, }, }


# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))
