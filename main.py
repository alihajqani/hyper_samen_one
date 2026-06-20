"""Entry point for هایپرمارکت ثامن (Hyper Market Samen) inventory app.

Usage:
    python main.py            # launch the GUI (added in v0.4.0)
    python main.py --check    # bootstrap config + logging and report health
"""

from __future__ import annotations

import argparse
import logging
import sys

from app.__version__ import __app_title_fa__, __version__
from app.backend.config import load_config
from app.backend.logging_setup import jalali_log_name, setup_logging


def _bootstrap() -> tuple[object, logging.Logger]:
    cfg = load_config()
    logger = setup_logging(cfg.log_dir, cfg.log_level)
    logger.info("شروع برنامه — نسخه %s", __version__)
    return cfg, logger


def run_check() -> int:
    """Bootstrap config + logging and print a health summary (no GUI)."""
    cfg, logger = _bootstrap()
    print(f"{__app_title_fa__}  (v{__version__})")
    print("-" * 48)
    print(f"پوشه پایه:            {cfg.log_dir}")
    print(f"فایل لاگ امروز:       {jalali_log_name()}")
    print(f"فایل موجودی:          {cfg.inventory_file}  (موجود: {cfg.inventory_file.exists()})")
    print(f"رمز اکسل تنظیم شده:   {'بله' if cfg.has_excel_secrets else 'خیر'}")
    print(f"کلید کاربران تنظیم شد: {'بله' if cfg.has_user_store_key else 'خیر'}")
    print(f"سطح لاگ:              {cfg.log_level}")
    logger.info("بررسی سلامت با موفقیت انجام شد")
    print("-" * 48)
    print("وضعیت: سالم ✔")
    return 0


def run_gui() -> int:
    """Launch the Qt GUI. Implemented in v0.4.0."""
    cfg, logger = _bootstrap()
    try:
        from app.frontend.app_qt import run_app
    except ImportError:
        logger.warning("رابط گرافیکی هنوز در این نسخه پیاده‌سازی نشده است")
        print("رابط گرافیکی در نسخه‌های بعدی اضافه می‌شود. از --check استفاده کنید.")
        return 0
    return run_app(cfg, logger)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__app_title_fa__)
    parser.add_argument("--check", action="store_true", help="بررسی سلامت بدون رابط گرافیکی")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    if args.check:
        return run_check()
    return run_gui()


if __name__ == "__main__":
    sys.exit(main())
