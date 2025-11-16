#!/usr/bin/env bash
python manage.py createsuperuser --noinput --username ${DJANGO_SUPERUSER_USERNAME:-admin} --email ${DJANGO_SUPERUSER_EMAIL:-admin@example.com} || true
