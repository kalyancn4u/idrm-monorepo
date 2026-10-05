"""Files module Pydantic schemas — the ``/files`` metadata response (doc 40 §5.4)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.files.models import FilePurpose


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    uploaded_by: uuid.UUID | None
    bucket: str
    object_key: str
    url: str | None
    content_type: str
    size_bytes: int
    purpose: FilePurpose
    entity_type: str | None
    entity_id: uuid.UUID | None
    created_at: datetime
