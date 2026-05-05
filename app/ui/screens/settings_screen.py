from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from data.settings_repository import SettingsData, SettingsRepository


class SettingsScreen(QWidget):
    def __init__(self, settings_repository: SettingsRepository) -> None:
        super().__init__()
        self.settings_repository = settings_repository
        self.current_settings: SettingsData | None = None

        self._build_ui()
        self.load_settings()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(12)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        root.addWidget(title)

        form_group = QGroupBox("Cấu hình hệ thống")
        form = QFormLayout(form_group)

        self.company_name = QLineEdit()
        self.department_name = QLineEdit()
        self.sender_email = QLineEdit()
        self.gmail_app_password = QLineEdit()
        self.gmail_app_password.setEchoMode(QLineEdit.Password)

        self.email_subject_template = QTextEdit()
        self.email_subject_template.setFixedHeight(52)
        self.email_body_template = QTextEdit()
        self.email_body_template.setFixedHeight(120)
        self.payslip_thank_you_text = QTextEdit()
        self.payslip_thank_you_text.setFixedHeight(72)
        self.payslip_security_note = QTextEdit()
        self.payslip_security_note.setFixedHeight(72)

        self.salary_view_password = QLineEdit()
        self.salary_view_password.setEchoMode(QLineEdit.Password)
        self.salary_view_password.setPlaceholderText("Để trống nếu không đổi mật khẩu")

        self.send_delay_seconds = QSpinBox()
        self.send_delay_seconds.setRange(1, 300)
        self.auto_lock_minutes = QSpinBox()
        self.auto_lock_minutes.setRange(1, 240)

        self.storage_base_path = QLineEdit()

        form.addRow("Company name", self.company_name)
        form.addRow("Department name", self.department_name)
        form.addRow("Sender email", self.sender_email)
        form.addRow("Gmail app password", self.gmail_app_password)
        form.addRow("Email subject template", self.email_subject_template)
        form.addRow("Email body template", self.email_body_template)
        form.addRow("Payslip thank-you text", self.payslip_thank_you_text)
        form.addRow("Payslip security note", self.payslip_security_note)
        form.addRow("Salary view password", self.salary_view_password)
        form.addRow("Send delay seconds", self.send_delay_seconds)
        form.addRow("Auto lock minutes", self.auto_lock_minutes)
        form.addRow("Storage base path", self.storage_base_path)

        root.addWidget(form_group)

        button_row = QHBoxLayout()
        self.test_email_button = QPushButton("Test email (placeholder)")
        self.test_email_button.clicked.connect(self._on_test_email)
        save_btn = QPushButton("Save settings")
        save_btn.clicked.connect(self.save_settings)

        button_row.addWidget(self.test_email_button)
        button_row.addStretch(1)
        button_row.addWidget(save_btn)
        root.addLayout(button_row)

    def load_settings(self) -> None:
        settings = self.settings_repository.get()
        self.current_settings = settings

        self.company_name.setText(settings.company_name)
        self.department_name.setText(settings.department_name)
        self.sender_email.setText(settings.sender_email)
        self.gmail_app_password.setText(settings.gmail_app_password)
        self.email_subject_template.setPlainText(settings.email_subject_template)
        self.email_body_template.setPlainText(settings.email_body_template)
        self.payslip_thank_you_text.setPlainText(settings.payslip_thank_you_text)
        self.payslip_security_note.setPlainText(settings.payslip_security_note)
        self.salary_view_password.clear()
        self.send_delay_seconds.setValue(settings.send_delay_seconds)
        self.auto_lock_minutes.setValue(settings.auto_lock_minutes)
        self.storage_base_path.setText(settings.storage_base_path)

    def save_settings(self) -> None:
        assert self.current_settings is not None

        payload = SettingsData(
            company_name=self.company_name.text(),
            department_name=self.department_name.text(),
            sender_email=self.sender_email.text(),
            gmail_app_password=self.gmail_app_password.text(),
            email_subject_template=self.email_subject_template.toPlainText(),
            email_body_template=self.email_body_template.toPlainText(),
            payslip_thank_you_text=self.payslip_thank_you_text.toPlainText(),
            payslip_security_note=self.payslip_security_note.toPlainText(),
            salary_view_password_hash=self.current_settings.salary_view_password_hash,
            send_delay_seconds=self.send_delay_seconds.value(),
            auto_lock_minutes=self.auto_lock_minutes.value(),
            storage_base_path=self.storage_base_path.text(),
        )
        self.settings_repository.save(payload, self.salary_view_password.text().strip() or None)
        self.load_settings()
        QMessageBox.information(self, "Saved", "Settings đã được lưu.")

    def _on_test_email(self) -> None:
        QMessageBox.information(
            self,
            "Test email",
            "Placeholder only. SMTP test sẽ được triển khai ở milestone sau.",
        )
