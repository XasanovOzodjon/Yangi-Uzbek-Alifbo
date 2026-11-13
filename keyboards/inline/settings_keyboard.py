from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_settings_keyboard(
    bot_lang: str = "yangi",
    translate_cyrillic: bool = False,
    translate_mixed: bool = False
) -> InlineKeyboardMarkup:
    """Sozlamalar menyusi uchun inline tugmalarni yaratadi."""
    if bot_lang == "yangi":
        lang_text = "🌐 Bot tili: 🆕 Yangi alifbo"
        cyr_status = "✅ Yoqiq" if translate_cyrillic else "❌ Öçiq"
        cyr_text = f"🇷🇺 Kirillçadan ögiriş: {cyr_status}"
        mixed_status = "✅ Yoqiq" if translate_mixed else "❌ Öçiq"
        mixed_text = f"🔀 Aralaş matn / fayllar: {mixed_status}"
    else:
        lang_text = "🌐 Bot tili: 🔤 Eski alifbo"
        cyr_status = "✅ Yoqiq" if translate_cyrillic else "❌ O'chiq"
        cyr_text = f"🇷🇺 Kirillchadan o'girish: {cyr_status}"
        mixed_status = "✅ Yoqiq" if translate_mixed else "❌ O'chiq"
        mixed_text = f"🔀 Aralash matn / fayllar: {mixed_status}"

    keyboard = [
        [InlineKeyboardButton(lang_text, callback_data="toggle_lang")],
        [InlineKeyboardButton(cyr_text, callback_data="toggle_cyrillic")],
        [InlineKeyboardButton(mixed_text, callback_data="toggle_mixed")],
    ]
    return InlineKeyboardMarkup(keyboard)
