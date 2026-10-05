"""Unit tests for resources schemas/enums (no database) — wire values and defaults."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.resources.models import OrgType
from app.modules.resources.schemas import CapacityRequest, OrganizationCreate


def test_org_type_wire_values() -> None:
    assert {t.value for t in OrgType} == {
        "ngo", "government", "private", "hospital", "volunteer_group"
    }


def test_org_create_defaults() -> None:
    org = OrganizationCreate(name="X", type="ngo")
    assert org.service_categories == []
    assert org.service_radius_km == 10.0
    assert org.capacity == 0


def test_capacity_rejects_negative() -> None:
    with pytest.raises(ValidationError):
        CapacityRequest(capacity=-1)
