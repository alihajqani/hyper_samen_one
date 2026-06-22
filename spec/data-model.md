# Data Model

## 1. Inventory (Excel — actual `data/samen.xlsx`)

> **Reflects the real file** (inspected after decryption). The workbook has **four sheets**:
> `همه` (All — 66 rows, canonical, includes a `قسمت`/section column) and `قسمت 1` / `قسمت 2` /
> `قسمت 3` (per-section views, with inconsistent/sometimes-missing headers).
>
> **The app treats the `همه` sheet as the canonical inventory.** Columns are mapped
> **positionally** (the column order is stable) after locating the header row, because the real
> headers contain stray whitespace and minor typos (e.g. `تعداد در هد کارتون / شل` — "هد" instead
> of "هر"). A normalized header-name match is used as a secondary check.

| Col # | Real Persian header (raw) | Display label | Internal field | Type | Notes |
|---|---|---|---|---|---|
| 0 | `نام ` | نام کالا | `name` | str | Product name |
| 1 | `بارکد ` | بارکد | `barcode` | str | **Often empty** in current data; scanner key when present |
| 2 | `تعداد کارتون/ شل` | تعداد کارتن/شِل | `carton_count` | int | Number of cartons / shrink-packs |
| 3 | `تعداد در هد کارتون / شل` | تعداد در هر کارتن/شِل | `qty_per_carton` | int | Items per carton/shrink |
| 4 | ` تعداد کل ` | موجودی کل | `total_qty` | int | Total quantity (= carton_count × qty_per_carton, but stored explicitly) |
| 5 | `کمینه ` | حد کمینه (هشدار) | `min_threshold` | int? | **Often empty**; low-stock trigger when set |
| 6 | `نوع ` | نوع کالا | `product_type` | str | Category/type |
| 7 | `شرکت ` | شرکت | `company` | str | Company (can be empty) |
| 8 | `مدل ` | مدل | `model` | str | Model |
| 9 | `قسمت` | قسمت | `section` | int? | Section 1/2/3 (only on the `همه` sheet) |

### Domain model (code)

```python
@dataclass
class Product:
    name: str
    barcode: str | None
    carton_count: int | None
    qty_per_carton: int | None
    total_qty: int | None
    min_threshold: int | None
    product_type: str | None
    company: str | None
    model: str | None
    section: int | None
    row: int | None = None          # 1-based Excel row for write-back

    @property
    def is_low_stock(self) -> bool:
        # Only meaningful when both values are present.
        return (
            self.min_threshold is not None
            and self.total_qty is not None
            and self.total_qty <= self.min_threshold
        )
```

### Validation rules (lenient — matches real data)
- `name` required, non-empty.
- `barcode` **optional** (mostly empty today); when present, treated as text (preserve leading
  zeros) and used for scanner lookups. Not enforced unique, but duplicates are warned about.
- `carton_count`, `qty_per_carton`, `total_qty`, `min_threshold`, `section` are non-negative
  integers **or empty**. Blank cells map to `None`, not `0`.
- Numbers are displayed with **Persian digits**; empty values render as a blank/placeholder.

### Column mapping
The canonical order above lives in one place (backend model module) and is the source of truth
for both parsing and header rendering. Display labels come from `i18n/fa.py`. Header detection
normalizes whitespace and tolerates the known typos before falling back to positional mapping.

---

## 2. User store (`users.dat`)

A JSON document, **Fernet-encrypted** at rest (key = `USER_STORE_KEY` from `.env`).

### Decrypted JSON shape

```json
{
  "version": 1,
  "recovery_hash": "$2b$12$....",
  "users": [
    {
      "username": "admin",
      "password_hash": "$2b$12$....",
      "role": "ADMIN",
      "is_active": true,
      "created_at": "1405/03/30 10:15"
    }
  ]
}
```

`recovery_hash` is the **bcrypt hash of the master recovery code** (forgot-password). It is set
when creating the initial admin (or later from the Users view) and is never stored in clear text —
the code itself lives only in the operator's memory. It is deliberately kept inside the encrypted
`users.dat` rather than `.env`.

### Fields
| Field | Type | Notes |
|---|---|---|
| `username` | str | Unique, case-insensitive match recommended |
| `password_hash` | str | **bcrypt** hash; never plaintext |
| `role` | enum str | `ADMIN` \| `PRIVILEGED` \| `READ_ONLY` |
| `is_active` | bool | Disabled users cannot log in |
| `created_at` | str | Jalali datetime string |

### Roles
```python
class Role(enum.Enum):
    ADMIN = "ADMIN"            # full access + user management   (مدیر)
    PRIVILEGED = "PRIVILEGED"  # full access, no user mgmt       (کاربر ارشد)
    READ_ONLY = "READ_ONLY"    # view only                       (کاربر فقط‌خواندنی)
```

### Rules
- First run with no users → force-create the initial `ADMIN` (and an optional recovery code).
- Admin can create only `PRIVILEGED` or `READ_ONLY` users via the UI (additional admins, if
  allowed, is a product decision — default: admin-managed).
- **Password policy** (`app/backend/validators.py`): at least 8 characters and at least one
  lowercase Latin letter; enforced on create / change / recovery reset.
- Password changes re-hash with bcrypt.
- **Forgot password:** entering the correct master recovery code resets the *primary* admin's
  password (earliest-created `ADMIN`).
- The store file is gitignored and never logged.

---

## 3. Derived/computed data

- **Low-stock set:** products where `total_qty ≤ min_threshold`. Used by the table flag and the
  reports view; count surfaced on the main window.
- **Barcode index:** an in-memory dict/Series (barcode → row) built from the DataFrame for O(1)
  scanner lookups.

---

## 4. Product / company images (optional)

The product detail popup shows two pictures, both resolved from disk by filename:

- **Product image:** `<PRODUCT_IMAGES_DIR>/<barcode>.<ext>` (default dir `data/product_images`).
- **Company logo:** `<COMPANY_LOGOS_DIR>/<company name>.<ext>` (default dir `data/company_logos`).

Supported extensions (probed in order): `.png .jpg .jpeg .webp .bmp .gif`. Matching on the file
stem is case-insensitive. When no file is found a Persian "no image" placeholder is shown. Both
folders are configurable via `.env` (`PRODUCT_IMAGES_DIR`, `COMPANY_LOGOS_DIR`).
