"""Files module service — validate, process, store uploads; fetch metadata (roadmap §13.5).

Enforces the media rules server-side (never trust the client): content-type allow-list, the 10 MB
hard limit (and the ~500 KB "lite" path), and — for images — EXIF/GPS stripping, downscale, minimum
dimensions, and a blur/quality gate. The blob goes to MinIO; only key/URL is stored (PICS-FIL-001).
"""

from __future__ import annotations

import logging
import uuid

from starlette.concurrency import run_in_threadpool

from app.core.config import Settings, get_settings
from app.core.exceptions import AppError
from app.modules.files.imaging import IMAGE_TYPES, process_image
from app.modules.files.models import File, FilePurpose
from app.modules.files.repository import FileRepository
from app.modules.files.storage import ObjectStorage

logger = logging.getLogger("idrm.files")

# content-type -> stored file extension. PDFs are stored as-is (no image processing).
_EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png", "application/pdf": "pdf"}


class FileService:
    """Upload handling and metadata retrieval."""

    def __init__(
        self,
        repo: FileRepository,
        storage: ObjectStorage | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.repo = repo
        self._storage = storage  # required for uploads; not needed for metadata reads
        self.settings = settings or get_settings()

    @property
    def storage(self) -> ObjectStorage:
        """The configured object storage; raises if the service was built for reads only."""
        if self._storage is None:  # pragma: no cover - guards a programming error
            raise RuntimeError("FileService needs object storage to upload.")
        return self._storage

    async def upload(
        self,
        *,
        raw: bytes,
        content_type: str,
        purpose: FilePurpose,
        uploaded_by: uuid.UUID | None,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        lite: bool = False,
    ) -> File:
        """Validate + process + store one upload, returning its metadata row."""
        if content_type not in _EXTENSIONS:
            raise AppError(
                400, "invalid_file_type", "Only JPEG, PNG, or PDF uploads are accepted."
            )
        max_bytes = self.settings.lite_photo_max_bytes if lite else self.settings.file_max_bytes
        if len(raw) > max_bytes:
            raise AppError(413, "file_too_large", "The uploaded file is too large.")

        # Re-process images server-side; PDFs are stored unchanged (only size/type checked).
        data = (
            await run_in_threadpool(process_image, raw, content_type, self.settings)
            if content_type in IMAGE_TYPES
            else raw
        )

        key = f"{purpose.value}/{uuid.uuid4().hex}.{_EXTENSIONS[content_type]}"
        url = await run_in_threadpool(self.storage.put, key, data, content_type)

        file = File(
            uploaded_by=uploaded_by,
            bucket=self.storage.bucket,
            object_key=key,
            url=url,
            content_type=content_type,
            size_bytes=len(data),
            purpose=purpose,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        await self.repo.add(file)
        logger.info(
            "file.upload",
            extra={"extra_fields": {"file_id": str(file.id), "purpose": purpose.value}},
        )
        return file

    async def get_for(self, file_id: uuid.UUID, user_id: uuid.UUID, role: str) -> File:
        """Fetch metadata; the uploader or a coordinator/admin may view it (role-scoped)."""
        file = await self.repo.get(file_id)
        if file is None:
            raise AppError(404, "not_found", "File not found.")
        if role not in {"coordinator", "admin"} and file.uploaded_by != user_id:
            raise AppError(403, "forbidden", "You can only view your own files.")
        return file
