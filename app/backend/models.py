"""Domain models: roles, users, and inventory products.

Inventory columns mirror the real ``data/samen.xlsx`` (the ``همه`` sheet). See
``spec/data-model.md``.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class Role(enum.Enum):
    """User access levels."""

    ADMIN = "ADMIN"            # full access + user management
    PRIVILEGED = "PRIVILEGED"  # full access, no user management
    READ_ONLY = "READ_ONLY"    # view only

    @property
    def can_write(self) -> bool:
        return self in (Role.ADMIN, Role.PRIVILEGED)

    @property
    def can_manage_users(self) -> bool:
        return self is Role.ADMIN

    @property
    def fa(self) -> str:
        return {
            Role.ADMIN: "مدیر",
            Role.PRIVILEGED: "کاربر ارشد",
            Role.READ_ONLY: "کاربر فقط‌خواندنی",
        }[self]

    @classmethod
    def assignable_by_admin(cls) -> list["Role"]:
        """Roles an administrator may assign through the UI."""
        return [cls.PRIVILEGED, cls.READ_ONLY]


@dataclass
class User:
    username: str
    password_hash: str
    role: Role
    is_active: bool = True
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "User":
        return cls(
            username=d["username"],
            password_hash=d["password_hash"],
            role=Role(d["role"]),
            is_active=d.get("is_active", True),
            created_at=d.get("created_at", ""),
        )


# --- Inventory ---------------------------------------------------------------

# Canonical column order of the ``همه`` sheet → internal field names.
# Index = column position (0-based) in the sheet.
INVENTORY_FIELDS: list[str] = [
    "name",
    "barcode",
    "carton_count",
    "qty_per_carton",
    "total_qty",
    "min_threshold",
    "product_type",
    "company",
    "model",
    "section",
]

# Integer-typed inventory fields (blank cells → None, not 0).
INVENTORY_INT_FIELDS: frozenset[str] = frozenset(
    {"carton_count", "qty_per_carton", "total_qty", "min_threshold", "section"}
)


@dataclass
class Product:
    name: str
    barcode: str | None = None
    carton_count: int | None = None
    qty_per_carton: int | None = None
    total_qty: int | None = None
    min_threshold: int | None = None
    product_type: str | None = None
    company: str | None = None
    model: str | None = None
    section: int | None = None
    row: int | None = None  # 1-based Excel row, for write-back

    @property
    def is_low_stock(self) -> bool:
        return (
            self.min_threshold is not None
            and self.total_qty is not None
            and self.total_qty <= self.min_threshold
        )

    def values_in_order(self) -> list:
        """Cell values in canonical column order (for writing back to Excel)."""
        return [getattr(self, f) for f in INVENTORY_FIELDS]

    @classmethod
    def from_cells(cls, cells: list, row: int | None = None) -> "Product":
        """Build a Product from a row of raw cell values (canonical order)."""
        data: dict = {"row": row}
        for field_name, value in zip(INVENTORY_FIELDS, cells):
            data[field_name] = _coerce(field_name, value)
        return cls(**data)


def _coerce(field_name: str, value):
    """Normalize a raw Excel cell value for a given field."""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
    if field_name in INVENTORY_INT_FIELDS:
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None
    if field_name == "barcode":
        # Keep barcodes as text (preserve leading zeros), drop trailing ".0".
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    return value
