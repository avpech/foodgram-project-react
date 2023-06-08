#!/bin/sh

python manage.py collectstatic --no-input
gunicorn foodgram.wsgi:application --bind 0:8000