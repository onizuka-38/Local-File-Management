from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from local_file_management.config import settings
from local_file_management.indexer.sqlite_indexer import get_connection, search
from local_file_management.pipeline import index_local_path

app = FastAPI(title="Local File Management API")


class IndexRequest(BaseModel):
    path: str


class SearchRequest(BaseModel):
    query: str
    limit: int = 20


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/index")
def index_docs(req: IndexRequest) -> dict[str, int]:
    conn = get_connection(settings.db_path)
    try:
        count = index_local_path(conn, Path(req.path))
    finally:
        conn.close()
    return {"indexed": count}


@app.post("/search")
def search_docs(req: SearchRequest) -> list[dict[str, object]]:
    conn = get_connection(settings.db_path)
    try:
        results = search(conn, req.query, req.limit)
    finally:
        conn.close()
    return [{"path": r.path, "rank": r.rank, "content": r.content[:300]} for r in results]
