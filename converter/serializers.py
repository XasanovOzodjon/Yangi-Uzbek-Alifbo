from rest_framework import serializers
from .models import TelegramUser, ConversionLog, WordException
from .services.alphabet import convert_to_new_alphabet, process_text


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = [
            "id",
            "telegram_id",
            "username",
            "first_name",
            "last_name",
            "language_code",
            "bot_lang",
            "translate_cyrillic",
            "translate_mixed",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ConversionLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.first_name", read_only=True)

    class Meta:
        model = ConversionLog
        fields = [
            "id",
            "user",
            "user_name",
            "content_type",
            "original_text",
            "converted_text",
            "file_name",
            "char_count",
            "created_at",
        ]


class WordExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordException
        fields = [
            "id",
            "word",
            "category",
            "replacement",
            "description",
            "is_active",
            "created_at",
        ]


class TextConversionSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, allow_blank=False, help_text="O'girilishi kerak bo'lgan matn")
    translate_cyrillic = serializers.BooleanField(required=False, default=False)
    translate_mixed = serializers.BooleanField(required=False, default=False)
    converted_text = serializers.CharField(read_only=True)
    char_count = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        raw_text = validated_data["text"]
        translate_cyrillic = validated_data.get("translate_cyrillic", False)
        translate_mixed = validated_data.get("translate_mixed", False)
        converted = process_text(
            raw_text,
            translate_cyrillic=translate_cyrillic,
            translate_mixed=translate_mixed
        )
        return {
            "text": raw_text,
            "translate_cyrillic": translate_cyrillic,
            "translate_mixed": translate_mixed,
            "converted_text": converted,
            "char_count": len(converted),
        }
