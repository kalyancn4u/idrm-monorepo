> *Type: Document (specification) · Audience: Developers, integrators · Status: Archived — v1 historical generation*

# IDRM Platform API Specification

> Comprehensive API documentation with JSON specifications, role-based access control, and security guidelines

<!-- IDRM-CLEANUP doc=v1-40-api status=ANNOTATED pass=2026-08-16 -->
> ## 🗺️ SECTION MAP (annotation pass, 2026-08-16)
> Gen-1 endpoint list (25 endpoints). **Superseded by the frozen canonical `docs/mvp/40-api-specification.md`
> (+ `40-api-openapi.yaml`).** Grouped by module below. *Legend:* ⚠ superseded (paths differ) · ⊘ dropped/FFP.
>
> | Snippet | Endpoints | → Addressed in | Phase | Verdict |
> |---|---|---|---|---|
> | `v1-40§auth` | 1–4 Register/Login/Refresh/Logout | `docs/mvp/40` + `22` | MVP | ⚠ |
> | `v1-40§svc` | 5–10 Service Requests (= incidents) | `docs/mvp/40` | MVP | ⚠ |
> | `v1-40§prov` | 11–13 Providers/location/available | `docs/mvp/40` (RES) | MVP | ⚠ |
> | `v1-40§geo` | 14 Nearby · 15 Heatmap · 16 Route-opt | nearby → MVP `40`; **heatmap/route → FFP** | MVP/FFP | ⚠ |
> | `v1-40§dis` | 17–18 Disasters | config → ADM; disaster-event → FFP | MVP/FFP | ⚠ |
> | `v1-40§fin` | 19–21 Donations/Financial | money → **FFP** | FFP | ⊘ |
> | `v1-40§usr` | 22–24 Profile/Activity/Dashboard | `docs/mvp/40` (USR); dashboard → RPT | MVP | ⚠ |
> | `v1-40§anon` | 10 Anon verify · 25 Anonymize | graded privacy → **FFP** | FFP | ⊘ |
>
> *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

## Table of Contents

