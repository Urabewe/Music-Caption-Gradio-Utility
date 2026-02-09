# Music Audio Captioner - Package Contents

## 📦 Complete Installation Package

This package contains everything you need to run the Music Audio Captioner application.

### Files Included:

#### Core Application
- **music_captioner.py** - Main application (runs on port 7865)
- **config.py** - Configuration file for customization
- **requirements.txt** - Python dependencies

#### Windows Installation
- **install.bat** - Windows installer (double-click to install)
- **run.bat** - Windows launcher (double-click to run)
- **download_model.bat** - Pre-download AI model (optional)

#### Linux/Mac Installation  
- **install.sh** - Linux/Mac installer (run with ./install.sh)
- **run.sh** - Linux/Mac launcher (run with ./run.sh)
- **download_model.sh** - Pre-download AI model (optional)

#### Documentation
- **README.md** - Complete documentation with troubleshooting
- **QUICKSTART.md** - Quick start guide for beginners
- **MODEL_LOADING.md** - Detailed guide on model download and loading
- **.gitignore** - Git ignore file (for developers)

---

## 🚀 Quick Install

### Windows
1. Extract the zip file
2. Double-click `install.bat`
3. Wait for installation to complete
4. (Optional) Double-click `download_model.bat` to pre-download the AI model
5. Double-click `run.bat` to start

### Linux/Mac
1. Extract the zip file
2. Open terminal in the folder
3. Run: `chmod +x install.sh run.sh download_model.sh`
4. Run: `./install.sh`
5. (Optional) Run: `./download_model.sh` to pre-download the AI model
6. Run: `./run.sh` to start

**Note:** If you skip the optional download step, the model (~14GB) will download automatically on first run.

---

## 🎯 Key Features

✅ Runs on port **7865** (not the default Gradio port)
✅ Single file and batch processing modes
✅ Automatic caption saving as .txt files
✅ Customizable prompts
✅ GPU acceleration support
✅ Progress tracking for batch operations

---

## 📋 System Requirements

- Python 3.9 or higher
- 8GB RAM minimum (16GB recommended)
- 20GB free disk space
- Optional: NVIDIA GPU with CUDA for faster processing

---

## 🔧 Port Configuration

The application uses **port 7865** by default to avoid conflicts.

To change it, edit `music_captioner.py` line 192:
```python
app.launch(server_port=7865, share=False)
```

Or edit `config.py`:
```python
SERVER_PORT = 7865
```

---

## 📖 More Information

See **README.md** for:
- Detailed installation instructions
- Usage examples
- Troubleshooting guide
- Customization options

See **QUICKSTART.md** for:
- 3-step setup guide
- Quick examples
- Common questions

---

**Ready to start captioning your music! 🎵**
