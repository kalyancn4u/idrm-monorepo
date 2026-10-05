-- =============================================================================
-- 02-schema.sql
-- PURPOSE: Create every table, index, view, function, and trigger for IDRM.
--          Run AFTER 01-extensions.sql and BEFORE 03-seed-data.sql.
--
-- Table creation order matters because of foreign keys:
--   users → (no dependencies)
--   organizations → references users (verified_by)
--   service_requests → references users + organizations
--   notifications → references users + service_requests + organizations
--   audit_logs → references users
--   disaster_types → (no dependencies — lookup/reference table)
-- =============================================================================

\connect idrm_db

-- ===========================================================================
-- UTILITY FUNCTION
-- Called automatically by triggers below to keep updated_at current.
-- "RETURNS TRIGGER" means PostgreSQL calls this function on every row change.
-- ===========================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column IS
    'Automatically stamps updated_at to NOW() on every UPDATE. Applied via triggers on all mutable tables.';


-- ===========================================================================
-- TABLE: users
-- Stores every account: citizens who request help, providers who offer it,
-- volunteers, coordinators, and system administrators.
-- ===========================================================================

CREATE TABLE users (
    -- Primary Key — UUID is preferred over integer IDs so IDs cannot be guessed/enumerated
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Authentication
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,          -- bcrypt hash (never store plain passwords)

    -- Profile
    full_name VARCHAR(255) NOT NULL,
    phone     VARCHAR(20) UNIQUE,                 -- NULL if not provided; E.164 format (+919876543210)

    -- Role — controls what the user can see and do (canonical Permission Matrix: docs/development/IDRM-FS.md §3.3)
    -- CITIZEN: request help | VOLUNTEER: assist | ORGANIZER: lead volunteers | PROVIDER: deliver services | MANAGER: run a provider org
    -- EVENT_MANAGER: run a disaster-event instance | EXECUTIVE: org leadership (Post-MVP) | DM_AUTHORITY: approve/oversee (GO or NGO) | AUDITOR: read-only audit | ADMIN: full access
    -- ("Public" = not logged in, view-only — not a stored role.)
    role VARCHAR(50) NOT NULL DEFAULT 'CITIZEN'
        CHECK (role IN ('CITIZEN', 'VOLUNTEER', 'ORGANIZER', 'PROVIDER', 'MANAGER',
                        'EVENT_MANAGER', 'EXECUTIVE', 'DM_AUTHORITY', 'AUDITOR', 'ADMIN')),

    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,   -- TRUE after email verification link is clicked

    -- Preferences stored as JSON so we can add new settings without schema changes
    preferences JSONB NOT NULL DEFAULT '{
        "language": "en",
        "notifications": { "email": true, "sms": true, "push": false },
        "theme": "light"
    }'::jsonb,

    -- Security tracking
    email_verified_at TIMESTAMP,
    phone_verified_at TIMESTAMP,
    last_login_at     TIMESTAMP,
    last_login_ip     INET,

    -- Timestamps — updated_at is auto-maintained by the trigger below
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Inline validation constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT phone_format  CHECK (phone IS NULL OR phone ~* '^\+[1-9][0-9]{1,14}$'),
    CONSTRAINT full_name_min CHECK (char_length(full_name) >= 2)
);

COMMENT ON TABLE  users                  IS 'All user accounts (citizens, providers, coordinators, admins)';
COMMENT ON COLUMN users.password_hash    IS 'bcrypt hash, cost factor 12 — never store plaintext';
COMMENT ON COLUMN users.role             IS 'Determines permissions throughout the system';
COMMENT ON COLUMN users.preferences      IS 'Flexible JSON bag for UI/notification settings';

