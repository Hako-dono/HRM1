from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.salary_lock_service import SalaryLockService


class DashboardScreen(QWidget):
    def __init__(self, lock_service: SalaryLockService) -> None:
        super().__init__()
        self.lock_service = lock_service
        layout = QVBoxLayout(self)
        self.title = QLabel("Dashboard")
        self.salary_stats = QLabel()
        layout.addWidget(self.title)
        layout.addWidget(self.salary_stats)
        self.lock_service.lock_changed.connect(self.refresh)
        self.refresh(self.lock_service.is_locked())

    def refresh(self, locked: bool) -> None:
        self.salary_stats.setText("Salary stats: ********" if locked else "Salary stats: (hiển thị theo phiên gửi)")
