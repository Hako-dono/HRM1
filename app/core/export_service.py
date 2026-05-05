from __future__ import annotations

from pathlib import Path
from openpyxl import Workbook

from data.history_repository import HistoryRepository


class ExportService:
    def __init__(self, history_repo: HistoryRepository) -> None:
        self.history_repo = history_repo

    def export_session_logs(self, session_id: int) -> Path | None:
        summary = self.history_repo.get_session(session_id)
        if not summary:
            return None
        rows = self.history_repo.list_recipients(session_id)
        export_dir = Path(summary["session_folder"] or "app_data") / "export"
        export_dir.mkdir(parents=True, exist_ok=True)
        out = export_dir / f"logs_{summary['session_code']}.xlsx"

        wb = Workbook()
        ws = wb.active
        ws.title = "Send Logs"
        ws.append(["Mã phiên", "Tháng lương", "Mã NV", "Họ tên", "Email", "Phòng ban", "Trạng thái gửi", "Thời gian gửi", "Tên file PDF", "Lỗi nếu có"])
        for r in rows:
            ws.append([summary["session_code"], summary["payroll_month"], r.employee_code, r.employee_name, r.email, r.department, r.send_status, r.sent_at, r.pdf_file_name, r.error_message])
        wb.save(out)
        return out
