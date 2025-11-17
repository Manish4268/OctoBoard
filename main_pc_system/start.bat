@echo off
REM Startup script for Main PC System

echo ================================================
echo OctoBoard Main PC System - Startup
echo ================================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo.
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo.
) else (
    call venv\Scripts\activate.bat
)

echo Virtual environment activated.
echo.

REM Check Python version
python --version
echo.

REM Create data directory if not exists
if not exist "C:\OctoBoard_Data" (
    echo Creating data directory: C:\OctoBoard_Data
    mkdir "C:\OctoBoard_Data"
    echo.
)

echo ================================================
echo Starting File Receiver and Dashboard
echo ================================================
echo.
echo File Receiver will run on: http://192.168.1.100:8000
echo Dashboard will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop both services
echo.

REM Start file receiver in background
start "OctoBoard File Receiver" cmd /k "venv\Scripts\activate.bat && python -m uvicorn file_receiver:app --host 0.0.0.0 --port 8000"

REM Wait for file receiver to start
timeout /t 3 /nobreak > nul

REM Start dashboard
start "OctoBoard Dashboard" cmd /k "venv\Scripts\activate.bat && streamlit run dashboard.py"

echo.
echo ================================================
echo Both services started successfully!
echo ================================================
echo.
echo File Receiver: Check terminal "OctoBoard File Receiver"
echo Dashboard: Check terminal "OctoBoard Dashboard"
echo.
echo To stop services: Close both terminal windows
echo.

pause
