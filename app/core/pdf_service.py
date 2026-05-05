from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from data.preview_repository import PreviewRepository, RecipientPayslipData
from data.settings_repository import SettingsRepository


class PdfService:
    def __init__(self, preview_repository: PreviewRepository, settings_repository: SettingsRepository) -> None:
        self.preview_repository = preview_repository
        self.settings_repository = settings_repository

    def generate_individual(self, recipient_ids: list[int], overwrite: bool = False) -> list[Path]:
        settings = self.settings_repository.get()
        paths = []
        for rid in recipient_ids:
            data = self.preview_repository.get_payslip_data(rid)
            if not data:
                continue
            session = self.preview_repository.get_session_meta_for_recipient(rid)
            base_dir = Path(session["session_folder"]) / "pdf"
            base_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{data.payroll_month}_{data.employee_code}_{self._slug_name(data.employee_name)}.pdf"
            output = base_dir / filename
            if output.exists() and not overwrite:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                output = base_dir / f"{output.stem}_{ts}.pdf"
            self._render_single(data, settings.company_name, settings.payslip_security_note, settings.payslip_thank_you_text, output)
            self._encrypt_pdf(output, output, data.employee_code)
            paths.append(output)
        return paths

    def generate_batch(self, recipient_ids: list[int], batch_password: str) -> Path | None:
        if not recipient_ids:
            return None
        settings = self.settings_repository.get()
        first = self.preview_repository.get_session_meta_for_recipient(recipient_ids[0])
        session_code = first["session_code"]
        out_dir = Path(first["session_folder"]) / "print"
        out_dir.mkdir(parents=True, exist_ok=True)
        final_path = out_dir / f"print_batch_{session_code}.pdf"

        temp_files = []
        merger = PdfWriter()
        for rid in recipient_ids:
            data = self.preview_repository.get_payslip_data(rid)
            if not data:
                continue
            tmp = out_dir / f"_tmp_{rid}.pdf"
            self._render_single(data, settings.company_name, settings.payslip_security_note, settings.payslip_thank_you_text, tmp)
            temp_files.append(tmp)
            reader = PdfReader(str(tmp))
            merger.add_page(reader.pages[0])

        with open(final_path, "wb") as f:
            merger.write(f)

        self._encrypt_pdf(final_path, final_path, batch_password)
        for t in temp_files:
            t.unlink(missing_ok=True)
        return final_path

    def _render_single(self, data: RecipientPayslipData, company_name: str, security_note: str, thank_you: str, output: Path) -> None:
        c = canvas.Canvas(str(output), pagesize=A4)
        w, h = A4
        receipt_w = 320
        x = (w - receipt_w) / 2
        y = h - 60
        c.setFont("Helvetica-Bold", 12); c.drawString(x, y, company_name); y -= 16
        c.setFont("Helvetica", 10)
        c.drawString(x, y, f"Tháng lương: {data.payroll_month}"); y -= 14
        c.drawString(x, y, f"Mã NV: {data.employee_code}"); y -= 14
        c.drawString(x, y, f"Họ và tên: {data.employee_name}"); y -= 14
        c.drawString(x, y, f"Chức vụ: {data.job_title}"); y -= 14
        c.drawString(x, y, f"Phòng ban: {data.department}"); y -= 18

        fields = ["Lương cơ bản","Ngày công chuẩn","Ngày công thực tế","Phụ cấp ăn trưa","Phụ cấp trang phục","Phụ cấp điện thoại","Lương hiệu suất","Lương làm thêm giờ","Đóng góp trách nhiệm","BHXH","BHYT","BHTN","Thuế TNCN","Tạm ứng","Thực nhận"]
        money_fields = {"Lương cơ bản","Phụ cấp ăn trưa","Phụ cấp trang phục","Phụ cấp điện thoại","Lương hiệu suất","Lương làm thêm giờ","Đóng góp trách nhiệm","BHXH","BHYT","BHTN","Thuế TNCN","Tạm ứng","Thực nhận"}
        for f in fields:
            val = data.payroll_data.get(f, 0)
            txt = self._money(val) if f in money_fields else str(val)
            c.drawString(x, y, f"{f}:")
            c.drawRightString(x + receipt_w, y, txt)
            y -= 13
        y -= 8
        c.drawString(x, y, security_note); y -= 13
        c.drawString(x, y, thank_you)
        c.save()

    def _money(self, v) -> str:
        try:
            n = int(round(float(v)))
        except Exception:
            n = 0
        return f"{n:,}".replace(",", ".") + " VNĐ"

    def _slug_name(self, name: str) -> str:
        n = unicodedata.normalize("NFD", name)
        n = "".join(ch for ch in n if unicodedata.category(ch) != "Mn")
        n = n.replace("đ", "d").replace("Đ", "D")
        return re.sub(r"[^A-Za-z0-9]", "", n)

    def _encrypt_pdf(self, input_path: Path, output_path: Path, password: str) -> None:
        reader = PdfReader(str(input_path)); writer = PdfWriter()
        for p in reader.pages: writer.add_page(p)
        writer.encrypt(password)
        with open(output_path, "wb") as f: writer.write(f)

