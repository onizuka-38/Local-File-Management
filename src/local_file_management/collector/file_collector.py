from pathlib import Path

SUPPORTED_SUFFIXES = {".txt", ".md", ".pdf"}


def _is_hidden(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def collect_file_paths(root: Path, max_file_size_mb: int = 20, exclude_hidden: bool = True):
    max_size_bytes = max_file_size_mb * 1024 * 1024

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        if exclude_hidden and _is_hidden(path):
            continue
        if path.stat().st_size > max_size_bytes:
            continue
        yield path
