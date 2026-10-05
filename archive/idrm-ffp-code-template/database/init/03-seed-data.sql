-- =============================================================================
-- 03-seed-data.sql
-- PURPOSE: Load the reference / lookup data that the app expects to exist
--          before it starts serving requests.
--
-- "Seed data" means the small, fixed datasets that define valid options in
-- the system — like a list of countries, categories, or in our case,
-- disaster types. These rarely change and must exist before the app runs.
--
-- Run AFTER 02-schema.sql.
-- =============================================================================

\connect idrm_db


-- ===========================================================================
-- TABLE: disaster_types  (reference / lookup)
-- A fixed catalogue of disaster categories used to classify events.
-- severity_level: 1 (minor nuisance) → 5 (catastrophic, mass casualties)
-- ===========================================================================

CREATE TABLE IF NOT EXISTS disaster_types (
    disaster_type_id SERIAL PRIMARY KEY,
    code             VARCHAR(50) UNIQUE NOT NULL,
    name             VARCHAR(255) NOT NULL,
    description      TEXT,
    severity_level   INTEGER CHECK (severity_level BETWEEN 1 AND 5),
    is_active        BOOLEAN  DEFAULT TRUE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE disaster_types IS
    'Static reference table of disaster categories. Severity 1=minor, 5=catastrophic.';

-- Seed rows — INSERT OR IGNORE pattern so re-running this script is safe
INSERT INTO disaster_types (code, name, description, severity_level) VALUES
    ('FLOOD',      'Flood',
     'Overflow of water onto normally dry land — displaces people and damages property',         4),

    ('CYCLONE',    'Cyclone',
     'Intense tropical storm with high sustained winds and heavy rainfall',                      5),

    ('EARTHQUAKE', 'Earthquake',
     'Sudden ground shaking caused by tectonic movement — can trigger landslides and tsunamis', 5),

    ('DROUGHT',    'Drought',
     'Prolonged period of abnormally low rainfall — causes crop failure and water scarcity',     3),

    ('FIRE',       'Fire',
     'Uncontrolled fire in buildings, forests, or industrial areas',                             4),

    ('LANDSLIDE',  'Landslide',
     'Rapid downward movement of rock, soil, and debris — often triggered by rain or quakes',   4),

    ('TSUNAMI',    'Tsunami',
     'Series of large ocean waves caused by underwater earthquakes or volcanic eruptions',       5),

    ('EPIDEMIC',   'Epidemic',
     'Rapid and widespread outbreak of infectious disease in a population',                      4),

    ('OTHER',      'Other',
     'Any disaster type not listed above — add detail in the service request description',       1)

ON CONFLICT (code) DO NOTHING;  -- Safe to re-run: won't duplicate rows if they already exist


-- ===========================================================================
-- Optional: verify the seed loaded correctly
-- Uncomment these lines to inspect after running:
-- SELECT code, name, severity_level FROM disaster_types ORDER BY severity_level DESC, code;
-- ===========================================================================
