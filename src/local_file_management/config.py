import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    db_path: Path
    scan_path: Path
    max_file_size_mb: int
    exclude_hidden: bool
    web_timeout_sec: int
    web_max_retries: int
    web_allowed_domains: tuple[str, ...]


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_csv(name: str) -> tuple[str, ...]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return ()
    return tuple(part.strip().lower() for part in raw.split(",") if part.strip())


settings = Settings(
    db_path=Path(os.getenv("LFM_DB_PATH", "data/index.db")),
    scan_path=Path(os.getenv("LFM_SCAN_PATH", ".")),
    max_file_size_mb=int(os.getenv("LFM_MAX_FILE_SIZE_MB", "20")),
    exclude_hidden=_env_bool("LFM_EXCLUDE_HIDDEN", True),
    web_timeout_sec=int(os.getenv("LFM_WEB_TIMEOUT_SEC", "10")),
    web_max_retries=int(os.getenv("LFM_WEB_MAX_RETRIES", "2")),
    web_allowed_domains=_env_csv("LFM_WEB_ALLOWED_DOMAINS"),
)
