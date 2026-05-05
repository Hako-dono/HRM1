from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from data.database import Database


@dataclass
class RecipientRecord:
    employee_code: str
    employee_name: str
    job_title: str
    department: str
    employee_email: str
    employment_status: str
    net_amount: float | None
    payroll_data: dict
    validation_status: str
    validation_message: str
    sendable: bool


class ImportRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_or_replace_draft_session(
        self,
        payroll_month: str,
        payroll_source_file: Path,
        employee_source_file: Path,
        recipients: list[RecipientRecord],
    ) -> int:
        with self.database.connect() as conn:
            row = conn.execute("SELECT id FROM send_sessions WHERE status='Draft' ORDER BY id DESC LIMIT 1").fetchone()
            if row:
                session_id = row["id"]
                session_code = self._build_session_code(payroll_month, conn)
                session_folder = self._session_folder(session_code)
                source_dir = session_folder / "source"
                source_dir.mkdir(parents=True, exist_ok=True)
                payroll_copy = source_dir / payroll_source_file.name
                employee_copy = source_dir / employee_source_file.name
                shutil.copy2(payroll_source_file, payroll_copy)
                shutil.copy2(employee_source_file, employee_copy)

                conn.execute(
                    """UPDATE send_sessions SET session_code=?, payroll_month=?, total_recipients=?, updated_at=CURRENT_TIMESTAMP,
                    session_folder=?, payroll_source_file=?, employee_source_file=? WHERE id=?""",
                    (session_code, payroll_month, len(recipients), str(session_folder), str(payroll_copy), str(employee_copy), session_id),
                )
                conn.execute("DELETE FROM session_recipients WHERE session_id=?", (session_id,))
            else:
                session_code = self._build_session_code(payroll_month, conn)
                session_folder = self._session_folder(session_code)
                source_dir = session_folder / "source"
                source_dir.mkdir(parents=True, exist_ok=True)
                payroll_copy = source_dir / payroll_source_file.name
                employee_copy = source_dir / employee_source_file.name
                shutil.copy2(payroll_source_file, payroll_copy)
                shutil.copy2(employee_source_file, employee_copy)
                cur = conn.execute(
                    """INSERT INTO send_sessions(session_code,payroll_month,status,total_recipients,session_folder,payroll_source_file,employee_source_file)
                    VALUES(?,?,'Draft',?,?,?,?)""",
                    (session_code, payroll_month, len(recipients), str(session_folder), str(payroll_copy), str(employee_copy)),
                )
                session_id = cur.lastrowid

            for r in recipients:
                conn.execute(
                    """INSERT INTO session_recipients(session_id,employee_code,employee_name,job_title,department,employee_email,
                    employment_status,net_amount,payroll_data_json,validation_status,validation_message,sendable)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        session_id,
                        r.employee_code,
                        r.employee_name,
                        r.job_title,
                        r.department,
                        r.employee_email,
                        r.employment_status,
                        r.net_amount,
                        json.dumps(r.payroll_data, ensure_ascii=False),
                        r.validation_status,
                        r.validation_message,
                        1 if r.sendable else 0,
                    ),
                )
            return session_id

    def _build_session_code(self, payroll_month: str, conn) -> str:
        today = datetime.now().strftime("%Y%m%d")
        seq_prefix = f"SP-{payroll_month}-{today}-"
        row = conn.execute("SELECT session_code FROM send_sessions WHERE session_code LIKE ? ORDER BY session_code DESC LIMIT 1", (f"{seq_prefix}%",)).fetchone()
        seq = 1
        if row:
            m = re.search(r"-(\d{3})$", row["session_code"])
            if m:
                seq = int(m.group(1)) + 1
        return f"{seq_prefix}{seq:03d}"

    def _session_folder(self, session_code: str) -> Path:
        return Path("app_data") / "sessions" / session_code
