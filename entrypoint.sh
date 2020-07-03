#!/bin/bash

echo "[$(date -u "+%Y-%m-%d  %H:%M:%S +0000")] [INFO] Starting disty"
echo "[$(date -u "+%Y-%m-%d  %H:%M:%S +0000")] Creating superuser"
python manage.py createsuperuser --noinput

echo "[$(date -u "+%Y-%m-%d  %H:%M:%S +0000")] Starting Gunicorn"
gunicorn --bind 0.0.0.0:8000 -w 4 disty_online.wsgi --preload