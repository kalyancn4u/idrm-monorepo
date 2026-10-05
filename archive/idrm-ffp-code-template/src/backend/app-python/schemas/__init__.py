"""
IDRM Pydantic schemas package — request/response models for the API layer.
Grouped by domain; import what you need, e.g. `from schemas.auth import LoginRequest`.
"""
from schemas import analytics, auth, common, geo, notification, service, user

__all__ = ["analytics", "auth", "common", "geo", "notification", "service", "user"]
