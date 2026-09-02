from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ImageAsset, ImageStatus, Job, JobStatus


def refresh_job_counters(db: Session, job_id: str) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise LookupError("Job not found")
    db.flush()
    statuses = db.scalars(select(ImageAsset.status).where(ImageAsset.job_id == job_id)).all()
    counts = Counter(statuses)
    job.total_images = len(statuses)
    uploaded_images = counts[ImageStatus.UPLOADED.value]
    job.queued_images = counts[ImageStatus.QUEUED.value]
    job.processing_images = counts[ImageStatus.PROCESSING.value]
    job.completed_images = counts[ImageStatus.COMPLETED.value]
    job.review_images = counts[ImageStatus.NEEDS_REVIEW.value]
    job.failed_images = counts[ImageStatus.FAILED.value]
    active = uploaded_images + job.queued_images + job.processing_images
    finished = job.completed_images + job.review_images + job.failed_images
    if not statuses:
        job.status = JobStatus.UPLOADED.value
    elif active:
        if job.processing_images:
            job.status = JobStatus.PROCESSING.value
        elif job.queued_images:
            job.status = JobStatus.QUEUED.value
        else:
            job.status = JobStatus.UPLOADED.value
    elif finished == len(statuses):
        if job.failed_images == len(statuses):
            job.status = JobStatus.FAILED.value
        elif job.failed_images:
            job.status = JobStatus.PARTIAL_FAILURE.value
        else:
            job.status = JobStatus.COMPLETED.value
        job.completed_at = job.completed_at or datetime.now(UTC).replace(tzinfo=None)
    job.updated_at = datetime.now(UTC).replace(tzinfo=None)
    db.flush()
    return job
