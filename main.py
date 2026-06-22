"""Entry point for Hyper Market Samen inventory app.

Usage:
    python main.py            # launch the GUI
    python main.py --check    # bootstrap config + logging and report health
"""

from __future__ import annotations

import argparse
import logging
import sys

from app.__version__ import __version__
from app.backend.config import load_config
from app.backend.logging_setup import jalali_log_name, setup_logging

APP_TITLE_EN = "Hyper Market Samen - Inventory Management"


def _force_utf8_stdio() -> None:
    """Avoid UnicodeEncodeError on legacy Windows consoles (cp1252).

    Persian still appears only in the Qt GUI; console/log output is English, but
    user-facing error strings may be Persian, so keep stdio UTF-8 to be safe.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _bootstrap() -> tuple[object, logging.Logger]:
    cfg = load_config()
    logger = setup_logging(cfg.log_dir, cfg.log_level)
    logger.info("Application start - version %s", __version__)
    return cfg, logger


def run_check() -> int:
    """Bootstrap config + logging and print a health summary (no GUI)."""
    cfg, logger = _bootstrap()
    print(f"{APP_TITLE_EN}  (v{__version__})")
    print("-" * 48)
    print(f"Base dir:          {cfg.log_dir}")
    print(f"Today's log file:  {jalali_log_name()}")
    print(f"Inventory file:    {cfg.inventory_file}  (exists: {cfg.inventory_file.exists()})")
    print(f"Excel secrets set: {cfg.has_excel_secrets}")
    print(f"User-store key:    {cfg.has_user_store_key}")
    print(f"Log level:         {cfg.log_level}")
    logger.info("Health check completed successfully")
    print("-" * 48)
    print("Status: healthy")
    return 0


def run_gui() -> int:
    """Launch the Qt GUI."""
    cfg, logger = _bootstrap()
    try:
        from app.frontend.app_qt import run_app
    except ImportError:
        logger.warning("GUI is not available in this build")
        print("GUI is not available. Use --check instead.")
        return 0
    return run_app(cfg, logger)


def main(argv: list[str] | None = None) -> int:
    _force_utf8_stdio()
    parser = argparse.ArgumentParser(description=APP_TITLE_EN)
    parser.add_argument("--check", action="store_true", help="health check without the GUI")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    if args.check:
        return run_check()
    return run_gui()


if __name__ == "__main__":
    sys.exit(main())
