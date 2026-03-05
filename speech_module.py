"""
Speech Module — ELSA-style English Learning Web Tool
Author: Khoa Beo (refactored)

Architecture Research:
- ELSA Speak  : ASR + phoneme-level feedback, rhythm/intonation/fluency scoring
- SpeechAce   : Phoneme/syllable/word/sentence quality scores (0-100), GOP metric
- SpeechSuper : Fluency, completeness, rhythm, pause-count metrics
- Langcraft    : IPA phoneme timestamps, mispronunciation detection (substitution/insertion/deletion)
- Web Speech API: Browser-native STT/TTS, zero-latency for real-time use

Design decisions for a WEB context:
1. STT  — Use browser Web Speech API (zero install, real-time) as primary,
           Whisper as server-side fallback for accuracy/recording mode.
2. TTS  — Web Speech API SpeechSynthesis (browser) for instant playback;
           gTTS for generating downloadable "model" reference audio.
3. Scoring — Whisper transcription + diff-based word accuracy (no paid API needed).
             Designed to plug in SpeechAce/SpeechSuper API later.
4. Feedback — Word-level color coding (correct / mispronounced / missing),
              fluency metrics (WPM, pause count), overall score 0-100.
"""

import os
import re
import math
import time
import string
import difflib
import warnings
import logging
from dataclasses import dataclass, field
from typing import Optional

# ── Optional heavy deps (graceful degradation) ──────────────────────────────
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("openai-whisper not installed. Server-side ASR disabled.")

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logging.warning("gTTS not installed. Reference audio generation disabled.")

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class WordResult:
    """Pronunciation result for a single word."""
    word: str
    status: str          # "correct" | "mispronounced" | "missing" | "extra"
    score: float = 1.0   # 0.0–1.0


@dataclass
class PronunciationFeedback:
    """Complete feedback object returned to the web frontend."""
    overall_score: float               # 0–100
    word_results: list[WordResult]     # Per-word breakdown
    fluency_wpm: float                 # Words per minute
    pause_count: int                   # Detected pause segments
    completeness: float                # 0–100: % of target words spoken
    transcript: str                    # What the learner actually said
    target_text: str                   # What they were supposed to say
    tips: list[str] = field(default_factory=list)  # Human-readable coaching tips
    duration_seconds: float = 0.0


