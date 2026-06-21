---
name: build-windows
description: Use when packaging this app into a Windows executable with PyInstaller, editing tools/build_exe.py, or troubleshooting the build. Covers one-folder layout, what must sit next to the exe (.env, font, logs), and smoke-testing. Trigger for any packaging/distribution task.
---

# build-windows

Package the app as a **PyInstaller one-folder** build (preferred over one-file so the Persian
font, `.env`, and produced `.log` files are visible next to the executable).

## Why one-folder
- Logs must be written **next to the executable** (`Path(sys.executable).parent` when frozen).
  One-folder keeps that directory stable and writable.
- `.env` is read from next to the exe; users edit it after install.
- The bundled font and other data files are easy to inspect/replace.

## Build steps (`tools/build_exe.py` automates these)

```bash
pip install -r requirements.txt   # includes pyinstaller (dev)
python tools/build_exe.py         # wraps PyInstaller with the right flags
```

Equivalent PyInstaller invocation the script should produce:

```bash
pyinstaller main.py \
  --name hyper_samen_one \
  --noconfirm --clean \
  --windowed \
  --add-data "app/frontend/assets/Vazirmatn.ttf;app/frontend/assets" \
  --icon app/frontend/assets/app.ico
```

> Note: on Windows `--add-data` uses `;` as the separator (`SRC;DEST`).

## Must sit next to the exe after install
- `.env` (copied from `.env.example`, filled in by the operator)
- the bundled Persian font (also embedded, but keep accessible)
- runtime-created files: `users.dat`, daily `YYYYMMDD.log` files, the inventory `.xlsx`

These runtime files are **created at run time**, not bundled — never ship real secrets/data.

## No Excel dependency
The app reads/writes the encrypted `.xlsx` with pure-Python `msoffcrypto` + `openpyxl`, so the
build needs **no** MS Excel on the runner or target machine. (See the `excel-data` skill.)

## CI release (GitHub Actions)
`.github/workflows/release.yml` builds the Windows `.zip` (on `windows-latest`) and Linux
`.tar.gz` (on `ubuntu-latest`) from `tools/build_exe.py` and attaches them to a GitHub Release.
It triggers on pushing a `v*` tag, or manually via `workflow_dispatch` (supply an existing tag).
The Linux job installs Qt runtime libs (`libegl1 libgl1 libxkbcommon0 libdbus-1-3 libxcb-cursor0`)
so PyInstaller can analyze PySide6. Releases use the built-in `GITHUB_TOKEN` (no extra secrets).

## Smoke test the build
1. Copy the `dist/hyper_samen_one/` folder to a clean path.
2. Place a filled-in `.env` next to the exe.
3. Launch; confirm:
   - the app starts with the Persian RTL UI,
   - a Jalali-named `YYYYMMDD.log` appears **next to the exe** and receives entries,
   - login + an encrypted-Excel read works,
   - no orphaned `EXCEL.EXE` after operations.

## References
- `spec/SPEC.md` §9 (logging next to exe), §11 (structure), CLAUDE.md (commands).
