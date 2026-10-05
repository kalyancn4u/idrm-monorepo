"""Unit tests for the password hashing primitives (no database needed)."""

from __future__ import annotations

from app.core.security import hash_password, verify_password


def test_hash_is_not_plaintext_and_verifies() -> None:
    hashed = hash_password("correct horse battery staple")
    assert hashed != "correct horse battery staple"
    assert hashed.startswith("$2")  # bcrypt marker
    assert verify_password("correct horse battery staple", hashed) is True


def test_verify_rejects_wrong_password() -> None:
    hashed = hash_password("s3cret-passphrase")
    assert verify_password("not-the-password", hashed) is False


def test_hashes_are_salted_and_differ() -> None:
    a = hash_password("same-password")
    b = hash_password("same-password")
    assert a != b  # random per-hash salt