CREATE INDEX idx_users_email      ON users(email);
CREATE INDEX idx_users_phone      ON users(phone) WHERE phone IS NOT NULL;
CREATE INDEX idx_users_role       ON users(role);
CREATE INDEX idx_users_active     ON users(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_users_created_at ON users(created_at DESC);
CREATE INDEX idx_users_name_fts   ON users USING GIN(to_tsvector('english', full_name));

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ===========================================================================
-- TABLE: organizations
-- NGOs, hospitals, and government agencies that provide disaster relief.
-- Organizations must be verified by a DM_AUTHORITY before appearing in search.
-- ===========================================================================

CREATE TABLE organizations (
    org_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identity
    name                VARCHAR(255) NOT NULL,
    org_type            VARCHAR(50) NOT NULL
        CHECK (org_type IN ('NGO', 'HOSPITAL', 'GOVT_AGENCY', 'VOLUNTEER_GROUP')),
    registration_number VARCHAR(100) UNIQUE,

    -- Which disaster services this org provides (stored as an array)
    -- Example: ARRAY['MEDICAL', 'FOOD'] means they handle both
    service_types VARCHAR(50)[] NOT NULL
        CHECK (
            array_length(service_types, 1) > 0 AND
            service_types <@ ARRAY['RESCUE','MEDICAL','FOOD','SHELTER','WATER','OTHER']::VARCHAR[]
        ),

    -- Capacity management — tracks how many simultaneous requests they can handle
    capacity           INTEGER NOT NULL DEFAULT 10 CHECK (capacity >= 1 AND capacity <= 1000),
    available_capacity INTEGER NOT NULL DEFAULT 10
        CHECK (available_capacity >= 0 AND available_capacity <= capacity),

    -- Geographic coverage stored as JSON: {"type":"circle","center":[lon,lat],"radius_km":25}
    coverage_area JSONB NOT NULL,

    -- Contact details
    contact_person VARCHAR(255),
    contact_phone  VARCHAR(20) NOT NULL CHECK (contact_phone ~* '^\+[1-9][0-9]{1,14}$'),
    contact_email  VARCHAR(255)
        CHECK (contact_email IS NULL OR
               contact_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),

    -- Verification — only verified orgs appear in provider search results
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMP,
    verified_by UUID REFERENCES users(user_id) ON DELETE SET NULL,

    -- Supporting documents (file paths or signed URLs)
    documents JSONB DEFAULT '{}'::jsonb,

    -- Denormalised statistics — updated by triggers for fast dashboard reads
    total_services_completed    INTEGER      NOT NULL DEFAULT 0,
    average_rating              NUMERIC(3,2) DEFAULT 0.00
        CHECK (average_rating >= 0.00 AND average_rating <= 5.00),
    average_response_time_minutes INTEGER DEFAULT 0,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_stats CHECK (total_services_completed >= 0 AND average_response_time_minutes >= 0)
);

COMMENT ON TABLE  organizations                    IS 'Service-provider organisations (NGOs, hospitals, agencies)';
COMMENT ON COLUMN organizations.service_types      IS 'Array of service types this org can deliver';
COMMENT ON COLUMN organizations.available_capacity IS 'Decreases when a request is ACCEPTED; increases when COMPLETED';
COMMENT ON COLUMN organizations.coverage_area      IS 'JSON circle: {type, center:[lon,lat], radius_km}';

CREATE INDEX idx_orgs_type              ON organizations(org_type);
CREATE INDEX idx_orgs_verified          ON organizations(is_verified, org_type) WHERE is_verified = TRUE;
CREATE INDEX idx_orgs_service_types     ON organizations USING GIN(service_types);
CREATE INDEX idx_orgs_created_at        ON organizations(created_at DESC);
CREATE INDEX idx_orgs_capacity          ON organizations(available_capacity)
    WHERE available_capacity > 0 AND is_verified = TRUE;
CREATE INDEX idx_orgs_coverage_area     ON organizations USING GIN(coverage_area);

CREATE TRIGGER trg_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ===========================================================================
-- TABLE: service_requests
-- The core entity — a citizen's request for disaster relief help.
-- Status lifecycle: SUBMITTED → APPROVED → ACCEPTED → IN_PROGRESS → COMPLETED → VERIFIED
--                   Branch/terminal states → REJECTED | CANCELLED | EXPIRED | DISPUTED
--                   (Emergencies are auto-approved; DISPUTED is raised from IN_PROGRESS/COMPLETED → reassign or reject)
-- ===========================================================================

CREATE TABLE service_requests (
    service_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Who is requesting and who will serve it
    requestor_id UUID NOT NULL REFERENCES users(user_id)         ON DELETE CASCADE  ON UPDATE CASCADE,
    provider_id  UUID         REFERENCES organizations(org_id)   ON DELETE SET NULL ON UPDATE CASCADE,

    -- What kind of help is needed
    service_type VARCHAR(50) NOT NULL
        CHECK (service_type IN ('RESCUE','MEDICAL','FOOD','SHELTER','WATER','OTHER')),
    priority     VARCHAR(20) NOT NULL
        CHECK (priority IN ('CRITICAL','HIGH','MEDIUM','LOW')),

    -- Workflow status (see lifecycle comment above)
    status VARCHAR(50) NOT NULL DEFAULT 'SUBMITTED'
        CHECK (status IN ('SUBMITTED','APPROVED','ACCEPTED','IN_PROGRESS','COMPLETED','VERIFIED',
                          'REJECTED','CANCELLED','EXPIRED','DISPUTED')),

    -- Where the help is needed — PostGIS Point stores a GPS coordinate
    -- ST_MakePoint(longitude, latitude) — longitude FIRST (GeoJSON convention)
    location GEOMETRY(Point, 4326) NOT NULL,
    address  TEXT,

    -- What is needed
    description        TEXT NOT NULL
        CHECK (char_length(description) >= 10 AND char_length(description) <= 500),
    num_people_affected INTEGER NOT NULL DEFAULT 1
        CHECK (num_people_affected >= 1 AND num_people_affected <= 1000),

    -- Privacy: PUBLIC = name + details visible to all authenticated users; PROTECTED = public sees a redacted request, responders get contact via the system; PRIVATE = only requestor + assigned provider + admins
    -- Default PROTECTED (privacy-first); can only be raised, never lowered.
    privacy_level VARCHAR(20) NOT NULL DEFAULT 'PROTECTED'
        CHECK (privacy_level IN ('PUBLIC','PROTECTED','PRIVATE')),

    -- An optional phone number that overrides the requestor's profile phone for this request
    contact_phone VARCHAR(20)
        CHECK (contact_phone IS NULL OR contact_phone ~* '^\+[1-9][0-9]{1,14}$'),

    -- Timeline milestones
    accepted_at  TIMESTAMP,
    completed_at TIMESTAMP,
    verified_at  TIMESTAMP,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Requestor feedback after verification
    rating   INTEGER CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5)),
    feedback TEXT,

    -- Free-text notes at each stage
    acceptance_notes TEXT,
    completion_notes TEXT,
    rejection_reason TEXT,  -- Populated when status = 'REJECTED' (DM Authority explains why)

    -- Ensure timestamps make chronological sense
    CONSTRAINT valid_timeline_accept   CHECK (accepted_at  IS NULL OR accepted_at  >= created_at),
    CONSTRAINT valid_timeline_complete CHECK (completed_at IS NULL OR
        (completed_at >= accepted_at AND accepted_at IS NOT NULL)),
    CONSTRAINT valid_timeline_verify   CHECK (verified_at  IS NULL OR
        (verified_at  >= completed_at AND completed_at IS NOT NULL)),
    CONSTRAINT rating_requires_verify  CHECK (rating IS NULL OR
        (verified_at IS NOT NULL AND status = 'VERIFIED')),
    CONSTRAINT provider_required       CHECK (
        status NOT IN ('ACCEPTED','IN_PROGRESS','COMPLETED','VERIFIED') OR provider_id IS NOT NULL)
);

