import sys
import os

os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

from PyQt6.QtWidgets import QApplication
from windows.login_window import LoginWindow
from windows.main_window import MainWindow


app = QApplication(sys.argv)

login = LoginWindow()
if login.exec() != LoginWindow.DialogCode.Accepted:
    sys.exit(0)

window = MainWindow()
window.show()

sys.exit(app.exec())
