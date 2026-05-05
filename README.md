# Smart Payslip — Milestone 0

Smart Payslip là ứng dụng desktop local trên Windows cho bộ phận HR của BSM.

Milestone 0 chỉ tập trung vào **khung ứng dụng** (UI skeleton), chưa có business logic.

## Tech stack (Milestone 0)
- Python
- PySide6

## Project structure

```text
app/
├─ main.py
├─ core/
│  └─ __init__.py
├─ data/
│  └─ __init__.py
├─ resources/
│  └─ __init__.py
└─ ui/
   ├─ __init__.py
   ├─ main_window.py
   ├─ widgets/
   │  └─ __init__.py
   └─ screens/
      ├─ __init__.py
      ├─ base_screen.py
      ├─ dashboard_screen.py
      ├─ import_screen.py
      ├─ preview_screen.py
      ├─ history_screen.py
      └─ settings_screen.py

requirements.txt
.gitignore
README.md
```

## Development setup

### 1) Prerequisites
- Python 3.10+ (khuyến nghị 3.11)

### 2) Create virtual environment
```bash
python -m venv .venv
```

### 3) Activate environment
**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bat
.venv\Scripts\activate.bat
```

### 4) Install dependencies
```bash
pip install -r requirements.txt
```

### 5) Run app
```bash
python app/main.py
```

## Implemented in Milestone 0
- Main window khởi động full-screen.
- Sidebar/navigation với 5 màn hình:
  1. Dashboard
  2. Import dữ liệu
  3. Preview & chọn gửi
  4. Lịch sử gửi
  5. Settings
- Mỗi màn hình hiển thị placeholder content.

## Intentionally not implemented yet
- Import/parse Excel.
- Generate/encrypt PDF.
- Gmail SMTP sending.
- SQLite and history logic.
- Resend/pause/cancel/resume session logic.
- Any business rules.
