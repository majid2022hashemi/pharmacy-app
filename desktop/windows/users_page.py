from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QDialog, QLineEdit, QComboBox, QMessageBox, QFormLayout,
    QCheckBox, QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

import requests
from api.users_api import get_users, create_user, update_user, update_permissions, deactivate_user, activate_user, admin_reset_password
from windows.login_window import _make_password_row
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

DEPT_FA = {
    "PHARMACEUTICAL":    "دارویی",
    "COSMETICS":         "آرایشی بهداشتی",
    "MEDICAL_EQUIPMENT": "تجهیزات پزشکی",
    "OTC":               "بدون نسخه",
    "ORTHOPEDICS":       "ارتوپدی",
    "SUPPLEMENTS":       "مکمل ورزشی",
    "BABY_PRODUCTS":     "محصولات کودک",
}

PAGE_STYLE = """
QWidget { font-family: Tahoma, Arial; }
QTableWidget {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f1f5f9;
    font-size: 13px;
}
QTableWidget::item { padding: 6px 12px; }
QTableWidget::item:selected { background: #eff6ff; color: #1e293b; }
QHeaderView::section {
    background: #f8fafc;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: bold;
    color: #64748b;
}
QPushButton#add-btn {
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    padding: 0 20px;
    height: 36px;
}
QPushButton#add-btn:hover { background: #1d4ed8; }
QPushButton#action-btn {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    font-size: 12px;
    color: #475569;
    padding: 3px 10px;
}
QPushButton#action-btn:hover { background: #e2e8f0; }
QPushButton#danger-btn {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 5px;
    font-size: 12px;
    color: #dc2626;
    padding: 3px 10px;
}
QPushButton#danger-btn:hover { background: #fee2e2; }
QPushButton#ok-btn {
    background: #16a34a;
    border: 1px solid #16a34a;
    border-radius: 5px;
    font-size: 12px;
    color: white;
    padding: 3px 10px;
}
QPushButton#ok-btn:hover { background: #15803d; }
"""

DIALOG_STYLE = """
QDialog { background: #f8fafc; }
QLabel { font-size: 12px; color: #374151; }
QLineEdit, QComboBox {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    background: white;
    color: #111827;
    min-height: 32px;
}
QLineEdit:focus, QComboBox:focus { border-color: #2563eb; }
QComboBox QAbstractItemView {
    background: white;
    color: #111827;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    selection-background-color: #2563eb;
    selection-color: white;
    outline: none;
    padding: 4px;
}
QComboBox QAbstractItemView::item {
    padding: 6px 12px;
    min-height: 28px;
    color: #111827;
    background: transparent;
}
QComboBox QAbstractItemView::item:hover {
    background: #eff6ff;
    color: #1e293b;
}
QComboBox QAbstractItemView::item:selected {
    background: #2563eb;
    color: white;
}
QPushButton#save-btn {
    background: #2563eb; color: white;
    border: none; border-radius: 6px;
    font-size: 13px; font-weight: bold;
    padding: 8px 24px;
}
QPushButton#save-btn:hover { background: #1d4ed8; }
QPushButton#cancel-btn {
    background: white; color: #6b7280;
    border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 13px; padding: 8px 20px;
}
QPushButton#cancel-btn:hover { background: #f9fafb; }
QLabel#error { color: #dc2626; font-size: 11px; }
"""


