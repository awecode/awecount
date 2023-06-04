#!/bin/bash

if [ -z "$PORT" ]; then
    export PORT=8000
fi

python manage.py migrate -v 0
python manage.py collectstatic  --noinput

gunicorn awecount.wsgi:application --bind 0.0.0.0:$PORT