1. [Authentication APIs](#authentication-apis)
2. [Service Request APIs](#service-request-apis)
3. [Provider APIs](#provider-apis)
4. [Geospatial APIs](#geospatial-apis)
5. [Disaster Management APIs](#disaster-management-apis)
6. [Donation & Financial APIs](#donation--financial-apis)
7. [User Management APIs](#user-management-apis)
8. [Analytics APIs](#analytics-apis)
9. [Privacy & ReVV APIs](#privacy--revv-apis)
10. [WebSocket Events](#websocket-events)

---

## API Base URL

```
Development: http://localhost:3000/api/v1
Production:  https://api.idrm.gov.in/api/v1
```

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## User Roles

```javascript
{
  "SUPER_ADMIN": "super_admin",      // Full system access
  "ADMIN": "admin",                  // Administrative access
  "COORDINATOR": "coordinator",      // Disaster coordination
  "PROVIDER": "provider",            // Service provider
  "CITIZEN": "citizen",              // General public
  "GUEST": "guest"                   // Unauthenticated user
}
```

## HTTP Methods

- **POST**: Create new resources (preferred for security)
- **GET**: Retrieve resources
- **POST (with action)**: Update resources (e.g., POST /services/{id}/update)
- **DELETE**: Remove resources

**Note**: We use POST for updates instead of PUT/PATCH for enhanced security and to avoid method tampering.

---

# Authentication APIs

## 1. Register User

**Endpoint**: `POST /auth/register`

**Access**: Public (GUEST)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe",
  "phone": "+919876543210",
  "role": "citizen",
  "location": {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "address": "Delhi, India"
  },
  "preferences": {
    "language": "en",
    "notifications": true
  }
}
```

**Validation Rules**:
- `email`: Valid email format, unique
- `password`: Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
- `phone`: Valid international format
- `role`: One of: citizen, provider (admin/coordinator require approval)
- `location.latitude`: -90 to 90
- `location.longitude`: -180 to 180

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_1234567890",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "citizen",
      "status": "active",
      "created_at": "2024-12-22T10:30:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIs...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
      "expires_in": 3600
    }
  }
}
```

**Errors**:
```json
{
  "success": false,
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "Email already registered",
    "field": "email"
  }
}
```

---

## 2. Login

**Endpoint**: `POST /auth/login`

**Access**: Public (GUEST)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "remember_me": true
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_1234567890",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "citizen",
      "permissions": ["service:create", "service:view"],
      "profile_complete": true
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIs...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
      "expires_in": 3600
    },
    "session": {
      "session_id": "sess_abc123",
      "device": "Chrome/Windows",
      "ip": "103.x.x.x"
    }
  }
}
```

---

## 3. Refresh Token

**Endpoint**: `POST /auth/refresh`

**Access**: Authenticated

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600
  }
}
```

---

## 4. Logout

**Endpoint**: `POST /auth/logout`

**Access**: Authenticated (ALL ROLES)

**Request Body**:
```json
{
  "session_id": "sess_abc123"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

# Service Request APIs

## 5. Create Service Request

**Endpoint**: `POST /services/requests`

**Access**: CITIZEN, COORDINATOR, ADMIN

**Request Body**:
```json
{
  "type": "medical",
  "category": "emergency",
  "priority": "high",
  "description": "Medical emergency - patient needs ambulance",
  "location": {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "address": "Connaught Place, New Delhi",
    "landmark": "Near Central Park"
  },
  "contact": {
    "name": "John Doe",
    "phone": "+919876543210",
    "alternate_phone": "+919876543211"
  },
  "details": {
    "num_people": 1,
    "age_group": "adult",
    "medical_condition": "chest pain",
    "mobility": "unable to walk"
  },
  "privacy": {
    "is_anonymous": false,
    "share_location": true,
    "share_contact": true
  },
  "media": [
    {
      "type": "image",
      "url": "https://storage.idrm.gov.in/uploads/img123.jpg"
    }
  ]
}
```

**Validation Rules**:
- `type`: medical, food, shelter, rescue, evacuation, supplies
- `category`: emergency, urgent, normal
- `priority`: critical, high, medium, low
- `description`: 10-1000 characters
- `location.latitude/longitude`: Valid coordinates
- `contact.phone`: Valid phone number
- `details`: Type-specific validation
- `privacy.is_anonymous`: If true, contact info is hidden (ReVV activated)

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "request": {
      "id": "req_9876543210",
      "revv_id": "revv_abc123xyz",  // Only if anonymous
      "verification_code": "XYZ789ABC",  // Only if anonymous
      "type": "medical",
      "category": "emergency",
      "priority": "high",
      "status": "pending",
      "location": {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "address": "Connaught Place, New Delhi"
      },
      "created_at": "2024-12-22T10:30:00Z",
      "estimated_response_time": "15 minutes",
      "assigned_provider": null
    },
    "message": "Service request created successfully. Save your verification code: XYZ789ABC"
  }
}
```

---

## 6. Get Service Requests

**Endpoint**: `GET /services/requests`

**Access**: ALL AUTHENTICATED ROLES

**Query Parameters**:
```
?status=pending,in-progress
&type=medical
&priority=high,critical
&disaster_zone=dzn_123
&latitude=28.6139
&longitude=77.2090
&radius=5000
&page=1
&limit=20
&sort_by=created_at
&sort_order=desc
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "requests": [
      {
        "id": "req_9876543210",
        "type": "medical",
        "priority": "high",
        "status": "pending",
        "location": {
          "latitude": 28.6139,
          "longitude": 77.2090,
          "address": "Connaught Place, New Delhi"
        },
        "distance_km": 2.5,
        "created_at": "2024-12-22T10:30:00Z",
        "contact": {
          "name": "John Doe",
          "phone": "+91-XXXX-XX3210"  // Masked for privacy
        },
        "is_anonymous": false
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 156,
      "total_pages": 8
    },
    "filters_applied": {
      "status": ["pending", "in-progress"],
      "type": "medical"
    }
  }
}
```

**Access Control**:
- **CITIZEN**: Only their own requests
- **PROVIDER**: Requests in their service area and type
- **COORDINATOR/ADMIN**: All requests in their jurisdiction

---

## 7. Get Service Request Details

**Endpoint**: `GET /services/requests/{request_id}`

**Access**: Creator, Assigned Provider, COORDINATOR, ADMIN

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "request": {
      "id": "req_9876543210",
      "type": "medical",
      "category": "emergency",
      "priority": "high",
      "status": "in-progress",
      "description": "Medical emergency - patient needs ambulance",
      "location": {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "address": "Connaught Place, New Delhi",
        "landmark": "Near Central Park"
      },
      "contact": {
        "name": "John Doe",
        "phone": "+919876543210"
      },
      "details": {
        "num_people": 1,
        "medical_condition": "chest pain"
      },
      "created_by": {
        "id": "usr_1234567890",
        "name": "John Doe",
        "role": "citizen"
      },
      "assigned_to": {
        "id": "prv_5555555555",
        "name": "City Hospital Ambulance",
        "type": "medical_provider",
        "eta": "10 minutes",
        "contact": "+919999999999"
      },
      "timeline": [
        {
          "status": "created",
          "timestamp": "2024-12-22T10:30:00Z",
          "by": "usr_1234567890"
        },
        {
          "status": "assigned",
          "timestamp": "2024-12-22T10:32:00Z",
          "by": "coordinator_123",
          "to": "prv_5555555555"
        },
        {
          "status": "accepted",
          "timestamp": "2024-12-22T10:33:00Z",
          "by": "prv_5555555555"
        },
        {
          "status": "in-progress",
          "timestamp": "2024-12-22T10:35:00Z",
          "by": "prv_5555555555"
        }
      ],
      "created_at": "2024-12-22T10:30:00Z",
      "updated_at": "2024-12-22T10:35:00Z"
    }
  }
}
```

---

## 8. Update Service Request Status

**Endpoint**: `POST /services/requests/{request_id}/status`

**Access**: Assigned Provider, COORDINATOR, ADMIN

**Request Body**:
```json
{
  "status": "in-progress",
  "notes": "Ambulance en route, ETA 10 minutes",
  "location": {
    "latitude": 28.6150,
    "longitude": 77.2100
  }
}
```

**Validation Rules**:
- `status`: pending → assigned → accepted → in-progress → completed | cancelled
- Status transitions must follow workflow
- `notes`: Optional, max 500 characters

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "request": {
      "id": "req_9876543210",
      "status": "in-progress",
      "updated_at": "2024-12-22T10:35:00Z"
    }
  },
  "message": "Status updated successfully"
}
```

---

## 9. Assign Service Request to Provider

**Endpoint**: `POST /services/requests/{request_id}/assign`

**Access**: COORDINATOR, ADMIN

**Request Body**:
```json
{
  "provider_id": "prv_5555555555",
  "priority_override": "critical",
  "notes": "Urgent case, prioritize",
  "expected_completion": "2024-12-22T11:00:00Z"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "assignment": {
      "request_id": "req_9876543210",
      "provider_id": "prv_5555555555",
      "assigned_at": "2024-12-22T10:32:00Z",
      "assigned_by": "coordinator_123",
      "status": "assigned"
    }
  },
  "message": "Request assigned to provider successfully"
}
```

---

## 10. Anonymous Request Verification

**Endpoint**: `POST /services/requests/verify`

**Access**: Public (GUEST)

**Request Body**:
```json
{
  "revv_id": "revv_abc123xyz",
  "verification_code": "XYZ789ABC"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "request": {
      "id": "req_9876543210",
      "revv_id": "revv_abc123xyz",
      "type": "medical",
      "status": "in-progress",
      "created_at": "2024-12-22T10:30:00Z",
      "last_updated": "2024-12-22T10:35:00Z"
    },
    "verified": true
  }
}
```

---

# Provider APIs

## 11. Register Provider Organization

**Endpoint**: `POST /providers/register`

**Access**: ADMIN only

**Request Body**:
```json
{
  "organization": {
    "name": "City Hospital",
    "type": "hospital",
    "registration_number": "REG123456",
    "verified": true,
    "contact": {
      "email": "contact@cityhospital.org",
      "phone": "+919999999999",
      "address": "123 Medical Street, Delhi"
    }
  },
  "services_offered": [
    {
      "type": "medical",
      "subtypes": ["ambulance", "emergency_care"],
      "capacity": 10,
      "availability": "24/7"
    }
  ],
  "service_area": {
    "type": "polygon",
    "coordinates": [
      [77.1, 28.5],
      [77.3, 28.5],
      [77.3, 28.7],
      [77.1, 28.7],
      [77.1, 28.5]
    ]
  },
  "admin_user": {
    "name": "Dr. Smith",
    "email": "admin@cityhospital.org",
    "phone": "+919999999998"
  }
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "provider": {
      "id": "prv_5555555555",
      "organization_name": "City Hospital",
      "type": "hospital",
      "status": "active",
      "services_offered": ["medical"],
      "created_at": "2024-12-22T10:00:00Z"
    },
    "admin_credentials": {
      "email": "admin@cityhospital.org",
      "temporary_password": "TempPass123!",
      "reset_required": true
    }
  }
}
```

---

## 12. Update Provider Location

**Endpoint**: `POST /providers/{provider_id}/location`

**Access**: PROVIDER (self), COORDINATOR, ADMIN

**Request Body**:
```json
{
  "location": {
    "latitude": 28.6150,
    "longitude": 77.2100,
    "accuracy": 10,
    "heading": 45,
    "speed": 30
  },
  "status": "en_route",
  "notes": "Heading to service request req_9876543210"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "provider_id": "prv_5555555555",
    "location": {
      "latitude": 28.6150,
      "longitude": 77.2100
    },
    "updated_at": "2024-12-22T10:35:00Z"
  }
}
```

---

## 13. Get Available Providers

**Endpoint**: `GET /providers/available`

**Access**: COORDINATOR, ADMIN

**Query Parameters**:
```
?service_type=medical
&latitude=28.6139
&longitude=77.2090
&radius=10000
&capacity_min=5
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "providers": [
      {
        "id": "prv_5555555555",
        "name": "City Hospital",
        "type": "hospital",
        "services": ["medical", "ambulance"],
        "location": {
          "latitude": 28.6150,
          "longitude": 77.2100
        },
        "distance_km": 1.2,
        "capacity": {
          "total": 10,
          "available": 7
        },
        "rating": 4.8,
        "response_time_avg": "12 minutes",
        "status": "available"
      }
    ],
    "total_found": 5
  }
}
```

---

# Geospatial APIs

## 14. Search Nearby Services

**Endpoint**: `POST /geospatial/nearby`

**Access**: ALL AUTHENTICATED ROLES

**Request Body**:
```json
{
  "location": {
    "latitude": 28.6139,
    "longitude": 77.2090
  },
  "radius_meters": 5000,
  "filters": {
    "service_types": ["medical", "food"],
    "status": ["pending", "in-progress"],
    "priority": ["high", "critical"]
  },
  "limit": 50
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "center": {
      "latitude": 28.6139,
      "longitude": 77.2090
    },
    "radius_meters": 5000,
    "results": [
      {
        "id": "req_9876543210",
        "type": "medical",
        "priority": "high",
        "location": {
          "latitude": 28.6145,
          "longitude": 77.2095
        },
        "distance_meters": 245,
        "bearing": 45,
        "created_at": "2024-12-22T10:30:00Z"
      }
    ],
    "total_found": 12,
    "density_per_km2": 0.6
  }
}
```

---

## 15. Get Service Density Heatmap

**Endpoint**: `POST /geospatial/density`

**Access**: COORDINATOR, ADMIN

**Request Body**:
```json
{
  "bounds": {
    "north": 28.7,
    "south": 28.5,
    "east": 77.3,
    "west": 77.1
  },
  "grid_size": 1000,
  "filters": {
    "status": ["pending"],
    "time_range": {
      "start": "2024-12-22T00:00:00Z",
      "end": "2024-12-22T23:59:59Z"
    }
  }
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "heatmap": [
      {
        "latitude": 28.6,
        "longitude": 77.2,
        "count": 15,
        "density": 2.5,
        "intensity": "high"
      }
    ],
    "hotspots": [
      {
        "center": {
          "latitude": 28.65,
          "longitude": 77.22
        },
        "radius_meters": 500,
        "count": 45,
        "severity": "critical"
      }
    ],
    "total_requests": 234
  }
}
```

---

## 16. Get Route Optimization

**Endpoint**: `POST /geospatial/route`

**Access**: PROVIDER, COORDINATOR, ADMIN

**Request Body**:
```json
{
  "start": {
    "latitude": 28.6139,
    "longitude": 77.2090
  },
  "waypoints": [
    {
      "id": "req_111",
      "latitude": 28.6145,
      "longitude": 77.2095,
      "priority": "high"
    },
    {
      "id": "req_222",
      "latitude": 28.6150,
      "longitude": 77.2100,
      "priority": "medium"
    }
  ],
  "optimize_for": "time",
  "avoid": ["tolls"]
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "route": {
      "total_distance_km": 5.2,
      "total_time_minutes": 18,
      "waypoint_order": ["req_111", "req_222"],
      "coordinates": [
        [77.2090, 28.6139],
        [77.2095, 28.6145],
        [77.2100, 28.6150]
      ]
    }
  }
}
```

---

# Disaster Management APIs

## 17. Create Disaster Event

**Endpoint**: `POST /disasters/events`

**Access**: ADMIN only

**Request Body**:
```json
{
  "name": "Delhi Floods 2024",
  "type": "flood",
  "severity": "severe",
  "affected_area": {
    "type": "multipolygon",
    "coordinates": [
      [
        [
          [77.1, 28.5],
          [77.3, 28.5],
          [77.3, 28.7],
          [77.1, 28.7],
          [77.1, 28.5]
        ]
      ]
    ]
  },
  "center_point": {
    "latitude": 28.6,
    "longitude": 77.2
  },
  "start_time": "2024-12-22T00:00:00Z",
  "estimated_end_time": "2024-12-25T00:00:00Z",
  "description": "Heavy rainfall causing severe flooding in low-lying areas",
  "warnings": [
    "Avoid travel in affected areas",
    "Move to higher ground if near river"
  ],
  "emergency_contacts": [
    {
      "type": "helpline",
      "number": "1070",
      "available": "24/7"
    }
  ]
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "disaster": {
      "id": "dzn_123456",
      "name": "Delhi Floods 2024",
      "type": "flood",
      "severity": "severe",
      "status": "active",
      "affected_area_km2": 245.6,
      "created_at": "2024-12-22T10:00:00Z"
    }
  }
}
```

---

## 18. Get Active Disasters

**Endpoint**: `GET /disasters/events/active`

**Access**: ALL AUTHENTICATED ROLES

**Query Parameters**:
```
?latitude=28.6139
&longitude=77.2090
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "disasters": [
      {
        "id": "dzn_123456",
        "name": "Delhi Floods 2024",
        "type": "flood",
        "severity": "severe",
        "distance_km": 2.5,
        "is_user_affected": true,
        "start_time": "2024-12-22T00:00:00Z",
        "warnings": ["Avoid travel in affected areas"]
      }
    ],
    "user_location": {
      "is_in_disaster_zone": true,
      "nearest_disaster": "dzn_123456",
      "distance_km": 2.5
    }
  }
}
```

---

# Donation & Financial APIs

## 19. Create Donation

**Endpoint**: `POST /donations/create`

**Access**: CITIZEN, GUEST (with limited info)

**Request Body**:
```json
{
  "amount": 1000.00,
  "currency": "INR",
  "donor": {
    "name": "Anonymous Donor",
    "email": "donor@example.com",
    "phone": "+919876543210",
    "pan": "ABCDE1234F",
    "is_anonymous": false
  },
  "allocation": {
    "disaster_id": "dzn_123456",
    "purpose": "medical_supplies",
    "specific_request_id": null
  },
  "payment": {
    "method": "upi",
    "upi_id": "donor@upi"
  }
}
```

**Validation Rules**:
- `amount`: Min 10.00, Max 1000000.00
- `currency`: INR only (for India)
- `donor.pan`: Valid PAN format (for tax receipt)
- `payment.method`: upi, card, netbanking

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "donation": {
      "id": "don_987654",
      "transaction_id": "txn_abc123",
      "amount": 1000.00,
      "currency": "INR",
      "status": "pending",
      "payment_link": "https://payments.idrm.gov.in/pay/don_987654",
      "qr_code": "data:image/png;base64,...",
      "expires_at": "2024-12-22T11:00:00Z"
    }
  }
}
```

---

## 20. Track Donation Allocation

**Endpoint**: `GET /donations/{donation_id}/tracking`

**Access**: Donor (with donation_id), ADMIN

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "donation": {
      "id": "don_987654",
      "amount": 1000.00,
      "date": "2024-12-22T10:30:00Z",
      "status": "allocated"
    },
    "allocation": {
      "disaster": "Delhi Floods 2024",
      "purpose": "medical_supplies",
      "allocated_amount": 1000.00,
      "allocated_at": "2024-12-22T12:00:00Z",
      "beneficiaries": 5,
      "impact": "Provided medical kits to 5 families"
    },
    "transparency": {
      "admin_overhead": 0.00,
      "processing_fee": 20.00,
      "net_contribution": 980.00,
      "blockchain_hash": "0x123abc...",
      "receipt_url": "https://storage.idrm.gov.in/receipts/don_987654.pdf"
    }
  }
}
```

---

## 21. Get Financial Report

**Endpoint**: `GET /donations/reports/summary`

**Access**: ADMIN, COORDINATOR (read-only)

**Query Parameters**:
```
?disaster_id=dzn_123456
&start_date=2024-12-01
&end_date=2024-12-31
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_donations": 5000000.00,
      "total_donors": 1234,
      "total_allocated": 4800000.00,
      "pending_allocation": 200000.00,
      "admin_overhead_percent": 0.5
    },
    "breakdown": [
      {
        "category": "medical_supplies",
        "amount": 2000000.00,
        "percentage": 41.7
      },
      {
        "category": "food_relief",
        "amount": 1500000.00,
        "percentage": 31.3
      }
    ],
    "period": {
      "start": "2024-12-01T00:00:00Z",
      "end": "2024-12-31T23:59:59Z"
    }
  }
}
```

---

# User Management APIs

## 22. Update User Profile

**Endpoint**: `POST /users/profile/update`

**Access**: User (self), ADMIN

**Request Body**:
```json
{
  "name": "John Updated Doe",
  "phone": "+919876543210",
  "location": {
    "latitude": 28.6150,
    "longitude": 77.2100,
    "address": "New Address, Delhi"
  },
  "preferences": {
    "language": "hi",
    "notifications": true,
    "email_alerts": false
  }
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_1234567890",
      "name": "John Updated Doe",
      "email": "user@example.com",
      "phone": "+919876543210",
      "updated_at": "2024-12-22T11:00:00Z"
    }
  }
}
```

---

## 23. Get User Activity Log

**Endpoint**: `GET /users/{user_id}/activity`

**Access**: User (self), ADMIN

**Query Parameters**:
```
?page=1
&limit=20
&action_type=service_created,donation_made
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": "act_111",
        "action": "service_created",
        "resource_id": "req_9876543210",
        "timestamp": "2024-12-22T10:30:00Z",
        "ip_address": "103.x.x.x",
        "device": "Chrome/Windows"
      },
      {
        "id": "act_222",
        "action": "donation_made",
        "resource_id": "don_987654",
        "timestamp": "2024-12-22T11:00:00Z",
        "ip_address": "103.x.x.x",
        "device": "Chrome/Windows"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45
    }
  }
}
```

---

# Analytics APIs

## 24. Get Dashboard Statistics

**Endpoint**: `GET /analytics/dashboard`

**Access**: COORDINATOR, ADMIN

**Query Parameters**:
```
?disaster_id=dzn_123456
&time_range=24h
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_requests": 1234,
      "pending_requests": 145,
      "in_progress": 89,
      "completed": 1000,
      "avg_response_time_minutes": 25
    },
    "by_type": [
      {
        "type": "medical",
        "count": 456,
        "percentage": 37
      },
      {
        "type": "food",
        "count": 389,
        "percentage": 31.5
      }
    ],
    "by_priority": [
      {
        "priority": "critical",
        "count": 45,
        "avg_resolution_time_minutes": 18
      }
    ],
    "geographic": {
      "hotspots": 5,
      "coverage_area_km2": 245.6
    },
    "resources": {
      "active_providers": 234,
      "total_capacity": 1500,
      "utilization_percent": 67
    }
  }
}
```

---

# Privacy & ReVV APIs

## 25. Anonymize Request

**Endpoint**: `POST /privacy/anonymize`

**Access**: CITIZEN (request owner), ADMIN

**Request Body**:
```json
{
  "request_id": "req_9876543210",
  "level": "full"
}
```

**Validation Rules**:
- `level`: partial (hide contact), full (hide contact + fuzzy location)
- Can only anonymize own requests
- Cannot reverse once anonymized

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "revv_id": "revv_abc123xyz",
    "verification_code": "XYZ789ABC",
    "anonymization_level": "full",
    "message": "Request anonymized. Save your verification code: XYZ789ABC"
  }
}
```

---

## 26. Audit Log Query

**Endpoint**: `GET /privacy/audit-logs`

**Access**: ADMIN only

**Query Parameters**:
```
?user_id=usr_1234567890
&action=data_access
&resource_type=service_request
&start_date=2024-12-01
&end_date=2024-12-31
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": "log_111",
        "user_id": "usr_1234567890",
        "action": "data_access",
        "resource_type": "service_request",
        "resource_id": "req_9876543210",
        "ip_address": "103.x.x.x",
        "timestamp": "2024-12-22T10:30:00Z",
        "details": {
          "fields_accessed": ["contact", "location"],
          "reason": "service_coordination"
        }
      }
    ],
    "total": 156
  }
}
```

---

# WebSocket Events

## Client → Server Events

### 1. Subscribe to Service Updates
```javascript
socket.emit('service:subscribe', {
  service_id: 'req_9876543210'
});
```

### 2. Update Location (Providers)
```javascript
socket.emit('location:update', {
  latitude: 28.6150,
  longitude: 77.2100,
  heading: 45,
  speed: 30
});
```

### 3. Send Message
```javascript
socket.emit('message:send', {
  room: 'service:req_9876543210',
  message: 'Ambulance arriving in 5 minutes',
  type: 'status_update'
});
```

---

## Server → Client Events

### 1. Service Created
```javascript
socket.on('service:created', (data) => {
  // data format:
  {
    "id": "req_9876543210",
    "type": "medical",
    "priority": "high",
    "location": {...}
  }
});
```

### 2. Service Updated
```javascript
socket.on('service:updated', (data) => {
  // data format:
  {
    "id": "req_9876543210",
    "status": "in-progress",
    "updated_fields": ["status", "assigned_to"]
  }
});
```

### 3. Provider Location Update
```javascript
socket.on('provider:location', (data) => {
  // data format:
  {
    "provider_id": "prv_5555555555",
    "location": {
      "latitude": 28.6150,
      "longitude": 77.2100
    },
    "timestamp": "2024-12-22T10:35:00Z"
  }
});
```

### 4. New Message
```javascript
socket.on('message:received', (data) => {
  // data format:
  {
    "from": "prv_5555555555",
    "message": "Ambulance arriving in 5 minutes",
    "timestamp": "2024-12-22T10:35:00Z"
  }
});
```

---

# Error Codes

```javascript
{
  // Authentication Errors (1000-1099)
  "AUTH_INVALID_TOKEN": 1001,
  "AUTH_TOKEN_EXPIRED": 1002,
  "AUTH_INSUFFICIENT_PERMISSIONS": 1003,
  
  // Validation Errors (2000-2099)
  "VALIDATION_INVALID_INPUT": 2001,
  "VALIDATION_MISSING_FIELD": 2002,
  "VALIDATION_INVALID_FORMAT": 2003,
  
  // Resource Errors (3000-3099)
  "RESOURCE_NOT_FOUND": 3001,
  "RESOURCE_ALREADY_EXISTS": 3002,
  "RESOURCE_DELETED": 3003,
  
  // Business Logic Errors (4000-4099)
  "SERVICE_ALREADY_ASSIGNED": 4001,
  "PROVIDER_NOT_AVAILABLE": 4002,
  "INVALID_STATUS_TRANSITION": 4003,
  
  // System Errors (5000-5099)
  "INTERNAL_SERVER_ERROR": 5001,
  "DATABASE_ERROR": 5002,
  "EXTERNAL_SERVICE_ERROR": 5003
}
```

---

# Rate Limiting

**Global Rate Limits**:
- Anonymous: 100 requests / 15 minutes
- Authenticated: 1000 requests / 15 minutes
- Admin: 5000 requests / 15 minutes

**Endpoint-Specific Limits**:
- POST /auth/login: 5 attempts / 15 minutes (per IP)
- POST /services/requests: 10 requests / hour (per user)
- POST /donations/create: 5 requests / hour (per user)

**Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1640181600
```

---

**This API specification ensures security, transparency, and proper separation of concerns for the IDRM platform.**