# ── Create User Dialog ─────────────────────────────────────
class CreateUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("کاربر جدید")
        self.setFixedWidth(400)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(DIALOG_STYLE)
        self._build_ui()

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(14)

        title = QLabel("ایجاد کاربر جدید")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #1e293b;")
        v.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.inp_fullname = QLineEdit()
        self.inp_fullname.setPlaceholderText("نام و نام خانوادگی")
        form.addRow("نام کامل *", self.inp_fullname)

        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("نام کاربری (انگلیسی)")
        form.addRow("نام کاربری *", self.inp_username)

        pass_box, self.inp_password = _make_password_row("حداقل ۶ کاراکتر")
        form.addRow("رمز عبور *", pass_box)

        self.inp_national = QLineEdit()
        self.inp_national.setPlaceholderText("۱۰ رقم")
        form.addRow("کد ملی", self.inp_national)

        self.inp_birth = QLineEdit()
        self.inp_birth.setPlaceholderText("مثال: ۱۳۷۰/۰۵/۱۲")
        form.addRow("تاریخ تولد", self.inp_birth)

        self.inp_phone = QLineEdit()
        self.inp_phone.setPlaceholderText("مثال: ۰۹۱۲۱۲۳۴۵۶۷")
        form.addRow("موبایل / تلفن", self.inp_phone)

        self.inp_address = QLineEdit()
        self.inp_address.setPlaceholderText("آدرس کامل")
        form.addRow("آدرس", self.inp_address)

        self.cmb_role = QComboBox()
        for key, val in ROLE_FA.items():
            self.cmb_role.addItem(val, key)
        form.addRow("نقش *", self.cmb_role)

        self.cmb_dept = QComboBox()
        self.cmb_dept.addItem("— انتخاب نشده —", None)
        for key, val in DEPT_FA.items():
            self.cmb_dept.addItem(val, key)
        form.addRow("بخش", self.cmb_dept)

        v.addLayout(form)

        self._error = QLabel("")
        self._error.setObjectName("error")
        v.addWidget(self._error)

        btns = QHBoxLayout()
        btns.setSpacing(8)
        save = QPushButton("ذخیره")
        save.setObjectName("save-btn")
        save.clicked.connect(self._save)
        cancel = QPushButton("انصراف")
        cancel.setObjectName("cancel-btn")
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(save)
        v.addLayout(btns)

    def _save(self):
        fullname = self.inp_fullname.text().strip()
        username = self.inp_username.text().strip()
        password = self.inp_password.text()
        national = self.inp_national.text().strip()
        birth = self.inp_birth.text().strip()
        phone = self.inp_phone.text().strip()
        address = self.inp_address.text().strip()
        role = self.cmb_role.currentData()
        dept = self.cmb_dept.currentData()

        if not fullname or not username or not password:
            self._error.setText("نام کامل، نام کاربری و رمز عبور الزامی است")
            return
        if len(password) < 6:
            self._error.setText("رمز عبور باید حداقل ۶ کاراکتر باشد")
            return
        if national and (not national.isdigit() or len(national) != 10):
            self._error.setText("کد ملی باید ۱۰ رقم باشد")
            return

        from windows.login_window import _normalize_jalali
        birth_normalized = _normalize_jalali(birth) if birth else None

        try:
            create_user({
                "username": username,
                "password": password,
                "full_name": fullname,
                "role": role,
                "department": dept,
                "national_id": national or None,
                "birth_date": birth_normalized,
                "phone": phone or None,
                "address": address or None,
                "extra_permissions": [],
            })
            self.accept()
        except requests.HTTPError as e:
            if e.response.status_code == 400:
                self._error.setText("نام کاربری تکراری است")
            else:
                self._error.setText("خطا در ارتباط با سرور")
        except Exception:
            self._error.setText("خطای غیرمنتظره رخ داد")


