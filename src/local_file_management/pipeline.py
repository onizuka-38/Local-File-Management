import sqlite3
from pathlib import Path

from local_file_management.collector.file_collector import collect_file_paths
from local_file_management.collector.web_collector import collect_web_text
from local_file_management.indexer.sqlite_indexer import initialize_db, upsert_document
from local_file_management.parser.text_parser import clean_text, parse_text


def index_local_path(conn: sqlite3.Connection, root: Path) -> int:
    initialize_db(conn)
    indexed = 0
    for path in collect_file_paths(root):
        content = clean_text(parse_text(path))
        if not content:
            continue
        upsert_document(conn, str(path.resolve()), content)
        indexed += 1
    conn.commit()
    return indexed


def index_web_url(conn: sqlite3.Connection, url: str) -> int:
    initialize_db(conn)
    content = clean_text(collect_web_text(url))
    if not content:
        return 0
    upsert_document(conn, url, content)
    conn.commit()
    return 1
