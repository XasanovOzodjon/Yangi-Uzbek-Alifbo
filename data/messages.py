"""
Bot xabarlari va matnlari (Yangi va Eski alifboda).
"""


def get_start_text(full_name: str, bot_lang: str = "yangi") -> str:
    if bot_lang == "yangi":
        return (
            f"Assalomu alaykum, <b>{full_name}</b>!\n\n"
            "Men matn va hujjatlarni (.docx, .pdf) <b>Yangi Oʻzbek Alifbosiga</b> oʻgirib beruvçi botman.\n\n"
            "✍️ Matn yuboring yoki hujjat yuklang.\n"
            "⚙️ Sozlamalarni sozlaş uçun /settings buyruğidan foydalaning."
        )
    else:
        return (
            f"Assalomu alaykum, <b>{full_name}</b>!\n\n"
            "Men matn va hujjatlarni (.docx, .pdf) <b>Yangi Oʻzbek Alifbosiga</b> oʻgirib beruvchi botman.\n\n"
            "✍️ Matn yuboring yoki hujjat yuklang.\n"
            "⚙️ Sozlamalarni sozlash uchun /settings buyrug'idan foydalaning."
        )


def get_help_text(bot_lang: str = "yangi") -> str:
    if bot_lang == "yangi":
        return (
            "📖 <b>Qoʻllanma va Maxsus Belgilar:</b>\n\n"
            "<b>Buyruqlar:</b>\n"
            "• /start - Botni qayta işga tuşiriş\n"
            "• /settings yoki /sozlamalar - Sozlamalar menyusi\n"
            "• /help - Qöllanma\n\n"
            "<b>Maxsus formatlaş teglari:</b>\n"
            "🔹 <code>$( matn )$</code> - Faqat şu qavs içidagi matn yangi alifboga ögiriladi, qolgan qism asl holida qoladi.\n"
            "🔹 <code>#( matn )#</code> - Şu qavs içidagi matn ögirişdan himoyalanadi (umuman tegilmaydi), qolgan matn yangi alifboga ögiriladi.\n\n"
            "<i>Natijada qavs belgilari $(, )$ va #(, )# avtomatik olib taşlanadi.</i>"
        )
    else:
        return (
            "📖 <b>Qoʻllanma va Maxsus Belgilar:</b>\n\n"
            "<b>Buyruqlar:</b>\n"
            "• /start - Botni qayta ishga tushirish\n"
            "• /settings yoki /sozlamalar - Sozlamalar menyusi\n"
            "• /help - Qoʻllanma\n\n"
            "<b>Maxsus formatlash teglari:</b>\n"
            "🔹 <code>$( matn )$</code> - Faqat shu qavs ichidagi matn yangi alifboga oʻgiriladi, qolgan qism asl holida qoladi.\n"
            "🔹 <code>#( matn )#</code> - Shu qavs ichidagi matn oʻgirishdan himoyalanadi (umuman tegilmaydi), qolgan matn yangi alifboga oʻgiriladi.\n\n"
            "<i>Natijada qavs belgilari $(, )$ va #(, )# avtomatik olib tashlanadi.</i>"
        )


def get_settings_text(bot_lang: str = "yangi", translate_cyrillic: bool = False, translate_mixed: bool = False) -> str:
    if bot_lang == "yangi":
        cyr_status = "✅ Yoqiq" if translate_cyrillic else "❌ Öçiq"
        mixed_status = "✅ Yoqiq" if translate_mixed else "❌ Öçiq"
        return (
            "⚙️ <b>Bot Sozlamalari</b>\n\n"
            "1️⃣ <b>Bot tili:</b> 🆕 Yangi alifbo\n"
            f"2️⃣ <b>Kirillçadan ögiriş:</b> {cyr_status}\n"
            f"3️⃣ <b>Aralaş matn / fayllar:</b> {mixed_status}\n\n"
            "<i>Sozlamalarni özgartiriş uçun quyidagi tugmalarni bosing:</i>"
        )
    else:
        cyr_status = "✅ Yoqiq" if translate_cyrillic else "❌ O'chiq"
        mixed_status = "✅ Yoqiq" if translate_mixed else "❌ O'chiq"
        return (
            "⚙️ <b>Bot Sozlamalari</b>\n\n"
            "1️⃣ <b>Bot tili:</b> 🔤 Eski alifbo\n"
            f"2️⃣ <b>Kirillchadan o'girish:</b> {cyr_status}\n"
            f"3️⃣ <b>Aralash matn / fayllar:</b> {mixed_status}\n\n"
            "<i>Sozlamalarni o'zgartirish uchun quyidagi tugmalarni bosing:</i>"
        )
