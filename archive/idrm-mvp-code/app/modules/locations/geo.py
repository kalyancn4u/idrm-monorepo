"""Pure geospatial helpers for the locations module (roadmap §13.5; PICS-LOC-*).

Kept free of any database or framework import so the maths and GeoJSON shaping are unit-testable in
isolation (the same pattern as the incidents ``lifecycle`` module). Data-backed proximity queries
(``ST_DWithin`` over stored geometry) live in the repository; this file is the DB-free core.

**Reverse-geocoding is an OFFLINE stub** — a tiny built-in bounding-box gazetteer, no third-party
call. This is a deliberate MVP choice: it keeps the platform free of an external network dependency
and honours DPDP (a citizen's exact coordinates are never shipped to a third-party geocoder). A real
geocoder (an offline dataset, or a self-hosted Nominatim) plugs in here as a future enhancement.
"""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from typing import Any

_EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lng points, in kilometres."""
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * asin(sqrt(a))


# A minimal offline gazetteer: (label, min_lat, max_lat, min_lng, max_lng). Ordered most-specific
# first. Covers the seed-data region (Telangana / Andhra Pradesh); everything else falls back to
# "India" then the generic label. Extend or replace with a real dataset in a later increment.
_REGIONS: list[tuple[str, float, float, float, float]] = [
    ("Telangana, India", 15.8, 19.9, 77.2, 81.4),
    ("Andhra Pradesh, India", 12.6, 19.2, 76.7, 84.8),
    ("India", 6.5, 35.7, 68.1, 97.4),
]


def reverse_geocode(latitude: float, longitude: float) -> dict[str, Any]:
    """Return a coarse, offline address label for a coordinate (no external call)."""
    region = next(
        (
            name
            for name, min_lat, max_lat, min_lng, max_lng in _REGIONS
            if min_lat <= latitude <= max_lat and min_lng <= longitude <= max_lng
        ),
        "Unknown area",
    )
    return {
        "latitude": latitude,
        "longitude": longitude,
        "address": f"{region} (~{latitude:.4f}, {longitude:.4f})",
        "region": region,
        "source": "offline",
    }


def point_feature(latitude: float, longitude: float, properties: dict[str, Any]) -> dict[str, Any]:
    """Build a GeoJSON Point Feature (note: GeoJSON is [longitude, latitude] order)."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [longitude, latitude]},
        "properties": properties,
    }


def feature_collection(features: list[dict[str, Any]]) -> dict[str, Any]:
    """Wrap features in a GeoJSON FeatureCollection."""
    return {"type": "FeatureCollection", "features": features}
