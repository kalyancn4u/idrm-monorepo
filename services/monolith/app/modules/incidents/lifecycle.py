"""The incident lifecycle state machine (roadmap §4.4, §13.4; doc 11 §4).

Pure data + helpers, so the rules are unit-testable without a database. Each *action* is a
dedicated transition with (allowed from-states → to-state) and the roles permitted to drive it.
An illegal jump raises ``409 invalid_transition``; a wrong role raises ``403``.
"""

from __future__ import annotations

import enum


class ServiceType(str, enum.Enum):
    medical = "medical"
    food = "food"
    rescue = "rescue"
    water = "water"
    shelter = "shelter"
    other = "other"


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IncidentStatus(str, enum.Enum):
    created = "created"
    approved = "approved"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    verified = "verified"
    cancelled = "cancelled"
    rejected = "rejected"


S = IncidentStatus

# action -> (allowed from-states, resulting to-state)
TRANSITIONS: dict[str, tuple[frozenset[IncidentStatus], IncidentStatus]] = {
    "approve": (frozenset({S.created}), S.approved),
    "reject": (frozenset({S.created, S.approved}), S.rejected),
    "accept": (frozenset({S.created, S.approved}), S.accepted),
    "assign": (frozenset({S.created, S.approved}), S.accepted),
    "start": (frozenset({S.accepted}), S.in_progress),
    "complete": (frozenset({S.in_progress}), S.completed),
    "verify": (frozenset({S.completed}), S.verified),
    "cancel": (frozenset({S.created, S.approved, S.accepted, S.in_progress}), S.cancelled),
}

# action -> the roles permitted to perform it
ACTION_ROLES: dict[str, frozenset[str]] = {
    "approve": frozenset({"coordinator", "admin"}),
    "reject": frozenset({"coordinator", "admin"}),
    "accept": frozenset({"provider"}),
    "assign": frozenset({"coordinator", "admin"}),
    "start": frozenset({"provider"}),
    "complete": frozenset({"provider"}),
    "verify": frozenset({"citizen"}),
    "cancel": frozenset({"citizen", "coordinator", "admin"}),
}


def can_transition(action: str, current: IncidentStatus) -> bool:
    """True if ``action`` is legal from the ``current`` state."""
    spec = TRANSITIONS.get(action)
    return spec is not None and current in spec[0]


def next_status(action: str) -> IncidentStatus:
    """The resulting state for an action (assumes it is already validated)."""
    return TRANSITIONS[action][1]


def role_allowed(action: str, role: str) -> bool:
    """True if ``role`` may perform ``action``."""
    return role in ACTION_ROLES.get(action, frozenset())
