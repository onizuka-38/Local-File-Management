import sqlite3
from pathlib import Path

from local_file_management.indexer.models import SearchResult


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts
        USING fts5(path, content, content='documents', content_rowid='id')
        """
    )
    conn.execute(
        """
        CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
            INSERT INTO documents_fts(rowid, path, content)
            VALUES (new.id, new.path, new.content);
        END
        """
    )
    conn.execute(
        """
        CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
            INSERT INTO documents_fts(documents_fts, rowid, path, content)
            VALUES('delete', old.id, old.path, old.content);
        END
        """
    )
    conn.execute(
        """
        CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
            INSERT INTO documents_fts(documents_fts, rowid, path, content)
            VALUES('delete', old.id, old.path, old.content);
            INSERT INTO documents_fts(rowid, path, content)
            VALUES (new.id, new.path, new.content);
        END
        """
    )
    conn.commit()


def upsert_document(conn: sqlite3.Connection, path: str, content: str) -> None:
    conn.execute(
        """
        INSERT INTO documents(path, content) VALUES(?, ?)
        ON CONFLICT(path) DO UPDATE SET
            content = excluded.content,
            updated_at = CURRENT_TIMESTAMP
        """,
        (path, content),
    )


def remove_missing_local_documents(conn: sqlite3.Connection, existing_paths: set[str]) -> int:
    rows = conn.execute(
        """
        SELECT path FROM documents
        WHERE path NOT LIKE 'http://%'
          AND path NOT LIKE 'https://%'
        """
    ).fetchall()
    stale_paths = [row["path"] for row in rows if row["path"] not in existing_paths]
    for stale_path in stale_paths:
        conn.execute("DELETE FROM documents WHERE path = ?", (stale_path,))
    return len(stale_paths)


def search(conn: sqlite3.Connection, query: str, limit: int = 20) -> list[SearchResult]:
    initialize_db(conn)
    rows = conn.execute(
        """
        SELECT path, content, bm25(documents_fts) AS rank
        FROM documents_fts
        WHERE documents_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """,
        (query, limit),
    ).fetchall()
    return [SearchResult(path=row["path"], content=row["content"], rank=row["rank"]) for row in rows]
