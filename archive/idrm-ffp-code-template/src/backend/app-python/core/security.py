"""
core/security.py — password hashing, JWT tokens, and the auth dependency (Module M2).

Three concerns live here:
  • Passwords — bcrypt hashing/verification (cost 12) via passlib.
  • JWTs — short-lived access tokens (15 min) + long-lived refresh tokens
    (7 days) via python-jose.
  • get_current_user — a FastAPI dependency that resolves the request's
    credentials to the logged-in `User` row.

Rookie notes:
  • We NEVER store or log plaintext passwords — only the bcrypt hash.
  • A JWT is *signed*, not encrypted: anyone can read its claims, so never put
    secrets in the payload. The signature is what proves we issued it.
  • Access tokens are deliberately short-lived; clients exchange the long-lived
    refresh token for a new one (see POST /auth/refresh).
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db
from dbmodels.user import User

# bcrypt at cost 12 (matches the schema's note + our security policy).
# deprecated="auto" lets passlib transparently re-hash with stronger settings later.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# Values for the JWT "type" claim — so a refresh token can't be used where an
# access token is expected (and vice-versa).
ACCESS_TOKEN = "access"
REFRESH_TOKEN = "refresh"


def unauthorized(detail: str = "Not authenticated") -> HTTPException:
    """Build a 401 carrying the `WWW-Authenticate: Bearer` header clients expect."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


# ---- Passwords --------------------------------------------------------------
def hash_password(plain: str) -> str:
    """Return a bcrypt hash of `plain`. Persist this — never the plaintext."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if `plain` matches the stored bcrypt `hashed` value."""
    return pwd_context.verify(plain, hashed)


# ---- JWT create / decode ----------------------------------------------------
def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra: dict[str, Any] | None = None,
) -> str:
    """Build and sign a JWT. `subject` becomes the `sub` claim (the user_id).

    `iat`/`exp` are integer Unix timestamps (the JWT standard); python-jose does
    not auto-convert `datetime` objects, so we convert explicitly.
    """
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    """A 15-minute access token. Carries `role` so the gateway can authorise fast."""
    return _create_token(
        str(user_id),
        ACCESS_TOKEN,
        timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        extra={"role": role},
    )


def create_refresh_token(user_id: uuid.UUID) -> str:
    """A 7-day refresh token, exchanged at POST /auth/refresh for a new access token."""
    return _create_token(
        str(user_id),
        REFRESH_TOKEN,
        timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    """Verify a token's signature + expiry and return its claims.

    Raises 401 if the token is malformed/expired, or — when `expected_type` is
    given — if it's the wrong kind (e.g. a refresh token used as an access token).
    """
    try:
        claims = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise unauthorized("Invalid or expired token")
    if expected_type is not None and claims.get("type") != expected_type:
        raise unauthorized("Wrong token type")
    return claims


# ---- The "who is calling?" dependency ---------------------------------------
async def get_current_user(
    authorization: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None, alias="X-User-ID"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve the caller to a `User` row, or raise 401.

    A request proves who it is in one of two ways:
      1. **Via the gateway** — it already verified the JWT and forwarded a trusted
         `X-User-ID` header. (In production the monolith is only reachable through
         the gateway, so this header can be trusted.)
      2. **Directly** — Swagger UI, tests, or no-gateway setups send
         `Authorization: Bearer <access_token>`, which we verify here.
    """
    user_id_str: str | None = None
    if x_user_id:
        user_id_str = x_user_id
    elif authorization and authorization.lower().startswith("bearer "):
        claims = decode_token(authorization[7:].strip(), expected_type=ACCESS_TOKEN)
        user_id_str = claims.get("sub")

    if not user_id_str:
        raise unauthorized()

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise unauthorized("Invalid user id")

    user = await db.scalar(select(User).where(User.user_id == user_id))
    if user is None or not user.is_active:
        raise unauthorized("User not found or inactive")
    return user


async def get_current_user_optional(
    authorization: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None, alias="X-User-ID"),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Like `get_current_user`, but returns None instead of raising when the request
    carries no credentials. Used by public, privacy-aware read endpoints (e.g.
    GET /services/{id}): a logged-out caller still gets the redacted view.

    A *present but invalid* token is also treated as anonymous (None) rather than a
    hard 401, so a stale token never blocks a public read.
    """
    has_creds = bool(x_user_id) or bool(
        authorization and authorization.lower().startswith("bearer ")
    )
    if not has_creds:
        return None
    try:
        return await get_current_user(authorization=authorization, x_user_id=x_user_id, db=db)
    except HTTPException:
        return None
