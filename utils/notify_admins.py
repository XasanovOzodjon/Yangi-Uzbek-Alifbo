import logging
from data.config import ADMINS


async def on_startup_notify(application):
    for admin in ADMINS:
        try:
            await application.bot.send_message(admin, "Bot ishga tushdi")
        except Exception as err:
            logging.exception(err)
