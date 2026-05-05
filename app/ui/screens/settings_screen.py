from __future__ import annotations

from PySide6.QtWidgets import (QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSpinBox, QTextEdit, QVBoxLayout, QWidget, QInputDialog)

from core.email_service import EmailService
from core.salary_lock_service import SalaryLockService
from data.settings_repository import SettingsData, SettingsRepository


class SettingsScreen(QWidget):
    def __init__(self, settings_repository: SettingsRepository, email_service: EmailService | None = None, lock_service: SalaryLockService | None = None) -> None:
        super().__init__()
        self.settings_repository = settings_repository
        self.email_service = email_service
        self.current_settings: SettingsData | None = None
        self.lock_service = lock_service
        self._build_ui(); self.load_settings()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self); root.setContentsMargins(24, 24, 24, 24)
        title = QLabel("Settings"); title.setStyleSheet("font-size: 24px; font-weight: 700;"); root.addWidget(title)
        form_group = QGroupBox("Cấu hình hệ thống"); form = QFormLayout(form_group)
        self.company_name = QLineEdit(); self.department_name = QLineEdit(); self.sender_email = QLineEdit(); self.gmail_app_password = QLineEdit(); self.gmail_app_password.setEchoMode(QLineEdit.Password)
        self.email_subject_template = QTextEdit(); self.email_subject_template.setFixedHeight(52)
        self.email_body_template = QTextEdit(); self.email_body_template.setFixedHeight(120)
        self.payslip_thank_you_text = QTextEdit(); self.payslip_thank_you_text.setFixedHeight(72)
        self.payslip_security_note = QTextEdit(); self.payslip_security_note.setFixedHeight(72)
        self.salary_view_password = QLineEdit(); self.salary_view_password.setEchoMode(QLineEdit.Password); self.salary_view_password.setPlaceholderText("Để trống nếu không đổi mật khẩu")
        self.send_delay_seconds = QSpinBox(); self.send_delay_seconds.setRange(1, 300)
        self.auto_lock_minutes = QSpinBox(); self.auto_lock_minutes.setRange(1, 240)
        self.storage_base_path = QLineEdit()
        form.addRow("Company name", self.company_name); form.addRow("Department name", self.department_name); form.addRow("Sender email", self.sender_email)
        form.addRow("Gmail app password", self.gmail_app_password); form.addRow("Email subject template", self.email_subject_template); form.addRow("Email body template", self.email_body_template)
        form.addRow("Payslip thank-you text", self.payslip_thank_you_text); form.addRow("Payslip security note", self.payslip_security_note); form.addRow("Salary view password", self.salary_view_password)
        form.addRow("Send delay seconds", self.send_delay_seconds); form.addRow("Auto lock minutes", self.auto_lock_minutes); form.addRow("Storage base path", self.storage_base_path)
        root.addWidget(form_group)
        row = QHBoxLayout(); test = QPushButton("Test email"); test.clicked.connect(self._on_test_email); chg = QPushButton("Đổi mật khẩu xem lương"); chg.clicked.connect(self._change_salary_password); save = QPushButton("Save settings"); save.clicked.connect(self.save_settings)
        row.addWidget(test); row.addWidget(chg); row.addStretch(1); row.addWidget(save); root.addLayout(row)

    def load_settings(self) -> None:
        s = self.settings_repository.get(); self.current_settings = s
        self.company_name.setText(s.company_name); self.department_name.setText(s.department_name); self.sender_email.setText(s.sender_email)
        self.gmail_app_password.setText(s.gmail_app_password); self.email_subject_template.setPlainText(s.email_subject_template)
        self.email_body_template.setPlainText(s.email_body_template); self.payslip_thank_you_text.setPlainText(s.payslip_thank_you_text)
        self.payslip_security_note.setPlainText(s.payslip_security_note); self.salary_view_password.clear(); self.send_delay_seconds.setValue(s.send_delay_seconds)
        self.auto_lock_minutes.setValue(s.auto_lock_minutes); self.storage_base_path.setText(s.storage_base_path)

    def save_settings(self) -> None:
        assert self.current_settings
        payload = SettingsData(self.company_name.text(), self.department_name.text(), self.sender_email.text(), self.gmail_app_password.text(),
                               self.email_subject_template.toPlainText(), self.email_body_template.toPlainText(), self.payslip_thank_you_text.toPlainText(),
                               self.payslip_security_note.toPlainText(), self.current_settings.salary_view_password_hash, self.send_delay_seconds.value(),
                               self.auto_lock_minutes.value(), self.storage_base_path.text())
        self.settings_repository.save(payload, self.salary_view_password.text().strip() or None)
        self.load_settings(); QMessageBox.information(self, "Saved", "Settings đã được lưu.")

    def _on_test_email(self) -> None:
        if not self.email_service:
            QMessageBox.information(self, "Test email", "Email service chưa sẵn sàng.")
            return
        to_email, ok = QInputDialog.getText(self, "Test email", "Nhập email nhận test:")
        if not ok or not to_email.strip():
            return
        try:
            self.email_service.send_test_email(to_email.strip())
            QMessageBox.information(self, "Test email", "Gửi test email thành công.")
        except Exception as ex:
            QMessageBox.critical(self, "Test email", f"Gửi thất bại: {ex}")

    def _change_salary_password(self) -> None:
        old_pw, ok = QInputDialog.getText(self, "Đổi mật khẩu", "Mật khẩu cũ:", QLineEdit.Password)
        if not ok: return
        new_pw, ok = QInputDialog.getText(self, "Đổi mật khẩu", "Mật khẩu mới:", QLineEdit.Password)
        if not ok: return
        confirm_pw, ok = QInputDialog.getText(self, "Đổi mật khẩu", "Xác nhận mật khẩu mới:", QLineEdit.Password)
        if not ok: return
        success, msg = self.settings_repository.change_salary_password(old_pw, new_pw, confirm_pw)
        if success:
            QMessageBox.information(self, "Đổi mật khẩu", msg)
            if self.lock_service: self.lock_service.force_lock()
        else:
            QMessageBox.warning(self, "Đổi mật khẩu", msg)
