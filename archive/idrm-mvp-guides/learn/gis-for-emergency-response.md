# GIS for Emergency Response

> *Type: Guide (101 / foundational) · Audience: all stakeholders → developers · Status: MVP — current · Track: Domain (#5)*
> *IDRM is "map-driven" — location is not a detail, it's the spine. This guide takes you from "what is a map,
> really?" to the actual technology IDRM uses (coordinates, GeoJSON, PostGIS, Leaflet). The first half needs no
> technical background; the second half is the layer developers build on.*

---

## 1. Why geography is everything in a disaster

Every disaster question is a *where* question: Where is the flooding? Where are the stranded people? Where is the
nearest boat? A **GIS — Geographic Information System** — is software for capturing, storing, and analysing data
tied to locations. In emergency response, the GIS turns a list of incidents into a **picture you can act on**.

That shared picture is the **Common Operational Picture (COP)** from Disaster Management 101. IDRM's map *is* a
COP in miniature.

---

## 2. The core idea: everything has coordinates

A **coordinate** pins a point on Earth with two numbers:

- **Latitude** — how far north/south (−90 to +90).
- **Longitude** — how far east/west (−180 to +180).

Example: Mumbai ≈ `19.076° N, 72.877° E`.

To make coordinates agree worldwide, we fix a **CRS — Coordinate Reference System** (the "ruler" for the
numbers). IDRM uses the global standard **WGS 84**, known by the code **EPSG:4326** — the same system GPS and web
maps use. *Whenever you see `4326` in the codebase, it means "ordinary GPS lat/long."*

> **Order gotcha (for developers):** humans say *lat, long*; many GIS tools store *long, lat* (x, y). Getting this
> backwards drops your point in the wrong hemisphere. GeoJSON (below) is **[longitude, latitude]**.

---

## 3. GeoJSON: how locations travel over the API

**GeoJSON** is a plain-text (JSON) format for geographic shapes. The building blocks:

- **Point** — one location (an incident). `{"type":"Point","coordinates":[72.877,19.076]}`
- **LineString** — a path (a route).
- **Polygon** — an area (a flood zone, a district boundary).

IDRM sends and receives locations as GeoJSON over the `/api/v1` API, so the web map and the server always speak
the same geographic language.

---

## 4. Storing and querying places: PostGIS

IDRM's database is **PostgreSQL + PostGIS**. **PostGIS** is an extension that teaches the database to understand
*shapes*, not just numbers and text. It adds:

- **Geometry/geography columns** — store a point/line/polygon in a table row.
- **Spatial indexes (GiST)** — make "what's near here?" fast even with millions of rows.
- **Spatial functions** (`ST_*`) — e.g. `ST_DWithin` ("within N metres of"), `ST_Contains` ("inside this
  district"), `ST_Distance` ("how far apart").

**Worked example (plain English → SQL):** *"Find all high-priority incidents within 5 km of this rescue team."*

```sql
SELECT id, service_type
FROM incidents
WHERE priority = 'high'
  AND ST_DWithin(location::geography, ST_MakePoint(72.877, 19.076)::geography, 5000);
```

That single query is the kind of thing that used to need a specialist GIS server — PostGIS does it natively.
(IDRM deliberately uses **PostGIS + Python**, *not* a separate GeoServer, in the MVP.)

---

## 5. Showing it: the map in the browser

On the screen, IDRM draws maps with **Leaflet** — a lightweight JavaScript map library. Leaflet displays **tiles**
(the map background) and **markers/layers** (incidents, resources) fed by GeoJSON from the API. The MVP uses plain
Leaflet + JavaScript; the future React phase uses **React-Leaflet** (the same engine, wrapped for React).

**Accessibility note:** a map is not usable by everyone. IDRM always pairs the map with an accessible **list/table**
of the same incidents, so a screen-reader user can do the job without the map.

---

## 6. How it maps to IDRM

| GIS concept | In IDRM |
|---|---|
| Coordinate / CRS | every incident & resource has a `location` in EPSG:4326 |
| GeoJSON | the shape format on the `/api/v1` API |
| PostGIS spatial query | "incidents near me", "inside this district" |
| Leaflet map | the citizen/coordinator map view (the COP) |
| Polygon | disaster/flood zones, administrative boundaries |

---

## 7. Mastery check

You've got GIS for Emergency Response when you can:

1. Say what a **GIS** is and why location is central to disaster response.
2. Define **latitude/longitude** and **CRS**, and say what **EPSG:4326** means.
3. State the GeoJSON coordinate order and why the gotcha matters.
4. Explain what **PostGIS** adds to a normal database and give one `ST_*` example.
5. Say what **Leaflet** does and why IDRM also shows a non-map list.

---

## 8. Go deeper

- PostGIS — postgis.net/documentation · EPSG:4326 — epsg.io/4326 · GeoJSON — geojson.org
- Leaflet — leafletjs.com · React-Leaflet — react-leaflet.js.org
- IDRM data model (spatial): [`../../idrm-mvp-docs/50-data-model.md`](../../idrm-mvp-docs/50-data-model.md) ·
  modeling spoke [`../../instructions/data-modeling.md`](../../instructions/data-modeling.md)

---
*Next:* [Resource Management 101](resource-management-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
