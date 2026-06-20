"""Encrypted local user store.

Users are kept in a Fernet-encrypted JSON document (``users.dat``) next to the
executable. Passwords are bcrypt-hashed; the Fernet key comes from ``.env``
(``USER_STORE_KEY``). See ``spec/data-model.md``.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import bcrypt
import jdatetime
from cryptography.fernet import Fernet, InvalidToken

from app.backend.models import Role, User

logger = logging.getLogger("hyper_samen.user_store")

_SCHEMA_VERSION = 1


class UserStoreError(Exception):
    """Raised for user-store problems (bad key, corrupt file, duplicate user)."""


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _now_jalali() -> str:
    return jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")


class UserStore:
    """Load/modify/save the encrypted collection of users."""

    def __init__(self, path: Path, key: str):
        if not key:
            raise UserStoreError("کلید رمزنگاری کاربران تنظیم نشده است (USER_STORE_KEY).")
        self._path = Path(path)
        try:
            self._fernet = Fernet(key.encode("utf-8"))
        except (ValueError, TypeError) as exc:
            raise UserStoreError("کلید رمزنگاری کاربران نامعتبر است.") from exc
        self._users: dict[str, User] = {}
        self._load()

    # -- persistence ----------------------------------------------------------

    def _load(self) -> None:
        if not self._path.exists():
            self._users = {}
            return
        try:
            decrypted = self._fernet.decrypt(self._path.read_bytes())
            payload = json.loads(decrypted.decode("utf-8"))
        except (InvalidToken, ValueError) as exc:
            raise UserStoreError("فایل کاربران خراب است یا کلید اشتباه است.") from exc
        self._users = {
            u["username"].lower(): User.from_dict(u) for u in payload.get("users", [])
        }

    def _save(self) -> None:
        payload = {
            "version": _SCHEMA_VERSION,
            "users": [u.to_dict() for u in self._users.values()],
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        token = self._fernet.encrypt(data)
        tmp = self._path.with_suffix(self._path.suffix + ".tmp")
        tmp.write_bytes(token)
        tmp.replace(self._path)

    # -- queries --------------------------------------------------------------

    def has_users(self) -> bool:
        return bool(self._users)

    def list_users(self) -> list[User]:
        return sorted(self._users.values(), key=lambda u: u.username.lower())

    def get(self, username: str) -> User | None:
        return self._users.get(username.lower())

    # -- mutations ------------------------------------------------------------

    def add_user(self, username: str, password: str, role: Role) -> User:
        username = username.strip()
        if not username:
            raise UserStoreError("نام کاربری نمی‌تواند خالی باشد.")
        if not password:
            raise UserStoreError("رمز عبور نمی‌تواند خالی باشد.")
        if username.lower() in self._users:
            raise UserStoreError("این نام کاربری قبلاً ثبت شده است.")
        user = User(
            username=username,
            password_hash=hash_password(password),
            role=role,
            is_active=True,
            created_at=_now_jalali(),
        )
        self._users[username.lower()] = user
        self._save()
        logger.info("کاربر جدید ایجاد شد: %s (%s)", username, role.value)
        return user

    def create_initial_admin(self, username: str, password: str) -> User:
        if self.has_users():
            raise UserStoreError("کاربر اولیه قبلاً ایجاد شده است.")
        return self.add_user(username, password, Role.ADMIN)

    def delete_user(self, username: str) -> None:
        if username.lower() not in self._users:
            raise UserStoreError("کاربر یافت نشد.")
        del self._users[username.lower()]
        self._save()
        logger.info("کاربر حذف شد: %s", username)

    def set_active(self, username: str, active: bool) -> None:
        user = self.get(username)
        if user is None:
            raise UserStoreError("کاربر یافت نشد.")
        user.is_active = active
        self._save()
        logger.info("وضعیت کاربر %s به %s تغییر کرد", username, active)

    def set_password(self, username: str, password: str) -> None:
        user = self.get(username)
        if user is None:
            raise UserStoreError("کاربر یافت نشد.")
        if not password:
            raise UserStoreError("رمز عبور نمی‌تواند خالی باشد.")
        user.password_hash = hash_password(password)
        self._save()
        logger.info("رمز عبور کاربر %s تغییر کرد", username)
