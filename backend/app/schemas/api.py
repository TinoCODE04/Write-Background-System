from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    name: str | None = Field(default=None, max_length=160)


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: str
    total_images: int
    queued_images: int
    processing_images: int
    completed_images: int
    review_images: int
    failed_images: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None


class ImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    original_filename: str
    width: int
    height: int
    file_size: int
    mime_type: str
    status: str
    quality_score: float | None
    quality_flags: list[str]
    processing_time_ms: int | None
    model_name: str | None
    model_version: str | None
    processing_settings: dict[str, Any]
    error_message: str | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UploadResponse(BaseModel):
    uploaded: list[ImageRead]
    errors: list[dict[str, str]]


class ProcessingSettings(BaseModel):
    edge_cleanup: float = Field(default=0.55, ge=0, le=1)
    feather: float = Field(default=0.8, ge=0, le=5)
    remove_halo: bool = True
    remove_small_islands: bool = True
    fill_holes: bool = True
    mask_smoothness: float = Field(default=0.35, ge=0, le=1)
    keep_natural_shadow: bool = True
    erosion: int = Field(default=0, ge=0, le=5)
    dilation: int = Field(default=0, ge=0, le=5)
    min_component_area: int = Field(default=24, ge=0, le=10000)
    max_hole_area: int = Field(default=64, ge=0, le=10000)
    background_color: str = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")


class DownloadRequest(BaseModel):
    format: Literal["transparent", "white_png", "white_jpg", "all"] = "all"


class SystemInfo(BaseModel):
    model_name: str
    model_version: str
    device: str
    database: str
    storage_location: str
    quality_threshold: int
    max_upload_mb: int

