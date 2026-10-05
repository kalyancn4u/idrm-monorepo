"""Organizations & resources: the org_type enum, both tables, and the incidents→org FK.

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-17

Roadmap §13.5; doc 50 §5.3–5.4. Reuses the existing ``service_type`` enum (created in 0002) for
``organizations.service_categories`` (an array), and finally adds the FK constraint from
``incidents.assigned_organization_id`` to ``organizations.id`` that 0002 deferred.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_UUID = postgresql.UUID(as_uuid=True)
_ORG_TYPE_VALUES = ("ngo", "government", "private", "hospital", "volunteer_group")
_ORG_TYPE = postgresql.ENUM(*_ORG_TYPE_VALUES, name="org_type", create_type=False)
# service_type already exists (0002) — reference it, do not recreate.
_SERVICE = postgresql.ENUM(
    "medical", "food", "rescue", "water", "shelter", "other", name="service_type", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    postgresql.ENUM(*_ORG_TYPE_VALUES, name="org_type").create(bind, checkfirst=True)

    op.create_table(
        "organizations",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", _ORG_TYPE, nullable=False),
        sa.Column("owner_user_id", _UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "service_categories",
            postgresql.ARRAY(_SERVICE),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.Column("service_area_center", Geometry("POINT", srid=4326, spatial_index=False)),
        sa.Column("service_radius_km", sa.Numeric(8, 2), nullable=False, server_default="10.0"),
        sa.Column("capacity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("available_capacity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_available", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("verified_by", _UUID, sa.ForeignKey("users.id")),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("rating", sa.Numeric(3, 2)),
        sa.Column("total_requests_completed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("contact_phone", sa.String(20)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_organizations_owner_user_id", "organizations", ["owner_user_id"])
    op.create_index(
        "ix_organizations_service_area", "organizations", ["service_area_center"],
        postgresql_using="gist",
    )
    op.create_index(
        "ix_organizations_service_categories", "organizations", ["service_categories"],
        postgresql_using="gin",
    )

    op.create_table(
        "resources",
        sa.Column("id", _UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", _UUID, sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("kind", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("location", Geometry("POINT", srid=4326, spatial_index=False)),
        sa.Column("is_available", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_resources_organization_id", "resources", ["organization_id"])
    op.create_index(
        "ix_resources_location", "resources", ["location"], postgresql_using="gist"
    )

    # The FK deferred in 0002 — now that organizations exists.
    op.create_foreign_key(
        "fk_incidents_assigned_organization",
        "incidents",
        "organizations",
        ["assigned_organization_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_incidents_assigned_organization", "incidents", type_="foreignkey")
    op.drop_table("resources")
    op.drop_table("organizations")
    postgresql.ENUM(name="org_type").drop(op.get_bind(), checkfirst=True)
