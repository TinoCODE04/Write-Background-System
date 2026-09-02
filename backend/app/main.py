from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import images, jobs, system
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import initialize_database


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    initialize_database()
    get_settings().storage_path.joinpath("jobs").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="AI Product Image Cleaner API",
    version="0.1.0",
    description="Local batch product-image cleanup and quality-control service.",
    lifespan=lifespan,
)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(jobs.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(system.router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