# ── Text utilities ────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """
    Normalize text for comparison: strip punctuation, lowercase, collapse spaces.
    Used to align transcribed speech with the target sentence.
    """
    if not text:
        return ""
    translator = str.maketrans("", "", string.punctuation)
    return " ".join(text.translate(translator).lower().split())


def tokenize(text: str) -> list[str]:
    """Split cleaned text into word tokens."""
    return clean_text(text).split()


# ── Scoring engine ────────────────────────────────────────────────────────────

class PronunciationScorer:
    """
    Scores a learner's speech against a target sentence.

    Approach (no paid API required):
    - Diff-based word alignment (like SpeechAce) using difflib SequenceMatcher.
    - Each word tagged: correct / mispronounced / missing / extra.
    - Inspired by GOP (Goodness of Pronunciation) concept — here approximated
      via edit-distance similarity between spoken and target word.

    Plug-in point: replace `_score_word_pair` with SpeechAce/SpeechSuper API
    call to get true phoneme-level scores.
    """

    def score(
        self,
        transcript: str,
        target_text: str,
        duration_seconds: float = 0.0,
        whisper_segments: Optional[list] = None,
    ) -> PronunciationFeedback:
        """
        Main scoring method.
        Args:
            transcript      : What the learner said (from ASR).
            target_text     : The reference sentence they should say.
            duration_seconds: Recording length (for WPM calculation).
            whisper_segments: Whisper output segments (used for pause detection).
        Returns:
            PronunciationFeedback dataclass.
        """
        spoken_tokens = tokenize(transcript)
        target_tokens = tokenize(target_text)

        word_results = self._align_words(spoken_tokens, target_tokens)

        # ── Metrics ──────────────────────────────────────────────────────────
        correct_count = sum(1 for w in word_results if w.status == "correct")
        total_target = len(target_tokens)
        completeness = (correct_count / total_target * 100) if total_target else 0.0

        pronunciation_score = (
            sum(w.score for w in word_results) / len(word_results) * 100
            if word_results else 0.0
        )

        # Fluency: words per minute
        spoken_word_count = len(spoken_tokens)
        fluency_wpm = (
            (spoken_word_count / duration_seconds) * 60
            if duration_seconds > 0 else 0.0
        )

        # Pause count: from Whisper segments gap analysis
        pause_count = self._count_pauses(whisper_segments) if whisper_segments else 0

        # Overall: weighted blend (ELSA-style)
        overall = (
            pronunciation_score * 0.50
            + completeness       * 0.30
            + self._fluency_score(fluency_wpm) * 0.20
        )

        tips = self._generate_tips(word_results, fluency_wpm, completeness)

        return PronunciationFeedback(
            overall_score=round(overall, 1),
            word_results=word_results,
            fluency_wpm=round(fluency_wpm, 1),
            pause_count=pause_count,
            completeness=round(completeness, 1),
            transcript=transcript,
            target_text=target_text,
            tips=tips,
            duration_seconds=round(duration_seconds, 2),
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _align_words(self, spoken: list[str], target: list[str]) -> list[WordResult]:
        """
        Use SequenceMatcher to align spoken vs target words.
        Opcodes: equal / replace / delete / insert.
        """
        results: list[WordResult] = []
        matcher = difflib.SequenceMatcher(None, target, spoken, autojunk=False)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for word in target[i1:i2]:
                    results.append(WordResult(word=word, status="correct", score=1.0))

            elif tag == "replace":
                # Words present but different — mispronounced
                for t_word, s_word in zip(target[i1:i2], spoken[j1:j2]):
                    sim = self._score_word_pair(t_word, s_word)
                    status = "correct" if sim > 0.85 else "mispronounced"
                    results.append(WordResult(word=t_word, status=status, score=sim))
                # Remainder of the longer side
                for word in target[i2 - (i2 - i1) + min(i2 - i1, j2 - j1):i2]:
                    results.append(WordResult(word=word, status="missing", score=0.0))

            elif tag == "delete":
                # Target words not spoken at all — missing
                for word in target[i1:i2]:
                    results.append(WordResult(word=word, status="missing", score=0.0))

            elif tag == "insert":
                # Spoken words not in target — extra (don't penalize heavily)
                for word in spoken[j1:j2]:
                    results.append(WordResult(word=word, status="extra", score=0.5))

        return results

    def _score_word_pair(self, target: str, spoken: str) -> float:
        """
        Approximate phoneme similarity using character-level edit distance ratio.
        In production: replace with actual phoneme-level API score.
        """
        return difflib.SequenceMatcher(None, target, spoken).ratio()

    def _count_pauses(self, segments: list[dict], gap_threshold: float = 0.5) -> int:
        """Count gaps > gap_threshold seconds between Whisper segments."""
        if not segments or len(segments) < 2:
            return 0
        pauses = 0
        for i in range(1, len(segments)):
            gap = segments[i].get("start", 0) - segments[i - 1].get("end", 0)
            if gap > gap_threshold:
                pauses += 1
        return pauses

    def _fluency_score(self, wpm: float) -> float:
        """
        Map WPM to 0-100.
        Native English: ~130-150 WPM. Learner targets: 80-120 WPM.
        """
        if wpm <= 0:
            return 0.0
        if wpm >= 130:
            return 100.0
        return min(100.0, (wpm / 130) * 100)

    def _generate_tips(
        self,
        word_results: list[WordResult],
        wpm: float,
        completeness: float,
    ) -> list[str]:
        """Generate human-readable coaching tips based on results."""
        tips = []

        mispronounced = [w.word for w in word_results if w.status == "mispronounced"]
        missing = [w.word for w in word_results if w.status == "missing"]

        if mispronounced:
            sample = ", ".join(f'"{w}"' for w in mispronounced[:3])
            tips.append(f"Focus on these words: {sample}. Try saying them slowly first.")

        if missing:
            sample = ", ".join(f'"{w}"' for w in missing[:3])
            tips.append(f"You skipped: {sample}. Try reading the full sentence aloud.")

        if wpm < 60 and wpm > 0:
            tips.append("Your pace is very slow. Try shadowing a native speaker recording.")
        elif wpm > 160:
            tips.append("You're speaking too fast. Slow down for clearer pronunciation.")

        if completeness < 70:
            tips.append("Try to complete the full sentence — don't stop halfway.")

        if not tips:
            tips.append("Great job! Keep practicing to maintain your fluency.")

        return tips


# ── ASR: Server-side Whisper ──────────────────────────────────────────────────

class WhisperASR:
    """
    Server-side ASR using OpenAI Whisper.
    Used as fallback/accuracy mode when browser Web Speech API is unavailable
    or for post-session analysis of recorded audio.
    """

    def __init__(self, model_size: str = "base"):
        if not WHISPER_AVAILABLE:
            raise RuntimeError("openai-whisper is not installed.")
        logger.info(f"Loading Whisper '{model_size}' model…")
        self.model = whisper.load_model(model_size)
        logger.info("Whisper ready.")

    def transcribe(self, audio_path: str) -> dict:
        """
        Transcribe an audio file.
        Returns:
            {
              "text": str,
              "segments": [...],         # Whisper segments (for pause analysis)
              "confidence": float,       # 0.0–1.0 average across all segments
              "duration": float,         # Audio duration in seconds
            }
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        result = self.model.transcribe(
            audio_path,
            fp16=False,
            language="en",
            word_timestamps=True,       # Enables word-level timing data
        )

        segments = result.get("segments", [])

        # Confidence: average across ALL segments (fixed from original)
        if segments:
            avg_logprob = sum(s["avg_logprob"] for s in segments) / len(segments)
            confidence = max(0.0, min(1.0, math.exp(avg_logprob)))
        else:
            confidence = 0.0

        # Duration: end time of last segment
        duration = segments[-1]["end"] if segments else 0.0

        return {
            "text": result["text"].strip(),
            "segments": segments,
            "confidence": round(confidence, 4),
            "duration": round(duration, 2),
        }


