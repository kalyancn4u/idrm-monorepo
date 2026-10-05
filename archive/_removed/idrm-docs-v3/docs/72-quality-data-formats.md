> *Type: Document (specification) · Audience: Developers, integrators · Status: Archived — v3 historical generation*

# IDRM: Data Formats & Structures Guide

<!-- IDRM-CLEANUP doc=v3-72-dataformats status=ANNOTATED pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — data formats → `docs/mvp/40` + `50` (+ new PICS row)
> Request/response + data-structure formats → canonical [`../../../../docs/mvp/40-api-specification.md`](../../../../docs/mvp/40-api-specification.md)
> (+ OpenAPI) and schema `docs/mvp/50`. **New conformance row added from this doc:** `PICS-STK-OPENAPI-01`
> (OpenAPI spec validated) in `docs/mvp/26`. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Complete Reference for JSON, API Payloads, and Data Types

**Version**: 3.0 Consolidated  
**Audience**: Developers & Complete Beginners  
**Reading Time**: 45-60 minutes  
**Last Updated**: May 16, 2026

---

## 📚 **Table of Contents**

1. [What Are Data Formats?](#1-what-are-data-formats)
2. [Understanding JSON](#2-understanding-json)
3. [Common Data Types](#3-common-data-types)
4. [Authentication Formats](#4-authentication-formats)
5. [Service Request Formats](#5-service-request-formats)
6. [User & Organization Formats](#6-user--organization-formats)
7. [Geospatial Formats](#7-geospatial-formats)
8. [Analytics Formats](#8-analytics-formats)
9. [Error Response Formats](#9-error-response-formats)
10. [Quick Reference Tables](#10-quick-reference-tables)
11. [Best Practices](#11-best-practices)
12. [Common Mistakes to Avoid](#12-common-mistakes-to-avoid)

---

## 1. **What Are Data Formats?**

### 1.1 The Simple Explanation

**Data formats** are like the "language" computers use to talk to each other. Just like humans need to speak the same language to communicate, computers need to agree on how to structure and send information.

### 1.2 Real-World Analogy

Think of sending a letter:

```
Traditional Letter:
┌─────────────────────┐
│ To: John Doe        │ ← Recipient
│ Address: 123 Street │ ← Location
│ Subject: Hello      │ ← Topic
│                     │
│ Dear John,          │ ← Content
│ How are you?        │
└─────────────────────┘

JSON (Computer Letter):
{
  "to": "John Doe",
  "address": "123 Street",
  "subject": "Hello",
  "content": "Dear John, How are you?"
}
```

**Both convey the same information, but in different formats!**

### 1.3 Why This Matters in IDRM

In IDRM, when:
- A **user creates a service request** → Their browser sends JSON to the server
- The **server saves to database** → It converts JSON to database format
- The **map displays requests** → Server sends JSON back to browser
- An **error occurs** → Server sends error JSON to explain what went wrong

**Everyone speaks JSON!** 🗣️

---

## 2. **Understanding JSON**

### 2.1 What is JSON?

**JSON** = **J**ava**S**cript **O**bject **N**otation

It's a way to write data that both humans and computers can read easily.

### 2.2 JSON Basics for Complete Beginners

**JSON has only 6 building blocks**:

#### Building Block 1: Objects (Containers)
```json
{
  "name": "John",
  "age": 30
}
```
Think of it as a **labeled box** containing related information.

#### Building Block 2: Arrays (Lists)
```json
[
  "apple",
  "banana",
  "orange"
]
```
Think of it as a **numbered list** of items.

#### Building Block 3: Strings (Text)
```json
"Hello, World!"
```
Any text, wrapped in quotes.

#### Building Block 4: Numbers
```json
42
3.14159
-10
```
No quotes needed! Just the number.

#### Building Block 5: Booleans (True/False)
```json
true
false
```
Only two options: `true` or `false` (no quotes).

#### Building Block 6: Null (Nothing)
```json
null
```
Represents "no value" or "unknown".

### 2.3 Combining Building Blocks

**Real IDRM Example - Service Request**:
```json
{
  "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
  "service_type": "MEDICAL",
  "priority": "CRITICAL",
  "description": "Urgent medical attention needed",
  "location": {
    "latitude": 17.3850,
    "longitude": 78.4867
  },
  "is_verified": false,
  "assigned_provider": null,
  "created_at": "2026-05-16T10:45:00Z"
}
```

**Breaking it down**:
- `service_id`: **String** (text identifier)
- `service_type`: **String** (category)
- `priority`: **String** (urgency level)
- `description`: **String** (details)
- `location`: **Object** (nested container with lat/lng)
  - `latitude`: **Number** (17.3850)
  - `longitude`: **Number** (78.4867)
- `is_verified`: **Boolean** (false = not yet verified)
- `assigned_provider`: **Null** (nobody assigned yet)
- `created_at`: **String** (timestamp)

**That's JSON! Not so scary, right?** 😊

---

## 3. **Common Data Types**

### 3.1 UUID (Unique Identifiers)

**What is a UUID?**

A UUID (Universally Unique IDentifier) is like a **super-long serial number** that guarantees no two items will ever have the same ID.

**Format**:
```
a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Pattern**: `8-4-4-4-12` characters separated by hyphens

**Example in IDRM**:
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
  "organization_id": "o1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Why UUIDs?**
- ✅ **Unique across entire system** (never duplicate)
- ✅ **Generated anywhere** (frontend, backend, database)
- ✅ **No collisions** (safe to create without checking existing IDs)

**Beginner Tip**: Think of UUIDs like **fingerprints** - every person (record) has a unique one that never changes!

---

### 3.2 Timestamps (Dates & Times)

**Format**: ISO 8601 Standard

```json
{
  "created_at": "2026-05-16T10:45:00Z",
  "updated_at": "2026-05-16T11:30:00.123Z"
}
```

**Breaking it down**:
```
2026-05-16  T  10:45:00  .123  Z
    │       │      │       │    │
    │       │      │       │    └─ Timezone (Z = UTC)
    │       │      │       └────── Milliseconds (optional)
    │       │      └────────────── Time (24-hour format)
    │       └───────────────────── Separator
    └───────────────────────────── Date (YYYY-MM-DD)
```

**Why this format?**
- ✅ **Unambiguous** (no confusion about DD/MM vs MM/DD)
- ✅ **Sortable** (can sort alphabetically and it works!)
- ✅ **Standard** (works everywhere: Python, JavaScript, databases)

**Example**:
```json
{
  "created_at": "2026-05-16T10:45:00Z",
  "meaning": "Created on May 16, 2026 at 10:45 AM UTC"
}
```

---

### 3.3 GeoJSON Point (Location Coordinates)

**What is GeoJSON?**

A standard way to represent **locations** and **shapes** on maps.

**CRITICAL**: GeoJSON uses **[longitude, latitude]** order (NOT [lat, lng]!)

**Format**:
```json
{
  "location": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]
  }
}
```

**Breaking it down**:
```json
{
  "type": "Point",              // ← Type of geometry
  "coordinates": [
    78.4867,                    // ← Longitude (FIRST!)
    17.3850                     // ← Latitude (SECOND!)
  ]
}
```

**Real-World Example - Hyderabad, India**:
```json
{
  "service_id": "abc123",
  "address": "Charminar, Hyderabad",
  "location": {
    "type": "Point",
    "coordinates": [78.4747, 17.3616]
  }
}
```

**Constraints for India**:
- Longitude: `68.0` to `97.0` (West to East)
- Latitude: `6.0` to `35.0` (South to North)

**Beginner Tip**: Remember **"LONG-LAT"** - Longitude comes first, just like how "long" comes before "lat" alphabetically!

---

### 3.4 Enumeration Values (Fixed Choices)

**What are Enums?**

Enums are like **multiple-choice questions** - you can only pick from a pre-defined list.

#### ServiceType (What kind of help is needed?)
```json
[
  "MEDICAL",         // 🏥 Doctors, ambulances, medicine
  "FOOD",            // 🍲 Meals, water, groceries
  "SHELTER",         // 🏠 Temporary housing, tents
  "RESCUE",          // 🚁 Search and rescue operations
  "SANITATION",      // 🚿 Toilets, cleaning, hygiene
  "COMMUNICATION",   // 📡 Phones, internet, connectivity
  "TRANSPORT",       // 🚗 Vehicles, fuel, logistics
  "PSYCHOSOCIAL",    // 🧠 Counseling, mental health
  "LEGAL",           // ⚖️ Legal aid, documentation
  "OTHER"            // 🔧 Anything else
]
```

#### PriorityLevel (How urgent is it?)
```json
[
  "CRITICAL",        // 🔴 Life-threatening - respond NOW
  "HIGH",            // 🟠 Urgent - respond within hours
  "MEDIUM",          // 🟡 Important - respond within a day
  "LOW"              // 🟢 Can wait - respond when possible
]
```

#### ServiceStatus (What's happening with this request?)
```json
[
  "SUBMITTED",       // 📝 Just created, awaiting review
  "UNDER_REVIEW",    // 👀 Being reviewed by coordinator
  "APPROVED",        // ✅ Approved, looking for provider
  "REJECTED",        // ❌ Cannot be fulfilled
  "ASSIGNED",        // 👤 Provider assigned
  "IN_PROGRESS",     // 🚀 Provider is on the way / working
  "COMPLETED",       // ✔️ Service delivered
  "VERIFIED",        // ⭐ Requestor confirmed completion
  "CANCELLED",       // 🚫 Request cancelled
  "DISPUTED"         // ⚠️ Problem reported
]
```

#### UserRole (What can this person do?)
```json
[
  "SYSTEM_ADMIN",     // 👑 Full system access
  "DM_AUTHORITY",     // 🏛️ District Magistrate / Government official
  "ORG_ADMIN",        // 🏢 Organization administrator
  "EVENT_MANAGER",    // 📋 Manages specific disaster events
  "SERVICE_PROVIDER", // 🚑 Delivers services
  "VOLUNTEER",        // 🙋 Helps coordinate
  "CITIZEN",          // 👤 Regular user (requests services)
  "AUDITOR"           // 🔍 Reviews system for compliance
]
```

**Why Enums?**
- ✅ **Prevents typos** (no "MEDEICAL" vs "MEDICAL")
- ✅ **Consistent** (everyone uses same terms)
- ✅ **Validatable** (backend rejects invalid values)

---

## 4. **Authentication Formats**

### 4.1 User Registration

**When does this happen?**

When a new user signs up for IDRM for the first time.

**Request** (What the browser sends):
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "phone": "9876543210",
  "role": "CITIZEN"
}
```

**Field Constraints**:

| Field | Rules | Example | Why? |
|-------|-------|---------|------|
| `email` | Valid email, max 255 chars, unique | `john@example.com` | Must be real email for verification |
| `password` | Min 8 chars, 1 upper, 1 lower, 1 number | `SecurePass123!` | Security requirement |
| `full_name` | Max 255 chars | `John Doe` | Human-readable name |
| `phone` | Exactly 10 digits (Indian mobile) | `9876543210` | For SMS notifications |
| `role` | `CITIZEN` or `SERVICE_PROVIDER` only | `CITIZEN` | Other roles require admin approval |

**Response** (What the server sends back):
```json
{
  "status": "success",
  "message": "Verification email sent to john@example.com",
  "data": {
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "CITIZEN",
    "is_verified": false,
    "created_at": "2026-05-16T10:30:00Z"
  }
}
```

**What happens next?**
1. User receives verification email
2. User clicks verification link
3. Account becomes active
4. User can log in

---

### 4.2 User Login

**When does this happen?**

When an existing user wants to access their account.

**Request**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response** (Success):
```json
{
  "status": "success",
  "data": {
    "user": {
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "email": "john@example.com",
      "full_name": "John Doe",
      "role": "CITIZEN",
      "organization_id": null
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 900,
    "token_type": "Bearer"
  }
}
```

**Understanding Tokens**:

```
access_token = "Your temporary key card"
├── Valid for: 15 minutes (900 seconds)
├── Use for: Every API request
└── Like: A day-pass to a building

refresh_token = "Your permanent key to get new day-passes"
├── Valid for: 7 days
├── Use for: Getting new access tokens when expired
└── Like: Your ID card that gets you a new day-pass
```

**Token Usage Example**:

```javascript
// Making an API request with access token
fetch('https://api.idrm.gov.in/services', {
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
    'Content-Type': 'application/json'
  }
})
```

---

### 4.3 Token Refresh

**When does this happen?**

When your access token expires (after 15 minutes) but your refresh token is still valid.

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "access_token": "new_access_token_here...",
    "refresh_token": "new_refresh_token_here...",
    "expires_in": 900,
    "token_type": "Bearer"
  }
}
```

**Beginner Tip**: Think of token refresh like renewing a library card - you show your old card to get a new one without having to re-apply from scratch!

---

## 5. **Service Request Formats**

### 5.1 Creating a Service Request

**When does this happen?**

When someone needs emergency help during a disaster.

**Request**:
```json
{
  "service_type": "MEDICAL",
  "priority": "CRITICAL",
  "location": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]
  },
  "address": "Charminar, Hyderabad, Telangana 500002",
  "description": "Urgent medical attention needed for elderly person with chest pain. Patient is 75 years old, experiencing severe chest pain and shortness of breath.",
  "privacy_level": "PROTECTED",
  "disaster_event_id": null,
  "metadata": {
    "patient_age": 75,
    "symptoms": ["chest pain", "shortness of breath"],
    "medical_history": "diabetes, hypertension"
  }
}
```

**Field Explanations**:

| Field | What It Means | Example |
|-------|---------------|---------|
| `service_type` | Category of help needed | `MEDICAL` |
| `priority` | How urgent is it? | `CRITICAL` = life-threatening |
| `location` | Exact GPS coordinates | `[78.4867, 17.3850]` |
| `address` | Human-readable location | "Charminar, Hyderabad" |
| `description` | Detailed explanation | "Elderly person needs medical help..." |
| `privacy_level` | Who can see this? | `PROTECTED` = only authorized responders |
| `disaster_event_id` | Related to specific disaster? | `null` = not associated with an event |
| `metadata` | Extra details (optional) | Age, symptoms, medical history |

**Response** (Success):
```json
{
  "status": "success",
  "message": "Service request created successfully",
  "data": {
    "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "status": "APPROVED",
    "created_at": "2026-05-16T10:45:00Z",
    "estimated_response_time": "30 minutes",
    "next_action": "Provider is being assigned automatically"
  }
}
```

**What happens next?**
1. Request appears on map with red marker (CRITICAL)
2. System looks for nearby medical providers
3. Provider accepts and gets assigned
4. Requester gets notification with provider details

---

### 5.2 Complete Service Request Object

**What you get when fetching a service request**:

```json
{
  "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
  "requestor_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "service_type": "MEDICAL",
  "priority": "CRITICAL",
  "location": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]
  },
  "address": "Charminar, Hyderabad, Telangana 500002",
  "description": "Urgent medical attention needed...",
  "privacy_level": "PROTECTED",
  "status": "IN_PROGRESS",
  "assigned_to": {
    "user_id": "p1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "full_name": "Dr. Rajesh Kumar",
    "organization": {
      "org_id": "o1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "City Hospital",
      "type": "GOVERNMENT"
    },
    "phone": "9999999999",
    "current_location": {
      "type": "Point",
      "coordinates": [78.4900, 17.3900]
    },
    "estimated_arrival": "2026-05-16T11:15:00Z"
  },
  "disaster_event_id": null,
  "estimated_completion": "2026-05-16T12:00:00Z",
  "completed_at": null,
  "verified_at": null,
  "rating": null,
  "proof_photo_url": null,
  "created_at": "2026-05-16T10:45:00Z",
  "updated_at": "2026-05-16T11:00:00Z",
  "metadata": {
    "patient_age": 75,
    "symptoms": ["chest pain", "shortness of breath"]
  }
}
```

**Lifecycle States**:
```
SUBMITTED → APPROVED → ASSIGNED → IN_PROGRESS → COMPLETED → VERIFIED
```

---

### 5.3 Listing Service Requests (with Filters)

**Request** (via URL parameters):
```
GET /api/v1/services?service_type=MEDICAL&priority=CRITICAL&status=APPROVED&limit=20
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "services": [
      {
        "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
        "service_type": "MEDICAL",
        "priority": "CRITICAL",
        "status": "APPROVED",
        "location": {
          "type": "Point",
          "coordinates": [78.4867, 17.3850]
        },
        "address": "Charminar, Hyderabad",
        "created_at": "2026-05-16T10:45:00Z",
        "requestor_name": "John Doe"
      },
      {
        "service_id": "e8d7c6b5-a4b3-2109-fedc-ba9876543211",
        "service_type": "MEDICAL",
        "priority": "CRITICAL",
        "status": "APPROVED",
        "location": {
          "type": "Point",
          "coordinates": [78.4900, 17.3900]
        },
        "address": "Mehdipatnam, Hyderabad",
        "created_at": "2026-05-16T10:30:00Z",
        "requestor_name": "Jane Smith"
      }
    ],
    "pagination": {
      "total": 45,
      "page": 1,
      "limit": 20,
      "pages": 3
    }
  }
}
```

**Available Filters**:
- `service_type`: Filter by service category
- `priority`: Filter by urgency
- `status`: Filter by current state
- `disaster_event_id`: Filter by disaster event
- `bbox`: Geographic bounding box (map area)
- `limit`: Number of results per page
- `page`: Which page of results

---

## 6. **User & Organization Formats**

### 6.1 User Profile Object

**What information we store about each user**:

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "john@example.com",
  "full_name": "John Doe",
  "phone": "9876543210",
  "role": "CITIZEN",
  "organization_id": null,
  "organization": null,
  "is_active": true,
  "is_verified": true,
  "last_login": "2026-05-16T09:00:00Z",
  "created_at": "2026-05-01T10:30:00Z",
  "updated_at": "2026-05-16T09:00:00Z"
}
```

**Privacy Levels**:
- ✅ **Public info**: `full_name`, `organization`, `role`
- 🔒 **Private info**: `email`, `phone` (only visible to authorized users)
- 🔐 **Never shared**: `password` (encrypted, never sent in API)

---

### 6.2 Organization Object

**What information we store about organizations**:

```json
{
  "org_id": "o1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Red Cross Hyderabad",
  "type": "NGO",
  "registration_number": "FCRA-2020-0001234",
  "address": "Road No 12, Banjara Hills, Hyderabad, Telangana 500034",
  "location": {
    "type": "Point",
    "coordinates": [78.4500, 17.4200]
  },
  "contact_email": "contact@redcross-hyd.org",
  "contact_phone": "04012345678",
  "description": "Humanitarian organization providing emergency relief and disaster response services across Telangana state.",
  "service_types": ["MEDICAL", "FOOD", "SHELTER"],
  "coverage_area": {
    "type": "Polygon",
    "coordinates": [
      [
        [78.0, 17.0],
        [79.0, 17.0],
        [79.0, 18.0],
        [78.0, 18.0],
        [78.0, 17.0]
      ]
    ]
  },
  "is_verified": true,
  "verified_at": "2026-05-01T12:00:00Z",
  "created_at": "2026-04-15T10:00:00Z",
  "updated_at": "2026-05-16T08:30:00Z",
  "metadata": {
    "certification": "ISO 9001:2015",
    "capacity": "100 personnel",
    "equipment": ["ambulances", "medical kits", "tents"]
  }
}
```

**Organization Types**:
- `NGO`: Non-Governmental Organization
- `GOVERNMENT`: Government agency
- `INTERNATIONAL_ORG`: UN, Red Cross, etc.
- `PRIVATE`: Private company providing services

---

## 7. **Geospatial Formats**

### 7.1 GeoJSON Feature Collection

**What is this?**

A collection of multiple map markers/locations, used to display many service requests on a map at once.

**Response**:
```json
{
  "status": "success",
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [78.4867, 17.3850]
        },
        "properties": {
          "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
          "service_type": "MEDICAL",
          "priority": "CRITICAL",
          "status": "IN_PROGRESS",
          "address": "Charminar, Hyderabad",
          "created_at": "2026-05-16T10:45:00Z",
          "requestor_name": "John Doe",
          "assigned_provider": "Dr. Rajesh Kumar"
        }
      },
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [78.4900, 17.3900]
        },
        "properties": {
          "service_id": "e8d7c6b5-a4b3-2109-fedc-ba9876543211",
          "service_type": "FOOD",
          "priority": "HIGH",
          "status": "APPROVED",
          "address": "Mehdipatnam, Hyderabad",
          "created_at": "2026-05-16T10:30:00Z"
        }
      }
    ]
  }
}
```

**Structure Breakdown**:
```
FeatureCollection
├── features[0]                    ← First marker
│   ├── geometry
│   │   ├── type: "Point"
│   │   └── coordinates: [lng, lat]
│   └── properties                 ← Data about this marker
│       ├── service_id
│       ├── service_type
│       └── ...
├── features[1]                    ← Second marker
│   ├── geometry
│   └── properties
└── ...
```

**How maps use this**:
1. Frontend requests: `GET /api/v1/services/geojson?bbox=78.4,17.3,78.6,17.5`
2. Backend sends GeoJSON FeatureCollection
3. Leaflet/Google Maps displays all markers at once
4. Each marker shows popup with `properties` data

---

### 7.2 Clustering Response

**What is clustering?**

When you have 1000 service requests in one area, you can't show 1000 markers - the map becomes unreadable! Clustering groups nearby requests together.

**Visual Example**:
```
Without Clustering:        With Clustering:
🔴🔴🔴🔴🔴🔴              [Medical: 12]
🔴🔴🔴🔴🔴🔴              [Food: 8]
🔴🔴🔴🔴🔴🔴              [Shelter: 5]
(Messy!)                   (Clear!)
```

**Request**:
```json
{
  "service_ids": [
    "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "e8d7c6b5-a4b3-2109-fedc-ba9876543211",
    "d7c6b5a4-b3a2-1098-fedc-ba9876543212"
    // ... 100 more IDs ...
  ],
  "k": 5
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "clusters": [
      {
        "cluster_id": 0,
        "center": {
          "type": "Point",
          "coordinates": [78.4867, 17.3850]
        },
        "count": 12,
        "service_types": {
          "MEDICAL": 5,
          "FOOD": 4,
          "SHELTER": 3
        },
        "priorities": {
          "CRITICAL": 2,
          "HIGH": 5,
          "MEDIUM": 3,
          "LOW": 2
        },
        "services": [
          "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
          "e8d7c6b5-a4b3-2109-fedc-ba9876543211"
          // ... list of service IDs in this cluster ...
        ]
      },
      {
        "cluster_id": 1,
        "center": {
          "type": "Point",
          "coordinates": [78.5200, 17.4100]
        },
        "count": 8,
        "service_types": {
          "FOOD": 5,
          "SHELTER": 3
        },
        "priorities": {
          "HIGH": 3,
          "MEDIUM": 4,
          "LOW": 1
        },
        "services": [
          "d7c6b5a4-b3a2-1098-fedc-ba9876543212"
          // ... more IDs ...
        ]
      }
    ]
  }
}
```

**How to use clusters on a map**:
1. Show large circle at `center` coordinates
2. Label circle with `count` (e.g., "12 requests")
3. Color-code by highest `priority` in cluster
4. On click, zoom in to show individual markers

---

## 8. **Analytics Formats**

### 8.1 Dashboard Metrics

**What is this?**

A summary of all disaster response activity, shown on admin dashboards.

**Response**:
```json
{
  "status": "success",
  "data": {
    "total_requests": 1250,
    "by_status": {
      "SUBMITTED": 45,
      "UNDER_REVIEW": 30,
      "APPROVED": 120,
      "IN_PROGRESS": 85,
      "COMPLETED": 850,
      "VERIFIED": 750,
      "REJECTED": 50,
      "CANCELLED": 20
    },
    "by_priority": {
      "CRITICAL": 12,
      "HIGH": 145,
      "MEDIUM": 680,
      "LOW": 413
    },
    "by_service_type": {
      "MEDICAL": 350,
      "FOOD": 450,
      "SHELTER": 250,
      "RESCUE": 80,
      "SANITATION": 70,
      "COMMUNICATION": 30,
      "TRANSPORT": 20
    },
    "avg_response_time_minutes": 42,
    "completion_rate": 0.85,
    "verification_rate": 0.88,
    "top_providers": [
      {
        "provider_id": "p1",
        "organization": "City Hospital",
        "total_completed": 245,
        "rating": 4.8
      },
      {
        "provider_id": "p2",
        "organization": "Red Cross",
        "total_completed": 198,
        "rating": 4.7
      }
    ],
    "critical_pending": {
      "count": 3,
      "services": [
        {
          "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
          "service_type": "MEDICAL",
          "location": "Charminar, Hyderabad",
          "age_minutes": 15
        }
      ]
    }
  }
}
```

**Key Metrics Explained**:

| Metric | Meaning | Good Value |
|--------|---------|------------|
| `avg_response_time_minutes` | How fast providers respond | < 60 minutes |
| `completion_rate` | % of approved requests completed | > 80% |
| `verification_rate` | % of completed requests verified | > 75% |
| `critical_pending.count` | CRITICAL requests waiting | 0 (ideally!) |

---

### 8.2 Time-Series Data

**What is this?**

Tracks how metrics change over time (daily, weekly, monthly).

**Response**:
```json
{
  "status": "success",
  "data": {
    "time_series": [
      {
        "date": "2026-05-01",
        "total": 45,
        "by_status": {
          "SUBMITTED": 10,
          "APPROVED": 15,
          "IN_PROGRESS": 12,
          "COMPLETED": 8
        }
      },
      {
        "date": "2026-05-02",
        "total": 52,
        "by_status": {
          "SUBMITTED": 12,
          "APPROVED": 18,
          "IN_PROGRESS": 14,
          "COMPLETED": 8
        }
      }
      // ... one entry per day ...
    ],
    "summary": {
      "total_period": 1250,
      "avg_per_day": 41.7,
      "peak_day": "2026-05-05",
      "peak_count": 78
    }
  }
}
```

**How to visualize this**:
- Line chart: X-axis = dates, Y-axis = total requests
- Stacked bar chart: Show status breakdown per day
- Highlight peak day in red

---

## 9. **Error Response Formats**

### 9.1 Standard Error Structure

**All errors follow this pattern**:

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {},
  "timestamp": "2026-05-16T12:00:00Z",
  "request_id": "req_abc123"
}
```

**Field Purposes**:
- `status`: Always `"error"` (vs `"success"`)
- `message`: What went wrong in plain English
- `code`: Machine-readable error code for logging
- `details`: Extra information (varies by error type)
- `timestamp`: When error occurred
- `request_id`: Unique ID for this request (for support/debugging)

---

### 9.2 Common Error Types

#### Validation Error (400 Bad Request)

**When**: You sent invalid data (wrong format, missing fields, etc.)

```json
{
  "status": "error",
  "message": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "errors": [
      {
        "field": "email",
        "message": "Email already registered",
        "value": "john@example.com"
      },
      {
        "field": "password",
        "message": "Password must contain at least one uppercase letter",
        "value": null
      }
    ]
  },
  "timestamp": "2026-05-16T12:00:00Z",
  "request_id": "req_abc123"
}
```

**How to fix**: Check the `errors` array and correct each field mentioned.

---

#### Unauthorized (401 - Not Logged In)

**When**: You're not logged in or your token expired.

```json
{
  "status": "error",
  "message": "Authentication required",
  "code": "UNAUTHORIZED",
  "details": {
    "reason": "No token provided"
  },
  "timestamp": "2026-05-16T12:00:00Z",
  "request_id": "req_abc123"
}
```

**How to fix**: Log in again or use token refresh endpoint.

---

#### Forbidden (403 - Not Allowed)

**When**: You're logged in but don't have permission.

```json
{
  "status": "error",
  "message": "You do not have permission to perform this action",
  "code": "FORBIDDEN",
  "details": {
    "required_role": "DM_AUTHORITY",
    "your_role": "CITIZEN",
    "action": "approve_service_request"
  },
  "timestamp": "2026-05-16T12:00:00Z",
  "request_id": "req_abc123"
}
```

**How to fix**: Contact admin to get the required role, or use a different account.

---

#### Not Found (404 - Doesn't Exist)

**When**: The resource you requested doesn't exist.

```json
{
  "status": "error",
  "message": "Service request not found",
  "code": "NOT_FOUND",
  "details": {
    "resource_type": "service_request",
    "resource_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210"
  },
  "timestamp": "2026-05-16T12:00:00Z",
  "request_id": "req_abc123"
}
```

**How to fix**: Double-check the ID you're requesting. It may have been deleted or never existed.

---

#### Rate Limit (429 - Too Many Requests)

**When**: You're making requests too quickly.

```json
{
  "status": "error",
  "message": "Too many requests. Please try again later.",
  "code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "limit": "100 requests per minute",
    "reset_at": "2026-05-16T12:01:00Z",
    "retry_after": 45
  },
  "timestamp": "2026-05-16T12:00:15Z",
  "request_id": "req_abc123"
}
```

**How to fix**: Wait `retry_after` seconds before trying again.

---

#### Server Error (500 - Our Fault)

**When**: Something broke on the server (not your fault!).

```json
{
  "status": "error",
  "message": "An internal server error occurred",
  "code": "INTERNAL_SERVER_ERROR",
  "details": {
    "error_id": "err_xyz789",
    "message": "The engineering team has been notified"
  },
  "timestamp": "2026-05-16T12:00:00Z",
  "request_id": "req_abc123"
}
```

**How to fix**: Wait a few minutes and try again. If it persists, report the `request_id` to support.

---

## 10. **Quick Reference Tables**

### 10.1 HTTP Status Codes

| Code | Name | When Used | Your Action |
|------|------|-----------|-------------|
| **200** | OK | Success (GET, PUT, DELETE) | Process the data! |
| **201** | Created | Success (POST - resource created) | New resource created successfully |
| **204** | No Content | Success (no response body) | Action succeeded, nothing to return |
| **400** | Bad Request | Validation error | Fix your request data |
| **401** | Unauthorized | Authentication required/failed | Log in again |
| **403** | Forbidden | Insufficient permissions | Need different role |
| **404** | Not Found | Resource doesn't exist | Check the ID |
| **409** | Conflict | Resource conflict (duplicate) | Resource already exists |
| **422** | Unprocessable Entity | Semantic error | Check business logic |
| **429** | Too Many Requests | Rate limited | Slow down requests |
| **500** | Server Error | Internal error | Wait and retry |
| **503** | Service Unavailable | Temporary outage | Service is down |

---

### 10.2 Response Envelope Pattern

**All successful responses**:
```json
{
  "status": "success",
  "data": { /* actual data here */ }
}
```

**All error responses**:
```json
{
  "status": "error",
  "message": "...",
  "code": "...",
  "details": {}
}
```

**Why this pattern?**

Your frontend can check `response.status` first:
```javascript
const response = await fetch('/api/v1/services');
const json = await response.json();

