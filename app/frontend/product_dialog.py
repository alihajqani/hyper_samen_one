"""Add / edit product dialog (write-capable roles only)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)

from app.backend.models import Product
from app.frontend.i18n import fa
from app.frontend.utils_fa import to_english_digits, to_persian_digits
from app.frontend.widgets.common import show_error


def _parse_optional_int(text: str) -> int | None:
    """Parse a possibly-empty integer field (Persian/Western digits). Raises ValueError."""
    text = to_english_digits(text or "").strip()
    if text == "":
        return None
    value = int(text)  # raises ValueError on non-numeric
    if value < 0:
        raise ValueError("negative")
    return value


class ProductDialog(QDialog):
    """Edit an existing product (when ``product`` given) or create a new one."""

    def __init__(self, parent=None, product: Product | None = None,
                 existing_barcodes: set[str] | None = None):
        super().__init__(parent)
        self._editing = product is not None
        self._original = product
        self._existing_barcodes = existing_barcodes or set()
        self.setWindowTitle(fa.TITLE_EDIT_PRODUCT if self._editing else fa.TITLE_ADD_PRODUCT)
        self.setMinimumWidth(420)
        self._build()
        if product is not None:
            self._fill(product)

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignRight | Qt.AlignTop)

        self.name = QLineEdit()
        self.barcode = QLineEdit()
        self.carton_count = QLineEdit()
        self.qty_per_carton = QLineEdit()
        self.total_qty = QLineEdit()
        self.min_threshold = QLineEdit()
        self.product_type = QLineEdit()
        self.company = QLineEdit()
        self.model = QLineEdit()
        self.section = QComboBox()
        self.section.addItem(fa.EMPTY_CELL, None)
        for s in (1, 2, 3):
            self.section.addItem(to_persian_digits(s), s)

        # Auto-compute total = carton × per (user may still override).
        self.carton_count.textChanged.connect(self._auto_total)
        self.qty_per_carton.textChanged.connect(self._auto_total)

        form.addRow(fa.COL_NAME, self.name)
        form.addRow(fa.COL_BARCODE, self.barcode)
        form.addRow(fa.COL_CARTON_COUNT, self.carton_count)
        form.addRow(fa.COL_QTY_PER_CARTON, self.qty_per_carton)
        form.addRow(fa.COL_TOTAL_QTY, self.total_qty)
        form.addRow(fa.COL_MIN_THRESHOLD, self.min_threshold)
        form.addRow(fa.COL_PRODUCT_TYPE, self.product_type)
        form.addRow(fa.COL_COMPANY, self.company)
        form.addRow(fa.COL_MODEL, self.model)
        form.addRow(fa.COL_SECTION, self.section)
        outer.addLayout(form)

        buttons = QDialogButtonBox()
        save = buttons.addButton(fa.BTN_SAVE, QDialogButtonBox.AcceptRole)
        buttons.addButton(fa.BTN_CANCEL, QDialogButtonBox.RejectRole)
        save.clicked.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)
        self._touched_total = self._editing  # don't clobber an edited total

    def _auto_total(self) -> None:
        if self._touched_total:
            return
        try:
            c = _parse_optional_int(self.carton_count.text())
            p = _parse_optional_int(self.qty_per_carton.text())
        except ValueError:
            return
        if c and p:
            self.total_qty.setText(to_english_digits(str(c * p)))

    def _fill(self, p: Product) -> None:
        self.name.setText(p.name or "")
        self.barcode.setText(p.barcode or "")
        for widget, value in (
            (self.carton_count, p.carton_count),
            (self.qty_per_carton, p.qty_per_carton),
            (self.total_qty, p.total_qty),
            (self.min_threshold, p.min_threshold),
        ):
            widget.setText("" if value is None else str(value))
        self.product_type.setText(p.product_type or "")
        self.company.setText(p.company or "")
        self.model.setText(p.model or "")
        idx = self.section.findData(p.section)
        self.section.setCurrentIndex(max(0, idx))

    def _on_accept(self) -> None:
        name = self.name.text().strip()
        if not name:
            show_error(self, fa.ERR_NAME_REQUIRED)
            return
        try:
            carton = _parse_optional_int(self.carton_count.text())
            per = _parse_optional_int(self.qty_per_carton.text())
            total = _parse_optional_int(self.total_qty.text())
            threshold = _parse_optional_int(self.min_threshold.text())
        except ValueError:
            show_error(self, fa.ERR_NON_NEGATIVE_INT)
            return

        barcode = to_english_digits(self.barcode.text()).strip() or None
        if barcode and barcode in self._existing_barcodes:
            show_error(self, fa.ERR_BARCODE_DUP)
            return

        if total is None and carton and per:
            total = carton * per

        self._result = Product(
            name=name,
            barcode=barcode,
            carton_count=carton,
            qty_per_carton=per,
            total_qty=total,
            min_threshold=threshold,
            product_type=self.product_type.text().strip() or None,
            company=self.company.text().strip() or None,
            model=self.model.text().strip() or None,
            section=self.section.currentData(),
            row=self._original.row if self._original else None,
        )
        self.accept()

    def product(self) -> Product:
        return self._result
