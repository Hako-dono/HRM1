from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class BasePlaceholderScreen(QWidget):
    def __init__(self, title: str, description: str) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(8)

        heading = QLabel(title)
        heading.setStyleSheet("font-size: 24px; font-weight: 700; color: #111827;")

        body = QLabel(description)
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        body.setStyleSheet("font-size: 14px; color: #4b5563;")

        layout.addWidget(heading)
        layout.addWidget(body)
        layout.addStretch(1)
