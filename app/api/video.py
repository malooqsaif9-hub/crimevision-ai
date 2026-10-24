from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import DISCLAIMER
from app.core import database as db
from app.core.provenance import verify_integrity
from app.core.schemas import AuditEntry, MediaType
from app.modules.image_analysis.detector import detect_objects
from app.modules.video_analysis.frame_sampler import FrameSampler

router = APIRouter(tags=["video analysis"])


@router.post("/evidence/{evidence_id}/analyze-video")
def analyze_video(evidence_id: str):
    evidence = db.get_evidence(evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found")
    if evidence.media_type != MediaType.VIDEO:
        raise HTTPException(400, "This endpoint only accepts video evidence")
    if not verify_integrity(evidence):
        raise HTTPException(409, "Integrity check failed: file no longer matches its upload hash")

    try:
        frames = FrameSampler().sample(
            evidence.stored_path,
            evidence.case_id,
            evidence.evidence_id,
        )
    except (OSError, ValueError) as exc:
        raise HTTPException(422, f"Unable to sample video evidence: {exc}") from exc

    findings = []
    try:
        for frame in frames:
            frame_findings = detect_objects(
                str(frame.path),
                evidence.case_id,
                evidence.evidence_id,
            )
            findings.extend(
                finding.model_copy(
                    update={
                        "source_time_sec": frame.timestamp_sec,
                        "frame_index": frame.frame_index,
                    }
                )
                for finding in frame_findings
            )
    except (OSError, RuntimeError, ValueError) as exc:
        raise HTTPException(503, f"Video frame analysis unavailable: {exc}") from exc

    for finding in findings:
        db.save_finding(finding)
    db.log_audit(
        AuditEntry(
            case_id=evidence.case_id,
            evidence_id=evidence_id,
            action="analyze_video",
            details=(
                f"{len(frames)} frames sampled; {len(findings)} object findings "
                "(unverified observations)"
            ),
        )
    )
    return {
        "evidence_id": evidence_id,
        "disclaimer": DISCLAIMER,
        "frames_sampled": len(frames),
        "observations": findings,
    }
