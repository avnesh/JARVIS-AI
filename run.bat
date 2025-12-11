@echo off
echo Starting Jarvis AI...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

REM Navigate to script directory then GUI
cd /d "%~dp0\GUI"

REM Check if dependencies are installed (simple check)
pip show kivy >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Run the application
echo Launching Application...
python main.py

pause
