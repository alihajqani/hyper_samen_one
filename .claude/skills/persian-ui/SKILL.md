---
name: persian-ui
description: Use when adding or editing any user-facing UI in this app (PySide6 views, dialogs, labels, messages, reports). Enforces fully-Persian RTL text, centralized strings in i18n/fa.py, and Persian-digit/Jalali formatting. Trigger when creating/modifying files under app/frontend/.
---

# persian-ui

This app's UI must be **fully Persian (Farsi) and right-to-left**. Follow these rules whenever you
touch anything visible to the user.

## Hard rules

1. **No hardcoded UI strings.** Every visible string (labels, buttons, placeholders, message-box
   text, column headers, report text, validation errors) must be defined in
   `app/frontend/i18n/fa.py` and referenced by key. Never put a literal string in a widget.
2. **RTL layout.** The app sets `Qt.RightToLeft` globally. New views/dialogs must read correctly
   in RTL — check alignment, label/field order, and icon sides.
3. **Persian digits & Jalali dates.** Format every displayed number with
   `utils_fa.to_persian_digits()` and every date with the Jalali helpers in `utils_fa.py`. Do not
   show Western digits or Gregorian dates in the UI.
4. **Persian font.** Rely on the app-wide Vazirmatn font set in `app_qt.py`; don't override fonts
   per-widget unless intentional.

## Workflow for adding UI text

1. Add a key + Persian value to `app/frontend/i18n/fa.py` (see seed list in
   `spec/ui-spec.md`).
2. Reference the key in the widget. Group keys by area (auth, nav, columns, validation, …).
3. For numbers/dates, wrap with the `utils_fa` helpers.

## Self-check before finishing (grep for stray non-Persian UI strings)

Look for hardcoded quoted strings in views that should have come from `i18n/fa.py`:

```bash
# Quoted Latin-letter strings inside frontend views (candidates for extraction)
grep -rnE "(setText|setWindowTitle|setPlaceholderText|addItem|setToolTip)\(\s*[\"'][^\"']*[A-Za-z][^\"']*[\"']" app/frontend \
  | grep -v "i18n/fa.py"
```

Any hit (other than keys/format placeholders) should be moved into `i18n/fa.py`. Also verify new
screens visually in RTL and that all digits/dates render in Persian/Jalali.

## References
- `spec/ui-spec.md` — screens, RTL behavior, and the starter Persian string keys.
- `spec/data-model.md` — the 9 Persian column headers.
