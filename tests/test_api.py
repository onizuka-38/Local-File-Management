import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

pytest.importorskip("fastapi")
pytest.importorskip("requests")
from fastapi.testclient import TestClient  # noqa: E402

from local_file_management import pipeline as pipeline_module  # noqa: E402
from local_file_management.api import app as api_module  # noqa: E402
from local_file_management.config import Settings  # noqa: E402


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "api.db"
    cfg = Settings(
        db_path=db_path,
        scan_path=tmp_path,
        max_file_size_mb=20,
        exclude_hidden=True,
        web_timeout_sec=1,
        web_max_retries=0,
        web_allowed_domains=(),
    )
    monkeypatch.setattr(api_module, "settings", cfg)
    monkeypatch.setattr(pipeline_module, "settings", cfg)
    api_module.reset_metrics()
    return TestClient(api_module.app)


def test_health(client: TestClient) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_index_and_search_roundtrip(client: TestClient, tmp_path: Path) -> None:
    doc = tmp_path / "api-sample.txt"
    doc.write_text("api test keyword", encoding="utf-8")

    idx = client.post("/index", json={"path": str(tmp_path)})
    assert idx.status_code == 200
    assert idx.json()["indexed"] >= 1

    res = client.post("/search", json={"query": "keyword", "limit": 20})
    assert res.status_code == 200
    rows = res.json()
    assert any("api-sample.txt" in row["path"] for row in rows)


def test_metrics_endpoint(client: TestClient, tmp_path: Path) -> None:
    doc = tmp_path / "metric-sample.txt"
    doc.write_text("metric keyword", encoding="utf-8")

    client.post("/index", json={"path": str(tmp_path)})
    client.post("/search", json={"query": "keyword", "limit": 20})
    client.post("/search", json={"query": '"', "limit": 20})

    m = client.get("/metrics")
    assert m.status_code == 200
    payload = m.json()
    assert payload["index_requests"] == 1
    assert payload["index_failures"] == 0
    assert payload["search_requests"] == 2
    assert payload["search_failures"] == 1
    assert payload["index_avg_ms"] >= 0
    assert payload["search_avg_ms"] >= 0


def test_index_invalid_path(client: TestClient) -> None:
    res = client.post("/index", json={"path": "./path-that-does-not-exist-xyz"})
    assert res.status_code == 400


def test_index_web_invalid_url(client: TestClient) -> None:
    res = client.post("/index/web", json={"url": "invalid-url"})
    assert res.status_code == 400


def test_search_invalid_query(client: TestClient) -> None:
    res = client.post("/search", json={"query": '"', "limit": 20})
    assert res.status_code == 400


def test_search_limit_validation(client: TestClient) -> None:
    res = client.post("/search", json={"query": "local", "limit": 0})
    assert res.status_code == 422