# ── Edit User Dialog ──────────────────────────────────────
class EditUserDialog(QDialog):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self._user = user
        self.setWindowTitle(f"ویرایش — {user.get('full_name', '')}")
        self.setFixedWidth(420)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(DIALOG_STYLE)
        self._build_ui()

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(14)

        title = QLabel("ویرایش اطلاعات کاربر")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #1e293b;")
        v.addWidget(title)

        uname = QLabel(f"نام کاربری: {self._user.get('username', '')}")
        uname.setStyleSheet("font-size: 11px; color: #6b7280;")
        v.addWidget(uname)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.inp_fullname = QLineEdit(self._user.get("full_name", ""))
        form.addRow("نام کامل *", self.inp_fullname)

        self.inp_national = QLineEdit(self._user.get("national_id") or "")
        self.inp_national.setPlaceholderText("۱۰ رقم")
        form.addRow("کد ملی", self.inp_national)

        self.inp_birth = QLineEdit(self._user.get("birth_date") or "")
        self.inp_birth.setPlaceholderText("مثال: ۱۳۷۰/۰۵/۱۲")
        form.addRow("تاریخ تولد", self.inp_birth)

        self.inp_phone = QLineEdit(self._user.get("phone") or "")
        self.inp_phone.setPlaceholderText("مثال: ۰۹۱۲۱۲۳۴۵۶۷")
        form.addRow("موبایل / تلفن", self.inp_phone)

        self.inp_address = QLineEdit(self._user.get("address") or "")
        self.inp_address.setPlaceholderText("آدرس کامل")
        form.addRow("آدرس", self.inp_address)

        self.cmb_role = QComboBox()
        for key, val in ROLE_FA.items():
            self.cmb_role.addItem(val, key)
        cur_role = self._user.get("role", "")
        idx = self.cmb_role.findData(cur_role)
        if idx >= 0:
            self.cmb_role.setCurrentIndex(idx)
        form.addRow("نقش *", self.cmb_role)

        self.cmb_dept = QComboBox()
        self.cmb_dept.addItem("— انتخاب نشده —", None)
        for key, val in DEPT_FA.items():
            self.cmb_dept.addItem(val, key)
        cur_dept = self._user.get("department")
        if cur_dept:
            idx = self.cmb_dept.findData(cur_dept)
            if idx >= 0:
                self.cmb_dept.setCurrentIndex(idx)
        form.addRow("بخش", self.cmb_dept)

        v.addLayout(form)

        self._error = QLabel("")
        self._error.setObjectName("error")
        v.addWidget(self._error)

        btns = QHBoxLayout()
        save = QPushButton("ذخیره تغییرات")
        save.setObjectName("save-btn")
        save.clicked.connect(self._save)
        cancel = QPushButton("انصراف")
        cancel.setObjectName("cancel-btn")
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(save)
        v.addLayout(btns)

    def _save(self):
        fullname = self.inp_fullname.text().strip()
        if not fullname:
            self._error.setText("نام کامل الزامی است")
            return

        national = self.inp_national.text().strip()
        if national and (not national.isdigit() or len(national) != 10):
            self._error.setText("کد ملی باید ۱۰ رقم باشد")
            return

        from windows.login_window import _normalize_jalali
        birth_raw = self.inp_birth.text().strip()
        birth = _normalize_jalali(birth_raw) if birth_raw else None

        try:
            update_user(self._user["id"], {
                "full_name": fullname,
                "role": self.cmb_role.currentData(),
                "department": self.cmb_dept.currentData(),
                "national_id": national or None,
                "birth_date": birth,
                "phone": self.inp_phone.text().strip() or None,
                "address": self.inp_address.text().strip() or None,
            })
            self.accept()
        except requests.HTTPError:
            self._error.setText("خطا در ارتباط با سرور")
        except Exception:
            self._error.setText("خطای غیرمنتظره رخ داد")


PERM_FA = {
    "create_purchase":   "ورود کالا (خرید)",
    "create_sale":       "فروش",
    "change_price":      "تغییر قیمت",
    "manage_inventory":  "مدیریت انبار",
    "manage_users":      "مدیریت کاربران",
    "view_reports":      "مشاهده گزارش‌ها",
    "manage_returns":    "مدیریت مرجوعی",
}

