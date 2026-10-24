from __future__ import annotations

from app.core.schemas import Finding, FindingType


class EventExtractor:
    """Represent recognized speech segments without inventing event timestamps."""

    def to_findings(
        self,
        segments: list[dict],
        case_id: str,
        evidence_id: str,
        model_name: str,
        model_version: str,
    ) -> list[Finding]:
        findings = []
        for segment in segments:
            text = str(segment.get("text", "")).strip()
            if not text:
                continue
            findings.append(
                Finding(
                    case_id=case_id,
                    evidence_id=evidence_id,
                    finding_type=FindingType.OBSERVATION,
                    label="transcript_segment",
                    description=text,
                    source_time_sec=float(segment["start"]),
                    source_end_time_sec=float(segment["end"]),
                    model_name=model_name,
                    model_version=model_version,
                )
            )
        return findings
