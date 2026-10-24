from __future__ import annotations

from pathlib import Path


class AudioTranscriber:
    """Transcribe audio files and return a structured, reviewable summary."""

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "Audio transcription requires faster-whisper. Install project requirements."
            ) from exc
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio_path: str | Path) -> dict:
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(f"Audio evidence file not found: {path}")

        segments, _ = self.model.transcribe(str(path), word_timestamps=False)
        transcript_segments = [
            {
                "start": float(segment.start),
                "end": float(segment.end),
                "text": segment.text.strip(),
            }
            for segment in segments
            if segment.text.strip()
        ]
        return {
            "text": " ".join(segment["text"] for segment in transcript_segments),
            "segments": transcript_segments,
        }
