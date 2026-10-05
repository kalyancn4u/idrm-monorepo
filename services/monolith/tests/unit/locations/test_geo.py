"""Unit tests for the pure geo helpers (no database) — distance, gazetteer, GeoJSON shape."""

from __future__ import annotations

from app.modules.locations import geo


def test_haversine_zero_for_same_point() -> None:
    assert geo.haversine_km(17.385, 78.486, 17.385, 78.486) == 0.0


def test_haversine_known_distance_hyderabad_to_delhi() -> None:
    # Hyderabad → New Delhi is ~1250 km great-circle.
    km = geo.haversine_km(17.385, 78.486, 28.6139, 77.2090)
    assert 1200 < km < 1300


def test_reverse_geocode_matches_seed_region() -> None:
    result = geo.reverse_geocode(17.385, 78.486)
    assert result["region"] == "Telangana, India"
    assert result["source"] == "offline"
    assert "17.3850" in result["address"]


def test_reverse_geocode_outside_india_is_unknown() -> None:
    assert geo.reverse_geocode(0.0, 0.0)["region"] == "Unknown area"


def test_point_feature_uses_lng_lat_order() -> None:
    feature = geo.point_feature(17.385, 78.486, {"id": "x"})
    assert feature["geometry"]["coordinates"] == [78.486, 17.385]
    assert feature["type"] == "Feature"


def test_feature_collection_wraps_features() -> None:
    fc = geo.feature_collection([geo.point_feature(1.0, 2.0, {})])
    assert fc["type"] == "FeatureCollection"
    assert len(fc["features"]) == 1
