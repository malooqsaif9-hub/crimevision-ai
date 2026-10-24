import io

from fastapi.testclient import TestClient

from app.core.schemas import Finding, FindingType
from app.main import app
from app.modules.video_analysis.frame_sampler import SampledFrame


def test_video_endpoint_saves_findings_with_frame_timestamps(monkeypatch, tmp_path):
    frame_path = tmp_path / "frame_00000012.jpg"
    frame_path.write_bytes(b"frame")

    class FakeSampler:
        def sample(self, video_path, case_id, evidence_id):
            return [SampledFrame(frame_index=12, timestamp_sec=2.4, path=frame_path)]

    def fake_detect_objects(image_path, case_id, evidence_id):
        return [
            Finding(
                case_id=case_id,
                evidence_id=evidence_id,
                finding_type=FindingType.OBSERVATION,
                label="person",
                confidence=0.9,
                bbox=[1, 2, 3, 4],
                model_name="test-detector",
            )
        ]

    monkeypatch.setattr("app.api.video.FrameSampler", FakeSampler)
    monkeypatch.setattr("app.api.video.detect_objects", fake_detect_objects)

    with TestClient(app) as client:
        case = client.post("/cases", data={"title": "Video timestamp test"}).json()
        evidence = client.post(
            f"/cases/{case['case_id']}/evidence",
            files={"file": ("scene.mp4", io.BytesIO(b"video bytes"), "video/mp4")},
        ).json()

        response = client.post(f"/evidence/{evidence['evidence_id']}/analyze-video")

        assert response.status_code == 200
        body = response.json()
        assert body["frames_sampled"] == 1
        assert body["observations"][0]["source_time_sec"] == 2.4
        assert body["observations"][0]["frame_index"] == 12
        assert body["observations"][0]["status"] == "unverified_lead"
        assert "do not establish guilt" in body["disclaimer"]

        stored = client.get(
            f"/cases/{case['case_id']}/findings",
            params={"evidence_id": evidence["evidence_id"]},
        ).json()
        assert stored["count"] == 1
        audit = client.get(f"/cases/{case['case_id']}/audit").json()
        assert any(entry["action"] == "analyze_video" for entry in audit)


def test_video_endpoint_rejects_non_video_evidence():
    with TestClient(app) as client:
        case = client.post("/cases", data={"title": "Wrong media test"}).json()
        evidence = client.post(
            f"/cases/{case['case_id']}/evidence",
            files={"file": ("recording.wav", io.BytesIO(b"audio bytes"), "audio/wav")},
        ).json()

        response = client.post(f"/evidence/{evidence['evidence_id']}/analyze-video")

        assert response.status_code == 400
