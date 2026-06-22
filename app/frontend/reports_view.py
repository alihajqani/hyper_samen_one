"""Reports view: low-stock report with Excel export."""

from __future__ import annotations

import logging
from pathlib import Path

import jdatetime
import openpyxl
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.backend.auth import Session
from app.backend.excel_service import encrypt_workbook
from app.backend.inventory_repo import InventoryRepo
from app.backend.models import Product
from app.backend.user_store import verify_password
from app.frontend.i18n import fa
from app.frontend.utils_fa import display, to_persian_digits
from app.frontend.widgets.common import prompt_password, show_error, show_info

logger = logging.getLogger("hyper_samen.ui.reports")

# Focused subset of columns for the low-stock report.
_REPORT_FIELDS = [
    "name", "barcode", "total_qty", "min_threshold", "product_type", "company", "section",
]


def export_low_stock(products: list[Product], path: Path, password: str | None = None) -> None:
    """Write a low-stock .xlsx report with Persian headers.

    If *password* is given, the file is encrypted/locked with it; otherwise it is
    written as a plain workbook.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "گزارش"
    ws.sheet_view.rightToLeft = True
    ws.append([fa.COLUMN_LABELS[f] for f in _REPORT_FIELDS])
    for p in products:
        ws.append([getattr(p, f) for f in _REPORT_FIELDS])
    if password:
        encrypt_workbook(wb, path, password)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(path)
    logger.info("Low-stock report exported: %s (%d rows, locked=%s)",
                path, len(products), bool(password))


class ReportsView(QWidget):
    def __init__(self, repo: InventoryRepo, session: Session):
        super().__init__()
        self._repo = repo
        self._session = session
        self._build()
        self.reload()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        top = QHBoxLayout()
        title = QLabel(fa.REPORT_LOW_STOCK_TITLE)
        title.setObjectName("title")
        top.addWidget(title)
        top.addStretch(1)
        self._refresh_btn = QPushButton(fa.BTN_REFRESH)
        self._refresh_btn.setObjectName("ghost")
        self._refresh_btn.clicked.connect(self.reload)
        top.addWidget(self._refresh_btn)
        # Export is restricted to write-capable roles (Admin + Privileged) and the
        # produced file is locked with the current user's password.
        if self._session.can_write:
            self._export_btn = QPushButton(fa.BTN_EXPORT)
            self._export_btn.clicked.connect(self._on_export)
            top.addWidget(self._export_btn)
        lay.addLayout(top)

        self._summary = QLabel()
        self._summary.setObjectName("subtitle")
        lay.addWidget(self._summary)

        self._table = QTableWidget(0, len(_REPORT_FIELDS))
        self._table.setHorizontalHeaderLabels([fa.COLUMN_LABELS[f] for f in _REPORT_FIELDS])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lay.addWidget(self._table, 1)

    def _low(self) -> list[Product]:
        return self._repo.low_stock()

    def reload(self) -> None:
        rows = self._low()
        self._summary.setText(
            fa.REPORT_EMPTY if not rows
            else fa.LBL_LOW_STOCK_BADGE.format(count=to_persian_digits(len(rows)))
        )
        self._table.setRowCount(len(rows))
        for r, p in enumerate(rows):
            for c, field in enumerate(_REPORT_FIELDS):
                item = QTableWidgetItem(display(getattr(p, field)))
                item.setTextAlignment(Qt.AlignCenter)
                self._table.setItem(r, c, item)

    def _on_export(self) -> None:
        if not self._session.can_write:
            show_error(self, fa.ERR_NO_PERMISSION)
            return
        rows = self._low()
        if not rows:
            show_info(self, fa.REPORT_EMPTY)
            return
        # Verify the current user's password; the export is locked with it.
        password = prompt_password(self, fa.TITLE_EXPORT_PASSWORD, fa.EXPORT_PASSWORD_HINT)
        if password is None:
            return
        if not password or not verify_password(password, self._session.user.password_hash):
            show_error(self, fa.ERR_WRONG_PASSWORD)
            return
        default = f"low_stock_{jdatetime.date.today().strftime('%Y%m%d')}.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, fa.BTN_EXPORT, default, "Excel (*.xlsx)")
        if not path:
            return
        try:
            export_low_stock(rows, Path(path), password=password)
        except Exception as exc:  # noqa: BLE001
            show_error(self, fa.ERR_GENERIC.format(detail=exc))
            return
        show_info(self, fa.EXPORT_DONE.format(path=path))
