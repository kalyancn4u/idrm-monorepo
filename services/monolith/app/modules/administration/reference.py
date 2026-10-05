"""Admin reference data — the platform's controlled vocabularies in one place (PICS-ADM-001).

Pure (no database): assembles the enumerations and the incident state machine that front-ends use to
build dropdowns and that admins consult. Mutable **disaster-type configuration** is deferred (the
disaster-event entity is → FFP); in the MVP the reference data is these fixed, code-defined lists.
"""

from __future__ import annotations

from typing import Any

from app.modules.alerts.models import AlertSeverity
from app.modules.files.models import FilePurpose
from app.modules.incidents.lifecycle import (
    ACTION_ROLES,
    TRANSITIONS,
    IncidentStatus,
    Priority,
    ServiceType,
)
from app.modules.notifications.models import NotificationType
from app.modules.resources.models import OrgType
from app.modules.users.models import UserRole, UserStatus


def _values(enum_cls: type) -> list[str]:
    """Return an enum's wire values as a list of strings."""
    return [member.value for member in enum_cls]


def build_reference_data() -> dict[str, Any]:
    """Return every controlled vocabulary + the incident lifecycle transitions."""
    transitions = {
        action: {
            "from": sorted(state.value for state in from_states),
            "to": to_state.value,
            "roles": sorted(ACTION_ROLES.get(action, frozenset())),
        }
        for action, (from_states, to_state) in TRANSITIONS.items()
    }
    return {
        "roles": _values(UserRole),
        "user_statuses": _values(UserStatus),
        "service_types": _values(ServiceType),
        "priorities": _values(Priority),
        "incident_statuses": _values(IncidentStatus),
        "incident_transitions": transitions,
        "org_types": _values(OrgType),
        "alert_severities": _values(AlertSeverity),
        "notification_types": _values(NotificationType),
        "file_purposes": _values(FilePurpose),
    }
