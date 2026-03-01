"""
Speech & AI Handler
Author: Khoa Beo
Purpose: Manage the "Listening" and "Speaking" components of the AI.
"""

import os
import string
import warnings
import tempfile
import whisper
from gtts import gTTS

# Suppress warnings
warnings.filterwarnings("ignore")

class SpeechHandler:
    def __init__(self, model_size="base"):
        """
        Initialize the SpeechHandler with OpenAI Whisper model.
        Args:
            model_size (str): Size of the Whisper model to load ('tiny', 'base', 'small', etc.)
        """
        print(f"Loading Whisper model ('{model_size}')... please wait.")
        try:
            self.model = whisper.load_model(model_size)
            print("Whisper model loaded successfully!")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            self.model = None

    def transcribe_audio(self, audio_path):
        """
        Transcribe audio file to text using Whisper.
        Args:
            audio_path (str): Path to the audio file.
        Returns:
            tuple: (transcribed_text, confidence_score)
        """
        if not self.model:
            return "Error: Model not loaded.", 0.0

        if not audio_path or not os.path.exists(audio_path):
            return "Error: Audio file not found.", 0.0

        try:
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_path,
                fp16=False, # Use FP32 to avoid warnings on CPU
                language='en'
            )
            
            text = result["text"].strip()
            
            # Calculate confidence score (avg_logprob -> probability)
            # Whisper returns avg_logprob per segment. We'll take the first one or average them.
            if "segments" in result and len(result["segments"]) > 0:
                avg_logprob = result["segments"][0]["avg_logprob"]
                # Convert log probability to linear probability: e^logprob
                # However, for simplicity and 0-1 scaling in some contexts, we can just use the exponential
                import math
                confidence = math.exp(avg_logprob)
            else:
                confidence = 0.0

            return text, confidence

        except Exception as e:
            return f"Error during transcription: {str(e)}", 0.0

    def generate_speech(self, text, output_filename="output_audio.mp3"):
        """
        Generate text-to-speech audio using gTTS.
        Args:
            text (str): Text to convert to speech.
            output_filename (str): Path to save the output audio file.
        Returns:
            str: Path to the generated audio file, or None if failed.
        """
        if not text:
            return None
        
        try:
            tts = gTTS(text=text, lang='en')
            tts.save(output_filename)
            return output_filename
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None

def clean_text(text):
    """
    Remove punctuation and convert text to lowercase.
    Args:
        text (str): Input text.
    Returns:
        str: Cleaned text.
    """
    if not text:
        return ""
    
    # Remove punctuation using translation table
    translator = str.maketrans('', '', string.punctuation)
    clean = text.translate(translator)
    
    # Convert to lowercase and strip whitespace
    return clean.lower().strip()

if __name__ == "__main__":
    # Test Block
    print("=== Testing Speech Module ===")
    
    # 1. Test clean_text
    raw_text = "Hello, World! This is: a test."
    cleaned = clean_text(raw_text)
    print(f"Raw: '{raw_text}'")
    print(f"Cleaned: '{cleaned}'")
    assert cleaned == "hello world this is a test"
    
    # 2. Test TTS (Generate a file)
    print("\nTesting TTS...")
    handler = SpeechHandler(model_size="tiny") # Use tiny for faster test loading
    
    test_audio_file = "test_speech.mp3"
    generated_path = handler.generate_speech("This is a test of the emergency broadcast system.", test_audio_file)
    
    if generated_path and os.path.exists(generated_path):
        print(f"[OK] Audio generated at {generated_path}")
    else:
        print("[FAIL] Audio generation failed")

    # 3. Test Transcription (using the file we just generated)
    # Note: Requires ffmpeg installed on system for Whisper to work.
    print("\nTesting Transcription (Whisper)...")
    if os.path.exists(test_audio_file):
        text, conf = handler.transcribe_audio(test_audio_file)
        print(f"Transcribed: '{text}'")
        print(f"Confidence: {conf:.4f}")
        
        # Cleanup
        try:
            os.remove(test_audio_file)
            print("[OK] Cleanup successful")
        except:
            pass
    else:
        print("Skipping transcription test (no audio file).")
