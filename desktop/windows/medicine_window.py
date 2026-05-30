from PyQt6.QtWidgets import (
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton
)

import requests


BASE_URL = "http://127.0.0.1:8001"


class MedicineWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pharmacy - Medicines")
        self.setGeometry(200, 200, 600, 400)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Quantity"])

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_data)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.refresh_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_data()

    def load_data(self):
        try:
            response = requests.get(f"{BASE_URL}/medicines")
            data = response.json()

            self.table.setRowCount(len(data))

            for row, item in enumerate(data):
                self.table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(item["name"]))
                self.table.setItem(row, 2, QTableWidgetItem(str(item["quantity"])))

        except Exception as e:
            print("Error loading data:", e)