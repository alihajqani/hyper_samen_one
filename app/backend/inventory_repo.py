"""In-memory inventory repository over the encrypted Excel file.

Loads products once into memory for fast search/barcode lookup, and routes writes
back through :class:`~app.backend.excel_service.ExcelService`.
"""

from __future__ import annotations

import logging

from app.backend.alerts import low_stock_products
from app.backend.excel_service import ExcelService
from app.backend.models import Product

logger = logging.getLogger("hyper_samen.inventory")


class InventoryRepo:
    def __init__(self, excel: ExcelService):
        self._excel = excel
        self._products: list[Product] = []
        self._barcode_index: dict[str, Product] = {}

    @property
    def products(self) -> list[Product]:
        return self._products

    @property
    def writable(self) -> bool:
        return self._excel.writable

    def load(self) -> list[Product]:
        self._products = self._excel.read_products()
        self._reindex()
        return self._products

    def _reindex(self) -> None:
        self._barcode_index = {
            p.barcode: p for p in self._products if p.barcode
        }

    # -- queries --------------------------------------------------------------

    def find_by_barcode(self, barcode: str) -> Product | None:
        return self._barcode_index.get(str(barcode).strip())

    def search(self, text: str) -> list[Product]:
        text = (text or "").strip().lower()
        if not text:
            return self._products
        fields = ("name", "barcode", "company", "model", "product_type")
        out = []
        for p in self._products:
            for f in fields:
                v = getattr(p, f)
                if v is not None and text in str(v).lower():
                    out.append(p)
                    break
        return out

    def low_stock(self) -> list[Product]:
        return low_stock_products(self._products)

    # -- mutations (reload after each to stay consistent) ---------------------

    def add(self, product: Product) -> Product:
        self._excel.append_product(product)
        self.load()
        return product

    def update(self, product: Product) -> Product:
        self._excel.update_product(product)
        self.load()
        return product

    def delete(self, product: Product) -> None:
        self._excel.delete_product(product)
        self.load()
