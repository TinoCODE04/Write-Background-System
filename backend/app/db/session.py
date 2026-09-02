from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
if settings.database_url.startswith("sqlite:///"):
    database_file = settings.database_url.removeprefix("sqlite:///")
    path = Path(database_file)
    if not path.is_absolute():
        path = settings.repository_root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    database_url = f"sqlite:///{path.as_posix()}"
else:
    database_url = settings.database_url

engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False, "timeout": 30} if database_url.startswith("sqlite") else {},
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_connection: object, _connection_record: object) -> None:
    if database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database() -> None:
    from app.models import ImageAsset, Job  # noqa: F401

    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        # create_all keeps first startup frictionless; stamping the initial revision
        # lets all subsequent schema changes use normal Alembic upgrades.
        connection.exec_driver_sql(
            "CREATE TABLE IF NOT EXISTS alembic_version "
            "(version_num VARCHAR(32) NOT NULL PRIMARY KEY)"
        )
        version = connection.exec_driver_sql("SELECT version_num FROM alembic_version LIMIT 1").scalar()
        if version is None:
            connection.exec_driver_sql(
                "INSERT INTO alembic_version (version_num) VALUES (?)", ("0001_initial",)
            )
        connection.exec_driver_sql("PRAGMA optimize")
