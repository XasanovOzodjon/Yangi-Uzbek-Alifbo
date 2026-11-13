from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from data.messages import get_settings_text
from keyboards.inline import get_settings_keyboard
from utils.db_api import get_or_create_telegram_user, update_user_settings


async def bot_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sozlamalar menyusini ko'rsatadi."""
    message = update.message
    if not message:
        return

    user = update.effective_user
    tg_user = await get_or_create_telegram_user(user)

    bot_lang = tg_user.bot_lang if tg_user else "yangi"
    translate_cyrillic = tg_user.translate_cyrillic if tg_user else False
    translate_mixed = tg_user.translate_mixed if tg_user else False

    text = get_settings_text(
        bot_lang=bot_lang,
        translate_cyrillic=translate_cyrillic,
        translate_mixed=translate_mixed
    )
    keyboard = get_settings_keyboard(
        bot_lang=bot_lang,
        translate_cyrillic=translate_cyrillic,
        translate_mixed=translate_mixed
    )

    await message.reply_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sozlamalar tugmasi bosilganda qiymatni o'zgartiradi va xabarni yangilaydi."""
    query = update.callback_query
    if not query or not query.data:
        return

    user = update.effective_user
    tg_user = await get_or_create_telegram_user(user)
    if not tg_user:
        await query.answer()
        return

    bot_lang = tg_user.bot_lang
    translate_cyrillic = tg_user.translate_cyrillic
    translate_mixed = tg_user.translate_mixed

    data = query.data
    answer_text = ""

    if data == "toggle_lang":
        bot_lang = "eski" if bot_lang == "yangi" else "yangi"
        await update_user_settings(user.id, bot_lang=bot_lang)
        answer_text = "Til o'zgartirildi / Til özgartirildi"
    elif data == "toggle_cyrillic":
        translate_cyrillic = not translate_cyrillic
        await update_user_settings(user.id, translate_cyrillic=translate_cyrillic)
        status = "yoqildi" if translate_cyrillic else "o'chirildi"
        answer_text = f"Kirillchadan o'girish {status}"
    elif data == "toggle_mixed":
        translate_mixed = not translate_mixed
        await update_user_settings(user.id, translate_mixed=translate_mixed)
        status = "yoqildi" if translate_mixed else "o'chirildi"
        answer_text = f"Aralash matnlarni o'girish {status}"

    new_text = get_settings_text(
        bot_lang=bot_lang,
        translate_cyrillic=translate_cyrillic,
        translate_mixed=translate_mixed
    )
    new_keyboard = get_settings_keyboard(
        bot_lang=bot_lang,
        translate_cyrillic=translate_cyrillic,
        translate_mixed=translate_mixed
    )

    try:
        await query.edit_message_text(
            text=new_text,
            reply_markup=new_keyboard,
            parse_mode=ParseMode.HTML
        )
    except Exception:
        pass

    await query.answer(answer_text)


def register_handlers(dp):
    dp.add_handler(CommandHandler(["settings", "sozlamalar"], bot_settings))
    dp.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.Regex(r"^(⚙️\s*Sozlamalar|⚙️\s*Sozlamalar)$"),
            bot_settings
        )
    )
    dp.add_handler(
        CallbackQueryHandler(
            settings_callback,
            pattern=r"^toggle_(lang|cyrillic|mixed)$"
        )
    )
