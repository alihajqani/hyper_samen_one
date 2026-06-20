"""Shared UI helpers: Persian message boxes and asset path resolution."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QWidget

from app.frontend.i18n import fa


def _resource_root() -> Path:
    """Root for bundled resources (PyInstaller _MEIPASS when frozen)."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[3]


def asset_path(*parts: str) -> Path:
    """Resolve a bundled asset path (works frozen and in dev)."""
    return _resource_root().joinpath(*parts)


def logo_path() -> Path:
    return asset_path("data", "logo.png")


def font_path() -> Path:
    return asset_path("app", "frontend", "assets", "Vazirmatn-Regular.ttf")


def show_info(parent: QWidget | None, text: str, title: str = fa.TITLE_INFO) -> None:
    QMessageBox.information(parent, title, text)


def show_error(parent: QWidget | None, text: str, title: str = fa.TITLE_ERROR) -> None:
    QMessageBox.critical(parent, title, text)


def show_warning(parent: QWidget | None, text: str, title: str = fa.TITLE_WARNING) -> None:
    QMessageBox.warning(parent, title, text)


def confirm(parent: QWidget | None, text: str, title: str = fa.TITLE_CONFIRM) -> bool:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(title)
    box.setText(text)
    yes = box.addButton(fa.CONFIRM_YES, QMessageBox.YesRole)
    box.addButton(fa.CONFIRM_NO, QMessageBox.NoRole)
    box.exec()
    return box.clickedButton() is yes
