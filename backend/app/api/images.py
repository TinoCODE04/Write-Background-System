from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import require_image
from app.db import get_db
from app.models import ImageAsset, ImageStatus
from app.schemas.api import ImageRead, ProcessingSettings
from app.services.jobs import refresh_job_counters
from app.storage.local import LocalStorage


router = APIRouter(prefix="/images", tags=["images"])


@router.get("/{image_id}", response_model=ImageRead)
def get_image(image_id: str, db: Session = Depends(get_db)) -> ImageAsset:
    return require_image(db, image_id)


@router.patch("/{image_id}/settings", response_model=ImageRead)
def update_settings(image_id: str, payload: ProcessingSettings, db: Session = Depends(get_db)) -> ImageAsset:
    image = require_image(db, image_id)
    source_hash = image.processing_settings.get("source_sha256")
    image.processing_settings = payload.model_dump()
    if source_hash:
        image.processing_settings["source_sha256"] = source_hash
    db.commit()
    db.refresh(image)
    return image


@router.post("/{image_id}/reprocess", response_model=ImageRead)
def reprocess(image_id: str, db: Session = Depends(get_db)) -> ImageAsset:
    image = require_image(db, image_id)
    if image.status == ImageStatus.PROCESSING.value:
        raise HTTPException(status_code=409, detail="Image is currently processing")
    image.status = ImageStatus.QUEUED.value
    image.error_message = None
    image.approved_at = None
    refresh_job_counters(db, image.job_id)
    db.commit()
    db.refresh(image)
    return image


@router.post("/{image_id}/approve", response_model=ImageRead)
def approve(image_id: str, db: Session = Depends(get_db)) -> ImageAsset:
    image = require_image(db, image_id)
    if image.status != ImageStatus.NEEDS_REVIEW.value:
        raise HTTPException(status_code=409, detail="Only images needing review can be approved")
    image.status = ImageStatus.COMPLETED.value
    image.approved_at = datetime.now(UTC).replace(tzinfo=None)
    refresh_job_counters(db, image.job_id)
    db.commit()
    db.refresh(image)
    return image


def _file_response(image: ImageAsset, field: str, media_type: str, download: bool = False) -> FileResponse:
    relative = getattr(image, field)
    if not relative:
        raise HTTPException(status_code=404, detail="Output is not available")
    try:
        path = LocalStorage().resolve(relative)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid stored path") from exc
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Output file is missing")
    filename = None
    if download:
        stem = image.original_filename.rsplit(".", 1)[0]
        filename = f"{stem}{path.suffix}"
    return FileResponse(path, media_type=media_type, filename=filename)


@router.get("/{image_id}/original")
def original(image_id: str, db: Session = Depends(get_db)) -> FileResponse:
    image = require_image(db, image_id)
    return _file_response(image, "original_path", image.mime_type)


@router.get("/{image_id}/transparent")
def transparent(image_id: str, download: bool = False, db: Session = Depends(get_db)) -> FileResponse:
    return _file_response(require_image(db, image_id), "transparent_path", "image/png", download)


@router.get("/{image_id}/white.png")
def white_png(image_id: str, download: bool = False, db: Session = Depends(get_db)) -> FileResponse:
    return _file_response(require_image(db, image_id), "white_png_path", "image/png", download)


@router.get("/{image_id}/white.jpg")
def white_jpg(image_id: str, download: bool = False, db: Session = Depends(get_db)) -> FileResponse:
    return _file_response(require_image(db, image_id), "white_jpg_path", "image/jpeg", download)


@router.get("/{image_id}/mask")
def mask(image_id: str, db: Session = Depends(get_db)) -> FileResponse:
    return _file_response(require_image(db, image_id), "mask_path", "image/png")


@router.get("/{image_id}/thumbnail")
def thumbnail(image_id: str, db: Session = Depends(get_db)) -> FileResponse:
    image = require_image(db, image_id)
    field = "thumbnail_path" if image.thumbnail_path else "original_path"
    return _file_response(image, field, "image/jpeg" if image.thumbnail_path else image.mime_type)

