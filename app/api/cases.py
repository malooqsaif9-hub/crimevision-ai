from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core import database as db
from app.core.schemas import AuditEntry, Case

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("/")
def list_cases_stub():
    """List persisted cases (compatibility route under /api/cases)."""
    return {"cases": db.list_cases()}


@router.get("/{case_id}")
def get_case_stub(case_id: str):
    case = db.get_case(case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    return case


@router.post("/", response_model=Case)
def create_case(title: str, description: str = ""):
    if not title.strip():
        raise HTTPException(400, "Case title is required")
    case = Case(title=title.strip(), description=description)
    db.save_case(case)
    db.log_audit(AuditEntry(case_id=case.case_id, action="create_case", details=case.title))
    return case
