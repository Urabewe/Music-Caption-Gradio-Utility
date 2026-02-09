import gradio as gr
import torch
from transformers import (
    Qwen2AudioForConditionalGeneration, 
    AutoProcessor, 
    BitsAndBytesConfig,
    AutoConfig
)
from pathlib import Path
import soundfile as sf
from tqdm import tqdm
import os
import json
import config
import inspect

class MusicCaptioner:
    def __init__(self):
        self.processor = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() and config.USE_GPU else "cpu"

    def _load_audio(self, audio_path, target_sr=16000):
        """Load audio from disk and resample to target sample rate."""
        audio, sr = sf.read(audio_path)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if sr != target_sr:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
        return audio, target_sr

    def _call_processor(self, text, audio, sample_rate):
        """Call processor with the correct audio argument name."""
        call = self.processor.__call__
        signature = inspect.signature(call)
        params = signature.parameters
        has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())

        base_kwargs = {
            "text": text,
            "return_tensors": "pt",
            "padding": True,
            "sampling_rate": sample_rate,
        }

        if "audios" in params:
            base_kwargs["audios"] = [audio]
        elif "audio" in params:
            base_kwargs["audio"] = audio
        elif "raw_speech" in params:
            base_kwargs["raw_speech"] = audio
        else:
            raise ValueError("Processor does not accept audio inputs (audios/audio/raw_speech).")

        if has_kwargs:
            return self.processor(**base_kwargs)

        # Drop any kwargs the processor doesn't accept.
        safe_kwargs = {key: value for key, value in base_kwargs.items() if key in params}
        return self.processor(**safe_kwargs)

    def _parse_caption_output(self, output_text):
        """Parse model output into caption and summary fields when labeled."""
        if not output_text:
            return None

        cleaned = output_text.strip()
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1].strip()

        upper_text = cleaned.upper()
        caption_block = ""
        summary_block = ""

        if "CAPTION:" in upper_text:
            caption_start = upper_text.index("CAPTION:") + len("CAPTION:")
            if "SUMMARY:" in upper_text:
                summary_start = upper_text.index("SUMMARY:")
                caption_block = cleaned[caption_start:summary_start].strip()
                summary_block = cleaned[summary_start + len("SUMMARY:"):].strip()
            else:
                caption_block = cleaned[caption_start:].strip()
        elif "SUMMARY:" in upper_text:
            summary_start = upper_text.index("SUMMARY:")
            summary_block = cleaned[summary_start + len("SUMMARY:"):].strip()
        else:
            return None

        summary = {}
        for line in summary_block.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key and value:
                summary[key] = value

        if not caption_block and not summary:
            return None

        return {
            "caption": caption_block,
            "summary": summary
        }

    def _format_parsed_output(self, parsed):
        """Format parsed output into a consistent text block."""
        if not parsed:
            return None
        caption_text = parsed["caption"].strip()
        lines = [f"CAPTION: {caption_text}", "", "SUMMARY:"]
        preferred_order = [
            "Genre",
            "Subgenre",
            "Instruments",
            "Mood",
            "Tempo",
            "Vocals",
            "Overall sound characteristics"
        ]
        summary = parsed["summary"]
        for key in preferred_order:
            if key in summary:
                lines.append(f"{key}: {summary[key]}")
        for key, value in summary.items():
            if key not in preferred_order:
                lines.append(f"{key}: {value}")
        return "\n".join(lines).strip()
        
    def load_model(self):
        """Load the Qwen2-Audio model"""
        if self.model is None:
            print("=" * 60)
            print("Loading Audio Model...")
            print("=" * 60)
            
            # Determine model path
            model_path = config.LOCAL_MODEL_PATH if config.USE_LOCAL_MODEL else config.MODEL_NAME
            
            print(f"Selected Model: {config.SELECTED_MODEL}")
            print(f"Model Path: {model_path}")
            print(f"Use Local: {config.USE_LOCAL_MODEL}")
            
            if config.USE_LOCAL_MODEL:
                print(f"Loading from local path: {model_path}")
            else:
                print("First run: This will download model from Hugging Face")
                print("Future runs: Model loads from cache instantly")
                print("Cache location:")
                print("  Windows: C:\\Users\\YourName\\.cache\\huggingface\\hub")
                print("  Linux/Mac: ~/.cache/huggingface/hub")
            print("=" * 60)
            
            try:
                print("\n[1/2] Loading processor...")
                self.processor = AutoProcessor.from_pretrained(
                    model_path,
                    trust_remote_code=True
                )
                print("✓ Processor loaded successfully")
                
                print("\n[2/2] Loading model (this may take several minutes on first run; uses cache if present)...")
                
                use_gpu = torch.cuda.is_available() and config.USE_GPU
                self.device = "cuda" if use_gpu else "cpu"

                # Configure quantization if enabled
                quantization_config = None
                if config.USE_QUANTIZATION and use_gpu:
                    print(f"Using {config.QUANTIZATION_TYPE} quantization for reduced memory usage...")
                    if config.QUANTIZATION_TYPE == "4bit":
                        quantization_config = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_compute_dtype=torch.float16,
                            bnb_4bit_use_double_quant=True,
                            bnb_4bit_quant_type="nf4"
                        )
                    elif config.QUANTIZATION_TYPE == "8bit":
                        quantization_config = BitsAndBytesConfig(
                            load_in_8bit=True,
                            llm_int8_enable_fp32_cpu_offload=True  # Enable CPU offload
                        )
                elif config.USE_QUANTIZATION and not use_gpu:
                    print("Warning: Quantization requires CUDA. Disabling quantization for CPU mode.")
                    config.USE_QUANTIZATION = False
                
                # Load model - use AutoConfig to determine correct class
                from transformers import AutoConfig, AutoModelForCausalLM
                
                load_kwargs = {
                    "trust_remote_code": True,
                    "device_map": "auto" if use_gpu else "cpu",
                }
                
                if quantization_config:
                    load_kwargs["quantization_config"] = quantization_config
                else:
                    load_kwargs["torch_dtype"] = torch.float16 if use_gpu else torch.float32
                
                # Load config to determine model type
                model_config = AutoConfig.from_pretrained(
                    model_path,
                    trust_remote_code=True
                )
                print(f"Model type detected: {model_config.model_type}")
                
                # Load model based on detected type
                try:
                    # For Qwen2.5-Omni and other multimodal models
                    if "qwen2_5_omni" in model_config.model_type or "omni" in model_config.model_type.lower():
                        print("Loading Qwen2.5-Omni model...")
                        from transformers import Qwen2_5OmniForConditionalGeneration
                        self.model = Qwen2_5OmniForConditionalGeneration.from_pretrained(
                            model_path,
                            **load_kwargs
                        )
                    # For Qwen2-Audio models
                    elif "qwen2_audio" in model_config.model_type:
                        print("Loading Qwen2-Audio model...")
                        self.model = Qwen2AudioForConditionalGeneration.from_pretrained(
                            model_path,
                            **load_kwargs
                        )
                    # Generic fallback for other models
                    else:
                        print(f"Loading generic AutoModel for type: {model_config.model_type}...")
                        self.model = AutoModelForCausalLM.from_pretrained(
                            model_path,
                            **load_kwargs
                        )
                except ImportError as e:
                    print(f"Warning: Specific model class not found, falling back to Qwen2AudioForConditionalGeneration: {e}")
                    self.model = Qwen2AudioForConditionalGeneration.from_pretrained(
                        model_path,
                        **load_kwargs
                    )
                
                if not use_gpu:
                    self.model = self.model.to(self.device)
                self.model.eval()
                
                print(f"✓ Model loaded successfully on {self.device}")
                if quantization_config:
                    print(f"✓ Using {config.QUANTIZATION_TYPE} quantization")
                print("=" * 60)
                
            except Exception as e:
                print(f"\n✗ Error loading model: {str(e)}")
                print("\nTroubleshooting:")
                print("1. Check your internet connection")
                print("2. Ensure you have ~14GB free disk space")
                print("3. Try running again (downloads can resume)")
                print("4. If using local model, check the path is correct")
                print("5. If using quantization, ensure bitsandbytes is installed")
                raise
    
    def generate_caption(self, audio_path, prompt, temperature=None, num_beams=None, repetition_penalty=None):
        """Generate caption for a single audio file"""
        self.load_model()
        
        # Ensure audio_path is absolute and properly formatted
        from pathlib import Path
        audio_path = str(Path(audio_path).absolute())
        audio, sample_rate = self._load_audio(audio_path, target_sr=16000)
        
        # Prepare the conversation format
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "audio", "audio_url": audio_path},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        # Process inputs
        if hasattr(self.processor, "apply_chat_template"):
            text = self.processor.apply_chat_template(conversation, add_generation_prompt=True, tokenize=False)
        else:
            text = prompt

        inputs = self._call_processor(text=text, audio=audio, sample_rate=sample_rate)
        if hasattr(inputs, "to"):
            inputs = inputs.to(self.device)
        elif isinstance(inputs, dict):
            for key, value in inputs.items():
                if torch.is_tensor(value):
                    inputs[key] = value.to(self.device)
                elif isinstance(value, list):
                    inputs[key] = torch.tensor(value).to(self.device)
        
        # Generate caption
        use_temperature = config.TEMPERATURE if temperature is None else temperature
        use_num_beams = config.NUM_BEAMS if num_beams is None else num_beams
        use_repetition_penalty = config.REPETITION_PENALTY if repetition_penalty is None else repetition_penalty
        do_sample = use_temperature is not None and use_temperature > 0

        with torch.no_grad():
            generate_ids = self.model.generate(
                **inputs,
                max_new_tokens=config.MAX_LENGTH,
                temperature=use_temperature,
                num_beams=use_num_beams,
                repetition_penalty=use_repetition_penalty,
                do_sample=do_sample
            )

        # Strip the prompt tokens if present (common for chat-style models)
        if "input_ids" in inputs:
            prompt_len = inputs["input_ids"].shape[1]
            if generate_ids.shape[1] > prompt_len:
                generate_ids = generate_ids[:, prompt_len:]
        
        # Decode output
        output = self.processor.batch_decode(
            generate_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]
        
        return output
    
    def process_single_file(self, audio_file, prompt, save_caption, model_display_name, quant_option, output_format, output_dir, temperature, num_beams, repetition_penalty):
        """Process a single uploaded audio file"""
        try:
            # Map display names to actual model names
            model_map = {
                "Qwen2-Audio-7B (~16GB)": "Qwen2-Audio-7B",
                "Qwen2-Audio-7B-4bit (~6.6GB)": "Qwen2-Audio-7B-4bit",
                "Qwen2.5-Omni-7B (~23GB)": "Qwen2.5-Omni-7B",
                "ACE-Step-Captioner (~23GB)": "ACE-Step-Captioner"
            }
            
            # Extract actual model name
            model_name = model_map.get(model_display_name, "Qwen2-Audio-7B")
            
            # Update config dynamically
            if model_name:
                config.SELECTED_MODEL = model_name
                config.MODEL_NAME = config.AVAILABLE_MODELS.get(model_name, config.AVAILABLE_MODELS["Qwen2-Audio-7B"])
            
            # Update quantization setting
            if quant_option == "Off":
                config.USE_QUANTIZATION = False
            elif quant_option == "4-bit":
                config.USE_QUANTIZATION = True
                config.QUANTIZATION_TYPE = "4bit"
            elif quant_option == "8-bit":
                config.USE_QUANTIZATION = True
                config.QUANTIZATION_TYPE = "8bit"
            
            # Unload model if settings changed
            if self.model is not None:
                del self.model
                del self.processor
                self.model = None
                self.processor = None
                import gc
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            caption = self.generate_caption(
                audio_file,
                prompt,
                temperature=temperature,
                num_beams=num_beams,
                repetition_penalty=repetition_penalty
            )
            
            parsed = self._parse_caption_output(caption)
            formatted_text = self._format_parsed_output(parsed)

            if output_format == "JSON":
                if parsed:
                    output_payload = {
                        "caption": parsed["caption"],
                        "summary": parsed["summary"]
                    }
                else:
                    output_payload = {"caption": caption}
                output_text = json.dumps(output_payload, ensure_ascii=False, indent=2)
            else:
                output_text = formatted_text if formatted_text else f"Caption:\n{caption}"

            if save_caption:
                audio_path = Path(audio_file)
                base_name = audio_path.stem
                target_dir = Path(output_dir).expanduser() if output_dir else Path("outputs")
                target_dir.mkdir(parents=True, exist_ok=True)
                if output_format == "JSON":
                    output_path = target_dir / f"{base_name}.json"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(output_text)
                else:
                    output_path = target_dir / f"{base_name}.txt"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(output_text if formatted_text else caption)

            return output_text
                
        except Exception as e:
            return f"Error processing file: {str(e)}"
    
    def process_folder(self, folder_path, prompt, model_display_name, quant_option, output_format, output_dir, temperature, num_beams, repetition_penalty, progress=gr.Progress()):
        """Process all audio files in a folder"""
        try:
            # Map display names to actual model names
            model_map = {
                "Qwen2-Audio-7B (~16GB)": "Qwen2-Audio-7B",
                "Qwen2-Audio-7B-4bit (~6.6GB)": "Qwen2-Audio-7B-4bit",
                "Qwen2.5-Omni-7B (~23GB)": "Qwen2.5-Omni-7B",
                "ACE-Step-Captioner (~23GB)": "ACE-Step-Captioner"
            }
            
            # Extract actual model name
            model_name = model_map.get(model_display_name, "Qwen2-Audio-7B")
            
            # Update config dynamically
            if model_name:
                config.SELECTED_MODEL = model_name
                config.MODEL_NAME = config.AVAILABLE_MODELS.get(model_name, config.AVAILABLE_MODELS["Qwen2-Audio-7B"])
            
            # Update quantization setting
            if quant_option == "Off":
                config.USE_QUANTIZATION = False
            elif quant_option == "4-bit":
                config.USE_QUANTIZATION = True
                config.QUANTIZATION_TYPE = "4bit"
            elif quant_option == "8-bit":
                config.USE_QUANTIZATION = True
                config.QUANTIZATION_TYPE = "8bit"
            
            # Unload model if settings changed
            if self.model is not None:
                del self.model
                del self.processor
                self.model = None
                self.processor = None
                import gc
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            folder = Path(folder_path)
            if not folder.exists():
                return "Error: Folder does not exist"
            
            # Find all audio files by attempting to read metadata
            audio_files = []
            for item in folder.iterdir():
                if not item.is_file():
                    continue
                try:
                    sf.info(str(item))
                    audio_files.append(item)
                except Exception:
                    continue
            
            if not audio_files:
                return f"No audio files found with extensions: {audio_extensions}"
            
            results = []
            results.append(f"Found {len(audio_files)} audio files\n")
            results.append("=" * 50 + "\n")
            
            # Process each file
            for i, audio_file in enumerate(audio_files):
                progress((i + 1) / len(audio_files), desc=f"Processing {audio_file.name}")
                
                try:
                    caption = self.generate_caption(
                        str(audio_file),
                        prompt,
                        temperature=temperature,
                        num_beams=num_beams,
                        repetition_penalty=repetition_penalty
                    )

                    parsed = self._parse_caption_output(caption)
                    formatted_text = self._format_parsed_output(parsed)
                    
                    # Save caption
                    target_dir = Path(output_dir).expanduser() if output_dir else Path("outputs")
                    target_dir.mkdir(parents=True, exist_ok=True)
                    if output_format == "JSON":
                        output_path = target_dir / f"{audio_file.stem}.json"
                        with open(output_path, 'w', encoding='utf-8') as f:
                            if parsed:
                                json.dump({"caption": parsed["caption"], "summary": parsed["summary"]}, f, ensure_ascii=False, indent=2)
                            else:
                                json.dump({"caption": caption}, f, ensure_ascii=False, indent=2)
                    else:
                        output_path = target_dir / f"{audio_file.stem}.txt"
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(formatted_text if formatted_text else caption)
                    
                    results.append(f"✓ {audio_file.name}\n")
                    results.append(f"  Caption: {caption[:100]}...\n")
                    results.append(f"  Saved to: {output_path}\n\n")
                    
                except Exception as e:
                    results.append(f"✗ {audio_file.name}\n")
                    results.append(f"  Error: {str(e)}\n\n")
            
            results.append("=" * 50 + "\n")
            results.append("Processing complete!")
            
            return "".join(results)
            
        except Exception as e:
            return f"Error processing folder: {str(e)}"

    def unload_model(self):
        """Unload model and processor to free VRAM."""
        if self.model is None and self.processor is None:
            return "Model already unloaded."

        try:
            del self.model
            del self.processor
            self.model = None
            self.processor = None
            import gc
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            return "✅ Model unloaded and VRAM cleared."
        except Exception as e:
            return f"❌ Failed to unload model: {str(e)}"

