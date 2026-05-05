from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from core.import_service import ImportService
from data.preview_repository import PreviewRepository
from data.settings_repository import SettingsRepository
from ui.screens.dashboard_screen import DashboardScreen
from ui.screens.history_screen import HistoryScreen
from ui.screens.import_screen import ImportScreen
from ui.screens.preview_screen import PreviewScreen
from ui.screens.settings_screen import SettingsScreen


class MainWindow(QMainWindow):
    def __init__(self, settings_repository: SettingsRepository, import_service: ImportService, preview_repository: PreviewRepository) -> None:
        super().__init__()
        self.settings_repository = settings_repository
        self.import_service = import_service
        self.preview_repository = preview_repository
        self.setWindowTitle("Smart Payslip")
        self.resize(1280, 800)
        self._setup_ui()

    def _setup_ui(self) -> None:
        central_widget = QWidget(); self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout(central_widget); root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self._create_sidebar())
        self.stack = QStackedWidget()
        self.stack.addWidget(DashboardScreen())
        self.stack.addWidget(ImportScreen(self.import_service))
        self.stack.addWidget(PreviewScreen(self.preview_repository, self.settings_repository))
        self.stack.addWidget(HistoryScreen())
        self.stack.addWidget(SettingsScreen(self.settings_repository))
        root_layout.addWidget(self.stack, 1)

    def _create_sidebar(self) -> QWidget:
        container = QFrame(); container.setFixedWidth(250)
        layout = QVBoxLayout(container)
        title = QLabel("Smart Payslip"); title.setAlignment(Qt.AlignCenter)
        self.nav_list = QListWidget()
        for label in ["Dashboard", "Import dữ liệu", "Preview & chọn gửi", "Lịch sử gửi", "Settings"]:
            QListWidgetItem(label, self.nav_list)
        self.nav_list.setCurrentRow(0); self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        layout.addWidget(title); layout.addWidget(self.nav_list, 1)
        return container
