"""Locations module router — ``/locations`` geo utilities (doc 40 §5.4).

Mounted at ``/api/v1/locations`` by ``app.main``. All outputs the map consumes are **GeoJSON**
FeatureCollections; ``distance`` and ``reverse-geocode`` are lightweight utilities available to any
authenticated role.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_claims, get_db, require_role
from app.core.rate_limit import rate_limit
from app.modules.locations.repository import LocationRepository
from app.modules.locations.schemas import (
    DistanceRequest,
    DistanceResponse,
    ReverseGeocodeResponse,
)
from app.modules.locations.service import LocationService

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]
Claims = Annotated[dict, Depends(get_current_claims)]


def _service(db: DbSession) -> LocationService:
    return LocationService(LocationRepository(db))


@router.get("/nearby", dependencies=[
    Depends(require_role("provider", "coordinator", "admin")),
    Depends(rate_limit("locations_nearby", limit=100)),
])
async def nearby(
    db: DbSession,
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    radius_km: float = Query(5.0, gt=0, le=100),
    layer: str = Query("all", pattern="^(all|incidents|providers)$"),
) -> dict:
    """Generic PostGIS proximity — open incidents and/or verified providers as GeoJSON (F3/F4)."""
    return await _service(db).nearby(latitude, longitude, radius_km, layer)


@router.post(
    "/distance",
    response_model=DistanceResponse,
    dependencies=[Depends(rate_limit("locations_distance", limit=200))],
)
async def distance(data: DistanceRequest, db: DbSession, _: Claims) -> DistanceResponse:
    """Great-circle distance in kilometres between two points."""
    km = _service(db).distance_km(
        (data.origin.latitude, data.origin.longitude),
        (data.destination.latitude, data.destination.longitude),
    )
    return DistanceResponse(distance_km=km)


@router.get(
    "/reverse-geocode",
    response_model=ReverseGeocodeResponse,
    dependencies=[Depends(rate_limit("locations_reverse_geocode", limit=100))],
)
async def reverse_geocode(
    db: DbSession,
    _: Claims,
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
) -> ReverseGeocodeResponse:
    """Coordinates → a coarse address label (offline; no third-party call — see ``geo.py``)."""
    return ReverseGeocodeResponse(**_service(db).reverse_geocode(latitude, longitude))


@router.get("/map/{layer}", dependencies=[Depends(rate_limit("locations_map", limit=200))])
async def map_layer(layer: str, db: DbSession, claims: Claims) -> dict:
    """A full GeoJSON map layer (``incidents`` or ``providers``), role-scoped."""
    return await _service(db).map_layer(layer, claims["role"], uuid.UUID(claims["sub"]))
