FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /happ
WORKDIR /happ
RUN apt-get update && apt-get install -y libpq-dev build-essential python-dev
ADD ./requires.txt /happ/
RUN pip install -r requires.txt
ADD . /happ