# مجوزهای پیش‌فرض هر نقش (کپی از backend/core/security.py)
ROLE_DEFAULT_PERMS: dict[str, list[str]] = {
    "ADMIN":               list(PERM_FA.keys()),
    "PHARMACIST":          ["create_purchase", "create_sale", "change_price", "manage_inventory", "view_reports", "manage_returns"],
    "OTC":                 ["create_sale", "view_reports"],
    "PRESCRIPTION":        ["create_sale", "view_reports"],
    "COSMETICS":           ["create_sale", "view_reports"],
    "CASHIER":             ["create_sale", "view_reports"],
    "WAREHOUSE":           ["create_purchase", "manage_inventory", "view_reports", "manage_returns"],
    "MEDICAL_EQUIPMENT":   ["create_sale", "view_reports"],
    "PHARMACY_TECHNICIAN": ["create_sale", "view_reports"],
    "TRAINEE":             [],
}


# ── Permissions Dialog ─────────────────────────────────────
class PermissionsDialog(QDialog):
    def __init__(self, user: dict, parent=None):
        super().__init__(parent)
        self._user = user
        self.setWindowTitle(f"مجوزها — {user.get('full_name', '')}")
        self.setFixedWidth(360)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(DIALOG_STYLE)
        self._build_ui()

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(12)

        title = QLabel("مدیریت مجوزهای کاربر")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #1e293b;")
        v.addWidget(title)

        uname = QLabel(f"نام کاربری: {self._user.get('username', '')}  ·  نقش: {ROLE_FA.get(self._user.get('role',''), '')}")
        uname.setStyleSheet("font-size: 11px; color: #6b7280;")
        v.addWidget(uname)

        note = QLabel("✅ خاکستری = مجوز پیش‌فرض نقش  |  آبی = مجوز اضافی")
        note.setStyleSheet("font-size: 10px; color: #94a3b8;")
        note.setWordWrap(True)
        v.addWidget(note)

        role = self._user.get("role", "")
        role_defaults = set(ROLE_DEFAULT_PERMS.get(role, []))
        extra = set(self._user.get("extra_permissions", []))

        self._checks: dict[str, QCheckBox] = {}

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        inner_v = QVBoxLayout(inner)
        inner_v.setSpacing(8)
        inner_v.setContentsMargins(0, 4, 0, 4)

        for perm_key, perm_fa in PERM_FA.items():
            cb = QCheckBox(perm_fa)
            cb.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

            if perm_key in role_defaults:
                cb.setChecked(True)
                cb.setEnabled(False)
                cb.setStyleSheet("QCheckBox { color: #9ca3af; font-size: 13px; }")
            else:
                cb.setChecked(perm_key in extra)
                cb.setStyleSheet("QCheckBox { color: #1e293b; font-size: 13px; } QCheckBox::indicator:checked { background: #2563eb; border: 2px solid #2563eb; border-radius: 3px; }")

            self._checks[perm_key] = cb
            inner_v.addWidget(cb)

        inner_v.addStretch()
        scroll.setWidget(inner)
        v.addWidget(scroll)

        self._error = QLabel("")
        self._error.setObjectName("error")
        v.addWidget(self._error)

        btns = QHBoxLayout()
        save = QPushButton("ذخیره مجوزها")
        save.setObjectName("save-btn")
        save.clicked.connect(self._save)
        cancel = QPushButton("انصراف")
        cancel.setObjectName("cancel-btn")
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(save)
        v.addLayout(btns)

    def _save(self):
        role = self._user.get("role", "")
        role_defaults = set(ROLE_DEFAULT_PERMS.get(role, []))

        extra = [
            perm_key
            for perm_key, cb in self._checks.items()
            if cb.isEnabled() and cb.isChecked() and perm_key not in role_defaults
        ]

        try:
            update_permissions(self._user["id"], extra)
            self.accept()
        except Exception:
            self._error.setText("خطا در ارتباط با سرور")


