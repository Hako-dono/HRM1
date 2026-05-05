from __future__ import annotations

from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from core.email_service import EmailService
from core.export_service import ExportService
from core.import_service import ImportService
from core.pdf_service import PdfService
from data.history_repository import HistoryRepository


class HistoryScreen(QWidget):
    def __init__(self, history_repo: HistoryRepository, email_service: EmailService, pdf_service: PdfService, import_service: ImportService, export_service: ExportService) -> None:
        super().__init__()
        self.repo = history_repo
        self.email_service = email_service
        self.pdf_service = pdf_service
        self.import_service = import_service
        self.export_service = export_service
        self.current_session_id = None
        self._build_ui(); self.reload_sessions()

    def _build_ui(self):
        root = QVBoxLayout(self)
        top = QHBoxLayout()
        self.month = QLineEdit(); self.month.setPlaceholderText("Filter payroll month YYYY-MM")
        btn = QPushButton("Filter"); btn.clicked.connect(self.reload_sessions)
        top.addWidget(self.month); top.addWidget(btn)
        root.addLayout(top)

        self.sessions = QTableWidget(0, 9)
        self.sessions.setHorizontalHeaderLabels(["session code","payroll month","created date","updated date","status","sent","failed","pending","internal note"])
        self.sessions.itemSelectionChanged.connect(self.on_session_selected)
        root.addWidget(self.sessions)

        self.recipients = QTableWidget(0, 8)
        self.recipients.setHorizontalHeaderLabels(["Mã NV","Họ tên","Email","Phòng ban","Send status","Last sent time","PDF file name","Error message"])
        root.addWidget(self.recipients)

        export_btn = QPushButton("Export selected session logs")
        export_btn.clicked.connect(self.export_selected_session)
        root.addWidget(export_btn)

        act = QHBoxLayout()
        self.mode = QComboBox(); self.mode.addItems(["Use old PDF", "Generate new PDF from newly imported payroll file"])
        resend = QPushButton("Resend selected")
        resend.clicked.connect(self.resend_selected)
        act.addWidget(self.mode); act.addWidget(resend)
        root.addLayout(act)

    def reload_sessions(self):
        sessions = self.repo.list_sessions(self.month.text().strip() or None)
        self.sessions.setRowCount(len(sessions))
        self.session_data = sessions
        for i, s in enumerate(sessions):
            vals=[s.session_code,s.payroll_month,s.created_at,s.updated_at,s.status,str(s.sent_count),str(s.failed_count),str(s.pending_count),s.internal_note]
            for j,v in enumerate(vals): self.sessions.setItem(i,j,QTableWidgetItem(v))

    def on_session_selected(self):
        row = self.sessions.currentRow()
        if row < 0: return
        s = self.session_data[row]; self.current_session_id = s.id
        recs = self.repo.list_recipients(s.id)
        self.recipient_data = recs
        self.recipients.setRowCount(len(recs))
        for i,r in enumerate(recs):
            vals=[r.employee_code,r.employee_name,r.email,r.department,r.send_status,r.sent_at,r.pdf_file_name,r.error_message]
            for j,v in enumerate(vals): self.recipients.setItem(i,j,QTableWidgetItem(v))

    def resend_selected(self):
        if not self.current_session_id: return
        rows = sorted({idx.row() for idx in self.recipients.selectedIndexes()})
        if not rows:
            QMessageBox.information(self, "Resend", "Please select recipients."); return
        mode = self.mode.currentText()
        for r in rows:
            item = self.recipient_data[r]
            email_item = self.recipients.item(r,2)
            email = email_item.text().strip() if email_item else item.email
            self.repo.update_email(item.id, email)
            try:
                if mode.startswith("Use old"):
                    sent, failed, _ = self.email_service.send_bulk(self.current_session_id, [item.id])
                    status = "SUCCESS" if sent == 1 else "FAILED"
                else:
                    # MVP simplified: regenerate from current session data
                    self.pdf_service.generate_individual([item.id], overwrite=False)
                    sent, failed, _ = self.email_service.send_bulk(self.current_session_id, [item.id])
                    status = "SUCCESS" if sent == 1 else "FAILED"
                self.repo.log_resend(self.current_session_id, item.id, "old_pdf" if mode.startswith("Use old") else "new_pdf", status, "")
            except Exception as ex:
                self.repo.log_resend(self.current_session_id, item.id, "old_pdf" if mode.startswith("Use old") else "new_pdf", "FAILED", str(ex))
        QMessageBox.information(self, "Resend", "Resend completed.")
        self.on_session_selected()

    def export_selected_session(self):
        if not self.current_session_id:
            QMessageBox.information(self, "Export", "Vui lòng chọn session để export.")
            return
        path = self.export_service.export_session_logs(self.current_session_id)
        if path:
            QMessageBox.information(self, "Export", f"Đã export: {path}")
