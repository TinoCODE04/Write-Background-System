from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from app.core.config import get_settings
from app.db import engine
from app.models import ImageAsset, ImageStatus


def create_job(client):
    response = client.post("/api/jobs", json={"name": "Autumn catalog"})
    assert response.status_code == 201
    return response.json()


def test_database_initialization_and_job_creation(client):
    job = create_job(client)
    assert job["name"] == "Autumn catalog"
    assert job["status"] == "UPLOADED"
    database = Path(get_settings().database_url.removeprefix("sqlite:///"))
    assert database.exists()
    with engine.connect() as connection:
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0001_initial"


def test_multi_image_upload_and_storage_paths(client, png_bytes):
    job = create_job(client)
    response = client.post(
        f"/api/jobs/{job['id']}/images",
        files=[("files", ("first.png", png_bytes, "image/png")), ("files", ("second.png", png_bytes + b"x", "application/octet-stream"))],
    )
    # App validates the image content rather than trusting the supplied MIME.
    assert response.status_code == 201
    body = response.json()
    assert len(body["uploaded"]) == 2
    assert all(item["mime_type"] == "image/png" for item in body["uploaded"])
    # The job folder is named after the first uploaded file ("first--{id prefix}")
    # so batches stay recognizable when browsing the storage directory directly.
    jobs_root = Path(get_settings().storage_path) / "jobs"
    (job_dir,) = [path for path in jobs_root.iterdir() if path.name.endswith(f"--{job['id'][:8]}")]
    assert job_dir.name.startswith("first--")
    for item in body["uploaded"]:
        stem = Path(item["original_filename"]).stem
        original = job_dir / "original"
        assert any(path.name.startswith(f"{stem}--") for path in original.iterdir())
        assert ".." not in item["original_filename"]


def test_upload_keeps_chinese_filename_readable(client, png_bytes):
    job = create_job(client)
    response = client.post(
        f"/api/jobs/{job['id']}/images",
        files=[("files", ("微信图片_20260902.jpg", png_bytes, "image/jpeg"))],
    )
    assert response.status_code == 201
    jobs_root = Path(get_settings().storage_path) / "jobs"
    (job_dir,) = [path for path in jobs_root.iterdir() if path.name.endswith(f"--{job['id'][:8]}")]
    assert job_dir.name.startswith("微信图片_20260902--")
    names = [path.name for path in (job_dir / "original").iterdir()]
    # The stored extension follows the detected content (PNG), not the claimed suffix.
    assert any(name.startswith("微信图片_20260902--") and name.endswith(".png") for name in names)


def test_invalid_and_corrupt_images_are_rejected(client):
    job = create_job(client)
    response = client.post(
        f"/api/jobs/{job['id']}/images",
        files=[("files", ("bad.jpg", b"not an image", "image/jpeg"))],
    )
    assert response.status_code == 422
    assert "corrupt" in str(response.json()).lower()


def test_queue_and_approve_workflow(client, db, png_bytes):
    job = create_job(client)
    uploaded = client.post(f"/api/jobs/{job['id']}/images", files=[("files", ("item.png", png_bytes, "image/png"))]).json()["uploaded"][0]
    queued = client.post(f"/api/jobs/{job['id']}/process")
    assert queued.status_code == 200
    assert queued.json()["queued_images"] == 1
    asset = db.get(ImageAsset, uploaded["id"])
    asset.status = ImageStatus.NEEDS_REVIEW.value
    asset.quality_score = 72
    db.commit()
    approved = client.post(f"/api/images/{asset.id}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "COMPLETED"
    assert approved.json()["approved_at"] is not None


def test_settings_and_health_api(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    info = client.get("/api/system")
    assert info.status_code == 200
    assert info.json()["database"] == "SQLite"
    assert "DATABASE_URL" not in info.text
