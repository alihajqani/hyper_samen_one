---
name: excel-data
description: Use when reading from or writing to the password-protected inventory Excel file, or editing excel_service.py / inventory_repo.py. Covers xlwings/COM password handling, guaranteed Excel cleanup, the repo boundary, and read/write role mapping. Trigger for any inventory data-access work.
---

# excel-data

The inventory lives in a **password-protected `.xlsx`** accessed via **xlwings (COM)**, because
MS Excel is installed on the target machine. Follow these rules for all data access.

## Boundaries

- **Only `app/backend/excel_service.py` talks to Excel.** Views and dialogs must go through
  `inventory_repo.py`, never open the workbook themselves.
- The repo loads rows into a **pandas DataFrame** for in-memory search/filter; writes go back
  through `excel_service` and are saved.

## Password / role mapping

- **Read-only password** (`EXCEL_READ_PASSWORD`) → Excel "password to open" → `password=`.
- **Read-write password** (`EXCEL_WRITE_PASSWORD`) → Excel "password to modify" →
  `write_res_password=`.
- A **read-only session** opens with only the read password (the file stays read-only).
- A **write-capable session** (Admin/Privileged) also supplies the write password so `save()`
  works. Decide which passwords to pass based on the **session role**, and re-check the role in
  the backend before any write — never trust the UI alone.

## Always close Excel (no orphaned EXCEL.EXE)

Launch Excel **invisible/headless** and guarantee teardown in `finally`:

```python
import xlwings as xw

def _open(path, *, write):
    app = xw.App(visible=False, add_book=False)
    app.display_alerts = False
    app.screen_updating = False
    try:
        book = app.books.open(
            path,
            password=EXCEL_READ_PASSWORD,
            write_res_password=(EXCEL_WRITE_PASSWORD if write else None),
            read_only=not write,
        )
        try:
            ...  # read into DataFrame, or write cells then book.save()
        finally:
            book.close()
    finally:
        app.quit()  # also kill the app instance; verify no EXCEL.EXE remains
```

- Never leave an `App` or `Book` open across UI events. Open → operate → close within one call.
- Set `display_alerts=False` so password/save dialogs don't block headless runs.

## Column mapping

Use the single Persian-header ⇄ internal-field mapping (see `spec/data-model.md`). Reuse the
Persian header strings from `i18n/fa.py` for display; keep the parsing map in the backend model
module so it stays the source of truth.

## Validation on write
- `barcode` required, unique, stored as text (preserve leading zeros).
- `total_qty`, `qty_per_unit`, `min_threshold` non-negative integers.
- `unit_type` ∈ {`کارتن`, `عددی`}.

## Verification after changes
- Round-trip: edit a product, save, reopen → change persisted.
- Confirm **no orphaned `EXCEL.EXE`** process remains after operations (Task Manager / `tasklist`).
- A read-only session must be unable to save.

## References
- `spec/SPEC.md` §4 (data store), `spec/data-model.md` (columns & types).
