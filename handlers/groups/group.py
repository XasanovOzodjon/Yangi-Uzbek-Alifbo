from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, MessageHandler, filters
from converter.services.alphabet import process_text
from utils.db_api import get_or_create_telegram_user, save_conversion_log
from utils.misc.text_splitter import split_into_copyable_chunks


async def bot_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    text_to_convert = message.text or message.caption
    if not text_to_convert:
        return

    bot_username = context.bot.username
    should_respond = False

    if message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id:
        should_respond = True
    elif bot_username and f"@{bot_username}" in text_to_convert:
        should_respond = True
        text_to_convert = text_to_convert.replace(f"@{bot_username}", "").strip()

    if not should_respond or not text_to_convert:
        return

    user = update.effective_user
    tg_user = await get_or_create_telegram_user(user)

    translate_cyrillic = tg_user.translate_cyrillic if tg_user else False
    translate_mixed = tg_user.translate_mixed if tg_user else False

    converted_text = process_text(
        text_to_convert,
        translate_cyrillic=translate_cyrillic,
        translate_mixed=translate_mixed
    )

    chunks = split_into_copyable_chunks(converted_text)
    if not chunks:
        chunks = [f"<code>{converted_text}</code>"]

    first = True
    for chunk in chunks:
        if first:
            await message.reply_text(
                chunk,
                reply_to_message_id=message.message_id,
                parse_mode=ParseMode.HTML
            )
            first = False
        else:
            await message.reply_text(
                chunk,
                parse_mode=ParseMode.HTML
            )

    await save_conversion_log(
        user_id=user.id if user else None,
        content_type="group_text",
        original_text=text_to_convert[:1000],
        converted_text=converted_text[:1000],
        char_count=len(text_to_convert)
    )


def register_handlers(dp):
    dp.add_handler(
        MessageHandler(
            (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP) & (filters.TEXT | filters.CAPTION) & ~filters.COMMAND,
            bot_group_message
        )
    )
