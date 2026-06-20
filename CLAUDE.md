# CLAUDE.md

Guidance for working in this repository. Read this before writing code.

## What this is

`hyper_samen_one` is a **Windows desktop application** (Python) for managing a hypermarket's
inventory. It is **single-PC, multi-login**: one machine, several people log in with their own
accounts and roles. The data store is a **password-protected Excel file**; user accounts live in a
**separate encrypted file**. The entire UI is **Persian (Farsi), right-to-left**.

Full requirements live in [`spec/`](spec/):
- [`spec/SPEC.md`](spec/SPEC.md) — functional + technical specification.
- [`spec/data-model.md`](spec/data-model.md) — Excel columns, types, user-store schema.
- [`spec/ui-spec.md`](spec/ui-spec.md) — screens, RTL behavior, Persian string inventory.

> **Status:** Documentation/scaffolding only. Application code is created phase-by-phase; do not
> add features outside the current phase without confirming.

## Tech stack

| Concern | Choice | Notes |
|---|---|---|
| GUI | **PySide6 (Qt)** | RTL layout, Persian font (Vazirmatn) |
| Excel I/O | **xlwings** (COM) | MS Excel is installed on target; honors both passwords natively |
| In-memory data | **pandas** (+ `openpyxl` as engine fallback) | fast filtering/search |
| Dates | **jdatetime** | Solar Hijri (Jalali) for log names + UI |
| Password hashing | **bcrypt** | user passwords never stored plaintext |
| User-store encryption | **cryptography** (Fernet) | encrypts the local user DB |
| Env loading | **python-dotenv** | reads `.env` next to the exe |
| Packaging | **PyInstaller** (one-folder) | `tools/build_exe.py` |

## Architecture

Layered backend/frontend split — see the tree in [`spec/SPEC.md`](spec/SPEC.md). Key modules:

- `app/backend/excel_service.py` — the **only** place that talks to Excel via COM.
- `app/backend/inventory_repo.py` — domain-level CRUD over inventory rows.
- `app/backend/user_store.py` / `auth.py` — encrypted user accounts + login/role state.
- `app/backend/logging_setup.py` — Jalali daily log handler.
- `app/frontend/i18n/fa.py` — **single source of truth for every Persian string.**
- `app/frontend/utils_fa.py` — Persian-digit + Jalali-date formatting helpers.

## Commands

```bash
# Install deps (Windows, with MS Excel present)
pip install -r requirements.txt

# Run the app
python main.py

# Build the Windows executable (one-folder)
python tools/build_exe.py
```

## Conventions — read before editing

1. **Persian strings are centralized.** Every user-facing string (labels, buttons, messages,
   column headers, report text) lives in `app/frontend/i18n/fa.py`. **No hardcoded UI strings in
   widgets.** See the `persian-ui` skill.
2. **RTL everywhere.** The app sets `Qt.RightToLeft`. New views/dialogs must lay out correctly in
   RTL. Display numbers and dates through `utils_fa.py` (Persian digits, Jalali calendar).
3. **All Excel access goes through `excel_service.py` → `inventory_repo.py`.** Never open the
   workbook from a view. **Always close the COM workbook/app in a `finally` block** to avoid
   orphaned `EXCEL.EXE` processes. See the `excel-data` skill.
4. **Passwords map to Excel-native features:** read-only password → Excel "password to open";
   read-write password → Excel "password to modify" (`write_res_password`). Read-only sessions
   open without the write password (file stays read-only).
5. **Roles gate actions, not just UI.** Check the role in the backend before any write, in
   addition to hiding/disabling UI. Roles: `ADMIN` (everything + user mgmt), `PRIVILEGED`
   (everything except user mgmt), `READ_ONLY` (view only).
6. **Logs are Jalali-named and exe-adjacent.** Log files are `YYYYMMDD.log` in Jalali digits
   (e.g. `14050512.log`), one per day, written next to the entry point (`sys.executable` when
   frozen, else project root). Don't hardcode a logs directory elsewhere.
7. **Secrets stay out of git.** `.env`, `users.dat`, `*.log`, and the inventory `.xlsx` are
   gitignored. Commit `.env.example`, never `.env`.

## Security expectations (be honest about these)

- Excel passwords and the Fernet key live in `.env` **next to the exe**. This is **obfuscation,
  not strong security** — anyone with file access can read them. Acceptable for an internal
  single-PC tool; do not present it as more than that.
- App-user passwords are **bcrypt-hashed**. Never log or store them in plaintext.
- Never write secrets into log files.

## Custom skills (`.claude/skills/`)

- **`persian-ui`** — adding/maintaining Persian RTL UI; keeping strings centralized.
- **`excel-data`** — safe use of the xlwings Excel layer (passwords, cleanup, repo boundary).
- **`build-windows`** — packaging with PyInstaller and smoke-testing the build.

## Do / Don't

- ✅ Add new UI text to `i18n/fa.py`; reference it by key.
- ✅ Route every inventory read/write through the repo layer.
- ✅ Wrap COM Excel operations in try/finally with guaranteed close.
- ❌ Don't hardcode Persian (or English) UI strings in widgets.
- ❌ Don't open the inventory Excel directly from a view.
- ❌ Don't commit `.env`, `users.dat`, logs, or the inventory file.
- ❌ Don't bypass role checks on the backend.