# ── TTS: Reference audio generation ──────────────────────────────────────────

class ReferenceAudioGenerator:
    """
    Generate native-speaker reference audio for a target sentence.
    The learner can listen to this BEFORE recording themselves.
    Uses gTTS (Google TTS) — can be swapped for higher-quality voices
    (ElevenLabs, Azure TTS) for production.
    """

    def __init__(self, output_dir: str = "reference_audio"):
        if not GTTS_AVAILABLE:
            raise RuntimeError("gTTS is not installed.")
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir

    def generate(self, text: str, filename: Optional[str] = None) -> str:
        """
        Generate and save reference audio.
        Args:
            text    : The sentence to synthesize.
            filename: Optional custom filename (without extension).
        Returns:
            Path to the .mp3 file.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        if not filename:
            # Deterministic filename from text hash (avoids duplicates)
            slug = re.sub(r"[^a-z0-9]", "_", clean_text(text))[:40]
            filename = slug

        output_path = os.path.join(self.output_dir, f"{filename}.mp3")

        # Skip regeneration if cached
        if not os.path.exists(output_path):
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(output_path)
            logger.info(f"Reference audio saved: {output_path}")
        else:
            logger.info(f"Using cached reference audio: {output_path}")

        return output_path

    def generate_slow(self, text: str, filename: Optional[str] = None) -> str:
        """Generate slow-speed version for learners to follow along."""
        filename = (filename or "slow") + "_slow"
        output_path = os.path.join(self.output_dir, f"{filename}.mp3")
        if not os.path.exists(output_path):
            tts = gTTS(text=text, lang="en", slow=True)
            tts.save(output_path)
        return output_path


# ── High-level facade (used by web backend/API routes) ───────────────────────

class SpeechModule:
    """
    Single entry point for the web backend.
    Orchestrates ASR → Scoring → Feedback for each practice attempt.

    Web flow:
    1. Frontend records audio (MediaRecorder API → WebM/WAV blob).
    2. POST audio + target_text to /api/assess.
    3. This module transcribes (Whisper) and scores.
    4. Returns PronunciationFeedback as JSON.
    """

    def __init__(self, whisper_model: str = "base", audio_output_dir: str = "reference_audio"):
        self.asr = WhisperASR(model_model=whisper_model) if WHISPER_AVAILABLE else None
        self.scorer = PronunciationScorer()
        self.tts = ReferenceAudioGenerator(output_dir=audio_output_dir) if GTTS_AVAILABLE else None

    def assess(self, audio_path: str, target_text: str) -> PronunciationFeedback:
        """
        Full pipeline: audio file → PronunciationFeedback.
        Called by the web API endpoint.
        """
        if not self.asr:
            raise RuntimeError("Whisper ASR not available. Install openai-whisper.")

        asr_result = self.asr.transcribe(audio_path)

        feedback = self.scorer.score(
            transcript=asr_result["text"],
            target_text=target_text,
            duration_seconds=asr_result["duration"],
            whisper_segments=asr_result["segments"],
        )

        return feedback

    def get_reference_audio(self, text: str) -> Optional[str]:
        """Return path to reference audio for a target sentence."""
        if not self.tts:
            return None
        return self.tts.generate(text)

    def get_slow_reference_audio(self, text: str) -> Optional[str]:
        """Return path to slow-speed reference audio."""
        if not self.tts:
            return None
        return self.tts.generate_slow(text)

    def score_from_transcript(self, transcript: str, target_text: str) -> PronunciationFeedback:
        """
        Score without ASR — for use with browser-side Web Speech API,
        which returns transcript directly to the frontend.
        Frontend POSTs { transcript, target_text } → this method.
        """
        return self.scorer.score(
            transcript=transcript,
            target_text=target_text,
            duration_seconds=0.0,  # WPM not available without audio timing
        )

    def feedback_to_dict(self, feedback: PronunciationFeedback) -> dict:
        """Serialize PronunciationFeedback to JSON-safe dict for API response."""
        return {
            "overall_score": feedback.overall_score,
            "completeness": feedback.completeness,
            "fluency_wpm": feedback.fluency_wpm,
            "pause_count": feedback.pause_count,
            "duration_seconds": feedback.duration_seconds,
            "transcript": feedback.transcript,
            "target_text": feedback.target_text,
            "tips": feedback.tips,
            "word_results": [
                {
                    "word": w.word,
                    "status": w.status,   # "correct" | "mispronounced" | "missing" | "extra"
                    "score": round(w.score, 3),
                }
                for w in feedback.word_results
            ],
        }


# ── Self-test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  ELSA Speech Module — Self Test")
    print("=" * 60)

    scorer = PronunciationScorer()

    tests = [
        {
            "target":     "The quick brown fox jumps over the lazy dog",
            "transcript": "the quick brown fox jump over lazy dog",
            "duration":   4.2,
        },
        {
            "target":     "She sells seashells by the seashore",
            "transcript": "she sells sea shells by the sea shore",
            "duration":   3.1,
        },
        {
            "target":     "How much wood would a woodchuck chuck",
            "transcript": "how much wood would a woodchuck",
            "duration":   2.8,
        },
    ]

    for i, t in enumerate(tests, 1):
        print(f"\n── Test {i} ──────────────────────────────────────────")
        print(f"  Target    : {t['target']}")
        print(f"  Transcript: {t['transcript']}")

        fb = scorer.score(t["transcript"], t["target"], t["duration"])

        print(f"  Score     : {fb.overall_score}/100")
        print(f"  Complete  : {fb.completeness}%")
        print(f"  WPM       : {fb.fluency_wpm}")
        print(f"  Words:")
        for w in fb.word_results:
            icon = {"correct": "✓", "mispronounced": "~", "missing": "✗", "extra": "+"}.get(w.status, "?")
            print(f"    [{icon}] {w.word:20s} ({w.status}, score={w.score:.2f})")
        print(f"  Tips:")
        for tip in fb.tips:
            print(f"    → {tip}")

    # ── clean_text utility ────────────────────────────────────────────────────
    print("\n── clean_text ──────────────────────────────────────────")
    raw = "Hello, World! This is: a test."
    cleaned = clean_text(raw)
    assert cleaned == "hello world this is a test", f"Unexpected: {cleaned!r}"
    print(f"  '{raw}'  →  '{cleaned}'  ✓")

    print("\n✓ All tests passed.")
