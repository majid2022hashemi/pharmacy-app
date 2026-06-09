from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QApplication,
    QMessageBox,
    QStackedWidget,
)
from PyQt6.QtCore import Qt, QTimer

import requests
from api.auth_api import login, reset_password, check_username
from session import Session

STYLE = """
QDialog {
    background-color: #f0f2f5;
}
QFrame#card {
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #dde1e7;
}
QLabel#title {
    color: #1a73e8;
    font-size: 15px;
    font-weight: bold;
}
QLabel#subtitle {
    color: #6b7280;
    font-size: 11px;
}
QLabel.field-label {
    color: #374151;
    font-size: 11px;
    font-weight: bold;
}
QLineEdit {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
    background: #f9fafb;
    color: #111827;
}
QLineEdit:focus {
    border: 1px solid #1a73e8;
    background: #ffffff;
}
QPushButton#login-btn {
    background-color: #1a73e8;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    padding: 8px;
}
QPushButton#login-btn:hover {
    background-color: #1558b0;
}
QPushButton#login-btn:disabled {
    background-color: #93c5fd;
}
QPushButton#secondary-btn {
    background-color: #6b7280;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    padding: 7px;
}
QPushButton#secondary-btn:hover {
    background-color: #4b5563;
}
QLabel#error {
    color: #dc2626;
    font-size: 11px;
}
QLabel#success {
    color: #16a34a;
    font-size: 11px;
}
QPushButton#forgot-btn {
    background: transparent;
    border: none;
    color: #6b7280;
    font-size: 10px;
    text-decoration: underline;
    padding: 0;
}
QPushButton#forgot-btn:hover {
    color: #1a73e8;
}
"""

_WIN_FLAGS = (
    Qt.WindowType.Dialog
    | Qt.WindowType.WindowCloseButtonHint
    | Qt.WindowType.WindowTitleHint
)


def _make_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("color: #374151; font-size: 11px; font-weight: bold;")
    return lbl


def _make_input(placeholder: str, password: bool = False) -> QLineEdit:
    inp = QLineEdit()
    inp.setPlaceholderText(placeholder)
    inp.setFixedHeight(34)
    if password:
        inp.setEchoMode(QLineEdit.EchoMode.Password)
    return inp


_S_NORMAL = "QFrame#pass_box { border: 1px solid #d1d5db; border-radius: 6px; background: #f9fafb; }"
_S_FOCUS  = "QFrame#pass_box { border: 1px solid #1a73e8; border-radius: 6px; background: #ffffff; }"
_E_BASE   = "QPushButton { border: none; background: transparent; font-size: 13px; color: "
_E_LOCK   = _E_BASE + "#c0c4cc; } QPushButton:hover { color: #6b7280; }"
_E_DIM    = _E_BASE + "#9ca3af; } QPushButton:hover { color: #1a73e8; }"
_E_BRIGHT = _E_BASE + "#1a73e8; } QPushButton:hover { color: #1558b0; }"


def _make_password_row(placeholder: str) -> tuple[QFrame, QLineEdit]:
    """فیلد رمز با دکمه 👁 سه حالته داخل textbox"""
    container = QFrame()
    container.setObjectName("pass_box")
    container.setFixedHeight(34)
    container.setStyleSheet(_S_NORMAL)

    row = QHBoxLayout(container)
    row.setContentsMargins(0, 0, 6, 0)
    row.setSpacing(0)

    inp = QLineEdit()
    inp.setPlaceholderText(placeholder)
    inp.setEchoMode(QLineEdit.EchoMode.Password)
    inp.setStyleSheet(
        "QLineEdit { border: none; background: transparent; padding: 0 8px;"
        " font-size: 12px; color: #111827; }"
        "QLineEdit:focus { border: none; background: transparent; }"
    )
    row.addWidget(inp)

    eye_btn = QPushButton("🔒")
    eye_btn.setFixedSize(24, 24)
    eye_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    eye_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    eye_btn.setStyleSheet(_E_LOCK)
    row.addWidget(eye_btn)

    _visible = [False]

    def _update():
        focused = inp.hasFocus()
        if _visible[0]:
            eye_btn.setText("👁")
            eye_btn.setStyleSheet(_E_BRIGHT)
        elif focused:
            eye_btn.setText("👁")
            eye_btn.setStyleSheet(_E_DIM)
        else:
            eye_btn.setText("🔒")
            eye_btn.setStyleSheet(_E_LOCK)

    def _focus_in(e):
        container.setStyleSheet(_S_FOCUS)
        QLineEdit.focusInEvent(inp, e)
        _update()

    def _focus_out(e):
        container.setStyleSheet(_S_NORMAL)
        _visible[0] = False
        inp.setEchoMode(QLineEdit.EchoMode.Password)
        QLineEdit.focusOutEvent(inp, e)
        _update()

    inp.focusInEvent = _focus_in
    inp.focusOutEvent = _focus_out

    def _click():
        if not inp.hasFocus():
            inp.setFocus()
            return
        _visible[0] = not _visible[0]
        inp.setEchoMode(QLineEdit.EchoMode.Normal if _visible[0] else QLineEdit.EchoMode.Password)
        _update()

    eye_btn.clicked.connect(_click)

    return container, inp


