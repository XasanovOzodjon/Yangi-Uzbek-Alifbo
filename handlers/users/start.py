from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes
from data.messages import get_start_text
from keyboards.default import get_main_menu_keyboard
from utils.db_api import get_or_create_telegram_user


async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    tg_user = await get_or_create_telegram_user(user)
    bot_lang = tg_user.bot_lang if tg_user else "yangi"

    text = get_start_text(user.full_name or "Foydalanuvchi", bot_lang=bot_lang)
    keyboard = get_main_menu_keyboard(bot_lang=bot_lang)

    await update.message.reply_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )


def register_handlers(dp):
    dp.add_handler(CommandHandler("start", bot_start))