COMMENT ON TABLE  service_requests          IS 'Citizen disaster-relief requests — the core IDRM entity';
COMMENT ON COLUMN service_requests.location IS 'PostGIS Point in WGS-84 (EPSG:4326). Cast to ::geography for metre-based distance queries.';
COMMENT ON COLUMN service_requests.status   IS 'Workflow state. Progresses forward; never jumps backwards.';

-- Foreign-key indexes (PostgreSQL does not create these automatically)
CREATE INDEX idx_sr_requestor_id  ON service_requests(requestor_id);
CREATE INDEX idx_sr_provider_id   ON service_requests(provider_id);
-- Query-pattern indexes
CREATE INDEX idx_sr_status        ON service_requests(status);
CREATE INDEX idx_sr_priority      ON service_requests(priority);
CREATE INDEX idx_sr_service_type  ON service_requests(service_type);
CREATE INDEX idx_sr_created_at    ON service_requests(created_at DESC);
-- Spatial index (GiST enables fast "within X km" queries)
CREATE INDEX idx_sr_location      ON service_requests USING GIST(location);
-- Composite indexes for dashboard queries
CREATE INDEX idx_sr_status_priority   ON service_requests(status, priority);
CREATE INDEX idx_sr_status_created    ON service_requests(status, created_at DESC);
CREATE INDEX idx_sr_type_status       ON service_requests(service_type, status);
-- Partial indexes — only index the "live" rows to keep the index small
CREATE INDEX idx_sr_active            ON service_requests(created_at DESC)
    WHERE status IN ('SUBMITTED','APPROVED','ACCEPTED','IN_PROGRESS');
