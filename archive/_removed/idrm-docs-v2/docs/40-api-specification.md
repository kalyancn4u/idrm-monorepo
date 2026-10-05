> *Type: Document (specification) · Audience: Developers, integrators · Status: Archived — v2 historical generation*

# IDRM Web Frontend - API Integration Guide

<!-- IDRM-CLEANUP doc=v2-40-api status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — API integration → canonical `docs/mvp/40`
> Gen-2 frontend API-integration guide. Canonical contract = [`../../../../docs/mvp/40-api-specification.md`](../../../../docs/mvp/40-api-specification.md)
> (+ `40-api-openapi.yaml`); JSON schemas cross-ref `v2-41-jsonformats`. ⚠ paths superseded by frozen `/api/v1`.
> *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Complete API Reference for Frontend Developers

**Version**: 2.0  
**Last Updated**: May 10, 2026  
**For**: HTML/Tailwind, React SPA, React Native frontends

---

## Table of Contents

1. [Overview](#1-overview)
2. [API Base Configuration](#2-api-base-configuration)
3. [Authentication APIs](#3-authentication-apis)
4. [Service Request APIs](#4-service-request-apis)
5. [Map & Geospatial APIs](#5-map--geospatial-apis)
6. [User & Organization APIs](#6-user--organization-apis)
7. [Analytics & Reports APIs](#7-analytics--reports-apis)
8. [Error Handling](#8-error-handling)
9. [Code Examples](#9-code-examples)

---

## 1. Overview

### 1.1 API Architecture

```
Frontend (Browser)
    ↓ HTTPS
NGINX (Reverse Proxy)
    ↓
Bun API Gateway (Port 3000)
    ↓
Python Microservices (Ports 8000-8004)
    ↓
PostgreSQL + Redis
```

### 1.2 Base URL

**Development**: `http://localhost:3000/api`  
**Staging**: `https://staging.idrm.gov.in/api`  
**Production**: `https://api.idrm.gov.in/api`

### 1.3 API Version

All endpoints are prefixed with `/api/v1/` (v1 implied in examples below)

---

## 2. API Base Configuration

### 2.1 JavaScript API Client Setup

**File**: `js/api.js`

```javascript
/**
 * IDRM API Client
 * Handles all API communication with authentication
 */

const API_BASE_URL = 'http://localhost:3000/api';

class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * Get stored access token
     */
    getToken() {
        return localStorage.getItem('access_token');
    }

    /**
     * Get stored refresh token
     */
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    }

    /**
     * Set tokens in localStorage
     */
    setTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    }

    /**
     * Clear all tokens (logout)
     */
    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    }

    /**
     * Build headers with authentication
     */
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (includeAuth) {
            const token = this.getToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        return headers;
    }

    /**
     * Generic request method with retry logic
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = this.getHeaders(options.auth !== false);

        try {
            const response = await fetch(url, {
                ...options,
                headers: { ...headers, ...options.headers }
            });

            // Handle 401 Unauthorized - try to refresh token
            if (response.status === 401 && !options._isRetry) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Retry original request
                    return this.request(endpoint, { ...options, _isRetry: true });
                } else {
                    // Refresh failed, redirect to login
                    this.clearTokens();
                    window.location.href = '/login.html';
                    throw new Error('Session expired. Please login again.');
                }
            }

            // Handle other HTTP errors
            if (!response.ok) {
                const error = await response.json();
                throw new APIError(error.message || 'Request failed', response.status, error);
            }

            return await response.json();

        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError('Network error. Please check your connection.', 0, error);
        }
    }

    /**
     * Refresh access token using refresh token
     */
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${this.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                this.setTokens(data.access_token, data.refresh_token);
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }

    // Convenience methods
    async get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }

    async post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
    constructor(message, status, details) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.details = details;
    }
}

// Export singleton instance
const api = new APIClient();
```

---

## 3. Authentication APIs

### 3.1 Register New User

**Endpoint**: `POST /auth/register`

**Request**:
```javascript
const registerUser = async (userData) => {
    try {
        const response = await api.post('/auth/register', {
            email: userData.email,
            password: userData.password,
            full_name: userData.fullName,
            phone: userData.phone,
            role: 'CITIZEN'  // Default role
        }, { auth: false });  // No auth needed for registration

        return response;
    } catch (error) {
        console.error('Registration failed:', error);
        throw error;
    }
};

// Usage
const result = await registerUser({
    email: 'john@example.com',
    password: 'SecurePass123!',
    fullName: 'John Doe',
    phone: '9876543210'
});

console.log(result.message); // "Verification email sent..."
```

**Response** (201 Created):
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
    "created_at": "2026-05-10T10:30:00Z"
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Email already registered"
    }
  ]
}
```

---

### 3.2 Login

**Endpoint**: `POST /auth/login`

**Request**:
```javascript
const login = async (email, password) => {
    try {
        const response = await api.post('/auth/login', {
            email,
            password
        }, { auth: false });

        // Store tokens
        api.setTokens(response.data.access_token, response.data.refresh_token);
        
        // Store user data
        localStorage.setItem('user', JSON.stringify(response.data.user));

        return response.data.user;
    } catch (error) {
        console.error('Login failed:', error);
        throw error;
    }
};

// Usage
const user = await login('john@example.com', 'SecurePass123!');
console.log('Logged in as:', user.full_name);
```

**Response** (200 OK):
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

---

### 3.3 Logout

**Endpoint**: `POST /auth/logout`

**Request**:
```javascript
const logout = async () => {
    try {
        await api.post('/auth/logout', {});
        
        // Clear local storage
        api.clearTokens();
        
        // Redirect to login
        window.location.href = '/login.html';
    } catch (error) {
        // Even if API fails, clear tokens locally
        api.clearTokens();
        window.location.href = '/login.html';
    }
};
```

---

### 3.4 Get Current User

**Endpoint**: `GET /users/me`

**Request**:
```javascript
const getCurrentUser = async () => {
    try {
        const response = await api.get('/users/me');
        return response.data;
    } catch (error) {
        console.error('Failed to get user:', error);
        throw error;
    }
};

// Usage
const user = await getCurrentUser();
console.log('Current user:', user.full_name);
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "john@example.com",
    "full_name": "John Doe",
    "phone": "9876543210",
    "role": "CITIZEN",
    "organization_id": null,
    "is_active": true,
    "is_verified": true,
    "created_at": "2026-05-10T10:30:00Z"
  }
}
```

---

## 4. Service Request APIs

### 4.1 Create Service Request

**Endpoint**: `POST /services`

**Request**:
```javascript
const createServiceRequest = async (serviceData) => {
    try {
        const response = await api.post('/services', {
            service_type: serviceData.type,        // 'MEDICAL', 'FOOD', etc.
            priority: serviceData.priority,        // 'CRITICAL', 'HIGH', etc.
            location: {
                type: 'Point',
                coordinates: [serviceData.lng, serviceData.lat]
            },
            address: serviceData.address,
            description: serviceData.description,
            privacy_level: serviceData.privacy || 'PROTECTED',
            disaster_event_id: serviceData.eventId || null,
            metadata: serviceData.metadata || {}
        });

        return response.data;
    } catch (error) {
        console.error('Failed to create service request:', error);
        throw error;
    }
};

// Usage
const service = await createServiceRequest({
    type: 'MEDICAL',
    priority: 'CRITICAL',
    lat: 17.3850,
    lng: 78.4867,
    address: 'Charminar, Hyderabad, Telangana',
    description: 'Urgent medical attention needed for elderly person',
    privacy: 'PROTECTED'
});

console.log('Service request created:', service.service_id);
```

**Response** (201 Created):
```json
{
  "status": "success",
  "message": "Service request created successfully",
  "data": {
    "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "status": "SUBMITTED",
    "created_at": "2026-05-10T10:45:00Z",
    "estimated_response_time": "30 minutes",
    "next_action": "Request is being reviewed by authorities"
  }
}
```

---

### 4.2 Get Service Requests (List)

**Endpoint**: `GET /services`

**Query Parameters**:
- `lat` - Latitude (required if using radius)
- `lng` - Longitude (required if using radius)
- `radius` - Search radius in meters (default: 5000)
- `service_type` - Filter by type (MEDICAL, FOOD, etc.)
- `status` - Filter by status (APPROVED, IN_PROGRESS, etc.)
- `priority` - Filter by priority (CRITICAL, HIGH, etc.)
- `page` - Page number (default: 1)
- `per_page` - Results per page (default: 20, max: 100)

**Request**:
```javascript
const getServiceRequests = async (filters = {}) => {
    try {
        // Build query string
        const params = new URLSearchParams();
        
        if (filters.lat && filters.lng) {
            params.append('lat', filters.lat);
            params.append('lng', filters.lng);
            params.append('radius', filters.radius || 5000);
        }
        
        if (filters.type) params.append('service_type', filters.type);
        if (filters.status) params.append('status', filters.status);
        if (filters.priority) params.append('priority', filters.priority);
        if (filters.page) params.append('page', filters.page);
        if (filters.perPage) params.append('per_page', filters.perPage);

        const response = await api.get(`/services?${params.toString()}`);
        return response.data;
    } catch (error) {
        console.error('Failed to get services:', error);
        throw error;
    }
};

// Usage - Get services near a location
const result = await getServiceRequests({
    lat: 17.3850,
    lng: 78.4867,
    radius: 10000,  // 10km
    status: 'APPROVED',
    page: 1,
    perPage: 20
});

console.log(`Found ${result.pagination.total} services`);
result.services.forEach(service => {
    console.log(`${service.service_type} - ${service.distance_meters}m away`);
});
```

**Response** (200 OK):
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
        "description": "Urgent medical attention needed...",
        "distance_meters": 1250.5,
        "created_at": "2026-05-10T10:45:00Z",
        "assigned_to": {
          "user_id": "...",
          "full_name": "Dr. Smith",
          "organization": "City Hospital"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 145,
      "pages": 8,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

### 4.3 Get Single Service Request

**Endpoint**: `GET /services/{service_id}`

**Request**:
```javascript
const getServiceById = async (serviceId) => {
    try {
        const response = await api.get(`/services/${serviceId}`);
        return response.data;
    } catch (error) {
        console.error('Failed to get service:', error);
        throw error;
    }
};

// Usage
const service = await getServiceById('f9e8d7c6-b5a4-3210-fedc-ba9876543210');
console.log('Service:', service);
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "requestor_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "service_type": "MEDICAL",
    "priority": "CRITICAL",
    "location": {
      "type": "Point",
      "coordinates": [78.4867, 17.3850]
    },
    "address": "Charminar, Hyderabad, Telangana",
    "description": "Urgent medical attention needed for elderly person",
    "privacy_level": "PROTECTED",
    "status": "IN_PROGRESS",
    "assigned_to": {
      "user_id": "p1",
      "full_name": "Dr. Smith",
      "organization": "City Hospital",
      "phone": "9999999999"
    },
    "disaster_event_id": null,
    "estimated_completion": "2026-05-10T12:00:00Z",
    "created_at": "2026-05-10T10:45:00Z",
    "updated_at": "2026-05-10T11:15:00Z",
    "metadata": {
      "patient_age": 75,
      "symptoms": ["chest pain", "shortness of breath"]
    }
  }
}
```

---

### 4.4 Update Service Status

**Endpoint**: `PUT /services/{service_id}/status`

**Request**:
```javascript
const updateServiceStatus = async (serviceId, newStatus, notes = null) => {
    try {
        const response = await api.put(`/services/${serviceId}/status`, {
            status: newStatus,
            notes: notes
        });
        return response.data;
    } catch (error) {
        console.error('Failed to update status:', error);
        throw error;
    }
};

// Usage - Provider marks service as in progress
await updateServiceStatus(
    'f9e8d7c6-b5a4-3210-fedc-ba9876543210',
    'IN_PROGRESS',
    'On the way to location'
);
```

---

### 4.5 Complete Service (Provider)

**Endpoint**: `POST /services/{service_id}/complete`

**Request**:
```javascript
const completeService = async (serviceId, proof) => {
    try {
        const response = await api.post(`/services/${serviceId}/complete`, {
            completion_notes: proof.notes,
            proof_photo_url: proof.photoUrl  // Upload photo first, get URL
        });
        return response.data;
    } catch (error) {
        console.error('Failed to complete service:', error);
        throw error;
    }
};

// Usage
await completeService('f9e8d7c6-...', {
    notes: 'Patient treated and stable',
    photoUrl: 'https://storage.example.com/proof/abc123.jpg'
});
```

---

### 4.6 Verify Service Completion (Citizen)

**Endpoint**: `POST /services/{service_id}/verify`

**Request**:
```javascript
const verifyService = async (serviceId, rating, feedback = null) => {
    try {
        const response = await api.post(`/services/${serviceId}/verify`, {
            verified: true,
            rating: rating,  // 1-5
            feedback: feedback
        });
        return response.data;
    } catch (error) {
        console.error('Failed to verify service:', error);
        throw error;
    }
};

// Usage - Citizen confirms service was delivered
await verifyService('f9e8d7c6-...', 5, 'Excellent service, very professional');
```

---

## 5. Map & Geospatial APIs

### 5.1 Get GeoJSON Features

**Endpoint**: `GET /geo/services`

**Query Parameters**:
- `bounds` - Map bounds (format: `minLng,minLat,maxLng,maxLat`)
- `service_type` - Filter by type
- `status` - Filter by status

**Request**:
```javascript
const getServicesGeoJSON = async (bounds, filters = {}) => {
    try {
        const params = new URLSearchParams({
            bounds: bounds.join(',')  // [minLng, minLat, maxLng, maxLat]
        });
        
        if (filters.type) params.append('service_type', filters.type);
        if (filters.status) params.append('status', filters.status);

        const response = await api.get(`/geo/services?${params.toString()}`);
        return response.data;
    } catch (error) {
        console.error('Failed to get GeoJSON:', error);
        throw error;
    }
};

// Usage with Leaflet map
const bounds = map.getBounds();
const geoJSON = await getServicesGeoJSON([
    bounds.getWest(),
    bounds.getSouth(),
    bounds.getEast(),
    bounds.getNorth()
], { status: 'APPROVED' });

// Add to map
L.geoJSON(geoJSON).addTo(map);
```

**Response** (200 OK):
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
          "status": "APPROVED",
          "address": "Charminar, Hyderabad",
          "created_at": "2026-05-10T10:45:00Z"
        }
      }
    ]
  }
}
```

---

### 5.2 Get Map Tiles

**Endpoint**: `GET /geo/tiles/{z}/{x}/{y}.png`

**Usage with Leaflet**:
```javascript
// Add tile layer to map
const tileLayer = L.tileLayer(
    'http://localhost:3000/api/geo/tiles/{z}/{x}/{y}.png',
    {
        attribution: 'IDRM',
        maxZoom: 18,
        minZoom: 1
    }
);

tileLayer.addTo(map);
```

**Response**: PNG image (256x256 pixels)

---

### 5.3 Clustering

**Endpoint**: `POST /geo/cluster`

**Request**:
```javascript
const clusterServices = async (serviceIds, numClusters = 10) => {
    try {
        const response = await api.post('/geo/cluster', {
            service_ids: serviceIds,
            k: numClusters
        });
        return response.data;
    } catch (error) {
        console.error('Failed to cluster:', error);
        throw error;
    }
};

// Usage
const clusters = await clusterServices(
    ['service_id_1', 'service_id_2', ...],
    5  // 5 clusters
);

clusters.forEach(cluster => {
    console.log(`Cluster at [${cluster.center}] has ${cluster.count} services`);
});
```

**Response** (200 OK):
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
        }
      }
    ]
  }
}
```

---

## 6. User & Organization APIs

### 6.1 Get User Profile

**Endpoint**: `GET /users/me`

(See Section 3.4)

---

### 6.2 Update User Profile

**Endpoint**: `PUT /users/me`

**Request**:
```javascript
const updateProfile = async (updates) => {
    try {
        const response = await api.put('/users/me', {
            full_name: updates.fullName,
            phone: updates.phone
            // Cannot update email or role
        });
        return response.data;
    } catch (error) {
        console.error('Failed to update profile:', error);
        throw error;
    }
};

