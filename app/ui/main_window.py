from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from core.email_service import EmailService
from core.import_service import ImportService
from core.pdf_service import PdfService
from data.preview_repository import PreviewRepository
from data.settings_repository import SettingsRepository
from ui.screens.dashboard_screen import DashboardScreen
from ui.screens.history_screen import HistoryScreen
from ui.screens.import_screen import ImportScreen
from ui.screens.preview_screen import PreviewScreen
from ui.screens.settings_screen import SettingsScreen


class MainWindow(QMainWindow):
    def __init__(self, settings_repository: SettingsRepository, import_service: ImportService, preview_repository: PreviewRepository, pdf_service: PdfService, email_service: EmailService) -> None:
        super().__init__()
        self.setWindowTitle("Smart Payslip")
        self.resize(1280, 800)
        self._setup_ui(settings_repository, import_service, preview_repository, pdf_service, email_service)

    def _setup_ui(self, settings_repository, import_service, preview_repository, pdf_service, email_service) -> None:
        cw = QWidget(); self.setCentralWidget(cw)
        root = QHBoxLayout(cw); root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._create_sidebar())
        self.stack = QStackedWidget()
        self.stack.addWidget(DashboardScreen())
        self.stack.addWidget(ImportScreen(import_service))
        self.stack.addWidget(PreviewScreen(preview_repository, settings_repository, pdf_service, email_service))
        self.stack.addWidget(HistoryScreen())
        self.stack.addWidget(SettingsScreen(settings_repository, email_service))
        root.addWidget(self.stack, 1)

    def _create_sidebar(self) -> QWidget:
        container = QFrame(); container.setFixedWidth(250)
        layout = QVBoxLayout(container)
        title = QLabel("Smart Payslip"); title.setAlignment(Qt.AlignCenter)
        self.nav_list = QListWidget()
        for label in ["Dashboard", "Import dữ liệu", "Preview & chọn gửi", "Lịch sử gửi", "Settings"]: QListWidgetItem(label, self.nav_list)
        self.nav_list.setCurrentRow(0); self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        layout.addWidget(title); layout.addWidget(self.nav_list, 1)
        return container
