@echo off
REM Start only the Dashboard

echo ================================================
echo OctoBoard Dashboard - Starting
echo ================================================
echo.

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run start.bat first to set up the system.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Dashboard opening in browser...
echo.

streamlit run dashboard.py

pause