if (json.status === 'success') {
  const services = json.data.services;
  displayServices(services);
} else {
  showError(json.message);
}
```

---

## 11. **Best Practices**

### 11.1 Always Validate Input

**❌ BAD** (Trust user input):
```javascript
const email = userInput.email;
fetch('/api/v1/register', {
  body: JSON.stringify({ email })
});
```

**✅ GOOD** (Validate first):
```javascript
const email = userInput.email;

// Validate email format
if (!email || !email.includes('@')) {
  showError('Invalid email format');
  return;
}

// Validate email length
if (email.length > 255) {
  showError('Email too long (max 255 characters)');
  return;
}

// Now safe to send
fetch('/api/v1/register', {
  body: JSON.stringify({ email })
});
```

---

### 11.2 Handle All Error Cases

**❌ BAD** (Assume success):
```javascript
const response = await fetch('/api/v1/services');
const data = await response.json();
displayServices(data.data.services); // ← Crashes if error!
```

**✅ GOOD** (Handle errors):
```javascript
try {
  const response = await fetch('/api/v1/services');
  const data = await response.json();
  
  if (data.status === 'success') {
    displayServices(data.data.services);
  } else {
    showError(data.message);
  }
} catch (error) {
  showError('Network error: ' + error.message);
}
```

---

### 11.3 Use Type Safety (TypeScript/Pydantic)

**JavaScript/TypeScript Example**:
```typescript
interface ServiceRequest {
  service_type: ServiceType;
  priority: PriorityLevel;
  location: GeoJSONPoint;
  address: string;
  description: string;
}

