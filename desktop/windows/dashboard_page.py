from __future__ import annotations

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QSpinBox, QMessageBox, QFrame, QListWidget,
    QListWidgetItem, QAbstractItemView, QComboBox, QCheckBox,
    QFormLayout, QScrollArea, QDoubleSpinBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QKeyEvent

import requests
from api.medicine_api import search_medicines, create_medicine, update_medicine, get_categories, get_companies
from api.sale_api import create_sale


# ── helpers ───────────────────────────────────────────────
def _drug_label(med: dict) -> str:
    parts = [
        (med.get("generic_name") or med.get("name") or "").lower(),
        (med.get("dosage_form") or "").lower(),
        (med.get("strength") or ""),
    ]
    return " ".join(p for p in parts if p).strip()


def _fmt(n) -> str:
    try:
        return f"{int(float(n)):,}"
    except Exception:
        return "—"


def _now_doc() -> str:
    return "SAL-" + datetime.now().strftime("%Y%m%d-%H%M%S%f")[:20]


# ── styles ────────────────────────────────────────────────
PAGE_STYLE = """
QWidget { font-family: Tahoma, Arial; }
QLabel#page-title { font-size: 16px; font-weight: bold; color: #1e293b; }
QLabel#doc-info   { font-size: 12px; color: #64748b; }
QLabel#total-lbl  { font-size: 17px; font-weight: bold; color: #16a34a; }
QLabel#hint       { font-size: 10px; color: #94a3b8; }
QFrame#topbar { background: white; border: 1px solid #e2e8f0; border-radius: 10px; }
QPushButton#submit-btn {
    background: #16a34a; color: white; border: none;
    border-radius: 8px; font-size: 14px; font-weight: bold;
    padding: 0 30px; min-height: 42px;
}
QPushButton#submit-btn:hover { background: #15803d; }
QPushButton#clear-btn {
    background: #fef2f2; color: #dc2626;
    border: 1px solid #fecaca; border-radius: 6px;
    font-size: 12px; padding: 0 14px; min-height: 36px;
}
QPushButton#clear-btn:hover { background: #fee2e2; }
QTableWidget {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 8px; gridline-color: #f1f5f9; font-size: 13px;
}
QTableWidget::item { padding: 2px 8px; }
QTableWidget::item:selected { background: #eff6ff; color: #1e293b; }
QHeaderView::section {
    background: #f8fafc; border: none;
    border-bottom: 1px solid #e2e8f0;
    padding: 6px 8px; font-size: 12px; font-weight: bold; color: #64748b;
}
QSpinBox {
    border: 1px solid #d1d5db; border-radius: 4px;
    padding: 1px 4px; font-size: 13px; font-weight: 400;
    min-width: 56px; min-height: 26px;
    background: white; color: #374151;
}
QSpinBox:focus { border-color: #2563eb; }
"""

_INPUT_NORMAL = (
    "QLineEdit { border: 1px solid #d1d5db; border-radius: 4px; "
    "padding: 2px 6px; font-size: 13px; font-weight: 400; background: white; "
    "color: #374151; min-height: 26px; }"
    "QLineEdit:focus { border: 1px solid #2563eb; }"
)
_INPUT_LOCKED = (
    "QLineEdit { border: 1px solid #bbf7d0; border-radius: 4px; "
    "padding: 2px 6px; font-size: 13px; font-weight: 400; background: #f0fdf4; "
    "color: #166534; min-height: 26px; }"
)
_INPUT_ERROR = (
    "QLineEdit { border: 1px solid #dc2626; border-radius: 4px; "
    "padding: 2px 6px; font-size: 13px; font-weight: 400; background: #fef2f2; "
    "color: #dc2626; min-height: 26px; }"
)

RECEIPT_STYLE = """
QDialog { background: white; }
QLabel { font-family: Tahoma, Arial; }
QLabel#r-title { font-size: 15px; font-weight: bold; color: #1e293b; }
QLabel#r-sub   { font-size: 11px; color: #6b7280; }
QLabel#r-total { font-size: 16px; font-weight: bold; color: #16a34a; }
QFrame#divider { background: #e2e8f0; max-height: 1px; }
"""


