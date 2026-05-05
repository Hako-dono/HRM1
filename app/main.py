import sys
from PySide6.QtWidgets import QApplication
from core.app_context import AppContext
from ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Smart Payslip")
    c = AppContext()
    w = MainWindow(c.settings_repository, c.import_service, c.preview_repository, c.pdf_service, c.email_service)
    w.showFullScreen()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
