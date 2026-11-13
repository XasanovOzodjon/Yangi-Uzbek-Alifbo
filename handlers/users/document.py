import io
from pathlib import Path
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes, MessageHandler, filters
from converter.services.docx_service import convert_docx_file
from converter.services.pdf_service import convert_pdf_file
from utils.db_api import get_or_create_telegram_user, save_conversion_log


async def bot_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.document:
        return

    user = update.effective_user
    tg_user = await get_or_create_telegram_user(user)
    bot_lang = tg_user.bot_lang if tg_user else "yangi"
    translate_cyrillic = tg_user.translate_cyrillic if tg_user else False
    translate_mixed = tg_user.translate_mixed if tg_user else False

    doc = message.document
    file_name = doc.file_name or "document"
    file_ext = Path(file_name).suffix.lower()

    if file_ext not in [".docx", ".pdf"]:
        msg = (
            "Faqat .docx yoki .pdf fayllarni yuboring :)"
            if bot_lang == "eski"
            else "Faqat .docx yoki .pdf fayllarni yuboring :)"
        )
        await message.reply_text(msg, reply_to_message_id=message.message_id)
        return

    wait_text = (
        "Sabr qiling, hujjat yangi alifboga o'girilmoqda..."
        if bot_lang == "eski"
        else "Sabr qiling, hujjat yangi alifboga ögirilmoqda..."
    )
    status_msg = await message.reply_text(
        wait_text,
        reply_to_message_id=message.message_id
    )
    await context.bot.send_chat_action(chat_id=message.chat_id, action=ChatAction.UPLOAD_DOCUMENT)

    try:
        file_obj = await doc.get_file()
        file_bytes = io.BytesIO()
        await file_obj.download_to_memory(file_bytes)
        file_bytes.seek(0)

        output_bytes = io.BytesIO()
        stem = Path(file_name).stem

        if file_ext == ".docx":
            convert_docx_file(
                file_bytes,
                output_bytes,
                translate_cyrillic=translate_cyrillic,
                translate_mixed=translate_mixed
            )
            new_file_name = f"{stem}_yangi_alifbo.docx"
            content_type = "document"
        else:
            convert_pdf_file(
                file_bytes,
                output_bytes,
                translate_cyrillic=translate_cyrillic,
                translate_mixed=translate_mixed
            )
            new_file_name = f"{stem}_yangi_alifbo.pdf"
            content_type = "pdf"

        output_bytes.seek(0)
        output_bytes.name = new_file_name

        caption = "Tayyor!"
        await message.reply_document(
            document=output_bytes,
            filename=new_file_name,
            caption=caption,
            reply_to_message_id=message.message_id
        )

        try:
            await status_msg.delete()
        except Exception:
            pass

        await save_conversion_log(
            user_id=user.id if user else None,
            content_type=content_type,
            original_text=file_name,
            converted_text=new_file_name,
            file_name=file_name,
            char_count=doc.file_size or 0
        )
    except Exception as e:
        await status_msg.edit_text(f"Xatolik boldi: {e}")


def register_handlers(dp):
    dp.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.Document.ALL,
            bot_document
        )
    )
