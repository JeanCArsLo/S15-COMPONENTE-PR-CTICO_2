"""
Alias WSGI para Render.

El comando por defecto de Render es `gunicorn app:app`, así que este módulo
expone la aplicación de taskcalc/wsgi.py con ese nombre. Si en el dashboard
configuras `gunicorn taskcalc.wsgi:application`, este archivo simplemente
no se usa.
"""
from taskcalc.wsgi import application

app = application
