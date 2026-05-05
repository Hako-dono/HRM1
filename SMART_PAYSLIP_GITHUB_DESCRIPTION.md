# Smart Payslip

Smart Payslip is a Windows local desktop application for BSM's HR team to generate, preview, send, and manage salary payslips automatically.

The MVP focuses on sending finalized monthly payslips to employees via email, using payroll data that has already been calculated and approved by HR.

## Purpose

Smart Payslip helps HR reduce manual work when sending salary slips one by one.

Instead of manually creating and emailing individual payslips, HR can:

- Import a finalized payroll Excel file.
- Import an employee email list.
- Map employees by employee code.
- Preview payroll data before sending.
- Select employees to receive payslips.
- Generate password-protected PDF payslips.
- Send payslips via Gmail SMTP.
- Track sending history in a local database.
- Resend payslips when needed.
- Generate a batch PDF for printing.

## MVP Scope

### Core Features

- Local Windows desktop app.
- Import payroll Excel file.
- Import employee email Excel file.
- Map employees by `Mã NV`.
- Validate required columns and payroll data.
- Preview employee list grouped by department.
- Search and filter employees.
- Mask salary amounts by default.
- Unlock salary data with HR password.
- Preview individual payslip inside the app.
- Generate individual PDF payslips.
- Protect each employee PDF with password = `Mã NV`.
- Send payslips via Gmail using Gmail App Password.
- Send emails one by one with configurable delay.
- Log sending results in local SQLite database.
- Support send session management: Draft, Sending, Paused, Cancelled, Completed.
- Pause, cancel, and resume sending sessions.
- View sending history by month or session.
- Resend payslips from history.
- Generate one combined PDF for batch printing.
- Export sending logs to Excel when needed.
- Configure email templates, storage folder, delay, and salary lock settings.

## Input Files

### Payroll File

The payroll file is exported from Google Sheet to Excel.

The MVP uses a fixed format based on the approved payroll template.

Required columns include:

- `Mã NV`
- `Họ và tên`
- `Chức vụ`
- `Phòng ban`
- `Lương cơ bản`
- `Ngày công chuẩn`
- `Ngày công thực tế`
- `Thực nhận`

Other payroll columns may include:

- `Phụ cấp ăn trưa`
- `Phụ cấp trang phục`
- `Phụ cấp điện thoại`
- `Lương hiệu suất`
- `Lương làm thêm giờ`
- `Đóng góp trách nhiệm`
- `BHXH`
- `BHYT`
- `BHTN`
- `Thuế TNCN`
- `Tạm ứng`

### Employee File

The employee file uses a fixed format:

```text
Mã NV | Email | Tình trạng
```

The MVP maps payroll data and employee email by `Mã NV`.

## Payslip PDF Rules

- PDF format: A4.
- Design style: supermarket receipt style.
- Individual PDF password: employee code / `Mã NV`.
- Batch print PDF password: HR salary-view password.
- File name format:

```text
YYYY-MM_MãNV_HoTenKhongDau.pdf
```

Example:

```text
2026-02_BSM001_NguyenVanA.pdf
```

## Email Rules

Default subject:

```text
[BSM] Phiếu lương tháng {thang_luong} - {ho_ten}
```

Default body:

```text
Kính gửi Anh/Chị {ho_ten},

Phòng HCNS gửi Anh/Chị phiếu lương tháng {thang_luong} trong file đính kèm.

Phiếu lương được bảo mật bằng mật khẩu. Mật khẩu mở file là Mã nhân viên của Anh/Chị.

Nếu có thắc mắc, Anh/Chị vui lòng phản hồi lại email này.

Trân trọng,
Phòng HCNS
```

## Recommended Tech Stack

- Python
- PySide6
- SQLite
- openpyxl
- pypdf
- smtplib
- PyInstaller

## MVP Development Approach

Development should be done milestone by milestone.

Recommended order:

1. Project setup
2. Database and Settings
3. Excel import and validation
4. Preview screen
5. Payslip preview
6. PDF generation and encryption
7. Email sending
8. Pause, cancel, and resume
9. History and resend
10. Security lock and auto-lock
11. Export log
12. Windows packaging

## Out of Scope for MVP

The following features are intentionally excluded from the MVP:

- Auto-calculate salary from timesheet.
- Send attendance sheet for employee confirmation.
- Track whether employees have opened the payslip.
- Direct Google Sheet API integration.
- Multi-company support.
- Logo on payslip.
- Flexible column mapping.
- Edit payroll data inside the app.
- CC/BCC email.
- Backup and restore.
- In-app user guide.
- Auto update/version checking.
- Automatic password reset.
- Automatic retry on failed email sending.

## Definition of Done

The MVP is considered complete when HR can:

1. Open the app on Windows.
2. Configure sender email and HR salary-view password.
3. Import payroll and employee files.
4. Preview mapped employee salary data.
5. Select employees to send.
6. Generate password-protected PDF payslips.
7. Send payslips via email.
8. Pause, cancel, and resume send sessions.
9. View sending history.
10. Resend payslips.
11. Generate batch print PDF.
12. Export sending logs when needed.
13. Run the app in dev mode and later package it as `.exe`.
