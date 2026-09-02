"""Initial jobs and image assets schema.

Revision ID: 0001_initial
Revises:
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(160), nullable=False),
        sa.Column("status", sa.String(32), nullable=False), sa.Column("total_images", sa.Integer(), nullable=False),
        sa.Column("queued_images", sa.Integer(), nullable=False), sa.Column("processing_images", sa.Integer(), nullable=False),
        sa.Column("completed_images", sa.Integer(), nullable=False), sa.Column("review_images", sa.Integer(), nullable=False),
        sa.Column("failed_images", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False), sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_jobs_status", "jobs", ["status"]); op.create_index("ix_jobs_created_at", "jobs", ["created_at"])
    op.create_table(
        "image_assets",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("job_id", sa.String(36), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(512), nullable=False), sa.Column("stored_filename", sa.String(64), nullable=False, unique=True),
        sa.Column("original_path", sa.String(1024), nullable=False), sa.Column("mask_path", sa.String(1024)),
        sa.Column("transparent_path", sa.String(1024)), sa.Column("white_png_path", sa.String(1024)),
        sa.Column("white_jpg_path", sa.String(1024)), sa.Column("thumbnail_path", sa.String(1024)),
        sa.Column("width", sa.Integer(), nullable=False), sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False), sa.Column("mime_type", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False), sa.Column("quality_score", sa.Float()), sa.Column("quality_flags", sa.JSON(), nullable=False),
        sa.Column("processing_time_ms", sa.Integer()), sa.Column("model_name", sa.String(255)), sa.Column("model_version", sa.String(128)),
        sa.Column("processing_settings", sa.JSON(), nullable=False), sa.Column("error_message", sa.Text()), sa.Column("approved_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_image_assets_job_id", "image_assets", ["job_id"]); op.create_index("ix_image_assets_status", "image_assets", ["status"])
    op.create_index("ix_image_assets_created_at", "image_assets", ["created_at"]); op.create_index("ix_image_assets_updated_at", "image_assets", ["updated_at"])
    op.create_index("idx_image_assets_queue", "image_assets", ["status", "created_at"]); op.create_index("idx_image_assets_job_status", "image_assets", ["job_id", "status"])


def downgrade() -> None:
    op.drop_table("image_assets"); op.drop_table("jobs")

