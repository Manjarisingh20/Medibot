import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
import os
from groq import Groq

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ensure GROQ_API_KEY is set
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY is not set. Please set it in your environment variables.")
else:
    logging.info("✅ GROQ_API_KEY is set.")

stt_model = "whisper-large-v3"
audio_filepath = "patient_voice_test_for_patient.mp3"

# Function to record and save audio
def record_audio(file_path, timeout=20, phrase_time_limit=None):
    """Records audio from the microphone and saves it as an MP3 file."""
    recognizer = sr.Recognizer()
    temp_wav_path = "temp_audio.wav"  # Temporary WAV file for conversion

    try:
        with sr.Microphone() as source:
            logging.info("🎤 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("🎙️ Start speaking now...")

            # Record the audio
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("🔴 Recording complete.")

            # Save the recording as a WAV file first
            with open(temp_wav_path, "wb") as wav_file:
                wav_file.write(audio_data.get_wav_data())

            # Convert WAV to MP3
            audio_segment = AudioSegment.from_wav(temp_wav_path)
            audio_segment.export(file_path, format="mp3", bitrate="128k")
            logging.info(f"✅ Audio saved to {file_path}")

            # Remove temporary WAV file
            os.remove(temp_wav_path)

    except Exception as e:
        logging.error(f"❌ An error occurred: {e}")

# Function to check if file exists and is not empty
def validate_audio_file(file_path):
    """Checks if the audio file exists and is not empty."""
    if not os.path.exists(file_path):
        logging.error(f"❌ Error: Audio file '{file_path}' does not exist!")
        return False
    if os.path.getsize(file_path) == 0:
        logging.error(f"❌ Error: Audio file '{file_path}' is empty!")
        return False
    logging.info(f"✅ File '{file_path}' exists and has size: {os.path.getsize(file_path)} bytes")
    return True

# Function to transcribe the audio
def transcribe_with_groq(stt_model, audio_filepath, GROQ_API_KEY):
    """Transcribes an audio file using Groq's STT API."""
    if not validate_audio_file(audio_filepath):
        return None  # Don't proceed if the file is invalid

    try:
        client = Groq(api_key=GROQ_API_KEY)
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en",
            )
        return transcription.text
    except Exception as e:
        logging.error(f"❌ Error during transcription: {e}")
        return None

# Uncomment the below line to record new audio
record_audio(audio_filepath)

# Perform transcription if the file is valid
transcription_result = transcribe_with_groq(stt_model, audio_filepath, GROQ_API_KEY)

if transcription_result:
    print("\n📝 Transcription Result:\n", transcription_result)
else:
    print("\n❌ Transcription failed.")
