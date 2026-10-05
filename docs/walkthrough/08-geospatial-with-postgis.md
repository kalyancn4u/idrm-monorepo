# Chapter 8 — Geospatial with PostGIS

*Turning "who's near me?" into a fast, correct database query.*

**By the end of this chapter you will be able to:** explain how locations are stored,
read a `ST_DWithin` proximity query, understand the pure-maths core, and say why the
reverse-geocoder is deliberately offline.

Files: [`locations/geo.py`](../../code/app/modules/locations/geo.py),
[`locations/repository.py`](../../code/app/modules/locations/repository.py),
[`locations/service.py`](../../code/app/modules/locations/service.py),
[`incidents/repository.py`](../../code/app/modules/incidents/repository.py).

---

## The database understands geography

Because **PostGIS** extends PostgreSQL with spatial types and functions, "near me",
"within radius", and "point in polygon" are answered **in the database** — over indexed
geometry — not by pulling rows into Python.[1]

An incident's `location` is a `POINT`; an alert's area is a `MULTIPOLYGON`; providers have
a service-area centre. All use **SRID 4326** (ordinary GPS latitude/longitude).[2]

> **Footnotes**
>
> - **[1]** Doing geography in the DB scales: a `GiST` spatial index lets PostGIS skip almost every row and return just the nearby ones. The alternative — load all incidents, compute distance in Python, sort — is O(everything) per request and collapses as data grows.
> - **[2]** ***SRID 4326*** = the WGS-84 coordinate system your phone's GPS uses (degrees of lat/lng). ***GiST*** (Generalized Search Tree) is the index type PostGIS uses for spatial columns. Storing a consistent SRID everywhere means distances and containment "just work."

---

## Storing a point

A helper turns lat/lng into a PostGIS point. **Watch the order:** WKT/GeoJSON are
`longitude latitude`, the opposite of how humans say "lat, long."[1]

```python
# app/modules/incidents/repository.py
def to_point(latitude: float, longitude: float) -> WKTElement:
    return WKTElement(f"POINT({longitude} {latitude})", srid=4326)   # lng first!

def from_point(geom) -> tuple[float, float]:
    shape = to_shape(geom);  return shape.y, shape.x                  # back to (lat, lng)
```

⚠️ **Pitfall:** swapping lat/lng is the classic geospatial bug — your points land in the
ocean. Centralising the conversion in `to_point`/`from_point` means the app gets it right
in exactly one place.[2]

> **Footnotes**
>
> - **[1]** ***WKT*** (Well-Known Text) is PostGIS's text form for geometry, e.g. `POINT(78.47 17.39)`. GeoJSON uses the same `[lng, lat]` order. The API, by contrast, takes human-friendly `{latitude, longitude}` — the boundary is exactly where these helpers convert.
> - **[2]** This is ***DRY*** applied to a footgun: one correct conversion, reused, beats re-deriving the order at every call site (where half will be wrong).

---

## Proximity: `ST_DWithin`, nearest first

"Open, unassigned incidents within N km, nearest first" is one query. Casting to
**geography** makes the radius true **metres** regardless of latitude:[1]

```python
# app/modules/incidents/repository.py — nearby (trimmed)
point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
distance = func.ST_Distance(func.cast(Incident.location, Geography), func.cast(point, Geography))
stmt = (select(Incident)
    .where(Incident.status.in_([created, approved]),
           func.ST_DWithin(func.cast(Incident.location, Geography),
                           func.cast(point, Geography), radius_km * 1000))   # metres
    .order_by(distance.asc()))
```

🧠 **Nuance:** `ST_DWithin` is *index-aware* — it uses the GiST index to prune, so it's
fast; `ST_Distance` then orders the survivors.[2]

> **Footnotes**
>
> - **[1]** PostGIS has two spatial types: ***geometry*** (fast, planar, units = degrees) and ***geography*** (spherical, units = metres, accurate over the globe). Casting to geography for the radius means "5 km" is really 5 km in Hyderabad and in Delhi alike — no degree-to-km fudge factor.
> - **[2]** Order matters for performance: `ST_DWithin` (a yes/no test the index accelerates) filters to a handful of rows; only those are sorted by exact `ST_Distance`. Sorting the whole table by distance would defeat the index.

---

## A pure-maths core, testable anywhere