// Now TypeScript prevents mistakes:
const request: ServiceRequest = {
  service_type: 'MEDEICAL', // ← TypeScript error: typo!
  // ...
};
```

**Python/Pydantic Example**:
```python
from pydantic import BaseModel, Field

class ServiceRequest(BaseModel):
    service_type: ServiceType
    priority: PriorityLevel
    location: GeoJSONPoint
    address: str = Field(max_length=500)
    description: str = Field(max_length=1000)

# Now Pydantic validates automatically:
request = ServiceRequest(
    service_type="MEDEICAL",  # ← Validation error: invalid enum!
    # ...
)
```

---

### 11.4 Use Constants for Enums

**❌ BAD** (Magic strings everywhere):
```javascript
if (service.status === 'IN_PROGRESS') { // ← Typo risk!
  // ...
}
```

**✅ GOOD** (Constants):
```javascript
const ServiceStatus = {
  SUBMITTED: 'SUBMITTED',
  APPROVED: 'APPROVED',
  IN_PROGRESS: 'IN_PROGRESS',
  COMPLETED: 'COMPLETED',
  // ...
};

if (service.status === ServiceStatus.IN_PROGRESS) { // ← Safe!
  // ...
}
```

---

## 12. **Common Mistakes to Avoid**

### 12.1 Mixing Latitude and Longitude Order

**❌ WRONG**:
```json
{
  "coordinates": [17.3850, 78.4867]
}
```
*This is [latitude, longitude] - WRONG for GeoJSON!*

**✅ CORRECT**:
```json
{
  "coordinates": [78.4867, 17.3850]
}
```
*GeoJSON always uses [longitude, latitude]*

**Memory Trick**: **"LONG-LAT"** - longitude comes first, just like alphabetically!

---

### 12.2 Forgetting to Send Authorization Header

**❌ WRONG**:
```javascript
fetch('/api/v1/services')
```
*Server returns 401 Unauthorized*

**✅ CORRECT**:
```javascript
fetch('/api/v1/services', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```

---

### 12.3 Not Handling Token Expiry

**❌ WRONG** (Ignore 401 errors):
```javascript
const response = await fetch('/api/v1/services', {
  headers: { 'Authorization': `Bearer ${oldToken}` }
});
// ← Token expired! But we don't refresh it
```

**✅ CORRECT** (Auto-refresh):
```javascript
let accessToken = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');

async function fetchWithAuth(url) {
  let response = await fetch(url, {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
  
  if (response.status === 401) {
    // Token expired - refresh it!
    const refreshResponse = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    
    const data = await refreshResponse.json();
    accessToken = data.data.access_token;
    localStorage.setItem('access_token', accessToken);
    
    // Retry original request with new token
    response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    });
  }
  
  return response;
}
```

---

### 12.4 Sending Wrong Content-Type

**❌ WRONG**:
```javascript
fetch('/api/v1/services', {
  method: 'POST',
  body: JSON.stringify(data)
  // ← Missing Content-Type header!
});
```
*Server may reject or misinterpret the request*

**✅ CORRECT**:
```javascript
fetch('/api/v1/services', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify(data)
});
```

---

### 12.5 Not Validating UUID Format

**❌ WRONG**:
```javascript
const serviceId = '123'; // ← Not a UUID!
fetch(`/api/v1/services/${serviceId}`); // ← Will fail
```

**✅ CORRECT**:
```javascript
const serviceId = 'f9e8d7c6-b5a4-3210-fedc-ba9876543210';

