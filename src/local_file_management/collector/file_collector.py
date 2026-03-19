from pathlib import Path

SUPPORTED_SUFFIXES = {".txt", ".md", ".pdf"}


def collect_file_paths(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            yield path
