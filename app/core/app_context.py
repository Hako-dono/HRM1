from pathlib import Path

from data.database import Database
from data.settings_repository import SettingsRepository


class AppContext:
    def __init__(self) -> None:
        self.database = Database(Path("app_data/smart_payslip.db"))
        self.database.initialize()
        self.settings_repository = SettingsRepository(self.database)
