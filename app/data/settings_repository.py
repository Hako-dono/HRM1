from __future__ import annotations

import hashlib
from dataclasses import dataclass

from data.database import Database


@dataclass
class SettingsData:
    company_name: str
    department_name: str
    sender_email: str
    gmail_app_password: str
    email_subject_template: str
    email_body_template: str
    payslip_thank_you_text: str
    payslip_security_note: str
    salary_view_password_hash: str
    send_delay_seconds: int
    auto_lock_minutes: int
    storage_base_path: str


class GmailPasswordStorage:
    @staticmethod
    def save(raw_password: str) -> str:
        return raw_password.strip()

    @staticmethod
    def load(stored_value: str) -> str:
        return stored_value


class SettingsRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get(self) -> SettingsData:
        with self.database.connect() as conn:
            row = conn.execute("SELECT * FROM settings WHERE id = 1").fetchone()
        return SettingsData(
            company_name=row["company_name"], department_name=row["department_name"], sender_email=row["sender_email"],
            gmail_app_password=GmailPasswordStorage.load(row["gmail_app_password"]), email_subject_template=row["email_subject_template"],
            email_body_template=row["email_body_template"], payslip_thank_you_text=row["payslip_thank_you_text"],
            payslip_security_note=row["payslip_security_note"], salary_view_password_hash=row["salary_view_password_hash"],
            send_delay_seconds=row["send_delay_seconds"], auto_lock_minutes=row["auto_lock_minutes"], storage_base_path=row["storage_base_path"],
        )

    def verify_salary_password(self, raw_password: str) -> bool:
        current = self.get()
        if not current.salary_view_password_hash:
            return False
        return hashlib.sha256(raw_password.encode("utf-8")).hexdigest() == current.salary_view_password_hash


    def change_salary_password(self, old_password: str, new_password: str, confirm_password: str) -> tuple[bool, str]:
        if not new_password.strip():
            return False, "Mật khẩu mới không được để trống."
        if new_password != confirm_password:
            return False, "Xác nhận mật khẩu mới không khớp."
        cur = self.get()
        if cur.salary_view_password_hash and not self.verify_salary_password(old_password):
            return False, "Mật khẩu cũ không đúng."
        self.save(cur, new_password)
        return True, "Đổi mật khẩu thành công."

    def save(self, payload: SettingsData, salary_password_raw: str | None = None) -> None:
        password_hash = payload.salary_view_password_hash
        if salary_password_raw:
            password_hash = hashlib.sha256(salary_password_raw.encode("utf-8")).hexdigest()
        with self.database.connect() as conn:
            conn.execute(
                """UPDATE settings SET company_name=?,department_name=?,sender_email=?,gmail_app_password=?,email_subject_template=?,
                email_body_template=?,payslip_thank_you_text=?,payslip_security_note=?,salary_view_password_hash=?,send_delay_seconds=?,
                auto_lock_minutes=?,storage_base_path=? WHERE id=1""",
                (payload.company_name.strip(), payload.department_name.strip(), payload.sender_email.strip(),
                 GmailPasswordStorage.save(payload.gmail_app_password), payload.email_subject_template, payload.email_body_template,
                 payload.payslip_thank_you_text, payload.payslip_security_note, password_hash, payload.send_delay_seconds,
                 payload.auto_lock_minutes, payload.storage_base_path.strip()),
            )