def _normalize_jalali(raw: str) -> str:
    """۱۳۶۱/۰۲/۰۶ یا ۰۶-۰۲-۱۳۶۱ → 1361-02-06"""
    parts = raw.replace("/", "-").split("-")
    if len(parts) != 3:
        return raw
    p0, p1, p2 = parts[0].strip(), parts[1].strip(), parts[2].strip()
    if len(p0) == 4:
        return f"{p0}-{p1.zfill(2)}-{p2.zfill(2)}"
    if len(p2) == 4:
        return f"{p2}-{p1.zfill(2)}-{p0.zfill(2)}"
    return raw


# ──────────────────────────────────────────────
class ResetPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("بازنشانی رمز عبور")
        self.setWindowFlags(_WIN_FLAGS)
        self.setFixedSize(340, 460)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(STYLE)
        self._verified_username = None
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(0)

        self._title = QLabel("بازنشانی رمز عبور")
        self._title.setObjectName("title")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self._title)

        card_layout.addSpacing(4)

        self._subtitle = QLabel("نام کاربری خود را وارد کنید")
        self._subtitle.setObjectName("subtitle")
        self._subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._subtitle.setWordWrap(True)
        card_layout.addWidget(self._subtitle)

        card_layout.addSpacing(12)

        # ── QStackedWidget ──
        self._stack = QStackedWidget()
        card_layout.addWidget(self._stack)

        # صفحه ۱: نام کاربری
        page1 = QFrame()
        p1 = QVBoxLayout(page1)
        p1.setContentsMargins(0, 0, 0, 0)
        p1.setSpacing(8)

        p1.addWidget(_make_label("نام کاربری"))
        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("نام کاربری")
        self.inp_username.setFixedHeight(34)
        self.inp_username.returnPressed.connect(self._check_user)
        p1.addWidget(self.inp_username)

        self._btn_check = QPushButton("بررسی کاربر")
        self._btn_check.setObjectName("login-btn")
        self._btn_check.setFixedHeight(38)
        self._btn_check.clicked.connect(self._check_user)
        p1.addWidget(self._btn_check)
        p1.addStretch()

        self._stack.addWidget(page1)

        # صفحه ۲: اطلاعات هویتی + رمز جدید
        page2 = QFrame()
        p2 = QVBoxLayout(page2)
        p2.setContentsMargins(0, 0, 0, 0)
        p2.setSpacing(8)

        p2.addWidget(_make_label("کد ملی"))
        self.inp_national_id = _make_input("۱۰ رقم بدون خط تیره")
        p2.addWidget(self.inp_national_id)

        p2.addWidget(_make_label("تاریخ تولد (شمسی)"))
        self.inp_birth_date = _make_input("مثال: ۱۳۶۱/۰۲/۰۶")
        p2.addWidget(self.inp_birth_date)

        p2.addWidget(_make_label("رمز عبور جدید"))
        box1, self.inp_new_pass = _make_password_row("حداقل ۶ کاراکتر")
        p2.addWidget(box1)

        p2.addWidget(_make_label("تکرار رمز عبور"))
        box2, self.inp_confirm_pass = _make_password_row("تکرار رمز عبور")
        p2.addWidget(box2)

        btn_row = QHBoxLayout()
        self._btn_back = QPushButton("بازگشت")
        self._btn_back.setObjectName("secondary-btn")
        self._btn_back.setFixedHeight(36)
        self._btn_back.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        btn_row.addWidget(self._btn_back)

        self._btn_reset = QPushButton("تغییر رمز")
        self._btn_reset.setObjectName("login-btn")
        self._btn_reset.setFixedHeight(36)
        self._btn_reset.clicked.connect(self._do_reset)
        btn_row.addWidget(self._btn_reset)
        p2.addLayout(btn_row)

        self._stack.addWidget(page2)

        # ── خطا ──
        card_layout.addSpacing(8)
        self._error_label = QLabel("")
        self._error_label.setObjectName("error")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.setWordWrap(True)
        self._error_label.setFixedHeight(32)
        card_layout.addWidget(self._error_label)

        outer.addWidget(card)

    def _check_user(self):
        username = self.inp_username.text().strip()
        if not username:
            self._error_label.setText("نام کاربری را وارد کنید")
            return
        self._btn_check.setEnabled(False)
        self._btn_check.setText("در حال بررسی...")
        self._error_label.setText("")
        try:
            if not check_username(username):
                self._error_label.setText("کاربری با این نام یافت نشد")
                return
            self._verified_username = username
            self._subtitle.setText(f"اطلاعات هویتی «{username}» را وارد کنید")
            self._stack.setCurrentIndex(1)
            self._error_label.setText("")
        except requests.ConnectionError:
            self._error_label.setText("اتصال به سرور برقرار نشد")
        except Exception:
            self._error_label.setText("خطای غیرمنتظره رخ داد")
        finally:
            self._btn_check.setEnabled(True)
            self._btn_check.setText("بررسی کاربر")

    def _do_reset(self):
        national_id = self.inp_national_id.text().strip()
        birth_date_raw = self.inp_birth_date.text().strip()
        new_pass = self.inp_new_pass.text()
        confirm = self.inp_confirm_pass.text()

        if not all([national_id, birth_date_raw, new_pass, confirm]):
            self._error_label.setText("همه فیلدها را پر کنید")
            return
        if len(national_id) != 10 or not national_id.isdigit():
            self._error_label.setText("کد ملی باید ۱۰ رقم باشد")
            return
        if new_pass != confirm:
            self._error_label.setText("رمز عبور و تکرار آن یکسان نیستند")
            return
        if len(new_pass) < 6:
            self._error_label.setText("رمز عبور باید حداقل ۶ کاراکتر باشد")
            return

        birth_date = _normalize_jalali(birth_date_raw)
        try:
            reset_password(self._verified_username, national_id, birth_date, new_pass)
            QMessageBox.information(self, "موفق", "رمز عبور با موفقیت تغییر کرد.")
            self.accept()
        except requests.HTTPError as e:
            if e.response.status_code == 400:
                self._error_label.setText("کد ملی یا تاریخ تولد صحیح نیست")
            else:
                self._error_label.setText("خطا در ارتباط با سرور")
        except requests.ConnectionError:
            self._error_label.setText("اتصال به سرور برقرار نشد")
        except Exception:
            self._error_label.setText("خطای غیرمنتظره رخ داد")


