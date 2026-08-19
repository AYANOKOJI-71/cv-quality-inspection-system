from __future__ import annotations

from fastapi.testclient import TestClient
from inspection.main import app


def test_health_reports_local_mode() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["mode"] == "local-first"


def test_upload_rejects_unsupported_file_type() -> None:
    with TestClient(app) as client:
        response = client.post("/v1/inspect", files={"image": ("notes.txt", b"not-image", "text/plain")})

    assert response.status_code == 415
