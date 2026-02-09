# 🎵 Music Audio Captioner

Generate detailed descriptions of your music files using AI. This tool uses Qwen2-Audio, Qwen2-Audio 4bit, Qwen-Omni, Ace-Step Captioner models to analyze songs and create captions describing genre, instruments, mood, tempo, and overall sound characteristics.

## Features

- 🎧 **Single File Processing**: Upload and analyze individual audio files
- 📁 **Batch Processing**: Process entire folders of music files at once
- ✏️ **Custom Prompts**: Customize what information you want extracted
- 💾 **Auto-Save**: Automatically saves captions as .txt files alongside your audio files
- 🚀 **GPU Acceleration**: Supports CUDA for faster processing
- 📊 **Progress Tracking**: Real-time progress bars for batch operations

## Requirements

- **Python**: 3.9 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: ~20GB for model and dependencies
- **GPU**: Optional but recommended (NVIDIA GPU with CUDA support for faster processing)

## Installation

The installer automatically detects your system configuration and installs the correct version of PyTorch:
- **CUDA 12.1+** → PyTorch with CUDA 12.1 support
- **CUDA 11.8-12.0** → PyTorch with CUDA 11.8 support  
- **No GPU or older CUDA** → CPU-only PyTorch

### Windows

1. **Install Python** (if not already installed):
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, **CHECK "Add Python to PATH"**

2. **Run the installer**:
   - Double-click `install.bat`
   - The installer will:
     - Detect your CUDA version (if you have an NVIDIA GPU)
     - Install the correct PyTorch build automatically
     - Install all other dependencies
   - Wait for installation to complete (may take 10-30 minutes)

3. **Download the model** (Optional - it auto-downloads on first run):
   - Double-click `download_model.bat` to pre-download the model
   - Or just skip this - the model downloads automatically when you first run the app

4. **Run the application**:
   - Double-click `run.bat`
   - Your browser will open at `http://localhost:7865`
   - First run: Model downloads automatically (~14GB, takes 10-30 minutes)
   - Future runs: Loads instantly from cache

### Linux/Mac

1. **Install Python 3.9+** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt install python3 python3-venv python3-pip
   
   # macOS (using Homebrew)
   brew install python@3.11
   ```

2. **Run the installer**:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
   The installer will automatically detect your CUDA version and install the appropriate PyTorch build.

3. **Download the model** (Optional - it auto-downloads on first run):
   ```bash
   chmod +x download_model.sh
   ./download_model.sh
   ```
   Or just skip this - the model downloads automatically when you first run the app

4. **Run the application**:
   ```bash
   ./run.sh
   ```
   Open your browser at `http://localhost:7865`
   
   First run: Model downloads automatically (~14GB, takes 10-30 minutes)
   Future runs: Loads instantly from cache

## Usage

### Single File Mode

1. Click the **"Single File"** tab
2. Upload an audio file (MP3, WAV, FLAC, M4A, etc.)
3. Optionally customize the prompt
4. Check "Save caption to .txt file" if you want to save the result
5. Click **"Generate Caption"**
6. The caption will appear in the result box

### Batch Processing Mode

1. Click the **"Batch Processing"** tab
2. Enter the full path to your music folder:
   - Windows example: `C:\Users\YourName\Music\MyAlbum`
   - Linux/Mac example: `/home/yourname/Music/MyAlbum`
3. Customize the prompt (will be used for all files)
4. Specify file extensions (e.g., `.mp3, .wav, .flac`)
5. Click **"Process Folder"**
6. Captions will be saved as `.txt` files next to each audio file

### Example Output

For a file named `song.mp3`, a caption file `song.txt` will be created:

```
This is an upbeat electronic dance track featuring synthesizers, drum machines, 
and a pulsing bassline. The genre is progressive house with elements of trance. 
The tempo is approximately 128 BPM with a driving four-on-the-floor beat. 
The mood is energetic and euphoric with atmospheric pads and melodic leads.
```

## Customizing Prompts

You can customize what information is extracted by modifying the prompt. Here are some examples:

### Detailed Analysis
```
Describe this song including its genre, subgenre, instruments, mood, tempo, 
and overall sound characteristics.
```

### Brief Description
```
Provide a brief 2-sentence description of the song's genre and vibe.
```

### Specific Focus
```
What instruments can you hear in this song? Also describe the vocal style if present.
```

