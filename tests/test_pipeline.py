import sqlite3
from pathlib import Path

import pytest

from local_file_management.config import Settings
from local_file_management.indexer.sqlite_indexer import get_connection, search
from local_file_management.pipeline import index_local_path, index_web_url


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
        assert str(doc.resolve()) == results[0].path
    finally:
        conn.close()


def test_reindex_removes_deleted_local_files(tmp_path: Path) -> None:
    doc = tmp_path / "to-delete.txt"
    doc.write_text("temporary content", encoding="utf-8")

    db_path = tmp_path / "index.db"
    conn = get_connection(db_path)
    try:
        first = index_local_path(conn, tmp_path)
        assert first == 1
        assert len(search(conn, "temporary", limit=10)) == 1

        doc.unlink()
        second = index_local_path(conn, tmp_path)
        assert second == 0
        assert len(search(conn, "temporary", limit=10)) == 0
    finally:
        conn.close()


def test_hidden_file_is_skipped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hidden = tmp_path / ".hidden.txt"
    hidden.write_text("hidden content", encoding="utf-8")

    custom_settings = Settings(
        db_path=Path("data/index.db"),
        scan_path=Path("."),
        max_file_size_mb=20,
        exclude_hidden=True,
    )
    monkeypatch.setattr("local_file_management.pipeline.settings", custom_settings)

    db_path = tmp_path / "index.db"
    conn = get_connection(db_path)
    try:
        indexed = index_local_path(conn, tmp_path)
        assert indexed == 0
        assert len(search(conn, "hidden", limit=10)) == 0
    finally:
        conn.close()


def test_large_file_is_skipped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    big = tmp_path / "big.txt"
    big.write_text("a" * 2048, encoding="utf-8")

    custom_settings = Settings(
        db_path=Path("data/index.db"),
        scan_path=Path("."),
        max_file_size_mb=0,
        exclude_hidden=True,
    )
    monkeypatch.setattr("local_file_management.pipeline.settings", custom_settings)

    db_path = tmp_path / "index.db"
    conn = get_connection(db_path)
    try:
        indexed = index_local_path(conn, tmp_path)
        assert indexed == 0
    finally:
        conn.close()


def test_index_web_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "index.db"
    conn = get_connection(db_path)

    monkeypatch.setattr(
        "local_file_management.pipeline.collect_web_text",
        lambda _url: "web article content for testing",
    )

    try:
        indexed = index_web_url(conn, "https://example.com/docs")
        assert indexed == 1

        results = search(conn, "article", limit=10)
        assert len(results) == 1
        assert results[0].path == "https://example.com/docs"
    finally:
        conn.close()


def test_index_local_invalid_path(tmp_path: Path) -> None:
    db_path = tmp_path / "index.db"
    conn = get_connection(db_path)
    try:
        with pytest.raises(ValueError):
            index_local_path(conn, tmp_path / "not-exists")
    finally:
        conn.close()


def test_index_web_invalid_url(tmp_path: Path) -> None:
    db_path = tmp_path / "index.db"
    conn = get_connection(db_path)
    try:
        with pytest.raises(ValueError):
            index_web_url(conn, "not-a-url")
    finally:
        conn.close()


def test_search_invalid_fts_query(tmp_path: Path) -> None:
    db_path = tmp_path / "index.db"
    conn = get_connection(db_path)
    try:
        indexed = index_local_path(conn, tmp_path)
        assert indexed == 0

        with pytest.raises(sqlite3.OperationalError):
            search(conn, '"', limit=10)
    finally:
        conn.close()
