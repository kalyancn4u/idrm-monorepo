"""
schemas/common.py — shared Pydantic pieces used by several schema modules.
"""
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    """
    A GeoJSON Point.

    ⚠️ Coordinate order is **[longitude, latitude]** (longitude first) — this is
    the GeoJSON / PostGIS convention and the OPPOSITE of how maps usually show it.
    """
    type: Literal["Point"] = "Point"
    coordinates: tuple[float, float] = Field(..., description="[longitude, latitude]")


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """A generic paginated list response: Page[ServiceListItem], Page[UserOut], …"""
    items: list[T]
    total: int
    page: int = 1
    per_page: int = 20
    pages: int
