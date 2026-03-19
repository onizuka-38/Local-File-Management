import sqlite3
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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/index")
def index_docs(req: IndexRequest) -> dict[str, int]:
    conn = get_connection(settings.db_path)
    try:
        count = index_local_path(conn, Path(req.path))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        conn.close()
    return {"indexed": count}


@app.post("/index/web")
def index_web(req: WebIndexRequest) -> dict[str, int]:
    conn = get_connection(settings.db_path)
    try:
        count = index_web_url(conn, req.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {exc}") from exc
    finally:
        conn.close()
    return {"indexed": count}


@app.post("/search")
def search_docs(req: SearchRequest) -> list[dict[str, object]]:
    conn = get_connection(settings.db_path)
    try:
        results = search(conn, req.query, req.limit)
    except sqlite3.OperationalError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid search query: {exc}") from exc
    finally:
        conn.close()
    return [{"path": r.path, "rank": r.rank, "content": r.content[:300]} for r in results]
