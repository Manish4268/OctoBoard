@echo off
REM Start only the File Receiver

echo ================================================
echo OctoBoard File Receiver - Starting
echo ================================================
echo.

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run start.bat first to set up the system.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo File Receiver starting on http://0.0.0.0:8000
echo.

python -m uvicorn file_receiver:app --host 0.0.0.0 --port 8000 --reload

pause
