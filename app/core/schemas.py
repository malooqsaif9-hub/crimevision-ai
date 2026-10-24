from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class MediaType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class FindingType(str, Enum):
    OBSERVATION = "observation"   # directly detected/transcribed by a model
    INFERENCE = "inference"       # interpretation or hypothesis


class ReviewStatus(str, Enum):
    UNVERIFIED = "unverified_lead"   # default for everything AI produces
    CONFIRMED = "confirmed_by_reviewer"
    REJECTED = "rejected_by_reviewer"


class Case(BaseModel):
    case_id: str = Field(default_factory=lambda: new_id("case"))
    title: str
    description: str = ""
    created_at: datetime = Field(default_factory=utcnow)


class EvidenceFile(BaseModel):
    """One original uploaded file. Never modified after upload."""
    evidence_id: str = Field(default_factory=lambda: new_id("ev"))
    case_id: str
    original_filename: str
    stored_path: str
    media_type: MediaType
    sha256: str
    size_bytes: int
    uploaded_at: datetime = Field(default_factory=utcnow)
    uploaded_by: str = "system"


class Finding(BaseModel):
    """One AI-produced item: a detection, a transcript segment, a caption, a hypothesis."""
    finding_id: str = Field(default_factory=lambda: new_id("fd"))
    case_id: str
    evidence_id: str                      # provenance link to the source file
    finding_type: FindingType
    label: str                            # e.g. "person", "knife", "said: 'I heard a bang'"
    description: str = ""
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # Where in the source this came from (preserved, never invented)
    source_time_sec: Optional[float] = None   # position in video/audio
    source_end_time_sec: Optional[float] = None
    frame_index: Optional[int] = None
    bbox: Optional[list[float]] = None        # [x1, y1, x2, y2]

    # Which model made it
    model_name: str
    model_version: str = "unknown"

    status: ReviewStatus = ReviewStatus.UNVERIFIED
    created_at: datetime = Field(default_factory=utcnow)


class AuditEntry(BaseModel):
    """Append-only log of every action on evidence."""
    entry_id: str = Field(default_factory=lambda: new_id("au"))
    case_id: str
    evidence_id: Optional[str] = None
    action: str                    # "upload", "analyze", "review", "report"
    actor: str = "system"
    details: str = ""
    timestamp: datetime = Field(default_factory=utcnow)