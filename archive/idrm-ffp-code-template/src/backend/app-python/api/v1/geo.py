"""
api/v1/geo.py — geospatial routes (Module M4): GET /geo/nearby and GET /geo/cluster.

Public, read-only map data: only live requests (APPROVED/ACCEPTED/IN_PROGRESS) and
no requestor identity, so no authentication is required. Thin handlers delegate to
`services.geo_service`. Mounted under `/api/v1`.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.geo import ClusterResponse, NearbyResponse
from services import geo_service

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get("/nearby", response_model=NearbyResponse)
async def nearby(
    latitude: float = Query(..., ge=-90, le=90, description="Centre latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Centre longitude"),
    radius: float = Query(5, gt=0, le=50, description="Search radius in km (default 5, max 50)"),
    service_type: str | None = Query(None, description="Optional exact service-type filter"),
    db: AsyncSession = Depends(get_db),
) -> NearbyResponse:
    """Find live requests within `radius` km of a point, nearest first."""
    return await geo_service.nearby(
        db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius,
        service_type=service_type,
    )


@router.get("/cluster", response_model=ClusterResponse)
async def cluster(
    zoom: int = Query(..., ge=1, le=20, description="Map zoom level (1–20)"),
    bounds: str | None = Query(None, description="Optional viewport 'south,west,north,east'"),
    db: AsyncSession = Depends(get_db),
) -> ClusterResponse:
    """K-means clusters of live requests for a zoomed-out map view."""
    return await geo_service.cluster(db, zoom=zoom, bounds=bounds)
