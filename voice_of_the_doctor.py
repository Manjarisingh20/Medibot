# if you don’t use pipenv, uncomment the following:
# from dotenv import load_dotenv
# load_dotenv()

import os
import logging
import subprocess
import platform
from gtts import gTTS
import elevenlabs
from elevenlabs.client import ElevenLabs

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load ElevenLabs API Key from Environment
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

def play_audio(file_path):
    """Plays the given audio file across different operating systems."""
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', file_path])
        elif os_name == "Windows":  # Windows
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{file_path}").PlaySync();'])
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', file_path])  # Alternative: use 'mpg123' or 'ffplay'
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        logging.error(f"❌ Error playing audio: {e}")

def text_to_speech_with_gtts(input_text, output_filepath):
    """Convert text to speech using gTTS and save as MP3."""
    try:
        logging.info("🎙️ Generating speech with gTTS...")
        tts = gTTS(text=input_text, lang="en", slow=False)
        tts.save(output_filepath)
        logging.info(f"✅ gTTS audio file saved: {output_filepath}")
        play_audio(output_filepath)
    except Exception as e:
        logging.error(f"❌ gTTS Error: {e}")

def text_to_speech_with_elevenlabs(input_text, output_filepath):
    """Convert text to speech using ElevenLabs API and save as MP3."""
    if not ELEVENLABS_API_KEY:
        logging.error("❌ ELEVENLABS_API_KEY is missing! Skipping ElevenLabs TTS.")
        return text_to_speech_with_gtts(input_text, output_filepath)  # Fallback to gTTS

    try:
        logging.info("🎙️ Generating speech with ElevenLabs...")

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = client.generate(
            text=input_text,
            voice="Aria",
            output_format="mp3_22050_32",
            model="eleven_turbo_v2"
        )
        elevenlabs.save(audio, output_filepath)

        if os.path.exists(output_filepath):
            logging.info(f"✅ ElevenLabs audio file saved: {output_filepath}")
            play_audio(output_filepath)
        else:
            logging.error("❌ ElevenLabs failed to save the audio file! Falling back to gTTS...")
            text_to_speech_with_gtts(input_text, output_filepath)  # Fallback to gTTS

    except Exception as e:
        # Handle specific ElevenLabs errors
        if "status_code: 401" in str(e):
            logging.error("❌ ElevenLabs access denied (401 Unauthorized).")
            logging.info("💡 Disable VPN or upgrade to a paid plan to continue.")
        else:
            logging.error(f"❌ ElevenLabs API Error: {e}")

        # Fallback to gTTS
        text_to_speech_with_gtts(input_text, output_filepath)

# Example Usage:
input_text = "Hi, this is Manjari!"
output_filepath = "tts_output.mp3"

# Try ElevenLabs first; if it fails, gTTS will be used automatically
text_to_speech_with_elevenlabs(input_text, output_filepath)
