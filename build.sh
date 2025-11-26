#!/usr/bin/env bash
set -o errexit
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py setup_site
python manage.py collectstatic --no-input
python manage.py createsuperuser --noinput --username "${DJANGO_SUPERUSER_USERNAME:-Neikiam}" --email "${DJANGO_SUPERUSER_EMAIL:-neikiam@500gmail.com}" 2>/dev/null || echo "Superuser already exists or creation skipped"
