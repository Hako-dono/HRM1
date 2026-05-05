from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from data.database import Database


@dataclass
class SessionHistory:
    id: int
    session_code: str
    payroll_month: str
    created_at: str
    updated_at: str
    status: str
    sent_count: int
    failed_count: int
    pending_count: int
    internal_note: str


@dataclass
class RecipientHistory:
    id: int
    employee_code: str
    employee_name: str
    email: str
    department: str
    send_status: str
    sent_at: str
    pdf_file_name: str
    error_message: str


class HistoryRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get_session(self, session_id: int):
        with self.db.connect() as conn:
            return conn.execute("SELECT * FROM send_sessions WHERE id=?", (session_id,)).fetchone()

    def list_sessions(self, payroll_month: str | None = None) -> list[SessionHistory]:
        q = "SELECT * FROM send_sessions"
        args = []
        if payroll_month:
            q += " WHERE payroll_month=?"
            args.append(payroll_month)
        q += " ORDER BY id DESC"
        with self.db.connect() as conn:
            rows = conn.execute(q, args).fetchall()
        out = []
        for r in rows:
            pending = max((r["total_recipients"] or 0) - (r["sent_count"] or 0) - (r["failed_count"] or 0), 0)
            out.append(SessionHistory(r["id"], r["session_code"] or "", r["payroll_month"] or "", r["created_at"] or "", r["updated_at"] or "", r["status"] or "", r["sent_count"] or 0, r["failed_count"] or 0, pending, ""))
        return out

    def list_recipients(self, session_id: int) -> list[RecipientHistory]:
        with self.db.connect() as conn:
            rows = conn.execute("SELECT * FROM session_recipients WHERE session_id=? ORDER BY employee_code", (session_id,)).fetchall()
            session = conn.execute("SELECT session_folder FROM send_sessions WHERE id=?", (session_id,)).fetchone()
        folder = Path(session["session_folder"] or "") / "pdf"
        out = []
        for r in rows:
            pdf = ""
            if folder.exists():
                cands = sorted(folder.glob(f"*_{r['employee_code']}_*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
                if cands: pdf = cands[0].name
            out.append(RecipientHistory(r["id"], r["employee_code"] or "", r["employee_name"] or "", r["employee_email"] or "", r["department"] or "", r["send_status"] or "", r["sent_at"] or "", pdf, r["last_error"] or ""))
        return out

    def log_resend(self, session_id: int, recipient_id: int, mode: str, status: str, msg: str) -> None:
        with self.db.connect() as conn:
            conn.execute("INSERT INTO send_logs(session_id,recipient_id,employee_code,employee_email,action,status,message,is_resend,resend_mode) SELECT ?,id,employee_code,employee_email,'RESEND',?,?,1,? FROM session_recipients WHERE id=?", (session_id, recipient_id, status, msg[:500], mode, recipient_id))

    def update_email(self, recipient_id: int, email: str) -> None:
        with self.db.connect() as conn:
            conn.execute("UPDATE session_recipients SET employee_email=? WHERE id=?", (email, recipient_id))
