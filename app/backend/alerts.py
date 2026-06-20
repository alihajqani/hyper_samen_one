"""Low-stock alert helpers."""

from __future__ import annotations

from collections.abc import Iterable

from app.backend.models import Product


def low_stock_products(products: Iterable[Product]) -> list[Product]:
    """Products whose total quantity has dropped to/below their minimum threshold."""
    return [p for p in products if p.is_low_stock]


def low_stock_count(products: Iterable[Product]) -> int:
    return sum(1 for p in products if p.is_low_stock)
