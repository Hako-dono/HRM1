from __future__ import annotations

from PySide6.QtCore import QObject, QEvent, QTimer, Signal

from data.settings_repository import SettingsRepository


class SalaryLockService(QObject):
    lock_changed = Signal(bool)

    def __init__(self, settings_repo: SettingsRepository) -> None:
        super().__init__()
        self.settings_repo = settings_repo
        self.locked = True
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.force_lock)
        self.reset_inactivity_timer()

    def eventFilter(self, _obj, event):
        if event.type() in (QEvent.MouseMove, QEvent.KeyPress, QEvent.MouseButtonPress):
            self.reset_inactivity_timer()
        return False

    def reset_inactivity_timer(self) -> None:
        minutes = self.settings_repo.get().auto_lock_minutes
        if minutes not in (1, 3, 5, 10, 15, 30):
            minutes = 5
        self.timer.start(minutes * 60 * 1000)

    def try_unlock(self, password: str) -> bool:
        if self.settings_repo.verify_salary_password(password):
            self.locked = False
            self.lock_changed.emit(self.locked)
            self.reset_inactivity_timer()
            return True
        return False

    def force_lock(self) -> None:
        self.locked = True
        self.lock_changed.emit(self.locked)

    def is_locked(self) -> bool:
        return self.locked
