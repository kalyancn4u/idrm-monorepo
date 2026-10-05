"""Object-storage abstraction for uploads (MinIO / S3, ADR-007; PICS-FIL-001).

The service depends on the :class:`ObjectStorage` *protocol*, not on boto3 directly, so tests can
inject an in-memory fake and production uses :class:`S3Storage`. Bytes go to MinIO; only the key and
URL are ever persisted in the database.
"""

from __future__ import annotations

from typing import Protocol

from app.core.config import Settings, get_settings


class ObjectStorage(Protocol):
    """Minimal put/url contract the files service needs (S3-compatible)."""

    bucket: str

    def put(self, key: str, data: bytes, content_type: str) -> str:
        """Store ``data`` under ``key`` and return a URL referencing it."""
        ...


class S3Storage:
    """MinIO / S3 storage via boto3. ``put`` is synchronous — call it in a threadpool."""

    def __init__(self, settings: Settings) -> None:
        import boto3  # imported lazily so the module loads without boto3 present

        self._endpoint = settings.s3_endpoint.rstrip("/")
        self.bucket = settings.s3_bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name="us-east-1",
        )

    def put(self, key: str, data: bytes, content_type: str) -> str:
        """Upload ``data`` to the bucket under ``key`` and return its public URL (synchronous)."""
        self._client.put_object(
            Bucket=self.bucket, Key=key, Body=data, ContentType=content_type
        )
        return f"{self._endpoint}/{self.bucket}/{key}"


def get_storage() -> ObjectStorage:
    """FastAPI dependency: the production S3/MinIO storage (overridden in tests)."""
    return S3Storage(get_settings())
