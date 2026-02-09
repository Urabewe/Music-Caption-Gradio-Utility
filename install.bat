@echo off
echo ========================================
echo Music Audio Captioner - Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.9 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

REM Check Python version
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"
if %errorlevel% neq 0 (
    echo ERROR: Python 3.9 or higher is required!
    echo Please upgrade your Python installation
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing PyTorch (this may take a while)...
echo.
python install_pytorch.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: PyTorch installation failed!
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To run the Music Audio Captioner:
echo 1. Double-click "run.bat"
echo    OR
echo 2. Run this command: venv\Scripts\activate.bat ^&^& python music_captioner.py
echo.
echo The application will open at: http://localhost:7865
echo.
echo NOTES:
echo - First run will download the AI model (~14GB)
echo - GPU recommended for faster processing
echo - Port 7865 will be used (different from default Gradio port)
echo.
pause
