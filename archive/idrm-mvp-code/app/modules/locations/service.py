"""Locations module service — proximity, distance, reverse-geocode, GeoJSON map layers.

Composes the spatial reads (repository) with the pure helpers (``geo``) and shapes everything as
GeoJSON for Leaflet on the web client (roadmap §13.5; PICS-LOC-003/005). Distance and
reverse-geocode need no stored data, so they run entirely on the DB-free ``geo`` helpers.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.core.exceptions import AppError
from app.modules.incidents.models import Incident
from app.modules.incidents.repository import from_point
from app.modules.locations import geo
from app.modules.locations.repository import LocationRepository
from app.modules.resources.models import Organization

_VALID_LAYERS = {"incidents", "providers"}


def _incident_feature(incident: Incident) -> dict[str, Any]:
    """Build a GeoJSON point feature for one incident (id/type/priority/status properties)."""
    latitude, longitude = from_point(incident.location)
    return geo.point_feature(
        latitude,
        longitude,
        {
            "id": str(incident.id),
            "kind": "incident",
            "service_type": incident.service_type.value,
            "priority": incident.priority.value,
            "status": incident.status.value,
        },
    )


def _organization_feature(org: Organization) -> dict[str, Any]:
    """Build a GeoJSON point feature for one provider (id/name/type/availability/radius)."""
    latitude, longitude = from_point(org.service_area_center)
    return geo.point_feature(
        latitude,
        longitude,
        {
            "id": str(org.id),
            "kind": "provider",
            "name": org.name,
            "type": org.type.value,
            "is_available": org.is_available,
            "service_radius_km": float(org.service_radius_km),
        },
    )


class LocationService:
    """Spatial queries and geo utilities that enrich incidents and organizations."""

    def __init__(self, repo: LocationRepository) -> None:
        self.repo = repo

    @staticmethod
    def distance_km(
        origin: tuple[float, float], destination: tuple[float, float]
    ) -> float:
        """Great-circle distance (km) between two points — no database needed."""
        return round(geo.haversine_km(origin[0], origin[1], destination[0], destination[1]), 3)

    @staticmethod
    def reverse_geocode(latitude: float, longitude: float) -> dict[str, Any]:
        """Offline region label for a point (built-in gazetteer, no third-party call)."""
        return geo.reverse_geocode(latitude, longitude)

    async def nearby(
        self, latitude: float, longitude: float, radius_km: float, layer: str
    ) -> dict[str, Any]:
        """GeoJSON of open incidents and/or verified providers within the radius."""
        features: list[dict[str, Any]] = []
        if layer in {"incidents", "all"}:
            features += [
                _incident_feature(i)
                for i in await self.repo.incidents_within(latitude, longitude, radius_km)
            ]
        if layer in {"providers", "all"}:
            features += [
                _organization_feature(o)
                for o in await self.repo.organizations_within(latitude, longitude, radius_km)
            ]
        return geo.feature_collection(features)

    async def map_layer(
        self, layer: str, role: str, user_id: uuid.UUID
    ) -> dict[str, Any]:
        """A full GeoJSON layer for the map (role-scoped for the incidents layer)."""
        if layer not in _VALID_LAYERS:
            raise AppError(404, "not_found", f"Unknown map layer '{layer}'.")
        if layer == "providers":
            orgs = await self.repo.verified_organizations()
            return geo.feature_collection([_organization_feature(o) for o in orgs])
        # incidents layer: citizens see only their own; providers/coordinators/admins see all open
        requester = user_id if role == "citizen" else None
        incidents = await self.repo.open_incidents(requester_id=requester)
        return geo.feature_collection([_incident_feature(i) for i in incidents])
