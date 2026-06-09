from __future__ import annotations

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QMessageBox, QCompleter,
)
from PyQt6.QtCore import Qt, QTimer, QStringListModel
from PyQt6.QtGui import QColor

from api.medicine_api import search_medicines, get_medicine_by_code, get_companies, create_purchase_invoice

# ── نام دارو به فرمت: generic_name dosage_form strength ─────
def _drug_label(med: dict) -> str:
    parts = [
        (med.get("generic_name") or med.get("name") or "").lower(),
        (med.get("dosage_form") or "").lower(),
        (med.get("strength") or ""),
    ]
    return " ".join(p for p in parts if p).strip()


PAGE_STYLE = """
QWidget { font-family: Tahoma, Arial; }
QLabel#page-title { font-size: 18px; font-weight: bold; color: #1e293b; }
QLabel#section-title { font-size: 13px; font-weight: bold; color: #374151; }
QLabel { font-size: 12px; color: #374151; }
QFrame#card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}
QLineEdit, QComboBox {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    background: white;
    color: #111827;
    min-height: 34px;
}
QLineEdit:focus, QComboBox:focus { border-color: #2563eb; }
QLineEdit[readOnly="true"] { background: #f8fafc; color: #64748b; }
QComboBox QAbstractItemView {
    background: white; color: #111827;
    border: 1px solid #d1d5db; border-radius: 4px;
    selection-background-color: #2563eb; selection-color: white;
}
QComboBox QAbstractItemView::item { padding: 6px 12px; min-height: 28px; color: #111827; }
QComboBox QAbstractItemView::item:hover { background: #eff6ff; }
QComboBox QAbstractItemView::item:selected { background: #2563eb; color: white; }
QPushButton#add-btn {
    background: #2563eb; color: white;
    border: none; border-radius: 6px;
    font-size: 13px; font-weight: bold;
    padding: 0 20px; min-height: 36px;
}
QPushButton#add-btn:hover { background: #1d4ed8; }
QPushButton#submit-btn {
    background: #16a34a; color: white;
    border: none; border-radius: 6px;
    font-size: 14px; font-weight: bold;
    padding: 0 30px; min-height: 40px;
}
QPushButton#submit-btn:hover { background: #15803d; }
QPushButton#remove-btn {
    background: #fef2f2; color: #dc2626;
    border: 1px solid #fecaca; border-radius: 5px;
    font-size: 11px; padding: 3px 8px;
}
QPushButton#remove-btn:hover { background: #fee2e2; }
QPushButton#search-btn {
    background: #f1f5f9; color: #374151;
    border: 1px solid #e2e8f0; border-radius: 6px;
    font-size: 12px; padding: 0 14px; min-height: 34px;
}
QPushButton#search-btn:hover { background: #e2e8f0; }
QPushButton#toggle-otc {
    border: 2px solid #2563eb; border-radius: 6px;
    font-size: 12px; font-weight: bold;
    padding: 4px 14px; min-height: 32px;
}
QPushButton#toggle-otc[active="true"]  { background: #2563eb; color: white; }
QPushButton#toggle-otc[active="false"] { background: white;   color: #2563eb; }
QTableWidget {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 8px; gridline-color: #f1f5f9;
    font-size: 13px;
}
QTableWidget::item { padding: 6px 10px; }
QTableWidget::item:selected { background: #eff6ff; color: #1e293b; }
QHeaderView::section {
    background: #f8fafc; border: none;
    border-bottom: 1px solid #e2e8f0;
    padding: 8px 10px; font-size: 12px;
    font-weight: bold; color: #64748b;
}
QLabel#error { color: #dc2626; font-size: 11px; }
QLabel#total-lbl { font-size: 16px; font-weight: bold; color: #1e293b; }
"""


class PurchasePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(PAGE_STYLE)
        self._items: list[dict] = []
        self._otc_mode = True
        self._companies: list[dict] = []
        self._current_med: dict | None = None
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)
        self._build_ui()
        self._load_companies()

    # ── Build ────────────────────────────────────────────────
    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(16)

        # Header row
        hdr = QHBoxLayout()
        title = QLabel("ورود کالا  /  فاکتور خرید")
        title.setObjectName("page-title")
        hdr.addWidget(title)
        hdr.addStretch()

        self._otc_btn = QPushButton("OTC  بدون نسخه")
        self._otc_btn.setObjectName("toggle-otc")
        self._otc_btn.setProperty("active", "true")
        self._otc_btn.setCheckable(False)
        self._otc_btn.clicked.connect(self._toggle_otc)
        hdr.addWidget(self._otc_btn)

        rx_btn = QPushButton("Rx  نسخه‌ای")
        rx_btn.setObjectName("toggle-otc")
        rx_btn.setProperty("active", "false")
        rx_btn.setCheckable(False)
        rx_btn.clicked.connect(self._toggle_rx)
        self._rx_btn = rx_btn
        hdr.addWidget(rx_btn)
        v.addLayout(hdr)

        # Invoice info card
        inv_card = QFrame()
        inv_card.setObjectName("card")
        inv_v = QVBoxLayout(inv_card)
        inv_v.setContentsMargins(16, 12, 16, 12)
        inv_v.setSpacing(10)

        lbl = QLabel("اطلاعات فاکتور")
        lbl.setObjectName("section-title")
        inv_v.addWidget(lbl)

        inv_row = QHBoxLayout()
        inv_row.setSpacing(12)

        inv_row.addWidget(QLabel("شماره فاکتور:"))
        self.inp_invoice = QLineEdit()
        self.inp_invoice.setText(self._auto_invoice_number())
        self.inp_invoice.setFixedWidth(180)
        inv_row.addWidget(self.inp_invoice)

        inv_row.addWidget(QLabel("شرکت / تأمین‌کننده:"))
        self.cmb_company = QComboBox()
        self.cmb_company.setMinimumWidth(200)
        inv_row.addWidget(self.cmb_company)

        inv_row.addStretch()
        inv_v.addLayout(inv_row)
        v.addWidget(inv_card)

        # Drug entry card
        entry_card = QFrame()
        entry_card.setObjectName("card")
        entry_v = QVBoxLayout(entry_card)
        entry_v.setContentsMargins(16, 12, 16, 12)
        entry_v.setSpacing(10)

        lbl2 = QLabel("افزودن دارو به فاکتور")
        lbl2.setObjectName("section-title")
        entry_v.addWidget(lbl2)

        # Row 1: code + name
        r1 = QHBoxLayout()
        r1.setSpacing(10)

        r1.addWidget(QLabel("کد دارو:"))
        self.inp_code = QLineEdit()
        self.inp_code.setPlaceholderText("کد IRC یا کد داخلی")
        self.inp_code.setFixedWidth(150)
        self.inp_code.returnPressed.connect(self._lookup_by_code)
        self.inp_code.textChanged.connect(lambda: self._search_timer.start(400))
        r1.addWidget(self.inp_code)

        srch_btn = QPushButton("🔍 جستجو")
        srch_btn.setObjectName("search-btn")
        srch_btn.clicked.connect(self._lookup_by_code)
        r1.addWidget(srch_btn)

        r1.addWidget(QLabel("نام دارو:"))
        self.inp_name = QLineEdit()
        self.inp_name.setReadOnly(True)
        self.inp_name.setMinimumWidth(250)
        self.inp_name.setPlaceholderText("پس از جستجو، نام دارو نمایش داده می‌شود")
        r1.addWidget(self.inp_name)

        r1.addStretch()
        entry_v.addLayout(r1)

        # Row 2: price + qty + batch + expiry
        r2 = QHBoxLayout()
        r2.setSpacing(10)

        r2.addWidget(QLabel("قیمت واحد (ریال):"))
        self.inp_price = QLineEdit()
        self.inp_price.setPlaceholderText("۰")
        self.inp_price.setFixedWidth(130)
        self.inp_price.textChanged.connect(self._update_total_preview)
        r2.addWidget(self.inp_price)

        r2.addWidget(QLabel("تعداد:"))
        self.inp_qty = QLineEdit("1")
        self.inp_qty.setFixedWidth(70)
        self.inp_qty.textChanged.connect(self._update_total_preview)
        r2.addWidget(self.inp_qty)

        self.lbl_line_total = QLabel("جمع: —")
        self.lbl_line_total.setStyleSheet("font-weight: bold; color: #2563eb; font-size: 13px;")
        r2.addWidget(self.lbl_line_total)

        r2.addSpacing(12)
        r2.addWidget(QLabel("شماره بچ:"))
        self.inp_batch = QLineEdit()
        self.inp_batch.setPlaceholderText("مثال: B2024-01")
        self.inp_batch.setFixedWidth(130)
        r2.addWidget(self.inp_batch)

        r2.addWidget(QLabel("تاریخ انقضا:"))
        self.inp_expiry = QLineEdit()
        self.inp_expiry.setPlaceholderText("YYYY-MM-DD")
        self.inp_expiry.setFixedWidth(120)
        r2.addWidget(self.inp_expiry)

        r2.addStretch()
        entry_v.addLayout(r2)

        # Row 3: error + add button
        r3 = QHBoxLayout()
        self._entry_error = QLabel("")
        self._entry_error.setObjectName("error")
        r3.addWidget(self._entry_error)
        r3.addStretch()
        add_btn = QPushButton("➕  افزودن به فاکتور")
        add_btn.setObjectName("add-btn")
        add_btn.clicked.connect(self._add_item)
        r3.addWidget(add_btn)
        entry_v.addLayout(r3)
        v.addWidget(entry_card)

        # Items table
        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(
            ["کد دارو", "نام دارو", "تعداد", "قیمت واحد", "جمع ردیف", "شماره بچ", "حذف"]
        )
        self._table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        hdr_t = self._table.horizontalHeader()
        hdr_t.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr_t.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr_t.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr_t.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr_t.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        hdr_t.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        hdr_t.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        v.addWidget(self._table)

        # Footer: total + submit
        footer = QHBoxLayout()
        self.lbl_total = QLabel("جمع کل: ۰ ریال")
        self.lbl_total.setObjectName("total-lbl")
        footer.addWidget(self.lbl_total)
        footer.addStretch()

        clear_btn = QPushButton("🗑  پاک کردن فاکتور")
        clear_btn.setObjectName("remove-btn")
        clear_btn.setMinimumHeight(38)
        clear_btn.clicked.connect(self._clear_invoice)
        footer.addWidget(clear_btn)

        submit_btn = QPushButton("✅  ثبت فاکتور خرید")
        submit_btn.setObjectName("submit-btn")
        submit_btn.clicked.connect(self._submit_invoice)
        footer.addWidget(submit_btn)
        v.addLayout(footer)

    # ── Helpers ──────────────────────────────────────────────
    def _auto_invoice_number(self) -> str:
        return "PUR-" + datetime.now().strftime("%Y%m%d-%H%M%S")

    def _format_number(self, n) -> str:
        try:
            return f"{int(n):,}"
        except Exception:
            return str(n)

    def _toggle_otc(self):
        self._otc_mode = True
        self._otc_btn.setProperty("active", "true")
        self._otc_btn.setStyle(self._otc_btn.style())
        self._rx_btn.setProperty("active", "false")
        self._rx_btn.setStyle(self._rx_btn.style())

    def _toggle_rx(self):
        self._otc_mode = False
        self._rx_btn.setProperty("active", "true")
        self._rx_btn.setStyle(self._rx_btn.style())
        self._otc_btn.setProperty("active", "false")
        self._otc_btn.setStyle(self._otc_btn.style())

    def _load_companies(self):
        try:
            self._companies = get_companies()
            self.cmb_company.clear()
            for c in self._companies:
                self.cmb_company.addItem(c["name"], c["id"])
        except Exception:
            self.cmb_company.addItem("— شرکت یافت نشد —", None)

    def _do_search(self):
        code = self.inp_code.text().strip()
        if not code:
            return
        med = get_medicine_by_code(code)
        if med:
            self._current_med = med
            self.inp_name.setText(_drug_label(med))
            price = med.get("sale_price") or ""
            self.inp_price.setText(str(price) if price else "")
            self._entry_error.setText("")

    def _lookup_by_code(self):
        self._search_timer.stop()
        self._do_search()

    def _update_total_preview(self):
        try:
            price = float(self.inp_price.text().replace(",", ""))
            qty = int(self.inp_qty.text())
            total = price * qty
            self.lbl_line_total.setText(f"جمع: {self._format_number(total)} ریال")
        except Exception:
            self.lbl_line_total.setText("جمع: —")

    def _add_item(self):
        self._entry_error.setText("")
        if not self._current_med:
            self._entry_error.setText("ابتدا یک دارو با کد جستجو کنید")
            return
        try:
            price = float(self.inp_price.text().replace(",", ""))
            qty = int(self.inp_qty.text())
        except ValueError:
            self._entry_error.setText("قیمت و تعداد باید عدد باشد")
            return
        if price <= 0 or qty <= 0:
            self._entry_error.setText("قیمت و تعداد باید بزرگ‌تر از صفر باشند")
            return
        batch = self.inp_batch.text().strip()
        expiry = self.inp_expiry.text().strip()
        if not batch:
            self._entry_error.setText("شماره بچ الزامی است")
            return
        if not expiry:
            self._entry_error.setText("تاریخ انقضا الزامی است")
            return

        item = {
            "medicine_id": self._current_med["id"],
            "code": self._current_med["code"],
            "name": _drug_label(self._current_med),
            "quantity": qty,
            "unit_price": price,
            "batch_number": batch,
            "expiry_date": expiry,
        }
        self._items.append(item)
        self._refresh_table()
        self._clear_entry_form()

    def _refresh_table(self):
        self._table.setRowCount(0)
        grand_total = 0
        for i, item in enumerate(self._items):
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 40)
            line_total = item["quantity"] * item["unit_price"]
            grand_total += line_total
            self._table.setItem(row, 0, QTableWidgetItem(item["code"]))
            self._table.setItem(row, 1, QTableWidgetItem(item["name"]))
            self._table.setItem(row, 2, QTableWidgetItem(str(item["quantity"])))
            self._table.setItem(row, 3, QTableWidgetItem(self._format_number(item["unit_price"])))
            total_item = QTableWidgetItem(self._format_number(line_total))
            total_item.setForeground(QColor("#16a34a"))
            self._table.setItem(row, 4, total_item)
            self._table.setItem(row, 5, QTableWidgetItem(item["batch_number"]))

            del_btn = QPushButton("🗑 حذف")
            del_btn.setObjectName("remove-btn")
            del_btn.clicked.connect(lambda _, idx=i: self._remove_item(idx))
            w = QWidget()
            h = QHBoxLayout(w)
            h.setContentsMargins(4, 4, 4, 4)
            h.addWidget(del_btn)
            self._table.setCellWidget(row, 6, w)

        self.lbl_total.setText(f"جمع کل: {self._format_number(grand_total)} ریال")

    def _remove_item(self, idx: int):
        if 0 <= idx < len(self._items):
            self._items.pop(idx)
            self._refresh_table()

    def _clear_entry_form(self):
        self._current_med = None
        self.inp_code.clear()
        self.inp_name.clear()
        self.inp_price.clear()
        self.inp_qty.setText("1")
        self.inp_batch.clear()
        self.inp_expiry.clear()
        self.lbl_line_total.setText("جمع: —")
        self.inp_code.setFocus()

    def _clear_invoice(self):
        if self._items:
            reply = QMessageBox.question(
                self, "پاک کردن فاکتور",
                "آیا از پاک کردن تمام ردیف‌های فاکتور مطمئن هستید؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self._items.clear()
        self._refresh_table()
        self._clear_entry_form()
        self.inp_invoice.setText(self._auto_invoice_number())

    def _submit_invoice(self):
        if not self._items:
            QMessageBox.warning(self, "خطا", "فاکتور خالی است. ابتدا داروها را اضافه کنید.")
            return
        invoice_number = self.inp_invoice.text().strip()
        if not invoice_number:
            QMessageBox.warning(self, "خطا", "شماره فاکتور الزامی است.")
            return
        company_id = self.cmb_company.currentData()
        if not company_id:
            QMessageBox.warning(self, "خطا", "لطفاً شرکت / تأمین‌کننده را انتخاب کنید.")
            return

        payload = {
            "invoice_number": invoice_number,
            "company_id": company_id,
            "items": [
                {
                    "medicine_id": it["medicine_id"],
                    "quantity": it["quantity"],
                    "unit_price": it["unit_price"],
                    "batch_number": it["batch_number"],
                    "expiry_date": it["expiry_date"],
                }
                for it in self._items
            ],
        }
        try:
            result = create_purchase_invoice(payload)
            QMessageBox.information(
                self, "موفق",
                f"فاکتور شماره {result.get('invoice_number', '')} با موفقیت ثبت شد.\n"
                f"جمع کل: {self._format_number(result.get('total_amount', 0))} ریال",
            )
            self._items.clear()
            self._refresh_table()
            self._clear_entry_form()
            self.inp_invoice.setText(self._auto_invoice_number())
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ثبت فاکتور:\n{e}")
