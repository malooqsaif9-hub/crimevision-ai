from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import DISCLAIMER
from app.core import database as db
from app.core.provenance import verify_integrity
from app.core.schemas import AuditEntry, MediaType
from app.modules.audio_analysis.event_extractor import EventExtractor
from app.modules.audio_analysis.transcriber import AudioTranscriber

router = APIRouter(tags=["audio analysis"])


@router.post("/evidence/{evidence_id}/transcribe-audio")
def transcribe_audio(evidence_id: str):
    evidence = db.get_evidence(evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found")
    if evidence.media_type != MediaType.AUDIO:
        raise HTTPException(400, "This endpoint only accepts audio evidence")
    if not verify_integrity(evidence):
        raise HTTPException(409, "Integrity check failed: file no longer matches its upload hash")

    try:
        transcriber = AudioTranscriber()
        transcript = transcriber.transcribe(evidence.stored_path)
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        raise HTTPException(503, f"Audio transcription unavailable: {exc}") from exc

    findings = EventExtractor().to_findings(
        transcript["segments"],
        evidence.case_id,
        evidence.evidence_id,
        model_name=f"faster-whisper:{transcriber.model_size}",
        model_version="faster-whisper",
    )
    for finding in findings:
        db.save_finding(finding)
    db.log_audit(
        AuditEntry(
            case_id=evidence.case_id,
            evidence_id=evidence_id,
            action="transcribe_audio",
            details=f"{len(findings)} timestamped transcript segments (unverified observations)",
        )
    )
    return {
        "evidence_id": evidence_id,
        "disclaimer": DISCLAIMER,
        "transcript": transcript,
        "findings": findings,
    }
