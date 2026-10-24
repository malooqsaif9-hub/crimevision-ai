from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import DISCLAIMER
from app.core import database as db
from app.core.provenance import verify_integrity
from app.core.schemas import AuditEntry, FindingType, MediaType
from app.modules.image_analysis.analyzer import analyze_image, annotated_path

router = APIRouter(tags=["image analysis"])


@router.post("/evidence/{evidence_id}/analyze-image")
def analyze(evidence_id: str):
    ev = db.get_evidence(evidence_id)
    if not ev:
        raise HTTPException(404, "Evidence not found")
    if ev.media_type != MediaType.IMAGE:
        raise HTTPException(400, "This endpoint only accepts image evidence")
    if not verify_integrity(ev):
        raise HTTPException(409, "Integrity check failed: file no longer matches its upload hash")

    try:
        findings = analyze_image(ev)
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        raise HTTPException(503, f"Image analysis unavailable: {exc}") from exc
    for f in findings:
        db.save_finding(f)
    db.log_audit(AuditEntry(
        case_id=ev.case_id, evidence_id=evidence_id, action="analyze_image",
        details=f"{len(findings)} findings (unverified leads)"))

    return {
        "evidence_id": evidence_id,
        "disclaimer": DISCLAIMER,
        "observations": [f for f in findings if f.finding_type == FindingType.OBSERVATION],
        "inferences": [f for f in findings if f.finding_type == FindingType.INFERENCE],
    }


@router.get("/cases/{case_id}/findings")
def get_findings(case_id: str, evidence_id: Optional[str] = None,
                 finding_type: Optional[FindingType] = None):
    items = db.list_findings(case_id)
    if evidence_id:
        items = [f for f in items if f.evidence_id == evidence_id]
    if finding_type:
        items = [f for f in items if f.finding_type == finding_type]
    return {"disclaimer": DISCLAIMER, "count": len(items), "findings": items}


@router.get("/evidence/{evidence_id}/annotated")
def get_annotated(evidence_id: str):
    ev = db.get_evidence(evidence_id)
    if not ev:
        raise HTTPException(404, "Evidence not found")
    p = annotated_path(ev.case_id, evidence_id)
    if not p.exists():
        raise HTTPException(404, "Run analyze-image first")
    return FileResponse(p, media_type="image/jpeg")