# ── Admin Reset Password Dialog ────────────────────────────
class AdminResetDialog(QDialog):
    def __init__(self, user_id: int, full_name: str, username: str, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle(f"تغییر رمز — {username}")
        self.setFixedWidth(340)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(DIALOG_STYLE)
        self._build_ui(full_name, username)

    def _build_ui(self, full_name: str, username: str):
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(12)

        title = QLabel("تغییر رمز عبور توسط مدیر")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b;")
        v.addWidget(title)

        info = QLabel(f"کاربر:  {full_name}  (@{username})")
        info.setStyleSheet(
            "font-size: 12px; color: #2563eb; background: #eff6ff; "
            "border: 1px solid #bfdbfe; border-radius: 6px; padding: 6px 10px;"
        )
        info.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        v.addWidget(info)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        pass_box, self.inp_pass = _make_password_row("رمز عبور جدید")
        form.addRow("رمز جدید *", pass_box)

        conf_box, self.inp_conf = _make_password_row("تکرار رمز عبور")
        form.addRow("تکرار *", conf_box)

        v.addLayout(form)

        self._error = QLabel("")
        self._error.setObjectName("error")
        v.addWidget(self._error)

        btns = QHBoxLayout()
        save = QPushButton("تغییر رمز")
        save.setObjectName("save-btn")
        save.clicked.connect(self._save)
        cancel = QPushButton("انصراف")
        cancel.setObjectName("cancel-btn")
        cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(cancel)
        btns.addWidget(save)
        v.addLayout(btns)

    def _save(self):
        pw = self.inp_pass.text()
        cf = self.inp_conf.text()
        if not pw:
            self._error.setText("رمز عبور را وارد کنید")
            return
        if len(pw) < 6:
            self._error.setText("رمز عبور باید حداقل ۶ کاراکتر باشد")
            return
        if pw != cf:
            self._error.setText("رمز عبور و تکرار آن یکسان نیستند")
            return
        try:
            admin_reset_password(self.user_id, pw)
            self.accept()
        except Exception:
            self._error.setText("خطا در ارتباط با سرور")


# ── Users Page ─────────────────────────────────────────────
class UsersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(PAGE_STYLE)
        self._users: list[dict] = []
        self._build_ui()
        self.load()

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("مدیریت کاربران")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        header.addWidget(title)
        header.addStretch()

        self._refresh_btn = QPushButton("🔄  بارگذاری مجدد")
        self._refresh_btn.setObjectName("action-btn")
        self._refresh_btn.setFixedHeight(36)
        self._refresh_btn.clicked.connect(lambda: self.load())
        header.addWidget(self._refresh_btn)

        add_btn = QPushButton("➕  کاربر جدید")
        add_btn.setObjectName("add-btn")
        add_btn.setFixedHeight(36)
        add_btn.clicked.connect(self._add_user)
        header.addWidget(add_btn)

        v.addLayout(header)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(9)
        self._table.setHorizontalHeaderLabels(
            ["نام کامل", "نام کاربری", "نقش", "بخش", "وضعیت", "ویرایش", "مجوزها", "تغییر رمز", "فعال/غیرفعال"]
        )
        self._table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(2, 140)
        self._table.setColumnWidth(3, 160)
        self._table.setColumnWidth(4, 100)
        self._table.setColumnWidth(5, 110)
        self._table.setColumnWidth(6, 110)
        self._table.setColumnWidth(7, 110)
        self._table.setColumnWidth(8, 130)
        self._table.setRowHeight(0, 44)
        v.addWidget(self._table)

        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet("font-size: 11px; color: #64748b;")
        v.addWidget(self._status_lbl)

    def load(self):
        self._refresh_btn.setEnabled(False)
        self._refresh_btn.setText("⏳  در حال بارگذاری...")
        self._status_lbl.setText("در حال بارگذاری...")
        try:
            self._users = get_users()
            self._populate()
            self._status_lbl.setText(f"{len(self._users)} کاربر")
        except Exception as e:
            self._status_lbl.setText(f"خطا: {e}")
            QMessageBox.critical(self, "خطا در بارگذاری", f"لیست کاربران بارگذاری نشد:\n{e}")
        finally:
            self._refresh_btn.setEnabled(True)
            self._refresh_btn.setText("🔄  بارگذاری مجدد")

    def _populate(self):
        self._table.setRowCount(0)
        for user in self._users:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 44)

            self._table.setItem(row, 0, QTableWidgetItem(user.get("full_name", "")))
            self._table.setItem(row, 1, QTableWidgetItem(user.get("username", "")))
            self._table.setItem(row, 2, QTableWidgetItem(ROLE_FA.get(user.get("role", ""), user.get("role", ""))))
            dept = user.get("department") or ""
            self._table.setItem(row, 3, QTableWidgetItem(DEPT_FA.get(dept, dept)))

            is_active = user.get("is_active", True)
            status_item = QTableWidgetItem("✅ فعال" if is_active else "⛔ غیرفعال")
            status_item.setForeground(QColor("#16a34a") if is_active else QColor("#dc2626"))
            self._table.setItem(row, 4, status_item)

            # Edit button
            edit_btn = QPushButton("✏️ ویرایش")
            edit_btn.setObjectName("action-btn")
            edit_btn.clicked.connect(lambda _, u=user: self._edit_user(u))
            self._table.setCellWidget(row, 5, self._wrap_btn(edit_btn))

            # Permissions button
            perm_btn = QPushButton("🔐 مجوزها")
            perm_btn.setObjectName("action-btn")
            perm_btn.clicked.connect(lambda _, u=user: self._edit_permissions(u))
            self._table.setCellWidget(row, 6, self._wrap_btn(perm_btn))

            # Reset password button
            reset_btn = QPushButton("🔑 تغییر رمز")
            reset_btn.setObjectName("action-btn")
            reset_btn.clicked.connect(
                lambda _, uid=user["id"], name=user["full_name"], uname=user["username"]:
                    self._reset_pass(uid, name, uname)
            )
            self._table.setCellWidget(row, 7, self._wrap_btn(reset_btn))

            # Activate/Deactivate button
            if is_active:
                toggle_btn = QPushButton("🚫 غیرفعال")
                toggle_btn.setObjectName("danger-btn")
                toggle_btn.clicked.connect(lambda _, uid=user["id"]: self._toggle_active(uid, False))
            else:
                toggle_btn = QPushButton("✅ فعال‌سازی")
                toggle_btn.setObjectName("ok-btn")
                toggle_btn.clicked.connect(lambda _, uid=user["id"]: self._toggle_active(uid, True))
            self._table.setCellWidget(row, 8, self._wrap_btn(toggle_btn))

    def _wrap_btn(self, btn: QPushButton) -> QWidget:
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(4, 4, 4, 4)
        h.addWidget(btn)
        return w

    def _add_user(self):
        dlg = CreateUserDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load()

    def _edit_user(self, user: dict):
        dlg = EditUserDialog(user, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load()

    def _edit_permissions(self, user: dict):
        dlg = PermissionsDialog(user, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load()

    def _reset_pass(self, user_id: int, full_name: str, username: str):
        me = Session.user() or {}
        if me.get("id") == user_id:
            QMessageBox.warning(
                self, "هشدار",
                "برای تغییر رمز خودتان از بخش پروفایل استفاده کنید.\n"
                "این بخش فقط برای تغییر رمز سایر کاربران است."
            )
            return
        dlg = AdminResetDialog(user_id, full_name, username, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "موفق", f"رمز عبور @{username} با موفقیت تغییر کرد.")

    def _toggle_active(self, user_id: int, activate: bool):
        action = "فعال‌سازی" if activate else "غیرفعال‌سازی"
        reply = QMessageBox.question(
            self, action,
            f"آیا از {action} این کاربر مطمئن هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            if activate:
                activate_user(user_id)
            else:
                deactivate_user(user_id)
            self.load()
        except Exception as e:
            QMessageBox.warning(self, "خطا", str(e))
