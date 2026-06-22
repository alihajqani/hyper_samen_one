"""Admin-only log viewer, locked behind the admin's password.

Lists the Jalali-named ``*.log`` files next to the executable and shows the
selected file read-only. Access is gated: the admin must enter their password
(verified against their bcrypt hash) before the contents are revealed.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.backend.auth import Session
from app.backend.logging_setup import list_log_files
from app.backend.user_store import verify_password
from app.frontend.i18n import fa
from app.frontend.widgets.common import prompt_password, show_error

logger = logging.getLogger("hyper_samen.ui.logs")

_MAX_LINES = 5000


class LogsView(QWidget):
    def __init__(self, log_dir: Path, session: Session):
        super().__init__()
        self._log_dir = Path(log_dir)
        self._session = session
        self._unlocked = False
        self._build()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        title = QLabel(fa.TITLE_LOGS)
        title.setObjectName("title")
        lay.addWidget(title)

        # Locked panel
        self._locked = QWidget()
        ll = QVBoxLayout(self._locked)
        ll.setContentsMargins(0, 8, 0, 0)
        hint = QLabel(fa.LOGS_UNLOCK_HINT)
        hint.setObjectName("subtitle")
        hint.setWordWrap(True)
        ll.addWidget(hint)
        unlock = QPushButton(fa.BTN_UNLOCK_LOGS)
        unlock.clicked.connect(self._on_unlock)
        ll.addWidget(unlock)
        ll.addStretch(1)
        lay.addWidget(self._locked, 1)

        # Unlocked content panel
        self._content = QWidget()
        cl = QVBoxLayout(self._content)
        cl.setContentsMargins(0, 0, 0, 0)
        top = QHBoxLayout()
        top.addWidget(QLabel(fa.LBL_LOG_FILE))
        self._combo = QComboBox()
        self._combo.currentIndexChanged.connect(self._on_select)
        top.addWidget(self._combo, 1)
        self._refresh_btn = QPushButton(fa.BTN_REFRESH)
        self._refresh_btn.setObjectName("ghost")
        self._refresh_btn.clicked.connect(self._populate)
        top.addWidget(self._refresh_btn)
        cl.addLayout(top)
        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setLineWrapMode(QPlainTextEdit.NoWrap)
        cl.addWidget(self._text, 1)
        self._content.setVisible(False)
        lay.addWidget(self._content, 1)

    def _on_unlock(self) -> None:
        password = prompt_password(self, fa.TITLE_LOGS, fa.LOGS_UNLOCK_HINT)
        if password is None:
            return
        if not password or not verify_password(password, self._session.user.password_hash):
            show_error(self, fa.ERR_WRONG_PASSWORD)
            return
        self._unlocked = True
        self._locked.setVisible(False)
        self._content.setVisible(True)
        logger.info("Logs unlocked by %s", self._session.user.username)
        self._populate()

    def _populate(self) -> None:
        files = list_log_files(self._log_dir)
        self._combo.blockSignals(True)
        self._combo.clear()
        for p in files:
            self._combo.addItem(p.name, str(p))
        self._combo.blockSignals(False)
        if files:
            self._combo.setCurrentIndex(0)
            self._on_select()
        else:
            self._text.setPlainText(fa.LOGS_EMPTY)

    def _on_select(self) -> None:
        path = self._combo.currentData()
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except OSError as exc:
            self._text.setPlainText(fa.ERR_GENERIC.format(detail=exc))
            return
        if len(lines) > _MAX_LINES:
            lines = lines[-_MAX_LINES:]
        self._text.setPlainText("".join(lines))
        self._text.moveCursor(QTextCursor.End)
