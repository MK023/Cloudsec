# Celery task example
# This file should be placed in backend/core/tasks.py

from celery import shared_task

@shared_task
def add(x, y):
    return x + y