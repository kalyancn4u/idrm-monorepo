"""Test helpers for building authenticated users of any role (not a test module)."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.resources.models import Organization, OrgType
from app.modules.users.models import User, UserRole, UserStatus

PASSWORD = "test-passphrase-123"


async def make_user(db: AsyncSession, email: str, role: str = "citizen") -> User:
    """Insert an active, verified user of the given role directly (bypasses signup limits)."""
    user = User(
        email=email,
        password_hash=hash_password(PASSWORD),
        name=f"Test {role}",
        role=UserRole(role),
        status=UserStatus.active,
        email_verified=True,
    )
    db.add(user)
    await db.commit()
    return user


async def auth_user(client: AsyncClient, db: AsyncSession, email: str, role: str = "citizen") -> tuple[str, uuid.UUID]:
    """Create a user and return (access_token, user_id)."""
    user = await make_user(db, email, role)
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    return resp.json()["access_token"], user.id


async def make_org(
    db: AsyncSession, owner_id: uuid.UUID, verified: bool = True
) -> Organization:
    """Insert an organization for a provider directly (verified by default) for test setup."""
    org = Organization(
        name="Test Relief Org",
        type=OrgType.ngo,
        owner_user_id=owner_id,
        service_categories=[],
        capacity=5,
        available_capacity=5,
        is_verified=verified,
    )
    db.add(org)
    await db.commit()
    return org


async def auth_provider_with_org(
    client: AsyncClient, db: AsyncSession, email: str, verified: bool = True
) -> tuple[str, uuid.UUID, uuid.UUID]:
    """Create a provider + its (verified) org. Returns (access_token, user_id, org_id)."""
    token, user_id = await auth_user(client, db, email, "provider")
    org = await make_org(db, user_id, verified=verified)
    return token, user_id, org.id


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
