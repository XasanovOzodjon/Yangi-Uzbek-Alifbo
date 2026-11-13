from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from converter.services.alphabet import process_text
from utils.misc.text_splitter import split_text_chunks


async def bot_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post = update.channel_post
    if not post or not post.text:
        return

    converted_text = process_text(post.text, translate_cyrillic=True, translate_mixed=True)
    if converted_text == post.text:
        return

    if len(converted_text) <= 4096:
        await context.bot.send_message(chat_id=post.chat_id, text=converted_text)
    else:
        chunks = split_text_chunks(converted_text, max_len=4096)
        for chunk in chunks:
            await context.bot.send_message(chat_id=post.chat_id, text=chunk)


def register_handlers(dp):
    dp.add_handler(
        MessageHandler(
            filters.ChatType.CHANNEL & filters.TEXT,
            bot_channel_post
        )
    )
