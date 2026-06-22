"""Qt application bootstrap: RTL layout, Persian font, theme, and the controller
that drives the login → main-window flow.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication

from app.__version__ import __version__
from app.backend.auth import AuthService
from app.backend.user_store import UserStore, UserStoreError
from app.frontend.i18n import fa
from app.frontend.widgets.common import font_path, logo_path, show_error

logger = logging.getLogger("hyper_samen.ui")

# Brand palette (Hyper Market Samen).
PRIMARY = "#1565c0"
PRIMARY_DARK = "#0d47a1"
ACCENT = "#e53935"
BG = "#f4f6f9"
CARD = "#ffffff"
TEXT = "#1f2933"

STYLESHEET = f"""
* {{ font-size: 14px; color: {TEXT}; }}
QMainWindow, QDialog, QWidget#root {{ background: {BG}; }}
QLabel#title {{ font-size: 20px; font-weight: bold; color: {PRIMARY_DARK}; }}
QLabel#subtitle {{ color: #607d8b; }}
QFrame#card {{ background: {CARD}; border: 1px solid #e0e6ed; border-radius: 12px; }}
QPushButton {{
    background: {PRIMARY}; color: white; border: none; border-radius: 8px;
    padding: 8px 18px; font-weight: bold;
}}
QPushButton:hover {{ background: {PRIMARY_DARK}; }}
QPushButton:disabled {{ background: #b0bec5; color: #eceff1; }}
QPushButton#ghost {{ background: transparent; color: {PRIMARY}; border: 1px solid {PRIMARY}; }}
QPushButton#ghost:hover {{ background: #e3f2fd; }}
QPushButton#danger {{ background: {ACCENT}; }}
QPushButton#danger:hover {{ background: #c62828; }}
QLineEdit, QComboBox, QSpinBox {{
    background: white; border: 1px solid #cfd8dc; border-radius: 8px; padding: 7px 10px;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{ border: 1px solid {PRIMARY}; }}
QListWidget#nav {{ background: {PRIMARY_DARK}; border: none; outline: none; }}
QListWidget#nav::item {{ color: #e3f2fd; padding: 12px 16px; border-radius: 8px; margin: 4px; }}
QListWidget#nav::item:selected {{ background: {PRIMARY}; color: white; }}
QListWidget#nav::item:hover {{ background: {PRIMARY}; }}
QTableView {{
    background: {CARD}; gridline-color: #eceff1; border: 1px solid #e0e6ed;
    border-radius: 10px; selection-background-color: #bbdefb; selection-color: {TEXT};
}}
QHeaderView::section {{
    background: {PRIMARY_DARK}; color: white; padding: 8px; border: none; font-weight: bold;
}}
QLabel#badge {{
    background: {ACCENT}; color: white; border-radius: 10px; padding: 3px 12px; font-weight: bold;
}}
"""


def _apply_font(app: QApplication) -> None:
    fp = font_path()
    family = None
    if fp.exists():
        fid = QFontDatabase.addApplicationFont(str(fp))
        fams = QFontDatabase.applicationFontFamilies(fid)
        if fams:
            family = fams[0]
    if family:
        font = app.font()
        font.setFamily(family)
        app.setFont(font)
    else:
        logger.info("Bundled Persian font not found; using the system default font.")


class AppController(QObject):
    """Owns the auth service and switches between login and main window."""

    def __init__(self, config, auth: AuthService):
        super().__init__()
        self._config = config
        self._auth = auth
        self._login = None
        self._main = None

    def start(self) -> None:
        self._show_login()

    def _show_login(self) -> None:
        from app.frontend.login_view import LoginWindow

        self._login = LoginWindow(self._auth)
        self._login.logged_in.connect(self._on_logged_in)
        self._login.show()

    def _on_logged_in(self, session) -> None:
        # Defer to the next event-loop tick so Qt finishes processing the
        # login button's clicked signal before we close the login window.
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._open_main(session))

    def _open_main(self, session) -> None:
        from app.frontend.main_window import MainWindow

        if self._login is not None:
            self._login.close()
            self._login = None
        self._main = MainWindow(self._config, self._auth, session)
        self._main.logout_requested.connect(self._on_logout)
        self._main.show()

    def _on_logout(self) -> None:
        # Same deferral: the logout button signal must finish before we close
        # the main window that hosts the button.
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self._close_main)

    def _close_main(self) -> None:
        if self._main is not None:
            self._main.close()
            self._main = None
        self._show_login()


def build_application(argv: list[str] | None = None) -> QApplication:
    app = QApplication.instance() or QApplication(argv or [])
    app.setApplicationName(fa.APP_TITLE)
    app.setApplicationVersion(__version__)
    app.setLayoutDirection(Qt.RightToLeft)
    if logo_path().exists():
        app.setWindowIcon(QIcon(str(logo_path())))
    _apply_font(app)
    app.setStyleSheet(STYLESHEET)
    return app


def run_app(config, app_logger: logging.Logger) -> int:
    """Build and run the GUI. Returns the process exit code."""
    app = build_application([])

    try:
        store = UserStore(config.user_store_file, config.user_store_key)
    except UserStoreError as exc:
        show_error(None, str(exc))
        app_logger.error("Failed to initialize the user store: %s", exc)
        return 1

    auth = AuthService(store)
    controller = AppController(config, auth)
    controller.start()
    app_logger.info("GUI started")
    return app.exec()
