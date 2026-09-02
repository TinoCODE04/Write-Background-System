from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import ImageAsset, Job


def require_job(db: Session, job_id: str) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


def require_image(db: Session, image_id: str) -> ImageAsset:
    image = db.get(ImageAsset, image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

