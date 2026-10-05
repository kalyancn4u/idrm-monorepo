"""API tests for the Files endpoints — upload validation, storage, and role-scoped metadata read.

Object storage is replaced with an in-memory fake (no MinIO needed); images are generated with Pillow.
"""

from __future__ import annotations

from io import BytesIO

import pytest

from app.main import app
from app.modules.files.storage import get_storage
from tests.factories import auth_user, bearer


class FakeStorage:
    """In-memory stand-in for MinIO/S3 — records puts and returns a memory URL."""

    bucket = "test-uploads"

    def __init__(self) -> None:
        self.saved: dict[str, bytes] = {}

    def put(self, key: str, data: bytes, content_type: str) -> str:
        self.saved[key] = data
        return f"memory://{self.bucket}/{key}"


@pytest.fixture
def storage():
    fake = FakeStorage()
    app.dependency_overrides[get_storage] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_storage, None)


def _noise_png(width: int = 800, height: int = 600) -> bytes:
    from PIL import Image

    img = Image.effect_noise((width, height), 128).convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def test_upload_stores_blob_and_returns_metadata(client, db, storage) -> None:
    token, uid = await auth_user(client, db, "u@ex.com", "citizen")
    resp = await client.post(
        "/api/v1/files",
        files={"file": ("p.png", _noise_png(), "image/png")},
        data={"purpose": "incident_photo"},
        headers=bearer(token),
    )
    assert resp.status_code == 201, resp.json()
    body = resp.json()
    assert body["bucket"] == "test-uploads"
    assert body["url"].startswith("memory://")
    assert body["uploaded_by"] == str(uid)
    # the blob went to (fake) object storage, not the DB
    assert len(storage.saved) == 1


async def test_invalid_content_type_rejected(client, db, storage) -> None:
    token, _ = await auth_user(client, db, "u2@ex.com", "citizen")
    resp = await client.post(
        "/api/v1/files",
        files={"file": ("note.txt", b"hello", "text/plain")},
        data={"purpose": "incident_photo"},
        headers=bearer(token),
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "invalid_file_type"


async def test_lite_path_enforces_smaller_limit(client, db, storage) -> None:
    token, _ = await auth_user(client, db, "u3@ex.com", "citizen")
    oversized = b"x" * (600 * 1024)  # > 512 KB lite cap; size is checked before processing
    resp = await client.post(
        "/api/v1/files",
        files={"file": ("big.png", oversized, "image/png")},
        data={"purpose": "incident_photo", "lite": "true"},
        headers=bearer(token),
    )
    assert resp.status_code == 413
    assert resp.json()["error"]["code"] == "file_too_large"


async def test_metadata_read_is_role_scoped(client, db, storage) -> None:
    owner, _ = await auth_user(client, db, "owner@ex.com", "citizen")
    fid = (await client.post(
        "/api/v1/files",
        files={"file": ("p.png", _noise_png(), "image/png")},
        data={"purpose": "incident_photo"},
        headers=bearer(owner),
    )).json()["id"]

    assert (await client.get(f"/api/v1/files/{fid}", headers=bearer(owner))).status_code == 200
    other, _ = await auth_user(client, db, "other@ex.com", "citizen")
    assert (await client.get(f"/api/v1/files/{fid}", headers=bearer(other))).status_code == 403
    coord, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    assert (await client.get(f"/api/v1/files/{fid}", headers=bearer(coord))).status_code == 200
