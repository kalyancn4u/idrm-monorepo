"""Core security primitives shared by every module: password hashing + RS256 JWTs.

Passwords are stored only as bcrypt (cost 12) hashes; access tokens are RS256-signed JWTs
verifiable with the public key alone. Full auth flow lives in the users module (roadmap §8, §13.3).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain: str) -> str:
    """Return a bcrypt (cost-12) hash of a plaintext password."""
    return _pwd.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Check a plaintext password against its stored bcrypt hash."""
    return _pwd.verify(plain, hashed)


def _read_key(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def create_access_token(subject: str, role: str) -> str:
    """Sign a short-lived RS256 access token carrying the user id (``sub``) and ``role``."""
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_ttl_min),
    }
    return jwt.encode(payload, _read_key(settings.jwt_private_key_path), algorithm="RS256")


def decode_token(token: str) -> dict[str, Any]:
    """Verify an access token with the public key and return its claims."""
    settings = get_settings()
    return jwt.decode(token, _read_key(settings.jwt_public_key_path), algorithms=["RS256"])
