import io
from fastapi.testclient import TestClient

from app.core.schemas import Finding, FindingType, ReviewStatus
from app.main import app
from app.modules.image_analysis.hypotheses import generate_hypotheses


def _obs(label, bbox, conf=0.9):
    return Finding(case_id="c", evidence_id="e", finding_type=FindingType.OBSERVATION,
                   label=label, confidence=conf, bbox=bbox, model_name="test")


def test_weapon_near_person_is_unverified_inference():
    person = _obs("person", [100, 100, 200, 400])
    knife = _obs("knife", [190, 250, 230, 300], 0.6)
    hyps = generate_hypotheses([person, knife], "c", "e")
    assert len(hyps) == 1
    h = hyps[0]
    assert h.finding_type == FindingType.INFERENCE
    assert h.status == ReviewStatus.UNVERIFIED
    assert "human review" in h.description.lower()
    assert person.finding_id in h.description and knife.finding_id in h.description


def test_weapon_far_from_person():
    person = _obs("person", [0, 0, 50, 100])
    knife = _obs("knife", [800, 800, 850, 860])
    hyps = generate_hypotheses([person, knife], "c", "e")
    assert hyps[0].label == "hypothesis:weapon_like_object_alone"


def test_no_detections_note():
    hyps = generate_hypotheses([], "c", "e")
    assert hyps[0].label == "hypothesis:no_detections"


def test_analyze_endpoint_with_mocked_models(monkeypatch):
    def fake_analyze(ev):
        det = Finding(case_id=ev.case_id, evidence_id=ev.evidence_id,
                      finding_type=FindingType.OBSERVATION, label="person",
                      confidence=0.88, bbox=[1, 1, 10, 10], model_name="fake")
        hyp = Finding(case_id=ev.case_id, evidence_id=ev.evidence_id,
                      finding_type=FindingType.INFERENCE, label="hypothesis:test",
                      description="Human review required.", model_name="fake")
        return [det, hyp]

    monkeypatch.setattr("app.api.images.analyze_image", fake_analyze)

    with TestClient(app) as client:
        cid = client.post("/cases", data={"title": "img test"}).json()["case_id"]
        ev = client.post(f"/cases/{cid}/evidence",
                         files={"file": ("a.png", io.BytesIO(b"\x89PNG fake"), "image/png")}).json()
        r = client.post(f"/evidence/{ev['evidence_id']}/analyze-image")
        assert r.status_code == 200
        body = r.json()
        assert len(body["observations"]) == 1 and len(body["inferences"]) == 1
        assert "do not establish guilt" in body["disclaimer"]

        listed = client.get(f"/cases/{cid}/findings", params={"finding_type": "inference"}).json()
        assert listed["count"] == 1
        actions = [a["action"] for a in client.get(f"/cases/{cid}/audit").json()]
        assert "analyze_image" in actions
