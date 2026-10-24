import io

from fastapi.testclient import TestClient

from app.core.schemas import FindingType
from app.main import app
from app.modules.audio_analysis.event_extractor import EventExtractor


def test_transcript_segments_keep_source_time_and_provenance():
    findings = EventExtractor().to_findings(
        [{"start": 1.25, "end": 3.75, "text": "I heard a loud sound."}],
        case_id="case_test",
        evidence_id="ev_test",
        model_name="faster-whisper:base",
        model_version="test",
    )

    assert len(findings) == 1
    finding = findings[0]
    assert finding.finding_type == FindingType.OBSERVATION
    assert finding.source_time_sec == 1.25
    assert finding.source_end_time_sec == 3.75
    assert finding.case_id == "case_test"
    assert finding.evidence_id == "ev_test"


def test_transcribe_audio_endpoint_persists_timestamped_findings(monkeypatch):
    class FakeTranscriber:
        model_size = "test"

        def transcribe(self, audio_path):
            assert audio_path.endswith(".wav")
            return {
                "text": "A door closed.",
                "segments": [{"start": 2.0, "end": 3.0, "text": "A door closed."}],
            }

    monkeypatch.setattr("app.api.audio.AudioTranscriber", FakeTranscriber)

    with TestClient(app) as client:
        case = client.post("/cases", data={"title": "Audio test"}).json()
        evidence = client.post(
            f"/cases/{case['case_id']}/evidence",
            files={"file": ("recording.wav", io.BytesIO(b"audio bytes"), "audio/wav")},
        ).json()

        response = client.post(f"/evidence/{evidence['evidence_id']}/transcribe-audio")

        assert response.status_code == 200
        body = response.json()
        assert body["findings"][0]["source_time_sec"] == 2.0
        assert body["findings"][0]["source_end_time_sec"] == 3.0
        assert body["findings"][0]["status"] == "unverified_lead"
        assert "do not establish guilt" in body["disclaimer"]

        stored = client.get(
            f"/cases/{case['case_id']}/findings",
            params={"evidence_id": evidence["evidence_id"]},
        ).json()
        assert stored["count"] == 1
        audit = client.get(f"/cases/{case['case_id']}/audit").json()
        assert any(entry["action"] == "transcribe_audio" for entry in audit)


def test_transcribe_audio_rejects_non_audio_evidence():
    with TestClient(app) as client:
        case = client.post("/cases", data={"title": "Wrong media test"}).json()
        evidence = client.post(
            f"/cases/{case['case_id']}/evidence",
            files={"file": ("scene.png", io.BytesIO(b"not a real image"), "image/png")},
        ).json()

        response = client.post(f"/evidence/{evidence['evidence_id']}/transcribe-audio")

        assert response.status_code == 400