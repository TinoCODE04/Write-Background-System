from __future__ import annotations

import io
import uuid
import zipfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_job
from app.db import get_db
from app.models import ImageAsset, ImageStatus, Job
from app.schemas.api import DownloadRequest, ImageRead, JobCreate, JobRead, UploadResponse
from app.services.jobs import refresh_job_counters
from app.services.uploads import UploadValidationError, store_upload
from app.storage.local import LocalStorage


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobRead, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)) -> Job:
    default_name = f"Batch {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    job = Job(id=str(uuid.uuid4()), name=(payload.name or default_name).strip() or default_name)
    db.add(job)
    db.commit()
    db.refresh(job)
    # The storage folder is created lazily on first upload so it can be named
    # after the original filename instead of the bare job UUID.
    return job


@router.get("", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[Job]:
    return list(db.scalars(select(Job).order_by(Job.created_at.desc()).limit(100)).all())


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: str, db: Session = Depends(get_db)) -> Job:
    job = require_job(db, job_id)
    refresh_job_counters(db, job.id)
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/images", response_model=UploadResponse, status_code=201)
async def upload_images(
    job_id: str,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> UploadResponse:
    job = require_job(db, job_id)
    if not files:
        raise HTTPException(status_code=400, detail="No files supplied")
    storage = LocalStorage()
    uploaded: list[ImageAsset] = []
    errors: list[dict[str, str]] = []
    for upload in files:
        try:
            with db.begin_nested():
                asset = await store_upload(db, job, upload, storage)
                db.flush()
            uploaded.append(asset)
        except UploadValidationError as exc:
            errors.append({"filename": Path(upload.filename or "unknown").name, "error": str(exc)})
        except Exception:
            errors.append({"filename": Path(upload.filename or "unknown").name, "error": "Upload could not be saved"})
    refresh_job_counters(db, job.id)
    db.commit()
    for asset in uploaded:
        db.refresh(asset)
    if not uploaded and errors:
        raise HTTPException(status_code=422, detail=errors)
    return UploadResponse(uploaded=[ImageRead.model_validate(item) for item in uploaded], errors=errors)


@router.post("/{job_id}/process", response_model=JobRead)
def queue_job(job_id: str, db: Session = Depends(get_db)) -> Job:
    job = require_job(db, job_id)
    assets = db.scalars(
        select(ImageAsset).where(ImageAsset.job_id == job.id, ImageAsset.status == ImageStatus.UPLOADED.value)
    ).all()
    for asset in assets:
        asset.status = ImageStatus.QUEUED.value
        asset.error_message = None
    refresh_job_counters(db, job.id)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}/images", response_model=list[ImageRead])
def list_images(job_id: str, db: Session = Depends(get_db)) -> list[ImageAsset]:
    require_job(db, job_id)
    return list(db.scalars(select(ImageAsset).where(ImageAsset.job_id == job_id).order_by(ImageAsset.created_at)).all())


@router.post("/{job_id}/download")
def download_job(job_id: str, payload: DownloadRequest, db: Session = Depends(get_db)) -> StreamingResponse:
    job = require_job(db, job_id)
    images = db.scalars(select(ImageAsset).where(ImageAsset.job_id == job.id)).all()
    field_map = {
        "transparent": [("transparent_path", "transparent")],
        "white_png": [("white_png_path", "white-png")],
        "white_jpg": [("white_jpg_path", "white-jpg")],
        "all": [
            ("transparent_path", "transparent"),
            ("white_png_path", "white-png"),
            ("white_jpg_path", "white-jpg"),
        ],
    }
    storage = LocalStorage()
    archive = io.BytesIO()
    added = 0
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for asset in images:
            safe_stem = Path(asset.original_filename).stem[:100] or asset.id
            for field, folder in field_map[payload.format]:
                relative = getattr(asset, field)
                if not relative:
                    continue
                source = storage.resolve(relative)
                if source.exists():
                    bundle.write(source, f"{folder}/{safe_stem}-{asset.id[:8]}{source.suffix}")
                    added += 1
    if not added:
        raise HTTPException(status_code=409, detail="No processed outputs are available")
    archive.seek(0)
    filename = f"{job.name.replace(' ', '-')[:80]}-{payload.format}.zip"
    return StreamingResponse(
        archive,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
