# IDRM Mock Data Guide
## Test Data Generation for Development, Testing & Demos

**Version**: 3.0  
**Source**: `backup/MOCK-DATA-GUIDE-v3.md`  
**Location**: `database/seeds/`  
**Last Updated**: May 30, 2026

---

## Three Data Levels

| Level | Users | Orgs | Requests | Notifications | Coverage | Load time |
|-------|-------|------|----------|---------------|----------|-----------|
| **L1 — Unit** | 10 | 3 | 25 | 50 | Single city (Hyderabad) | ~500 ms |
| **L2 — Integration** | 100 | 15 | 500 | 1 500 | 3 cities (Hyderabad, Vijayawada, Vizag) | ~5 s |
| **L3 — Full demo/UAT** | 1 500 | 50 | 8 000 | 25 000 | All of Telangana & Andhra Pradesh | ~30 s |

**Which level to use**:
- **L1** — local unit tests, fast CI runs
- **L2** — integration tests, API testing, developer development environment
- **L3** — demo to stakeholders, UAT, load testing

---

## Quick Start

```bash
# Load unit test data
psql -U idrm_user -d idrm_db -f database/seeds/mock_data_unittest.sql

# Load integration test data
psql -U idrm_user -d idrm_db -f database/seeds/mock_data_integration.sql

# Generate and load full demo data
python database/seeds/generators/generate_full_data.py > database/seeds/mock_data_full.sql
psql -U idrm_user -d idrm_db -f database/seeds/mock_data_full.sql
```

---

## Level 1 — Unit Test Data (SQL)

File: `database/seeds/mock_data_unittest.sql`

### Test user credentials

| Role | Email | Password |
|------|-------|----------|
| CITIZEN | citizen1@test.com | TestPass123! |
| CITIZEN | citizen2@test.com | TestPass123! |
| PROVIDER | provider1@test.com | TestPass123! |
| EVENT_MANAGER | coordinator1@test.com | TestPass123! |
| DM_AUTHORITY | coordinator2@test.com | TestPass123! |
| ADMIN | admin1@test.com | TestPass123! |

