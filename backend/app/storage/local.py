from __future__ import annotations

import re
from pathlib import Path

from app.core.config import get_settings


SUBDIRECTORIES = ("original", "masks", "transparent", "white_png", "white_jpg", "thumbnails")
SAFE_ID = re.compile(r"^[0-9a-fA-F-]{36}$")


class LocalStorage:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or get_settings().storage_path).resolve()
        self.jobs_root = self.root / "jobs"
        self.jobs_root.mkdir(parents=True, exist_ok=True)

    def job_directory(self, job_id: str) -> Path:
        if not SAFE_ID.fullmatch(job_id):
            raise ValueError("Invalid job identifier")
        path = (self.jobs_root / job_id).resolve()
        if self.jobs_root not in path.parents:
            raise ValueError("Unsafe storage path")
        return path

    def ensure_job(self, job_id: str) -> Path:
        root = self.job_directory(job_id)
        for directory in SUBDIRECTORIES:
            (root / directory).mkdir(parents=True, exist_ok=True)
        return root

    def relative(self, path: Path) -> str:
        resolved = path.resolve()
        if self.root != resolved and self.root not in resolved.parents:
            raise ValueError("Path is outside storage root")
        return resolved.relative_to(self.root).as_posix()

    def resolve(self, relative_path: str) -> Path:
        path = (self.root / relative_path).resolve()
        if self.root != path and self.root not in path.parents:
            raise ValueError("Unsafe storage path")
        return path