// Usage
const user = await updateProfile({
    fullName: 'John Michael Doe',
    phone: '9876543211'
});
```

---

### 6.3 Register Organization

**Endpoint**: `POST /organizations`

**Request**:
```javascript
const registerOrganization = async (orgData) => {
    try {
        const response = await api.post('/organizations', {
            name: orgData.name,
            type: orgData.type,  // 'NGO', 'GOVERNMENT', etc.
            registration_number: orgData.regNumber,
            address: orgData.address,
            location: {
                type: 'Point',
                coordinates: [orgData.lng, orgData.lat]
            },
            contact_email: orgData.email,
            contact_phone: orgData.phone,
            description: orgData.description
        });
        return response.data;
    } catch (error) {
        console.error('Failed to register organization:', error);
        throw error;
    }
};
```

---

## 7. Analytics & Reports APIs

### 7.1 Get Dashboard Data

**Endpoint**: `GET /analytics/dashboard`

**Request**:
```javascript
const getDashboardData = async () => {
    try {
        const response = await api.get('/analytics/dashboard');
        return response.data;
    } catch (error) {
        console.error('Failed to get dashboard:', error);
        throw error;
    }
};

// Usage
const dashboard = await getDashboardData();
console.log('Total requests:', dashboard.total_requests);
console.log('Critical pending:', dashboard.critical_pending);
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "total_requests": 1250,
    "by_status": {
      "SUBMITTED": 45,
      "APPROVED": 120,
      "IN_PROGRESS": 85,
      "COMPLETED": 950,
      "VERIFIED": 850
    },
    "by_priority": {
      "CRITICAL": 12,
      "HIGH": 145,
      "MEDIUM": 680,
      "LOW": 413
    },
    "avg_response_time_minutes": 42,
    "completion_rate": 0.85,
    "top_service_types": [
      { "type": "FOOD", "count": 450 },
      { "type": "MEDICAL", "count": 350 },
      { "type": "SHELTER", "count": 250 }
    ]
  }
}
```

---

## 8. Error Handling

### 8.1 Error Response Format

All errors follow this format:

```json
{
  "status": "error",
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {},
  "timestamp": "2026-05-10T12:00:00Z",
  "request_id": "req_abc123"
}
```

### 8.2 HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | Request succeeded |
| 201 | Created | Resource created |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limited |
| 500 | Server Error | Internal error |

### 8.3 Error Handling Pattern

```javascript
// Display user-friendly error messages
const handleAPIError = (error) => {
    let message = 'An unexpected error occurred';
    
    if (error instanceof APIError) {
        switch (error.status) {
            case 400:
                message = error.details?.errors
                    ? error.details.errors.map(e => e.message).join(', ')
                    : error.message;
                break;
            case 401:
                message = 'Please login to continue';
                // Redirect to login
                setTimeout(() => {
                    window.location.href = '/login.html';
                }, 2000);
                break;
            case 403:
                message = 'You do not have permission to perform this action';
                break;
            case 404:
                message = 'The requested resource was not found';
                break;
            case 429:
                message = 'Too many requests. Please try again later.';
                break;
            default:
                message = error.message || 'An unexpected error occurred';
        }
    }
    
    // Show error to user
    showNotification(message, 'error');
    
    return message;
};

