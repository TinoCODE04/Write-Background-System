from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def _load_dotenv(path: Path) -> None:
    """Load a small .env file without making app startup depend on python-dotenv."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Settings:
    repository_root: Path
    database_url: str
    storage_path: Path
    model_name: str
    device: str
    max_upload_mb: int
    quality_pass_threshold: int
    worker_poll_interval: float
    stale_processing_minutes: int
    model_input_size: int
    frontend_url: str


@lru_cache
def get_settings() -> Settings:
    _load_dotenv(REPOSITORY_ROOT / ".env")
    database_url = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
    storage_value = Path(os.getenv("STORAGE_PATH", "./storage"))
    storage_path = storage_value if storage_value.is_absolute() else REPOSITORY_ROOT / storage_value
    return Settings(
        repository_root=REPOSITORY_ROOT,
        database_url=database_url,
        storage_path=storage_path.resolve(),
        model_name=os.getenv("MODEL_NAME", "ZhengPeng7/BiRefNet"),
        device=os.getenv("DEVICE", "auto").lower(),
        max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", "50")),
        quality_pass_threshold=int(os.getenv("QUALITY_PASS_THRESHOLD", "85")),
        worker_poll_interval=float(os.getenv("WORKER_POLL_INTERVAL", "1")),
        stale_processing_minutes=int(os.getenv("STALE_PROCESSING_MINUTES", "30")),
        model_input_size=int(os.getenv("MODEL_INPUT_SIZE", "1024") or "1024"),
        frontend_url=os.getenv("FRONTEND_URL", "http://localhost:3000"),
    )

