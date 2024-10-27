#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Celery worker in the background
# echo "Starting Celery worker..."
# celery -A phoenix worker --loglevel=info -P solo &

# # Start Celery Beat (scheduler) in the background
# echo "Starting Celery Beat..."
# celery -A phoenix beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn phoenix.wsgi:application --bind 0.0.0.0:8000 --timeout 120
