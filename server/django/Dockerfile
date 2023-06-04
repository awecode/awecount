FROM python:3.11.2-slim-buster

RUN apt-get update && apt-get install -y libmagic-dev libpq-dev libffi-dev musl-dev libfreetype6-dev

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED 1

COPY . .

RUN apt-get update \
  && apt-get -y install gcc \
  && apt-get clean \
  && pip install --upgrade pip \
  && pip install -r requirements/frozen.txt

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]