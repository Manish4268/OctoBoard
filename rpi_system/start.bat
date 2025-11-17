@echo off
REM Startup script for Raspberry Pi System

echo ================================================
echo OctoBoard RPi System - Startup
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

REM Detect simulation mode
set /p RUN_MODE="Run in SIMULATION mode? (y/n): "
if /i "%RUN_MODE%"=="y" (
    echo.
    echo *** SIMULATION MODE ENABLED ***
    set OCTOBOARD_SIMULATION=True
    echo This will use mock hardware for testing.
    echo.
) else (
    echo.
    echo *** HARDWARE MODE ***
    echo This will use actual Raspberry Pi hardware.
    echo Make sure you are running on a Raspberry Pi!
    echo.
)

echo ================================================
echo Starting API Server
echo ================================================
echo.
echo Server will run on: http://0.0.0.0:8001
echo Main PC should be at: http://192.168.1.100:8000
echo.
echo Press Ctrl+C to stop the server
echo.

python api_server.py

pause
