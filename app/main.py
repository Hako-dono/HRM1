import sys
from PySide6.QtWidgets import QApplication
from core.app_context import AppContext
from ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Smart Payslip")
    c = AppContext()
    app.installEventFilter(c.salary_lock_service)
    w = MainWindow(c.settings_repository, c.import_service, c.preview_repository, c.pdf_service, c.email_service, c.history_repository, c.salary_lock_service, c.export_service)
    w.showFullScreen()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
