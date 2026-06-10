from __future__ import annotations

import json
import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFrame, QComboBox, QMessageBox, QButtonGroup,
    QRadioButton, QFormLayout, QTextEdit, QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

import requests
from api.medicine_api import get_medicines, search_medicines, get_categories, update_medicine


# ── column indices ────────────────────────────────────────
COL_RX        = 0
COL_STOCK     = 1
COL_NEW_PRICE = 2
COL_PRICE     = 3
COL_FORM      = 4
COL_GENERIC   = 5
COL_TRADE     = 6
COL_CODE      = 7
COL_ROW       = 8

_COLS = [
    "نسخه‌ای", "موجودی", "قیمت جدید(ریال)", "قیمت (ریال)",
    "شکل دارویی", "نام ژنریک", "نام تجاری", "کد ملی", "ردیف",
]

_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "price_api_config.json")

_CONFIG_DEFAULTS: dict = {
    "url": "",
    "method": "GET",
    "auth_type": "none",       # none | bearer | api_key | basic
    "auth_header": "Authorization",
    "auth_value": "",
    "code_field": "irc_code",  # فیلد کد IRC در پاسخ JSON
    "price_field": "price",    # فیلد قیمت در پاسخ JSON
    "response_path": "",       # مسیر آرایه اگه تودرتوست: مثلاً data.items
}


def _load_config() -> dict:
    cfg = dict(_CONFIG_DEFAULTS)
    try:
        with open(_CONFIG_FILE, encoding="utf-8") as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    return cfg


def _save_config(cfg: dict):
    with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def _resolve_path(data, path: str):
    """data.items.list → data['items']['list']"""
    if not path:
        return data
    for key in path.split("."):
        if isinstance(data, dict):
            data = data.get(key, data)
        elif isinstance(data, list):
            break
    return data


# ─────────────────────────────────────────────────────────
# دیالوگ تنظیمات API قیمت
# ─────────────────────────────────────────────────────────
_DLG_STYLE = """
QDialog { background: #f8fafc; }
QLabel { font-family: Tahoma, Arial; font-size: 12px; color: #374151; }
QLabel#dlg-title { font-size: 15px; font-weight: bold; color: #1e293b; }
QLabel#section { font-size: 11px; font-weight: bold; color: #6b7280;
    background: #f1f5f9; padding: 4px 8px; border-radius: 4px; }
QLineEdit, QComboBox {
    border: 1px solid #d1d5db; border-radius: 5px;
    padding: 4px 8px; font-size: 12px; background: white;
    color: #111827; min-height: 28px;
}
QLineEdit:focus, QComboBox:focus { border-color: #2563eb; }
QPushButton#save-btn {
    background: #2563eb; color: white; border: none;
    border-radius: 6px; font-size: 13px; font-weight: bold;
    padding: 0 24px; min-height: 36px;
}
QPushButton#save-btn:hover { background: #1d4ed8; }
QPushButton#test-btn {
    background: #16a34a; color: white; border: none;
    border-radius: 6px; font-size: 12px;
    padding: 0 16px; min-height: 34px;
}
QPushButton#test-btn:hover { background: #15803d; }
QPushButton#cancel-btn {
    background: white; color: #374151;
    border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 12px; padding: 0 18px; min-height: 36px;
}
QPushButton#cancel-btn:hover { background: #f1f5f9; }
QTextEdit {
    border: 1px solid #d1d5db; border-radius: 5px;
    font-family: monospace; font-size: 11px;
    background: #f8fafc; color: #374151;
}
"""


class PriceApiConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تنظیمات منبع قیمت خارجی")
        self.setMinimumWidth(560)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(_DLG_STYLE)
        self._cfg = _load_config()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        title = QLabel("⚙️  تنظیمات منبع قیمت خارجی")
        title.setObjectName("dlg-title")
        root.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def _lbl(t): return QLabel(t)
        def _ltr(w):
            w.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            return w

        # URL
        self.inp_url = QLineEdit(self._cfg["url"])
        self.inp_url.setPlaceholderText("https://api.example.com/medicines/prices")
        _ltr(self.inp_url)
        form.addRow(_lbl("آدرس API  *"), self.inp_url)

        # Method
        self.cmb_method = QComboBox()
        self.cmb_method.addItems(["GET", "POST"])
        self.cmb_method.setCurrentText(self._cfg["method"])
        _ltr(self.cmb_method)
        form.addRow(_lbl("روش درخواست"), self.cmb_method)

        # Auth type
        self.cmb_auth = QComboBox()
        self.cmb_auth.addItems(["بدون احراز هویت", "Bearer Token", "API Key (Header)", "Basic Auth"])
        _auth_map = {"none": 0, "bearer": 1, "api_key": 2, "basic": 3}
        self.cmb_auth.setCurrentIndex(_auth_map.get(self._cfg["auth_type"], 0))
        self.cmb_auth.currentIndexChanged.connect(self._toggle_auth)
        form.addRow(_lbl("احراز هویت"), self.cmb_auth)

        # Auth header name
        self.inp_auth_header = QLineEdit(self._cfg["auth_header"])
        _ltr(self.inp_auth_header)
        form.addRow(_lbl("نام Header"), self.inp_auth_header)

        # Auth value
        self.inp_auth_value = QLineEdit(self._cfg["auth_value"])
        self.inp_auth_value.setPlaceholderText("توکن یا مقدار...")
        self.inp_auth_value.setEchoMode(QLineEdit.EchoMode.Password)
        _ltr(self.inp_auth_value)
        form.addRow(_lbl("مقدار / توکن"), self.inp_auth_value)

        root.addLayout(form)

        # section: mapping fields
        sec2 = QLabel("نگاشت فیلدهای JSON")
        sec2.setObjectName("section")
        root.addWidget(sec2)

        form2 = QFormLayout()
        form2.setSpacing(8)
        form2.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.inp_response_path = QLineEdit(self._cfg["response_path"])
        self.inp_response_path.setPlaceholderText("مثلاً: data.items  (خالی اگه پاسخ مستقیماً آرایه است)")
        _ltr(self.inp_response_path)
        form2.addRow(_lbl("مسیر آرایه در JSON"), self.inp_response_path)

        self.inp_code_field = QLineEdit(self._cfg["code_field"])
        self.inp_code_field.setPlaceholderText("مثلاً: irc_code")
        _ltr(self.inp_code_field)
        form2.addRow(_lbl("نام فیلد کد ملی"), self.inp_code_field)

        self.inp_price_field = QLineEdit(self._cfg["price_field"])
        self.inp_price_field.setPlaceholderText("مثلاً: price یا sale_price")
        _ltr(self.inp_price_field)
        form2.addRow(_lbl("نام فیلد قیمت"), self.inp_price_field)

        root.addLayout(form2)

        # test result
        self._test_result = QTextEdit()
        self._test_result.setReadOnly(True)
        self._test_result.setFixedHeight(110)
        self._test_result.setPlaceholderText(
            "نتیجه تست اتصال اینجا نمایش داده می‌شود..."
        )
        root.addWidget(self._test_result)

        # buttons
        btns = QHBoxLayout()
        btns.addStretch()
        cancel = QPushButton("انصراف")
        cancel.setObjectName("cancel-btn")
        cancel.clicked.connect(self.reject)
        test_btn = QPushButton("🔌  تست اتصال")
        test_btn.setObjectName("test-btn")
        test_btn.clicked.connect(self._test_connection)
        save = QPushButton("💾  ذخیره")
        save.setObjectName("save-btn")
        save.clicked.connect(self._save)
        btns.addWidget(cancel)
        btns.addWidget(test_btn)
        btns.addWidget(save)
        root.addLayout(btns)

        self._toggle_auth()

    def _toggle_auth(self):
        show = self.cmb_auth.currentIndex() != 0
        self.inp_auth_header.setEnabled(show)
        self.inp_auth_value.setEnabled(show)

    def _build_headers(self) -> dict:
        idx = self.cmb_auth.currentIndex()
        val = self.inp_auth_value.text().strip()
        hdr = self.inp_auth_header.text().strip() or "Authorization"
        if idx == 1:
            return {hdr: f"Bearer {val}"}
        elif idx == 2:
            return {hdr: val}
        elif idx == 3:
            import base64
            token = base64.b64encode(val.encode()).decode()
            return {"Authorization": f"Basic {token}"}
        return {}

    def _test_connection(self):
        url = self.inp_url.text().strip()
        if not url:
            self._test_result.setPlainText("❌  آدرس API خالی است.")
            return
        self._test_result.setPlainText("⏳  در حال اتصال...")
        try:
            method = self.cmb_method.currentText()
            headers = self._build_headers()
            r = requests.request(method, url, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            path = self.inp_response_path.text().strip()
            items = _resolve_path(data, path)
            if isinstance(items, list) and items:
                sample = json.dumps(items[0], ensure_ascii=False, indent=2)
                self._test_result.setPlainText(
                    f"✅  اتصال موفق — {len(items)} رکورد دریافت شد.\n"
                    f"نمونه اول:\n{sample}"
                )
            else:
                self._test_result.setPlainText(
                    f"✅  پاسخ دریافت شد ولی آرایه‌ای یافت نشد.\n"
                    f"مسیر response_path را بررسی کنید.\n\n"
                    f"{json.dumps(data, ensure_ascii=False, indent=2)[:600]}"
                )
        except requests.exceptions.ConnectionError:
            self._test_result.setPlainText("❌  خطا: اتصال برقرار نشد.")
        except requests.HTTPError as e:
            self._test_result.setPlainText(f"❌  خطای HTTP {e.response.status_code}: {e}")
        except Exception as e:
            self._test_result.setPlainText(f"❌  خطا: {e}")

    def _save(self):
        _auth_rev = {0: "none", 1: "bearer", 2: "api_key", 3: "basic"}
        cfg = {
            "url": self.inp_url.text().strip(),
            "method": self.cmb_method.currentText(),
            "auth_type": _auth_rev[self.cmb_auth.currentIndex()],
            "auth_header": self.inp_auth_header.text().strip() or "Authorization",
            "auth_value": self.inp_auth_value.text().strip(),
            "code_field": self.inp_code_field.text().strip() or "irc_code",
            "price_field": self.inp_price_field.text().strip() or "price",
            "response_path": self.inp_response_path.text().strip(),
        }
        try:
            _save_config(cfg)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"ذخیره تنظیمات ناموفق: {e}")