# ── Drug search popup ─────────────────────────────────────
class DrugPopup(QFrame):
    """Floating popup — never steals focus from the input field."""
    drug_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.Tool |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet(
            "QFrame { background: white; border: 2px solid #2563eb; border-radius: 6px; }"
            "QListWidget { border: none; font-size: 13px; background: white; outline: none; }"
            "QListWidget::item { padding: 6px 10px; color: #111827; }"
            "QListWidget::item:hover { background: #eff6ff; }"
            "QListWidget::item:selected { background: #2563eb; color: white; }"
        )
        v = QVBoxLayout(self)
        v.setContentsMargins(2, 2, 2, 2)
        self._list = QListWidget()
        self._list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._list.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list.itemClicked.connect(self._pick)
        v.addWidget(self._list)
        self._current_row = -1

    def show_for(self, medicines: list[dict], inp: QLineEdit, row: int):
        self._current_row = row
        self._list.clear()
        if not medicines:
            self.hide()
            return
        for med in medicines[:15]:
            item = QListWidgetItem(_drug_label(med))
            item.setData(Qt.ItemDataRole.UserRole, med)
            self._list.addItem(item)
        row_h = 32
        h = min(len(medicines), 15) * row_h + 6
        self._list.setFixedHeight(h)
        self.setFixedHeight(h + 4)
        self.setFixedWidth(max(320, inp.width()))
        pos = inp.mapToGlobal(QPoint(0, inp.height() + 2))
        self.move(pos)
        self.show()
        self._list.setCurrentRow(0)

    def move_selection(self, direction: int):
        cur = self._list.currentRow()
        nxt = max(0, min(cur + direction, self._list.count() - 1))
        self._list.setCurrentRow(nxt)

    def confirm(self):
        item = self._list.currentItem()
        if item:
            self._pick(item)

    def _pick(self, item: QListWidgetItem):
        med = item.data(Qt.ItemDataRole.UserRole)
        self.hide()
        self.drug_selected.emit(med)


# ── QtySpinBox ───────────────────────────────────────────
class QtySpinBox(QSpinBox):
    enter_hit = pyqtSignal()
    nav_requested = pyqtSignal(int)  # -1 = up row, +1 = down row

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.enter_hit.emit()
        elif event.key() == Qt.Key.Key_Up:
            self.nav_requested.emit(-1)
        elif event.key() == Qt.Key.Key_Down:
            self.nav_requested.emit(1)
        else:
            super().keyPressEvent(event)


# ── DrugInput ────────────────────────────────────────────
class DrugInput(QLineEdit):
    enter_hit = pyqtSignal()
    unlock_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def mousePressEvent(self, event):
        if self.isReadOnly():
            self.unlock_requested.emit()
            return
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.enter_hit.emit()
        elif key == Qt.Key.Key_Down:
            p = self._get_page()
            if p and p._popup.isVisible():
                p._popup.move_selection(1)
            else:
                self._navigate_row(1)
        elif key == Qt.Key.Key_Up:
            p = self._get_page()
            if p and p._popup.isVisible():
                p._popup.move_selection(-1)
            else:
                self._navigate_row(-1)
        elif key == Qt.Key.Key_Escape:
            p = self._get_page()
            if p and p._popup.isVisible():
                p._popup.hide()
            else:
                self._restore_original()
        else:
            super().keyPressEvent(event)

    def _navigate_row(self, direction: int):
        p = self._get_page()
        if p:
            p._nav_from_input(self, direction)

    def _restore_original(self):
        p = self._get_page()
        if p:
            p._restore_row_from_input(self)

    def _get_page(self):
        w = self.parent()
        while w:
            if isinstance(w, DashboardPage):
                return w
            w = w.parent()
        return None


