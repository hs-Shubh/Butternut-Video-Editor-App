from fastapi.testclient import TestClient
from app.main import app


def test_upload_enqueues_job(monkeypatch, tmp_path):
    called = {"args": None}

    class DummyQueue:
        def enqueue(self, *args, **kwargs):
            called["args"] = args

    monkeypatch.setattr("app.main.queue", DummyQueue())

    video = tmp_path / "input.mp4"
    video.write_bytes(b"0000")

    meta = {
        "title": "Test",
        "overlays": [],
        "output_format": "mp4",
        "resolution": {"width": 1280, "height": 720},
    }

    client = TestClient(app)
    files = {
        "file": ("input.mp4", video.read_bytes(), "video/mp4"),
        "metadata": (None, json_dumps(meta), "application/json"),
    }
    r = client.post("/upload", files=files)
    assert r.status_code == 200
    jid = r.json()["job_id"]
    assert isinstance(jid, str) and len(jid) > 0
    assert called["args"] is not None


def json_dumps(obj):
    import json

    return json.dumps(obj)
