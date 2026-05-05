import sys
from PySide6.QtWidgets import QApplication

from core.app_context import AppContext
from ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Smart Payslip")
    app_context = AppContext()
    window = MainWindow(app_context.settings_repository, app_context.import_service, app_context.preview_repository, app_context.pdf_service)
    window.showFullScreen()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
