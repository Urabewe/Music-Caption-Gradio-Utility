@echo off
echo ========================================
echo Manual Model Download
echo ========================================
echo.
echo This script will pre-download the AI model
echo Model size: ~14GB
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
echo Downloading model from Hugging Face...
echo This may take 10-30 minutes depending on your internet speed
echo.

python -c "from transformers import AutoProcessor, Qwen2AudioForConditionalGeneration; print('Downloading processor...'); AutoProcessor.from_pretrained('Qwen/Qwen2-Audio-7B-Instruct', trust_remote_code=True); print('Downloading model...'); Qwen2AudioForConditionalGeneration.from_pretrained('Qwen/Qwen2-Audio-7B-Instruct', trust_remote_code=True); print('Download complete!')"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Model downloaded successfully!
    echo ========================================
    echo.
    echo The model is cached at:
    echo %USERPROFILE%\.cache\huggingface\hub
    echo.
    echo You can now run the application with run.bat
) else (
    echo.
    echo ========================================
    echo Download failed!
    echo ========================================
    echo.
    echo Please check:
    echo 1. Internet connection
    echo 2. Available disk space (~14GB needed)
    echo 3. Firewall settings
    echo.
    echo You can try running this script again
)

echo.
pause
