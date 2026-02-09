# Alternative Models & Quantization Guide

## 🎯 Understanding Model Formats

### What DOESN'T Work with This App

**❌ GGUF Format (llama.cpp)**
- Used by: Ollama, LM Studio, llama.cpp
- File extension: `.gguf`
- **Not compatible** with this app (uses PyTorch/Transformers, not llama.cpp)

### What DOES Work

**✅ HuggingFace Format**
- Standard PyTorch model files
- File extensions: `.safetensors`, `.bin`
- **Fully compatible** with this app

**✅ HuggingFace Quantized Models**
- Formats: GPTQ, AWQ, bitsandbytes
- Smaller file size, reduced VRAM usage
- **Compatible** with minor code changes

---

## 🔧 Option 1: Use Built-in Quantization (Easiest)

The app now supports **on-the-fly quantization** using bitsandbytes!

### Enable 4-bit Quantization

Edit `config.py`:
```python
USE_QUANTIZATION = True
QUANTIZATION_TYPE = "4bit"  # Reduces ~14GB model to ~4GB VRAM
```

**Benefits:**
- Reduces VRAM usage by ~70%
- No need to download separate quantized model
- Minimal quality loss
- Works with any HuggingFace model

**Requirements:**
- NVIDIA GPU with CUDA
- bitsandbytes library (included in requirements.txt)

### Enable 8-bit Quantization

Edit `config.py`:
```python
USE_QUANTIZATION = True
QUANTIZATION_TYPE = "8bit"  # Reduces ~14GB model to ~7GB VRAM
```

**Benefits:**
- Reduces VRAM usage by ~50%
- Better quality than 4-bit
- Faster than 4-bit

---

## 🗂️ Option 2: Use Local Model Files

If you've downloaded the model manually or want to use a different model:

### Step 1: Download Model

**Option A: Download from HuggingFace**
```bash
# Install huggingface-cli
pip install huggingface-hub

# Download model
huggingface-cli download Qwen/Qwen2-Audio-7B-Instruct --local-dir ./models/Qwen2-Audio-7B-Instruct
```

**Option B: Use browser**
1. Visit: https://huggingface.co/Qwen/Qwen2-Audio-7B-Instruct/tree/main
2. Download all files
3. Place in `./models/Qwen2-Audio-7B-Instruct/`

### Step 2: Configure App

Edit `config.py`:
```python
USE_LOCAL_MODEL = True
LOCAL_MODEL_PATH = "./models/Qwen2-Audio-7B-Instruct"
```

### Expected Folder Structure
```
music-captioner/
├── models/
│   └── Qwen2-Audio-7B-Instruct/
│       ├── config.json
│       ├── model.safetensors (or multiple .safetensors files)
│       ├── tokenizer_config.json
│       ├── preprocessor_config.json
│       └── ... (other files)
├── music_captioner.py
├── config.py
└── ...
```

---

## 🎨 Option 3: Use Pre-Quantized GPTQ/AWQ Models

Some community members create pre-quantized versions of models.

### Finding Quantized Models

Search HuggingFace for:
- `Qwen2-Audio GPTQ`
- `Qwen2-Audio AWQ`
- `[model-name]-GPTQ-Int4`

**Example hypothetical models:**
```
TheBloke/Qwen2-Audio-7B-GPTQ-Int4
# or
someone/Qwen2-Audio-7B-AWQ
```

**Note:** As of now, I haven't found pre-quantized versions of Qwen2-Audio specifically, but they may exist or be created in the future.

### Using GPTQ Models

1. Install additional library:
```bash
pip install auto-gptq
```

2. Edit `config.py`:
```python
MODEL_NAME = "TheBloke/Qwen2-Audio-7B-GPTQ-Int4"  # Example
USE_LOCAL_MODEL = False
```

3. The app will automatically detect and use GPTQ if available

### Using AWQ Models

1. Install additional library:
```bash
pip install autoawq
```

