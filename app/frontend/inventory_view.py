"""Inventory view: searchable/scannable product table with low-stock highlighting."""

from __future__ import annotations

import logging

from PySide6.QtCore import QAbstractTableModel, QItemSelectionModel, QModelIndex, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from app.backend.inventory_repo import InventoryRepo
from app.backend.models import INVENTORY_FIELDS, Product
from app.frontend.i18n import fa
from app.frontend.utils_fa import display, to_persian_digits
from app.frontend.widgets.common import show_info
from app.frontend.widgets.search_bar import SearchBar

logger = logging.getLogger("hyper_samen.ui.inventory")

_LOW_STOCK_BG = QColor("#ffebee")
_LOW_STOCK_FG = QColor("#b71c1c")


class ProductTableModel(QAbstractTableModel):
    """Read-only table model over a list of :class:`Product`."""

    def __init__(self, products: list[Product] | None = None):
        super().__init__()
        self._rows: list[Product] = products or []
        self._headers = [fa.COLUMN_LABELS[f] for f in INVENTORY_FIELDS]

    def set_products(self, products: list[Product]) -> None:
        self.beginResetModel()
        self._rows = products
        self.endResetModel()

    def product_at(self, row: int) -> Product | None:
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    # Qt model API
    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(INVENTORY_FIELDS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        return to_persian_digits(section + 1)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        product = self._rows[index.row()]
        field = INVENTORY_FIELDS[index.column()]
        if role == Qt.DisplayRole:
            return display(getattr(product, field))
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignCenter)
        if product.is_low_stock and role == Qt.BackgroundRole:
            return _LOW_STOCK_BG
        if product.is_low_stock and role == Qt.ForegroundRole:
            return _LOW_STOCK_FG
        return None


class InventoryView(QWidget):
    """Container with a scan/search bar and the product table."""

    def __init__(self, repo: InventoryRepo, on_changed=None):
        super().__init__()
        self._repo = repo
        self._on_changed = on_changed  # callback to refresh badge after edits
        self._model = ProductTableModel(repo.products)
        self._build()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        top = QHBoxLayout()
        self._search = SearchBar()
        self._search.changed.connect(self._apply_filter)
        self._search.submitted.connect(self._on_scan)
        top.addWidget(self._search, 1)

        self._refresh_btn = QPushButton(fa.BTN_REFRESH)
        self._refresh_btn.setObjectName("ghost")
        self._refresh_btn.clicked.connect(self.reload)
        top.addWidget(self._refresh_btn)
        lay.addLayout(top)

        self._count = QLabel()
        self._count.setObjectName("subtitle")
        lay.addWidget(self._count)

        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        lay.addWidget(self._table, 1)

        self._update_count(len(self._repo.products))

    # -- behavior -------------------------------------------------------------

    def _update_count(self, n: int) -> None:
        self._count.setText(fa.LBL_TOTAL_ITEMS.format(count=to_persian_digits(n)))

    def _apply_filter(self, text: str) -> None:
        rows = self._repo.search(text)
        self._model.set_products(rows)
        self._update_count(len(rows))

    def _on_scan(self, code: str) -> None:
        """Enter pressed: try barcode lookup first, else keep the text filter."""
        if not code:
            return
        product = self._repo.find_by_barcode(code)
        if product is None:
            # Not a known barcode — treat as a search; warn if nothing matches.
            if not self._repo.search(code):
                show_info(self, fa.MSG_PRODUCT_NOT_FOUND)
            return
        self._select_product(product)

    def _select_product(self, product: Product) -> None:
        # Make sure the full list is shown, then select the matching row.
        self._model.set_products(self._repo.products)
        self._update_count(len(self._repo.products))
        for i in range(self._model.rowCount()):
            if self._model.product_at(i) is product:
                index = self._model.index(i, 0)
                sel = self._table.selectionModel()
                sel.setCurrentIndex(
                    index,
                    QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows,
                )
                self._table.scrollTo(index)
                break

    def selected_product(self) -> Product | None:
        rows = self._table.selectionModel().selectedRows()
        if rows:
            return self._model.product_at(rows[0].row())
        idx = self._table.currentIndex()
        return self._model.product_at(idx.row()) if idx.isValid() else None

    def reload(self) -> None:
        self._repo.load()
        self._search.clear()
        self._model.set_products(self._repo.products)
        self._update_count(len(self._repo.products))
        if self._on_changed:
            self._on_changed()
