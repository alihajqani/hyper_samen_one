# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/) and
versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.1.1] - 2026-06-22
### Changed
- Converted all development artifacts (log messages, comments, print statements, workflow
  step names, CHANGELOG, README) from Persian to English, while keeping the app GUI strings
  Persian (user-facing). Fixes `UnicodeEncodeError` on Windows CI runner (cp1252 console).
- Added `_force_utf8_stdio()` to `main.py` and `tools/build_exe.py` to reconfigure stdout/stderr
  to UTF-8 before any output, preventing encoding crashes on Windows.

## [1.1.0] - 2026-06-17
### Added
- GitHub Actions workflow (`.github/workflows/release.yml`): pushing a `v*` tag (or running
  manually via `workflow_dispatch`) builds Windows (`.zip`) and Linux Ubuntu (`.tar.gz`)
  executables and uploads them to GitHub Releases using the built-in `GITHUB_TOKEN` — no extra
  secrets required.

## [1.0.0] - 2026-06-16
### Added
- Version label on the home screen.
### Changed
- Updated `spec/SPEC.md` to reflect the pure-Python crypto backend (no MS Excel required).
- First stable release with all features: login and roles, inventory, barcode scan, product
  editing, user management, reports, and executable packaging.

## [0.9.0] - 2026-06-16
### Added
- `tools/build_exe.py` PyInstaller packaging script (one-folder, cross-platform
  Windows/Linux): OS-aware `--add-data` separator, bundled logo and font, optional icon,
  and `.env.example` copy.
- Packaging smoke-test on Linux: run the executable, `--check` mode, Jalali log created next
  to the executable, and successful GUI launch.
- "Build executable" section in README.

## [0.8.0] - 2026-06-16
### Added
- Reports view with "low-stock products" report and item count summary
  (`app/frontend/reports_view.py`).
- Excel export of the report (RTL `.xlsx` with Persian column headers) via a save-file dialog.
- Reports view wired into the main window.

## [0.7.0] - 2026-06-16
### Added
- User management view (admin-only) with a user table showing username, role, status, and
  created-at date (`app/frontend/users_view.py`).
- Add user (privileged or read-only), change password, toggle active/inactive, delete user.
- Self-protection: prevents deleting or disabling the currently logged-in admin account.

## [0.6.0] - 2026-06-16
### Added
- Add/edit product dialog with Persian validation (`app/frontend/product_dialog.py`):
  auto-computes `total_qty = carton_count × qty_per_carton`, accepts Persian digits,
  optional numeric fields, and duplicate-barcode check.
- Add / Edit / Delete buttons in the inventory toolbar — visible only for write-capable roles.
- Saves changes (add/edit/delete) to the encrypted Excel file and refreshes the table and
  low-stock badge.
- Double-click on a row opens the edit dialog.

## [0.5.0] - 2026-06-16
### Added
- Inventory view with full product table and Persian column headers
  (`app/frontend/inventory_view.py`).
- Live search on name / barcode / company / model / product type.
- Barcode scan bar (`app/frontend/widgets/search_bar.py`): pressing Enter (scanner input)
  selects and scrolls to the matching row; unknown barcode shows "not found" message.
- Low-stock row highlighting with a warning colour.
- Inventory view wired into the main window; low-stock badge updates on changes.

## [0.4.0] - 2026-06-16
### Added
- PySide6 GUI foundation with RTL layout and Samen brand colour palette
  (`app/frontend/app_qt.py`).
- Single source of truth for Persian strings (`app/frontend/i18n/fa.py`) and
  digit/Jalali-date formatting helpers (`app/frontend/utils_fa.py`).
- Login window with first-run "create initial admin" mode (`app/frontend/login_view.py`).
- Role-aware main window with sidebar, header, logo, low-stock badge, and logout
  (`app/frontend/main_window.py`). User-management page shown for admin only.
- Loads real inventory on startup (66 products) and displays low-stock count.

## [0.3.0] - 2026-06-16
### Added
- Fully cross-platform pure-Python encrypted Excel data layer
  (`app/backend/excel_service.py`): decrypt and re-encrypt with `msoffcrypto`, edit with
  `openpyxl` — no Microsoft Excel installation required.
- In-memory inventory repository with search, barcode index, and add/update/delete
  (`app/backend/inventory_repo.py`).
- Low-stock detection (`app/backend/alerts.py`).
- Successfully reads real `data/samen.xlsx` (sheet "همه", 66 products) and passes write
  round-trip tests.
### Changed
- Replaced xlwings/COM approach with the pure-Python crypto backend (simpler, no Excel
  dependency).
- Removed `pandas` and `xlwings` from dependencies.

## [0.2.0] - 2026-06-16
### Added
- Domain models: `Role`, `User`, and `Product` aligned with the real `samen.xlsx` columns
  (`app/backend/models.py`).
- Fernet-encrypted user store with bcrypt password hashing (`app/backend/user_store.py`):
  add/delete/toggle-active user, change password.
- Auth service and session with role detection (`app/backend/auth.py`).
- First-run bootstrap: creates the initial admin account if no users exist.

## [0.1.0] - 2026-06-16
### Added
- Initial project structure and Python packaging (`pyproject.toml`, `requirements.txt`).
- Single-source version management (`app/__version__.py`) and `CHANGELOG.md`.
- App configuration via `.env` with exe-adjacent path resolution (`app/backend/config.py`).
- Daily Jalali-dated log handler writing `YYYYMMDD.log` next to the executable
  (`app/backend/logging_setup.py`).
- `main.py` entry point with `--check` health-check mode.
- Documentation: `CLAUDE.md`, `spec/`, and custom skills.

[Unreleased]: https://github.com/alihajqani/hyper_samen_one/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/alihajqani/hyper_samen_one/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/alihajqani/hyper_samen_one/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/alihajqani/hyper_samen_one/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/alihajqani/hyper_samen_one/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/alihajqani/hyper_samen_one/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/alihajqani/hyper_samen_one/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/alihajqani/hyper_samen_one/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/alihajqani/hyper_samen_one/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/alihajqani/hyper_samen_one/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/alihajqani/hyper_samen_one/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/alihajqani/hyper_samen_one/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/alihajqani/hyper_samen_one/releases/tag/v0.1.0
