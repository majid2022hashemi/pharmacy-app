import sys
from PyQt6.QtWidgets import QApplication
from windows.medicine_window import MedicineWindow


app = QApplication(sys.argv)

window = MedicineWindow()
window.show()

sys.exit(app.exec())