# UI Specification (Persian / RTL)

## Global rules

- **Direction:** right-to-left everywhere (`QApplication.setLayoutDirection(Qt.RightToLeft)`).
- **Font:** bundled Persian font (Vazirmatn) applied app-wide.
- **Strings:** every visible string comes from `app/frontend/i18n/fa.py` (keys → Persian text).
  No literals in widget code.
- **Numbers:** rendered with Persian digits via `utils_fa.py` (`to_persian_digits`).
- **Dates:** rendered in the Jalali calendar via `utils_fa.py`.
- **Feedback:** validation errors, confirmations, and notifications are Persian message boxes.

## Screens

### 1. Login (`login_view.py`)
- Fields: نام کاربری (username), رمز عبور (password), دکمه ورود (login button).
- On first run with no users: redirect to an **initial admin setup** form
  (username + password + confirm) instead of login.
- Wrong credentials / disabled user → Persian error message; failures are logged.

### 2. Main window (`main_window.py`)
- Role-aware shell with a navigation sidebar/menu (RTL):
  - موجودی کالا (Inventory) — all roles
  - گزارش‌ها (Reports) — all roles
  - مدیریت کاربران (User management) — **Admin only**
  - خروج (Logout)
- Header shows current user + role (Persian) and a **low-stock badge** (count of low items).

### 3. Inventory view (`inventory_view.py`)
- A **scan/search field** at the top (focused by default) — accepts barcode-scanner input;
  on Enter, selects/scrolls to the matching row. Unknown barcode → "کالا یافت نشد".
- Free-text search filters the table (name/barcode/company/model).
- Table columns = the 9 Persian headers from [`data-model.md`](data-model.md).
- **Low-stock rows visually flagged** (e.g. colored row/cell + warning icon).
- Toolbar (write roles only): افزودن کالا (add), ویرایش (edit), حذف (delete).
  These buttons are hidden/disabled for Read-only users.

### 4. Product add/edit dialog (`product_dialog.py`)
- One field per inventory column (Persian labels), with validation:
  - بارکد required & unique; numeric fields non-negative integers; نوع واحد = combo
    (کارتن / عددی).
- Barcode field accepts scanner input.
- Save/cancel: دخیره / انصراف. Save is rejected server-side if the session role lacks write
  permission.

### 5. User management view (`users_view.py`) — Admin only
- List of users (نام کاربری، سطح دسترسی، وضعیت، تاریخ ایجاد).
- Create user: نام کاربری + رمز عبور + سطح دسترسی (کاربر ارشد / کاربر فقط‌خواندنی).
- Actions: حذف کاربر، تغییر رمز عبور، فعال/غیرفعال کردن.

### 6. Reports view (`reports_view.py`)
- **Low-stock report:** lists products where `total_qty ≤ min_threshold`, Persian headers.
- Optional export (e.g. to a Persian-labeled file). All counts/dates in Persian/Jalali.

## Persian string inventory (starter keys for `i18n/fa.py`)

Grouped by area; this is the seed list (extend as views are built):

```
# App / general
app_title            = "سامانه مدیریت موجودی هایپرمارکت"
btn_save             = "ذخیره"
btn_cancel           = "انصراف"
btn_add              = "افزودن کالا"
btn_edit             = "ویرایش"
btn_delete           = "حذف"
btn_login            = "ورود"
btn_logout           = "خروج"
confirm_yes          = "بله"
confirm_no           = "خیر"

# Auth
lbl_username         = "نام کاربری"
lbl_password         = "رمز عبور"
lbl_password_confirm = "تکرار رمز عبور"
msg_login_failed     = "نام کاربری یا رمز عبور نادرست است"
msg_user_disabled    = "این کاربر غیرفعال است"
setup_admin_title    = "ایجاد مدیر اولیه"

# Navigation
nav_inventory        = "موجودی کالا"
nav_reports          = "گزارش‌ها"
nav_users            = "مدیریت کاربران"

# Inventory columns
col_name             = "نام کالا"
col_barcode          = "بارکد"
col_unit_type        = "نوع واحد"
col_total_qty        = "موجودی کل"
col_qty_per_unit     = "تعداد در هر کارتن/واحد"
col_min_threshold    = "حد آستانه هشدار موجودی"
col_product_type     = "نوع کالا"
col_company          = "شرکت"
col_model            = "مدل"

# Unit types
unit_carton          = "کارتن"
unit_single          = "عددی"

# Roles
role_admin           = "مدیر"
role_privileged      = "کاربر ارشد"
role_readonly        = "کاربر فقط‌خواندنی"

# Inventory / scan
ph_scan_search       = "بارکد را اسکن کنید یا جستجو کنید…"
msg_product_not_found = "کالا یافت نشد"
warn_low_stock       = "موجودی کم"

# Reports
report_low_stock_title = "گزارش کالاهای رو به اتمام"

# Validation
err_required         = "این فیلد الزامی است"
err_barcode_dup      = "این بارکد قبلاً ثبت شده است"
err_non_negative_int = "مقدار باید عددی صحیح و نامنفی باشد"

# Generic feedback
msg_saved            = "با موفقیت ذخیره شد"
msg_deleted          = "با موفقیت حذف شد"
err_no_permission    = "شما اجازه انجام این عملیات را ندارید"
```

## Accessibility / UX notes
- Default focus to the scan/search field on the inventory view for fast scanning.
- Keep the low-stock badge visible from the main window.
- Use clear Persian confirmation dialogs before destructive actions (delete user/product).
