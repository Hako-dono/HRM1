from ui.screens.base_screen import BasePlaceholderScreen


class HistoryScreen(BasePlaceholderScreen):
    def __init__(self) -> None:
        super().__init__(
            "Lịch sử gửi",
            "Màn hình lịch sử gửi email payslip (lọc, xem chi tiết, resend) sẽ được thêm ở milestone tiếp theo.",
        )