```sql
-- FILE: database/seeds/mock_data_unittest.sql

BEGIN;

-- Clear existing data (safe for test environments only)
TRUNCATE TABLE audit_logs, notifications, service_requests, organizations, users CASCADE;

-- ── USERS (10 total) ───────────────────────────────────────────────────────

INSERT INTO users (user_id, email, password_hash, full_name, phone, role, is_verified) VALUES
-- Citizens
('a0000001-0000-0000-0000-000000000001', 'citizen1@test.com', '$2b$12$hashedpass', 'Rajesh Kumar',    '+919876543201', 'CITIZEN',       true),
('a0000001-0000-0000-0000-000000000002', 'citizen2@test.com', '$2b$12$hashedpass', 'Priya Sharma',    '+919876543202', 'CITIZEN',       true),
('a0000001-0000-0000-0000-000000000003', 'citizen3@test.com', '$2b$12$hashedpass', 'Arjun Reddy',     '+919876543203', 'CITIZEN',       true),
('a0000001-0000-0000-0000-000000000004', 'citizen4@test.com', '$2b$12$hashedpass', 'Lakshmi Iyer',    '+919876543204', 'CITIZEN',       true),
-- Providers
('a0000001-0000-0000-0000-000000000005', 'provider1@test.com','$2b$12$hashedpass', 'Dr. Ramesh',      '+919876543205', 'PROVIDER',      true),
('a0000001-0000-0000-0000-000000000006', 'provider2@test.com','$2b$12$hashedpass', 'Nurse Kavita',    '+919876543206', 'PROVIDER',      true),
-- Coordinators
('a0000001-0000-0000-0000-000000000007', 'coordinator1@test.com','$2b$12$hashedpass', 'Suresh Coordinator', '+919876543207', 'EVENT_MANAGER', true),
('a0000001-0000-0000-0000-000000000008', 'coordinator2@test.com','$2b$12$hashedpass', 'Vijay DM Officer',   '+919876543208', 'DM_AUTHORITY',  true),
-- Admins
('a0000001-0000-0000-0000-000000000009', 'admin1@test.com',  '$2b$12$hashedpass', 'Admin User',      '+919876543209', 'ADMIN',         true),
('a0000001-0000-0000-0000-000000000010', 'admin2@test.com',  '$2b$12$hashedpass', 'Super Admin',     '+919876543210', 'ADMIN',         true);

-- ── ORGANIZATIONS (3 total) ────────────────────────────────────────────────

INSERT INTO organizations (org_id, name, org_type, service_types, contact_phone, is_verified) VALUES
('b0000001-0000-0000-0000-000000000001', 'Sion Hospital',   'HOSPITAL',    ARRAY['MEDICAL','RESCUE'],        '+919123456789', true),
('b0000001-0000-0000-0000-000000000002', 'Help India NGO',  'NGO',         ARRAY['FOOD','SHELTER','WATER'],  '+919123456790', true),
('b0000001-0000-0000-0000-000000000003', 'Fire Department', 'GOVT_AGENCY', ARRAY['RESCUE','MEDICAL'],        '+919123456791', true);

-- ── SERVICE REQUESTS (25 mixed statuses) ──────────────────────────────────

-- SUBMITTED (5)
INSERT INTO service_requests
    (service_id, requestor_id, service_type, priority, status, location, description)
VALUES
('c0000001-0000-0000-0000-000000000001', 'a0000001-0000-0000-0000-000000000001',
 'MEDICAL', 'CRITICAL', 'SUBMITTED',
 ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326),
 'Elderly man, chest pain, needs ambulance urgently'),

('c0000001-0000-0000-0000-000000000002', 'a0000001-0000-0000-0000-000000000002',
 'RESCUE', 'HIGH', 'SUBMITTED',
 ST_SetSRID(ST_MakePoint(78.4900, 17.3900), 4326),
 'Family trapped on 2nd floor, water level rising'),

('c0000001-0000-0000-0000-000000000003', 'a0000001-0000-0000-0000-000000000003',
 'FOOD', 'MEDIUM', 'SUBMITTED',
 ST_SetSRID(ST_MakePoint(78.5000, 17.4000), 4326),
 'Need food supplies for 5 people, 3 days without'),

('c0000001-0000-0000-0000-000000000004', 'a0000001-0000-0000-0000-000000000004',
 'WATER', 'HIGH', 'SUBMITTED',
 ST_SetSRID(ST_MakePoint(78.4800, 17.3800), 4326),
 'No clean water for 2 days, 8 people affected'),

('c0000001-0000-0000-0000-000000000005', 'a0000001-0000-0000-0000-000000000001',
 'SHELTER', 'HIGH', 'SUBMITTED',
 ST_SetSRID(ST_MakePoint(78.4950, 17.3950), 4326),
 'House flooded, family of 4 needs temporary shelter');

-- ACCEPTED (provider assigned)
INSERT INTO service_requests
    (service_id, requestor_id, provider_id, service_type, priority, status, location, description, accepted_at)
VALUES
('c0000001-0000-0000-0000-000000000006',
 'a0000001-0000-0000-0000-000000000002', 'b0000001-0000-0000-0000-000000000001',
 'MEDICAL', 'HIGH', 'ACCEPTED',
 ST_SetSRID(ST_MakePoint(78.4850, 17.3870), 4326),
 'Broken leg, requires immobilisation',
 CURRENT_TIMESTAMP - INTERVAL '10 minutes');

-- COMPLETED
INSERT INTO service_requests
    (service_id, requestor_id, provider_id, service_type, priority, status,
     location, description, accepted_at, completed_at)
VALUES
('c0000001-0000-0000-0000-000000000007',
 'a0000001-0000-0000-0000-000000000003', 'b0000001-0000-0000-0000-000000000003',
 'RESCUE', 'CRITICAL', 'COMPLETED',
 ST_SetSRID(ST_MakePoint(78.4880, 17.3880), 4326),
 'Rescue from rooftop — 3 people',
 CURRENT_TIMESTAMP - INTERVAL '2 hours',
 CURRENT_TIMESTAMP - INTERVAL '1 hour');

-- VERIFIED (with rating)
INSERT INTO service_requests
    (service_id, requestor_id, provider_id, service_type, priority, status,
     location, description, accepted_at, completed_at, verified_at, rating)
VALUES
('c0000001-0000-0000-0000-000000000008',
 'a0000001-0000-0000-0000-000000000001', 'b0000001-0000-0000-0000-000000000001',
 'MEDICAL', 'HIGH', 'VERIFIED',
 ST_SetSRID(ST_MakePoint(78.4870, 17.3860), 4326),
 'Fever treatment for elderly woman',
 CURRENT_TIMESTAMP - INTERVAL '3 hours',
 CURRENT_TIMESTAMP - INTERVAL '2 hours',
 CURRENT_TIMESTAMP - INTERVAL '1 hour',
 5);

COMMIT;
```

---

## Level 2 & 3 — Generated Data

Integration and full datasets are too large for hand-written SQL. Use the Python generators:

```
database/seeds/generators/
├── generate_users.py          # Generates users for any role and count
├── generate_organizations.py  # Generates orgs with realistic service types and coverage
├── generate_services.py       # Generates service requests with realistic descriptions
└── generate_full_data.py      # Combines all generators for Level 3 output
```

### Python user generator

