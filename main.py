from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from local_file_management.indexer.sqlite_indexer import get_connection, search
from local_file_management.pipeline import index_local_path, index_web_url


def cmd_index(args: argparse.Namespace) -> int:
    conn = get_connection(Path(args.db))
    try:
        indexed = index_local_path(conn, Path(args.path))
    finally:
        conn.close()
    print(f"Indexed documents: {indexed}")
    return 0


def cmd_index_web(args: argparse.Namespace) -> int:
    conn = get_connection(Path(args.db))
    try:
        indexed = index_web_url(conn, args.url)
    finally:
        conn.close()
    print(f"Indexed web documents: {indexed}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    conn = get_connection(Path(args.db))
    try:
        results = search(conn, args.query, args.limit)
    finally:
        conn.close()

    for row in results:
        print(f"[{row.rank:.4f}] {row.path}")
        print(f"  {row.content[:180]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local file management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index", help="Index local files into SQLite FTS5")
    index_parser.add_argument("path", help="Path to scan")
    index_parser.add_argument("--db", default="data/index.db", help="SQLite DB path")
    index_parser.set_defaults(func=cmd_index)

    index_web_parser = subparsers.add_parser("index-web", help="Index a web page URL")
    index_web_parser.add_argument("url", help="Web page URL")
    index_web_parser.add_argument("--db", default="data/index.db", help="SQLite DB path")
    index_web_parser.set_defaults(func=cmd_index_web)

    search_parser = subparsers.add_parser("search", help="Search indexed documents")
    search_parser.add_argument("query", help="FTS query")
    search_parser.add_argument("--db", default="data/index.db", help="SQLite DB path")
    search_parser.add_argument("--limit", type=int, default=20, help="Result limit")
    search_parser.set_defaults(func=cmd_search)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
