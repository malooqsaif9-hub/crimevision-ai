import io

from fastapi.testclient import TestClient

from app.core import database as db
from app.core.schemas import Finding, FindingType
from app.main import app


def test_timeline_groups_findings_by_source_and_keeps_relative_time():
    with TestClient(app) as client:
        case = client.post("/cases", data={"title": "Timeline test"}).json()
        evidence = client.post(
            f"/cases/{case['case_id']}/evidence",
            files={"file": ("recording.wav", io.BytesIO(b"audio"), "audio/wav")},
        ).json()
        db.save_finding(
            Finding(
                case_id=case["case_id"],
                evidence_id=evidence["evidence_id"],
                finding_type=FindingType.OBSERVATION,
                label="transcript_segment",
                description="I heard a bang.",
                source_time_sec=4.5,
                source_end_time_sec=5.2,
                model_name="test-model",
            )
        )

        response = client.get(f"/cases/{case['case_id']}/timeline")

        assert response.status_code == 200
        body = response.json()
        assert body["evidence_groups"][0]["events"][0]["source_time_sec"] == 4.5
        assert body["evidence_groups"][0]["events"][0]["source_end_time_sec"] == 5.2
        assert "upload time is not the incident time" in body["chronology_note"]


def test_chat_answers_with_case_finding_citations():
    with TestClient(app) as client:
        case = client.post("/cases", data={"title": "Chat test"}).json()
        evidence = client.post(
            f"/cases/{case['case_id']}/evidence",
            files={"file": ("recording.wav", io.BytesIO(b"audio"), "audio/wav")},
        ).json()
        db.save_finding(
            Finding(
                case_id=case["case_id"],
                evidence_id=evidence["evidence_id"],
                finding_type=FindingType.OBSERVATION,
                label="transcript_segment",
                description="A witness said they heard a loud bang.",
                source_time_sec=8.0,
                model_name="test-model",
            )
        )

        response = client.post(
            f"/cases/{case['case_id']}/chat",
            json={"query": "loud bang"},
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["citations"]) == 1
        assert body["citations"][0]["evidence_id"] == evidence["evidence_id"]
        assert "human verification required" in body["answer"]


def test_case_report_contains_a_pdf_and_logs_audit(monkeypatch, tmp_path):
    monkeypatch.setattr("app.api.reports.REPORT_DIR", tmp_path)

    with TestClient(app) as client:
        case = client.post("/cases", data={"title": "Report test"}).json()
        response = client.post(f"/cases/{case['case_id']}/report")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content.startswith(b"%PDF")
        audit = client.get(f"/cases/{case['case_id']}/audit").json()
        assert any(entry["action"] == "report" for entry in audit)