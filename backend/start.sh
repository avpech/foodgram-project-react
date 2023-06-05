gunicorn foodgram.wsgi:application --bind 0:8000
python manage.py migrate
python manage.py collectstatic --no-input