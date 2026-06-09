from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from session import Session

ROLE_FA = {
    "ADMIN":                "مدیریت",
    "PHARMACIST":           "داروساز",
    "PHARMACY_TECHNICIAN":  "تکنسین دارویی",
    "TRAINEE":              "کارآموز",
    "OTC":                  "بدون نسخه",
    "PRESCRIPTION":         "نسخه‌پیچی",
    "COSMETICS":            "آرایشی بهداشتی",
    "CASHIER":              "صندوقدار",
    "WAREHOUSE":            "انباردار",
    "MEDICAL_EQUIPMENT":    "تجهیزات پزشکی",
}

# (label, icon, permission_or_None, admin_only)
NAV_ITEMS = [
    ("داشبورد",           "🏠", None,              False),
    ("داروها",            "💊", None,              False),
    ("فروش",              "💰", "create_sale",     False),
    ("خرید",              "🛒", "create_purchase", False),
    ("گزارش‌ها",          "📊", "view_reports",    False),
    ("مدیریت کاربران",    "👥", None,              True),
]

_BTN_NORMAL = """
QPushButton {
    text-align: right; padding: 0 18px;
    border: none; border-radius: 8px;
    font-size: 13px; color: #94a3b8; background: transparent;
}
QPushButton:hover { background: rgba(255,255,255,0.1); color: #e2e8f0; }
"""

_BTN_ACTIVE = """
QPushButton {
    text-align: right; padding: 0 18px;
    border: none; border-radius: 8px;
    font-size: 13px; color: #ffffff; background: #2563eb;
    font-weight: bold;
}
QPushButton:hover { background: #1d4ed8; color: white; }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سیستم مدیریت داروخانه")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._nav_btns: list[tuple[QPushButton, int, str]] = []
        self._build_ui()

    # ── Build ──────────────────────────────────────────
    def _build_ui(self):
        root_widget = QWidget()
        self.setCentralWidget(root_widget)

        root = QHBoxLayout(root_widget)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # content (left)
        content_wrap = QWidget()
        content_wrap.setStyleSheet("background: #f1f5f9;")
        cv = QVBoxLayout(content_wrap)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(0)
        cv.addWidget(self._make_topbar())

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: #f1f5f9;")
        cv.addWidget(self._stack)

        # sidebar راست — در RTL اول اضافه شده = سمت راست
        root.addWidget(self._make_sidebar())

        root.addWidget(content_wrap)

        self._load_pages()

    def _make_topbar(self):
        bar = QFrame()
        bar.setFixedHeight(56)
        bar.setStyleSheet(
            "QFrame { background: white; border-bottom: 1px solid #e2e8f0; }"
        )
        h = QHBoxLayout(bar)
        h.setContentsMargins(24, 0, 24, 0)

        self._page_title = QLabel("داشبورد")
        self._page_title.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #1e293b;"
        )
        h.addWidget(self._page_title)
        h.addStretch()

        user = Session.user() or {}
        role_fa = ROLE_FA.get(user.get("role", ""), user.get("role", ""))
        info = QLabel(f"{user.get('full_name', '')}  ·  {role_fa}")
        info.setStyleSheet("font-size: 12px; color: #64748b; padding-left: 12px;")
        h.addWidget(info)

        return bar

    def _make_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(215)
        sidebar.setStyleSheet("QFrame { background: #1e293b; border: none; }")

        v = QVBoxLayout(sidebar)
        v.setContentsMargins(10, 0, 10, 16)
        v.setSpacing(3)

        # Logo
        logo_area = QFrame()
        logo_area.setFixedHeight(70)
        la = QVBoxLayout(logo_area)
        la.setContentsMargins(6, 10, 6, 8)

        logo = QLabel("💊  داروخانه")
        logo.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: white;"
        )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        la.addWidget(logo)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #334155; max-height: 1px;")
        la.addWidget(sep)

        v.addWidget(logo_area)
        v.addSpacing(6)

        # Nav buttons
        user = Session.user() or {}
        role = user.get("role", "")
        perms = user.get("permissions", [])

        self._nav_btns.clear()
        first = None
        for label, icon, perm, admin_only in NAV_ITEMS:
            if admin_only and role != "ADMIN":
                continue
            if perm and perm not in perms:
                continue

            btn = QPushButton(f"{icon}  {label}")
            btn.setFixedHeight(46)
            btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            btn.setStyleSheet(_BTN_NORMAL)

            idx = len(self._nav_btns)
            self._nav_btns.append((btn, -1, label))  # page index set later
            btn.clicked.connect(
                lambda _checked, b=btn, lbl=label: self._nav_clicked(b, lbl)
            )
            v.addWidget(btn)
            if first is None:
                first = btn

        v.addStretch()

        # Logout
        logout = QPushButton("🚪  خروج از سیستم")
        logout.setFixedHeight(42)
        logout.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        logout.setStyleSheet("""
            QPushButton {
                text-align: right; padding: 0 18px;
                border: 1px solid #475569; border-radius: 8px;
                font-size: 12px; color: #94a3b8; background: transparent;
            }
            QPushButton:hover { background: #dc2626; color: white; border-color: #dc2626; }
        """)
        logout.clicked.connect(self._logout)
        v.addWidget(logout)

        if first:
            first.setStyleSheet(_BTN_ACTIVE)

        return sidebar

    def _load_pages(self):
        from windows.users_page import UsersPage

        user = Session.user() or {}
        role = user.get("role", "")
        perms = user.get("permissions", [])

        page_map: dict[str, int] = {}

        def _placeholder(text: str) -> QLabel:
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-size: 18px; color: #94a3b8;")
            return lbl

        idx = 0
        for label, _icon, perm, admin_only in NAV_ITEMS:
            if admin_only and role != "ADMIN":
                continue
            if perm and perm not in perms:
                continue

            if label == "داشبورد":
                from windows.dashboard_page import DashboardPage
                self._dashboard_page = DashboardPage()
                self._stack.addWidget(self._dashboard_page)
            elif label == "مدیریت کاربران":
                self._users_page = UsersPage()
                self._stack.addWidget(self._users_page)
            else:
                self._stack.addWidget(_placeholder(f"{label}  —  به زودی"))

            page_map[label] = idx
            idx += 1

        # update nav_btns with real page indices
        for i, (btn, _, lbl) in enumerate(self._nav_btns):
            real_idx = page_map.get(lbl, 0)
            self._nav_btns[i] = (btn, real_idx, lbl)

    # ── Nav ────────────────────────────────────────────
    def _nav_clicked(self, clicked_btn: QPushButton, label: str):
        for btn, page_idx, lbl in self._nav_btns:
            if btn is clicked_btn:
                btn.setStyleSheet(_BTN_ACTIVE)
                self._stack.setCurrentIndex(page_idx)
                self._page_title.setText(lbl)
            else:
                btn.setStyleSheet(_BTN_NORMAL)

    # ── Logout ─────────────────────────────────────────
    def _logout(self):
        reply = QMessageBox.question(
            self, "خروج",
            "آیا می‌خواهید از سیستم خارج شوید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            Session.clear()
            self.close()
