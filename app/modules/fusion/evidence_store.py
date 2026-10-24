from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class EvidenceRecord:
    evidence_id: str
    case_id: str
    source_type: str
    label: str
    description: str
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)


class EvidenceStore:
    """In-memory store for multimodal evidence records."""

    def __init__(self):
        self._records: list[EvidenceRecord] = []

    def add_record(self, record: EvidenceRecord) -> None:
        self._records.append(record)

    def list_records(self) -> list[EvidenceRecord]:
        return list(self._records)

    def build_timeline(self) -> list[dict]:
        records = sorted(
            self._records,
            key=lambda item: item.timestamp or datetime.now(timezone.utc).isoformat(),
        )
        return [
            {
                "evidence_id": item.evidence_id,
                "case_id": item.case_id,
                "source_type": item.source_type,
                "label": item.label,
                "description": item.description,
                "timestamp": item.timestamp,
                "metadata": item.metadata,
            }
            for item in records
        ]
