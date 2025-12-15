@echo off
cd /d %~dp0
call .env
if not exist .venv (
    echo Virtual environment not found. Please create one.
    pause
    exit /b
)
call .venv\Scripts\activate.bat
python daily_sync.py
pause
