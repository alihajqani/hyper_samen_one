"""Single source of truth for every user-facing Persian string.

Do NOT hardcode UI strings elsewhere — add a constant here and reference it.
Grouped by area for easy auditing (see the `persian-ui` skill).
"""

# --- App / general -----------------------------------------------------------
APP_TITLE = "سامانه مدیریت موجودی هایپرمارکت ثامن"
APP_SHORT = "هایپرمارکت ثامن"

BTN_SAVE = "ذخیره"
BTN_CANCEL = "انصراف"
BTN_ADD = "افزودن کالا"
BTN_EDIT = "ویرایش"
BTN_DELETE = "حذف"
BTN_REFRESH = "بازخوانی"
BTN_LOGIN = "ورود"
BTN_LOGOUT = "خروج"
BTN_CREATE = "ایجاد"
BTN_CLOSE = "بستن"
BTN_EXPORT = "خروجی گرفتن"

CONFIRM_YES = "بله"
CONFIRM_NO = "خیر"
TITLE_CONFIRM = "تأیید"
TITLE_ERROR = "خطا"
TITLE_INFO = "پیام"
TITLE_WARNING = "هشدار"

# --- Auth --------------------------------------------------------------------
LBL_USERNAME = "نام کاربری"
LBL_PASSWORD = "رمز عبور"
LBL_PASSWORD_CONFIRM = "تکرار رمز عبور"
LOGIN_TITLE = "ورود به سامانه"
SETUP_ADMIN_TITLE = "ایجاد مدیر اولیه"
SETUP_ADMIN_HINT = "هیچ کاربری وجود ندارد. لطفاً نخستین حساب مدیر را بسازید."
MSG_LOGIN_FAILED = "نام کاربری یا رمز عبور نادرست است"
MSG_USER_DISABLED = "این کاربر غیرفعال است"
MSG_PASSWORD_MISMATCH = "رمز عبور و تکرار آن یکسان نیستند"
MSG_FILL_ALL_FIELDS = "لطفاً همهٔ فیلدها را پر کنید"
MSG_WELCOME = "خوش آمدید"

# --- Navigation --------------------------------------------------------------
LBL_VERSION = "نسخه {version}"
NAV_HOME = "خانه"
NAV_INVENTORY = "موجودی کالا"
NAV_REPORTS = "گزارش‌ها"
NAV_USERS = "مدیریت کاربران"

# --- Roles -------------------------------------------------------------------
ROLE_ADMIN = "مدیر"
ROLE_PRIVILEGED = "کاربر ارشد"
ROLE_READONLY = "کاربر فقط‌خواندنی"
LBL_ROLE = "سطح دسترسی"
LBL_LOGGED_IN_AS = "کاربر فعلی"

# --- Inventory columns (display labels) --------------------------------------
COL_NAME = "نام کالا"
COL_BARCODE = "بارکد"
COL_CARTON_COUNT = "تعداد کارتن/شِل"
COL_QTY_PER_CARTON = "تعداد در هر کارتن/شِل"
COL_TOTAL_QTY = "موجودی کل"
COL_MIN_THRESHOLD = "حد کمینه (هشدار)"
COL_PRODUCT_TYPE = "نوع کالا"
COL_COMPANY = "شرکت"
COL_MODEL = "مدل"
COL_SECTION = "قسمت"

# Inventory column labels keyed by internal field name (matches models.INVENTORY_FIELDS).
COLUMN_LABELS = {
    "name": COL_NAME,
    "barcode": COL_BARCODE,
    "carton_count": COL_CARTON_COUNT,
    "qty_per_carton": COL_QTY_PER_CARTON,
    "total_qty": COL_TOTAL_QTY,
    "min_threshold": COL_MIN_THRESHOLD,
    "product_type": COL_PRODUCT_TYPE,
    "company": COL_COMPANY,
    "model": COL_MODEL,
    "section": COL_SECTION,
}

# --- Inventory view / scan ---------------------------------------------------
PH_SCAN_SEARCH = "بارکد را اسکن کنید یا جستجو کنید…"
MSG_PRODUCT_NOT_FOUND = "کالایی با این بارکد یافت نشد"
WARN_LOW_STOCK = "موجودی کم"
LBL_LOW_STOCK_BADGE = "کالای رو به اتمام: {count}"
LBL_TOTAL_ITEMS = "تعداد کل اقلام: {count}"
MSG_NO_RESULTS = "نتیجه‌ای یافت نشد"
TITLE_ADD_PRODUCT = "افزودن کالای جدید"
TITLE_EDIT_PRODUCT = "ویرایش کالا"
CONFIRM_DELETE_PRODUCT = "آیا از حذف کالای «{name}» مطمئن هستید؟"

# --- Users view --------------------------------------------------------------
TITLE_ADD_USER = "افزودن کاربر"
COL_USER_STATUS = "وضعیت"
COL_CREATED_AT = "تاریخ ایجاد"
STATUS_ACTIVE = "فعال"
STATUS_INACTIVE = "غیرفعال"
BTN_RESET_PASSWORD = "تغییر رمز"
BTN_TOGGLE_ACTIVE = "فعال/غیرفعال"
CONFIRM_DELETE_USER = "آیا از حذف کاربر «{username}» مطمئن هستید؟"
TITLE_RESET_PASSWORD = "تغییر رمز عبور کاربر «{username}»"

# --- Reports -----------------------------------------------------------------
REPORT_LOW_STOCK_TITLE = "گزارش کالاهای رو به اتمام"
REPORT_EMPTY = "هیچ کالای رو به اتمامی وجود ندارد"
EXPORT_DONE = "گزارش با موفقیت ذخیره شد:\n{path}"

# --- Validation / feedback ---------------------------------------------------
ERR_REQUIRED = "این فیلد الزامی است"
ERR_NAME_REQUIRED = "نام کالا الزامی است"
ERR_NON_NEGATIVE_INT = "مقدار باید عددی صحیح و نامنفی باشد"
ERR_BARCODE_DUP = "این بارکد قبلاً برای کالای دیگری ثبت شده است"
MSG_SAVED = "با موفقیت ذخیره شد"
MSG_DELETED = "با موفقیت حذف شد"
MSG_CREATED = "با موفقیت ایجاد شد"
ERR_NO_PERMISSION = "شما اجازهٔ انجام این عملیات را ندارید"
ERR_GENERIC = "خطایی رخ داد: {detail}"
PLACEHOLDER_COMING_SOON = "این بخش به‌زودی اضافه می‌شود."

# --- Empty value display -----------------------------------------------------
EMPTY_CELL = "—"