CREATE INDEX idx_sr_critical_active   ON service_requests(created_at DESC)
    WHERE priority = 'CRITICAL' AND status IN ('SUBMITTED','APPROVED');
-- Full-text search on description
CREATE INDEX idx_sr_description_fts   ON service_requests
    USING GIN(to_tsvector('english', description));

CREATE TRIGGER trg_service_requests_updated_at
    BEFORE UPDATE ON service_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ===========================================================================
-- TABLE: notifications
-- Every message sent to a user, regardless of delivery channel.
-- The retry_count column lets the background job know when to stop retrying.
-- ===========================================================================

CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Who receives this notification
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,

    -- What kind of event triggered it (drives the UI icon and message template)
    -- SYSTEM = platform-wide announcements (maintenance, emergency broadcasts)
    type VARCHAR(50) NOT NULL
        CHECK (type IN ('SERVICE_CREATED','SERVICE_ACCEPTED','SERVICE_COMPLETED',
                        'VERIFICATION_REQUEST','GENERAL','SYSTEM')),

    -- How it is delivered
    channel VARCHAR(20) NOT NULL
        CHECK (channel IN ('EMAIL','SMS','PUSH','IN_APP')),

    -- Message content (subject is required for EMAIL channel)
    subject VARCHAR(255),
    body    TEXT NOT NULL,

    -- Links to the entity that caused this notification (used for deep-linking in the UI)
    related_service_id UUID REFERENCES service_requests(service_id) ON DELETE CASCADE,
    related_org_id     UUID REFERENCES organizations(org_id) ON DELETE SET NULL,

    -- Delivery tracking
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING','SENT','FAILED','READ')),
    sent_at       TIMESTAMP,
    read_at       TIMESTAMP,
    error_message TEXT,
    retry_count   INTEGER NOT NULL DEFAULT 0,  -- Delivery attempts made; stop retrying after 3

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT sent_before_read        CHECK (read_at IS NULL OR (sent_at IS NOT NULL AND read_at >= sent_at)),
    CONSTRAINT email_needs_subject     CHECK (channel != 'EMAIL' OR subject IS NOT NULL)
);

COMMENT ON TABLE  notifications             IS 'All notifications sent to users across every delivery channel';
COMMENT ON COLUMN notifications.retry_count IS 'Background job increments this on each failed attempt. Max 3 before giving up.';
COMMENT ON COLUMN notifications.channel     IS 'EMAIL | SMS | PUSH | IN_APP';

CREATE INDEX idx_notif_user_id      ON notifications(user_id);
CREATE INDEX idx_notif_user_status  ON notifications(user_id, status);
CREATE INDEX idx_notif_user_unread  ON notifications(user_id, created_at DESC)
    WHERE status IN ('SENT','PENDING');
CREATE INDEX idx_notif_status       ON notifications(status);
CREATE INDEX idx_notif_channel      ON notifications(channel);
CREATE INDEX idx_notif_service      ON notifications(related_service_id) WHERE related_service_id IS NOT NULL;
CREATE INDEX idx_notif_created_at   ON notifications(created_at DESC);
CREATE INDEX idx_notif_failed_retry ON notifications(created_at)
    WHERE status = 'FAILED' AND retry_count < 3;


