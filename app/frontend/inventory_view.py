"""Inventory view: searchable/scannable product table with low-stock highlighting.

The table supports per-column filtering (a filter row aligned under the headers),
click-to-sort headers, and interactive/movable columns. Double-clicking a row
opens a read-only detail popup (with product image and company logo); editing is
reached from there or from the toolbar (write roles only).
"""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import (
    QAbstractTableModel,
    QItemSelectionModel,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
)
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from app.backend.inventory_repo import InventoryRepo
from app.backend.models import INVENTORY_FIELDS, Product
from app.frontend.i18n import fa
from app.frontend.utils_fa import display, to_english_digits, to_persian_digits
from app.frontend.widgets.common import confirm, show_error, show_info
from app.frontend.widgets.search_bar import SearchBar

logger = logging.getLogger("hyper_samen.ui.inventory")

_LOW_STOCK_BG = QColor("#ffebee")
_LOW_STOCK_FG = QColor("#b71c1c")

# Role exposing the raw (unformatted) cell value, used for numeric-aware sorting.
_SORT_ROLE = Qt.UserRole + 1


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
        if role == _SORT_ROLE:
            return getattr(product, field)
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignCenter)
        if product.is_low_stock and role == Qt.BackgroundRole:
            return _LOW_STOCK_BG
        if product.is_low_stock and role == Qt.ForegroundRole:
            return _LOW_STOCK_FG
        return None


class ProductFilterProxy(QSortFilterProxyModel):
    """Per-column AND filtering with numeric-aware, None-safe sorting."""

    def __init__(self):
        super().__init__()
        self._filters: dict[int, str] = {}
        self.setSortRole(_SORT_ROLE)

    def set_column_filter(self, col: int, text: str) -> None:
        needle = to_english_digits(text or "").strip().casefold()
        if needle:
            self._filters[col] = needle
        else:
            self._filters.pop(col, None)
        self.invalidateFilter()

    def clear_filters(self) -> None:
        self._filters.clear()
        self.invalidateFilter()

    def has_filters(self) -> bool:
        return bool(self._filters)

    def filterAcceptsRow(self, source_row, source_parent) -> bool:  # noqa: N802
        model = self.sourceModel()
        for col, needle in self._filters.items():
            idx = model.index(source_row, col, source_parent)
            hay = to_english_digits(str(model.data(idx, Qt.DisplayRole) or "")).casefold()
            if needle not in hay:
                return False
        return True

    def lessThan(self, left, right) -> bool:  # noqa: N802
        lv = self.sourceModel().data(left, _SORT_ROLE)
        rv = self.sourceModel().data(right, _SORT_ROLE)
        if lv is None and rv is None:
            return False
        if lv is None:
            return True
        if rv is None:
            return False
        try:
            return lv < rv
        except TypeError:
            return str(lv) < str(rv)


class _FilterRow(QWidget):
    """A row of per-column filter editors kept aligned under the table headers."""

    def __init__(self, table: QTableView, on_filter):
        super().__init__()
        self._table = table
        self._header = table.horizontalHeader()
        self._on_filter = on_filter
        self._edits: list[QLineEdit] = []
        self.setFixedHeight(34)

        cols = table.model().columnCount()
        for c in range(cols):
            e = QLineEdit(self)
            e.setPlaceholderText(fa.PH_COL_FILTER)
            e.setClearButtonEnabled(True)
            e.textChanged.connect(lambda text, col=c: self._on_filter(col, text))
            self._edits.append(e)

        self._header.sectionResized.connect(lambda *_: self._reposition())
        self._header.sectionMoved.connect(lambda *_: self._reposition())
        self._table.horizontalScrollBar().valueChanged.connect(lambda *_: self._reposition())

    def clear(self) -> None:
        for e in self._edits:
            e.blockSignals(True)
            e.clear()
            e.blockSignals(False)

    def _reposition(self) -> None:
        h = self._header
        for logical, e in enumerate(self._edits):
            x = h.sectionViewportPosition(logical)
            w = h.sectionSize(logical)
            visible = w > 0 and not h.isSectionHidden(logical)
            e.setVisible(visible)
            if visible:
                e.setGeometry(x + 1, 3, max(1, w - 2), self.height() - 6)

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        self._reposition()

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        self._reposition()


