"""
schemas/geo.py — geospatial response shapes (mirrors CLAUDE.md §Geospatial APIs).
"""
import uuid

from pydantic import BaseModel

from dbmodels.enums import Priority, ServiceStatus, ServiceType
from schemas.common import GeoPoint


class NearbyResult(BaseModel):
    """One request found near the search point, with its straight-line distance."""

    service_id: uuid.UUID
    service_type: ServiceType
    priority: Priority
    status: ServiceStatus
    address: str | None = None
    location: GeoPoint
    distance_km: float


class NearbyResponse(BaseModel):
    """Response for GET /geo/nearby: the search center, radius, and matching requests."""

    center: GeoPoint
    radius_km: float
    total: int
    results: list[NearbyResult]


class Cluster(BaseModel):
    """A map cluster: a point, how many requests it groups, and a per-priority count."""

    latitude: float
    longitude: float
    count: int
    priority_breakdown: dict[str, int] = {}


class ClusterResponse(BaseModel):
    """Response for GET /geo/cluster: the clusters computed for the requested zoom."""

    clusters: list[Cluster]
