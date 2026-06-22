"""Forgot-password recovery: master-key gated reset of the main admin's password.

The recovery (master) code is never stored in clear text — only its bcrypt hash
lives inside the Fernet-encrypted ``users.dat``. Entering the correct code lets the
user set a new password for the primary administrator account (policy-enforced).
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
)

from app.backend.auth import AuthService
from app.backend.user_store import UserStoreError
from app.frontend.i18n import fa
from app.frontend.widgets.common import PasswordEdit, show_error

logger = logging.getLogger("hyper_samen.ui.forgot")


class ForgotPasswordDialog(QDialog):
    """Single screen: recovery code + new admin password."""

    def __init__(self, auth: AuthService, parent=None):
        super().__init__(parent)
        self._auth = auth
        self._admin_username = ""
        self.setWindowTitle(fa.TITLE_FORGOT_PASSWORD)
        self.setMinimumWidth(380)
        self._build()

    @property
    def admin_username(self) -> str:
        return self._admin_username

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setSpacing(12)

        hint = QLabel(fa.FORGOT_PASSWORD_HINT)
        hint.setObjectName("subtitle")
        hint.setWordWrap(True)
        lay.addWidget(hint)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        self.code = PasswordEdit(placeholder=fa.LBL_RECOVERY_CODE)
        self.password = PasswordEdit(placeholder=fa.LBL_NEW_PASSWORD)
        self.password2 = PasswordEdit(placeholder=fa.LBL_PASSWORD_CONFIRM)
        form.addRow(fa.LBL_RECOVERY_CODE, self.code)
        form.addRow(fa.LBL_NEW_PASSWORD, self.password)
        form.addRow(fa.LBL_PASSWORD_CONFIRM, self.password2)
        lay.addLayout(form)

        buttons = QDialogButtonBox()
        ok = buttons.addButton(fa.BTN_SAVE, QDialogButtonBox.AcceptRole)
        buttons.addButton(fa.BTN_CANCEL, QDialogButtonBox.RejectRole)
        ok.clicked.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        lay.addWidget(buttons)

    def _on_accept(self) -> None:
        store = self._auth.store
        code = self.code.text()
        if not code or not self.password.text():
            show_error(self, fa.MSG_FILL_ALL_FIELDS)
            return
        if not store.verify_recovery_code(code):
            logger.warning("Forgot-password: wrong recovery code entered")
            show_error(self, fa.ERR_RECOVERY_CODE_WRONG)
            return
        if self.password.text() != self.password2.text():
            show_error(self, fa.MSG_PASSWORD_MISMATCH)
            return
        try:
            self._admin_username = store.reset_admin_password(self.password.text())
        except UserStoreError as exc:
            show_error(self, str(exc))
            return
        self.accept()
