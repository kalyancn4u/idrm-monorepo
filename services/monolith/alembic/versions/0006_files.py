"""Files: the file_purpose enum and the upload-metadata table (bytes live in MinIO).

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-17

Roadmap §13.5; doc 50 §5.9. Metadata only — the object key/URL is stored, never the blob (ADR-007).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_UUID = postgresql.UUID(as_uuid=True)
_PURPOSE_VALUES = ("incident_photo", "completion_proof", "org_document")
_PURPOSE = postgresql.ENUM(*_PURPOSE_VALUES, name="file_purpose", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(*_PURPOSE_VALUES, name="file_purpose").create(bind, checkfirst=True)

    op.create_table(
        "files",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("uploaded_by", _UUID, sa.ForeignKey("users.id")),
        sa.Column("bucket", sa.String(63), nullable=False),
        sa.Column("object_key", sa.String(512), nullable=False),
        sa.Column("url", sa.String(1024)),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger, nullable=False),
        sa.Column("purpose", _PURPOSE, nullable=False),
        sa.Column("entity_type", sa.String(30)),
        sa.Column("entity_id", _UUID),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("size_bytes <= 10485760", name="ck_files_size_max_10mb"),
    )
    op.create_index("ix_files_uploaded_by", "files", ["uploaded_by"])
    op.create_index("ix_files_entity", "files", ["entity_type", "entity_id"])


def downgrade() -> None:
    op.drop_table("files")
    postgresql.ENUM(name="file_purpose").drop(op.get_bind(), checkfirst=True)
