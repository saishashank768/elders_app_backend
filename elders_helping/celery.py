import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elders_helping.settings')
app = Celery('elders_helping')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