// Usage
try {
    const service = await createServiceRequest(data);
    showNotification('Service request created!', 'success');
} catch (error) {
    handleAPIError(error);
}
```

---

## 9. Code Examples

### 9.1 Complete Login Flow

**File**: `js/auth.js`

```javascript
// Check if user is logged in
const isLoggedIn = () => {
    return !!api.getToken() && !!localStorage.getItem('user');
};

// Get current user from localStorage
const getCurrentUser = () => {
    const userJson = localStorage.getItem('user');
    return userJson ? JSON.parse(userJson) : null;
};

// Login form handler
document.getElementById('login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        showLoading('Logging in...');
        
        const user = await login(email, password);
        
        hideLoading();
        showNotification(`Welcome back, ${user.full_name}!`, 'success');
        
        // Redirect to dashboard
        window.location.href = '/dashboard.html';
        
    } catch (error) {
        hideLoading();
        handleAPIError(error);
    }
});

// Logout handler
document.getElementById('logout-btn')?.addEventListener('click', async (e) => {
    e.preventDefault();
    
    if (confirm('Are you sure you want to logout?')) {
        await logout();
    }
});

// Protect pages - redirect if not logged in
const protectPage = () => {
    if (!isLoggedIn()) {
        window.location.href = '/login.html';
    }
};

