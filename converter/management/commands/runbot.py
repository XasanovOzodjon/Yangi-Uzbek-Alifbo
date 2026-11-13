from django.core.management.base import BaseCommand
import handlers
from loader import application, dp
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def post_init(app):
    await set_default_commands(app)
    await on_startup_notify(app)


class Command(BaseCommand):
    help = "Telegram Botni ishga tushirish"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Bot ishga tushirilmoqda..."))
        handlers.register_handlers(dp)
        application.post_init = post_init
        application.run_polling()
