from pathlib import Path

from core.email_service import EmailService
from core.export_service import ExportService
from core.import_service import ImportService
from core.pdf_service import PdfService
from core.salary_lock_service import SalaryLockService
from data.database import Database
from data.history_repository import HistoryRepository
from data.import_repository import ImportRepository
from data.preview_repository import PreviewRepository
from data.settings_repository import SettingsRepository


class AppContext:
    def __init__(self) -> None:
        self.database = Database(Path("app_data/smart_payslip.db"))
        self.database.initialize()
        self.settings_repository = SettingsRepository(self.database)
        self.salary_lock_service = SalaryLockService(self.settings_repository)
        self.import_repository = ImportRepository(self.database)
        self.import_service = ImportService(self.import_repository)
        self.preview_repository = PreviewRepository(self.database)
        self.pdf_service = PdfService(self.preview_repository, self.settings_repository)
        self.email_service = EmailService(self.settings_repository, self.preview_repository, self.pdf_service)
        self.history_repository = HistoryRepository(self.database)
        self.export_service = ExportService(self.history_repository)