# ─────────────────────────────────────────────────────────
# صفحه داروها
# ─────────────────────────────────────────────────────────
def _fmt(n) -> str:
    try:
        return f"{int(float(n)):,}"
    except Exception:
        return "—"


PAGE_STYLE = """
QWidget { font-family: Tahoma, Arial; }
QFrame#topbar { background: white; border: 1px solid #e2e8f0; border-radius: 10px; }
QLabel#page-title { font-size: 16px; font-weight: bold; color: #1e293b; }
QLabel#status-lbl { font-size: 11px; color: #64748b; }
QLineEdit#search {
    border: 1px solid #d1d5db; border-radius: 6px;
    padding: 4px 10px; font-size: 13px; background: white;
    min-height: 30px; min-width: 220px;
}
QLineEdit#search:focus { border-color: #2563eb; }
QComboBox {
    border: 1px solid #d1d5db; border-radius: 6px;
    padding: 4px 8px; font-size: 12px; background: white;
    min-height: 30px; min-width: 130px;
}
QPushButton#add-btn {
    background: #2563eb; color: white; border: none;
    border-radius: 6px; font-size: 12px; font-weight: bold;
    padding: 0 16px; min-height: 32px;
}
QPushButton#add-btn:hover { background: #1d4ed8; }
QPushButton#apply-btn {
    background: #d97706; color: white; border: none;
    border-radius: 6px; font-size: 12px; font-weight: bold;
    padding: 0 16px; min-height: 32px;
}
QPushButton#apply-btn:hover { background: #b45309; }
QPushButton#fetch-btn {
    background: #0891b2; color: white; border: none;
    border-radius: 6px; font-size: 12px; font-weight: bold;
    padding: 0 14px; min-height: 32px;
}
QPushButton#fetch-btn:hover { background: #0e7490; }
QPushButton#cfg-btn {
    background: white; color: #374151;
    border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 12px; padding: 0 12px; min-height: 32px;
}
QPushButton#cfg-btn:hover { background: #f1f5f9; }
QPushButton#reload-btn {
    background: white; color: #374151;
    border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 12px; padding: 0 12px; min-height: 32px;
}
QPushButton#reload-btn:hover { background: #f1f5f9; }
QTableWidget {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 8px; gridline-color: #f1f5f9; font-size: 12px;
}
QTableWidget::item { padding: 3px 8px; }
QTableWidget::item:selected { background: #eff6ff; color: #1e293b; }
QHeaderView::section {
    background: #f8fafc; border: none;
    border-bottom: 1px solid #e2e8f0;
    padding: 6px 8px; font-size: 11px; font-weight: bold; color: #64748b;
}
QRadioButton { font-size: 12px; color: #374151; }
"""

