#!/usr/bin/env bash
set -o errexit

python manage.py migrate --noinput
python manage.py seed_demo_data
python manage.py seed_vestibulando_content
python manage.py bootstrap_superuser
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-10000}"
