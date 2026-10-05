"""Unit tests for the incident lifecycle state machine (no database; roadmap §4.4)."""

from __future__ import annotations

from app.modules.incidents.lifecycle import (
    IncidentStatus as S,
)
from app.modules.incidents.lifecycle import (
    can_transition,
    next_status,
    role_allowed,
)


def test_legal_happy_path_transitions() -> None:
    assert can_transition("approve", S.created)
    assert can_transition("accept", S.approved)
    assert can_transition("start", S.accepted)
    assert can_transition("complete", S.in_progress)
    assert can_transition("verify", S.completed)


def test_illegal_jumps_are_rejected() -> None:
    assert not can_transition("start", S.created)  # can't start before accept
    assert not can_transition("verify", S.accepted)
    assert not can_transition("accept", S.completed)


def test_next_status_mapping() -> None:
    assert next_status("accept") is S.accepted
    assert next_status("complete") is S.completed
    assert next_status("verify") is S.verified


def test_role_permissions() -> None:
    assert role_allowed("accept", "provider")
    assert not role_allowed("accept", "citizen")
    assert role_allowed("approve", "coordinator")
    assert role_allowed("verify", "citizen")
    assert not role_allowed("verify", "provider")


def test_cancel_allowed_from_active_states_only() -> None:
    assert can_transition("cancel", S.created)
    assert can_transition("cancel", S.in_progress)
    assert not can_transition("cancel", S.verified)
    assert not can_transition("cancel", S.completed)
