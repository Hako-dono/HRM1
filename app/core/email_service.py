from __future__ import annotations

import smtplib
import time
from email.message import EmailMessage
from pathlib import Path

from data.preview_repository import PreviewRepository
from data.settings_repository import SettingsRepository
from core.pdf_service import PdfService


class EmailService:
    def __init__(self, settings_repo: SettingsRepository, preview_repo: PreviewRepository, pdf_service: PdfService) -> None:
        self.settings_repo = settings_repo
        self.preview_repo = preview_repo
        self.pdf_service = pdf_service

    def send_test_email(self, to_email: str) -> None:
        settings = self.settings_repo.get()
        msg = EmailMessage()
        msg["From"] = settings.sender_email
        msg["To"] = to_email
        msg["Subject"] = "[Smart Payslip] Test Email"
        msg.set_content("This is a test email from Smart Payslip.")
        self._send_message(msg, settings.sender_email, settings.gmail_app_password)

    def send_bulk(self, session_id: int, recipient_ids: list[int]) -> tuple[int, int]:
        settings = self.settings_repo.get()
        sent = 0
        failed = 0
        self.pdf_service.generate_individual(recipient_ids, overwrite=False)
        for rid in recipient_ids:
            detail = self.preview_repo.get_send_detail(rid)
            if not detail:
                continue
            pdf_path = self.preview_repo.find_latest_pdf_for_recipient(rid)
            try:
                subject = self._render_template(settings.email_subject_template, detail)
                body = self._render_template(settings.email_body_template, detail)
                msg = EmailMessage()
                msg["From"] = settings.sender_email
                msg["To"] = detail["employee_email"]
                msg["Subject"] = subject
                msg.set_content(body)
                if pdf_path and pdf_path.exists():
                    msg.add_attachment(pdf_path.read_bytes(), maintype="application", subtype="pdf", filename=pdf_path.name)
                self._send_message(msg, settings.sender_email, settings.gmail_app_password)
                self.preview_repo.mark_send_success(session_id, rid)
                sent += 1
            except Exception as ex:
                self.preview_repo.mark_send_failed(session_id, rid, str(ex))
                failed += 1
            time.sleep(max(1, settings.send_delay_seconds))
        self.preview_repo.update_session_counters(session_id)
        return sent, failed

    def _send_message(self, msg: EmailMessage, sender: str, app_password: str) -> None:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.starttls()
            server.login(sender, app_password)
            server.send_message(msg)

    def _render_template(self, template: str, detail: dict) -> str:
        mapping = {
            "{ho_ten}": detail.get("employee_name", ""),
            "{thang_luong}": detail.get("payroll_month", ""),
            "{ma_nv}": detail.get("employee_code", ""),
            "{company_name}": detail.get("company_name", "BSM"),
            "{department_name}": detail.get("department_name", "Phòng HCNS"),
        }
        result = template
        for k, v in mapping.items():
            result = result.replace(k, str(v))
        return result
