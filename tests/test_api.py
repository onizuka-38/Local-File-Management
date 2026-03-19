import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

pytest.importorskip("fastapi")
pytest.importorskip("requests")
from fastapi.testclient import TestClient  # noqa: E402

from local_file_management.api.app import app  # noqa: E402


client = TestClient(app)


def test_health() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_index_invalid_path() -> None:
    res = client.post("/index", json={"path": "./path-that-does-not-exist-xyz"})
    assert res.status_code == 400


def test_index_web_invalid_url() -> None:
    res = client.post("/index/web", json={"url": "invalid-url"})
    assert res.status_code == 400


def test_search_invalid_query() -> None:
    res = client.post("/search", json={"query": '"', "limit": 20})
    assert res.status_code == 400


def test_search_limit_validation() -> None:
    res = client.post("/search", json={"query": "local", "limit": 0})
    assert res.status_code == 422
