"""
dbmodels/user.py — the `users` table (mirrors 02-schema.sql §users).

Enum-like columns (role) are stored as VARCHAR; the database CHECK constraint
enforces valid values, and the Pydantic schemas validate with the Python enums.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, text
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from dbmodels.base import Base


class User(Base):
    """A registered account — citizen, volunteer, provider, organizer, etc. The
    `role` column drives permissions; `password_hash` is a bcrypt hash, never the
    plaintext password."""

    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # bcrypt, cost 12

    # Profile
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)  # E.164, e.g. +919876543210

    # Role — see dbmodels.enums.UserRole (DB CHECK enforces the 10 valid values)
    role: Mapped[str] = mapped_column(String(50), nullable=False, server_default="CITIZEN")

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    # Flexible settings bag (language, notification prefs, theme).
    # The database supplies a rich default; pass your own to override.
    preferences: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Security tracking
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    phone_verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)
    last_login_ip: Mapped[str | None] = mapped_column(INET)

    # Timestamps (updated_at is auto-maintained by a DB trigger)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self) -> str:  # handy in logs / shell
        return f"<User {self.email} ({self.role})>"
