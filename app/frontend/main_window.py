"""Main application window: role-aware shell with sidebar navigation."""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.__version__ import __version__
from app.backend.auth import Session
from app.backend.excel_service import ExcelError, create_excel_service
from app.backend.inventory_repo import InventoryRepo
from app.frontend.i18n import fa
from app.frontend.utils_fa import to_persian_digits
from app.frontend.widgets.common import logo_path, show_error

logger = logging.getLogger("hyper_samen.ui.main")


def _placeholder(text: str = fa.PLACEHOLDER_COMING_SOON) -> QWidget:
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setAlignment(Qt.AlignCenter)
    label = QLabel(text)
    label.setObjectName("subtitle")
    lay.addWidget(label)
    return w


class MainWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self, config, auth, session: Session):
        super().__init__()
        self._config = config
        self._auth = auth
        self._session = session
        self._repo: InventoryRepo | None = None
        self._pages: dict[str, QWidget] = {}

        self.setWindowTitle(fa.APP_TITLE)
        self.resize(1040, 680)
        self._load_inventory()
        self._build()

    # -- data -----------------------------------------------------------------

    def _load_inventory(self) -> None:
        try:
            excel = create_excel_service(self._config, writable=self._session.can_write)
            self._repo = InventoryRepo(excel)
            self._repo.load()
        except ExcelError as exc:
            self._repo = None
            logger.error("Failed to load inventory: %s", exc)
            show_error(self, str(exc))

    @property
    def repo(self) -> InventoryRepo | None:
        return self._repo

    # -- layout ---------------------------------------------------------------

    def _build(self) -> None:
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(12, 12, 12, 12)
        body.setSpacing(12)
        self._nav = QListWidget()
        self._nav.setObjectName("nav")
        self._nav.setFixedWidth(200)
        self._stack = QStackedWidget()
        body.addWidget(self._nav)
        body.addWidget(self._stack, 1)
        outer.addLayout(body, 1)

        self._build_pages()
        self._nav.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._nav.setCurrentRow(0)

    def _build_header(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet("QFrame { background: #0d47a1; }")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 10, 16, 10)

        if logo_path().exists():
            logo = QLabel()
            logo.setPixmap(QPixmap(str(logo_path())).scaledToHeight(40, Qt.SmoothTransformation))
            lay.addWidget(logo)

        title = QLabel(fa.APP_SHORT)
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        lay.addWidget(title)

        lay.addStretch(1)

        self._badge = QLabel()
        self._badge.setObjectName("badge")
        self._refresh_badge()
        lay.addWidget(self._badge)

        user = QLabel(f"{self._session.user.username} — {self._session.role.fa}")
        user.setStyleSheet("color: #e3f2fd; margin: 0 12px;")
        lay.addWidget(user)

        logout = QPushButton(fa.BTN_LOGOUT)
        logout.setObjectName("ghost")
        logout.setStyleSheet(
            "QPushButton#ghost { color: white; border-color: white; }"
            "QPushButton#ghost:hover { background: #1565c0; }"
        )
        logout.clicked.connect(self.logout_requested.emit)
        lay.addWidget(logout)
        return bar

    def _refresh_badge(self) -> None:
        count = len(self._repo.low_stock()) if self._repo else 0
        self._badge.setText(fa.LBL_LOW_STOCK_BADGE.format(count=to_persian_digits(count)))
        self._badge.setVisible(count > 0)

    def _build_pages(self) -> None:
        self._add_page("home", fa.NAV_HOME, self._make_home_page())
        self._add_page("inventory", fa.NAV_INVENTORY, self._make_inventory_page())
        self._add_page("reports", fa.NAV_REPORTS, self._make_reports_page())
        if self._session.can_manage_users:
            self._add_page("users", fa.NAV_USERS, self._make_users_page())

    def _add_page(self, key: str, label: str, widget: QWidget) -> None:
        self._pages[key] = widget
        self._stack.addWidget(widget)
        QListWidgetItem(label, self._nav)

    # -- pages (real views are wired in later versions) -----------------------

    def _make_home_page(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(14)
        lay.setAlignment(Qt.AlignTop)

        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(24, 24, 24, 24)
        cl.setSpacing(10)

        hello = QLabel(f"{fa.MSG_WELCOME}، {self._session.user.username}")
        hello.setObjectName("title")
        cl.addWidget(hello)

        role = QLabel(f"{fa.LBL_ROLE}: {self._session.role.fa}")
        role.setObjectName("subtitle")
        cl.addWidget(role)

        total = len(self._repo.products) if self._repo else 0
        low = len(self._repo.low_stock()) if self._repo else 0
        cl.addWidget(QLabel(fa.LBL_TOTAL_ITEMS.format(count=to_persian_digits(total))))
        cl.addWidget(QLabel(fa.LBL_LOW_STOCK_BADGE.format(count=to_persian_digits(low))))

        version = QLabel(fa.LBL_VERSION.format(version=to_persian_digits(__version__)))
        version.setObjectName("subtitle")
        cl.addWidget(version)

        lay.addWidget(card)
        return page

    def _make_inventory_page(self) -> QWidget:
        if self._repo is None:
            return _placeholder()
        from app.frontend.inventory_view import InventoryView

        self._inventory_view = InventoryView(self._repo, on_changed=self._refresh_badge)
        return self._inventory_view

    def _make_reports_page(self) -> QWidget:
        if self._repo is None:
            return _placeholder()
        from app.frontend.reports_view import ReportsView

        self._reports_view = ReportsView(self._repo)
        return self._reports_view

    def _make_users_page(self) -> QWidget:
        from app.frontend.users_view import UsersView

        self._users_view = UsersView(self._auth.store, self._session.user.username)
        return self._users_view
