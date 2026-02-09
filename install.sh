#!/bin/bash

echo "========================================"
echo "Music Audio Captioner - Installer"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "Python found!"
python3 --version
echo

# Check Python version
python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3.9 or higher is required!"
    echo "Please upgrade your Python installation"
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo
echo "Activating virtual environment..."
source venv/bin/activate

echo
echo "Upgrading pip..."
pip install --upgrade pip

echo
echo "Installing PyTorch (this may take a while)..."
echo

python3 install_pytorch.py
if [ $? -ne 0 ]; then
    echo
    echo "ERROR: PyTorch installation failed!"
    echo "Please check the error messages above"
    exit 1
fi

echo
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo
echo "To run the Music Audio Captioner:"
echo "1. Run: ./run.sh"
echo "   OR"
echo "2. Run: source venv/bin/activate && python music_captioner.py"
echo
echo "The application will open at: http://localhost:7865"
echo
echo "NOTES:"
echo "- First run will download the AI model (~14GB)"
echo "- GPU recommended for faster processing"
echo "- Port 7865 will be used (different from default Gradio port)"
echo
