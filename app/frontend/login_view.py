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
from app.frontend.widgets.common import logo_path, show_error

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
        outer.setContentsMargins(40, 30, 40, 40)
        outer.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(360)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(28, 28, 28, 28)
        lay.setSpacing(12)

        # logo
        if logo_path().exists():
            logo = QLabel()
            pix = QPixmap(str(logo_path())).scaledToWidth(96, Qt.SmoothTransformation)
            logo.setPixmap(pix)
            logo.setAlignment(Qt.AlignCenter)
            lay.addWidget(logo)

        title = QLabel(fa.SETUP_ADMIN_TITLE if self._setup_mode else fa.LOGIN_TITLE)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        subtitle = QLabel(fa.SETUP_ADMIN_HINT if self._setup_mode else fa.APP_SHORT)
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        lay.addWidget(subtitle)

        self.username = QLineEdit()
        self.username.setPlaceholderText(fa.LBL_USERNAME)
        lay.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setPlaceholderText(fa.LBL_PASSWORD)
        self.password.setEchoMode(QLineEdit.Password)
        lay.addWidget(self.password)

        self.password2 = QLineEdit()
        self.password2.setPlaceholderText(fa.LBL_PASSWORD_CONFIRM)
        self.password2.setEchoMode(QLineEdit.Password)
        self.password2.setVisible(self._setup_mode)
        lay.addWidget(self.password2)

        self.submit = QPushButton(fa.BTN_CREATE if self._setup_mode else fa.BTN_LOGIN)
        self.submit.clicked.connect(self._on_submit)
        lay.addWidget(self.submit)

        # Enter submits.
        self.username.returnPressed.connect(self._on_submit)
        self.password.returnPressed.connect(self._on_submit)
        self.password2.returnPressed.connect(self._on_submit)

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
                session = self._auth.create_initial_admin(username, password)
            else:
                session = self._auth.login(username, password)
        except (AuthError, UserStoreError) as exc:
            show_error(self, str(exc))
            return
        self.logged_in.emit(session)
