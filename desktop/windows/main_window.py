from PyQt6.QtWidgets import QMainWindow, QLabel


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pharmacy Management System")
        self.resize(1000, 700)

        label = QLabel("Pharmacy Management System", self)
        label.move(20, 20)