// Call on protected pages
if (window.location.pathname !== '/login.html' && 
    window.location.pathname !== '/register.html') {
    protectPage();
}
```

---

### 9.2 Complete Service Request Creation

**File**: `js/services.js`

```javascript
// Service request form handler
document.getElementById('service-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        type: document.getElementById('service-type').value,
        priority: document.getElementById('priority').value,
        lat: parseFloat(document.getElementById('latitude').value),
        lng: parseFloat(document.getElementById('longitude').value),
        address: document.getElementById('address').value,
        description: document.getElementById('description').value,
        privacy: document.getElementById('privacy-level').value
    };
    
    try {
        showLoading('Creating service request...');
        
        const service = await createServiceRequest(formData);
        
        hideLoading();
        showNotification(
            `Service request created! ID: ${service.service_id}`,
            'success'
        );
        
        // Reset form
        e.target.reset();
        
        // Redirect to view page
        window.location.href = `/service-detail.html?id=${service.service_id}`;
        
    } catch (error) {
        hideLoading();
        handleAPIError(error);
    }
});
```

---

### 9.3 Map with Services

**File**: `js/map.js`

```javascript
// Initialize map
const map = L.map('map').setView([17.3850, 78.4867], 13);

// Add tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Load services on map
const loadServicesOnMap = async () => {
    try {
        const center = map.getCenter();
        
        const services = await getServiceRequests({
            lat: center.lat,
            lng: center.lng,
            radius: 10000,  // 10km
            status: 'APPROVED'
        });
        
        // Clear existing markers
        map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                map.removeLayer(layer);
            }
        });
        
        // Add markers for each service
        services.services.forEach(service => {
            const [lng, lat] = service.location.coordinates;
            
            // Choose icon color by priority
            const iconColor = {
                'CRITICAL': 'red',
                'HIGH': 'orange',
                'MEDIUM': 'yellow',
                'LOW': 'blue'
            }[service.priority];
            
            const marker = L.marker([lat, lng], {
                icon: L.icon({
                    iconUrl: `/assets/markers/${iconColor}-marker.png`,
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34]
                })
            }).addTo(map);
            
            // Add popup
            marker.bindPopup(`
                <div class="service-popup">
                    <h4>${service.service_type}</h4>
                    <p><strong>Priority:</strong> ${service.priority}</p>
                    <p><strong>Status:</strong> ${service.status}</p>
                    <p>${service.description.substring(0, 100)}...</p>
                    <a href="/service-detail.html?id=${service.service_id}">
                        View Details
                    </a>
                </div>
            `);
        });
        
    } catch (error) {
        console.error('Failed to load services:', error);
        handleAPIError(error);
    }
};

