from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import DISCLAIMER
from app.core import database as db

router = APIRouter(tags=["timeline"])


@router.get("/cases/{case_id}/timeline")
def get_case_timeline(case_id: str):
    if not db.get_case(case_id):
        raise HTTPException(404, "Case not found")

    evidence = {item.evidence_id: item for item in db.list_evidence(case_id)}
    findings = db.list_findings(case_id)
    groups = []
    for item in evidence.values():
        item_findings = [finding for finding in findings if finding.evidence_id == item.evidence_id]
        item_findings.sort(
            key=lambda finding: (
                finding.source_time_sec is None,
                finding.source_time_sec if finding.source_time_sec is not None else 0,
                finding.created_at,
            )
        )
        groups.append(
            {
                "evidence_id": item.evidence_id,
                "original_filename": item.original_filename,
                "media_type": item.media_type,
                "uploaded_at": item.uploaded_at,
                "events": [
                    {
                        "finding_id": finding.finding_id,
                        "finding_type": finding.finding_type,
                        "label": finding.label,
                        "description": finding.description,
                        "source_time_sec": finding.source_time_sec,
                        "source_end_time_sec": finding.source_end_time_sec,
                        "frame_index": finding.frame_index,
                        "status": finding.status,
                        "model_name": finding.model_name,
                        "model_version": finding.model_version,
                    }
                    for finding in item_findings
                ],
            }
        )

    groups.sort(key=lambda group: group["uploaded_at"])
    return {
        "case_id": case_id,
        "disclaimer": DISCLAIMER,
        "chronology_note": (
            "Findings are ordered by media-relative time within each evidence file. "
            "Evidence files are grouped by upload time; upload time is not the incident time. "
            "Cross-file chronological alignment requires verified time metadata or reviewer offsets."
        ),
        "evidence_groups": groups,
    }
