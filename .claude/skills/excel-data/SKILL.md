---
name: excel-data
description: Use when reading from or writing to the password-protected inventory Excel file, or editing excel_service.py / inventory_repo.py. Covers the pure-Python msoffcrypto+openpyxl backend, the repo boundary, role-gated writes, and the formula/canonical-sheet quirks. Trigger for any inventory data-access work.
---

# excel-data

The inventory lives in a **password-protected `.xlsx`** accessed via a **pure-Python crypto
backend**: `msoffcrypto` decrypts → `openpyxl` reads/edits → `msoffcrypto` re-encrypts. This is
cross-platform (Ubuntu dev and Windows prod behave identically) and needs **no MS Excel install**.
Follow these rules for all data access.

> Note: an earlier plan considered xlwings/COM; we switched to the crypto backend because
> `msoffcrypto` can both decrypt and encrypt, which is simpler and dependency-free.

## Boundaries

- **Only `app/backend/excel_service.py` talks to Excel.** Views and dialogs must go through
  `inventory_repo.py`, never open the workbook themselves.
- The repo loads rows into a **pandas DataFrame** for in-memory search/filter; writes go back
  through `excel_service` and are saved.

## Password / role mapping

- **Read-only password** (`EXCEL_READ_PASSWORD`) is the Excel open/encryption password — used by
  `msoffcrypto` to **decrypt** when reading and to **re-encrypt** when saving.
- **Read-write (modify) password** (`EXCEL_WRITE_PASSWORD`) is enforced at the **role/app layer**:
  only a *writable* `ExcelService` (built for Admin/Privileged) calls the write methods. Re-check
  the role in the backend (`_require_writable`) — never trust the UI alone.

## Read / write pattern (pure Python)

```python
# read
office = msoffcrypto.OfficeFile(open(path, "rb")); office.load_key(password=read_pw)
buf = io.BytesIO(); office.decrypt(buf); buf.seek(0)
wb = openpyxl.load_workbook(buf, data_only=True)   # data_only -> cached formula values

# write (atomic + re-encrypt)
plain = io.BytesIO(); wb.save(plain)               # load with data_only=False to edit
enc = io.BytesIO(); OOXMLFile(plain).encrypt(read_pw, enc)
tmp = path.with_suffix(path.suffix + ".tmp"); tmp.write_bytes(enc.getvalue()); tmp.replace(path)
```

- Open → operate → save within one method; don't hold a workbook across UI events.
- Use a `.tmp` + `replace()` for atomic saves (already implemented in `excel_service.py`).

## Canonical sheet & quirks (real `samen.xlsx`)
- Canonical sheet = **`همه`**; columns mapped positionally (`INVENTORY_FIELDS`) after header
  detection. Display labels live in `i18n/fa.py`.
- `total_qty` is often a **formula** (`carton_count × qty_per_carton`). On read, use the cached
  value (`data_only=True`) or compute it; on write, store a **literal int** (headless openpyxl
  doesn't evaluate formulas).
- `barcode` and `min_threshold` are frequently **empty** → map blanks to `None`, never `0`.

## Validation on write
- `name` required. `barcode` optional, text (preserve leading zeros), warn on duplicates.
- `carton_count`, `qty_per_carton`, `total_qty`, `min_threshold`, `section`: non-negative int or empty.

## Verification after changes
- Round-trip on a **copy**: add/edit/delete, reopen → change persisted, file still encrypted.
- A read-only `ExcelService` must raise on any write method.

## References
- `spec/SPEC.md` §4 (data store), `spec/data-model.md` (columns & types).