```python
# database/seeds/generators/generate_users.py

import uuid
import random

# Indian name pool
FIRST_NAMES = ['Rajesh', 'Suresh', 'Arjun', 'Priya', 'Lakshmi', 'Kavita',
               'Vikram', 'Anjali', 'Karthik', 'Deepa', 'Ravi', 'Meena']
LAST_NAMES  = ['Kumar', 'Sharma', 'Reddy', 'Iyer', 'Patel', 'Singh', 'Nair', 'Rao']

def generate_phone():
    return f"+919{random.randint(100_000_000, 999_999_999)}"

def generate_users_sql(count: int, role: str) -> str:
    rows = []
    for i in range(count):
        uid   = str(uuid.uuid4())
        email = f"{role.lower()}{i+1}@test.com"
        name  = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        phone = generate_phone()
        rows.append(
            f"('{uid}', '{email}', '$2b$12$hashedpassword', "
            f"'{name}', '{phone}', '{role}', true)"
        )
    return (
        "INSERT INTO users (user_id, email, password_hash, full_name, phone, role, is_verified) VALUES\n"
        + ",\n".join(rows) + ";"
    )

if __name__ == '__main__':
    print("-- Citizens (70)")
    print(generate_users_sql(70, 'CITIZEN'))
    print("\n-- Providers (15)")
    print(generate_users_sql(15, 'PROVIDER'))
    print("\n-- Event Managers (10)")
    print(generate_users_sql(10, 'EVENT_MANAGER'))
    print("\n-- DM Authority (3)")
    print(generate_users_sql(3, 'DM_AUTHORITY'))
    print("\n-- Admins (2)")
    print(generate_users_sql(2, 'ADMIN'))
```

### Python service request generator

```python
# database/seeds/generators/generate_services.py

import uuid, random
from datetime import datetime, timedelta

# Hyderabad bounding box (Level 2)
BBOX = {'min_lon': 78.35, 'max_lon': 78.65, 'min_lat': 17.25, 'max_lat': 17.55}

DESCRIPTIONS = {
    'MEDICAL':  ['Elderly person with chest pain', 'Child with high fever', 'Diabetic patient needs insulin'],
    'RESCUE':   ['Family trapped on rooftop', 'Person stuck in flooded vehicle', 'Collapsed building, people inside'],
    'FOOD':     ['3-day food shortage, 6 people', 'Infant needs formula milk', 'Diabetic-friendly food needed'],
    'WATER':    ['No clean water for 48 hours', 'Well contaminated after flooding', 'Water for 10 people for 3 days'],
    'SHELTER':  ['House damaged by flood', 'Roof collapsed, needs temporary stay', 'Displaced family, 5 people'],
    'OTHER':    ['Need information on evacuation routes', 'Power outage, medical equipment offline'],
}

STATUSES = ['SUBMITTED'] * 40 + ['APPROVED'] * 20 + ['ACCEPTED'] * 15 + \
           ['IN_PROGRESS'] * 10 + ['COMPLETED'] * 10 + ['VERIFIED'] * 5

def random_point():
    lon = round(random.uniform(BBOX['min_lon'], BBOX['max_lon']), 4)
    lat = round(random.uniform(BBOX['min_lat'], BBOX['max_lat']), 4)
    return lon, lat

def generate_services_sql(count, user_ids, org_ids):
    rows = []
    for _ in range(count):
        sid    = str(uuid.uuid4())
        stype  = random.choice(['MEDICAL', 'RESCUE', 'FOOD', 'WATER', 'SHELTER', 'OTHER'])
        prio   = random.choices(['CRITICAL','HIGH','MEDIUM','LOW'], weights=[10,25,45,20])[0]
        status = random.choice(STATUSES)
        lon, lat = random_point()
        desc   = random.choice(DESCRIPTIONS[stype])
        req_id = random.choice(user_ids)
        prov   = f"'{random.choice(org_ids)}'" if status not in ('SUBMITTED', 'APPROVED') else 'NULL'

        rows.append(
            f"('{sid}', '{req_id}', {prov}, '{stype}', '{prio}', '{status}', "
            f"ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), '{desc}')"
        )
    return (
        "INSERT INTO service_requests\n"
        "    (service_id, requestor_id, provider_id, service_type, priority, status, location, description)\nVALUES\n"
        + ",\n".join(rows) + ";"
    )
```

---

## Disaster Scenario Seeds

For realistic demos, use named disaster scenario seeds. These represent specific real-world flood events with geographically clustered data.

| Scenario | Location | Requests | Focus |
|----------|----------|----------|-------|
| `scenario_flood_hyderabad.sql` | Hyderabad Old City | 120 | RESCUE + MEDICAL |
| `scenario_cyclone_vizag.sql` | Visakhapatnam coast | 250 | SHELTER + FOOD + WATER |
| `scenario_earthquake_vijayawada.sql` | Vijayawada district | 180 | RESCUE + MEDICAL + SHELTER |

```bash
# Load a specific disaster scenario on top of base data
psql -U idrm_user -d idrm_db -f database/seeds/scenarios/scenario_flood_hyderabad.sql
```

---

## Reset & Re-seed

```bash
# Full reset (drops all data, reloads schema, seeds)
psql -U idrm_user -d idrm_db << 'EOF'
TRUNCATE TABLE audit_logs, notifications, service_requests, organizations, users CASCADE;
EOF

# Then seed
psql -U idrm_user -d idrm_db -f database/seeds/mock_data_unittest.sql

# Or use the convenience Makefile target (if configured)
make db-reset-seed LEVEL=unittest
make db-reset-seed LEVEL=integration
make db-reset-seed LEVEL=full
```

---

**See also**:
- `backup/MOCK-DATA-GUIDE-v3.md` — Full data guide with complete disaster scenario SQL
- `docs/IDRM-Testing-Strategy.md` — How to use this data in test suites
- `docs/diagrams/IDRM-Database-Schema.md` — Schema reference for understanding data shape
