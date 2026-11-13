from django.core.management.commands.runserver import Command as BaseRunserverCommand
from converter.bot_runner import start_bot_background


class Command(BaseRunserverCommand):
    help = "Django veb-serverini va Telegram Botni birga ishga tushirish"

    def inner_run(self, *args, **options):
        start_bot_background()
        super().inner_run(*args, **options)
