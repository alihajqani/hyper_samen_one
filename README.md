# سامانه مدیریت موجودی هایپرمارکت ثامن

Hyper Market Samen — a Persian (RTL) Windows desktop inventory management application.
Data is stored in a password-protected Excel file; users and roles are managed locally.

> در حال توسعه — به‌صورت نسخه‌به‌نسخه ساخته می‌شود. تاریخچه تغییرات در
> [`CHANGELOG.md`](CHANGELOG.md).

## امکانات (planned by version)
- **v0.1.0** — پیکربندی، لاگ روزانه با تاریخ شمسی، ساختار پروژه.
- **v0.2.0** — کاربران رمزگذاری‌شده، احراز هویت، نقش‌ها.
- **v0.3.0** — خواندن فایل اکسل رمزدار موجودی.
- **v0.4.0** — رابط گرافیکی فارسی (ورود، پنجره اصلی).
- **v0.5.0** — نمایش موجودی، جستجو، اسکن بارکد، هشدار کمبود.
- **v0.6.0** — افزودن/ویرایش کالا و ذخیره در اکسل.
- **v0.7.0** — مدیریت کاربران (مدیر).
- **v0.8.0** — گزارش کالاهای رو به اتمام.
- **v0.9.0** — بسته‌بندی اجرایی ویندوز/لینوکس.
- **v1.0.0** — نسخه نهایی.

## پیش‌نیازها
- Python 3.10+ (تست‌شده روی 3.14)
- برای ویندوز نهایی: نصب Microsoft Excel (برای دسترسی COM با هر دو رمز)

## راه‌اندازی توسعه (Ubuntu/Windows)
```bash
python3 -m venv .venv
. .venv/bin/activate            # ویندوز: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env            # سپس مقادیر را پر کنید
python main.py --check          # بررسی سلامت
python main.py                  # اجرای برنامه (از v0.4.0)
```

## ساخت فایل اجرایی (ویندوز/لینوکس)
```bash
pip install -r requirements-dev.txt
python tools/build_exe.py
```
خروجی به‌صورت «تک‌پوشه» در `dist/hyper_samen_one/` ساخته می‌شود. فایل‌های زمان‌اجرا کنار فایل
اجرایی قرار می‌گیرند:
- `.env` (رمزها) — باید پر شود.
- `data/samen.xlsx` (فایل موجودی رمزدار).
- `users.dat` و `YYYYMMDD.log` (به‌صورت خودکار ساخته می‌شوند).

برای آیکون ویندوز، فایل `data/app.ico` را قرار دهید؛ برای فونت فارسی، فایل
`app/frontend/assets/Vazirmatn-Regular.ttf` را اضافه کنید (هر دو اختیاری).

## ساختار
- `app/backend/` — پیکربندی، لاگ، داده، احراز هویت.
- `app/frontend/` — رابط گرافیکی PySide6 (فارسی، RTL).
- `spec/` — مشخصات کامل.
- `tools/` — اسکریپت‌های بسته‌بندی.

## امنیت
رمزها در `.env` کنار فایل اجرایی نگهداری می‌شوند — این صرفاً «مبهم‌سازی» است نه امنیت قوی.
رمز کاربران با bcrypt هش می‌شود. فایل‌های `.env`، `users.dat`، `*.log` و دادهٔ اکسل در گیت نادیده گرفته می‌شوند.
