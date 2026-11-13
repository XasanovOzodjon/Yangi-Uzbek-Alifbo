from django.contrib import admin
from .models import TelegramUser, ConversionLog, WordException


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "username", "first_name", "last_name", "is_active", "created_at", "updated_at")
    search_fields = ("telegram_id", "username", "first_name", "last_name")
    list_filter = ("is_active", "is_bot", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ConversionLog)
class ConversionLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "content_type", "short_original", "char_count", "file_name", "created_at")
    list_filter = ("content_type", "created_at")
    search_fields = ("original_text", "converted_text", "file_name", "user__username", "user__first_name")
    readonly_fields = ("created_at",)

    def short_original(self, obj):
        text = obj.original_text or obj.file_name or ""
        return text[:50] + ("..." if len(text) > 50 else "")
    short_original.short_description = "Matn / Fayl"


@admin.register(WordException)
class WordExceptionAdmin(admin.ModelAdmin):
    list_display = ("word", "category", "replacement", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("word", "replacement", "description")
