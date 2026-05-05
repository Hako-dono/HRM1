from __future__ import annotations

import json
from dataclasses import dataclass

from data.database import Database


@dataclass
class RecipientView:
    id: int
    employee_code: str
    employee_name: str
    department: str
    job_title: str
    employee_email: str
    net_amount: float | None
    validation_status: str
    send_status: str
    sendable: bool
    selected: bool


@dataclass
class RecipientPayslipData:
    employee_code: str
    employee_name: str
    department: str
    job_title: str
    payroll_month: str
    payroll_data: dict


class PreviewRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get_current_draft_session_id(self) -> int | None:
        with self.database.connect() as conn:
            row = conn.execute("SELECT id FROM send_sessions WHERE status='Draft' ORDER BY id DESC LIMIT 1").fetchone()
            return row["id"] if row else None

    def get_recipients(self, session_id: int) -> list[RecipientView]:
        with self.database.connect() as conn:
            rows = conn.execute("SELECT * FROM session_recipients WHERE session_id=? ORDER BY department, employee_code", (session_id,)).fetchall()
        return [RecipientView(
            id=r["id"], employee_code=r["employee_code"] or "", employee_name=r["employee_name"] or "",
            department=r["department"] or "", job_title=r["job_title"] or "", employee_email=r["employee_email"] or "",
            net_amount=r["net_amount"], validation_status=r["validation_status"] or "valid", send_status=r["send_status"] or "Pending",
            sendable=bool(r["sendable"]), selected=bool(r["selected"])
        ) for r in rows]

    def get_payslip_data(self, recipient_id: int) -> RecipientPayslipData | None:
        with self.database.connect() as conn:
            row = conn.execute(
                """SELECT r.employee_code,r.employee_name,r.department,r.job_title,r.payroll_data_json,s.payroll_month
                   FROM session_recipients r JOIN send_sessions s ON s.id=r.session_id WHERE r.id=?""",
                (recipient_id,),
            ).fetchone()
        if not row:
            return None
        return RecipientPayslipData(
            employee_code=row["employee_code"] or "",
            employee_name=row["employee_name"] or "",
            department=row["department"] or "",
            job_title=row["job_title"] or "",
            payroll_month=row["payroll_month"] or "",
            payroll_data=json.loads(row["payroll_data_json"] or "{}"),
        )

    def update_email(self, recipient_id: int, email: str, validation_status: str, sendable: bool) -> None:
        with self.database.connect() as conn:
            conn.execute("UPDATE session_recipients SET employee_email=?, validation_status=?, sendable=? WHERE id=?", (email, validation_status, 1 if sendable else 0, recipient_id))

    def update_selected(self, recipient_id: int, selected: bool) -> None:
        with self.database.connect() as conn:
            conn.execute("UPDATE session_recipients SET selected=? WHERE id=?", (1 if selected else 0, recipient_id))
