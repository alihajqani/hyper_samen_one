"""Persian formatting helpers: digits and Jalali dates.

Used everywhere a number or date is shown so the UI stays fully Persian.
"""

from __future__ import annotations

import jdatetime

_PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
_FA_TO_EN = {ord(p): str(i) for i, p in enumerate(_PERSIAN_DIGITS)}
_FA_TO_EN[ord("٫")] = "."  # arabic decimal separator
_EN_TO_FA = {ord(str(i)): p for i, p in enumerate(_PERSIAN_DIGITS)}


def to_persian_digits(value) -> str:
    """Convert any Western digits in ``value`` to Persian digits."""
    return str(value).translate(_EN_TO_FA)


def to_english_digits(value) -> str:
    """Convert Persian/Arabic digits in ``value`` to Western digits (for parsing)."""
    return str(value).translate(_FA_TO_EN)


def format_int(value, *, grouped: bool = True) -> str:
    """Format an integer with optional thousands grouping, in Persian digits.

    ``None`` / empty renders as an em dash placeholder.
    """
    from app.frontend.i18n import fa

    if value is None or value == "":
        return fa.EMPTY_CELL
    try:
        n = int(value)
    except (TypeError, ValueError):
        return to_persian_digits(value)
    text = f"{n:,}" if grouped else str(n)
    return to_persian_digits(text)


def display(value) -> str:
    """Display any cell value: empty -> placeholder, numbers -> Persian digits."""
    from app.frontend.i18n import fa

    if value is None or (isinstance(value, str) and not value.strip()):
        return fa.EMPTY_CELL
    if isinstance(value, (int, float)):
        return format_int(value)
    return to_persian_digits(str(value))


def jalali_now(fmt: str = "%Y/%m/%d %H:%M") -> str:
    return to_persian_digits(jdatetime.datetime.now().strftime(fmt))


def jalali_today(fmt: str = "%Y/%m/%d") -> str:
    return to_persian_digits(jdatetime.date.today().strftime(fmt))
