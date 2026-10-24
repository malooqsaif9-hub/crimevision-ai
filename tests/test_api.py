import io
from fastapi.testclient import TestClient
from app.main import app


def test_full_flow():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"

        case = client.post("/cases", data={"title": "Test case"}).json()
        cid = case["case_id"]

        fake_png = io.BytesIO(b"\x89PNG\r\n\x1a\n fake image bytes")
        r = client.post(f"/cases/{cid}/evidence",
                        files={"file": ("scene.png", fake_png, "image/png")})
        assert r.status_code == 200
        ev = r.json()
        assert ev["media_type"] == "image" and len(ev["sha256"]) == 64

        assert client.get(f"/evidence/{ev['evidence_id']}/verify").json()["intact"] is True

        bad = client.post(f"/cases/{cid}/evidence",
                          files={"file": ("virus.exe", io.BytesIO(b"x"), "application/octet-stream")})
        assert bad.status_code == 400

        actions = [a["action"] for a in client.get(f"/cases/{cid}/audit").json()]
        assert "create_case" in actions and "upload" in actions


def test_blank_title_is_rejected():
    with TestClient(app) as client:
        response = client.post("/cases", data={"title": "   "})
        assert response.status_code == 400
        assert "title" in response.json()["detail"].lower()