// Validate UUID format
const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
if (!uuidPattern.test(serviceId)) {
  showError('Invalid service ID format');
  return;
}

fetch(`/api/v1/services/${serviceId}`);
```

---

## 🎉 **Congratulations!**

You now understand all the data formats used in IDRM! You can:

✅ **Read and write JSON** for API requests  
✅ **Understand authentication** flows (login, tokens, refresh)  
✅ **Work with service requests** (create, update, list)  
✅ **Handle geospatial data** (GeoJSON, coordinates, clustering)  
✅ **Process analytics** (dashboard metrics, time-series)  
✅ **Interpret error messages** (status codes, error formats)  
✅ **Follow best practices** (validation, error handling, type safety)  
✅ **Avoid common mistakes** (lat/lng order, token expiry, headers)

---

## 📚 **What's Next?**

**Continue your learning journey**:

- **[41-CODE-STANDARDS.md](41-CODE-STANDARDS.md)** - Learn coding best practices
- **[42-VERIFICATION-CHECKLISTS.md](42-VERIFICATION-CHECKLISTS.md)** - Learn testing and quality assurance
- **[23-API-SPECIFICATION.md](23-API-SPECIFICATION.md)** - Detailed API endpoint documentation
- **[24-FRONTEND-IMPLEMENTATION.md](24-FRONTEND-IMPLEMENTATION.md)** - Build frontend features
- **[25-BACKEND-IMPLEMENTATION.md](25-BACKEND-IMPLEMENTATION.md)** - Build backend services

---

## 🆘 **Need Help?**

**If you're stuck**:
1. Re-read the relevant section above
2. Check the examples in section 11 (Best Practices)
3. Review common mistakes in section 12
4. Look at code examples in other documentation files
5. Ask for help in the project discussion forum

---

**Document Information**  
**Created**: May 16, 2026  
**Purpose**: Complete guide to IDRM data formats  
**Difficulty**: 🟢 Beginner-friendly with advanced topics  
**Estimated Reading Time**: 45-60 minutes  
**Part of**: IDRM Documentation Series (Document 40/43)
