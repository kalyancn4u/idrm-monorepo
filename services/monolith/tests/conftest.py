"""Shared test fixtures (roadmap §10.2).

Sets a test environment — a test database URL and an **ephemeral RS256 keypair** — BEFORE importing
the app, then provides per-test schema isolation, an async HTTP client, and a direct DB session.
Unit tests that request neither ``client`` nor ``db`` run without any database.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

# --- the test environment must be set BEFORE any app import (settings are cached at import) ---
_TMP = Path(tempfile.mkdtemp(prefix="idrm-test-"))


def _generate_rs256_keypair() -> None:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    (_TMP / "jwt_private.pem").write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    (_TMP / "jwt_public.pem").write_bytes(
        key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )


_generate_rs256_keypair()
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://idrm_user:test@localhost:5432/idrm_test"
)
os.environ["JWT_PRIVATE_KEY_PATH"] = str(_TMP / "jwt_private.pem")
os.environ["JWT_PUBLIC_KEY_PATH"] = str(_TMP / "jwt_public.pem")
os.environ["APP_ENV"] = "test"

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.rate_limit import reset as reset_rate_limits  # noqa: E402
from app.infrastructure.database.base import Base  # noqa: E402
from app.infrastructure.database.engine import async_session, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_rate_limits() -> None:
    """Clear the in-process rate-limit counters between tests (no DB needed)."""
    reset_rate_limits()


@pytest_asyncio.fixture
async def _schema() -> None:
    """Create a fresh schema for a test, then drop it (per-test isolation)."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db(_schema: None):
    """A direct async session for test setup/assertions."""
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(_schema: None):
    """An async HTTP client bound to the ASGI app (in-process)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
        yield http
