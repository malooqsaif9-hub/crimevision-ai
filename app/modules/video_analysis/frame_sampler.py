from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import cv2

from app.config import PROCESSED_DIR


@dataclass(frozen=True)
class SampledFrame:
    frame_index: int
    timestamp_sec: float
    path: Path


class FrameSampler:
    """Sample frames to separate processed files without changing original evidence."""

    def sample(
        self,
        video_path: str | Path,
        case_id: str,
        evidence_id: str,
        interval_seconds: float = 5.0,
        max_frames: int = 10,
    ) -> list[SampledFrame]:
        if interval_seconds <= 0:
            raise ValueError("Frame sampling interval must be greater than zero")
        if max_frames <= 0:
            raise ValueError("Maximum frame count must be greater than zero")

        source = Path(video_path)
        capture = cv2.VideoCapture(str(source))
        if not capture.isOpened():
            capture.release()
            raise ValueError(f"Unable to open video evidence: {source.name}")

        try:
            fps = float(capture.get(cv2.CAP_PROP_FPS))
            if not math.isfinite(fps) or fps <= 0:
                raise ValueError("Video does not provide a valid frame rate")

            frame_interval = max(1, round(fps * interval_seconds))
            output_dir = PROCESSED_DIR / case_id / evidence_id
            output_dir.mkdir(parents=True, exist_ok=True)
            sampled: list[SampledFrame] = []
            frame_index = 0

            while len(sampled) < max_frames:
                success, frame = capture.read()
                if not success:
                    break
                if frame_index % frame_interval == 0:
                    frame_path = output_dir / f"frame_{frame_index:08d}.jpg"
                    if not cv2.imwrite(str(frame_path), frame):
                        raise OSError(f"Unable to save sampled frame {frame_index}")
                    sampled.append(
                        SampledFrame(
                            frame_index=frame_index,
                            timestamp_sec=frame_index / fps,
                            path=frame_path,
                        )
                    )
                frame_index += 1
            return sampled
        finally:
            capture.release()
