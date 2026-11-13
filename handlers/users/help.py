from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters
from data.messages import get_help_text
from utils.db_api import get_or_create_telegram_user


async def bot_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    tg_user = await get_or_create_telegram_user(user)
    bot_lang = tg_user.bot_lang if tg_user else "yangi"

    text = get_help_text(bot_lang=bot_lang)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


def register_handlers(dp):
    dp.add_handler(CommandHandler(["help", "yordam"], bot_help))
    dp.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.Regex(r"^(ℹ️\s*Qoʻllanma|ℹ️\s*Qöllanma|ℹ️\s*Yordam)$"),
            bot_help
        )
    )
