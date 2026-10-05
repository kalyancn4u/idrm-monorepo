"""Alerts module repository — persistence + area-scoped active-alert queries (PICS-ALR-002)."""

from __future__ import annotations

from datetime import datetime

from geoalchemy2.elements import WKTElement
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alerts.models import Alert
from app.modules.alerts.schemas import GeoPoint


def to_multipolygon(ring: list[GeoPoint]) -> WKTElement:
    """Build a single-ring PostGIS MULTIPOLYGON (SRID 4326) from a list of points.

    GeoJSON/WKT use ``longitude latitude`` order; the ring is closed automatically if the caller did
    not repeat the first point.
    """
    pts = [(p.longitude, p.latitude) for p in ring]
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    coords = ", ".join(f"{lng} {lat}" for lng, lat in pts)
    return WKTElement(f"MULTIPOLYGON((({coords})))", srid=4326)


class AlertRepository:
    """Async data access for coordinator alerts."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, alert: Alert) -> Alert:
        """Persist one alert (flush) and return it."""
        self.session.add(alert)
        await self.session.flush()
        return alert

    async def list_active(
        self, now: datetime, point: tuple[float, float] | None = None
    ) -> list[Alert]:
        """Active, non-expired alerts. If a point is given, only those whose area contains it
        (plus platform-wide alerts, whose ``area`` is NULL)."""
        stmt = select(Alert).where(
            Alert.active.is_(True),
            or_(Alert.expires_at.is_(None), Alert.expires_at > now),
        )
        if point is not None:
            latitude, longitude = point
            geom = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
            stmt = stmt.where(
                or_(Alert.area.is_(None), func.ST_Contains(Alert.area, geom))
            )
        stmt = stmt.order_by(Alert.created_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())
