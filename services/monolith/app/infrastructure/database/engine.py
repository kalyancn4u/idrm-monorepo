"""The async SQLAlchemy engine and session factory (PostgreSQL + PostGIS)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_settings = get_settings()

engine = create_async_engine(_settings.database_url, pool_size=5, max_overflow=0, future=True)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
