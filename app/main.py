# import sys
# from PySide6.QtWidgets import QApplication

# from ui.main_window import MainWindow


# def main() -> int:
#     app = QApplication(sys.argv)
#     app.setApplicationName("Smart Payslip")

#     window = MainWindow()
#     window.showMaximized()

#     return app.exec()


# if __name__ == "__main__":
#     raise SystemExit(main())

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Payslip")
        self.resize(1200, 800)
        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self._create_pages()

        sidebar = self._create_sidebar()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)

        self.setCentralWidget(central_widget)

    def _create_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(240)

        layout = QVBoxLayout(sidebar)

        title = QLabel("Smart Payslip")
        title.setAlignment(Qt.AlignCenter)

        self.nav_list = QListWidget()
        items = [
            "Dashboard",
            "Import dữ liệu",
            "Preview & chọn gửi",
            "Lịch sử gửi",
            "Settings",
        ]

        for item in items:
            self.nav_list.addItem(QListWidgetItem(item))

        self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav_list.setCurrentRow(0)

        layout.addWidget(title)
        layout.addWidget(self.nav_list)

        return sidebar

    def _create_pages(self):
        pages = [
            "Dashboard",
            "Import dữ liệu",
            "Preview & chọn gửi",
            "Lịch sử gửi",
            "Settings",
        ]

        for page_name in pages:
            page = QWidget()
            layout = QVBoxLayout(page)

            label = QLabel(page_name)
            label.setAlignment(Qt.AlignCenter)

            layout.addWidget(label)
            self.stack.addWidget(page)
