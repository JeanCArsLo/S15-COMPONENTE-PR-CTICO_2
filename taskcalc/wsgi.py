"""Punto de entrada WSGI (usado por gunicorn en producción)."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskcalc.settings")

application = get_wsgi_application()