Not everything needs the database. `locations/geo.py` holds **DB-free** helpers —
great-circle distance and GeoJSON builders — so the maths is unit-tested in isolation
(and actually runs on any machine).[1]

```python
# app/modules/locations/geo.py (trimmed)
def haversine_km(lat1, lon1, lat2, lon2) -> float: ...       # great-circle distance
def point_feature(lat, lng, properties) -> dict:             # a GeoJSON Point Feature
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lng, lat]}, "properties": properties}
def feature_collection(features) -> dict:
    return {"type": "FeatureCollection", "features": features}
```

The service uses `haversine_km` for a stateless `POST /locations/distance` (no DB needed
at all).[2]

> **Footnotes**
>
> - **[1]** Same design as `lifecycle.py` (Ch 7): pull the pure logic out so it's fast and trivial to test. `to_shape`/`WKTElement` (the DB-bound bits) stay in the repository. ***GeoJSON*** is the JSON standard for geographic features that Leaflet consumes directly.
> - **[2]** ***Haversine*** computes distance on a sphere from two lat/lng pairs — enough for a "how far apart are these?" answer without a round-trip to PostGIS. Use PostGIS when you must *search* stored geometry; use haversine for a one-off calculation.

---

## Reverse-geocoding is offline — on purpose

Turning a coordinate into a place label uses a tiny **built-in bounding-box gazetteer** —
**no third-party call**:

```python
# app/modules/locations/geo.py (trimmed)
_REGIONS = [("Telangana, India", 15.8, 19.9, 77.2, 81.4),
            ("Andhra Pradesh, India", 12.6, 19.2, 76.7, 84.8),
            ("India", 6.5, 35.7, 68.1, 97.4)]
def reverse_geocode(latitude, longitude) -> dict:            # returns a coarse region label
    ...
```

🧠 **Nuance:** this is a **deliberate MVP choice**, not laziness — it keeps the platform
free of an external dependency **and** honours DPDP by never shipping a citizen's exact
coordinates to an outside geocoder.[1]

> **Footnotes**
>
> - **[1]** **Honest scope note:** the gazetteer is coarse (region-level) and covers the seed area first. A real geocoder — an offline dataset or a self-hosted *Nominatim* — plugs in behind this same function later. What would change the decision: needing street-level labels, once a privacy-preserving (self-hosted) option is in place. ***DPDP*** = India's Digital Personal Data Protection Act 2023.

---

## Map layers for Leaflet, role-scoped

`GET /locations/map/{layer}` returns a **GeoJSON FeatureCollection** the web map draws
directly — and it is **role-scoped**: a citizen sees only their own incidents; staff see
all open ones.[1]

```python
# app/modules/locations/service.py (trimmed)
async def map_layer(self, layer, role, user_id) -> dict:
    if layer == "providers":
        return geo.feature_collection([_organization_feature(o) for o in await self.repo.verified_organizations()])
    requester = user_id if role == "citizen" else None       # citizens: own incidents only
    incidents = await self.repo.open_incidents(requester_id=requester)
    return geo.feature_collection([_incident_feature(i) for i in incidents])
```

> **Footnotes**
>
> - **[1]** Returning GeoJSON means the frontend does zero transformation — Leaflet ingests a FeatureCollection natively. Role-scoping *in the query* (not in the UI) is the safe place to do it: the server never sends a citizen data they shouldn't see, no matter what the client asks for.

---

## Recap & what's next

- **PostGIS** answers geography *in the database* over a **GiST** index; points use
  **SRID 4326**, stored `lng lat` (the classic order pitfall).
- Proximity uses **`ST_DWithin` cast to geography** (true metres), nearest-first; a
  **pure-maths core** (`geo.py`) handles DB-free distance + GeoJSON.
- Reverse-geocoding is an **offline gazetteer** (privacy + no external dependency); map
  layers are **role-scoped GeoJSON** for Leaflet.

🛠️ **Try it:** in `geo.py`, call `haversine_km(17.39, 78.47, 17.44, 78.50)` — that's two
points in Hyderabad. It runs with no database at all (it's in the unit tests).

**Next:** [Chapter 9 — Cross-Cutting: Audit · Notifications · Files](09-cross-cutting-audit-notifications-files.md),
where features gain effects without losing their purity.
