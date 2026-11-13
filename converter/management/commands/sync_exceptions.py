import json
from pathlib import Path
from django.core.management.base import BaseCommand
from converter.models import WordException
from data import config


class Command(BaseCommand):
    help = "data/exceptions.json faylidagi so'zlarni ma'lumotlar bazasiga sinxronlash"

    def handle(self, *args, **options):
        json_file = Path(config.EXCEPTIONS_FILE)
        if not json_file.exists():
            self.stdout.write(self.style.ERROR(f"Fayl topilmadi: {json_file}"))
            return

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        created_count = 0
        updated_count = 0

        # NG exceptions
        for word in data.get("ng_exceptions", []):
            word_clean = word.strip().lower()
            if not word_clean:
                continue
            obj, created = WordException.objects.get_or_create(
                word=word_clean,
                defaults={"category": "ng", "description": "JSON fayldan yuklangan NG istisnosi"}
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        # SH exceptions
        for word in data.get("sh_exceptions", []):
            word_clean = word.strip().lower()
            if not word_clean:
                continue
            obj, created = WordException.objects.get_or_create(
                word=word_clean,
                defaults={"category": "sh", "description": "JSON fayldan yuklangan SH istisnosi"}
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sinxronlash yakunlandi: {created_count} ta yangi qo'shildi, {updated_count} ta mavjud edi."
            )
        )
