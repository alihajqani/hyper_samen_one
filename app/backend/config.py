"""Application configuration.

Resolves paths relative to the executable (so logs/.env sit next to the .exe when
frozen by PyInstaller, and next to the project root in development) and loads
secrets from a ``.env`` file.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def base_dir() -> Path:
    """Directory the app should treat as "next to the executable".

    * Frozen (PyInstaller): the folder containing the .exe.
    * Development: the project root (two levels up from this file).
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


# Load .env from next to the executable / project root, once at import time.
load_dotenv(base_dir() / ".env")


def _resolve(path_str: str | None, default: Path) -> Path:
    if not path_str:
        return default
    p = Path(path_str)
    return p if p.is_absolute() else (base_dir() / p)


@dataclass(frozen=True)
class Config:
    """Resolved runtime configuration."""

    excel_read_password: str
    excel_write_password: str
    user_store_key: str
    inventory_file: Path
    user_store_file: Path
    product_images_dir: Path
    company_logos_dir: Path
    log_dir: Path
    log_level: str

    @property
    def has_excel_secrets(self) -> bool:
        return bool(self.excel_read_password)

    @property
    def has_user_store_key(self) -> bool:
        return bool(self.user_store_key)


def load_config() -> Config:
    """Build a :class:`Config` from the current environment."""
    root = base_dir()
    return Config(
        excel_read_password=os.getenv("EXCEL_READ_PASSWORD", ""),
        excel_write_password=os.getenv("EXCEL_WRITE_PASSWORD", ""),
        user_store_key=os.getenv("USER_STORE_KEY", ""),
        inventory_file=_resolve(os.getenv("INVENTORY_FILE"), root / "data" / "samen.xlsx"),
        user_store_file=_resolve(os.getenv("USER_STORE_FILE"), root / "users.dat"),
        product_images_dir=_resolve(
            os.getenv("PRODUCT_IMAGES_DIR"), root / "data" / "product_images"
        ),
        company_logos_dir=_resolve(
            os.getenv("COMPANY_LOGOS_DIR"), root / "data" / "company_logos"
        ),
        log_dir=root,
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
