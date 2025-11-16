"""
Deployment instructions / helpers for Render (Docker).

Render: configure a Web Service (Docker) and add environment variables from `.env.example`.
Run with:
  gunicorn elders_helping.wsgi:application --bind 0.0.0.0:$PORT --workers=3

Create separate services for Celery worker and beat pointing to same image/registry.
"""

def render_notes():
    return True
