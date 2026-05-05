from __future__ import annotations

import re
from collections import defaultdict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox, QPushButton, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout, QWidget, QInputDialog)

from data.preview_repository import PreviewRepository, RecipientView
from data.settings_repository import SettingsRepository

COLUMNS = ["Mã NV", "Họ và tên", "Phòng ban", "Chức vụ", "Email", "Thực nhận", "Data status", "Send status", "Chọn gửi"]


class PreviewScreen(QWidget):
    def __init__(self, preview_repo: PreviewRepository, settings_repo: SettingsRepository) -> None:
        super().__init__()
        self.preview_repo = preview_repo
        self.settings_repo = settings_repo
        self.salary_unlocked = False
        self.recipient_by_item: dict[int, RecipientView] = {}
        self.current_session_id: int | None = None
        self._build_ui()
        self.reload_data()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        title = QLabel("Preview & chọn gửi")
        title.setStyleSheet("font-size:24px;font-weight:700;")
        root.addWidget(title)

        toolbar = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("Tìm theo Mã NV / Họ tên")
        self.search.textChanged.connect(self.render)
        self.filter_dept = QComboBox(); self.filter_dept.currentTextChanged.connect(self.render)
        self.filter_data = QComboBox(); self.filter_data.addItems(["All", "valid", "warning", "error"]); self.filter_data.currentTextChanged.connect(self.render)
        self.filter_send = QComboBox(); self.filter_send.addItems(["All", "Pending", "Sent", "Failed"]); self.filter_send.currentTextChanged.connect(self.render)
        reload_btn = QPushButton("Reload"); reload_btn.clicked.connect(self.reload_data)
        unlock_btn = QPushButton("Hiện số tiền"); unlock_btn.clicked.connect(self.unlock_salary)
        lock_btn = QPushButton("Khóa dữ liệu lương"); lock_btn.clicked.connect(self.lock_salary)
        for w in [self.search, self.filter_dept, self.filter_data, self.filter_send, reload_btn, unlock_btn, lock_btn]: toolbar.addWidget(w)
        root.addLayout(toolbar)

        self.stats = QLabel()
        root.addWidget(self.stats)

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
        self.tree.blockSignals(True)
        self.tree.clear(); self.recipient_by_item.clear()
        grouped = defaultdict(list)
        filtered = [r for r in self.recipients if self._match_filter(r)]
        for r in filtered: grouped[r.department or "(No phòng ban)"].append(r)

        for dept, recs in grouped.items():
            parent = QTreeWidgetItem([dept, "", dept, "", "", "", "", "", ""])
            parent.setFirstColumnSpanned(True)
            self.tree.addTopLevelItem(parent)
            for r in recs:
                amount = f"{r.net_amount:,.0f}" if (self.salary_unlocked and r.net_amount is not None) else "********"
                item = QTreeWidgetItem([r.employee_code, r.employee_name, r.department, r.job_title, r.employee_email, amount, r.validation_status, r.send_status, ""])
                item.setData(0, Qt.UserRole, r.id)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                if r.sendable:
                    item.setCheckState(8, Qt.Checked if r.selected else Qt.Unchecked)
                else:
                    item.setCheckState(8, Qt.Unchecked)
                    item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                parent.addChild(item)
                self.recipient_by_item[r.id] = r
            parent.setExpanded(True)

        self.tree.blockSignals(False)
        self._update_stats(filtered)

    def _match_filter(self, r: RecipientView) -> bool:
        q = self.search.text().strip().lower()
        if q and q not in r.employee_code.lower() and q not in r.employee_name.lower(): return False
        if self.filter_dept.currentText() not in ("", "All") and r.department != self.filter_dept.currentText(): return False
        if self.filter_data.currentText() != "All" and r.validation_status != self.filter_data.currentText(): return False
        if self.filter_send.currentText() != "All" and r.send_status != self.filter_send.currentText(): return False
        return True

    def _update_stats(self, recs: list[RecipientView]) -> None:
        total = len(recs); valid = sum(1 for r in recs if r.sendable)
        missing_email = sum(1 for r in recs if not r.employee_email)
        data_error = sum(1 for r in recs if r.validation_status == "error")
        selected = sum(1 for r in recs if r.selected)
        sent = sum(1 for r in recs if r.send_status == "Sent")
        failed = sum(1 for r in recs if r.send_status == "Failed")
        pending = sum(1 for r in recs if r.send_status == "Pending")
        total_net = sum((r.net_amount or 0) for r in recs)
        selected_net = sum((r.net_amount or 0) for r in recs if r.selected)
        net_mask = (f"{total_net:,.0f}", f"{selected_net:,.0f}") if self.salary_unlocked else ("********", "********")
        self.stats.setText(f"Total:{total} | Valid sendable:{valid} | Missing email:{missing_email} | Data error:{data_error} | Selected:{selected} | Sent:{sent} | Failed:{failed} | Pending:{pending} | Total net:{net_mask[0]} | Selected net:{net_mask[1]}")

    def unlock_salary(self) -> None:
        pw, ok = QInputDialog.getText(self, "Mở khóa", "Nhập mật khẩu xem lương:", QLineEdit.Password)
        if not ok:
            return
        if self.settings_repo.verify_salary_password(pw):
            self.salary_unlocked = True
            self.render()
        else:
            QMessageBox.warning(self, "Sai mật khẩu", "Mật khẩu không đúng.")

    def lock_salary(self) -> None:
        self.salary_unlocked = False
        self.render()

    def on_item_changed(self, item: QTreeWidgetItem, col: int) -> None:
        if col != 8 or item.parent() is None:
            return
        rid = item.data(0, Qt.UserRole)
        if rid is None:
            return
        selected = item.checkState(8) == Qt.Checked
        self.preview_repo.update_selected(rid, selected)
        for r in self.recipients:
            if r.id == rid: r.selected = selected
        self._update_stats([r for r in self.recipients if self._match_filter(r)])

    def on_item_double_clicked(self, item: QTreeWidgetItem, col: int) -> None:
        if col != 4 or item.parent() is None:
            return
        rid = item.data(0, Qt.UserRole)
        r = next((x for x in self.recipients if x.id == rid), None)
        if not r:
            return
        if r.employee_email and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", r.employee_email):
            return
        email, ok = QInputDialog.getText(self, "Sửa email", "Nhập email:", text=r.employee_email)
        if not ok:
            return
        email = email.strip()
        valid = re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None
        status = "valid" if valid else "error"
        self.preview_repo.update_email(rid, email, status, valid)
        self.reload_data()
