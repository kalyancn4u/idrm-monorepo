"""Files module repository — persist and fetch upload metadata (never the blob)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.files.models import File


class FileRepository:
    """Async data access for file metadata rows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, file: File) -> File:
        """Persist one file-metadata row (flush) and return it."""
        self.session.add(file)
        await self.session.flush()
        return file

    async def get(self, file_id: uuid.UUID) -> File | None:
        """Fetch file metadata by id, or ``None`` if absent."""
        result = await self.session.execute(select(File).where(File.id == file_id))
        return result.scalar_one_or_none()
