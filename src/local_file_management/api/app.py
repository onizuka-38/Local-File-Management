import sqlite3
import threading
import time
from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from local_file_management.config import settings
from local_file_management.indexer.sqlite_indexer import get_connection, search
from local_file_management.pipeline import index_local_path, index_web_url

app = FastAPI(title="Local File Management API")


class IndexRequest(BaseModel):
    path: str


class WebIndexRequest(BaseModel):
    url: str


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=20, ge=1, le=100)


_metrics_lock = threading.Lock()
_metrics = {
    "index_requests": 0,
    "index_failures": 0,
    "index_web_requests": 0,
    "index_web_failures": 0,
    "search_requests": 0,
    "search_failures": 0,
    "index_total_ms": 0.0,
    "index_web_total_ms": 0.0,
    "search_total_ms": 0.0,
}


def reset_metrics() -> None:
    with _metrics_lock:
        for key in _metrics:
            _metrics[key] = 0 if key.endswith("requests") or key.endswith("failures") else 0.0


def _inc(name: str, value: int = 1) -> None:
    with _metrics_lock:
        _metrics[name] += value


def _add_ms(name: str, elapsed_ms: float) -> None:
    with _metrics_lock:
        _metrics[name] += elapsed_ms


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> dict[str, float | int]:
    with _metrics_lock:
        index_avg = _metrics["index_total_ms"] / _metrics["index_requests"] if _metrics["index_requests"] else 0.0
        web_avg = _metrics["index_web_total_ms"] / _metrics["index_web_requests"] if _metrics["index_web_requests"] else 0.0
        search_avg = _metrics["search_total_ms"] / _metrics["search_requests"] if _metrics["search_requests"] else 0.0

        return {
            "index_requests": _metrics["index_requests"],
            "index_failures": _metrics["index_failures"],
            "index_avg_ms": round(index_avg, 3),
            "index_web_requests": _metrics["index_web_requests"],
            "index_web_failures": _metrics["index_web_failures"],
            "index_web_avg_ms": round(web_avg, 3),
            "search_requests": _metrics["search_requests"],
            "search_failures": _metrics["search_failures"],
            "search_avg_ms": round(search_avg, 3),
        }


@app.post("/index")
def index_docs(req: IndexRequest) -> dict[str, int]:
    _inc("index_requests")
    start = time.perf_counter()

    conn = get_connection(settings.db_path)
    try:
        count = index_local_path(conn, Path(req.path))
    except ValueError as exc:
        _inc("index_failures")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        conn.close()
        _add_ms("index_total_ms", (time.perf_counter() - start) * 1000)

    return {"indexed": count}


@app.post("/index/web")
def index_web(req: WebIndexRequest) -> dict[str, int]:
    _inc("index_web_requests")
    start = time.perf_counter()

    conn = get_connection(settings.db_path)
    try:
        count = index_web_url(conn, req.url)
    except ValueError as exc:
        _inc("index_web_failures")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except requests.RequestException as exc:
        _inc("index_web_failures")
        raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {exc}") from exc
    finally:
        conn.close()
        _add_ms("index_web_total_ms", (time.perf_counter() - start) * 1000)

    return {"indexed": count}


@app.post("/search")
def search_docs(req: SearchRequest) -> list[dict[str, object]]:
    _inc("search_requests")
    start = time.perf_counter()

    conn = get_connection(settings.db_path)
    try:
        results = search(conn, req.query, req.limit)
    except sqlite3.OperationalError as exc:
        _inc("search_failures")
        raise HTTPException(status_code=400, detail=f"Invalid search query: {exc}") from exc
    finally:
        conn.close()
        _add_ms("search_total_ms", (time.perf_counter() - start) * 1000)

    return [{"path": r.path, "rank": r.rank, "content": r.content[:300]} for r in results]
