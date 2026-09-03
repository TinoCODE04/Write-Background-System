from __future__ import annotations

import re
from pathlib import Path

from app.core.config import get_settings


SUBDIRECTORIES = ("original", "masks", "transparent", "white_png", "white_jpg", "thumbnails")
_INVALID_NAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
_REPEATED_DOTS = re.compile(r"\.{2,}")
_RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def sanitize_stem(filename: str | None, max_length: int = 60, fallback: str = "image") -> str:
    """Keep the original filename readable (CJK included) while staying Windows-safe."""
    stem = Path(filename).stem if filename else ""
    stem = _INVALID_NAME_CHARS.sub("_", stem)
    stem = _REPEATED_DOTS.sub(".", stem).strip(" .")
    stem = stem[:max_length].rstrip(" ._")
    if not stem:
        return fallback
    if stem.upper() in _RESERVED_NAMES:
        return f"_{stem}"
    return stem


class LocalStorage:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or get_settings().storage_path).resolve()
        self.jobs_root = self.root / "jobs"
        self.jobs_root.mkdir(parents=True, exist_ok=True)

    def job_directory(self, dirname: str) -> Path:
        # Accepts legacy UUID folders and new "{name}--{id}" folders; anything with
        # separators, control characters, or leading/trailing dots/spaces is rejected.
        if (
            not dirname
            or len(dirname) > 120
            or _INVALID_NAME_CHARS.search(dirname)
            or dirname != dirname.strip(" .")
        ):
            raise ValueError("Invalid job directory name")
        path = (self.jobs_root / dirname).resolve()
        if self.jobs_root not in path.parents:
            raise ValueError("Unsafe storage path")
        return path

    def ensure_job(self, dirname: str) -> Path:
        root = self.job_directory(dirname)
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
