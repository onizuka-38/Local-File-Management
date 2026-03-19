import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    db_path: Path
    scan_path: Path
    max_file_size_mb: int
    exclude_hidden: bool


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


settings = Settings(
    db_path=Path(os.getenv("LFM_DB_PATH", "data/index.db")),
    scan_path=Path(os.getenv("LFM_SCAN_PATH", ".")),
    max_file_size_mb=int(os.getenv("LFM_MAX_FILE_SIZE_MB", "20")),
    exclude_hidden=_env_bool("LFM_EXCLUDE_HIDDEN", True),
)
