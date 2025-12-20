@echo off
cd /d %~dp0

REM .env 파일 확인
if not exist .env (
    echo [ERROR] .env file not found at %~dp0.env
    echo Please create .env file with required environment variables.
    echo Result: FAILED - .env Not Found >> daily_sync.log
    exit /b 1
)

REM 가상환경이 있으면 활성화, 없으면 시스템 Python 사용
if exist .venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [INFO] No virtual environment found, using system Python...
)

REM Python 스크립트 실행
echo [INFO] Starting daily_sync.py at %date% %time%
python daily_sync.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] daily_sync.py failed with error code %ERRORLEVEL%
    echo Result: FAILED - Python Script Error >> daily_sync.log
    exit /b %ERRORLEVEL%
)

echo [INFO] daily_sync.py completed successfully at %date% %time%
exit /b 0
