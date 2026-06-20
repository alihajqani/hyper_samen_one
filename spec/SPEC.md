# SPEC — Hypermarket Inventory Management System

**Project:** `hyper_samen_one`
**Type:** Windows desktop application (Python, PySide6)
**Language of UI:** Persian (Farsi), fully right-to-left
**Last updated:** 1405 (2026)

---

## 1. Purpose

A desktop tool that lets hypermarket staff view and manage inventory stored in a
password-protected Excel file. It supports role-based access, barcode-scanner lookups,
low-stock alerts, and Persian (Jalali) daily logging.

## 2. Scope & deployment model

- **Single PC, multiple logins.** One Windows machine; multiple people log in with their own
  accounts/roles at different times. No concurrent multi-machine access → **no network file
  locking required**.
- **MS Excel is installed** on the machine, enabling COM automation (xlwings) for reliable
  read/write with Excel's native passwords.
- Distributed as a **PyInstaller one-folder** build; `.env`, the Persian font, and produced
  `.log` files sit next to the executable.

## 3. Roles & permissions

| Role | Persian | View inventory | Edit inventory | Manage users |
|---|---|---|---|---|
| Administrator | مدیر | ✅ | ✅ | ✅ |
| Privileged user | کاربر ارشد | ✅ | ✅ | ❌ |
| Read-only user | کاربر فقط‌خواندنی | ✅ | ❌ | ❌ |

- Role checks are enforced **both** in the UI (hide/disable controls) **and** in the backend
  (reject writes from non-write roles).
- On **first run**, if no users exist, the app forces creation of the initial Administrator.

## 4. Data store — encrypted Excel

- The inventory is a **password-protected `.xlsx`** with two passwords:
  - **Read-only password** → Excel "password to open" (decrypts the file).
  - **Read-write password** → Excel "password to modify" (`write_res_password`; required to save).
- Both passwords are read from `.env` (`EXCEL_READ_PASSWORD`, `EXCEL_WRITE_PASSWORD`).
- **Read-only sessions** open the workbook with only the read password → file is read-only.
- **Write-capable sessions** (Admin/Privileged) also supply the write password → saving allowed.
- Implementation: **xlwings** (`app.books.open(path, password=..., write_res_password=...)`),
  Excel launched **invisible/headless**, workbook + app **always closed in `finally`**.
- Inventory rows are loaded into a **pandas DataFrame** for fast in-memory search/filter; edits
  are written back through xlwings and saved.
- **Admin "upload initial inventory"**: the admin selects an encrypted `.xlsx`; the app validates
  the columns and registers it as the active data file (replacing any previous active file).
- Inventory columns: see [`data-model.md`](data-model.md).

## 5. User store — separate encrypted file

- A local file `users.dat` holding a JSON array of users, **Fernet-encrypted**
  (key in `.env` → `USER_STORE_KEY`).
- Per-user fields: `username`, `password_hash` (bcrypt), `role`, `created_at` (Jalali).
- Admin operations: create user (username + password + role of Privileged or Read-only),
  list users, delete/disable user, reset password.
- Schema details in [`data-model.md`](data-model.md).

## 6. Authentication & session

- Login screen: username + password. Verify against bcrypt hash in the user store.
- On success, hold an in-memory session: current user + role. The session decides which Excel
  passwords are supplied (write password only for write roles) and which UI is shown.
- Log all auth events (success/failure, logout) — never log passwords.

## 7. Barcode scanner

- Scanners behave as **HID keyboard** devices: they type the barcode then send Enter.
- The inventory view has a **scan/search field** that, on Enter, looks up the barcode in the
  DataFrame and selects/scrolls to the matching row. Unknown barcode → Persian "not found".
- Product add/edit dialogs accept scanner input directly into the barcode field.
- No custom serial driver assumed.

## 8. Low-stock alerts

- A product is **low** when `total_qty ≤ min_threshold`.
- Low products are visually flagged in the inventory table and listed in the **reports view**.
- A summary count of low-stock items is surfaced on the main window.

## 9. Logging

- One `.log` file **per day**, named with the **Jalali date** in Persian-calendar digits:
  format `YYYYMMDD.log`, e.g. `14050512.log` (year 1405, month 05, day 12).
- Files are written **next to the executable**: `Path(sys.executable).parent` when frozen,
  else the project root in development.
- Rollover happens at local midnight (date checked on emit).
- Logged: app start/stop, auth events, inventory create/update/delete, Excel open/save,
  errors with stack traces. **No secrets in logs.**

## 10. Localization (Persian / RTL)

- `QApplication` layout direction = `Qt.RightToLeft`; bundled Persian font (Vazirmatn).
- **Every** user-facing string lives in `app/frontend/i18n/fa.py`. No hardcoded literals in views.
- All displayed numbers use **Persian digits**; all dates use the **Jalali** calendar
  (via `utils_fa.py`).
- Column headers, dialogs, validation messages, reports, and notifications are all Persian.
- See [`ui-spec.md`](ui-spec.md).

## 11. Project structure

```
hyper_samen_one/
├── .env / .env.example
├── requirements.txt
├── pyproject.toml
├── CLAUDE.md
├── spec/{SPEC.md, data-model.md, ui-spec.md}
├── main.py
├── app/
│   ├── backend/{config, logging_setup, excel_service, inventory_repo,
│   │            models, auth, user_store, alerts}.py
│   └── frontend/
│       ├── app_qt.py
│       ├── i18n/fa.py
│       ├── utils_fa.py
│       ├── widgets/
│       ├── login_view.py
│       ├── main_window.py
│       ├── inventory_view.py
│       ├── product_dialog.py
│       ├── users_view.py
│       └── reports_view.py
└── tools/build_exe.py
```

## 12. Configuration (`.env`)

| Variable | Purpose |
|---|---|
| `EXCEL_READ_PASSWORD` | Excel password-to-open (read-only access) |
| `EXCEL_WRITE_PASSWORD` | Excel password-to-modify (read-write access) |
| `USER_STORE_KEY` | Fernet key encrypting `users.dat` |
| `INVENTORY_FILE` | Path to the active inventory `.xlsx` (optional; default next to exe) |
| `LOG_LEVEL` | Logging verbosity (default `INFO`) |

See [`.env.example`](../.env.example).

## 13. Security notes

- `.env` secrets next to the exe = **obfuscation, not strong security**. Documented openly.
- User passwords are **bcrypt-hashed**; never stored/logged in plaintext.
- `.env`, `users.dat`, `*.log`, and the inventory `.xlsx` are gitignored.

## 14. Implementation phases

0. **Docs/scaffolding** (this spec, CLAUDE.md, skills, `.env.example`) — done before code.
1. **Backend foundation:** config, Jalali logging, models, user store, auth.
2. **Excel layer:** excel_service, inventory_repo, alerts.
3. **Frontend foundation:** Qt app/RTL/font, i18n strings, utils, login, role-aware main window.
4. **Feature views:** inventory (search/scan), product dialog, users (admin), reports.
5. **Packaging & polish:** PyInstaller build, icon, README, verification.

## 15. Acceptance / verification

See the **Verification** section of the approved plan. Summary: confirm Jalali log creation &
rollover; encrypted-Excel edit round-trip with no orphaned `EXCEL.EXE`; role enforcement;
barcode lookup; low-stock flagging; fully-Persian RTL UI; working packaged build.

## 16. Open assumptions

- Barcode scanner is a standard HID/keyboard-wedge device.
- One active inventory `.xlsx` at a time; admin upload replaces it.
- Inventory lives on one worksheet with a header in the first row.
