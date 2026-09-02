from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.api import SystemInfo


router = APIRouter(prefix="/system", tags=["system"])


def detect_device() -> str:
    settings = get_settings()
    if settings.device == "cpu":
        return "CPU"
    try:
        import torch

        return "CUDA" if torch.cuda.is_available() else "CPU"
    except ImportError:
        return "CPU (PyTorch not installed)"


@router.get("", response_model=SystemInfo)
def system_info() -> SystemInfo:
    settings = get_settings()
    return SystemInfo(
        model_name=settings.model_name,
        model_version="Resolved when worker loads model",
        device=detect_device(),
        database="SQLite",
        storage_location=str(settings.storage_path),
        quality_threshold=settings.quality_pass_threshold,
        max_upload_mb=settings.max_upload_mb,
    )

