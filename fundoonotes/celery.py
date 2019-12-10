from __future__ import absolute_import, unicode_literals
import os
import sys

import requests
from celery import Celery
from celery.schedules import crontab
from celery.task import task
from django.conf import settings

# sys.path.append(os.path.abspath('fundoonotes'))
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundoonotes.settings')
app = Celery('name', broker="amqp://guest@localhost//")
app.conf.beat_schedule = {'test-task': {'task': 'celery.email', 'schedule': crontab(), }, }
# app.config_from_object(settings, namespace='CELERY')
# app.autodiscover_tasks()

@task
def email():
    print("adgfsajcvjsahdvgfjghsvfkjbvkjdsgfbvbkxzbvgfkjdfsgkligj")
    requests.get(url="http://localhost:8000/api/celery", )