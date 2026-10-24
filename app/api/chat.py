from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import DISCLAIMER
from app.core import database as db
from app.modules.chat.qa_engine import QuestionAnswerEngine
from app.modules.chat.retriever import EvidenceRetriever

router = APIRouter(tags=["case chat"])


class ChatQuestion(BaseModel):
    query: str = Field(min_length=1)


@router.post("/cases/{case_id}/chat")
def answer_question(case_id: str, question: ChatQuestion):
    if not db.get_case(case_id):
        raise HTTPException(404, "Case not found")
    if not question.query.strip():
        raise HTTPException(400, "Question cannot be blank")

    evidence_by_id = {item.evidence_id: item for item in db.list_evidence(case_id)}
    records = []
    for finding in db.list_findings(case_id):
        evidence = evidence_by_id.get(finding.evidence_id)
        records.append(
            {
                "finding_id": finding.finding_id,
                "evidence_id": finding.evidence_id,
                "label": finding.label,
                "description": finding.description,
                "source_type": evidence.media_type.value if evidence else "unknown",
                "original_filename": evidence.original_filename if evidence else "",
                "source_time_sec": finding.source_time_sec,
                "finding_type": finding.finding_type.value,
                "status": finding.status.value,
            }
        )

    matches = EvidenceRetriever(records).search(question.query)
    return {
        "case_id": case_id,
        "query": question.query,
        "answer": QuestionAnswerEngine().answer(question.query, matches),
        "citations": matches,
        "disclaimer": DISCLAIMER,
    }
