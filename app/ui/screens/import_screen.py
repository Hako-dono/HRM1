from ui.screens.base_screen import BasePlaceholderScreen


class ImportScreen(BasePlaceholderScreen):
    def __init__(self) -> None:
        super().__init__(
            "Import dữ liệu",
            "Màn hình này sẽ dùng để nhập file payroll và danh sách email nhân viên ở các milestone tiếp theo.",
        )
