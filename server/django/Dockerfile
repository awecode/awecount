FROM python:3.12.7-alpine AS backend

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apk add --no-cache \
  "libpq" \
  "libxslt" \
  "xmlsec"

COPY requirements.txt ./

RUN apk add --no-cache libffi-dev
RUN apk add --no-cache --virtual .build-deps \
  "bash~=5.2" \
  "g++" \
  "gcc" \
  "git" \
  "make" \
  "postgresql-dev" \
  "libc-dev" \
  "linux-headers" \
  && \
  pip install -r requirements.txt --compile --no-cache-dir \
  && \
  apk del .build-deps

# Add in Django deps and generate Django's static files
COPY manage.py manage.py
COPY . .

RUN apk --no-cache add "bash~=5.2"
COPY ./bin ./bin/

RUN mkdir -p /app/logs
RUN chmod +x ./bin/*

# Expose container port and run entry point script
EXPOSE 8000
