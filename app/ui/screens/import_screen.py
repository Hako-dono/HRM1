from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.import_service import ImportErrorMessage, ImportService


class ImportScreen(QWidget):
    def __init__(self, import_service: ImportService) -> None:
        super().__init__()
        self.import_service = import_service
        self.payroll_path = QLineEdit()
        self.employee_path = QLineEdit()
        self.manual_month = QLineEdit()
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Import dữ liệu")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        root.addWidget(title)

        form = QFormLayout()

        pay_row = QHBoxLayout()
        pay_btn = QPushButton("Chọn file payroll")
        pay_btn.clicked.connect(self._pick_payroll)
        pay_row.addWidget(self.payroll_path, 1)
        pay_row.addWidget(pay_btn)

        emp_row = QHBoxLayout()
        emp_btn = QPushButton("Chọn file employee")
        emp_btn.clicked.connect(self._pick_employee)
        emp_row.addWidget(self.employee_path, 1)
        emp_row.addWidget(emp_btn)

        form.addRow("Payroll file", pay_row)
        form.addRow("Employee file", emp_row)
        form.addRow("Manual payroll month (YYYY-MM)", self.manual_month)
        root.addLayout(form)

        import_btn = QPushButton("Import & map dữ liệu")
        import_btn.clicked.connect(self._import)
        root.addWidget(import_btn)
        root.addWidget(self.output, 1)

    def _pick_payroll(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Chọn payroll file", "", "Excel Files (*.xlsx *.xlsm)")
        if path:
            self.payroll_path.setText(path)

    def _pick_employee(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Chọn employee file", "", "Excel Files (*.xlsx *.xlsm)")
        if path:
            self.employee_path.setText(path)

    def _import(self) -> None:
        payroll = self.payroll_path.text().strip()
        employee = self.employee_path.text().strip()
        if not payroll or not employee:
            QMessageBox.warning(self, "Thiếu file", "Vui lòng chọn đủ payroll file và employee file.")
            return
        try:
            result = self.import_service.import_files(Path(payroll), Path(employee), self.manual_month.text().strip() or None)
            lines = [
                "Import thành công.",
                f"Session ID: {result.session_id}",
                f"Payroll month: {result.payroll_month}",
            ]
            lines.extend([f"Warning: {w}" for w in result.warnings])
            self.output.setPlainText("\n".join(lines))
        except ImportErrorMessage as ex:
            QMessageBox.critical(self, "Import lỗi", str(ex))
