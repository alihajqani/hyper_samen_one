"""Password and recovery-code policy checks (Persian error messages).

Kept in the backend so the rules are enforced regardless of the UI, mirroring the
existing pattern of Persian error text raised from ``user_store.py``.
"""

from __future__ import annotations

import re

MIN_PASSWORD_LEN = 8
MIN_RECOVERY_LEN = 8


class PolicyError(ValueError):
    """Raised when a password / recovery code violates the policy."""


def validate_password(password: str) -> None:
    """Require at least 8 characters including one lowercase Latin letter."""
    if not password or len(password) < MIN_PASSWORD_LEN:
        raise PolicyError("رمز عبور باید حداقل ۸ نویسه باشد.")
    if not re.search(r"[a-z]", password):
        raise PolicyError("رمز عبور باید دست‌کم یک حرف کوچک انگلیسی (a–z) داشته باشد.")


def validate_recovery_code(code: str) -> None:
    """Require a recovery (master) code of at least 8 characters."""
    if not code or len(code.strip()) < MIN_RECOVERY_LEN:
        raise PolicyError("شاه‌کلید بازیابی باید حداقل ۸ نویسه باشد.")
