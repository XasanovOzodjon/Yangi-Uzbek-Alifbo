"""
Yangi O'zbek Alifbosi Konvertatsiya xizmati (Transliteration Service)

"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Set
from .cyrillic import convert_cyrillic_to_new_latin

logger = logging.getLogger(__name__)

# Barcha apostrof va unga o'xshash belgilar
APOSTROPHE_RAW = "'\u02bb\u2019\u2018\u02bc`\u00b4\u2032"
APOSTROPHE_CLASS = r"['\u02bb\u2019\u2018\u02bc\`\u00b4\u2032]"

# Ichki himoya belgilari (Unicode Private Use Area)
# Bu belgilar oraliq bosqichda istisno harflarni himoya qilish uchun ishlatiladi
PROTECT_SH_UPPER = "\uE004"
PROTECT_SH_TITLE = "\uE005"
PROTECT_SH_LOWER = "\uE006"


class AlphabetConverter:
    def __init__(self, exceptions_file_path: Path = None):
        if exceptions_file_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.exceptions_file_path = base_dir / "data" / "exceptions.json"
        else:
            self.exceptions_file_path = Path(exceptions_file_path)

        self._ng_exceptions: Set[str] = set()
        self._sh_exceptions: Set[str] = set()
        self._custom_mappings: Dict[str, str] = {}
        self.reload_exceptions()

    def reload_exceptions(self):
        """JSON fayl va ma'lumotlar bazasidan istisnolarni yuklaydi."""
        self._ng_exceptions.clear()
        self._sh_exceptions.clear()
        self._custom_mappings.clear()

        # 1. JSON fayldan o'qish
        if self.exceptions_file_path.exists():
            try:
                with open(self.exceptions_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for word in data.get("ng_exceptions", []):
                        if word and word.strip():
                            self._ng_exceptions.add(word.strip().lower())
                    for word in data.get("sh_exceptions", []):
                        if word and word.strip():
                            self._sh_exceptions.add(word.strip().lower())
                    for k, v in data.get("custom_mappings", {}).items():
                        if k and v:
                            self._custom_mappings[k.strip()] = v.strip()
            except Exception as e:
                logger.error(f"exceptions.json faylini o'qishda xatolik: {e}")

        # 2. Django Modelidan qo'shimcha o'qish (agar Django yuklangan bo'lsa)
        try:
            from converter.models import WordException
            for exc in WordException.objects.filter(is_active=True):
                w = exc.word.strip().lower()
                if exc.category == "ng":
                    self._ng_exceptions.add(w)
                elif exc.category == "sh":
                    self._sh_exceptions.add(w)
                elif exc.category == "custom" and exc.replacement:
                    self._custom_mappings[exc.word.strip()] = exc.replacement.strip()
        except Exception:
            # Django hali yuklanmagan yoki migratsiya qilinmagan bo'lishi mumkin
            pass

    def add_ng_exception(self, word: str) -> bool:
        """Yangi NG istisnolari"""
        word = word.strip().lower()
        if not word:
            return False
        self._ng_exceptions.add(word)
        return self._save_to_json()

    def _save_to_json(self) -> bool:
        """Joriy istisnolarni JSON faylga yozish."""
        try:
            data = {
                "_comment": "Yangi alifboga o'girishda istisno so'zlar ro'yxati.",
                "ng_exceptions": sorted(list(self._ng_exceptions)),
                "sh_exceptions": sorted(list(self._sh_exceptions)),
                "custom_mappings": self._custom_mappings
            }
            with open(self.exceptions_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"exceptions.json ga yozishda xatolik: {e}")
            return False

    def _protect_sh_in_word(self, match: re.Match) -> str:
        """Istisno so'zdagi SH harflarini himoyalash."""
        w = match.group(0)
        w = re.sub(r"SH", PROTECT_SH_UPPER, w)
        w = re.sub(r"Sh", PROTECT_SH_TITLE, w)
        w = re.sub(r"sh", PROTECT_SH_LOWER, w)
        return w

    def convert(self, text: str) -> str:
        """
        Kiritilgan matnni Yangi O'zbek Alifbosiga o'giradi.
        Yangi alifboda 4 ta asosiy o'zgarish mavjud:
        1. Oʻ / oʻ (O', o') -> Ö / ö
        2. Gʻ / gʻ (G', g') -> Ğ / ğ
        3. CH / Ch / ch -> Ç / Ç / ç
        4. SH / Sh / sh -> Ş / Ş / ş
        (NG birikmasi o'zgarmaydi)
        """
        if not text:
            return ""

        for original, target in self._custom_mappings.items():
            text = text.replace(original, target)

        # 1. SH istisno so'zlarni himoyalash (masalan: Is'hoq, as'hob)
        if self._sh_exceptions:
            sorted_sh = sorted(self._sh_exceptions, key=len, reverse=True)
            sh_pattern = (
                r"(?i)\b("
                + "|".join(re.escape(w) for w in sorted_sh)
                + r")[a-zA-Z" + APOSTROPHE_RAW + r"]*"
            )
            text = re.sub(sh_pattern, self._protect_sh_in_word, text)

        # 2. Oʻ / O' -> Ö va oʻ / o' -> ö
        text = re.sub(r"O" + APOSTROPHE_CLASS, "Ö", text)
        text = re.sub(r"o" + APOSTROPHE_CLASS, "ö", text)

        # 3. Gʻ / G' -> Ğ va gʻ / g' -> ğ
        text = re.sub(r"G" + APOSTROPHE_CLASS, "Ğ", text)
        text = re.sub(r"g" + APOSTROPHE_CLASS, "ğ", text)

        # 4. CH / Ch / ch -> Ç / Ç / ç
        text = re.sub(r"CH", "Ç", text)
        text = re.sub(r"Ch", "Ç", text)
        text = re.sub(r"ch", "ç", text)

        # 5. SH / Sh / sh -> Ş / Ş / ş
        text = re.sub(r"SH", "Ş", text)
        text = re.sub(r"Sh", "Ş", text)
        text = re.sub(r"sh", "ş", text)

        # 6. SH himoyasini qaytarish
        text = text.replace(PROTECT_SH_UPPER, "SH")
        text = text.replace(PROTECT_SH_TITLE, "Sh")
        text = text.replace(PROTECT_SH_LOWER, "sh")

        return text


default_converter = AlphabetConverter()


def convert_to_new_alphabet(text: str) -> str:
    """Yangi alifboga ugartiruvchi."""
    return default_converter.convert(text)


def has_cyrillic(text: str) -> bool:
    """Matnda kirill harflari mavjudligini aniqlaydi."""
    if not text:
        return False
    return bool(re.search(r"[\u0400-\u04FF]", text))


def has_latin(text: str) -> bool:
    """Matnda lotin harflari mavjudligini aniqlaydi."""
    if not text:
        return False
    return bool(re.search(r"[a-zA-Z]", text))


def is_mixed(text: str) -> bool:
    """Matnda ham kirill, ham lotin harflari mavjudligini aniqlaydi."""
    if not text:
        return False
    return has_cyrillic(text) and has_latin(text)


def convert_full_to_new_alphabet(text: str) -> str:
    """Kirill va eski lotin matnlarini to'liq Yangi O'zbek Alifbosiga o'giradi."""
    if not text:
        return ""
    if has_cyrillic(text):
        text = convert_cyrillic_to_new_latin(text)
    return convert_to_new_alphabet(text)


def convert_text_with_settings(text: str, translate_cyrillic: bool = False, translate_mixed: bool = False) -> str:
    """Foydalanuvchi sozlamalariga asosan matnni o'giradi (maxsus teglarsiz)."""
    if not text:
        return ""

    if is_mixed(text):
        if translate_mixed:
            return convert_full_to_new_alphabet(text)
        else:
            return convert_to_new_alphabet(text)
    elif has_cyrillic(text):
        if translate_cyrillic:
            return convert_full_to_new_alphabet(text)
        else:
            return text
    else:
        return convert_to_new_alphabet(text)


def process_text(text: str, translate_cyrillic: bool = False, translate_mixed: bool = False) -> str:
    """
    Maxsus $( )$ va #( )# qavslari hamda foydalanuvchi sozlamalarini hisobga olgan holda
    matnni Yangi O'zbek Alifbosiga o'giradi.

    1. $( matn )$:
       Faqat shu qavs ichidagi matn yangi alifboga o'giriladi, qolgan qism o'z holida qoladi.
       Qavs belgilari $( va )$ olib tashlanadi.

    2. #( matn )#:
       Shu qavs ichidagi matn tarjima qilinmaydi (umuman tegilmaydi).
       Qolgan qism yangi alifboga o'giriladi.
       Qavs belgilari #( va )# olib tashlanadi.

    3. Qavslar bo'lmaganda:
       - Aralash matn: translate_mixed ga qarab
       - Kirillcha matn: translate_cyrillic ga qarab
       - Lotincha matn: Yangi alifboga o'giriladi
    """
    if not text:
        return ""

    has_convert_tag = bool(re.search(r"\$\(.*?\)\$", text, flags=re.DOTALL))
    has_ignore_tag = bool(re.search(r"#\(.*?\)#", text, flags=re.DOTALL))

    if has_convert_tag:
        protected_ignores = []

        def _protect_ignore(m):
            idx = len(protected_ignores)
            protected_ignores.append(m.group(1))
            return f"\uE100_IGN_{idx}_\uE101"

        text_protected = re.sub(r"#\((.*?)\)#", _protect_ignore, text, flags=re.DOTALL)

        def _convert_match(m):
            inner = m.group(1)
            return convert_full_to_new_alphabet(inner)

        result = re.sub(r"\$\((.*?)\)\$", _convert_match, text_protected, flags=re.DOTALL)

        for idx, content in enumerate(protected_ignores):
            result = result.replace(f"\uE100_IGN_{idx}_\uE101", content)

        return result

    if has_ignore_tag:
        protected_ignores = []

        def _protect_ignore(m):
            idx = len(protected_ignores)
            protected_ignores.append(m.group(1))
            return f"\uE100_IGN_{idx}_\uE101"

        text_protected = re.sub(r"#\((.*?)\)#", _protect_ignore, text, flags=re.DOTALL)

        converted = convert_text_with_settings(text_protected, translate_cyrillic, translate_mixed)

        for idx, content in enumerate(protected_ignores):
            converted = converted.replace(f"\uE100_IGN_{idx}_\uE101", content)

        return converted

    return convert_text_with_settings(text, translate_cyrillic, translate_mixed)
