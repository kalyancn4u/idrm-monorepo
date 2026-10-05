-- =============================================================================
-- 01-extensions.sql
-- PURPOSE: Enable the PostgreSQL extensions IDRM depends on.
--          Run this FIRST, before creating any tables.
--
-- What each extension does (in plain English):
--   postgis    — adds geography/geometry types and spatial functions so we can
--                store GPS coordinates and run "find things within X km" queries
--   uuid-ossp  — lets us generate universally unique IDs (UUIDs) automatically
--                as primary keys instead of auto-incrementing integers
--   pg_trgm    — enables fuzzy text search (e.g. "find users whose name is
--                similar to 'Jon'") using trigram matching
--   btree_gist — lets us build combined indexes that mix regular columns with
--                spatial/range columns (needed for some PostGIS index types)
-- =============================================================================

-- Run inside the idrm_db database
\connect idrm_db

CREATE EXTENSION IF NOT EXISTS postgis;        -- Geospatial support (points, distances, etc.)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";    -- UUID generation via gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pg_trgm;        -- Fuzzy / trigram text search
CREATE EXTENSION IF NOT EXISTS btree_gist;     -- Combined B-tree + GiST index support

-- Verify
SELECT name, default_version, installed_version
FROM pg_available_extensions
WHERE name IN ('postgis', 'uuid-ossp', 'pg_trgm', 'btree_gist')
ORDER BY name;
