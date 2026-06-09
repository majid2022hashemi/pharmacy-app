from __future__ import annotations

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QSpinBox, QMessageBox, QFrame, QListWidget,
    QListWidgetItem, QAbstractItemView,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QKeyEvent

import requests
from api.medicine_api import search_medicines
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
    return "SAL-" + datetime.now().strftime("%Y%m%d-%H%M%S")


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
    """Floating popup showing filtered drug results."""
    drug_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
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


# ── DrugInput ────────────────────────────────────────────
class DrugInput(QLineEdit):
    enter_hit = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.enter_hit.emit()
        elif event.key() == Qt.Key.Key_Down:
            self.parent_page_down()
        elif event.key() == Qt.Key.Key_Up:
            self.parent_page_up()
        elif event.key() == Qt.Key.Key_Escape:
            self.parent_hide_popup()
        else:
            super().keyPressEvent(event)

    def parent_page_down(self):
        p = self._get_page()
        if p:
            p._popup.move_selection(1)

    def parent_page_up(self):
        p = self._get_page()
        if p:
            p._popup.move_selection(-1)

    def parent_hide_popup(self):
        p = self._get_page()
        if p:
            p._popup.hide()

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
        self._build_ui()
        self._load_medicines()
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
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
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

    # ── medicines ─────────────────────────────────────────
    def _load_medicines(self):
        try:
            self._medicines = search_medicines()
        except Exception:
            self._medicines = []

    def _filter(self, text: str) -> list[dict]:
        t = text.strip().lower()
        if len(t) < 1:
            return []
        return [
            m for m in self._medicines
            if t in _drug_label(m).lower() or t in (m.get("code") or "").lower()
        ]

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
        self._table.setCellWidget(row, 1, inp)

        for c in (2, 3, 4):
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, c, item)

        QTimer.singleShot(0, inp.setFocus)

    def _on_text_changed(self, row: int, text: str):
        inp = self._table.cellWidget(row, 1)
        if not isinstance(inp, DrugInput) or inp.isReadOnly():
            return
        matches = self._filter(text)
        if matches:
            self._popup._current_row = row
            self._popup.show_for(matches, inp, row)
        else:
            self._popup.hide()

    def _on_enter(self, row: int):
        # if popup is visible → confirm from popup
        if self._popup.isVisible() and self._popup._current_row == row:
            self._popup.confirm()
            return
        # else try to match current text
        inp = self._table.cellWidget(row, 1)
        if isinstance(inp, DrugInput) and not inp.isReadOnly():
            matches = self._filter(inp.text())
            if matches:
                self._confirm_row(row, matches[0])

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

        spin = QSpinBox()
        spin.setMinimum(1)
        spin.setMaximum(9999)
        spin.setValue(1)
        spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spin.valueChanged.connect(lambda v, r=row: self._update_row_total(r))
        self._table.setCellWidget(row, 2, spin)

        price = float(med.get("sale_price") or 0)
        p_item = self._table.item(row, 3)
        p_item.setText(_fmt(price))
        p_item.setData(Qt.ItemDataRole.UserRole, price)

        self._update_row_total(row)
        self._add_entry_row()

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
            code = e.response.status_code if e.response else 0
            if code == 400:
                QMessageBox.critical(self, "خطا", "شماره سند تکراری.")
                self._doc_number = _now_doc()
                self._update_doc_label()
            else:
                QMessageBox.critical(self, "خطا", str(e))
        except Exception as e:
            QMessageBox.critical(self, "خطا", str(e))