# ── Receipt dialog ────────────────────────────────────────
class ReceiptDialog(QDialog):
    def __init__(self, sale: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("فیش فروش")
        self.setFixedWidth(340)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(RECEIPT_STYLE)
        self._build(sale)

    def _build(self, sale: dict):
        v = QVBoxLayout(self)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(6)

        h = QLabel("💊  داروخانه")
        h.setObjectName("r-title")
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(h)

        created = sale.get("created_at") or ""
        try:
            dt = datetime.fromisoformat(created)
            date_str, time_str = dt.strftime("%Y/%m/%d"), dt.strftime("%H:%M:%S")
        except Exception:
            date_str = datetime.now().strftime("%Y/%m/%d")
            time_str = datetime.now().strftime("%H:%M:%S")

        for lbl, val in [
            ("شماره سند:", sale.get("sale_number", "")),
            ("تاریخ:", date_str),
            ("ساعت:", time_str),
        ]:
            v.addWidget(QLabel(f"{lbl}  {val}"))

        div = QFrame()
        div.setObjectName("divider")
        v.addWidget(div)

        for item in sale.get("items", []):
            med = item.get("medicine", {})
            name = _drug_label(med) if med else ""
            qty = item.get("quantity", 1)
            price = float(item.get("unit_price", 0))
            n = QLabel(name)
            n.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            n.setAlignment(Qt.AlignmentFlag.AlignLeft)
            n.setStyleSheet("font-size: 12px; color: #1e293b; font-weight: bold;")
            v.addWidget(n)
            s = QLabel(f"  {qty}  ×  {_fmt(price)}  =  {_fmt(price * qty)} ریال")
            s.setObjectName("r-sub")
            v.addWidget(s)

        div2 = QFrame()
        div2.setObjectName("divider")
        v.addWidget(div2)

        t = QLabel(f"جمع کل:  {_fmt(sale.get('total_amount', 0))} ریال")
        t.setObjectName("r-total")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t)

        close = QPushButton("بستن  (Enter)")
        close.setDefault(True)
        close.clicked.connect(self.accept)
        v.addWidget(close)


MEDICINE_DIALOG_STYLE = """
QDialog { background: #f8fafc; }
QLabel { font-family: Tahoma, Arial; font-size: 12px; color: #374151; }
QLabel#dlg-title { font-size: 15px; font-weight: bold; color: #1e293b; }
QLabel#section { font-size: 11px; font-weight: bold; color: #6b7280;
    background: #f1f5f9; padding: 4px 8px; border-radius: 4px; }
QLineEdit, QComboBox, QDoubleSpinBox {
    border: 1px solid #d1d5db; border-radius: 5px;
    padding: 4px 8px; font-size: 12px; background: white;
    color: #111827; min-height: 28px;
}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus { border-color: #2563eb; }
QLineEdit[readonly="true"] { background: #f1f5f9; color: #6b7280; }
QCheckBox { font-size: 12px; color: #374151; }
QPushButton#save-btn {
    background: #2563eb; color: white; border: none;
    border-radius: 6px; font-size: 13px; font-weight: bold;
    padding: 0 24px; min-height: 36px;
}
QPushButton#save-btn:hover { background: #1d4ed8; }
QPushButton#cancel-btn {
    background: white; color: #374151;
    border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 12px; padding: 0 18px; min-height: 36px;
}
QPushButton#cancel-btn:hover { background: #f1f5f9; }
QLabel#err { color: #dc2626; font-size: 11px; }
"""

_DOSAGE_FORMS = [
    "", "قرص", "کپسول", "شربت", "آمپول", "پماد", "قطره", "اسپری",
    "پچ", "کرم", "ژل", "سوسپانسیون", "پودر", "شیاف", "قرص جوشان",
]