class InventoryView(QWidget):
    """Container with a scan/search bar and the product table."""

    def __init__(
        self,
        repo: InventoryRepo,
        on_changed=None,
        product_images_dir: Path | str | None = None,
        company_logos_dir: Path | str | None = None,
    ):
        super().__init__()
        self._repo = repo
        self._on_changed = on_changed  # callback to refresh badge after edits
        self._product_images_dir = product_images_dir
        self._company_logos_dir = company_logos_dir
        self._model = ProductTableModel(repo.products)
        self._proxy = ProductFilterProxy()
        self._proxy.setSourceModel(self._model)
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

        if self._repo.writable:
            self._add_btn = QPushButton(fa.BTN_ADD)
            self._add_btn.clicked.connect(self._on_add)
            self._edit_btn = QPushButton(fa.BTN_EDIT)
            self._edit_btn.setObjectName("ghost")
            self._edit_btn.clicked.connect(self._on_edit)
            self._del_btn = QPushButton(fa.BTN_DELETE)
            self._del_btn.setObjectName("danger")
            self._del_btn.clicked.connect(self._on_delete)
            self._import_btn = QPushButton(fa.BTN_IMPORT)
            self._import_btn.setObjectName("ghost")
            self._import_btn.clicked.connect(self._on_import)
            top.addWidget(self._add_btn)
            top.addWidget(self._edit_btn)
            top.addWidget(self._del_btn)
            top.addWidget(self._import_btn)

        self._filter_btn = QPushButton(fa.BTN_TOGGLE_FILTERS)
        self._filter_btn.setObjectName("ghost")
        self._filter_btn.setCheckable(True)
        self._filter_btn.setChecked(True)
        self._filter_btn.toggled.connect(self._toggle_filters)
        top.addWidget(self._filter_btn)

        self._refresh_btn = QPushButton(fa.BTN_REFRESH)
        self._refresh_btn.setObjectName("ghost")
        self._refresh_btn.clicked.connect(self.reload)
        top.addWidget(self._refresh_btn)
        lay.addLayout(top)

        self._count = QLabel()
        self._count.setObjectName("subtitle")
        lay.addWidget(self._count)

        self._table = QTableView()
        self._table.setModel(self._proxy)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)
        self._table.verticalHeader().setVisible(False)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)
        self._table.doubleClicked.connect(self._on_row_activated)

        # Per-column filter row, kept aligned under the headers.
        self._filter_row = _FilterRow(self._table, self._proxy.set_column_filter)
        lay.addWidget(self._filter_row)
        lay.addWidget(self._table, 1)

        self._update_count(len(self._repo.products))

    # -- write operations (write roles only) ----------------------------------

    def _barcodes_except(self, product: Product | None) -> set[str]:
        return {
            p.barcode for p in self._repo.products
            if p.barcode and p is not product
        }

    def _after_change(self) -> None:
        self._search.clear()
        self._filter_row.clear()
        self._proxy.clear_filters()
        self._model.set_products(self._repo.products)
        self._update_count(len(self._repo.products))
        if self._on_changed:
            self._on_changed()

    def _on_add(self) -> None:
        from app.frontend.product_dialog import ProductDialog

        dlg = ProductDialog(self, existing_barcodes=self._barcodes_except(None))
        if dlg.exec():
            try:
                self._repo.add(dlg.product())
            except Exception as exc:  # noqa: BLE001
                show_error(self, fa.ERR_GENERIC.format(detail=exc))
                return
            self._after_change()
            show_info(self, fa.MSG_SAVED)

    def _on_edit(self) -> None:
        self._edit_product(self.selected_product())

    def _edit_product(self, product: Product | None) -> None:
        from app.frontend.product_dialog import ProductDialog

        if product is None:
            return
        dlg = ProductDialog(self, product=product,
                            existing_barcodes=self._barcodes_except(product))
        if dlg.exec():
            try:
                self._repo.update(dlg.product())
            except Exception as exc:  # noqa: BLE001
                show_error(self, fa.ERR_GENERIC.format(detail=exc))
                return
            self._after_change()
            show_info(self, fa.MSG_SAVED)

    def _on_delete(self) -> None:
        product = self.selected_product()
        if product is None:
            return
        if not confirm(self, fa.CONFIRM_DELETE_PRODUCT.format(name=product.name)):
            return
        try:
            self._repo.delete(product)
        except Exception as exc:  # noqa: BLE001
            show_error(self, fa.ERR_GENERIC.format(detail=exc))
            return
        self._after_change()
        show_info(self, fa.MSG_DELETED)

    def _on_import(self) -> None:
        from app.frontend.import_dialog import ImportDialog
        from app.backend.inventory_repo import IMPORT_REPLACE

        dlg = ImportDialog(self)
        if not dlg.exec():
            return
        path, mode, password = dlg.values()
        if mode == IMPORT_REPLACE and not confirm(self, fa.CONFIRM_IMPORT_REPLACE):
            return
        try:
            summary = self._repo.import_from_excel(path, mode, password)
        except ValueError:
            show_error(self, fa.ERR_IMPORT_EMPTY)
            return
        except Exception as exc:  # noqa: BLE001
            show_error(self, fa.ERR_GENERIC.format(detail=exc))
            return
        self._after_change()
        if summary["mode"] == IMPORT_REPLACE:
            show_info(self, fa.MSG_IMPORT_REPLACE_DONE.format(total=summary["total"]))
        else:
            show_info(self, fa.MSG_IMPORT_MERGE_DONE.format(
                updated=summary["updated"], added=summary["added"]))

    # -- behavior -------------------------------------------------------------

    def _toggle_filters(self, checked: bool) -> None:
        self._filter_row.setVisible(checked)
        if not checked:
            self._filter_row.clear()
            self._proxy.clear_filters()

    def _on_row_activated(self, *_) -> None:
        product = self.selected_product()
        if product is None:
            return
        from app.frontend.product_detail_dialog import ProductDetailDialog

        dlg = ProductDetailDialog(
            self,
            product=product,
            product_images_dir=self._product_images_dir,
            company_logos_dir=self._company_logos_dir,
            writable=self._repo.writable,
        )
        dlg.exec()
        if dlg.edit_requested and self._repo.writable:
            self._edit_product(product)

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
                proxy_index = self._proxy.mapFromSource(self._model.index(i, 0))
                if not proxy_index.isValid():
                    break
                sel = self._table.selectionModel()
                sel.setCurrentIndex(
                    proxy_index,
                    QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows,
                )
                self._table.scrollTo(proxy_index)
                break

    def selected_product(self) -> Product | None:
        rows = self._table.selectionModel().selectedRows()
        if rows:
            src = self._proxy.mapToSource(rows[0])
            return self._model.product_at(src.row())
        idx = self._table.currentIndex()
        if idx.isValid():
            src = self._proxy.mapToSource(idx)
            return self._model.product_at(src.row())
        return None

    def reload(self) -> None:
        self._repo.load()
        self._search.clear()
        self._filter_row.clear()
        self._proxy.clear_filters()
        self._model.set_products(self._repo.products)
        self._update_count(len(self._repo.products))
        if self._on_changed:
            self._on_changed()
