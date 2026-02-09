# Model Loading Guide

## 🤖 How the Model Works

The Music Audio Captioner uses **Qwen2-Audio-7B-Instruct**, a 7 billion parameter AI model that can understand and describe audio.

---

## 📥 Model Loading Options

### Option 1: Automatic Download (Recommended)

**What happens:**
- Model downloads automatically on first run
- Downloads from Hugging Face Hub
- Cached locally for future use

**Steps:**
1. Run the application normally with `run.bat` or `./run.sh`
2. Model downloads in the background (takes 10-30 minutes)
3. Application starts when download completes
4. Future runs load instantly from cache

**Where is it cached?**
- Windows: `C:\Users\YourName\.cache\huggingface\hub\`
- Linux/Mac: `~/.cache/huggingface/hub/`

### Option 2: Manual Pre-Download

If you want to download the model before running the app:

**Windows:**
```batch
download_model.bat
```

**Linux/Mac:**
```bash
./download_model.sh
```

This is useful if:
- You want to download on faster internet
- You're preparing for offline use
- You want to verify the download separately

### Option 3: Use Local Model Files

If you already have the model downloaded elsewhere:

1. Create a `models` folder in the application directory
2. Copy the model files to `models/Qwen2-Audio-7B-Instruct/`
3. Edit `music_captioner.py` line 21 to point to local path:

```python
MODEL_PATH = "./models/Qwen2-Audio-7B-Instruct"
```

---

## 📊 Model Details

| Property | Value |
|----------|-------|
| Model Name | Qwen2-Audio-7B-Instruct |
| Size | ~14GB (compressed) |
| Parameters | 7 billion |
| Developer | Alibaba Cloud (Qwen Team) |
| License | Apache 2.0 |
| Source | https://huggingface.co/Qwen/Qwen2-Audio-7B-Instruct |

---

## 🔍 What Gets Downloaded?

When the model downloads, you'll get:
- **Model weights** (~13GB) - The AI model itself
- **Tokenizer** (~2MB) - Text processing
- **Processor** (~1MB) - Audio processing
- **Config files** (~10KB) - Model settings

Total: **~14GB**

---

## ⚡ Loading Speed

**First Run (Download + Load):**
- With fast internet: 10-20 minutes
- With slow internet: 30-60 minutes

**Subsequent Runs (Load from Cache):**
- With GPU: 30-60 seconds
- With CPU: 1-2 minutes

---

## 🛠️ Troubleshooting

### "Connection timeout" or "Download failed"

**Solution 1: Retry**
```bash
# Downloads can resume from where they stopped
# Just run the application or download script again
```

**Solution 2: Use HF Mirror (China users)**
```bash
# Set environment variable before running
export HF_ENDPOINT=https://hf-mirror.com
```

**Solution 3: Manual download from browser**
1. Visit: https://huggingface.co/Qwen/Qwen2-Audio-7B-Instruct/tree/main
2. Download all files
3. Place in local models folder (see Option 3 above)

### "Out of disk space"

**Check space:**
```bash
# Windows
dir C:\Users\%USERNAME%\.cache\huggingface

# Linux/Mac
du -sh ~/.cache/huggingface
```

**Free up space:**
- Need at least 20GB free (14GB model + 6GB working space)
- Delete unused Hugging Face models from cache
- Or change cache location (see below)

### "Model not loading" or "CUDA out of memory"

**For GPU memory issues:**
```python
# Edit music_captioner.py, change line 26:
torch_dtype=torch.float32  # Use full precision
# Or force CPU:
device_map="cpu"
```

**For RAM issues:**
- Close other applications
- Minimum 8GB RAM required, 16GB recommended
- Consider using a smaller model (if available)

---

## 🔧 Advanced Configuration

### Change Cache Location

**Windows:**
```batch
set HF_HOME=D:\AI_Models\huggingface
```

**Linux/Mac:**
```bash
export HF_HOME=/path/to/your/cache
```

Add this to your environment variables to make it permanent.

### Offline Mode

Once model is downloaded, you can run offline:

```python
# Edit music_captioner.py
# Add after imports:
import os
os.environ['TRANSFORMERS_OFFLINE'] = '1'
```

### Use Different Model

To use a different audio model (if you find one):

Edit `config.py`:
```python
MODEL_NAME = "YourOrg/your-audio-model"
```

---

## 📝 Model License & Attribution

**License:** Apache License 2.0
- Free for commercial and personal use
- No attribution required (but appreciated)
- Model provided "as-is"

**Citation:**
```
@article{qwen2audio,
  title={Qwen2-Audio Technical Report},
  author={Qwen Team},
  year={2024}
}
```

---

## 🆘 Still Having Issues?

1. **Check internet connection** - Model downloads from internet
2. **Check disk space** - Need 20GB free
3. **Check Python version** - Need 3.9+
4. **Try manual download** - Use `download_model.bat` or `.sh`
5. **Check firewall** - May block Hugging Face downloads
6. **Try different network** - Some networks block HuggingFace

---

**Questions? Check README.md for more troubleshooting help!**
