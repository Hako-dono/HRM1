from ui.screens.base_screen import BasePlaceholderScreen


class DashboardScreen(BasePlaceholderScreen):
    def __init__(self) -> None:
        super().__init__(
            "Dashboard",
            "Màn hình tổng quan cho Smart Payslip sẽ hiển thị trạng thái xử lý, phiên gửi gần đây và số liệu nhanh.",
        )
