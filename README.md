# Hyper Market Samen — Inventory Management

A Persian (RTL) Windows desktop application for managing a hypermarket's inventory.
Data is stored in a password-protected Excel file; user accounts and roles are managed locally.

See [CHANGELOG.md](CHANGELOG.md) for the version history.

## Features (by version)

- **v0.1.0** — Project structure, daily Jalali-dated logging, configuration.
- **v0.2.0** — Encrypted user store, authentication, roles.
- **v0.3.0** — Pure-Python encrypted Excel inventory reader/writer.
- **v0.4.0** — Persian RTL GUI (login, main window).
- **v0.5.0** — Inventory table, live search, barcode scan, low-stock alert.
- **v0.6.0** — Add / edit / delete products with encrypted Excel save.
- **v0.7.0** — User management (admin only).
- **v0.8.0** — Low-stock report with Excel export.
- **v0.9.0** — Windows / Linux executable packaging (PyInstaller).
- **v1.0.0** — First stable release.
- **v1.1.0** — GitHub Actions CI: builds Windows `.exe` and Linux binary on tag push.
- **v1.1.1** — All dev artifacts (logs, comments, workflow) converted to English.

## Requirements

- Python 3.10+ (tested on 3.12)
- No Microsoft Excel installation needed — the backend uses pure-Python `msoffcrypto` + `openpyxl`.

## Development setup (Ubuntu / Windows)

```bash
python3 -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env            # fill in passwords and key
python main.py --check          # health check
python main.py                  # launch the app (from v0.4.0)
```

## Building the executable (Windows / Linux)

```bash
pip install -r requirements-dev.txt
python tools/build_exe.py
```

Output is a one-folder bundle at `dist/hyper_samen_one/`. Runtime files that must sit next
to the executable:

- `.env` — Excel passwords + user-store key (fill in before distributing).
- `data/samen.xlsx` — encrypted inventory file.
- `users.dat` and `YYYYMMDD.log` — created automatically on first run.

Optional extras (place before building):

- `data/app.ico` — Windows taskbar icon.
- `app/frontend/assets/Vazirmatn-Regular.ttf` — bundled Persian font.

## Project structure

```
app/backend/    config, logging, Excel data layer, auth, models
app/frontend/   PySide6 views and dialogs (Persian, RTL)
spec/           full functional and technical specification
tools/          build scripts
```

## Releases

GitHub Actions builds Windows (`.zip`) and Linux Ubuntu (`.tar.gz`) executables on every
version tag push. Download from the
[Releases](https://github.com/alihajqani/hyper_samen_one/releases) page.

## Security notes

Passwords are stored in `.env` next to the executable — this is **obfuscation, not strong
security**. Acceptable for an internal single-PC tool; do not treat it as more than that.
App-user passwords are **bcrypt-hashed**. The files `.env`, `users.dat`, `*.log`, and the
inventory `.xlsx` are gitignored.
