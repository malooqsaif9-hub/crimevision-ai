```python
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add the repository root to Python's module search path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException

from app.config import APP_NAME, DISCLAIMER
from app.core import database as db
from app.core.provenance import save_evidence, verify_integrity
from app.core.schemas import Case, AuditEntry
from app.api.audio import router as audio_router
from app.api.images import router as images_router
from app.api.video import router as video_router
from app.api.chat import router as chat_router
from app.api.reports import router as reports_router
from app.api.timeline import router as timeline_router
from app.api.cases import router as cases_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(
    title=APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": APP_NAME,
        "disclaimer": DISCLAIMER,
    }


@app.post("/cases", response_model=Case)
def create_case(
    title: str = Form(...),
    description: str = Form(""),
):
    if not title or not title.strip():
        raise HTTPException(400, "Case title is required")

    case = Case(
        title=title.strip(),
        description=description,
    )
    db.save_case(case)
    db.log_audit(
        AuditEntry(
            case_id=case.case_id,
            action="create_case",
            details=title.strip(),
        )
    )
    return case


@app.get("/cases")
def get_cases():
    return db.list_cases()


@app.post("/cases/{case_id}/evidence")
def upload_evidence(
    case_id: str,
    file: UploadFile = File(...),
    uploaded_by: str = Form("system"),
):
    if not case_id or not case_id.strip():
        raise HTTPException(400, "Case ID is required")

    if not db.get_case(case_id):
        raise HTTPException(404, "Case not found")

    try:
        record = save_evidence(file, case_id, uploaded_by)
    except ValueError as e:
        raise HTTPException(400, str(e))

    db.save_evidence_record(record)
    db.log_audit(
        AuditEntry(
            case_id=case_id,
            evidence_id=record.evidence_id,
            action="upload",
            actor=uploaded_by,
            details=f"{record.original_filename} sha256={record.sha256}",
        )
    )
    return record


@app.get("/cases/{case_id}/evidence")
def get_case_evidence(case_id: str):
    return db.list_evidence(case_id)


@app.get("/evidence/{evidence_id}/verify")
def verify(evidence_id: str):
    rec = db.get_evidence(evidence_id)
    if not rec:
        raise HTTPException(404, "Evidence not found")

    return {
        "evidence_id": evidence_id,
        "sha256": rec.sha256,
        "intact": verify_integrity(rec),
    }


@app.get("/cases/{case_id}/audit")
def get_audit(case_id: str):
    return db.list_audit(case_id)


app.include_router(images_router)
app.include_router(audio_router)
app.include_router(video_router)
app.include_router(timeline_router)
app.include_router(chat_router)
app.include_router(reports_router)
app.include_router(cases_router)
```
