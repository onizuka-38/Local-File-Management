from pathlib import Path

from local_file_management.indexer.sqlite_indexer import get_connection, search
from local_file_management.pipeline import index_local_path


def test_index_and_search(tmp_path: Path) -> None:
    doc = tmp_path / "sample.txt"
    doc.write_text("hello local file management search", encoding="utf-8")

    db_path = tmp_path / "index.db"
    conn = get_connection(db_path)
    try:
        indexed = index_local_path(conn, tmp_path)
        assert indexed == 1

        results = search(conn, "local", limit=10)
        assert len(results) == 1
        assert "sample.txt" in results[0].path
    finally:
        conn.close()
