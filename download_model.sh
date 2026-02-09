#!/bin/bash

echo "========================================"
echo "Manual Model Download"
echo "========================================"
echo
echo "This script will pre-download the AI model"
echo "Model size: ~14GB"
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
echo "Downloading model from Hugging Face..."
echo "This may take 10-30 minutes depending on your internet speed"
echo

python3 -c "
from transformers import AutoProcessor, Qwen2AudioForConditionalGeneration
print('Downloading processor...')
AutoProcessor.from_pretrained('Qwen/Qwen2-Audio-7B-Instruct', trust_remote_code=True)
print('Downloading model...')
Qwen2AudioForConditionalGeneration.from_pretrained('Qwen/Qwen2-Audio-7B-Instruct', trust_remote_code=True)
print('Download complete!')
"

if [ $? -eq 0 ]; then
    echo
    echo "========================================"
    echo "Model downloaded successfully!"
    echo "========================================"
    echo
    echo "The model is cached at:"
    echo "~/.cache/huggingface/hub"
    echo
    echo "You can now run the application with ./run.sh"
else
    echo
    echo "========================================"
    echo "Download failed!"
    echo "========================================"
    echo
    echo "Please check:"
    echo "1. Internet connection"
    echo "2. Available disk space (~14GB needed)"
    echo "3. Firewall settings"
    echo
    echo "You can try running this script again"
fi

echo
