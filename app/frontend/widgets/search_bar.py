"""A search / barcode-scan input.

Behaves as a normal search box (live ``changed`` signal) and also emits
``submitted`` on Enter — which is what a HID barcode scanner sends after typing a
code. Western/Persian digits in submissions are normalized to Western for lookup.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit

from app.frontend.i18n import fa
from app.frontend.utils_fa import to_english_digits


class SearchBar(QLineEdit):
    submitted = Signal(str)  # emitted on Enter (barcode scan or manual)
    changed = Signal(str)    # emitted on each edit (live filter)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(fa.PH_SCAN_SEARCH)
        self.setClearButtonEnabled(True)
        self.returnPressed.connect(self._on_return)
        self.textChanged.connect(self.changed.emit)

    def _on_return(self) -> None:
        self.submitted.emit(to_english_digits(self.text()).strip())