-- ===========================================================================
-- TABLE: audit_logs
-- Immutable record of every significant action in the system.
-- Uses BIGSERIAL (auto-incrementing integer) instead of UUID because audit
-- logs are high-volume and we want fast sequential inserts.
-- ===========================================================================

CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,

    -- Who did it
    user_id    UUID         REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    user_email VARCHAR(255),    -- Denormalised — survives even if the user account is later deleted
    user_role  VARCHAR(50),     -- Role at the time of the action

    -- What they did
    action VARCHAR(100) NOT NULL,  -- e.g. 'SERVICE_CREATED', 'SERVICE_ACCEPTED', 'ROLE_CHANGED'

    -- What they did it to
    resource_type VARCHAR(50) NOT NULL
        CHECK (resource_type IN ('User','ServiceRequest','Organization','Notification','System')),
    resource_id UUID,

    -- Context
    ip_address INET,
    user_agent TEXT,
    request_id UUID,           -- Tie together all log entries from one HTTP request for debugging

    -- What changed (JSONB lets us store any shape of before/after data)
    changes JSONB,             -- { "before": {...}, "after": {...} }

    -- Outcome
    success       BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,

    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE  audit_logs            IS 'Immutable audit trail — rows are never updated or deleted';
COMMENT ON COLUMN audit_logs.user_email IS 'Copied at write time so logs remain readable if user is deleted';
COMMENT ON COLUMN audit_logs.changes    IS 'JSON diff: {"before":{...},"after":{...}}';
COMMENT ON COLUMN audit_logs.request_id IS 'Correlates all log entries from the same HTTP request';

CREATE INDEX idx_audit_user_id         ON audit_logs(user_id);
CREATE INDEX idx_audit_action          ON audit_logs(action);
CREATE INDEX idx_audit_resource        ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_timestamp       ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_user_timestamp  ON audit_logs(user_id, timestamp DESC);
CREATE INDEX idx_audit_action_ts       ON audit_logs(action, timestamp DESC);
CREATE INDEX idx_audit_failures        ON audit_logs(timestamp DESC) WHERE success = FALSE;

-- Partitioning hint for production (uncomment and adapt when table exceeds ~10M rows):
-- CREATE TABLE audit_logs_2026_06 PARTITION OF audit_logs
--     FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');


-- ===========================================================================
-- VIEW: v_active_service_requests
-- A pre-joined view of all in-flight requests with requestor and provider info.
-- Used by dashboards and map layers to avoid repeated joins in application code.
-- ===========================================================================

CREATE VIEW v_active_service_requests AS
SELECT
    sr.service_id,
    sr.service_type,
    sr.priority,
    sr.status,
    sr.location,
    ST_X(sr.location::geometry)  AS longitude,   -- Extract longitude from PostGIS point
    ST_Y(sr.location::geometry)  AS latitude,    -- Extract latitude  from PostGIS point
    sr.address,
    sr.description,
    sr.num_people_affected,
    sr.created_at,
    sr.accepted_at,
    -- Requestor details
    u.user_id   AS requestor_id,
    u.full_name AS requestor_name,
    u.phone     AS requestor_phone,
    u.email     AS requestor_email,
    -- Provider details (NULL when not yet assigned)
    o.org_id        AS provider_id,
    o.name          AS provider_name,
    o.contact_phone AS provider_phone,
    -- How long the request has been waiting (minutes)
    EXTRACT(EPOCH FROM (COALESCE(sr.accepted_at, NOW()) - sr.created_at)) / 60 AS wait_time_minutes
FROM service_requests sr
INNER JOIN users         u ON sr.requestor_id = u.user_id
LEFT  JOIN organizations o ON sr.provider_id  = o.org_id
WHERE sr.status IN ('SUBMITTED','APPROVED','ACCEPTED','IN_PROGRESS');

COMMENT ON VIEW v_active_service_requests IS
    'All in-flight service requests with requestor and provider details pre-joined. Refresh on dashboard load.';


-- ===========================================================================
-- VIEW: v_organization_stats
-- Aggregated performance metrics per organisation.
-- Used by the admin dashboard and provider-matching algorithm.
-- ===========================================================================