# ──────────────────────────────────────────────
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ورود به سیستم")
        self.setWindowFlags(_WIN_FLAGS)
        self.setFixedSize(320, 380)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(STYLE)
        self._build_ui()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._do_center)

    def _do_center(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.x() + (screen.width() - self.width()) // 2
        self.move(x, screen.y() + 60)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(10)

        title = QLabel("داروخانه")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("ورود به سیستم ")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        layout.addWidget(_make_label("نام کاربری"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری")
        self.username_input.setFixedHeight(34)
        layout.addWidget(self.username_input)

        layout.addWidget(_make_label("رمز عبور"))
        pass_box, self.password_input = _make_password_row("رمز عبور")
        self.password_input.returnPressed.connect(self._do_login)
        layout.addWidget(pass_box)

        self.username_input.returnPressed.connect(self.password_input.setFocus)

        self.error_label = QLabel("")
        self.error_label.setObjectName("error")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setFixedHeight(18)
        layout.addWidget(self.error_label)

        self.login_btn = QPushButton("ورود")
        self.login_btn.setObjectName("login-btn")
        self.login_btn.setFixedHeight(38)
        self.login_btn.clicked.connect(self._do_login)
        layout.addWidget(self.login_btn)

        forgot_btn = QPushButton("رمز عبور را فراموش کرده‌اید؟")
        forgot_btn.setObjectName("forgot-btn")
        forgot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_btn.clicked.connect(self._show_forgot)
        layout.addWidget(forgot_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        outer.addWidget(card)

    def _show_forgot(self):
        ResetPasswordDialog(self).exec()

    def _do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.error_label.setText("نام کاربری و رمز عبور را وارد کنید")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("در حال ورود...")
        self.error_label.setText("")

        try:
            result = login(username, password)
            Session.set(result["access_token"], result["user"])
            self.accept()
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                self.error_label.setText("نام کاربری یا رمز عبور اشتباه است")
            elif e.response.status_code == 403:
                self.error_label.setText("حساب کاربری غیرفعال است")
            else:
                self.error_label.setText("خطا در ارتباط با سرور")
        except requests.ConnectionError:
            self.error_label.setText("اتصال به سرور برقرار نشد")
        except Exception:
            self.error_label.setText("خطای غیرمنتظره رخ داد")
        finally:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("ورود")
