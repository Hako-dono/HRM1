from pathlib import Path

from core.import_service import ImportService
from data.database import Database
from data.import_repository import ImportRepository
from data.settings_repository import SettingsRepository


class AppContext:
    def __init__(self) -> None:
        self.database = Database(Path("app_data/smart_payslip.db"))
        self.database.initialize()
        self.settings_repository = SettingsRepository(self.database)
        self.import_repository = ImportRepository(self.database)
        self.import_service = ImportService(self.import_repository)
