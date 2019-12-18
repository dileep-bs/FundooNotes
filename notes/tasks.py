import requests
from celery.task import task
from fundoonotes.settings import user_url


@task()
def email():
    requests.get(url=user_url)


