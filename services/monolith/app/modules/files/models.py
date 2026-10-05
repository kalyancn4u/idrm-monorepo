"""Files module ORM model — upload **metadata only**; the bytes live in MinIO (doc 50 §5.9).

The database stores the object key / URL and never the blob itself (ADR-007, PICS-FIL-001). A
``size_bytes`` CHECK mirrors the 10 MB hard limit enforced in the service.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, UUIDPrimaryKey


class FilePurpose(str, enum.Enum):
    incident_photo = "incident_photo"
    completion_proof = "completion_proof"
    org_document = "org_document"


file_purpose_enum = SAEnum(FilePurpose, name="file_purpose")


class File(UUIDPrimaryKey, Base):
    """One stored upload's metadata (doc 50 §5.9)."""

    __tablename__ = "files"
    __table_args__ = (
        CheckConstraint("size_bytes <= 10485760", name="ck_files_size_max_10mb"),
    )

    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id"), index=True
    )  # NULL = guest
    bucket: Mapped[str] = mapped_column(String(63), nullable=False)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1024))
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    purpose: Mapped[FilePurpose] = mapped_column(file_purpose_enum, nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(30), index=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
