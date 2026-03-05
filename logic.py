import whisper
from gtts import gTTS
import os
import tempfile
import io
import numpy as np
from pydub import AudioSegment
from difflib import SequenceMatcher
import algorithm
import eng_to_ipa as ipa
import warnings
import history

warnings.filterwarnings("ignore")

class PronunciationTrainer:
    def __init__(self, mock_mode=False):
        self.mock_mode = mock_mode
        self.whisper_model = None
        
        if not self.mock_mode:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
            print("Model loaded successfully!")
        else:
            print("⚠️ Running in MOCK MODE - AI Models disabled for fast UI dev")

    def generate_reference_audio(self, text):
        """Generate reference audio using gTTS, returned as numpy array to avoid
        Gradio's FileResponse / brotli_middleware Content-Length bug on Windows."""
        if self.mock_mode:
            return None, "⚠️ Mock Mode: Audio generation skipped"

        try:
            if not text or text.strip() == "":
                return None, "Please enter text first."

            # Generate MP3 bytes in-memory (no temp file on disk)
            buf = io.BytesIO()
            tts = gTTS(text=text, lang='en', slow=False)
            tts.write_to_fp(buf)
            buf.seek(0)

            # Decode MP3 → PCM numpy array via pydub
            audio_seg = AudioSegment.from_file(buf, format="mp3")
            audio_seg = audio_seg.set_channels(1)   # mono
            sample_rate = audio_seg.frame_rate
            samples = np.array(audio_seg.get_array_of_samples(), dtype=np.int16)

            return (sample_rate, samples), "✓ Reference audio generated!"
        except Exception as e:
            return None, f"Error generating audio: {str(e)}"

    def transcribe_audio(self, audio):
        """Transcribe audio using Whisper.
        Accepts either a file path (str) or a (sample_rate, numpy_array) tuple
        from gr.Audio(type='numpy').
        """
        if self.mock_mode:
            return "This is a mock transcription result.", 0.95, None

        try:
            if audio is None:
                return None, 0.0, "No audio provided"

            # If Gradio passes (sample_rate, ndarray), write a temp WAV for Whisper
            if isinstance(audio, tuple):
                import wave, struct
                sample_rate, samples = audio
                # Ensure int16
                samples = np.array(samples, dtype=np.int16)
                if samples.ndim > 1:
                    samples = samples[:, 0]  # take first channel if stereo
                fd, tmp_path = tempfile.mkstemp(suffix=".wav")
                try:
                    with wave.open(tmp_path, 'w') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)  # int16 = 2 bytes
                        wf.setframerate(sample_rate)
                        wf.writeframes(samples.tobytes())
                    audio_path = tmp_path
                    result = self.whisper_model.transcribe(
                        audio_path,
                        language="en",
                        temperature=0.0,
                        no_speech_threshold=0.6,
                        logprob_threshold=-1.0,
                        compression_ratio_threshold=2.4,
                        fp16=False
                    )
                finally:
                    os.close(fd)
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass
            else:
                # Legacy: filepath string
                result = self.whisper_model.transcribe(
                    audio,
                    language="en",
                    temperature=0.0,
                    no_speech_threshold=0.6,
                    logprob_threshold=-1.0,
                    compression_ratio_threshold=2.4,
                    fp16=False
                )

            transcribed_text = result["text"].strip()

            # Calculate confidence
            avg_logprob = result.get("segments", [{}])[0].get("avg_logprob", -1) if result.get("segments") else -1
            confidence_score = max(0, min(1, (avg_logprob + 1)))

            return transcribed_text, confidence_score, None
        except Exception as e:
            return None, 0.0, f"Error transcribing audio: {str(e)}"

    def text_to_ipa(self, text):
        """Convert text to IPA phonemes"""
        try:
            return ipa.convert(text)
        except Exception:
            return text

    def calculate_ipa_similarity(self, target_ipa, user_ipa):
        """Calculate IPA similarity score (0-100) using algorithm.py"""
        return algorithm.get_pronunciation_score(target_ipa, user_ipa)

    def generate_visual_feedback(self, target_ipa, user_ipa):
        """Generate HTML visual feedback"""
        if not user_ipa or user_ipa.strip() == "":
            return "<p style='color: red;'>No pronunciation detected.</p>"
        
        matcher = SequenceMatcher(None, target_ipa, user_ipa)
        opcodes = matcher.get_opcodes()
        
        html_parts = []
        html_parts.append("<div style='font-size: 20px; line-height: 2; font-family: monospace;'>")
        html_parts.append(f"<p><strong>Target IPA:</strong> {target_ipa}</p>")
        html_parts.append("<p><strong>Your IPA:</strong></p>")
        html_parts.append("<p>")
        
        for tag, i1, i2, j1, j2 in opcodes:
            target_segment = target_ipa[i1:i2]
            user_segment = user_ipa[j1:j2]
            
            if tag == 'equal':
                html_parts.append(f"<span style='color: green; font-weight: bold;'>{user_segment}</span>")
            elif tag == 'replace':
                html_parts.append(f"<span style='color: red; text-decoration: underline; font-weight: bold;'>{user_segment}</span>")
            elif tag == 'delete':
                html_parts.append(f"<span style='background-color: yellow; color: black; font-weight: bold;'>[{target_segment}]</span>")
            elif tag == 'insert':
                html_parts.append(f"<span style='color: grey; font-weight: bold;'>{user_segment}</span>")
        
        html_parts.append("</p>")
        return "".join(html_parts) + self._get_legend_html()

    def _get_legend_html(self):
        return """
        <br>
        <p style='font-size: 14px;'><strong>Legend:</strong> 
        <span style='color: green;'>● Correct</span> | 
        <span style='color: red; text-decoration: underline;'>● Wrong</span> | 
        <span style='background-color: yellow; color: black;'>● Missing</span> | 
        <span style='color: grey;'>● Extra</span>
        </p>
        </div>
        """

    def format_score_display(self, score):
        """Format score display with custom CSS circle"""
        color_class = "score-good" if score >= 80 else "score-average" if score >= 50 else "score-bad"
        return f"""
        <div class="score-circle {color_class}">
            <h1 class="score-value">{score:.1f}</h1>
            <span class="score-label">Overall Score</span>
        </div>
        """

    def calculate_final_score(self, confidence_score, ipa_similarity):
        # ipa_similarity is already 0-100 from algorithm.py;
        # confidence_score is 0-1, so scale it to 0-100 first.
        return (ipa_similarity * 0.6) + (confidence_score * 100 * 0.4)

    def process_pronunciation(self, target_text, audio):
        """Main processing function linked to UI"""
        try:
            # Input validation
            if not target_text or target_text.strip() == "":
                return self.format_score_display(0), "<p class='error'>Please enter target text.</p>", "Please enter text.", None
            
            if audio is None and not self.mock_mode:
                return self.format_score_display(0), "<p class='error'>Please record audio.</p>", "Please record audio.", None

            # 1. Transcribe
            user_text, confidence_score, error = self.transcribe_audio(audio)
            if error:
                return self.format_score_display(0), f"<p class='error'>{error}</p>", error, None

            # 2. Analysis
            target_ipa = self.text_to_ipa(target_text.lower())
            user_ipa = self.text_to_ipa(user_text.lower())
            ipa_similarity = self.calculate_ipa_similarity(target_ipa, user_ipa)
            final_score = self.calculate_final_score(confidence_score, ipa_similarity)

            # 3. Formats
            score_html = self.format_score_display(final_score)
            visual_feedback = self.generate_visual_feedback(target_ipa, user_ipa)
            details = f"📝 Transcribed: \"{user_text}\"\n🎯 Similarity: {ipa_similarity*100:.1f}%\n🔊 Confidence: {confidence_score*100:.1f}%"

            # 4. Save History (Only if not mocking, or if desired)
            updated_history = history.save_attempt(target_text, user_text, final_score, ipa_similarity)

            return score_html, visual_feedback, details, updated_history
            
        except Exception as e:
            return self.format_score_display(0), f"<p class='error'>System Error: {str(e)}</p>", str(e), None
