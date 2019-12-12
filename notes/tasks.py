import requests
from celery.task import task


# @task(bind=True)
# def debug_task(self):
#     print("yes working")
#     print('Request: {0!r}'.format(self.request))


@task()
def email():
    requests.get(url="http://localhost:8000/api/celery")


