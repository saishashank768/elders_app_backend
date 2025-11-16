web: gunicorn elders_helping.wsgi:application --bind 0.0.0.0:$PORT --workers=3
worker: celery -A elders_helping worker --loglevel=info
beat: celery -A elders_helping beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
