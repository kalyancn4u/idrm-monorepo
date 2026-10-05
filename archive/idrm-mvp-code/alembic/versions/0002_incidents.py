"""Incidents: enums, the incidents table (PostGIS point), and the status timeline.

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-17

Roadmap §13.4; doc 50 §5.5–5.6. ``assigned_organization_id`` has no FK yet — added when the
organizations module lands.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_UUID = postgresql.UUID(as_uuid=True)
_SERVICE = postgresql.ENUM(
    "medical", "food", "rescue", "water", "shelter", "other", name="service_type", create_type=False
)
_PRIORITY = postgresql.ENUM("low", "medium", "high", "critical", name="priority", create_type=False)
_STATUS_VALUES = (
    "created", "approved", "accepted", "in_progress", "completed", "verified", "cancelled", "rejected"
)
_STATUS = postgresql.ENUM(*_STATUS_VALUES, name="incident_status", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(
        "medical", "food", "rescue", "water", "shelter", "other", name="service_type"
    ).create(bind, checkfirst=True)
    postgresql.ENUM("low", "medium", "high", "critical", name="priority").create(bind, checkfirst=True)
    postgresql.ENUM(*_STATUS_VALUES, name="incident_status").create(bind, checkfirst=True)

    op.create_table(
        "incidents",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("service_type", _SERVICE, nullable=False),
        sa.Column("priority", _PRIORITY, nullable=False),
        sa.Column("status", _STATUS, nullable=False, server_default="created"),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("location", Geometry("POINT", srid=4326, spatial_index=False), nullable=False),
        sa.Column("requester_id", _UUID, sa.ForeignKey("users.id")),
        sa.Column("guest_contact", sa.String(20)),
        sa.Column("tracking_token", sa.String(64), unique=True),
        sa.Column("assigned_organization_id", _UUID),
        sa.Column("approved_by", _UUID, sa.ForeignKey("users.id")),
        sa.Column("rating", sa.SmallInteger),
        sa.Column("review", sa.Text),
        sa.Column("rejection_reason", sa.Text),
        sa.Column("cancellation_reason", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_incidents_rating_range"),
    )
    op.create_index("ix_incidents_location", "incidents", ["location"], postgresql_using="gist")
    op.create_index("ix_incidents_status", "incidents", ["status"])
    op.create_index("ix_incidents_service_type", "incidents", ["service_type"])
    op.create_index("ix_incidents_priority", "incidents", ["priority"])
    op.create_index("ix_incidents_requester_id", "incidents", ["requester_id"])
    op.create_index("ix_incidents_assigned_org", "incidents", ["assigned_organization_id"])
    op.create_index("ix_incidents_created_at", "incidents", ["created_at"])
    op.execute(
        "CREATE INDEX ix_incidents_description_fts ON incidents "
        "USING gin (to_tsvector('english', description))"
    )

    op.create_table(
        "incident_updates",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("incident_id", _UUID, sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("from_status", _STATUS),
        sa.Column("to_status", _STATUS, nullable=False),
        sa.Column("actor_id", _UUID, sa.ForeignKey("users.id")),
        sa.Column("note", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_incident_updates_incident_id", "incident_updates", ["incident_id"])


def downgrade() -> None:
    op.drop_table("incident_updates")
    op.drop_index("ix_incidents_description_fts", table_name="incidents")
    op.drop_table("incidents")
    postgresql.ENUM(name="incident_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="priority").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="service_type").drop(op.get_bind(), checkfirst=True)
