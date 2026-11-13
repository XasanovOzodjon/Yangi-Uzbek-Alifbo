import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

import handlers
from loader import application, dp
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def post_init(app):
    await set_default_commands(app)
    await on_startup_notify(app)


def main():
    handlers.register_handlers(dp)
    application.post_init = post_init
    application.run_polling()


if __name__ == "__main__":
    main()
