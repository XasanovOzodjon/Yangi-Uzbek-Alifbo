from asgiref.sync import sync_to_async
from converter.models import TelegramUser, ConversionLog


@sync_to_async
def get_or_create_telegram_user(user):
    if not user:
        return None
    try:
        tg_user, created = TelegramUser.objects.update_or_create(
            telegram_id=user.id,
            defaults={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language_code": user.language_code or "uz",
                "is_bot": user.is_bot,
                "is_active": True,
            }
        )
        return tg_user
    except Exception:
        return None


@sync_to_async
def update_user_settings(telegram_id: int, **kwargs):
    """Foydalanuvchi sozlamalarini yangilaydi (bot_lang, translate_cyrillic, translate_mixed)."""
    try:
        tg_user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        if tg_user:
            for key, val in kwargs.items():
                if hasattr(tg_user, key):
                    setattr(tg_user, key, val)
            tg_user.save()
            return tg_user
    except Exception:
        pass
    return None


@sync_to_async
def get_user_settings(telegram_id: int):
    """Foydalanuvchi sozlamalarini lug'at sifatida qaytaradi."""
    try:
        tg_user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        if tg_user:
            return {
                "bot_lang": tg_user.bot_lang,
                "translate_cyrillic": tg_user.translate_cyrillic,
                "translate_mixed": tg_user.translate_mixed,
            }
    except Exception:
        pass
    return {
        "bot_lang": "yangi",
        "translate_cyrillic": False,
        "translate_mixed": False,
    }


@sync_to_async
def save_conversion_log(user_id, content_type, original_text="", converted_text="", file_name=None, char_count=0):
    try:
        user_instance = None
        if user_id:
            user_instance = TelegramUser.objects.filter(telegram_id=user_id).first()

        ConversionLog.objects.create(
            user=user_instance,
            content_type=content_type,
            original_text=original_text or "",
            converted_text=converted_text or "",
            file_name=file_name,
            char_count=char_count or len(converted_text or "")
        )
    except Exception:
        pass
