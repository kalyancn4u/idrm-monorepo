"""
services/geo_service.py — geospatial queries (Module M4).

Two read-only, public-safe endpoints power the map:
  • nearby  — requests within a radius of a point, nearest first. Distance is
              measured on the `geography` type (true metres on the Earth's surface,
              via ST_DWithin / ST_Distance), then converted to kilometres.
  • cluster — K-means grouping (ST_ClusterKMeans) for a zoomed-out map: one
              centroid + count + priority breakdown per cluster.

Both consider only "live" requests (APPROVED / ACCEPTED / IN_PROGRESS) and expose
no requestor identity, so they are safe to serve to the public map.

We use raw, parameterised SQL (SQLAlchemy `text()`) because these PostGIS
expressions read most clearly written out — and they mirror
docs/IDRM-Database-Query-Reference.md §Spatial. All caller-supplied values go
through bound parameters (`:name`); the only interpolated fragments are our own
constant clauses, never user input.
"""
from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.common import GeoPoint
from schemas.geo import Cluster, ClusterResponse, NearbyResponse, NearbyResult

# Requests that belong on the live map / are actionable by responders.
# (A constant literal — safe to interpolate into the SQL below.)
_ACTIVE_STATUSES = "('APPROVED', 'ACCEPTED', 'IN_PROGRESS')"


async def nearby(
    db: AsyncSession,
    *,
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    service_type: str | None = None,
    limit: int = 50,
) -> NearbyResponse:
    """Live requests within `radius_km` of (latitude, longitude), nearest first.

    `ST_DWithin(... ::geography, ... , metres)` does the radius test in true metres
    (handling the Earth's curvature); `ST_Distance` gives the metre distance, which
    we divide by 1000 for kilometres. `service_type` is an optional exact filter.
    """
    radius_km = min(max(radius_km, 0.1), 50.0)  # clamp to (0, 50] km

    params: dict = {
        "lon": longitude,
        "lat": latitude,
        "radius_m": radius_km * 1000.0,
        "limit": limit,
    }
    # Build the optional type filter as a clause (rather than a `:p IS NULL OR ...`
    # test) so we never bind an untyped NULL parameter, which asyncpg rejects.
    type_clause = ""
    if service_type:
        type_clause = " AND s.service_type = :service_type"
        params["service_type"] = service_type

    sql = text(
        f"""
        SELECT
            s.service_id,
            s.service_type,
            s.priority,
            s.status,
            s.address,
            ST_X(s.location) AS lon,
            ST_Y(s.location) AS lat,
            ST_Distance(
                s.location::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            ) / 1000.0 AS distance_km
        FROM service_requests s
        WHERE ST_DWithin(
                s.location::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                :radius_m
              )
          AND s.status IN {_ACTIVE_STATUSES}{type_clause}
        ORDER BY distance_km ASC
        LIMIT :limit
        """
    )

    result = await db.execute(sql, params)
    results = [
        NearbyResult(
            service_id=row["service_id"],
            service_type=row["service_type"],
            priority=row["priority"],
            status=row["status"],
            address=row["address"],
            location=GeoPoint(coordinates=(row["lon"], row["lat"])),
            distance_km=round(row["distance_km"], 3),
        )
        for row in result.mappings()
    ]
    return NearbyResponse(
        center=GeoPoint(coordinates=(longitude, latitude)),
        radius_km=radius_km,
        total=len(results),
        results=results,
    )


def _parse_bounds(bounds: str | None) -> dict | None:
    """Parse a `south,west,north,east` viewport string into envelope params, or None.
    Raises 400 if it isn't four numbers."""
    if not bounds:
        return None
    parts = bounds.split(",")
    if len(parts) != 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="bounds must be 'south,west,north,east'",
        )
    try:
        south, west, north, east = (float(p) for p in parts)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="bounds must be four numbers: 'south,west,north,east'",
        )
    return {"south": south, "west": west, "north": north, "east": east}


async def cluster(db: AsyncSession, *, zoom: int, bounds: str | None = None) -> ClusterResponse:
    """K-means clusters of live requests for a zoomed-out map.

    More clusters as you zoom in (a simple `zoom`-based heuristic), but never more
    than the number of candidate points (ST_ClusterKMeans needs k ≤ point count).
    An optional `south,west,north,east` viewport limits the area considered.
    """
    envelope = _parse_bounds(bounds)
    bbox_clause = ""
    params: dict = {}
    if envelope:
        # ST_MakeEnvelope(xmin, ymin, xmax, ymax, srid) = (west, south, east, north).
        bbox_clause = " AND location && ST_MakeEnvelope(:west, :south, :east, :north, 4326)"
        params.update(envelope)

    # K-means needs k ≤ number of input points, so count the candidates first.
    count = await db.scalar(
        text(f"SELECT COUNT(*) FROM service_requests WHERE status IN {_ACTIVE_STATUSES}{bbox_clause}"),
        params,
    ) or 0
    if count == 0:
        return ClusterResponse(clusters=[])

    # Heuristic: more (finer) clusters at higher zoom, capped at 50 and the point count.
    k = max(1, min(zoom * 2, 50, count))

    # `k` is our own validated integer (not user text), so it is safe to inline —
    # this also sidesteps parameter-typing quirks for ST_ClusterKMeans' 2nd argument.
    sql = text(
        f"""
        WITH clustered AS (
            SELECT
                ST_ClusterKMeans(location, {k}) OVER () AS cluster_id,
                location,
                priority
            FROM service_requests
            WHERE status IN {_ACTIVE_STATUSES}{bbox_clause}
        )
        SELECT
            cluster_id,
            COUNT(*)                                      AS count,
            ST_X(ST_Centroid(ST_Collect(location)))       AS lon,
            ST_Y(ST_Centroid(ST_Collect(location)))       AS lat,
            COUNT(*) FILTER (WHERE priority = 'CRITICAL') AS critical,
            COUNT(*) FILTER (WHERE priority = 'HIGH')     AS high,
            COUNT(*) FILTER (WHERE priority = 'MEDIUM')   AS medium,
            COUNT(*) FILTER (WHERE priority = 'LOW')      AS low
        FROM clustered
        GROUP BY cluster_id
        ORDER BY count DESC
        """
    )

    result = await db.execute(sql, params)
    clusters = [
        Cluster(
            latitude=row["lat"],
            longitude=row["lon"],
            count=row["count"],
            priority_breakdown={
                "CRITICAL": row["critical"],
                "HIGH": row["high"],
                "MEDIUM": row["medium"],
                "LOW": row["low"],
            },
        )
        for row in result.mappings()
    ]
    return ClusterResponse(clusters=clusters)
