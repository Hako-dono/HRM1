# Smart Payslip (Milestone 0)

Smart Payslip là ứng dụng desktop nội bộ chạy local trên Windows cho phòng HR của BSM.

## Milestone 0 scope

Milestone 0 tập trung vào skeleton ứng dụng:
- Cấu trúc project Python rõ ràng.
- Main window khởi động full-screen.
- Sidebar điều hướng với các màn hình placeholder:
  1. Dashboard
  2. Import dữ liệu
  3. Preview & chọn gửi
  4. Lịch sử gửi
  5. Settings

> Chưa triển khai logic nghiệp vụ ở milestone này.

## Project structure

```
app/
  main.py
  core/
  data/
  resources/
  ui/
    main_window.py
    screens/
      base_screen.py
      dashboard_screen.py
      import_screen.py
      preview_screen.py
      history_screen.py
      settings_screen.py
    widgets/
requirements.txt
README.md
.gitignore
```

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python app/main.py
```

## Notes

- App hiện chỉ là UI khung.
- Các chức năng import Excel, generate PDF, gửi email SMTP, SQLite history, resend/pause/resume, batch print sẽ được triển khai ở milestone sau.
