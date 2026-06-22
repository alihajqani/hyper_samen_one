"""Authentication and session management.

Wraps :class:`~app.backend.user_store.UserStore` to authenticate users and hold
the current in-memory session (user + role). The session determines which Excel
passwords are supplied to the data layer and which UI is shown.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.backend.models import Role, User
from app.backend.user_store import UserStore, verify_password

logger = logging.getLogger("hyper_samen.auth")


@dataclass
class Session:
    """The currently logged-in user."""

    user: User

    @property
    def role(self) -> Role:
        return self.user.role

    @property
    def can_write(self) -> bool:
        return self.role.can_write

    @property
    def can_manage_users(self) -> bool:
        return self.role.can_manage_users


class AuthError(Exception):
    """Raised on a failed/blocked login."""


class AuthService:
    """Login + first-run admin bootstrap on top of a UserStore."""

    def __init__(self, store: UserStore):
        self._store = store

    def needs_initial_admin(self) -> bool:
        return not self._store.has_users()

    def create_initial_admin(
        self, username: str, password: str, recovery_code: str | None = None
    ) -> Session:
        user = self._store.create_initial_admin(username, password, recovery_code)
        logger.info("Initial admin created: %s", username)
        return Session(user=user)

    def login(self, username: str, password: str) -> Session:
        user = self._store.get(username)
        if user is None or not verify_password(password, user.password_hash):
            logger.warning("Failed login for username: %s", username)
            raise AuthError("نام کاربری یا رمز عبور نادرست است")
        if not user.is_active:
            logger.warning("Disabled user login attempt: %s", username)
            raise AuthError("این کاربر غیرفعال است")
        logger.info("Successful login: %s (%s)", username, user.role.value)
        return Session(user=user)

    @property
    def store(self) -> UserStore:
        return self._store