_NEW_PRICE_STYLE = (
    "QLineEdit { border: 1px solid #fbbf24; border-radius: 3px; "
    "padding: 1px 6px; font-size: 12px; background: #fffbeb; color: #92400e; }"
    "QLineEdit:focus { border-color: #f59e0b; background: #fef3c7; }"
)


class MedicinesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(PAGE_STYLE)
        self._all_medicines: list[dict] = []
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)
        self._build_ui()
        self._load_categories()
        self.load()

    # ── UI ────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 12, 20, 12)
        root.setSpacing(8)

        topbar = QFrame()
        topbar.setObjectName("topbar")
        tb = QHBoxLayout(topbar)
        tb.setContentsMargins(14, 10, 14, 10)
        tb.setSpacing(8)

        title = QLabel("کاتالوگ داروها")
        title.setObjectName("page-title")
        tb.addWidget(title)
        tb.addStretch()

        self._search = QLineEdit()
        self._search.setObjectName("search")
        self._search.setPlaceholderText("🔍  جستجو: نام، کد ملی، ژنریک...")
        self._search.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._search.textChanged.connect(lambda: self._search_timer.start(280))
        tb.addWidget(self._search)

        self._cmb_cat = QComboBox()
        self._cmb_cat.addItem("همه دسته‌ها", None)
        self._cmb_cat.currentIndexChanged.connect(self._apply_filters)
        tb.addWidget(self._cmb_cat)

        self._rbg = QButtonGroup(self)
        for i, lbl in enumerate(["همه", "OTC", "نسخه‌ای"]):
            rb = QRadioButton(lbl)
            if i == 0:
                rb.setChecked(True)
            self._rbg.addButton(rb, i)
            tb.addWidget(rb)
        self._rbg.idClicked.connect(self._apply_filters)

        tb.addSpacing(4)

        reload_btn = QPushButton("🔄")
        reload_btn.setObjectName("reload-btn")
        reload_btn.setToolTip("بارگذاری مجدد")
        reload_btn.setFixedWidth(36)
        reload_btn.clicked.connect(lambda: self.load())
        tb.addWidget(reload_btn)

        cfg_btn = QPushButton("⚙️  تنظیم API")
        cfg_btn.setObjectName("cfg-btn")
        cfg_btn.clicked.connect(self._open_api_config)
        tb.addWidget(cfg_btn)

        fetch_btn = QPushButton("🌐  دریافت قیمت از منبع")
        fetch_btn.setObjectName("fetch-btn")
        fetch_btn.clicked.connect(self._fetch_prices_from_api)
        tb.addWidget(fetch_btn)

        apply_btn = QPushButton("💾  اعمال قیمت‌های جدید")
        apply_btn.setObjectName("apply-btn")
        apply_btn.clicked.connect(self._apply_new_prices)
        tb.addWidget(apply_btn)

        add_btn = QPushButton("➕  دارو جدید")
        add_btn.setObjectName("add-btn")
        add_btn.clicked.connect(self._add_medicine)
        tb.addWidget(add_btn)

        root.addWidget(topbar)

        hint = QLabel(
            "💡  ستون «قیمت جدید» را دستی وارد کنید یا از دکمه «دریافت قیمت از منبع» auto-fill کنید، "
            "سپس «اعمال قیمت‌های جدید» را بزنید."
        )
        hint.setStyleSheet(
            "font-size: 11px; color: #92400e; background: #fffbeb; "
            "padding: 4px 10px; border-radius: 6px;"
        )
        root.addWidget(hint)

        self._table = QTableWidget()
        self._table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._table.setColumnCount(len(_COLS))
        self._table.setHorizontalHeaderLabels(_COLS)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.cellDoubleClicked.connect(self._on_double_click)

        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(COL_RX,        QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(COL_STOCK,     QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(COL_NEW_PRICE, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(COL_PRICE,     QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(COL_FORM,      QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(COL_GENERIC,   QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(COL_TRADE,     QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(COL_CODE,      QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(COL_ROW,       QHeaderView.ResizeMode.ResizeToContents)
        self._table.setColumnWidth(COL_NEW_PRICE, 150)
        root.addWidget(self._table)

        self._status = QLabel("")
        self._status.setObjectName("status-lbl")
        root.addWidget(self._status)

    # ── Categories ────────────────────────────────────────
    def _load_categories(self):
        try:
            for cat in get_categories():
                self._cmb_cat.addItem(cat["name"], cat["id"])
        except Exception:
            pass

    # ── Data ──────────────────────────────────────────────
    def load(self):
        self._status.setText("در حال بارگذاری...")
        try:
            self._all_medicines = get_medicines()
            self._apply_filters()
        except Exception as e:
            QMessageBox.critical(self, "خطا", str(e))
            self._status.setText("خطا در بارگذاری")

    def _do_search(self):
        q = self._search.text().strip()
        if len(q) >= 2:
            try:
                self._populate(search_medicines(q=q))
                return
            except Exception:
                pass
        self._apply_filters()

    def _apply_filters(self, *_):
        meds = self._all_medicines
        cat_id = self._cmb_cat.currentData()
        if cat_id is not None:
            meds = [m for m in meds if m.get("category_id") == cat_id]
        rx_id = self._rbg.checkedId()
        if rx_id == 1:
            meds = [m for m in meds if not m.get("is_prescription", False)]
        elif rx_id == 2:
            meds = [m for m in meds if m.get("is_prescription", False)]
        self._populate(meds)

    def _populate(self, meds: list[dict]):
        self._table.setRowCount(0)
        self._table.setRowCount(len(meds))
        for r, med in enumerate(meds):
            self._table.setRowHeight(r, 32)

            row_item = QTableWidgetItem(str(r + 1))
            row_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row_item.setForeground(QColor("#94a3b8"))
            row_item.setData(Qt.ItemDataRole.UserRole, med)
            self._table.setItem(r, COL_ROW, row_item)

            self._cell(r, COL_CODE,    med.get("code") or "", center=True)
            self._cell(r, COL_TRADE,   med.get("name") or "")
            self._cell(r, COL_GENERIC, med.get("generic_name") or "", color="#6b7280")
            self._cell(r, COL_FORM,    med.get("dosage_form") or "", center=True, color="#6b7280")
            self._cell(r, COL_PRICE,   _fmt(med.get("sale_price") or 0), center=True)

            inp = QLineEdit()
            inp.setPlaceholderText("قیمت جدید...")
            inp.setStyleSheet(_NEW_PRICE_STYLE)
            inp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            inp.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self._table.setCellWidget(r, COL_NEW_PRICE, inp)

            stock = med.get("current_stock") or 0
            self._cell(r, COL_STOCK, str(stock), center=True,
                       color="#16a34a" if stock > 0 else "#dc2626")

            rx = "✓  نسخه‌ای" if med.get("is_prescription") else "—"
            self._cell(r, COL_RX, rx, center=True,
                       color="#2563eb" if med.get("is_prescription") else "#9ca3af")

        self._status.setText(f"نمایش {len(meds)} دارو")

    def _cell(self, row, col, text, center=False, color=None):
        item = QTableWidgetItem(text)
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if color:
            item.setForeground(QColor(color))
        self._table.setItem(row, col, item)

    # ── Fetch prices from external API ────────────────────
    def _open_api_config(self):
        dlg = PriceApiConfigDialog(self)
        dlg.exec()

    def _fetch_prices_from_api(self):
        cfg = _load_config()
        if not cfg.get("url"):
            QMessageBox.warning(
                self, "تنظیمات ناقص",
                "آدرس API تنظیم نشده است.\n"
                "ابتدا «⚙️ تنظیم API» را باز کنید و URL را وارد کنید."
            )
            return

        self._status.setText("⏳  در حال دریافت قیمت از منبع خارجی...")
        try:
            headers = self._build_request_headers(cfg)
            r = requests.request(
                cfg["method"], cfg["url"], headers=headers, timeout=15
            )
            r.raise_for_status()
            data = r.json()
            items = _resolve_path(data, cfg["response_path"])
            if not isinstance(items, list):
                raise ValueError("پاسخ API آرایه نیست — مسیر response_path را بررسی کنید.")
        except Exception as e:
            QMessageBox.critical(self, "خطا در دریافت قیمت", str(e))
            self._status.setText("خطا در دریافت قیمت از منبع خارجی")
            return

        code_f = cfg["code_field"]
        price_f = cfg["price_field"]
        price_map: dict[str, str] = {}
        for item in items:
            if isinstance(item, dict):
                code = str(item.get(code_f) or "").strip()
                price = item.get(price_f)
                if code and price is not None:
                    price_map[code] = str(price)

        filled = 0
        for r in range(self._table.rowCount()):
            code_item = self._table.item(r, COL_CODE)
            inp = self._table.cellWidget(r, COL_NEW_PRICE)
            if not code_item or not isinstance(inp, QLineEdit):
                continue
            code = code_item.text().strip()
            if code in price_map:
                inp.setText(price_map[code])
                filled += 1

        if filled:
            self._status.setText(
                f"✅  {filled} دارو از منبع خارجی قیمت‌گذاری شد — "
                "بررسی کنید و «اعمال قیمت‌های جدید» را بزنید."
            )
        else:
            self._status.setText(
                f"⚠️  داده دریافت شد ({len(items)} رکورد) ولی هیچ کدی تطابق نداشت. "
                "نام فیلد کد را در تنظیمات بررسی کنید."
            )

    def _build_request_headers(self, cfg: dict) -> dict:
        auth_type = cfg.get("auth_type", "none")
        val = cfg.get("auth_value", "")
        hdr = cfg.get("auth_header", "Authorization")
        if auth_type == "bearer":
            return {hdr: f"Bearer {val}"}
        elif auth_type == "api_key":
            return {hdr: val}
        elif auth_type == "basic":
            import base64
            token = base64.b64encode(val.encode()).decode()
            return {"Authorization": f"Basic {token}"}
        return {}

    # ── Apply new prices ──────────────────────────────────
    def _apply_new_prices(self):
        updates: list[tuple[int, float, str]] = []
        for r in range(self._table.rowCount()):
            inp = self._table.cellWidget(r, COL_NEW_PRICE)
            if not isinstance(inp, QLineEdit):
                continue
            txt = inp.text().strip().replace(",", "")
            if not txt:
                continue
            try:
                price = float(txt)
                if price <= 0:
                    raise ValueError
            except ValueError:
                trade = (self._table.item(r, COL_TRADE) or QTableWidgetItem()).text()
                QMessageBox.warning(self, "خطا", f"قیمت نامعتبر در ردیف {r+1}  ({trade})")
                return
            row_item = self._table.item(r, COL_ROW)
            med = row_item.data(Qt.ItemDataRole.UserRole) if row_item else None
            if med:
                updates.append((med["id"], price, med.get("name") or ""))

        if not updates:
            QMessageBox.information(self, "راهنما",
                                    "هیچ قیمت جدیدی وارد نشده است.")
            return

        reply = QMessageBox.question(
            self, "تأیید",
            f"قیمت {len(updates)} دارو آپدیت می‌شود. ادامه می‌دهید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        errors, ok_count = [], 0
        for med_id, price, name in updates:
            try:
                update_medicine(med_id, {"sale_price": price})
                ok_count += 1
            except Exception as e:
                errors.append(f"{name}: {e}")

        if errors:
            QMessageBox.warning(self, "نتیجه",
                                f"{ok_count} دارو آپدیت شد.\nخطا:\n" + "\n".join(errors))
        else:
            QMessageBox.information(self, "موفق",
                                    f"قیمت {ok_count} دارو با موفقیت آپدیت شد.")
        self.load()

    # ── Edit / Add ────────────────────────────────────────
    def _on_double_click(self, row: int, col: int):
        if col == COL_NEW_PRICE:
            return
        row_item = self._table.item(row, COL_ROW)
        if not row_item:
            return
        med = row_item.data(Qt.ItemDataRole.UserRole)
        if med:
            self._edit_medicine(med)

    def _add_medicine(self):
        from windows.dashboard_page import MedicineDialog
        dlg = MedicineDialog(None, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_medicine:
            self.load()

    def _edit_medicine(self, med: dict):
        from windows.dashboard_page import MedicineDialog
        dlg = MedicineDialog(med, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_medicine:
            self.load()
