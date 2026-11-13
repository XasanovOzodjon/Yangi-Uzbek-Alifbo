from telegram import KeyboardButton, ReplyKeyboardMarkup


def get_main_menu_keyboard(bot_lang: str = "yangi") -> ReplyKeyboardMarkup:
    """Asosiy pastki menyu tugmalari."""
    if bot_lang == "yangi":
        settings_btn = "⚙️ Sozlamalar"
        help_btn = "ℹ️ Qöllanma"
    else:
        settings_btn = "⚙️ Sozlamalar"
        help_btn = "ℹ️ Qoʻllanma"

    keyboard = [
        [KeyboardButton(settings_btn), KeyboardButton(help_btn)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
