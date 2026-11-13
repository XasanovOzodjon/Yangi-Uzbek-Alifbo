from django.db import models


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, db_index=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name="Username")
    first_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ism")
    last_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Familiya")
    language_code = models.CharField(max_length=10, default="uz", verbose_name="Til kodi")
    bot_lang = models.CharField(
        max_length=20,
        default="yangi",
        choices=[("yangi", "Yangi alifbo"), ("eski", "Eski alifbo")],
        verbose_name="Bot tili"
    )
    translate_cyrillic = models.BooleanField(
        default=False,
        verbose_name="Kirillcha xabarlarni tarjima qilish"
    )
    translate_mixed = models.BooleanField(
        default=False,
        verbose_name="Aralash matn va fayllarni tarjima qilish"
    )
    is_bot = models.BooleanField(default=False, verbose_name="Botmi")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ro'yxatdan o'tgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Oxirgi faollik")

    class Meta:
        verbose_name = "Telegram Foydalanuvchi"
        verbose_name_plural = "Telegram Foydalanuvchilar"
        ordering = ["-updated_at"]

    def __str__(self):
        name = self.first_name or "Noma'lum"
        if self.username:
            return f"{name} (@{self.username})"
        return f"{name} ({self.telegram_id})"


class ConversionLog(models.Model):
    CONTENT_TYPES = [
        ("text", "Oddiy matn"),
        ("photo", "Rasmli post (caption)"),
        ("video", "Video post (caption)"),
        ("document", "Word hujjati (.docx)"),
        ("pdf", "PDF hujjati (.pdf)"),
        ("other", "Boshqa"),
    ]

    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversions",
        verbose_name="Foydalanuvchi"
    )
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPES,
        default="text",
        verbose_name="Tarkib turi"
    )
    original_text = models.TextField(blank=True, null=True, verbose_name="Asl matn")
    converted_text = models.TextField(blank=True, null=True, verbose_name="O'girilgan matn")
    file_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Fayl nomi")
    char_count = models.PositiveIntegerField(default=0, verbose_name="Belgilar soni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vaqt")

    class Meta:
        verbose_name = "O'girish tarixi"
        verbose_name_plural = "O'girish tarixlari"
        ordering = ["-created_at"]

    def __str__(self):
        user_display = self.user.first_name if self.user else "Anonim"
        return f"{self.get_content_type_display()} - {user_display} ({self.char_count} belgi)"


class WordException(models.Model):
    CATEGORY_CHOICES = [
        ("ng", "NG birikmasi istisnosi (ñ ga aylanmaydi)"),
        ("sh", "SH birikmasi istisnosi (ş ga aylanmaydi)"),
        ("custom", "Maxsus so'zma-so'z almashtirish"),
    ]

    word = models.CharField(max_length=100, unique=True, verbose_name="Istisno so'z yoki o'zak")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="ng",
        verbose_name="Toifa"
    )
    replacement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Maxsus almashtirish (ixtiyoriy)"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Izoh / Ma'lumot")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqt")

    class Meta:
        verbose_name = "So'z istisnosi"
        verbose_name_plural = "So'z istisnolari"
        ordering = ["word"]

    def __str__(self):
        return f"{self.word} ({self.get_category_display()})"