2. Edit `config.py`:
```python
MODEL_NAME = "someone/Qwen2-Audio-7B-AWQ"  # Example
USE_LOCAL_MODEL = False
```

---

## 📊 Comparison: Quantization Methods

| Method | VRAM Usage | Quality | Speed | Setup Difficulty |
|--------|-----------|---------|-------|-----------------|
| **Full FP16** | ~14GB | Best | Fast | Easy |
| **bitsandbytes 8-bit** | ~7GB | Excellent | Fast | Easy ⭐ |
| **bitsandbytes 4-bit** | ~4GB | Very Good | Medium | Easy ⭐ |
| **GPTQ 4-bit** | ~4GB | Very Good | Fast | Medium |
| **AWQ 4-bit** | ~4GB | Very Good | Very Fast | Medium |
| **GGUF** | Varies | Good | Fast | ❌ Not Compatible |

**Recommendation:** Use built-in **bitsandbytes 4-bit** quantization - it's the easiest and works great!

---

## 🚀 Quick Start: Enable Quantization

### For Low VRAM GPUs (<8GB)

Edit `config.py`:
```python
USE_QUANTIZATION = True
QUANTIZATION_TYPE = "4bit"
```

That's it! The model will automatically load in 4-bit mode on next run.

### For Medium VRAM GPUs (8-12GB)

Edit `config.py`:
```python
USE_QUANTIZATION = True
QUANTIZATION_TYPE = "8bit"
```

### For High VRAM GPUs (>16GB)

No changes needed! Use the full model for best quality:
```python
USE_QUANTIZATION = False
```

---

## 🛠️ Troubleshooting Quantization

### "bitsandbytes not installed"

```bash
# Activate your virtual environment first
# Windows
venv\Scripts\activate
pip install bitsandbytes

# Linux/Mac
source venv/bin/activate
pip install bitsandbytes
```

### "CUDA not available" with quantization enabled

Quantization requires NVIDIA GPU. Either:
1. Disable quantization: `USE_QUANTIZATION = False`
2. Use CPU mode (slow): `USE_GPU = False`

### "Out of memory" even with 4-bit

Reduce batch size or close other GPU applications:
```python
# In config.py
BATCH_SIZE = 1
```

### Model loads but generates poor captions

- Try 8-bit instead of 4-bit
- Or disable quantization
- Some models don't quantize well - test to verify

---

## 🔍 Advanced: Using Different Audio Models

Want to try a different audio understanding model? 

### Requirements
- Model must support audio input
- Model must be on HuggingFace
- Model must use Transformers library

### Example: Hypothetical Alternative

```python
# In config.py
MODEL_NAME = "SomeOrg/audio-model-name"
```

**Known Audio Models (check compatibility):**
- Qwen2-Audio-7B-Instruct ✅ (default)
- Qwen2-Audio-Instruct
- Gemini models (via API, not local)
- Whisper (speech-to-text only, not music analysis)

---

## 💡 Tips for Best Performance

1. **Start with 4-bit quantization** - easiest way to reduce VRAM
2. **Use local models** - faster loading after initial download
3. **Monitor VRAM** - use `nvidia-smi` to check usage
4. **Test quality** - quantization may affect caption quality, test with your music
5. **Keep originals** - download full model first, then experiment

---

## ❓ FAQ

**Q: Can I convert GGUF to HuggingFace format?**
A: Theoretically yes, but it's complex and not recommended. Better to download the original HuggingFace model.

**Q: Will quantization affect caption quality?**
A: Slightly, but usually minimal. 8-bit is nearly identical, 4-bit is very close.

**Q: Can I use CPU with quantization?**
A: No, quantization requires CUDA GPU. For CPU, use full model.

**Q: Why not just use Ollama with GGUF?**
A: Qwen2-Audio may not be in Ollama's format, and this app is built on Transformers, not llama.cpp.

**Q: Can I quantize to 3-bit or 2-bit?**
A: Not with bitsandbytes. You'd need specialized quantization tools and the quality loss would be significant.

---

**Need help? Check README.md or MODEL_LOADING.md for more info!**
