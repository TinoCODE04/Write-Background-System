from __future__ import annotations

import uuid

from app.models import ImageAsset, ImageStatus, Job
from app.storage.local import LocalStorage
from app.workers.image_worker import claim_next_task, process_asset


def make_asset(db, name: str = "product.png") -> ImageAsset:
    job = Job(name="Worker test")
    db.add(job); db.flush()
    image_id = str(uuid.uuid4())
    root = LocalStorage().ensure_job(job.id)
    original = root / "original" / f"{image_id}.png"
    from PIL import Image
    Image.new("RGB", (20, 20), "white").save(original)
    asset = ImageAsset(
        id=image_id, job_id=job.id, original_filename=name, stored_filename=original.name,
        original_path=LocalStorage().relative(original), width=20, height=20, file_size=original.stat().st_size,
        mime_type="image/png", status=ImageStatus.QUEUED.value, processing_settings={},
    )
    db.add(asset); db.commit()
    return asset


def test_worker_task_claim_is_conditional(db):
    asset = make_asset(db)
    claimed = claim_next_task(db)
    assert claimed is not None and claimed.id == asset.id
    assert claimed.status == ImageStatus.PROCESSING.value
    assert claim_next_task(db) is None


class FailingPipeline:
    class Model:
        @staticmethod
        def get_model_name(): return "failure-test"
        @staticmethod
        def get_model_version(): return "1"
    model = Model()
    @staticmethod
    def process(*_args, **_kwargs): raise RuntimeError("isolated test failure")


def test_processing_failure_is_isolated(db):
    first = make_asset(db, "first.png")
    first.status = ImageStatus.PROCESSING.value
    db.commit()
    process_asset(db, first, FailingPipeline(), LocalStorage())  # type: ignore[arg-type]
    db.refresh(first)
    assert first.status == ImageStatus.FAILED.value
    assert "isolated test failure" in (first.error_message or "")
    second = make_asset(db, "second.png")
    assert second.status == ImageStatus.QUEUED.value