// Load on page load
loadServicesOnMap();

// Reload when map moves
map.on('moveend', loadServicesOnMap);
```

---

### 9.4 Dashboard with Real-time Updates

**File**: `js/dashboard.js`

```javascript
// Load dashboard data
const loadDashboard = async () => {
    try {
        const data = await getDashboardData();
        
        // Update counts
        document.getElementById('total-requests').textContent = 
            data.total_requests;
        document.getElementById('critical-pending').textContent = 
            data.by_priority.CRITICAL;
        document.getElementById('completion-rate').textContent = 
            `${(data.completion_rate * 100).toFixed(1)}%`;
        document.getElementById('avg-response-time').textContent = 
            `${data.avg_response_time_minutes} min`;
        
        // Update chart
        updateStatusChart(data.by_status);
        
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
};

// Update status chart (using Chart.js)
const updateStatusChart = (statusData) => {
    new Chart(document.getElementById('status-chart'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(statusData),
            datasets: [{
                data: Object.values(statusData),
                backgroundColor: [
                    '#fbbf24', // SUBMITTED - yellow
                    '#10b981', // APPROVED - green
                    '#3b82f6', // IN_PROGRESS - blue
                    '#8b5cf6', // COMPLETED - purple
                    '#059669'  // VERIFIED - dark green
                ]
            }]
        }
    });
};

// Auto-refresh every 30 seconds
setInterval(loadDashboard, 30000);

// Initial load
loadDashboard();
```

---

## Appendix: Quick Reference

### API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/register` | POST | Register user |
| `/auth/login` | POST | Login |
| `/auth/logout` | POST | Logout |
| `/auth/refresh` | POST | Refresh token |
| `/users/me` | GET | Get current user |
| `/users/me` | PUT | Update profile |
| `/services` | POST | Create request |
| `/services` | GET | List requests |
| `/services/{id}` | GET | Get request |
| `/services/{id}/status` | PUT | Update status |
| `/services/{id}/complete` | POST | Complete |
| `/services/{id}/verify` | POST | Verify |
| `/geo/services` | GET | GeoJSON |
| `/geo/tiles/{z}/{x}/{y}.png` | GET | Map tiles |
| `/geo/cluster` | POST | Cluster |
| `/organizations` | POST | Register org |
| `/analytics/dashboard` | GET | Dashboard |

---

**END OF API INTEGRATION GUIDE**

**Version**: 2.0  
**Last Updated**: May 10, 2026  
**Next**: See instructions_pages_v2.md for complete page examples
