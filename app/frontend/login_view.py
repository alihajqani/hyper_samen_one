"""Login window — also handles first-run administrator creation."""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.backend.auth import AuthError, AuthService
from app.backend.user_store import UserStoreError
from app.frontend.i18n import fa
from app.frontend.widgets.common import PasswordEdit, logo_path, show_error, show_info

logger = logging.getLogger("hyper_samen.ui.login")


class LoginWindow(QWidget):
    logged_in = Signal(object)  # emits a Session

    def __init__(self, auth: AuthService):
        super().__init__()
        self._auth = auth
        self._setup_mode = auth.needs_initial_admin()
        self.setObjectName("root")
        self.setWindowTitle(fa.APP_TITLE)
        self.setMinimumWidth(420)
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 18, 40, 40)
        outer.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(360)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(28, 22, 28, 24)
        lay.setSpacing(12)

        # Brand name first, so "هایپرمارکت ثامن" sits at the very top of the card.
        brand = QLabel(fa.APP_SHORT)
        brand.setObjectName("title")
        brand.setAlignment(Qt.AlignCenter)
        lay.addWidget(brand)

        # logo
        if logo_path().exists():
            logo = QLabel()
            pix = QPixmap(str(logo_path())).scaledToWidth(96, Qt.SmoothTransformation)
            logo.setPixmap(pix)
            logo.setAlignment(Qt.AlignCenter)
            lay.addWidget(logo)

        title = QLabel(fa.SETUP_ADMIN_TITLE if self._setup_mode else fa.LOGIN_TITLE)
        title.setObjectName("subtitle")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        if self._setup_mode:
            hint = QLabel(fa.SETUP_ADMIN_HINT)
            hint.setObjectName("subtitle")
            hint.setAlignment(Qt.AlignCenter)
            hint.setWordWrap(True)
            lay.addWidget(hint)

        self.username = QLineEdit()
        self.username.setPlaceholderText(fa.LBL_USERNAME)
        lay.addWidget(self.username)

        self.password = PasswordEdit(placeholder=fa.LBL_PASSWORD)
        lay.addWidget(self.password)

        self.password2 = PasswordEdit(placeholder=fa.LBL_PASSWORD_CONFIRM)
        self.password2.setVisible(self._setup_mode)
        lay.addWidget(self.password2)

        # Recovery (master) code — only collected when creating the initial admin.
        self.recovery = PasswordEdit(placeholder=fa.LBL_RECOVERY_CODE_SETUP)
        self.recovery.setVisible(self._setup_mode)
        lay.addWidget(self.recovery)
        if self._setup_mode:
            rec_hint = QLabel(fa.SETUP_RECOVERY_HINT)
            rec_hint.setObjectName("subtitle")
            rec_hint.setWordWrap(True)
            lay.addWidget(rec_hint)

        self.submit = QPushButton(fa.BTN_CREATE if self._setup_mode else fa.BTN_LOGIN)
        self.submit.clicked.connect(self._on_submit)
        lay.addWidget(self.submit)

        # Forgot-password link — only when a recovery code has been configured.
        if not self._setup_mode and self._auth.store.has_recovery_code():
            self.forgot = QPushButton(fa.LINK_FORGOT_PASSWORD)
            self.forgot.setFlat(True)
            self.forgot.setCursor(Qt.PointingHandCursor)
            self.forgot.setStyleSheet(
                "QPushButton { background: transparent; border: none; color: #1565c0; }"
                "QPushButton:hover { text-decoration: underline; }"
            )
            self.forgot.clicked.connect(self._on_forgot)
            lay.addWidget(self.forgot)

        # Enter submits.
        self.username.returnPressed.connect(self._on_submit)
        self.password.returnPressed.connect(self._on_submit)
        self.password2.returnPressed.connect(self._on_submit)
        self.recovery.returnPressed.connect(self._on_submit)

        outer.addWidget(card)

    def _on_submit(self) -> None:
        username = self.username.text().strip()
        password = self.password.text()
        if not username or not password:
            show_error(self, fa.MSG_FILL_ALL_FIELDS)
            return
        try:
            if self._setup_mode:
                if password != self.password2.text():
                    show_error(self, fa.MSG_PASSWORD_MISMATCH)
                    return
                session = self._auth.create_initial_admin(
                    username, password, self.recovery.text() or None
                )
            else:
                session = self._auth.login(username, password)
        except (AuthError, UserStoreError) as exc:
            show_error(self, str(exc))
            return
        self.logged_in.emit(session)

    def _on_forgot(self) -> None:
        from app.frontend.forgot_password_dialog import ForgotPasswordDialog

        dlg = ForgotPasswordDialog(self._auth, self)
        if dlg.exec():
            show_info(self, fa.MSG_RECOVERY_SUCCESS.format(username=dlg.admin_username))
