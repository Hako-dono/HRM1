from __future__ import annotations

import smtplib
import time
from dataclasses import dataclass
from email.message import EmailMessage

from core.pdf_service import PdfService
from data.preview_repository import PreviewRepository
from data.settings_repository import SettingsRepository


@dataclass
class SendProgress:
    current_recipient: str
    sent_count: int
    failed_count: int
    pending_count: int
    total_count: int


class EmailService:
    def __init__(self, settings_repo: SettingsRepository, preview_repo: PreviewRepository, pdf_service: PdfService) -> None:
        self.settings_repo = settings_repo
        self.preview_repo = preview_repo
        self.pdf_service = pdf_service
        self.pause_requested = False
        self.cancel_requested = False

    def request_pause(self) -> None:
        self.pause_requested = True

    def request_cancel(self) -> None:
        self.cancel_requested = True

    def send_test_email(self, to_email: str) -> None:
        settings = self.settings_repo.get()
        msg = EmailMessage()
        msg["From"] = settings.sender_email
        msg["To"] = to_email
        msg["Subject"] = "[Smart Payslip] Test Email"
        msg.set_content("This is a test email from Smart Payslip.")
        self._send_message(msg, settings.sender_email, settings.gmail_app_password)

    def send_bulk(self, session_id: int, recipient_ids: list[int], progress_cb=None) -> tuple[int, int, str]:
        self.pause_requested = False
        self.cancel_requested = False
        settings = self.settings_repo.get()
        self.preview_repo.set_session_status(session_id, "Đang gửi")
        sent = failed = 0
        total = len(recipient_ids)
        self.pdf_service.generate_individual(recipient_ids, overwrite=False)

        for idx, rid in enumerate(recipient_ids, start=1):
            detail = self.preview_repo.get_send_detail(rid)
            if not detail:
                continue
            pdf_path = self.preview_repo.find_latest_pdf_for_recipient(rid)
            try:
                msg = EmailMessage()
                msg["From"] = settings.sender_email
                msg["To"] = detail["employee_email"]
                msg["Subject"] = self._render_template(settings.email_subject_template, detail)
                msg.set_content(self._render_template(settings.email_body_template, detail))
                if pdf_path and pdf_path.exists():
                    msg.add_attachment(pdf_path.read_bytes(), maintype="application", subtype="pdf", filename=pdf_path.name)
                self._send_message(msg, settings.sender_email, settings.gmail_app_password)
                self.preview_repo.mark_send_success(session_id, rid)
                sent += 1
            except Exception as ex:
                self.preview_repo.mark_send_failed(session_id, rid, str(ex))
                failed += 1

            pending = total - (sent + failed)
            if progress_cb:
                progress_cb(SendProgress(detail["employee_name"], sent, failed, pending, total))

            if self.cancel_requested:
                self.preview_repo.mark_remaining_cancelled(session_id)
                self.preview_repo.set_session_status(session_id, "Đã hủy")
                self.preview_repo.update_session_counters(session_id)
                return sent, failed, "cancelled"
            if self.pause_requested:
                self.preview_repo.set_session_status(session_id, "Tạm dừng")
                self.preview_repo.update_session_counters(session_id)
                return sent, failed, "paused"

            time.sleep(max(1, settings.send_delay_seconds))

        self.preview_repo.set_session_status(session_id, "Completed")
        self.preview_repo.update_session_counters(session_id)
        return sent, failed, "completed"

    def _send_message(self, msg: EmailMessage, sender: str, app_password: str) -> None:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.starttls(); server.login(sender, app_password); server.send_message(msg)

    def _render_template(self, template: str, detail: dict) -> str:
        mapping = {
            "{ho_ten}": detail.get("employee_name", ""),
            "{thang_luong}": detail.get("payroll_month", ""),
            "{ma_nv}": detail.get("employee_code", ""),
            "{company_name}": detail.get("company_name", "BSM"),
            "{department_name}": detail.get("department_name", "Phòng HCNS"),
        }
        for k, v in mapping.items():
            template = template.replace(k, str(v))
        return template
