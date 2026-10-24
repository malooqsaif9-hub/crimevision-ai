from __future__ import annotations


class TimelineFusionEngine:
    """Combine evidence from image, audio, and video into a unified timeline."""

    def fuse(self, records: list[dict]) -> list[dict]:
        sorted_records = sorted(records, key=lambda item: item.get("timestamp", ""))
        timeline = []
        for idx, item in enumerate(sorted_records, start=1):
            timeline.append(
                {
                    "event_id": f"timeline_{idx}",
                    "timestamp": item.get("timestamp", "unknown"),
                    "source_type": item.get("source_type", "unknown"),
                    "label": item.get("label", "evidence"),
                    "description": item.get("description", ""),
                    "provenance": item.get("metadata", {}),
                }
            )
        return timeline