CREATE VIEW v_organization_stats AS
SELECT
    o.org_id,
    o.name,
    o.org_type,
    o.is_verified,
    o.capacity,
    o.available_capacity,
    COUNT(sr.service_id)                                                     AS total_services,
    COUNT(sr.service_id) FILTER (WHERE sr.status = 'COMPLETED')             AS completed_services,
    COUNT(sr.service_id) FILTER (WHERE sr.status = 'VERIFIED')              AS verified_services,
    COALESCE(AVG(sr.rating) FILTER (WHERE sr.rating IS NOT NULL), 0)        AS average_rating,
    COALESCE(
        AVG(EXTRACT(EPOCH FROM (sr.accepted_at  - sr.created_at))  / 60)
        FILTER (WHERE sr.accepted_at IS NOT NULL), 0
    )                                                                        AS avg_acceptance_time_minutes,
    COALESCE(
        AVG(EXTRACT(EPOCH FROM (sr.completed_at - sr.accepted_at)) / 60)
        FILTER (WHERE sr.completed_at IS NOT NULL), 0
    )                                                                        AS avg_completion_time_minutes,
    o.created_at
FROM organizations o
LEFT JOIN service_requests sr ON o.org_id = sr.provider_id
GROUP BY o.org_id, o.name, o.org_type, o.is_verified, o.capacity, o.available_capacity, o.created_at;

COMMENT ON VIEW v_organization_stats IS
    'Per-org performance metrics (counts, ratings, response times). Used by admin dashboards and matching.';


-- ===========================================================================
-- FUNCTION: calculate_distance_km
-- Utility: straight-line distance between two GPS points in kilometres.
-- Uses PostGIS geography type so the result is in metres (divided by 1000).
-- ===========================================================================

CREATE OR REPLACE FUNCTION calculate_distance_km(
    lon1 NUMERIC, lat1 NUMERIC,
    lon2 NUMERIC, lat2 NUMERIC
)
RETURNS NUMERIC AS $$
BEGIN
    -- ::geography cast makes ST_Distance return metres (not degrees)
    RETURN ST_Distance(
        ST_SetSRID(ST_Point(lon1, lat1), 4326)::geography,
        ST_SetSRID(ST_Point(lon2, lat2), 4326)::geography
    ) / 1000;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_distance_km IS
    'Returns kilometre distance between two lon/lat points using PostGIS geography (metres ÷ 1000).';


-- ===========================================================================
-- FUNCTION: get_nearby_providers
-- Finds verified organisations within a given radius that can handle a
-- specific service type and still have available capacity.
-- Called by the provider-matching module when a request is APPROVED.
-- ===========================================================================

