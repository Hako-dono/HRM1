from __future__ import annotations

import re
from collections import defaultdict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDialog, QFormLayout, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox, QPushButton, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout, QWidget, QInputDialog)

from data.preview_repository import PreviewRepository, RecipientView
from data.settings_repository import SettingsRepository

COLUMNS = ["Mã NV", "Họ và tên", "Phòng ban", "Chức vụ", "Email", "Thực nhận", "Data status", "Send status", "Chọn gửi"]
PAYROLL_FIELDS = [
    "Lương cơ bản", "Ngày công chuẩn", "Ngày công thực tế", "Phụ cấp ăn trưa", "Phụ cấp trang phục", "Phụ cấp điện thoại",
    "Lương hiệu suất", "Lương làm thêm giờ", "Đóng góp trách nhiệm", "BHXH", "BHYT", "BHTN", "Thuế TNCN", "Tạm ứng", "Thực nhận",
]


class PreviewScreen(QWidget):
    def __init__(self, preview_repo: PreviewRepository, settings_repo: SettingsRepository) -> None:
        super().__init__()
        self.preview_repo = preview_repo
        self.settings_repo = settings_repo
        self.salary_unlocked = False
        self.current_session_id: int | None = None
        self._build_ui()
        self.reload_data()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        title = QLabel("Preview & chọn gửi")
        title.setStyleSheet("font-size:24px;font-weight:700;")
        root.addWidget(title)

        toolbar = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("Tìm theo Mã NV / Họ tên"); self.search.textChanged.connect(self.render)
        self.filter_dept = QComboBox(); self.filter_dept.currentTextChanged.connect(self.render)
        self.filter_data = QComboBox(); self.filter_data.addItems(["All", "valid", "warning", "error"]); self.filter_data.currentTextChanged.connect(self.render)
        self.filter_send = QComboBox(); self.filter_send.addItems(["All", "Pending", "Sent", "Failed"]); self.filter_send.currentTextChanged.connect(self.render)
        reload_btn = QPushButton("Reload"); reload_btn.clicked.connect(self.reload_data)
        unlock_btn = QPushButton("Hiện số tiền"); unlock_btn.clicked.connect(self.unlock_salary)
        lock_btn = QPushButton("Khóa dữ liệu lương"); lock_btn.clicked.connect(self.lock_salary)
        for w in [self.search, self.filter_dept, self.filter_data, self.filter_send, reload_btn, unlock_btn, lock_btn]: toolbar.addWidget(w)
        root.addLayout(toolbar)

        self.stats = QLabel(); root.addWidget(self.stats)
        self.tree = QTreeWidget(); self.tree.setColumnCount(len(COLUMNS)); self.tree.setHeaderLabels(COLUMNS)
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.itemChanged.connect(self.on_item_changed)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        root.addWidget(self.tree, 1)

    def reload_data(self) -> None:
        self.current_session_id = self.preview_repo.get_current_draft_session_id()
        self.recipients = [] if not self.current_session_id else self.preview_repo.get_recipients(self.current_session_id)
        self.filter_dept.blockSignals(True)
        self.filter_dept.clear(); self.filter_dept.addItem("All")
        for d in sorted({r.department for r in self.recipients if r.department}): self.filter_dept.addItem(d)
        self.filter_dept.blockSignals(False)
        self.render()

    def render(self) -> None:
        self.tree.blockSignals(True); self.tree.clear()
        grouped = defaultdict(list)
        filtered = [r for r in self.recipients if self._match_filter(r)]
        for r in filtered: grouped[r.department or "(No phòng ban)"].append(r)
        for dept, recs in grouped.items():
            parent = QTreeWidgetItem([dept, "", dept, "", "", "", "", "", ""]); parent.setFirstColumnSpanned(True); self.tree.addTopLevelItem(parent)
            for r in recs:
                amount = self._fmt_money(r.net_amount) if (self.salary_unlocked and r.net_amount is not None) else "********"
                item = QTreeWidgetItem([r.employee_code, r.employee_name, r.department, r.job_title, r.employee_email, amount, r.validation_status, r.send_status, ""])
                item.setData(0, Qt.UserRole, r.id); item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                if r.sendable: item.setCheckState(8, Qt.Checked if r.selected else Qt.Unchecked)
                else:
                    item.setCheckState(8, Qt.Unchecked); item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                parent.addChild(item)
            parent.setExpanded(True)
        self.tree.blockSignals(False)
        self._update_stats(filtered)

    def _fmt_money(self, value) -> str:
        return f"{int(round(float(value))):,}".replace(",", ".") + " VNĐ"

    def _match_filter(self, r: RecipientView) -> bool:
        q = self.search.text().strip().lower()
        if q and q not in r.employee_code.lower() and q not in r.employee_name.lower(): return False
        if self.filter_dept.currentText() not in ("", "All") and r.department != self.filter_dept.currentText(): return False
        if self.filter_data.currentText() != "All" and r.validation_status != self.filter_data.currentText(): return False
        if self.filter_send.currentText() != "All" and r.send_status != self.filter_send.currentText(): return False
        return True

    def _update_stats(self, recs: list[RecipientView]) -> None:
        total = len(recs); valid = sum(1 for r in recs if r.sendable); missing_email = sum(1 for r in recs if not r.employee_email)
        data_error = sum(1 for r in recs if r.validation_status == "error"); selected = sum(1 for r in recs if r.selected)
        sent = sum(1 for r in recs if r.send_status == "Sent"); failed = sum(1 for r in recs if r.send_status == "Failed"); pending = sum(1 for r in recs if r.send_status == "Pending")
        total_net = sum((r.net_amount or 0) for r in recs); selected_net = sum((r.net_amount or 0) for r in recs if r.selected)
        net_mask = (self._fmt_money(total_net), self._fmt_money(selected_net)) if self.salary_unlocked else ("********", "********")
        self.stats.setText(f"Total:{total} | Valid sendable:{valid} | Missing email:{missing_email} | Data error:{data_error} | Selected:{selected} | Sent:{sent} | Failed:{failed} | Pending:{pending} | Total net:{net_mask[0]} | Selected net:{net_mask[1]}")

    def unlock_salary(self) -> None:
        pw, ok = QInputDialog.getText(self, "Mở khóa", "Nhập mật khẩu xem lương:", QLineEdit.Password)
        if ok and self.settings_repo.verify_salary_password(pw): self.salary_unlocked = True; self.render()
        elif ok: QMessageBox.warning(self, "Sai mật khẩu", "Mật khẩu không đúng.")

    def lock_salary(self) -> None:
        self.salary_unlocked = False; self.render()

    def on_item_changed(self, item: QTreeWidgetItem, col: int) -> None:
        if col != 8 or item.parent() is None: return
        rid = item.data(0, Qt.UserRole)
        if rid is None: return
        selected = item.checkState(8) == Qt.Checked
        self.preview_repo.update_selected(rid, selected)
        for r in self.recipients:
            if r.id == rid: r.selected = selected
        self._update_stats([r for r in self.recipients if self._match_filter(r)])

    def on_item_double_clicked(self, item: QTreeWidgetItem, col: int) -> None:
        if item.parent() is None: return
        rid = item.data(0, Qt.UserRole)
        r = next((x for x in self.recipients if x.id == rid), None)
        if not r: return
        if col == 4:
            if r.employee_email and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", r.employee_email): return
            email, ok = QInputDialog.getText(self, "Sửa email", "Nhập email:", text=r.employee_email)
            if not ok: return
            email = email.strip(); valid = re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None
            self.preview_repo.update_email(rid, email, "valid" if valid else "error", valid); self.reload_data()
        elif col in (0, 1):
            self.open_payslip_preview(rid)

    def open_payslip_preview(self, recipient_id: int) -> None:
        if not self.salary_unlocked:
            QMessageBox.warning(self, "Bị khóa", "Vui lòng mở khóa dữ liệu lương trước khi xem payslip preview.")
            return
        data = self.preview_repo.get_payslip_data(recipient_id)
        if not data:
            return
        settings = self.settings_repo.get()

        dlg = QDialog(self); dlg.setWindowTitle("Payslip Preview"); dlg.resize(900, 1000)
        lay = QVBoxLayout(dlg)
        page = QFrame(); page.setStyleSheet("background:#f5f5f5;")
        page_l = QVBoxLayout(page)
        receipt = QFrame(); receipt.setStyleSheet("background:white;border:1px solid #ddd;")
        receipt.setFixedWidth(450)
        receipt_l = QVBoxLayout(receipt)

        receipt_l.addWidget(QLabel(f"<h3>{settings.company_name}</h3>"))
        receipt_l.addWidget(QLabel(f"Tháng lương: {data.payroll_month}"))
        receipt_l.addWidget(QLabel(f"Mã NV: {data.employee_code}"))
        receipt_l.addWidget(QLabel(f"Họ và tên: {data.employee_name}"))
        receipt_l.addWidget(QLabel(f"Chức vụ: {data.job_title}"))
        receipt_l.addWidget(QLabel(f"Phòng ban: {data.department}"))

        form = QFormLayout()
        for field in PAYROLL_FIELDS:
            val = data.payroll_data.get(field, 0)
            text = self._fmt_money(val) if "Lương" in field or field in ["Phụ cấp ăn trưa", "Phụ cấp trang phục", "Phụ cấp điện thoại", "Đóng góp trách nhiệm", "BHXH", "BHYT", "BHTN", "Thuế TNCN", "Tạm ứng", "Thực nhận"] else str(val)
            form.addRow(field, QLabel(text))
        receipt_l.addLayout(form)
        receipt_l.addWidget(QLabel(settings.payslip_security_note))
        receipt_l.addWidget(QLabel(settings.payslip_thank_you_text))

        page_l.addWidget(receipt, alignment=Qt.AlignHCenter)
        lay.addWidget(page)
        dlg.exec()
