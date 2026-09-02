from __future__ import annotations

import hashlib
import io
import uuid
from pathlib import Path

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import ImageAsset, ImageStatus, Job
from app.schemas.api import ProcessingSettings
from app.storage.local import LocalStorage


FORMAT_MIME = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


class UploadValidationError(ValueError):
    pass


async def store_upload(db: Session, job: Job, upload: UploadFile, storage: LocalStorage) -> ImageAsset:
    settings = get_settings()
    payload = await upload.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if not payload:
        raise UploadValidationError("File is empty")
    if len(payload) > settings.max_upload_mb * 1024 * 1024:
        raise UploadValidationError(f"File exceeds {settings.max_upload_mb} MB")

    try:
        with Image.open(io.BytesIO(payload)) as probe:
            image_format = probe.format
            probe.verify()
        if image_format not in FORMAT_MIME:
            raise UploadValidationError("Only JPG, PNG, and WEBP images are supported")
        with Image.open(io.BytesIO(payload)) as source:
            normalized = ImageOps.exif_transpose(source)
            width, height = normalized.size
            normalized.load()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        if isinstance(exc, UploadValidationError):
            raise
        raise UploadValidationError("The file is corrupt or is not a valid image") from exc

    digest = hashlib.sha256(payload).hexdigest()
    duplicate = db.scalar(
        select(ImageAsset).where(
            ImageAsset.job_id == job.id,
            ImageAsset.processing_settings["source_sha256"].as_string() == digest,
        )
    )
    if duplicate:
        raise UploadValidationError("Duplicate file in this batch")

    image_id = str(uuid.uuid4())
    extension = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}[image_format]
    stored_filename = f"{image_id}{extension}"
    root = storage.ensure_job(job.id)
    target = root / "original" / stored_filename
    target.write_bytes(payload)
    relative = storage.relative(target)
    processing_settings = ProcessingSettings().model_dump()
    processing_settings["source_sha256"] = digest
    asset = ImageAsset(
        id=image_id,
        job_id=job.id,
        original_filename=Path(upload.filename or "image").name[:512],
        stored_filename=stored_filename,
        original_path=relative,
        width=width,
        height=height,
        file_size=len(payload),
        mime_type=FORMAT_MIME[image_format],
        status=ImageStatus.UPLOADED.value,
        processing_settings=processing_settings,
    )
    db.add(asset)
    return asset

