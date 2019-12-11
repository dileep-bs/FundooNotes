from celery.decorators import task
from django.core.mail import EmailMessage
import time

@task(name="Sending_Emails")
def send_email(to_email,message):
    time1 = 1
    while(time1 != 5):
        print("Sending Email")
        email = EmailMessage('Checking Asynchronous Task', message+str(time1), to=['dileep.bs@yahoo.com'])
        email.send()
        time.sleep(1)
        time1 += 1