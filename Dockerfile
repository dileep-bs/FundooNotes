FROM python:3.6
ENV PYTHONDONTWRITEBYCODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/* build-essential libssl-dev python3-dev python3-pip
RUN mkdir /fundoonotes
WORKDIR /fundoonotes
COPY requirements.txt /fundoonotes/
RUN pip install -r requirements.txt
#RUN apt-get update
#RUN apt-get install build-essential libssl-dev libffi-dev python3-dev -y
#RUN apt-get install python3-pip -y
COPY . ./
CMD ["python","manage.py","runserver","0.0.0.0:8000"]