### Music Production
```
Analyze this track from a production perspective: describe the mix, effects used, 
and production style.
```

## Port Configuration

This application runs on **port 7865** by default (instead of Gradio's default 7860) to avoid conflicts with other Gradio applications.

To change the port, edit `music_captioner.py` and modify this line:
```python
app.launch(server_port=7865, share=False)
```

## Troubleshooting

### Model Loading Issues

**First run takes forever**
- The model (~14GB) downloads automatically on first run
- Can take 10-30 minutes depending on internet speed
- See `MODEL_LOADING.md` for detailed info

**Model download fails**
- Check internet connection and disk space (~20GB needed)
- Try pre-downloading: run `download_model.bat` (Windows) or `./download_model.sh` (Linux/Mac)
- Downloads can resume if interrupted - just run again
- For China users: Set `HF_ENDPOINT=https://hf-mirror.com` environment variable

**Where is the model stored?**
- Windows: `C:\Users\YourName\.cache\huggingface\hub`
- Linux/Mac: `~/.cache/huggingface/hub`
- See `MODEL_LOADING.md` for how to change cache location

### Installation Issues

**"Python is not installed or not in PATH"**
- Reinstall Python and ensure "Add Python to PATH" is checked
- Or manually add Python to your system PATH

**"Failed to install dependencies"**
- Make sure you have a stable internet connection
- Try running the installer again
- On Linux, you may need to install: `sudo apt install python3-dev build-essential`

### Runtime Issues

**"Out of memory" errors**
- Close other applications to free up RAM
- Try processing fewer files at once
- Use CPU mode if GPU memory is insufficient

**Model download fails**
- Ensure you have ~14GB free disk space
- Check your internet connection
- The model downloads automatically on first run from Hugging Face

**"Audio file not supported"**
- Ensure your audio file is a common format (MP3, WAV, FLAC, M4A)
- Try converting to WAV using a tool like FFmpeg

### Performance Tips

- **GPU is much faster**: If you have an NVIDIA GPU, make sure CUDA is installed
- **Batch processing**: More efficient than processing files one by one
- **File formats**: WAV files process slightly faster than compressed formats

## Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- FLAC (.flac)
- M4A (.m4a)
- OGG (.ogg)
- And most other common audio formats

## Reducing Memory Usage (Quantization)

If you have limited GPU memory (VRAM), you can enable quantization to reduce memory usage:

1. Go to the **"ℹ️ Info"** tab in the web interface
2. Enable **"Enable Quantization"**
3. Choose **4-bit** (~4GB VRAM) or **8-bit** (~7GB VRAM)
4. Click **"Apply Settings"**
5. Restart the application

**Note:** Quantization requires an NVIDIA GPU with CUDA. Quality impact is minimal - most users won't notice a difference.

Alternatively, you can edit `config.py` directly:
```python
USE_QUANTIZATION = True
QUANTIZATION_TYPE = "4bit"  # or "8bit"
```

## Technical Details

- **Model**: Qwen2-Audio-7B-Instruct
- **Model Size**: ~14GB
- **Framework**: PyTorch + Transformers
- **Interface**: Gradio
- **Processing**: Supports both CPU and GPU (CUDA)

## Updating

To update to the latest version:

1. Download the new release
2. Copy your `venv` folder to the new directory (optional, to save time)
3. Run the installer again

## Uninstalling

1. Delete the entire `music-captioner` folder
2. The AI model cache is stored in:
   - Windows: `C:\Users\YourName\.cache\huggingface`
   - Linux/Mac: `~/.cache/huggingface`
   - Delete this folder to remove the downloaded model

## Credits

- **Model**: [Qwen2-Audio by Alibaba Cloud](https://huggingface.co/Qwen/Qwen2-Audio-7B-Instruct)
- **Interface**: [Gradio](https://www.gradio.app/)
- **Framework**: [Hugging Face Transformers](https://huggingface.co/docs/transformers)

## License

This application is provided as-is for personal use. The Qwen2-Audio model has its own license terms - please review them at the [model page](https://huggingface.co/Qwen/Qwen2-Audio-7B-Instruct).

## Support

For issues, questions, or suggestions:
- Check the troubleshooting section above
- Review the Qwen2-Audio documentation
- Check Gradio documentation for interface issues

---

**Happy Music Captioning! 🎵**
