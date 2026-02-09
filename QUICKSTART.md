# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Windows Users

1. **Install**: Double-click `install.bat` and wait
2. **Run**: Double-click `run.bat`
3. **Use**: Browser opens automatically at http://localhost:7865

### Linux/Mac Users

1. **Install**: Run `./install.sh` in terminal
2. **Run**: Run `./run.sh` in terminal
3. **Use**: Open http://localhost:7865 in your browser

---

## 📝 First Time Setup

**What happens during installation:**
- Creates isolated Python environment
- Installs PyTorch and dependencies
- Takes 10-30 minutes depending on internet speed

**First run (one-time):**
- Downloads AI model (~14GB)
- Takes 5-15 minutes
- Model is cached for future use

---

## 🎵 Quick Examples

### Caption a Single Song
1. Go to "Single File" tab
2. Upload your song
3. Click "Generate Caption"
4. Caption appears instantly!

### Caption an Entire Album
1. Go to "Batch Processing" tab
2. Enter folder path: `C:\Music\MyAlbum`
3. Click "Process Folder"
4. All songs get captioned automatically!

---

## ⚙️ Customization

### Change the Port
Edit `music_captioner.py`, line at bottom:
```python
app.launch(server_port=7865, share=False)
```

### Customize the Default Prompt
Edit `config.py`:
```python
DEFAULT_PROMPT = "Your custom prompt here"
```

### Process Different File Types
In batch mode, change extensions:
```
.mp3, .wav, .flac, .m4a
```

---

## 💡 Tips

- **GPU = Faster**: If you have NVIDIA GPU, processing is much faster
- **Batch = Efficient**: Process multiple files at once
- **Prompt = Control**: Customize prompts to get different styles of captions
- **Save = Automatic**: Captions save automatically as .txt files

---

## ❓ Common Questions

**Q: Where are captions saved?**
A: Same folder as the audio file, same name with .txt extension

**Q: Can I change the caption format?**
A: Yes! Modify the prompt to change what information is included

**Q: How long does processing take?**
A: With GPU: 5-10 seconds per song
   Without GPU: 30-60 seconds per song

**Q: Can I run multiple instances?**
A: Yes! Each instance needs a different port number

---

## 🆘 Need Help?

1. Check `README.md` for detailed troubleshooting
2. Make sure Python 3.9+ is installed
3. Ensure you have 20GB free disk space
4. Try running installer again if it failed

---

**Enjoy your music captioning! 🎵**
