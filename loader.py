import os
import django

# Django muhitini sozlash
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from telegram.ext import ApplicationBuilder
from data import config

application = ApplicationBuilder().token(config.BOT_TOKEN).build()
bot = application.bot
dp = application
