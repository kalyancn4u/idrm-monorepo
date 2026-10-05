"""
dbmodels/audit_log.py — the `audit_logs` table (immutable action trail).
Mirrors 02-schema.sql §audit_logs.

Uses BIGSERIAL (auto-incrementing integer) PK — audit logs are high-volume and
benefit from fast sequential inserts. Rows are NEVER updated or deleted.
"""
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from dbmodels.base import Base


class AuditLog(Base):
    """One immutable record of a significant action — who did what to which resource,
    and whether it succeeded. Append-only: rows are never updated or deleted."""

    __tablename__ = "audit_logs"

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Who (email/role denormalised so logs stay readable if the user is deleted)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL", onupdate="CASCADE")
    )
    user_email: Mapped[str | None] = mapped_column(String(255))
    user_role: Mapped[str | None] = mapped_column(String(50))

    # What
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # enums.AuditResourceType
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    # Context
    ip_address: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(Text)
    request_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    # What changed: {"before": {...}, "after": {...}}
    changes: Mapped[dict | None] = mapped_column(JSONB)

    # Outcome
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    error_message: Mapped[str | None] = mapped_column(Text)

    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} {self.resource_type}:{self.resource_id} ok={self.success}>"
