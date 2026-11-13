"""
Kirill alifbosidan Yangi O'zbek Alifbosiga o'girish xizmati.
"""

import re

CYRILLIC_VOWELS = set("аоуиэеёюяўАОУИЭЕЁЮЯЎaouieöAOUİEÖ")
APOSTROPHES = set("ъЪьЬ'ʻ’‘ʼ`´′")


def is_vowel_or_boundary(prev_char: str) -> bool:
    """Oldingi belgi unli, tutuq belgisi yoki so'z boshi ekanligini tekshiradi."""
    if prev_char is None or prev_char == "":
        return True
    if prev_char in CYRILLIC_VOWELS or prev_char in APOSTROPHES:
        return True
    if not prev_char.isalpha():
        return True
    return False


def is_next_upper(text: str, idx: int) -> bool:
    """Keyingi yoki oldingi harf katta ekanligini tekshiradi (bosh harf / ALL CAPS)."""
    if idx + 1 < len(text) and text[idx + 1].isupper():
        return True
    if idx > 0 and text[idx - 1].isupper():
        if idx + 1 >= len(text) or not text[idx + 1].islower():
            return True
    return False


def convert_cyrillic_to_new_latin(text: str) -> str:
    """
    O'zbek Kirill alifbosidagi matnni Yangi O'zbek Lotin alifbosiga o'giradi.
    Qoidalar:
    - е -> ye (unlidan keyin, tutuq belgisidan keyin yoki so'z boshida), e (undoshdan keyin)
    - ё -> yo, ю -> yu, я -> ya, ц -> ts
    - ч -> ç, ш -> ş, щ -> ş
    - ў -> ö, ғ -> ğ
    - сҳ -> sh (masalan: Исҳоқ -> Ishoq)
    - ъ -> '
    - ь -> tushib qoladi
    """
    if not text:
        return ""

    # 1. сҳ birikmasi (s va h tovushlari ajralgan holda, masalan: Исҳоқ)
    text = re.sub(r"С[Ҳҳ]", lambda m: "SH" if m.group(0) == "СҲ" else "Sh", text)
    text = text.replace("сҳ", "sh")

    res = []
    for i, ch in enumerate(text):
        prev_ch = text[i - 1] if i > 0 else None
        upper_next = is_next_upper(text, i)

        if ch == 'е':
            if is_vowel_or_boundary(prev_ch):
                res.append("ye")
            else:
                res.append("e")
        elif ch == 'Е':
            if is_vowel_or_boundary(prev_ch):
                res.append("YE" if upper_next else "Ye")
            else:
                res.append("E")
        elif ch == 'ё':
            res.append("yo")
        elif ch == 'Ё':
            res.append("YO" if upper_next else "Yo")
        elif ch == 'ю':
            res.append("yu")
        elif ch == 'Ю':
            res.append("YU" if upper_next else "Yu")
        elif ch == 'я':
            res.append("ya")
        elif ch == 'Я':
            res.append("YA" if upper_next else "Ya")
        elif ch == 'ц':
            res.append("ts")
        elif ch == 'Ц':
            res.append("TS" if upper_next else "Ts")
        elif ch == 'ч':
            res.append("ç")
        elif ch == 'Ч':
            res.append("Ç")
        elif ch == 'ш':
            res.append("ş")
        elif ch == 'Ш':
            res.append("Ş")
        elif ch == 'щ':
            res.append("ş")
        elif ch == 'Щ':
            res.append("Ş")
        elif ch == 'ў':
            res.append("ö")
        elif ch == 'Ў':
            res.append("Ö")
        elif ch == 'ғ':
            res.append("ğ")
        elif ch == 'Ғ':
            res.append("Ğ")
        elif ch in ('ъ', 'Ъ'):
            res.append("'")
        elif ch in ('ь', 'Ь'):
            # Lotin imlosida yumshatish belgisi yozilmaydi
            pass
        elif ch == 'а': res.append('a')
        elif ch == 'А': res.append('A')
        elif ch == 'б': res.append('b')
        elif ch == 'Б': res.append('B')
        elif ch == 'в': res.append('v')
        elif ch == 'В': res.append('V')
        elif ch == 'г': res.append('g')
        elif ch == 'Г': res.append('G')
        elif ch == 'д': res.append('d')
        elif ch == 'Д': res.append('D')
        elif ch == 'ж': res.append('j')
        elif ch == 'Ж': res.append('J')
        elif ch == 'з': res.append('z')
        elif ch == 'З': res.append('Z')
        elif ch == 'и': res.append('i')
        elif ch == 'И': res.append('I')
        elif ch == 'й': res.append('y')
        elif ch == 'Й': res.append('Y')
        elif ch == 'к': res.append('k')
        elif ch == 'К': res.append('K')
        elif ch == 'л': res.append('l')
        elif ch == 'Л': res.append('L')
        elif ch == 'м': res.append('m')
        elif ch == 'М': res.append('M')
        elif ch == 'н': res.append('n')
        elif ch == 'Н': res.append('N')
        elif ch == 'о': res.append('o')
        elif ch == 'О': res.append('O')
        elif ch == 'п': res.append('p')
        elif ch == 'П': res.append('P')
        elif ch == 'р': res.append('r')
        elif ch == 'Р': res.append('R')
        elif ch == 'с': res.append('s')
        elif ch == 'С': res.append('S')
        elif ch == 'т': res.append('t')
        elif ch == 'Т': res.append('T')
        elif ch == 'у': res.append('u')
        elif ch == 'У': res.append('U')
        elif ch == 'ф': res.append('f')
        elif ch == 'Ф': res.append('F')
        elif ch == 'х': res.append('x')
        elif ch == 'Х': res.append('X')
        elif ch == 'ҳ': res.append('h')
        elif ch == 'Ҳ': res.append('H')
        elif ch == 'қ': res.append('q')
        elif ch == 'Қ': res.append('Q')
        elif ch == 'э': res.append('e')
        elif ch == 'Э': res.append('E')
        elif ch == 'ы': res.append('i')
        elif ch == 'Ы': res.append('I')
        else:
            res.append(ch)

    return "".join(res)
