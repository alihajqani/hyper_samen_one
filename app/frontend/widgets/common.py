"""Shared UI helpers: Persian message boxes and asset path resolution."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLineEdit, QMessageBox, QWidget

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


# Image extensions probed (in order) when matching a product/company picture.
_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")


def find_image(directory: Path | str | None, stem: str | None) -> Path | None:
    """Return the first existing ``<stem>.<ext>`` file in *directory*, else ``None``.

    Used to resolve a product image by barcode or a company logo by company name.
    Matching is case-insensitive on the file stem.
    """
    if not directory or not stem:
        return None
    stem = str(stem).strip()
    if not stem:
        return None
    d = Path(directory)
    if not d.is_dir():
        return None
    # Fast path: exact stem with a known extension.
    for ext in _IMAGE_EXTS:
        p = d / f"{stem}{ext}"
        if p.exists():
            return p
    # Fallback: case-insensitive stem match over the directory.
    lower = stem.casefold()
    for child in d.iterdir():
        if child.is_file() and child.stem.casefold() == lower \
                and child.suffix.lower() in _IMAGE_EXTS:
            return child
    return None


def show_info(parent: QWidget | None, text: str, title: str = fa.TITLE_INFO) -> None:
    QMessageBox.information(parent, title, text)


def show_error(parent: QWidget | None, text: str, title: str = fa.TITLE_ERROR) -> None:
    QMessageBox.critical(parent, title, text)


def show_warning(parent: QWidget | None, text: str, title: str = fa.TITLE_WARNING) -> None:
    QMessageBox.warning(parent, title, text)


def _eye_icon(revealed: bool) -> QIcon:
    """Draw a small eye icon at runtime (no bundled asset). Slashed when revealed."""
    size = 18
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    pen = QPen(QColor("#546e7a"))
    pen.setWidth(2)
    pen.setCapStyle(Qt.RoundCap)
    p.setPen(pen)
    # Almond eye outline (two arcs) + pupil.
    p.drawArc(2, 4, 14, 10, 0, 180 * 16)
    p.drawArc(2, 4, 14, 10, 180 * 16, 180 * 16)
    p.setBrush(QColor("#546e7a"))
    p.drawEllipse(6, 6, 6, 6)
    if revealed:
        p.drawLine(3, 15, 15, 3)  # slash = currently visible, click to hide
    p.end()
    return QIcon(pm)


class PasswordEdit(QLineEdit):
    """A password field with a trailing eye icon that toggles visibility."""

    def __init__(self, parent: QWidget | None = None, placeholder: str = ""):
        super().__init__(parent)
        self.setEchoMode(QLineEdit.Password)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self._revealed = False
        self._action = self.addAction(_eye_icon(False), QLineEdit.TrailingPosition)
        self._action.setToolTip(fa.TIP_SHOW_PASSWORD)
        self._action.triggered.connect(self._toggle)

    def _toggle(self) -> None:
        self._revealed = not self._revealed
        self.setEchoMode(QLineEdit.Normal if self._revealed else QLineEdit.Password)
        self._action.setIcon(_eye_icon(self._revealed))
        self._action.setToolTip(
            fa.TIP_HIDE_PASSWORD if self._revealed else fa.TIP_SHOW_PASSWORD
        )


def confirm(parent: QWidget | None, text: str, title: str = fa.TITLE_CONFIRM) -> bool:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(title)
    box.setText(text)
    yes = box.addButton(fa.CONFIRM_YES, QMessageBox.YesRole)
    box.addButton(fa.CONFIRM_NO, QMessageBox.NoRole)
    box.exec()
    return box.clickedButton() is yes
