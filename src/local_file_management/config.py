from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    db_path: Path = Path("data/index.db")
    scan_path: Path = Path(".")


settings = Settings()
