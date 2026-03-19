import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from local_file_management.collector.file_collector import collect_file_paths
from local_file_management.collector.web_collector import collect_web_text
from local_file_management.config import settings
from local_file_management.indexer.sqlite_indexer import (
    initialize_db,
    remove_missing_local_documents,
    upsert_document,
)
from local_file_management.parser.text_parser import clean_text, parse_text


def index_local_path(conn: sqlite3.Connection, root: Path) -> int:
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Invalid directory path: {root}")

    initialize_db(conn)
    indexed = 0
    existing_paths: set[str] = set()

    try:
        for path in collect_file_paths(
            root,
            max_file_size_mb=settings.max_file_size_mb,
            exclude_hidden=settings.exclude_hidden,
        ):
            resolved_path = str(path.resolve())
            existing_paths.add(resolved_path)

            content = clean_text(parse_text(path))
            if not content:
                continue
            upsert_document(conn, resolved_path, content)
            indexed += 1

        remove_missing_local_documents(conn, existing_paths)
        conn.commit()
    except Exception:
        conn.rollback()
        raise

    return indexed


def index_web_url(conn: sqlite3.Connection, url: str) -> int:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")

    if settings.web_allowed_domains and parsed.netloc.lower() not in settings.web_allowed_domains:
        raise ValueError(f"Domain not allowed: {parsed.netloc}")

    initialize_db(conn)

    try:
        content = clean_text(
            collect_web_text(
                url,
                timeout=settings.web_timeout_sec,
                max_retries=settings.web_max_retries,
            )
        )
        if not content:
            return 0
        upsert_document(conn, url, content)
        conn.commit()
    except Exception:
        conn.rollback()
        raise

    return 1