class MedicineDialog(QDialog):
    """فرم ورود / ویرایش دارو"""

    def __init__(self, medicine: dict | None = None, parent=None):
        super().__init__(parent)
        self._medicine = medicine
        self._categories: list[dict] = []
        self._companies: list[dict] = []
        self.result_medicine: dict | None = None
        self.setWindowTitle("ویرایش دارو" if medicine else "ورود دارو جدید")
        self.setMinimumWidth(500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(MEDICINE_DIALOG_STYLE)
        self._build_ui()
        self._load_dropdowns()
        if medicine:
            self._populate(medicine)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        title_lbl = QLabel("ویرایش دارو" if self._medicine else "ورود دارو جدید")
        title_lbl.setObjectName("dlg-title")
        root.addWidget(title_lbl)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        def _lbl(t): return QLabel(t)

        def _ltr(w):
            w.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            return w

        # کد IRC
        self.inp_code = QLineEdit()
        self.inp_code.setPlaceholderText("مثال: 1234567890")
        _ltr(self.inp_code)
        form.addRow(_lbl("کد IRC *"), self.inp_code)

        # کد مجازی
        self.inp_virtual_code = QLineEdit()
        self.inp_virtual_code.setPlaceholderText("کد مجازی")
        _ltr(self.inp_virtual_code)
        form.addRow(_lbl("کد مجازی"), self.inp_virtual_code)

        # نام تجاری (انگلیسی)
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("PARACETAMOL 500MG TAB")
        _ltr(self.inp_name)
        form.addRow(_lbl("نام تجاری *"), self.inp_name)

        # نام ژنریک
        self.inp_generic = QLineEdit()
        self.inp_generic.setPlaceholderText("استامینوفن")
        form.addRow(_lbl("نام ژنریک"), self.inp_generic)

        # شکل دارویی
        self.cmb_dosage = QComboBox()
        self.cmb_dosage.addItems(_DOSAGE_FORMS)
        form.addRow(_lbl("شکل دارویی"), self.cmb_dosage)

        # دوز / غلظت
        self.inp_strength = QLineEdit()
        self.inp_strength.setPlaceholderText("500mg")
        _ltr(self.inp_strength)
        form.addRow(_lbl("دوز / غلظت"), self.inp_strength)

        # قیمت
        self.inp_price = QDoubleSpinBox()
        self.inp_price.setRange(0, 999_999_999)
        self.inp_price.setDecimals(0)
        self.inp_price.setSingleStep(1000)
        self.inp_price.setSuffix("  ریال")
        _ltr(self.inp_price)
        form.addRow(_lbl("قیمت فروش"), self.inp_price)

        # تعداد پیش‌فرض فروش
        self.inp_default_qty = QSpinBox()
        self.inp_default_qty.setMinimum(1)
        self.inp_default_qty.setMaximum(9999)
        self.inp_default_qty.setValue(1)
        _ltr(self.inp_default_qty)
        form.addRow(_lbl("تعداد پیش‌فرض"), self.inp_default_qty)

        # دسته
        self.cmb_category = QComboBox()
        form.addRow(_lbl("دسته‌بندی"), self.cmb_category)

        # شرکت / تولیدکننده
        self.cmb_company = QComboBox()
        form.addRow(_lbl("شرکت / تولیدکننده"), self.cmb_company)

        # نسخه‌ای
        self.chk_prescription = QCheckBox("نسخه‌ای است (Rx)")
        form.addRow(_lbl(""), self.chk_prescription)

        root.addLayout(form)

        self._err = QLabel("")
        self._err.setObjectName("err")
        root.addWidget(self._err)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel = QPushButton("انصراف")
        cancel.setObjectName("cancel-btn")
        cancel.clicked.connect(self.reject)
        save = QPushButton("💾  ذخیره")
        save.setObjectName("save-btn")
        save.clicked.connect(self._save)
        btns.addWidget(cancel)
        btns.addWidget(save)
        root.addLayout(btns)

    def _load_dropdowns(self):
        try:
            cats = get_categories()
            self._categories = cats
            self.cmb_category.clear()
            self.cmb_category.addItem("— انتخاب کنید —", None)
            for c in cats:
                self.cmb_category.addItem(c["name"], c["id"])
        except Exception:
            pass
        try:
            comps = get_companies()
            self._companies = comps
            self.cmb_company.clear()
            self.cmb_company.addItem("— انتخاب کنید —", None)
            for c in comps:
                self.cmb_company.addItem(c["name"], c["id"])
        except Exception:
            pass

    def _populate(self, med: dict):
        self.inp_code.setText(med.get("code") or "")
        self.inp_virtual_code.setText(med.get("virtual_code") or "")
        self.inp_name.setText(med.get("name") or "")
        self.inp_generic.setText(med.get("generic_name") or "")
        df = med.get("dosage_form") or ""
        idx = self.cmb_dosage.findText(df)
        self.cmb_dosage.setCurrentIndex(idx if idx >= 0 else 0)
        self.inp_strength.setText(med.get("strength") or "")
        self.inp_price.setValue(float(med.get("sale_price") or 0))
        self.inp_default_qty.setValue(int(med.get("default_quantity") or 1))
        self.chk_prescription.setChecked(bool(med.get("is_prescription", False)))
        for cmb, key in [(self.cmb_category, "category_id"), (self.cmb_company, "company_id")]:
            val = med.get(key)
            if val:
                for i in range(cmb.count()):
                    if cmb.itemData(i) == val:
                        cmb.setCurrentIndex(i)
                        break

    def _save(self):
        code = self.inp_code.text().strip()
        name = self.inp_name.text().strip()
        if not code or not name:
            self._err.setText("کد IRC و نام تجاری الزامی است")
            return
        price_val = self.inp_price.value()
        data = {
            "virtual_code": self.inp_virtual_code.text().strip() or None,
            "name": name,
            "generic_name": self.inp_generic.text().strip() or None,
            "dosage_form": self.cmb_dosage.currentText() or None,
            "strength": self.inp_strength.text().strip() or None,
            "is_prescription": self.chk_prescription.isChecked(),
            "sale_price": price_val if price_val > 0 else None,
            "default_quantity": self.inp_default_qty.value(),
            "category_id": self.cmb_category.currentData(),
            "company_id": self.cmb_company.currentData(),
        }
        try:
            if self._medicine:
                self.result_medicine = update_medicine(self._medicine["id"], data)
            else:
                self.result_medicine = create_medicine(code=code, **data)
            self.accept()
        except requests.HTTPError as e:
            status = e.response.status_code if e.response else 0
            if status == 400:
                self._err.setText("کد دارو تکراری است")
            else:
                self._err.setText(f"خطا {status}: {e}")
        except Exception as e:
            self._err.setText(f"خطا: {e}")


# ── Dashboard / POS ───────────────────────────────────────
class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(PAGE_STYLE)
        self._medicines: list[dict] = []
        self._doc_number = _now_doc()
        self._popup = DrugPopup()
        self._popup.drug_selected.connect(self._on_drug_selected)
        self._clock_timer = QTimer()
        self._clock_timer.timeout.connect(self._tick)
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)
        self._pending_search: tuple[int, str] = (-1, "")
        self._build_ui()
        self._clock_timer.start(1000)
        self._tick()

    # ── build ─────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 12, 20, 12)
        root.setSpacing(8)

        # top bar
        topbar = QFrame()
        topbar.setObjectName("topbar")
        tb = QHBoxLayout(topbar)
        tb.setContentsMargins(14, 8, 14, 8)
        title = QLabel("صندوق فروش  —  OTC")
        title.setObjectName("page-title")
        tb.addWidget(title)
        tb.addStretch()
        new_drug_btn = QPushButton("➕  دارو جدید")
        new_drug_btn.setStyleSheet(
            "QPushButton { background:#2563eb; color:white; border:none; border-radius:6px;"
            " font-size:12px; padding:0 14px; min-height:30px; }"
            "QPushButton:hover { background:#1d4ed8; }"
        )
        new_drug_btn.clicked.connect(lambda: self._open_medicine_dialog(None))
        tb.addWidget(new_drug_btn)
        tb.addSpacing(12)
        self.lbl_doc = QLabel()
        self.lbl_doc.setObjectName("doc-info")
        tb.addWidget(self.lbl_doc)
        tb.addSpacing(16)
        self.lbl_clock = QLabel()
        self.lbl_clock.setStyleSheet("font-size: 13px; font-weight: bold; color: #374151;")
        tb.addWidget(self.lbl_clock)
        root.addWidget(topbar)

        hint = QLabel(
            "↵ Enter = تأیید دارو / سطر بعد  ·  ↑↓ = انتخاب از لیست  ·  "
            "Delete = حذف سطر  ·  F12 = صدور فیش"
        )
        hint.setObjectName("hint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint)

        # table — LTR so drug name inputs stay LTR
        self._table = QTableWidget()
        self._table.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(
            ["#", "Drug Name", "Qty", "Unit Price (Rial)", "Total (Rial)"]
        )
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.cellDoubleClicked.connect(self._on_row_double_clicked)
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(2, 70)
        self._table.setColumnWidth(3, 140)
        self._table.setColumnWidth(4, 140)
        root.addWidget(self._table)

        # footer
        footer = QHBoxLayout()
        clear_btn = QPushButton("🗑  پاک کردن")
        clear_btn.setObjectName("clear-btn")
        clear_btn.clicked.connect(self._clear)
        footer.addWidget(clear_btn)
        footer.addStretch()
        self.lbl_total = QLabel("جمع کل:  ۰ ریال")
        self.lbl_total.setObjectName("total-lbl")
        footer.addWidget(self.lbl_total)
        submit_btn = QPushButton("✅  صدور فیش  (F12)")
        submit_btn.setObjectName("submit-btn")
        submit_btn.clicked.connect(self._submit)
        footer.addWidget(submit_btn)
        root.addLayout(footer)

        self._update_doc_label()
        self._add_entry_row()

    # ── clock ─────────────────────────────────────────────
    def _tick(self):
        self.lbl_clock.setText(datetime.now().strftime("%H:%M:%S"))

    def _update_doc_label(self):
        self.lbl_doc.setText(
            f"سند:  {self._doc_number}    تاریخ:  {datetime.now().strftime('%Y/%m/%d')}"
        )

    # ── medicines / debounce search ───────────────────────
    def _on_text_changed(self, row: int, text: str):
        inp = self._table.cellWidget(row, 1)
        if not isinstance(inp, DrugInput) or inp.isReadOnly():
            return
        t = text.strip()
        if len(t) < 2:
            self._popup.hide()
            self._search_timer.stop()
            return
        self._pending_search = (row, t)
        self._search_timer.start(280)

    def _do_search(self):
        row, text = self._pending_search
        inp = self._table.cellWidget(row, 1)
        if not isinstance(inp, DrugInput) or inp.isReadOnly():
            return
        try:
            results = search_medicines(q=text)
        except Exception:
            results = []
        if results:
            self._popup._current_row = row
            self._popup.show_for(results, inp, row)
        else:
            self._popup.hide()

    # ── row management ────────────────────────────────────
    def _add_entry_row(self):
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setRowHeight(row, 34)

        num = QTableWidgetItem(str(row + 1))
        num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        num.setForeground(QColor("#94a3b8"))
        self._table.setItem(row, 0, num)

        inp = DrugInput()
        inp.setStyleSheet(_INPUT_NORMAL)
        inp.textChanged.connect(lambda txt, r=row: self._on_text_changed(r, txt))
        inp.enter_hit.connect(lambda r=row: self._on_enter(r))
        inp.unlock_requested.connect(lambda r=row: self._unlock_row(r))
        self._table.setCellWidget(row, 1, inp)

        for c in (2, 3, 4):
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, c, item)

        QTimer.singleShot(0, inp.setFocus)

    def _on_enter(self, row: int):
        if self._popup.isVisible() and self._popup._current_row == row:
            self._popup.confirm()
            return
        inp = self._table.cellWidget(row, 1)
        if isinstance(inp, DrugInput) and not inp.isReadOnly():
            t = inp.text().strip()
            if len(t) >= 2:
                self._search_timer.stop()
                self._pending_search = (row, t)
                self._do_search()
            elif len(t) == 0 and row > 0:
                # سطر خالی + Enter → برو SpinBox سطر قبلی
                prev_spin = self._table.cellWidget(row - 1, 2)
                if isinstance(prev_spin, QtySpinBox):
                    def _focus():
                        prev_spin.setFocus()
                        prev_spin.lineEdit().selectAll()
                    QTimer.singleShot(0, _focus)

    def _on_drug_selected(self, med: dict):
        row = self._popup._current_row
        self._confirm_row(row, med)

    def _confirm_row(self, row: int, med: dict):
        inp = self._table.cellWidget(row, 1)
        if not isinstance(inp, DrugInput):
            return
        inp.setText(_drug_label(med))
        inp.setReadOnly(True)
        inp.setStyleSheet(_INPUT_LOCKED)
        inp.setProperty("medicine_data", med)
        inp.setProperty("orig_medicine", None)
        inp.setProperty("orig_qty", None)

        default_qty = int(med.get("default_quantity") or 1)
        spin = QtySpinBox()
        spin.setMinimum(1)
        spin.setMaximum(9999)
        spin.setValue(default_qty)
        spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spin.setStyleSheet(
            "QSpinBox { border:1px solid #d1d5db; border-radius:4px; "
            "padding:1px 4px; font-size:13px; font-weight:400; "
            "min-height:26px; background:white; color:#374151; }"
            "QSpinBox:focus { border-color:#2563eb; }"
        )
        spin.valueChanged.connect(lambda v, r=row: self._update_row_total(r))
        spin.enter_hit.connect(lambda r=row: self._finalize_row(r))
        spin.nav_requested.connect(lambda d, r=row: self._navigate_from_spinbox_row(r, d))
        self._table.setCellWidget(row, 2, spin)

        price = float(med.get("sale_price") or 0)
        p_item = self._table.item(row, 3)
        p_item.setText(_fmt(price))
        p_item.setData(Qt.ItemDataRole.UserRole, price)

        self._update_row_total(row)
        def _focus_spin():
            spin.setFocus()
            spin.lineEdit().selectAll()
        QTimer.singleShot(50, _focus_spin)

    def _on_row_double_clicked(self, row: int, col: int):
        inp = self._table.cellWidget(row, 1)
        if isinstance(inp, DrugInput) and inp.isReadOnly():
            med = inp.property("medicine_data")
            if med:
                self._open_medicine_dialog(med, row)

    def _open_medicine_dialog(self, med: dict | None, row: int = -1):
        dlg = MedicineDialog(med, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_medicine:
            updated = dlg.result_medicine
            if row >= 0:
                inp = self._table.cellWidget(row, 1)
                if isinstance(inp, DrugInput):
                    inp.setText(_drug_label(updated))
                    inp.setProperty("medicine_data", updated)
                    price = float(updated.get("sale_price") or 0)
                    p_item = self._table.item(row, 3)
                    if p_item:
                        p_item.setText(_fmt(price))
                        p_item.setData(Qt.ItemDataRole.UserRole, price)
                    self._update_row_total(row)

    def _finalize_row(self, row: int):
        self._update_row_total(row)
        # اگه آخرین سطر هنوز خالی است، فقط focus بده — سطر جدید اضافه نکن
        last = self._table.rowCount() - 1
        last_inp = self._table.cellWidget(last, 1)
        if isinstance(last_inp, DrugInput) and not last_inp.isReadOnly():
            QTimer.singleShot(0, last_inp.setFocus)
        else:
            self._add_entry_row()

    def _unlock_row(self, row: int):
        """کاربر روی نام دارویِ تأییدشده کلیک کرد — سطر را برای ویرایش مجدد باز کن."""
        inp = self._table.cellWidget(row, 1)
        if not isinstance(inp, DrugInput):
            return
        orig_med = inp.property("medicine_data")
        spin = self._table.cellWidget(row, 2)
        orig_qty = spin.value() if isinstance(spin, QtySpinBox) else None
        self._popup.hide()
        inp.setReadOnly(False)
        inp.setStyleSheet(_INPUT_NORMAL)
        inp.setProperty("medicine_data", None)
        inp.setProperty("orig_medicine", orig_med)
        inp.setProperty("orig_qty", orig_qty)
        # متن را نگه می‌داریم، فقط انتخاب می‌کنیم تا کاربر بتونه جایگزین کنه
        def _sel():
            inp.setFocus()
            inp.selectAll()
        QTimer.singleShot(0, _sel)

    def _find_row_for_col(self, widget, col: int) -> int:
        for r in range(self._table.rowCount()):
            if self._table.cellWidget(r, col) is widget:
                return r
        return -1

    def _go_to_row(self, target: int):
        if target < 0 or target >= self._table.rowCount():
            return
        spin = self._table.cellWidget(target, 2)
        inp = self._table.cellWidget(target, 1)
        if isinstance(spin, QtySpinBox):
            def _f():
                spin.setFocus()
                spin.lineEdit().selectAll()
            QTimer.singleShot(0, _f)
        elif isinstance(inp, DrugInput):
            QTimer.singleShot(0, inp.setFocus)

    def _nav_from_input(self, inp: DrugInput, direction: int):
        row = self._find_row_for_col(inp, 1)
        if row < 0:
            return
        if inp.property("orig_medicine") is not None:
            # سطر باز شده بود ولی دارو جدید تأیید نشد — بازگردانی خودکار
            self._restore_row_from_input(inp)
            QTimer.singleShot(60, lambda: self._go_to_row(row + direction))
        else:
            self._go_to_row(row + direction)

    def _navigate_from_spinbox_row(self, row: int, direction: int):
        # اگه نام دارو در همان سطر باز مانده، قبل از رفتن بازگردانی کن
        inp = self._table.cellWidget(row, 1)
        if isinstance(inp, DrugInput) and inp.property("orig_medicine") is not None:
            self._restore_row_from_input(inp)
            QTimer.singleShot(60, lambda: self._go_to_row(row + direction))
        else:
            self._go_to_row(row + direction)

    def _restore_row_from_input(self, inp: DrugInput):
        row = self._find_row_for_col(inp, 1)
        if row < 0:
            return
        orig_med = inp.property("orig_medicine")
        orig_qty = inp.property("orig_qty")
        if orig_med is not None:
            self._confirm_row(row, orig_med)
            if orig_qty is not None:
                spin = self._table.cellWidget(row, 2)
                if isinstance(spin, QtySpinBox):
                    spin.setValue(orig_qty)

    def _update_row_total(self, row: int):
        spin = self._table.cellWidget(row, 2)
        p = self._table.item(row, 3)
        t = self._table.item(row, 4)
        if not isinstance(spin, QSpinBox) or not p or not t:
            return
        price = p.data(Qt.ItemDataRole.UserRole) or 0
        total = spin.value() * price
        t.setText(_fmt(total))
        t.setForeground(QColor("#16a34a"))
        t.setData(Qt.ItemDataRole.UserRole, total)
        self._recalc_total()

    def _recalc_total(self):
        grand = sum(
            (self._table.item(r, 4).data(Qt.ItemDataRole.UserRole) or 0)
            for r in range(self._table.rowCount())
            if self._table.item(r, 4)
        )
        self.lbl_total.setText(f"جمع کل:  {_fmt(grand)} ریال")

    def _delete_selected_rows(self):
        rows = sorted(
            {idx.row() for idx in self._table.selectedIndexes()},
            reverse=True,
        )
        for r in rows:
            inp = self._table.cellWidget(r, 1)
            if isinstance(inp, DrugInput) and not inp.isReadOnly() and self._table.rowCount() == 1:
                continue
            self._table.removeRow(r)
        for r in range(self._table.rowCount()):
            n = self._table.item(r, 0)
            if n:
                n.setText(str(r + 1))
        last = self._table.cellWidget(self._table.rowCount() - 1, 1) if self._table.rowCount() else None
        if not isinstance(last, DrugInput) or last.isReadOnly():
            self._add_entry_row()
        self._recalc_total()

    def _clear(self, confirm: bool = True):
        if confirm and self._table.rowCount() > 1:
            if QMessageBox.question(
                self, "پاک کردن", "سفارش فعلی پاک شود؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            ) != QMessageBox.StandardButton.Yes:
                return
        self._popup.hide()
        self._table.setRowCount(0)
        self.lbl_total.setText("جمع کل:  ۰ ریال")
        self._doc_number = _now_doc()
        self._update_doc_label()
        self._add_entry_row()

    # ── keys ──────────────────────────────────────────────
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_F12:
            self._submit()
        elif event.key() in (Qt.Key.Key_Delete,):
            self._delete_selected_rows()
        else:
            super().keyPressEvent(event)

    # ── submit ────────────────────────────────────────────
    def _submit(self):
        items = []
        for r in range(self._table.rowCount()):
            inp = self._table.cellWidget(r, 1)
            spin = self._table.cellWidget(r, 2)
            p = self._table.item(r, 3)
            if not isinstance(inp, DrugInput) or not inp.isReadOnly():
                continue
            med = inp.property("medicine_data")
            if not med or not isinstance(spin, QSpinBox) or not p:
                continue
            price = p.data(Qt.ItemDataRole.UserRole) or 0
            if price <= 0:
                QMessageBox.warning(self, "خطا", f"قیمت «{_drug_label(med)}» تعریف نشده.")
                return
            items.append({
                "medicine_id": med["id"],
                "quantity": spin.value(),
                "unit_price": price,
            })

        if not items:
            QMessageBox.warning(self, "خطا", "هیچ دارویی اضافه نشده است.")
            return

        try:
            result = create_sale({"sale_number": self._doc_number, "items": items})
            ReceiptDialog(result, self).exec()
            self._clear(confirm=False)
        except requests.HTTPError as e:
            status = e.response.status_code if e.response else 0
            try:
                detail = e.response.json().get("detail", str(e))
            except Exception:
                detail = str(e)
            if status == 400:
                if "تکراری" in detail or "duplicate" in detail.lower():
                    QMessageBox.critical(self, "خطا", "شماره سند تکراری.")
                    self._doc_number = _now_doc()
                    self._update_doc_label()
                else:
                    QMessageBox.critical(self, "خطا", detail)
            elif status == 500:
                QMessageBox.critical(self, "خطای سرور", detail)
            else:
                QMessageBox.critical(self, "خطا", detail)
        except Exception as e:
            QMessageBox.critical(self, "خطا", str(e))
