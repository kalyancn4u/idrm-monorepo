"""Files module router — ``/files`` uploads to MinIO + metadata read (doc 40 §5.4).

Mounted at ``/api/v1/files`` by ``app.main``. ``POST /files`` is a multipart upload; the response
carries the ``url`` an incident (or organization) then references. Any authenticated user uploads.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_claims, get_db
from app.core.rate_limit import rate_limit
from app.modules.files.models import FilePurpose
from app.modules.files.repository import FileRepository
from app.modules.files.schemas import FileResponse
from app.modules.files.service import FileService
from app.modules.files.storage import ObjectStorage, get_storage

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]
Claims = Annotated[dict, Depends(get_current_claims)]


@router.post(
    "",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("file_upload", limit=20))],
)
async def upload_file(
    db: DbSession,
    claims: Claims,
    storage: Annotated[ObjectStorage, Depends(get_storage)],
    file: Annotated[UploadFile, File()],
    purpose: Annotated[FilePurpose, Form()],
    entity_type: Annotated[str | None, Form()] = None,
    entity_id: Annotated[uuid.UUID | None, Form()] = None,
    lite: Annotated[bool, Form()] = False,
) -> FileResponse:
    """Upload a photo/document (server re-checks size/type + processes images)."""
    raw = await file.read()
    service = FileService(FileRepository(db), storage)
    stored = await service.upload(
        raw=raw,
        content_type=file.content_type or "application/octet-stream",
        purpose=purpose,
        uploaded_by=uuid.UUID(claims["sub"]),
        entity_type=entity_type,
        entity_id=entity_id,
        lite=lite,
    )
    return FileResponse.model_validate(stored)


@router.get("/{file_id}", response_model=FileResponse,
            dependencies=[Depends(rate_limit("file_get", limit=100))])
async def get_file(file_id: uuid.UUID, db: DbSession, claims: Claims) -> FileResponse:
    """File metadata, role-scoped (uploader or coordinator/admin)."""
    service = FileService(FileRepository(db))  # reads need no object storage
    file = await service.get_for(file_id, uuid.UUID(claims["sub"]), claims["role"])
    return FileResponse.model_validate(file)
