@echo off
echo ========================================
echo Music Audio Captioner
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Music Audio Captioner...
echo The application will open at: http://localhost:7865
echo.
echo Press Ctrl+C to stop the application
echo.

python music_captioner.py

pause
