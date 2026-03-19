from pathlib import Path

from local_file_management.collector.file_collector import collect_file_paths
from local_file_management.indexer.sqlite_indexer import initialize_db, upsert_document
from local_file_management.parser.text_parser import clean_text, parse_text


def index_local_path(conn, root: Path) -> int:
    initialize_db(conn)
    indexed = 0
    for path in collect_file_paths(root):
        content = clean_text(parse_text(path))
        if not content:
            continue
        upsert_document(conn, str(path), content)
        indexed += 1
    return indexed
