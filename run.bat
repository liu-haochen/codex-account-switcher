@echo off
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%~dp0codex_account_switcher.py"
) else (
    python "%~dp0codex_account_switcher.py"
)
