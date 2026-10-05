"""Locations module Pydantic schemas — the ``/locations`` request/response contract (doc 40)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class DistanceRequest(BaseModel):
    """Two points to measure the great-circle distance between (F3/F4)."""

    origin: GeoPoint
    destination: GeoPoint


class DistanceResponse(BaseModel):
    distance_km: float


class ReverseGeocodeResponse(BaseModel):
    latitude: float
    longitude: float
    address: str
    region: str
    source: str
