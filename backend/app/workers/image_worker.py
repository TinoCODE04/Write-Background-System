from __future__ import annotations

import logging
import time
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.ai.models import BiRefNetModel
from app.ai.pipeline import ImageProcessingPipeline
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db import SessionLocal
from app.db.session import initialize_database
from app.models import ImageAsset, ImageStatus
from app.services.jobs import refresh_job_counters
from app.storage.local import LocalStorage


logger = logging.getLogger(__name__)


def recover_stale_tasks(db: Session) -> int:
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=get_settings().stale_processing_minutes)
    result = db.execute(
        update(ImageAsset)
        .where(ImageAsset.status == ImageStatus.PROCESSING.value, ImageAsset.updated_at < cutoff)
        .values(status=ImageStatus.QUEUED.value, error_message="Recovered after interrupted worker")
    )
    db.commit()
    return int(result.rowcount or 0)


def claim_next_task(db: Session) -> ImageAsset | None:
    """Optimistic conditional update prevents two workers from claiming one row."""
    while True:
        candidate_id = db.scalar(
            select(ImageAsset.id)
            .where(ImageAsset.status == ImageStatus.QUEUED.value)
            .order_by(ImageAsset.created_at, ImageAsset.id)
            .limit(1)
        )
        if candidate_id is None:
            return None
        claimed_at = datetime.now(UTC).replace(tzinfo=None)
        result = db.execute(
            update(ImageAsset)
            .where(ImageAsset.id == candidate_id, ImageAsset.status == ImageStatus.QUEUED.value)
            .values(status=ImageStatus.PROCESSING.value, updated_at=claimed_at, error_message=None)
        )
        if result.rowcount == 1:
            db.commit()
            asset = db.get(ImageAsset, candidate_id)
            if asset:
                refresh_job_counters(db, asset.job_id)
                db.commit()
                db.refresh(asset)
            return asset
        db.rollback()


def process_asset(db: Session, asset: ImageAsset, pipeline: ImageProcessingPipeline, storage: LocalStorage) -> None:
    settings = get_settings()
    try:
        original = storage.resolve(asset.original_path)
        output_root = storage.ensure_job(asset.job_id)
        result = pipeline.process(original, output_root, asset.id, asset.processing_settings)
        asset.mask_path = storage.relative(result.mask_path)
        asset.transparent_path = storage.relative(result.transparent_path)
        asset.white_png_path = storage.relative(result.white_png_path)
        asset.white_jpg_path = storage.relative(result.white_jpg_path)
        asset.thumbnail_path = storage.relative(result.thumbnail_path)
        asset.width = result.width
        asset.height = result.height
        asset.quality_score = result.quality_score
        asset.quality_flags = result.quality_flags
        asset.processing_time_ms = result.processing_time_ms
        asset.model_name = pipeline.model.get_model_name()
        asset.model_version = pipeline.model.get_model_version()
        asset.status = (
            ImageStatus.COMPLETED.value
            if result.quality_score >= settings.quality_pass_threshold
            else ImageStatus.NEEDS_REVIEW.value
        )
        asset.error_message = None
        logger.info(
            "Image processing completed",
            extra={
                "job_id": asset.job_id,
                "image_id": asset.id,
                "input_filename": asset.original_filename,
                "resolution": f"{asset.width}x{asset.height}",
                "model": asset.model_name,
                "device": getattr(pipeline.model, "device", "unknown"),
                "duration_ms": result.processing_time_ms,
                "quality_score": result.quality_score,
                "quality_flags": result.quality_flags,
            },
        )
    except Exception as exc:
        message = "GPU memory insufficient" if "out of memory" in str(exc).lower() else str(exc)[:1000]
        asset.status = ImageStatus.FAILED.value
        asset.error_message = message
        logger.exception(
            "Image processing failed",
            extra={"job_id": asset.job_id, "image_id": asset.id, "input_filename": asset.original_filename, "error_detail": message},
        )
        if message == "GPU memory insufficient":
            try:
                import torch

                torch.cuda.empty_cache()
            except ImportError:
                pass
    finally:
        refresh_job_counters(db, asset.job_id)
        db.commit()


def run_worker() -> None:
    configure_logging()
    initialize_database()
    settings = get_settings()
    model = BiRefNetModel()
    # Deliberately load once, before polling. The first run downloads the real weights.
    model.load()
    pipeline = ImageProcessingPipeline(model)
    storage = LocalStorage()
    with SessionLocal() as db:
        recovered = recover_stale_tasks(db)
        if recovered:
            logger.warning("Recovered stale tasks", extra={"quality_flags": [f"recovered:{recovered}"]})
    logger.info("Image worker ready", extra={"model": model.get_model_name(), "device": model.device})
    while True:
        with SessionLocal() as db:
            asset = claim_next_task(db)
            if asset:
                process_asset(db, asset, pipeline, storage)
        if not asset:
            time.sleep(settings.worker_poll_interval)


if __name__ == "__main__":
    run_worker()
