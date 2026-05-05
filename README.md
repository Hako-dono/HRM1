# Smart Payslip

## Dev mode
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

## Build Windows .exe (PyInstaller)
```bat
build_windows.bat
```
Output: `dist\SmartPayslip\SmartPayslip.exe`

## App data location
- Dev mode: `<repo>\app_data\`
- Packaged exe: `<folder_chứa_exe>\app_data\`

Contains:
- `smart_payslip.db`
- `sessions\<session_code>\source|pdf|print|export`

## Packaging notes
- `SmartPayslip.spec` includes app resources (`app/resources/*`).
- DB/sessions/export paths are resolved at runtime next to executable.
- Generated payslips and logs remain writable in local `app_data`.

## Known MVP limitations
- UI and flow are MVP-level; not production-hardened.
- Limited error handling and no background worker thread for long sends.
- Resend "new payroll" mode is simplified.
- No forgot-password/reset flow.
