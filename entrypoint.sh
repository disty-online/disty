#!/bin/bash
set -eu
echo "[$(date -u "+%Y-%m-%d %H:%M:%S +0000")] [INFO] Starting disty"

echo "[$(date -u "+%Y-%m-%d %H:%M:%S +0000")] [INFO] Running migrations"
echo ${SECRET_KEY} > /dev/null
echo ${DJANGO_ALLOWED_HOSTS} > /dev/null
python manage.py migrate

echo "[$(date -u "+%Y-%m-%d %H:%M:%S +0000")] Creating superuser"
python manage.py createsuperuser --noinput && :

echo "[$(date -u "+%Y-%m-%d %H:%M:%S +0000")] Starting Gunicorn"
gunicorn --bind 0.0.0.0:8000 -w 4 disty_online.wsgi --preload --access-logfile - --error-logfile -

