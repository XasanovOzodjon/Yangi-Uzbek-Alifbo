import os
import sys
from django.apps import AppConfig


class ConverterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'converter'

    def ready(self):
        if 'runserver' in sys.argv:
            is_worker = (os.environ.get('RUN_MAIN') == 'true') or ('--noreload' in sys.argv)
            if is_worker:
                from .bot_runner import start_bot_background
                start_bot_background()
