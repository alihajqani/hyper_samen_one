"""User management view (administrator only)."""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.backend.models import Role
from app.backend.user_store import UserStore, UserStoreError
from app.frontend.i18n import fa
from app.frontend.utils_fa import to_persian_digits
from app.frontend.widgets.common import confirm, show_error, show_info

logger = logging.getLogger("hyper_samen.ui.users")


class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(fa.TITLE_ADD_USER)
        self.setMinimumWidth(360)
        form = QFormLayout()
        self.username = QLineEdit()
        self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.Password)
        self.password2 = QLineEdit(); self.password2.setEchoMode(QLineEdit.Password)
        self.role = QComboBox()
        for r in Role.assignable_by_admin():
            self.role.addItem(r.fa, r)
        form.addRow(fa.LBL_USERNAME, self.username)
        form.addRow(fa.LBL_PASSWORD, self.password)
        form.addRow(fa.LBL_PASSWORD_CONFIRM, self.password2)
        form.addRow(fa.LBL_ROLE, self.role)

        buttons = QDialogButtonBox()
        ok = buttons.addButton(fa.BTN_CREATE, QDialogButtonBox.AcceptRole)
        buttons.addButton(fa.BTN_CANCEL, QDialogButtonBox.RejectRole)
        ok.clicked.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        lay = QVBoxLayout(self); lay.addLayout(form); lay.addWidget(buttons)

    def _on_accept(self) -> None:
        if not self.username.text().strip() or not self.password.text():
            show_error(self, fa.MSG_FILL_ALL_FIELDS); return
        if self.password.text() != self.password2.text():
            show_error(self, fa.MSG_PASSWORD_MISMATCH); return
        self.accept()

    def values(self):
        return self.username.text().strip(), self.password.text(), self.role.currentData()


class PasswordDialog(QDialog):
    def __init__(self, parent=None, username: str = ""):
        super().__init__(parent)
        self.setWindowTitle(fa.TITLE_RESET_PASSWORD.format(username=username))
        self.setMinimumWidth(340)
        form = QFormLayout()
        self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.Password)
        self.password2 = QLineEdit(); self.password2.setEchoMode(QLineEdit.Password)
        form.addRow(fa.LBL_PASSWORD, self.password)
        form.addRow(fa.LBL_PASSWORD_CONFIRM, self.password2)
        buttons = QDialogButtonBox()
        ok = buttons.addButton(fa.BTN_SAVE, QDialogButtonBox.AcceptRole)
        buttons.addButton(fa.BTN_CANCEL, QDialogButtonBox.RejectRole)
        ok.clicked.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        lay = QVBoxLayout(self); lay.addLayout(form); lay.addWidget(buttons)

    def _on_accept(self) -> None:
        if not self.password.text():
            show_error(self, fa.MSG_FILL_ALL_FIELDS); return
        if self.password.text() != self.password2.text():
            show_error(self, fa.MSG_PASSWORD_MISMATCH); return
        self.accept()

    def value(self) -> str:
        return self.password.text()


class UsersView(QWidget):
    _COLUMNS = [fa.LBL_USERNAME, fa.LBL_ROLE, fa.COL_USER_STATUS, fa.COL_CREATED_AT]

    def __init__(self, store: UserStore, current_username: str):
        super().__init__()
        self._store = store
        self._current = current_username
        self._build()
        self.reload()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        top = QHBoxLayout()
        title = QLabel(fa.NAV_USERS); title.setObjectName("title")
        top.addWidget(title); top.addStretch(1)
        self._add_btn = QPushButton(fa.TITLE_ADD_USER); self._add_btn.clicked.connect(self._on_add)
        self._pw_btn = QPushButton(fa.BTN_RESET_PASSWORD); self._pw_btn.setObjectName("ghost")
        self._pw_btn.clicked.connect(self._on_reset_pw)
        self._toggle_btn = QPushButton(fa.BTN_TOGGLE_ACTIVE); self._toggle_btn.setObjectName("ghost")
        self._toggle_btn.clicked.connect(self._on_toggle)
        self._del_btn = QPushButton(fa.BTN_DELETE); self._del_btn.setObjectName("danger")
        self._del_btn.clicked.connect(self._on_delete)
        for b in (self._add_btn, self._pw_btn, self._toggle_btn, self._del_btn):
            top.addWidget(b)
        lay.addLayout(top)

        self._table = QTableWidget(0, len(self._COLUMNS))
        self._table.setHorizontalHeaderLabels(self._COLUMNS)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setSelectionMode(QTableWidget.SingleSelection)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lay.addWidget(self._table, 1)

    def reload(self) -> None:
        users = self._store.list_users()
        self._table.setRowCount(len(users))
        for r, u in enumerate(users):
            status = fa.STATUS_ACTIVE if u.is_active else fa.STATUS_INACTIVE
            cells = [u.username, u.role.fa, status, to_persian_digits(u.created_at)]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                if c == 0:
                    item.setData(Qt.UserRole, u.username)
                self._table.setItem(r, c, item)

    def _selected_username(self) -> str | None:
        row = self._table.currentRow()
        if row < 0:
            return None
        item = self._table.item(row, 0)
        return item.data(Qt.UserRole) if item else None

    def _guard_self(self, username: str) -> bool:
        """Block destructive actions on the currently logged-in admin."""
        if username == self._current:
            show_error(self, fa.ERR_NO_PERMISSION)
            return True
        return False

    def _on_add(self) -> None:
        dlg = AddUserDialog(self)
        if not dlg.exec():
            return
        username, password, role = dlg.values()
        try:
            self._store.add_user(username, password, role)
        except UserStoreError as exc:
            show_error(self, str(exc)); return
        self.reload(); show_info(self, fa.MSG_CREATED)

    def _on_reset_pw(self) -> None:
        username = self._selected_username()
        if not username:
            return
        dlg = PasswordDialog(self, username)
        if not dlg.exec():
            return
        try:
            self._store.set_password(username, dlg.value())
        except UserStoreError as exc:
            show_error(self, str(exc)); return
        show_info(self, fa.MSG_SAVED)

    def _on_toggle(self) -> None:
        username = self._selected_username()
        if not username or self._guard_self(username):
            return
        user = self._store.get(username)
        try:
            self._store.set_active(username, not user.is_active)
        except UserStoreError as exc:
            show_error(self, str(exc)); return
        self.reload()

    def _on_delete(self) -> None:
        username = self._selected_username()
        if not username or self._guard_self(username):
            return
        if not confirm(self, fa.CONFIRM_DELETE_USER.format(username=username)):
            return
        try:
            self._store.delete_user(username)
        except UserStoreError as exc:
            show_error(self, str(exc)); return
        self.reload(); show_info(self, fa.MSG_DELETED)
