from __future__ import annotations


class ActionRecognizer:
    """Simple action recognition stub that can later call a video model."""

    def recognize(self, frames: list[str]) -> list[dict]:
        actions = []
        for idx, frame in enumerate(frames[:5], start=1):
            actions.append(
                {
                    "frame": frame,
                    "action": "observed_activity",
                    "confidence": 0.72,
                    "index": idx,
                    "source": "video",
                }
            )
        return actions
