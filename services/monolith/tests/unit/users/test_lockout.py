"""Unit tests for the account-lockout policy constants (roadmap §8.3; doc 22 §2.4)."""

from __future__ import annotations

from app.modules.users.service import LOCKOUT_MINUTES, MAX_FAILED_ATTEMPTS


def test_lockout_policy_matches_locked_decision() -> None:
    # Locked policy: 5 failed attempts, then a 15-minute lock (short, for emergency users).
    assert MAX_FAILED_ATTEMPTS == 5
    assert LOCKOUT_MINUTES == 15
