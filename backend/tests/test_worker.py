from __future__ import annotations

import uuid

from PIL import Image

from app.ai.pipeline.image_pipeline import PipelineResult
from app.models import ImageAsset, ImageStatus, Job
from app.services.jobs import resolve_job_dirname
from app.storage.local import LocalStorage, sanitize_stem
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


class FakePipeline:
    class Model:
        @staticmethod
        def get_model_name(): return "fake-test"
        @staticmethod
        def get_model_version(): return "1"
    model = Model()
    device = "cpu"

    @staticmethod
    def process(original, output_root, stem, settings):
        paths = {}
        for sub, ext in (("masks", "png"), ("transparent", "png"), ("white_png", "png"), ("white_jpg", "jpg"), ("thumbnails", "jpg")):
            target = output_root / sub / f"{stem}.{ext}"
            target.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", (4, 4), "white").save(target)
            paths[sub] = target
        return PipelineResult(paths["masks"], paths["transparent"], paths["white_png"], paths["white_jpg"], paths["thumbnails"], 99.0, [], 5, 20, 20)


def make_readable_asset(db, name: str = "微信图片_测试.jpg") -> ImageAsset:
    job = Job(name="Readable test")
    db.add(job); db.flush()
    storage = LocalStorage()
    image_id = str(uuid.uuid4())
    dirname = resolve_job_dirname(db, job, storage, filename_hint=name)
    root = storage.ensure_job(dirname)
    stored = f"{sanitize_stem(name, max_length=40)}--{image_id[:8]}.png"
    original = root / "original" / stored
    Image.new("RGB", (20, 20), "white").save(original)
    asset = ImageAsset(
        id=image_id, job_id=job.id, original_filename=name, stored_filename=stored,
        original_path=storage.relative(original), width=20, height=20, file_size=original.stat().st_size,
        mime_type="image/png", status=ImageStatus.QUEUED.value, processing_settings={},
    )
    db.add(asset); db.commit()
    return asset


def test_worker_writes_readable_output_names(db):
    asset = make_readable_asset(db)
    process_asset(db, asset, FakePipeline(), LocalStorage())  # type: ignore[arg-type]
    db.refresh(asset)
    assert asset.status == ImageStatus.COMPLETED.value
    transparent = LocalStorage().resolve(asset.transparent_path)
    assert transparent.is_file()
    assert transparent.parent.parent.name.startswith("微信图片_测试--")
    assert transparent.name.startswith("微信图片_测试--")


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

