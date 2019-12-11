# from __future__ import absolute_import, unicode_literals
# import os
# import sys
# 
# import requests
# from celery import Celery
# from celery.schedules import crontab
# from celery.task import task
# from django.conf import settings
# sys.path.append(os.path.abspath('fundoonotes'))
# # from fundoonotes.notes import tasks
# 
# 
# # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundoonotes.settings')
# app = Celery('name', broker="amqp://guest@localhost//")
# app.conf.beat_schedule = {'test-task': {'task': 'tasks.email', 'schedule': crontab(), }, }
# # app.config_from_object(settings, namespace='CELERY')
# # app.autodiscover_tasks()
# 
# # @task
# # def email():
# #     print("adgfsajcvjsahdvgfjghsvfkjbvkjdsgfbvbkxzbvgfkjdfsgkligj")
# #     requests.get(url="http://localhost:8000/api/celery", )


from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundoonotes.settings')
app = Celery('Sending_Emails')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.beat_schedule = {'test-task': {'task': 'tasks.email', 'schedule': crontab(),}, }

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))