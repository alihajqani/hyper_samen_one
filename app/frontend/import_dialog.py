"""Bulk-import dialog: pick an external .xlsx and choose Merge or Replace."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QRadioButton,
    QVBoxLayout,
)

from app.backend.inventory_repo import IMPORT_MERGE, IMPORT_REPLACE
from app.frontend.i18n import fa
from app.frontend.widgets.common import PasswordEdit, show_error


class ImportDialog(QDialog):
    """Collect (file path, mode, optional password) for a bulk import."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(fa.TITLE_IMPORT)
        self.setMinimumWidth(440)
        self._path: str = ""
        self._build()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        choose = QDialogButtonBox()
        pick = choose.addButton(fa.IMPORT_CHOOSE_FILE, QDialogButtonBox.ActionRole)
        pick.clicked.connect(self._on_pick)
        lay.addWidget(choose)

        self._file_label = QLabel(fa.IMPORT_NO_FILE)
        self._file_label.setObjectName("subtitle")
        self._file_label.setWordWrap(True)
        lay.addWidget(self._file_label)

        mode_title = QLabel(fa.LBL_IMPORT_MODE)
        mode_title.setObjectName("subtitle")
        lay.addWidget(mode_title)
        self._merge = QRadioButton(fa.IMPORT_MODE_MERGE)
        self._merge.setChecked(True)
        self._replace = QRadioButton(fa.IMPORT_MODE_REPLACE)
        group = QButtonGroup(self)
        group.addButton(self._merge)
        group.addButton(self._replace)
        lay.addWidget(self._merge)
        lay.addWidget(self._replace)

        self._password = PasswordEdit(placeholder=fa.LBL_IMPORT_PASSWORD)
        lay.addWidget(self._password)

        buttons = QDialogButtonBox()
        ok = buttons.addButton(fa.BTN_OK, QDialogButtonBox.AcceptRole)
        buttons.addButton(fa.BTN_CANCEL, QDialogButtonBox.RejectRole)
        ok.clicked.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        lay.addWidget(buttons)

    def _on_pick(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, fa.IMPORT_CHOOSE_FILE, "", "Excel (*.xlsx)"
        )
        if path:
            self._path = path
            self._file_label.setText(fa.IMPORT_SELECTED.format(name=Path(path).name))

    def _on_accept(self) -> None:
        if not self._path:
            show_error(self, fa.ERR_IMPORT_NO_FILE)
            return
        self.accept()

    def values(self) -> tuple[str, str, str | None]:
        mode = IMPORT_REPLACE if self._replace.isChecked() else IMPORT_MERGE
        return self._path, mode, (self._password.text() or None)
