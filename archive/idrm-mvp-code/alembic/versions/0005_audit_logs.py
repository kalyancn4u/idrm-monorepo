"""Audit logs: the append-only accountability table.

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-17

Roadmap §13.5; doc 50 §5.10. Append-only — no ``updated_at`` / ``deleted_at``; only inserts and
reads ever touch this table (PICS-AUD-001/002).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("actor_id", _UUID, sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50)),
        sa.Column("resource_id", _UUID),
        sa.Column("ip_address", postgresql.INET),
        sa.Column("old_values", postgresql.JSONB),
        sa.Column("new_values", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_resource", "audit_logs", ["resource_type", "resource_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", [sa.text("created_at DESC")])


def downgrade() -> None:
    op.drop_table("audit_logs")
