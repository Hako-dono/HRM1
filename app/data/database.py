from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    company_name TEXT NOT NULL DEFAULT 'BSM',
                    department_name TEXT NOT NULL DEFAULT 'Phòng HCNS',
                    sender_email TEXT DEFAULT '',
                    gmail_app_password TEXT DEFAULT '',
                    email_subject_template TEXT DEFAULT '[BSM] Phiếu lương tháng {thang_luong} - {ho_ten}',
                    email_body_template TEXT DEFAULT 'Kính gửi Anh/Chị {ho_ten},\n\nPhòng HCNS gửi Anh/Chị phiếu lương tháng {thang_luong} trong file đính kèm.\n\nNếu có thắc mắc, Anh/Chị vui lòng phản hồi lại email này.\n\nTrân trọng,\nPhòng HCNS',
                    payslip_thank_you_text TEXT DEFAULT 'Trân trọng,\nPhòng HCNS',
                    payslip_security_note TEXT DEFAULT 'Mật khẩu mở file là Mã nhân viên của Anh/Chị.',
                    salary_view_password_hash TEXT DEFAULT '',
                    send_delay_seconds INTEGER NOT NULL DEFAULT 3,
                    auto_lock_minutes INTEGER NOT NULL DEFAULT 5,
                    storage_base_path TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS send_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_code TEXT NOT NULL UNIQUE,
                    payroll_month TEXT,
                    status TEXT NOT NULL DEFAULT 'Draft',
                    total_recipients INTEGER NOT NULL DEFAULT 0,
                    sent_count INTEGER NOT NULL DEFAULT 0,
                    failed_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    started_at TEXT,
                    ended_at TEXT,
                    session_folder TEXT,
                    payroll_source_file TEXT,
                    employee_source_file TEXT
                );

                CREATE TABLE IF NOT EXISTS session_recipients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    employee_code TEXT NOT NULL,
                    employee_name TEXT,
                    job_title TEXT,
                    department TEXT,
                    employee_email TEXT,
                    employment_status TEXT,
                    net_amount REAL,
                    payroll_data_json TEXT,
                    validation_status TEXT NOT NULL DEFAULT 'valid',
                    validation_message TEXT,
                    sendable INTEGER NOT NULL DEFAULT 1,
                    send_status TEXT NOT NULL DEFAULT 'Pending',
                    selected INTEGER NOT NULL DEFAULT 1,
                    last_error TEXT,
                    sent_at TEXT,
                    FOREIGN KEY (session_id) REFERENCES send_sessions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS send_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    recipient_id INTEGER,
                    employee_code TEXT,
                    employee_email TEXT,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES send_sessions(id),
                    FOREIGN KEY (recipient_id) REFERENCES session_recipients(id)
                );
                """
            )
            conn.execute("INSERT INTO settings (id) VALUES (1) ON CONFLICT(id) DO NOTHING")
