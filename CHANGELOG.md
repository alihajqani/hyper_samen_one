# تغییرات / Changelog

تمام تغییرات قابل توجه این پروژه در این فایل ثبت می‌شود.
قالب بر اساس [Keep a Changelog](https://keepachangelog.com/) و نسخه‌گذاری
[Semantic Versioning](https://semver.org/lang/fa/) است.

## [Unreleased]

## [0.1.0] - 1405-03-30
### افزوده شد (Added)
- ساختار اولیه پروژه و بسته‌بندی پایتون (`pyproject.toml`, `requirements.txt`).
- مدیریت نسخه از یک منبع واحد (`app/__version__.py`) و فایل `CHANGELOG.md`.
- پیکربندی برنامه از طریق `.env` با مسیرهای کنار فایل اجرایی (`app/backend/config.py`).
- سامانه ثبت رویداد (لاگ) با نام‌گذاری تاریخ شمسی روزانه `YYYYMMDD.log`
  کنار فایل اجرایی (`app/backend/logging_setup.py`).
- نقطه ورود `main.py` با حالت بررسی سلامت (`--check`).
- مستندات: `CLAUDE.md`, `spec/`, و اسکیل‌های سفارشی.

[Unreleased]: https://example.com/compare/v0.1.0...HEAD
[0.1.0]: https://example.com/releases/tag/v0.1.0
