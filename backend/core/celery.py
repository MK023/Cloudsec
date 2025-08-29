import multiprocessing
import os

from celery import Celery

try:
    multiprocessing.set_start_method("spawn")
except RuntimeError:
    pass

# Ensure the Django settings module is set before importing Django
# This is necessary for Celery to work correctly with Django.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")  # Initialize Celery app with the name 'core'
app.config_from_object("django.conf:settings", namespace="CELERY")  # Load settings from Django's settings module
app.autodiscover_tasks()  # Automatically discover tasks in all installed Django apps
print(
    ">>> celery.py loaded and autodiscover_tasks called <<<"
)  # This line is for debugging purposes to confirm the file is loaded