CREATE OR REPLACE FUNCTION get_nearby_providers(
    search_lon         NUMERIC,
    search_lat         NUMERIC,
    search_radius_km   NUMERIC  DEFAULT 50,
    search_service_type VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    org_id             UUID,
    name               VARCHAR,
    org_type           VARCHAR,
    distance_km        NUMERIC,
    available_capacity INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.org_id,
        o.name,
        o.org_type,
        -- Distance from search point to org's coverage centre (in km)
        ST_Distance(
            ST_SetSRID(ST_Point(search_lon, search_lat), 4326)::geography,
            ST_SetSRID(
                ST_Point(
                    (o.coverage_area->'center'->>0)::NUMERIC,   -- longitude from JSON
                    (o.coverage_area->'center'->>1)::NUMERIC    -- latitude  from JSON
                ), 4326
            )::geography
        ) / 1000 AS distance_km,
        o.available_capacity
    FROM organizations o
    WHERE o.is_verified = TRUE
      AND o.available_capacity > 0
      AND (search_service_type IS NULL OR search_service_type = ANY(o.service_types))
      AND ST_DWithin(
            ST_SetSRID(ST_Point(search_lon, search_lat), 4326)::geography,
            ST_SetSRID(
                ST_Point(
                    (o.coverage_area->'center'->>0)::NUMERIC,
                    (o.coverage_area->'center'->>1)::NUMERIC
                ), 4326
            )::geography,
            search_radius_km * 1000   -- convert km to metres for ST_DWithin
          )
    ORDER BY distance_km ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_nearby_providers IS
    'Returns verified providers within radius_km that serve the given service_type, ordered by distance.';


-- ===========================================================================
-- TRIGGER FUNCTION: update_organization_stats
-- Fires after a service_request row changes status.
-- Keeps the denormalised capacity and rating columns on organisations in sync
-- without requiring the application layer to remember to do it.
-- ===========================================================================

CREATE OR REPLACE FUNCTION update_organization_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- When a provider accepts a request: decrease their available capacity
    IF NEW.status = 'ACCEPTED' AND OLD.status IN ('SUBMITTED','APPROVED') THEN
        UPDATE organizations
        SET available_capacity = GREATEST(0, available_capacity - 1)
        WHERE org_id = NEW.provider_id;
    END IF;

    -- When a service is completed: free up one capacity slot and increment the counter
    IF NEW.status = 'COMPLETED' AND OLD.status != 'COMPLETED' THEN
        UPDATE organizations
        SET total_services_completed = total_services_completed + 1,
            -- LEAST(capacity, ...) prevents available_capacity from exceeding total capacity
            available_capacity = LEAST(capacity, available_capacity + 1)
        WHERE org_id = NEW.provider_id;
    END IF;

    -- When a completed service is verified and rated: recalculate average rating
    IF NEW.status = 'VERIFIED' AND OLD.status = 'COMPLETED' AND NEW.rating IS NOT NULL THEN
        UPDATE organizations
        SET average_rating = (
            SELECT COALESCE(AVG(rating), 0)
            FROM service_requests
            WHERE provider_id = NEW.provider_id AND rating IS NOT NULL
        )
        WHERE org_id = NEW.provider_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_organization_stats
    AFTER UPDATE ON service_requests
    FOR EACH ROW EXECUTE FUNCTION update_organization_stats();


-- ===========================================================================
-- TRIGGER FUNCTION: audit_service_request_changes
-- Fires after every INSERT and status-changing UPDATE on service_requests.
-- Writes a row to audit_logs so there is an immutable trail of all changes.
-- ===========================================================================

CREATE OR REPLACE FUNCTION audit_service_request_changes()
RETURNS TRIGGER AS $$
DECLARE
    v_actor_id    UUID;
    v_actor_email VARCHAR(255);
    v_action      VARCHAR(100);
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- New request created by the citizen (requestor)
        INSERT INTO audit_logs (user_id, user_email, action, resource_type, resource_id, changes)
        VALUES (
            NEW.requestor_id,
            (SELECT email FROM users WHERE user_id = NEW.requestor_id),
            'SERVICE_CREATED',
            'ServiceRequest',
            NEW.service_id,
            jsonb_build_object('after', row_to_json(NEW))
        );

    ELSIF TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN
        -- Status changed — log who made the change and what it changed to
        -- The actor is the provider for acceptance, otherwise the requestor
        v_actor_id := COALESCE(NEW.provider_id::UUID, NEW.requestor_id);

        SELECT email INTO v_actor_email FROM users WHERE user_id = v_actor_id;

        v_action := CASE NEW.status
            WHEN 'ACCEPTED'    THEN 'SERVICE_ACCEPTED'
            WHEN 'IN_PROGRESS' THEN 'SERVICE_IN_PROGRESS'
            WHEN 'COMPLETED'   THEN 'SERVICE_COMPLETED'
            WHEN 'VERIFIED'    THEN 'SERVICE_VERIFIED'
            WHEN 'REJECTED'    THEN 'SERVICE_REJECTED'
            WHEN 'CANCELLED'   THEN 'SERVICE_CANCELLED'
            ELSE                    'SERVICE_UPDATED'
        END;

        INSERT INTO audit_logs (
            user_id, user_email, action, resource_type, resource_id, changes
        )
        VALUES (
            v_actor_id,
            v_actor_email,
            v_action,
            'ServiceRequest',
            NEW.service_id,
            jsonb_build_object(
                'before',         row_to_json(OLD),
                'after',          row_to_json(NEW),
                'changed_fields', jsonb_build_object('status', NEW.status)
            )
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_service_requests
    AFTER INSERT OR UPDATE ON service_requests
    FOR EACH ROW EXECUTE FUNCTION audit_service_request_changes();
