"""Alerts & notifications: two enums, the alerts table, notifications + preferences.

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-17

Roadmap §13.5; doc 50 §5.7–5.8. Alerts carry a PostGIS MultiPolygon area (NULL = platform-wide);
notifications are per-user rows pulled by the client (no broker in the MVP, ADR-012).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_UUID = postgresql.UUID(as_uuid=True)
_SEVERITY_VALUES = ("info", "warning", "critical")
_NTYPE_VALUES = ("incident_update", "assignment", "alert", "verification", "system")
_SEVERITY = postgresql.ENUM(*_SEVERITY_VALUES, name="alert_severity", create_type=False)
_NTYPE = postgresql.ENUM(*_NTYPE_VALUES, name="notification_type", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(*_SEVERITY_VALUES, name="alert_severity").create(bind, checkfirst=True)
    postgresql.ENUM(*_NTYPE_VALUES, name="notification_type").create(bind, checkfirst=True)

    op.create_table(
        "alerts",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("severity", _SEVERITY, nullable=False),
        sa.Column("area", Geometry("MULTIPOLYGON", srid=4326, spatial_index=False)),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_by", _UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_alerts_area", "alerts", ["area"], postgresql_using="gist")
    op.create_index("ix_alerts_active", "alerts", ["active"])

    op.create_table(
        "notifications",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", _UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("type", _NTYPE, nullable=False),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("link", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])

    op.create_table(
        "notification_preferences",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", _UUID, sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("email", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("sms", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("in_app", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_notification_preferences_user_id", "notification_preferences", ["user_id"])


def downgrade() -> None:
    op.drop_table("notification_preferences")
    op.drop_table("notifications")
    op.drop_table("alerts")
    postgresql.ENUM(name="notification_type").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="alert_severity").drop(op.get_bind(), checkfirst=True)