# Initialize captioner
captioner = MusicCaptioner()

# Default prompt from config
DEFAULT_PROMPT = config.DEFAULT_PROMPT

# Create Gradio interface
with gr.Blocks(title="Music Audio Captioner") as app:
    gr.Markdown("# 🎵 Music Audio Captioner")
    gr.Markdown("*Automatically generate AI descriptions for your music files*")
    
    # Status banner
    with gr.Row():
        # Get model name from config, with fallback
        try:
            current_model = config.SELECTED_MODEL
        except AttributeError:
            current_model = config.AVAILABLE_MODELS.get("Qwen2-Audio-7B", "Qwen2-Audio-7B")
        
        gr.Markdown(f"""
        <div style="padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; text-align: center;">
            <h3 style="margin: 0; color: white;">✨ Ready to caption your music!</h3>
            <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">
                Model: {current_model} | 
                GPU: {"✅ Enabled" if torch.cuda.is_available() else "❌ CPU Mode"} |
                Port: {config.SERVER_PORT}
            </p>
        </div>
        """)
    
    gr.Markdown("---")

    # Global settings (shared across tabs)
    with gr.Row():
        with gr.Column(scale=3):
            global_prompt = gr.Textbox(
                label="✏️ Caption Prompt",
                value=DEFAULT_PROMPT,
                placeholder="Describe what you want in the captions...",
                lines=10
            )

            with gr.Row():
                apply_global_btn = gr.Button("💾 Apply Settings", variant="secondary", scale=1)
                unload_global_btn = gr.Button("🧹 Unload Model", variant="secondary", scale=1)

        with gr.Column(scale=2):
            # Model choices with sizes
            model_choices = [
                "Qwen2-Audio-7B (~16GB)",
                "Qwen2-Audio-7B-4bit (~6.6GB)",
                "Qwen2.5-Omni-7B (~23GB)",
                "ACE-Step-Captioner (~23GB)"
            ]
            
            # Map display names to config keys
            model_map = {
                "Qwen2-Audio-7B (~16GB)": "Qwen2-Audio-7B",
                "Qwen2-Audio-7B-4bit (~6.6GB)": "Qwen2-Audio-7B-4bit",
                "Qwen2.5-Omni-7B (~23GB)": "Qwen2.5-Omni-7B",
                "ACE-Step-Captioner (~23GB)": "ACE-Step-Captioner"
            }
            
            # Get current model with fallback
            try:
                current_model = config.SELECTED_MODEL
                # Convert to display name
                current_display = [k for k, v in model_map.items() if v == current_model][0]
            except (AttributeError, IndexError):
                current_display = "Qwen2-Audio-7B (~16GB)"
            
            global_model = gr.Dropdown(
                choices=model_choices,
                value=current_display,
                label="🤖 Model",
                info="Choose AI model (download size shown)"
            )

            global_quant = gr.Radio(
                choices=["Off", "4-bit", "8-bit"],
                value="Off",
                label="⚡ Quantization",
                info="Reduces VRAM usage"
            )

            with gr.Row():
                output_format = gr.Dropdown(
                    choices=["Text", "JSON"],
                    value="Text",
                    label="🧾 Output Format",
                    info="Controls display and saved file type"
                )
                global_status = gr.Textbox(
                    label="Status",
                    value="Settings ready",
                    interactive=False
                )

            output_dir = gr.Textbox(
                label="📁 Output Folder",
                value="outputs",
                placeholder="Example: C:\\Users\\YourName\\Music\\captions",
                info="Saved captions go here (leave blank for ./outputs)",
                lines=1
            )

    with gr.Row():
        temperature = gr.Slider(
            minimum=0.0,
            maximum=1.5,
            value=config.TEMPERATURE,
            step=0.05,
            label="🌡️ Temperature",
            info="Higher = more creative but less stable; 0 for deterministic output"
        )
        num_beams = gr.Slider(
            minimum=1,
            maximum=10,
            value=config.NUM_BEAMS,
            step=1,
            label="🧠 Num Beams",
            info="Higher = better quality but slower; 1 is fastest"
        )
        repetition_penalty = gr.Slider(
            minimum=1.0,
            maximum=2.0,
            value=config.REPETITION_PENALTY,
            step=0.05,
            label="🔁 Repetition Penalty",
            info="Higher reduces repetition; too high can hurt fluency"
        )
    
    gr.Markdown("---")
    
    with gr.Tabs():
        with gr.Tab("📁 Batch Processing"):
            gr.Markdown("### Process an entire folder of music files at once")
            gr.Markdown("💡 **Tip:** Captions are saved to the Output Folder in the selected format")
            
            with gr.Row():
                with gr.Column(scale=2):
                    folder_input = gr.Textbox(
                        label="📂 Music Folder Path",
                        placeholder="Example: C:\\Users\\YourName\\Music\\MyAlbum",
                        info="Enter the full path to the folder containing your music files",
                        lines=1
                    )
                    
                    gr.Markdown("Supported file types: .mp3, .wav, .flac, .m4a, .ogg")
                    
                    with gr.Row():
                        batch_btn = gr.Button("🚀 Start Processing", variant="primary", scale=2)
                        gr.Button("❌ Clear", variant="secondary", scale=1)
                
                with gr.Column(scale=3):
                    output_batch = gr.Textbox(
                        label="📊 Processing Results",
                        lines=20
                    )
            
            batch_btn.click(
                fn=captioner.process_folder,
                inputs=[folder_input, global_prompt, global_model, global_quant, output_format, output_dir, temperature, num_beams, repetition_penalty],
                outputs=output_batch
            )
        
        with gr.Tab("🎵 Single File"):
            gr.Markdown("### Process one audio file at a time")
            gr.Markdown("💡 **Tip:** Upload a file, customize the prompt if needed, then click Generate")
            
            with gr.Row():
                with gr.Column(scale=2):
                    audio_input = gr.Audio(
                        type="filepath",
                        label="🎧 Upload Audio File"
                    )
                    
                    save_checkbox = gr.Checkbox(
                        label="💾 Save output file",
                        value=True,
                        info="Saved to the Output Folder using the selected format"
                    )
                    process_btn = gr.Button("✨ Generate Caption", variant="primary")
                
                with gr.Column(scale=3):
                    output_single = gr.Textbox(
                        label="📝 Generated Caption",
                        lines=15
                    )
            
            process_btn.click(
                fn=captioner.process_single_file,
                inputs=[audio_input, global_prompt, save_checkbox, global_model, global_quant, output_format, output_dir, temperature, num_beams, repetition_penalty],
                outputs=output_single
            )
    
        with gr.Tab("💡 Tips & Info"):
            with gr.Accordion("📖 Quick Start Guide", open=True):
                gr.Markdown("""
                ## 🚀 Getting Started
                
                ### For Batch Processing (Multiple Files):
                1. Go to **"📁 Batch Processing"** tab
                2. Enter your music folder path (example: `C:\\Users\\YourName\\Music\\MyAlbum`)
                3. Optionally customize the prompt
                4. Click **"🚀 Start Processing"**
                5. ✅ Done! Captions are automatically saved as .txt files next to your music
                
                ### For Single Files:
                1. Go to **"🎵 Single File"** tab  
                2. Upload an audio file
                3. Optionally customize the prompt
                4. Click **"✨ Generate Caption"**
                5. ✅ Done! Caption appears and optionally saves as .txt
                """)
            
            with gr.Accordion("✏️ Prompt Examples", open=False):
                gr.Markdown("""
                Copy and paste these into the prompt field, or create your own!
                
                **Detailed Analysis:**
                ```
                Describe this song including its genre, subgenre, instruments, mood, tempo, and overall sound characteristics.
                ```
                
                **Brief Description:**
                ```
                Provide a 2-sentence description of this song's genre and vibe.
                ```
                
                **Focus on Instruments:**
                ```
                What instruments can you hear? Describe the vocal style if present.
                ```
                
                **Production Focus:**
                ```
                Analyze this track from a production perspective: mixing, effects, and production style.
                ```
                
                **For Dataset Training:**
                ```
                Genre, tempo, key instruments, mood, energy level.
                ```
                
                **Custom Style:**
                ```
                Describe this song in the style of a music critic reviewing for Rolling Stone magazine.
                ```
                """)
            
            with gr.Accordion("📋 Supported File Formats", open=False):
                gr.Markdown("""
                ✅ **Fully Supported:**
                - MP3 (.mp3)
                - WAV (.wav)
                - FLAC (.flac)
                - M4A/AAC (.m4a)
                - OGG (.ogg)
                
                Most common audio formats work! If you encounter issues, try converting to WAV or MP3.
                """)
            
            with gr.Accordion("💡 Tips & Best Practices", open=False):
                gr.Markdown("""
                ### Getting the Best Results
                
                **Prompt Engineering:**
                - Be specific about what you want described
                - Include examples of desired output style
                - Mention specific attributes (genre, mood, instruments, tempo)
                
                **File Organization:**
                - Keep music organized in folders (by album, artist, genre)
                - Process one folder at a time for better organization
                - Captions save to your Output Folder with the same base filename
                
                **Performance:**
                - First run downloads the model (~14GB) - be patient!
                - GPU mode is much faster than CPU
                - Enable quantization in Batch/Single tabs if running out of VRAM
                - Close other GPU applications for best performance
                
                **Troubleshooting:**
                - If captions seem off, try a different model (Qwen2-Audio vs ACE-Step)
                - For music-specific tasks, ACE-Step may give better results
                - Experiment with different prompts to find what works best
                - Check that file extensions match what you entered (.mp3, .wav, etc.)
                """)
            
            with gr.Accordion("❓ FAQ", open=False):
                gr.Markdown("""
                **Q: Where are my captions saved?**
                A: In your Output Folder, using the selected format (.txt or .json).
                
                **Q: Can I edit the captions after generation?**
                A: Yes! They're plain text files - open with any text editor.
                
                **Q: Which model should I use?**
                A: Try Qwen2-Audio first. If results aren't great, try ACE-Step or Qwen2.5-Omni.
                
                **Q: How long does processing take?**
                A: With GPU: 5-10 seconds per song. Without GPU: 30-60 seconds per song.
                
                **Q: Can I process thousands of files?**
                A: Yes! Process in batches of 100-500 for best results.
                
                **Q: Will this work offline after first download?**
                A: Yes! Model is cached locally after first download.
                
                **Q: Can I use custom prompts for different folders?**
                A: Yes! Change the prompt for each batch as needed.
                """)
    
    # Settings handler function
    def apply_settings_handler(model_display_name, quant_option):
        """Save settings to config.py and reload config"""
        try:
            # Map display names to actual model names
            model_map = {
                "Qwen2-Audio-7B (~16GB)": "Qwen2-Audio-7B",
                "Qwen2-Audio-7B-4bit (~6.6GB)": "Qwen2-Audio-7B-4bit",
                "Qwen2.5-Omni-7B (~23GB)": "Qwen2.5-Omni-7B",
                "ACE-Step-Captioner (~23GB)": "ACE-Step-Captioner"
            }
            
            model_name = model_map.get(model_display_name, "Qwen2-Audio-7B")
            
            # Read current config
            with open('config.py', 'r') as f:
                config_content = f.read()
            
            # Update model selection
            import re
            config_content = re.sub(
                r'SELECTED_MODEL = "[^"]*"',
                f'SELECTED_MODEL = "{model_name}"',
                config_content
            )
            
            # Update quantization settings
            if quant_option == "Off":
                config_content = re.sub(
                    r'USE_QUANTIZATION = (True|False)',
                    'USE_QUANTIZATION = False',
                    config_content
                )
            else:
                config_content = re.sub(
                    r'USE_QUANTIZATION = (True|False)',
                    'USE_QUANTIZATION = True',
                    config_content
                )
                quant_type = "4bit" if quant_option == "4-bit" else "8bit"
                config_content = re.sub(
                    r'QUANTIZATION_TYPE = "[^"]*"',
                    f'QUANTIZATION_TYPE = "{quant_type}"',
                    config_content
                )
            
            # Write back
            with open('config.py', 'w') as f:
                f.write(config_content)
            
            # Reload config module
            import importlib
            importlib.reload(config)
            
            # Unload current model to force reload with new settings
            if captioner.model is not None:
                del captioner.model
                del captioner.processor
                captioner.model = None
                captioner.processor = None
                
                import gc
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            return f"✅ Settings saved! Model: {model_name} | Quantization: {quant_option}\n\nModel will reload on next caption."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def apply_global_settings(model_display, quant):
        return apply_settings_handler(model_display, quant)

    apply_global_btn.click(
        fn=apply_global_settings,
        inputs=[global_model, global_quant],
        outputs=global_status
    )

    unload_global_btn.click(
        fn=captioner.unload_model,
        outputs=global_status
    )
    
    # Footer
    gr.Markdown("---")
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
            ### 💡 Need Help?
            - Check the **Tips & Info** tab
            - See README.md in install folder
            - Model auto-downloads on first use (~14GB)
            """)
        with gr.Column(scale=1):
            # Get current settings with fallbacks
            try:
                current_model = config.SELECTED_MODEL
            except AttributeError:
                current_model = "Qwen2-Audio-7B"
            
            try:
                quant_status = f"✅ {config.QUANTIZATION_TYPE.upper()}" if config.USE_QUANTIZATION else "❌ Disabled"
            except AttributeError:
                quant_status = "❌ Disabled"
            
            gr.Markdown(f"""
            ### ⚙️ System Status
            - **Port:** {config.SERVER_PORT}
            - **GPU:** {"✅ Available" if torch.cuda.is_available() else "❌ CPU Only"}
            - **Model:** {current_model}
            - **Quantization:** {quant_status}
            """)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎵 Music Audio Captioner Starting...")
    print("="*60)
    print(f"Opening web interface at: http://localhost:{config.SERVER_PORT}")
    print(f"GPU Available: {'Yes' if torch.cuda.is_available() else 'No (CPU mode)'}")
    try:
        print(f"Current Model: {config.SELECTED_MODEL}")
    except AttributeError:
        print(f"Current Model: Qwen2-Audio-7B (default)")
    print("="*60 + "\n")
    
    # Gradio 6.0: theme moved to launch()
    app.launch(
        server_port=config.SERVER_PORT, 
        share=config.SHARE_GRADIO,
        inbrowser=True,
        show_error=True
    )
