#!/usr/bin/env bash
# Script de build para Render.
# Configurar en el dashboard: Build Command = ./build.sh
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
