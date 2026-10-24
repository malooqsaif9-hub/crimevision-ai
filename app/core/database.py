from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL
from app.core.schemas import Case, EvidenceFile, Finding, AuditEntry

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


class CaseRow(Base):
    __tablename__ = "cases"
    id = Column(String, primary_key=True)
    data = Column(Text, nullable=False)


class EvidenceRow(Base):
    __tablename__ = "evidence"
    id = Column(String, primary_key=True)
    case_id = Column(String, index=True)
    data = Column(Text, nullable=False)


class FindingRow(Base):
    __tablename__ = "findings"
    id = Column(String, primary_key=True)
    case_id = Column(String, index=True)
    evidence_id = Column(String, index=True)
    data = Column(Text, nullable=False)


class AuditRow(Base):
    __tablename__ = "audit_log"
    id = Column(String, primary_key=True)
    case_id = Column(String, index=True)
    data = Column(Text, nullable=False)


def init_db():
    Base.metadata.create_all(engine)


# ---- Simple helpers (save/get) ----
def save_case(c: Case):
    with SessionLocal() as s:
        s.merge(CaseRow(id=c.case_id, data=c.model_dump_json()))
        s.commit()


def get_case(case_id: str) -> Case | None:
    with SessionLocal() as s:
        row = s.get(CaseRow, case_id)
        return Case.model_validate_json(row.data) if row else None


def list_cases() -> list[Case]:
    with SessionLocal() as s:
        return [Case.model_validate_json(r.data) for r in s.query(CaseRow).all()]


def save_evidence_record(e: EvidenceFile):
    with SessionLocal() as s:
        s.merge(EvidenceRow(id=e.evidence_id, case_id=e.case_id, data=e.model_dump_json()))
        s.commit()


def get_evidence(evidence_id: str) -> EvidenceFile | None:
    with SessionLocal() as s:
        row = s.get(EvidenceRow, evidence_id)
        return EvidenceFile.model_validate_json(row.data) if row else None


def list_evidence(case_id: str) -> list[EvidenceFile]:
    with SessionLocal() as s:
        rows = s.query(EvidenceRow).filter_by(case_id=case_id).all()
        return [EvidenceFile.model_validate_json(r.data) for r in rows]


def save_finding(f: Finding):
    with SessionLocal() as s:
        s.merge(FindingRow(id=f.finding_id, case_id=f.case_id,
                           evidence_id=f.evidence_id, data=f.model_dump_json()))
        s.commit()


def list_findings(case_id: str) -> list[Finding]:
    with SessionLocal() as s:
        rows = s.query(FindingRow).filter_by(case_id=case_id).all()
        return [Finding.model_validate_json(r.data) for r in rows]


def log_audit(entry: AuditEntry):
    """Append-only: there is intentionally no update or delete function."""
    with SessionLocal() as s:
        s.add(AuditRow(id=entry.entry_id, case_id=entry.case_id, data=entry.model_dump_json()))
        s.commit()


def list_audit(case_id: str) -> list[AuditEntry]:
    with SessionLocal() as s:
        rows = s.query(AuditRow).filter_by(case_id=case_id).all()
        return [AuditEntry.model_validate_json(r.data) for r in rows]