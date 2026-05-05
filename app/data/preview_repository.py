from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from data.database import Database


@dataclass
class RecipientView:
    id: int; employee_code: str; employee_name: str; department: str; job_title: str; employee_email: str
    net_amount: float | None; validation_status: str; send_status: str; sendable: bool; selected: bool


@dataclass
class RecipientPayslipData:
    employee_code: str; employee_name: str; department: str; job_title: str; payroll_month: str; payroll_data: dict


class PreviewRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get_current_draft_session_id(self) -> int | None:
        with self.database.connect() as conn:
            row = conn.execute("SELECT id FROM send_sessions WHERE status='Draft' ORDER BY id DESC LIMIT 1").fetchone()
            return row["id"] if row else None

    def get_session_summary(self, session_id: int):
        with self.database.connect() as conn:
            return conn.execute("SELECT * FROM send_sessions WHERE id=?", (session_id,)).fetchone()

    def get_recipients(self, session_id: int) -> list[RecipientView]:
        with self.database.connect() as conn:
            rows = conn.execute("SELECT * FROM session_recipients WHERE session_id=? ORDER BY department, employee_code", (session_id,)).fetchall()
        return [RecipientView(r["id"], r["employee_code"] or "", r["employee_name"] or "", r["department"] or "", r["job_title"] or "", r["employee_email"] or "", r["net_amount"], r["validation_status"] or "valid", r["send_status"] or "Pending", bool(r["sendable"]), bool(r["selected"])) for r in rows]

    def get_payslip_data(self, recipient_id: int) -> RecipientPayslipData | None:
        with self.database.connect() as conn:
            row = conn.execute("SELECT r.employee_code,r.employee_name,r.department,r.job_title,r.payroll_data_json,s.payroll_month FROM session_recipients r JOIN send_sessions s ON s.id=r.session_id WHERE r.id=?", (recipient_id,)).fetchone()
        if not row: return None
        return RecipientPayslipData(row["employee_code"] or "", row["employee_name"] or "", row["department"] or "", row["job_title"] or "", row["payroll_month"] or "", json.loads(row["payroll_data_json"] or "{}"))

    def get_session_meta_for_recipient(self, recipient_id: int):
        with self.database.connect() as conn:
            return conn.execute("SELECT s.session_code, s.session_folder FROM session_recipients r JOIN send_sessions s ON s.id=r.session_id WHERE r.id=?", (recipient_id,)).fetchone()

    def get_send_detail(self, recipient_id: int):
        with self.database.connect() as conn:
            return conn.execute("""SELECT r.employee_code,r.employee_name,r.employee_email,s.payroll_month,st.company_name,st.department_name
            FROM session_recipients r JOIN send_sessions s ON s.id=r.session_id JOIN settings st ON st.id=1 WHERE r.id=?""", (recipient_id,)).fetchone()

    def find_latest_pdf_for_recipient(self, recipient_id: int) -> Path | None:
        meta = self.get_session_meta_for_recipient(recipient_id)
        detail = self.get_send_detail(recipient_id)
        if not meta or not detail:
            return None
        folder = Path(meta["session_folder"]) / "pdf"
        if not folder.exists(): return None
        code = detail["employee_code"]
        candidates = sorted(folder.glob(f"*_{code}_*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
        return candidates[0] if candidates else None

    def update_email(self, recipient_id: int, email: str, validation_status: str, sendable: bool) -> None:
        with self.database.connect() as conn:
            conn.execute("UPDATE session_recipients SET employee_email=?, validation_status=?, sendable=? WHERE id=?", (email, validation_status, 1 if sendable else 0, recipient_id))

    def update_selected(self, recipient_id: int, selected: bool) -> None:
        with self.database.connect() as conn:
            conn.execute("UPDATE session_recipients SET selected=? WHERE id=?", (1 if selected else 0, recipient_id))

    def mark_send_success(self, session_id: int, recipient_id: int) -> None:
        with self.database.connect() as conn:
            conn.execute("UPDATE session_recipients SET send_status='Sent', last_error=NULL, sent_at=CURRENT_TIMESTAMP WHERE id=?", (recipient_id,))
            conn.execute("INSERT INTO send_logs(session_id,recipient_id,employee_code,employee_email,action,status,message) SELECT ?,id,employee_code,employee_email,'SEND','SUCCESS','' FROM session_recipients WHERE id=?", (session_id, recipient_id))

    def mark_send_failed(self, session_id: int, recipient_id: int, error: str) -> None:
        with self.database.connect() as conn:
            conn.execute("UPDATE session_recipients SET send_status='Failed', last_error=? WHERE id=?", (error[:500], recipient_id))
            conn.execute("INSERT INTO send_logs(session_id,recipient_id,employee_code,employee_email,action,status,message) SELECT ?,id,employee_code,employee_email,'SEND','FAILED',? FROM session_recipients WHERE id=?", (session_id, error[:500], recipient_id))

    def update_session_counters(self, session_id: int) -> None:
        with self.database.connect() as conn:
            row = conn.execute("SELECT COUNT(*) total, SUM(CASE WHEN send_status='Sent' THEN 1 ELSE 0 END) sent, SUM(CASE WHEN send_status='Failed' THEN 1 ELSE 0 END) failed FROM session_recipients WHERE session_id=?", (session_id,)).fetchone()
            conn.execute("UPDATE send_sessions SET total_recipients=?, sent_count=?, failed_count=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (row["total"] or 0, row["sent"] or 0, row["failed"] or 0, session_id))
