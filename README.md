# Yangi O'zbek Alifbosi Telegram Boti & Django REST API

Ushbu loyiha matnlar, rasmli/videoli postlar (caption bilan) hamda **Word (.docx)** va **PDF (.pdf)** hujjatlarini **Yangi O'zbek Lotin Alifbosi**ga avtomatik o'girib beruvchi zamonaviy Telegram Bot va Django tizimidir.

---

## 📌 Yangi Alifbo Qoidalari (4 ta o'zgarish)

| Oldingi shakli | Yangi shakli | Misollar |
| :--- | :---: | :--- |
| **Ch, ch** | **Ç, ç** | `choy` ➡️ `çoy`, `chaqaloq` ➡️ `çaqaloq` |
| **Sh, sh** | **Ş, ş** | `shaxta` ➡️ `şaxta`, `quyosh` ➡️ `quyoş` |
| **Oʻ, oʻ (O', o')** | **Ö, ö** | `oʻqish` / `o'qish` ➡️ `öqiş`, `oʻzbek` ➡️ `özbek` |
| **Gʻ, gʻ (G', g')** | **Ğ, ğ** | `gʻalaba` / `g'alaba` ➡️ `ğalaba`, `gʻoza` ➡️ `ğoza` |

> [!IMPORTANT]
> **Apostroflar:** Bot barcha turdagi apostroflarni (`'`, `ʻ`, `’`, `‘`, `ʼ`, `` ` ``, `´`, `′`) to'g'ri tushunadi va o'giradi.  
> **Eslatma:** Yangi alifboda faqat 4 ta harf o'zgaradi (`oʻ`, `gʻ`, `ch`, `sh`). `ng` birikmasi esa o'zgarmaydi va o'z holicha qoladi.
> **Matndan nusxa olish:** Bot yuborgan natija ustiga bir marta bosish orqali matnni to'g'ridan-to'g'ri clipboardga ko'chirib olish (copy) mumkin.

---

## ✨ Asosiy Imkoniyatlar

1. ✍️ **Matnlar va Postlar:** Oddiy xabarlar, jumlalar va kanallardan forward qilingan postlarni o'girish.
2. 🖼 **Rasmli va Videoli Postlar:** Rasm yoki video tagidagi matn (caption) bilan yuborilganda, rasmni/videoni o'zini yangi alifbodagi caption bilan qaytarish.
3. 📄 **Word (.docx) va PDF (.pdf) Hujjatlari:** `.docx` va `.pdf` fayllarni qabul qiladi. Hujjat ichidagi matnlar, paragraflar, jadvallar va shrift/formatini saqlagan holda yangi alifboga o'giradi va yangi `.docx` yoki `.pdf` fayl qilib qaytaradi.
4. ⚙️ **Django ORM & Baza:**
   - `TelegramUser` — foydalanuvchilar ma'lumotlari.
   - `ConversionLog` — barcha o'girishlar tarixi (matn, rasm, docx, pdf va belgilar soni).
   - `WordException` — istisno so'zlarni boshqarish.
5. 🛡 **Django Admin Panel:** Foydalanuvchilar, konvertatsiya tarixi va istisnolarni boshqarish.
6. 🌐 **Kelajakdagi Sayt & REST API:**
   - `POST /api/v1/convert/` — matnni o'girish API si.
   - `POST /api/v1/convert-file/` — Word (.docx) va PDF (.pdf) fayllarni o'girish API si.
   - `GET /api/v1/exceptions/` — istisnolar ro'yxati API si.
   - `GET /api/v1/stats/` — statistika API si.

---

## 📁 Loyiha Tuzilishi

```text
Yangi-Uzbek-Alifbo/
├── manage.py                     # Django boshqaruv fayli
├── main.py                       # Botni to'g'ridan-to'g'ri yurgizish nuqtasi
├── core/                         # Django settings va urls
├── converter/                    # Django app
│   ├── models.py                 # TelegramUser, ConversionLog, WordException
│   ├── admin.py                  # Django Admin sozlamalari
│   ├── serializers.py            # REST API serializers
│   ├── views.py                  # API va web views
│   ├── urls.py                   # API yo'llari
│   ├── services/
│   │   ├── alphabet.py           # Yangi alifboga o'giruvchi asosiy modul
│   │   ├── docx_service.py       # Word (.docx) o'giruvchi modul
│   │   └── pdf_service.py        # PDF (.pdf) o'giruvchi modul
│   └── management/commands/
│       ├── runbot.py             # python manage.py runbot
│       └── sync_exceptions.py    # JSON va DB ni sinxronlash
├── bot/                          # Telegram Bot (python-telegram-bot v21 async)
│   ├── app.py                    # Bot application va handlerlar
│   ├── db_helpers.py             # Django ORM async helperlari
│   └── handlers/
│       ├── commands.py           # /start, /help, /alifbo, /istisnolar
│       ├── text_handlers.py      # Matnli xabarlar
│       ├── media_handlers.py     # Rasm, video, animatsiya
│       └── document_handlers.py   # Word (.docx) fayllar
├── data/
│   ├── exceptions.json           # Istisno so'zlar ro'yxati (JSON)
│   └── config.py                 # Sozlamalar va muhit o'zgaruvchilari
├── tests/                        # Avtomatik testlar
│   ├── test_converter.py         # Alifbo va DOCX testlari
│   └── test_api.py               # REST API testlari
├── requirements.txt              # Kerakli kutubxonalar
└── .env                          # Token va maxfiy kalitlar
```

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Bog'liqliklarni o'rnatish:
```bash
python3 -m pip install -r requirements.txt
```

### 2. `.env` faylini sozlash:
Loyiha ildizidagi `.env` faylini oching va Telegram bot tokeningizni kiriting:
```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
ADMINS=12345678
DEBUG=True
```

### 3. Ma'lumotlar bazasini yangilash va istisnolarni sinxronlash:
```bash
python3 manage.py migrate
python3 manage.py sync_exceptions
```

### 4. Admin yaratish (ixtiyoriy, admin panel uchun):
```bash
python3 manage.py createsuperuser
```

### 5. Botni ishga tushirish:
Xohlagan usuldan foydalanishingiz mumkin:
```bash
python3 main.py
```
yoki:
```bash
python3 manage.py runbot
```

### 6. Django Web Serverni ishga tushirish (Admin va REST API uchun):
```bash
python3 manage.py runserver
```
- Web interfeys va status: `http://127.0.0.1:8000/`
- Django Admin: `http://127.0.0.1:8000/admin/`
- REST API o'girish: `http://127.0.0.1:8000/api/v1/convert/`

---

## 🧪 Testlarni Ishga Tushirish

Barcha testlar avtomatlashtirilgan:
```bash
python3 manage.py test tests
```
