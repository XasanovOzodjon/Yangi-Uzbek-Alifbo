from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, MessageHandler, filters
from converter.services.alphabet import process_text
from utils.db_api import get_or_create_telegram_user, save_conversion_log
from utils.misc.text_splitter import split_into_copyable_chunks


async def bot_media_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    caption = message.caption
    if not caption:
        await message.reply_text(
            "Rasm yoki video tagiga text yozib tashang birodar :)",
            reply_to_message_id=message.message_id
        )
        return

    user = update.effective_user
    tg_user = await get_or_create_telegram_user(user)

    translate_cyrillic = tg_user.translate_cyrillic if tg_user else False
    translate_mixed = tg_user.translate_mixed if tg_user else False

    converted_text = process_text(
        caption,
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

    media_type = "photo" if message.photo else ("video" if message.video else "media")
    await save_conversion_log(
        user_id=user.id if user else None,
        content_type=media_type,
        original_text=caption[:1000],
        converted_text=converted_text[:1000],
        char_count=len(caption)
    )


def register_handlers(dp):
    dp.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & (
                filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.AUDIO | filters.VOICE
            ),
            bot_media_caption
        )
    )
