#!/bin/bash

echo "========================================"
echo "Music Audio Captioner"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run ./install.sh first"
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo
echo "Starting Music Audio Captioner..."
echo "The application will open at: http://localhost:7865"
echo
echo "Press Ctrl+C to stop the application"
echo

python music_captioner.py
