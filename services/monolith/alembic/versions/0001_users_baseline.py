"""Baseline: PostGIS extension, user enums, and the Users/Auth tables.

Revision ID: 0001
Revises:
Create Date: 2026-08-17

The first migration (roadmap §3.2, §13.3). Later modules add their tables in new revisions.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_UUID = postgresql.UUID(as_uuid=True)
_ROLE = postgresql.ENUM("citizen", "provider", "coordinator", "admin", name="user_role", create_type=False)
_STATUS = postgresql.ENUM("pending", "active", "suspended", "deactivated", name="user_status", create_type=False)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    postgresql.ENUM("citizen", "provider", "coordinator", "admin", name="user_role").create(
        op.get_bind(), checkfirst=True
    )
    postgresql.ENUM("pending", "active", "suspended", "deactivated", name="user_status").create(
        op.get_bind(), checkfirst=True
    )

    op.create_table(
        "users",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20)),
        sa.Column("role", _ROLE, nullable=False, server_default="citizen"),
        sa.Column("status", _STATUS, nullable=False, server_default="pending"),
        sa.Column("email_verified", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("failed_login_attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True)),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("language", sa.String(5), nullable=False, server_default="en"),
        sa.Column("preferences", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table(
        "user_sessions",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", _UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("refresh_token", sa.String(500), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip_address", postgresql.INET),
        sa.Column("user_agent", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])
    op.create_index("ix_user_sessions_refresh_token", "user_sessions", ["refresh_token"], unique=True)

    for name in ("email_verification_tokens", "password_reset_tokens"):
        extra = "verified_at" if name == "email_verification_tokens" else "used_at"
        op.create_table(
            name,
            sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("user_id", _UUID, sa.ForeignKey("users.id"), nullable=False),
            sa.Column("token", sa.String(255), nullable=False, unique=True),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column(extra, sa.DateTime(timezone=True)),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
        op.create_index(f"ix_{name}_token", name, ["token"], unique=True)
        op.create_index(f"ix_{name}_user_id", name, ["user_id"])


def downgrade() -> None:
    op.drop_table("password_reset_tokens")
    op.drop_table("email_verification_tokens")
    op.drop_table("user_sessions")
    op.drop_table("users")
    postgresql.ENUM(name="user_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="user_role").drop(op.get_bind(), checkfirst=True)
