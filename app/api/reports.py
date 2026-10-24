from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import DISCLAIMER, REPORT_DIR
from app.core import database as db
from app.core.schemas import AuditEntry
from app.modules.reports.pdf_generator import PDFReportGenerator

router = APIRouter(tags=["case reports"])


@router.post("/cases/{case_id}/report")
def generate_report(case_id: str):
    case = db.get_case(case_id)
    if not case:
        raise HTTPException(404, "Case not found")

    evidence = db.list_evidence(case_id)
    findings = db.list_findings(case_id)
    sections = [
        f"Case ID: {case.case_id}",
        f"Created: {case.created_at.isoformat()}",
        f"Description: {case.description or 'Not provided'}",
        f"Notice: {DISCLAIMER}",
        f"Evidence files ({len(evidence)}):",
    ]
    if not evidence:
        sections.append("No evidence files are stored in this case.")
    for item in evidence:
        sections.append(
            f"{item.original_filename} | {item.media_type.value} | evidence ID {item.evidence_id} | "
            f"SHA-256 {item.sha256} | uploaded {item.uploaded_at.isoformat()}"
        )

    sections.append(f"Findings ({len(findings)}):")
    if not findings:
        sections.append("No analysis findings are stored in this case.")
    for finding in findings:
        source_time = (
            f"{finding.source_time_sec:.2f}s"
            if finding.source_time_sec is not None
            else "not available"
        )
        if finding.source_end_time_sec is not None:
            source_time += f" to {finding.source_end_time_sec:.2f}s"
        sections.append(
            f"{finding.finding_type.value.upper()} | {finding.label} | {finding.status.value} | "
            f"finding ID {finding.finding_id} | evidence ID {finding.evidence_id} | "
            f"source time {source_time} | model {finding.model_name} {finding.model_version}\n"
            f"{finding.description}"
        )

    output_path = REPORT_DIR / case.case_id / f"report_{uuid4().hex}.pdf"
    try:
        generated_path = PDFReportGenerator().build(case.title, sections, output_path)
    except (OSError, ValueError) as exc:
        raise HTTPException(500, f"Unable to generate report: {exc}") from exc

    db.log_audit(
        AuditEntry(
            case_id=case_id,
            action="report",
            details=f"Generated report covering {len(evidence)} evidence files and {len(findings)} findings",
        )
    )
    return FileResponse(
        generated_path,
        media_type="application/pdf",
        filename=f"{case.case_id}_report.pdf",
    )
