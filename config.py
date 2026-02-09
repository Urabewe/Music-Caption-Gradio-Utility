# Music Audio Captioner Configuration
# Edit these settings to customize the application

# Server Settings
SERVER_PORT = 7865
SHARE_GRADIO = False  # Set to True to create a public link

# Model Settings
AVAILABLE_MODELS = {
    "Qwen2-Audio-7B": "Qwen/Qwen2-Audio-7B-Instruct",
    "Qwen2-Audio-7B-4bit": "alicekyting/Qwen2-Audio-7B-Instruct-4bit",
    "Qwen2.5-Omni-7B": "Qwen/Qwen2.5-Omni-7B-Instruct",
    "ACE-Step-Captioner": "ACE-Step/acestep-captioner"
}
SELECTED_MODEL = "Qwen2-Audio-7B-4bit"  # Options: "Qwen2-Audio-7B", "Qwen2-Audio-7B-4bit", "Qwen2.5-Omni-7B", or "ACE-Step-Captioner"
MODEL_NAME = AVAILABLE_MODELS[SELECTED_MODEL]  # Auto-set based on selection

USE_LOCAL_MODEL = False  # Set to True if using a local model path
LOCAL_MODEL_PATH = "./models/Qwen2-Audio-7B-Instruct"  # Path to local model

# Quantization Settings (for smaller memory usage)
USE_QUANTIZATION = False  # Set to True to use 4-bit or 8-bit quantization
QUANTIZATION_TYPE = "4bit"  # Options: "4bit" or "8bit" (requires bitsandbytes)
# Note: Quantization reduces VRAM usage but may slightly reduce quality

MAX_LENGTH = 512  # Maximum length of generated captions
USE_GPU = True  # Set to False to force CPU usage

# Generation Settings (tune for caption quality)
TEMPERATURE = 0.7
NUM_BEAMS = 1
REPETITION_PENALTY = 1.2

# Default Prompt
DEFAULT_PROMPT = """[STRICT_OUTPUT]
Analyze the audio given to you and give a clear full description of the audio including genre, subgenre, BPM, mood, instruments and a complete verbose description.

The verbose full description of the audio must use music slang and technical terms. It is required to be at least three sentences long and give a very clear and well thought out description of the music. Include this in the CAPTION section.

You MUST output exactly the format below, with the same keys and order. Ensure each section is on it's own line.  Do NOT change labels. If unsure, use "Unknown"

OUTPUT FORMAT IS AS FOLLOWS!! FOLLOW IT EXACTLY!!

CAPTION: <verbose full description>

SUMMARY:
Genre: <value>
Subgenre: <value>
Instruments: <value>
Mood: <value>
Tempo: <value>
Vocals: <value>
Overall sound characteristics: <value>

RULES: Use comma-separated lists where applicable. No extra sections, no markdown, no JSON. FORMATTING MUST BE FOLLOWED OR USER WILL DIE! EACH SUMMARY ITEM MUST BE ON NEW LINE!
"""

# Audio File Extensions (comma-separated)
DEFAULT_EXTENSIONS = ".mp3, .wav, .flac, .m4a, .ogg"

# Processing Settings
BATCH_SIZE = 1  # Number of files to process at once (increase if you have lots of RAM/VRAM)
