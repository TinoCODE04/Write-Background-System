from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image


TEST_ROOT = Path(tempfile.mkdtemp(prefix="image-cleaner-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(TEST_ROOT / 'test.db').as_posix()}"
os.environ["STORAGE_PATH"] = str(TEST_ROOT / "storage")
os.environ["MAX_UPLOAD_MB"] = "2"

from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db():
    with SessionLocal() as session:
        yield session


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def image_bytes(fmt: str = "PNG", color: tuple[int, int, int] = (180, 45, 25)) -> bytes:
    stream = io.BytesIO()
    Image.new("RGB", (48, 36), color).save(stream, format=fmt)
    return stream.getvalue()


@pytest.fixture
def png_bytes():
    return image_bytes("PNG")

