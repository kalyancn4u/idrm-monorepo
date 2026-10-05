# IDRM v3 — HTML/Tailwind Web Platform Guide
## Detailed Developer Reference for `src/frontend/web-html/`

**Source**: backup/47-FRONTEND-WORKFLOWS-REFERENCE.md · backup/51-BUN-API-GATEWAY-GUIDE.md  
**Version**: 3.0  
**Audience**: Frontend developers working on the citizen-facing HTML/Tailwind platform  
**Last Updated**: May 30, 2026

> **What is this platform?** The HTML/Tailwind web interface is the primary way citizens access IDRM during a disaster. It is deliberately lightweight — no heavy JavaScript framework, fast to load even on 2G, works in low-connectivity emergencies. It runs on Port 5173 in development and is served via NGINX in production.

---

## Part 1 — Project Structure

```
src/frontend/web-html/
├── package.json              # Bun workspace config, Tailwind build script
├── vite.config.ts            # Dev server (port 5173), proxy to gateway
├── tailwind.config.js        # Custom IDRM colours and themes
├── src/
│   ├── index.html            # Homepage (public)
│   ├── about.html
│   ├── auth/
│   │   ├── register.html
│   │   ├── login.html
│   │   └── forgot-password.html
│   ├── pages/
│   │   ├── app/              # Authenticated citizen pages
│   │   ├── provider/         # Provider-only pages
│   │   └── admin/            # (minimal — full admin is web-react)
│   ├── assets/
│   │   ├── css/
│   │   │   └── tailwind.min.css    # Built Tailwind output
│   │   ├── js/
│   │   │   ├── api/          # API client modules
│   │   │   │   ├── auth.js       # /auth/* calls
│   │   │   │   ├── services.js   # /services/* calls
│   │   │   │   ├── geo.js        # /geo/* calls
│   │   │   │   └── notifications.js
│   │   │   ├── app.js        # Shared init, token refresh loop
│   │   │   ├── map.js        # Leaflet map helpers
│   │   │   └── utils.js      # Helpers: toast, format, validate
│   │   └── images/
│   └── components/           # Reusable HTML partials (loaded via fetch)
│       ├── navbar.html
│       ├── footer.html
│       └── modals.html
```

**Dev command**: `cd src/frontend/web-html && bun run dev`  
**Build command**: `bun run build` → output in `dist/`

---

## Part 2 — JavaScript Libraries

| Library | Version | Purpose | How included |
|---------|---------|---------|-------------|
| **Tailwind CSS** | 3.4 | All styling | CDN or local build |
| **Axios** | 1.6 | HTTP requests to API | CDN |
| **Leaflet** | 1.9.4 | Interactive maps | CDN |
| **Chart.js** | 4.4 | Bar/pie charts on admin pages | CDN (admin only) |
| **DOMPurify** | 3.0 | Sanitise user HTML (XSS prevention) | CDN |

**Why no React/Vue/Angular?** The HTML platform is intentionally framework-free. During a disaster, citizens may be on cheap phones with 2G. Loading a React bundle (100–300KB) takes precious seconds. Vanilla JS + Tailwind loads in under 30KB.

**CDN links** (copy into `<head>`):
```html
<!-- Tailwind (or use locally built file) -->
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.0/dist/tailwind.min.css" rel="stylesheet">

<!-- Axios -->
<script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"></script>

<!-- Leaflet (only on map pages) -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<!-- DOMPurify (on pages that render user content) -->
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.0.0/dist/purify.min.js"></script>
```

---

## Part 3 — API Integration

### 3.1 How the Web Platform Talks to the Backend

```
Web browser (Port 5173)
    │
    │  HTTP/WebSocket
    ↓
Bun API Gateway (Port 3000)
    │  validates JWT, rate limits, CORS
    │
    ↓
FastAPI Backend (Port 8000)
    │  business logic, DB queries
    │
    ↓
PostgreSQL (Port 5432) + Redis (Port 6379)
```

The web platform **never calls the FastAPI backend directly**. Every request goes through the gateway on port 3000.

**Dev Vite proxy** (in `vite.config.ts`) — so you can call `/api/v1/...` without a full URL:
```typescript
server: {
  port: 5173,
  proxy: {
    '/api': 'http://localhost:3000',
    '/ws':  'ws://localhost:3001'
  }
}
```

---

### 3.2 Axios Setup (shared `assets/js/api/api-client.js`)

```javascript
// Global Axios instance with interceptors
const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

// Attach access token to every request
apiClient.interceptors.request.use(config => {
  const token = sessionStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401: auto-refresh token then retry
apiClient.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      try {
        const refreshToken = sessionStorage.getItem('refresh_token');
        const res = await axios.post('/api/v1/auth/refresh', { refresh_token: refreshToken });
        sessionStorage.setItem('access_token', res.data.data.access_token);
        error.config.headers.Authorization = `Bearer ${res.data.data.access_token}`;
        return apiClient(error.config);
      } catch {
        // Refresh failed — redirect to login
        sessionStorage.clear();
        window.location.href = '/auth/login.html';
      }
    }
    return Promise.reject(error);
  }
);
```

---

### 3.3 Auth API calls (`assets/js/api/auth.js`)

```javascript
const auth = {

  async register(formData) {
    return apiClient.post('/auth/register', formData);
  },

  async login(email, password) {
    const res = await apiClient.post('/auth/login', { email, password });
    const { access_token, refresh_token, user } = res.data.data;
    sessionStorage.setItem('access_token', access_token);
    sessionStorage.setItem('refresh_token', refresh_token);
    sessionStorage.setItem('user', JSON.stringify(user));
    return user;
  },

  logout() {
    apiClient.post('/auth/logout').finally(() => {
      sessionStorage.clear();
      window.location.href = '/auth/login.html';
    });
  },

  currentUser() {
    const raw = sessionStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  },

  isLoggedIn() {
    return !!sessionStorage.getItem('access_token');
  }
};
```

---

### 3.4 Service Request API calls (`assets/js/api/services.js`)

```javascript
const services = {

  async create(requestData) {
    return apiClient.post('/services/requests', requestData);
  },

  async list(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    return apiClient.get(`/services/requests?${params}`);
  },

  async get(serviceId) {
    return apiClient.get(`/services/requests/${serviceId}`);
  },

  async updateStatus(serviceId, status, notes = '') {
    return apiClient.put(`/services/requests/${serviceId}/status`, { status, notes });
  },

  async cancel(serviceId) {
    return this.updateStatus(serviceId, 'CANCELLED');
  }
};
```

---

## Part 4 — Map Integration (Leaflet)

### 4.1 Basic Map Setup

```javascript
// Initialise map centred on India
const map = L.map('map-container', {
  center: [20.5937, 78.9629],  // India centre
  zoom: 5,
  preferCanvas: true           // Better performance for many markers
});

// Free OpenStreetMap tiles (no API key needed)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19
}).addTo(map);
```

### 4.2 Priority-Coloured Markers

```javascript
const PRIORITY_COLOURS = {
  CRITICAL: '#ef4444',  // red-500
  HIGH:     '#f97316',  // orange-500
  MEDIUM:   '#eab308',  // yellow-500
  LOW:      '#22c55e'   // green-500
};

function createMarker(request) {
  const colour = PRIORITY_COLOURS[request.priority] || '#6b7280';

  const icon = L.divIcon({
    className: '',
    html: `<div style="width:16px;height:16px;border-radius:50%;
                       background:${colour};border:2px solid white;
                       box-shadow:0 1px 3px rgba(0,0,0,0.4);"></div>`,
    iconSize: [16, 16]
  });

  return L.marker(
    [request.location.coordinates[1], request.location.coordinates[0]],  // lat, lng (note reverse from GeoJSON)
    { icon }
  ).bindPopup(`
    <strong>${request.service_type}</strong><br>
    ${request.address}<br>
    <a href="/pages/app/service-detail.html?id=${request.service_id}">View Details →</a>
  `);
}
```

### 4.3 GPS — Get User's Current Location

```javascript
function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation not supported'));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      pos => resolve({
        latitude:  pos.coords.latitude,
        longitude: pos.coords.longitude
      }),
      err => reject(err),
      { enableHighAccuracy: true, timeout: 5000 }
    );
  });
}

// Usage
try {
  const { latitude, longitude } = await getCurrentLocation();
  // Move map to user's location
  map.setView([latitude, longitude], 14);
  // For API call: longitude first (GeoJSON order)
  const geoJsonCoordinates = [longitude, latitude];
} catch (err) {
  showToast('Could not get your location. Please pin it on the map.', 'warning');
}
```

---

## Part 5 — WebSocket Real-time Updates

```javascript
// assets/js/websocket.js
class IDRMWebSocket {
  constructor() {
    this.ws = null;
    this.reconnectDelay = 1000;
    this.handlers = {};
  }

  connect() {
    const wsUrl = window.location.protocol === 'https:'
      ? 'wss://api.idrm.gov.in/ws'
      : 'ws://localhost:3001';

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectDelay = 1000;
      this.subscribe('service_requests');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const handler = this.handlers[data.type];
      if (handler) handler(data);
    };

    this.ws.onclose = () => {
      // Auto-reconnect with exponential backoff
      setTimeout(() => this.connect(), this.reconnectDelay);
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
    };
  }

  subscribe(channel) {
    this.ws.send(JSON.stringify({ type: 'subscribe', channel }));
  }

  on(eventType, handler) {
    this.handlers[eventType] = handler;
    return this;  // chain: ws.on('request_created', fn).on('request_updated', fn)
  }
}

// Usage on map.html
const ws = new IDRMWebSocket();
ws.connect();
ws.on('request_created', data => addMarkerToMap(data.request));
ws.on('request_updated', data => updateMarkerOnMap(data.request));
ws.on('request_deleted', data => removeMarkerFromMap(data.request.id));
```

---

## Part 6 — UI Patterns & Utilities

### 6.1 Toast Notifications

```javascript
// assets/js/utils.js
function showToast(message, type = 'info') {
  const colours = {
    success: 'bg-green-500',
    error:   'bg-red-500',
    warning: 'bg-yellow-500',
    info:    'bg-blue-500'
  };

  const toast = document.createElement('div');
  toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded shadow-lg text-white
                     ${colours[type]} transition-opacity duration-300`;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
```

### 6.2 Auth Guard (every protected page top)

```javascript
// Paste at top of <script> block on every page in /pages/app/ and /pages/provider/
(function guardAuth() {
  const token = sessionStorage.getItem('access_token');
  const user  = sessionStorage.getItem('user');
  if (!token || !user) {
    window.location.href = '/auth/login.html';
  }
})();
```

### 6.3 Role Guard (provider and admin pages)

```javascript
function requireRole(...allowedRoles) {
  const user = JSON.parse(sessionStorage.getItem('user') || '{}');
  if (!allowedRoles.includes(user.role)) {
    window.location.href = '/pages/app/dashboard.html';
  }
}

// Usage at top of provider-dashboard.html
requireRole('SERVICE_PROVIDER', 'ORG_ADMIN');

// Usage at top of admin pages
requireRole('EVENT_MANAGER', 'DM_AUTHORITY', 'SYSTEM_ADMIN');
```

### 6.4 Form Validation Helpers

```javascript
const validate = {
  email:    v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
  password: v => /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(v),
  phone:    v => /^\+?[1-9]\d{9,14}$/.test(v),  // E.164 format
  uuid:     v => /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v),
  required: v => v !== null && v !== undefined && String(v).trim().length > 0
};
```

### 6.5 Safe HTML Rendering (XSS prevention)

**Never do this** — it allows script injection from user-entered descriptions:
```javascript
element.innerHTML = request.description;  // ❌ XSS vulnerability
```

**Always do this**:
```javascript
element.innerHTML = DOMPurify.sanitize(request.description);  // ✅ Safe
// or for plain text (no HTML at all):
element.textContent = request.description;                    // ✅ Safest
```

---

## Part 7 — How the Bun Gateway Serves This Platform

The HTML/Tailwind platform is served as **static files** by the Bun gateway in development and by NGINX in production.

### Development (Port 5173)

In dev, Vite handles file serving with Hot Module Replacement (HMR). Vite proxies `/api/*` and `/ws` to the Bun gateway at Port 3000:

```
Browser → :5173 (Vite)
           ├── /api/v1/* → :3000 (Bun gateway) → :8000 (FastAPI)
           └── /ws       → :3001 (Bun WebSocket)
```

### Production (via NGINX → Bun)

In production, NGINX handles SSL and routes citizen traffic:

```
User Browser
  ↓ HTTPS :443
NGINX
  ├── idrm.gov.in/       → frontend-web container (NGINX serving dist/)
  └── idrm.gov.in/api/*  → Bun gateway :3000 (proxied)
```

The HTML/Tailwind `dist/` is just static files — NGINX can serve them directly at ~50,000 req/s without touching Bun or FastAPI.

### What the Bun Gateway does for this platform

| Concern | How Bun handles it |
|---------|-------------------|
| **JWT validation** | Checks `Authorization: Bearer ...` header before forwarding to FastAPI |
| **Rate limiting** | 100 req/min per IP for citizens (Redis-backed counters) |
| **CORS** | Allows `idrm.gov.in`, `admin.idrm.gov.in`, `localhost:5173`, `localhost:5174` |
| **Security headers** | Adds `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` to all responses |
| **WebSocket upgrade** | Upgrades `/ws` connections and subscribes to Redis pub/sub for real-time events |

---

## Part 8 — Common Mistakes & Debugging

### 8.1 "My API call returns 401 even though I'm logged in"

1. Check `sessionStorage.getItem('access_token')` in browser DevTools → Application → Session Storage
2. Check if the token has expired (they expire after 15 minutes in dev)
3. Make sure the Axios interceptor in `api-client.js` is loaded before page-specific scripts
4. Check that Vite proxy is running — `bun run dev` output should say "server running"

### 8.2 "My map pin is in the wrong place"

GeoJSON uses `[longitude, latitude]` but Leaflet uses `[latitude, longitude]`:
```javascript
// GeoJSON (from API): [lng, lat]
const coords = request.location.coordinates;  // [78.4867, 17.3850]

// Leaflet expects [lat, lng]:
const marker = L.marker([coords[1], coords[0]]);  // ✅ swap them
```

### 8.3 "CORS error in browser console"

- In dev: make sure both Vite (`:5173`) and Bun gateway (`:3000`) are running
- In dev: calls should go to `/api/v1/...` (relative URL through Vite proxy), NOT `http://localhost:3000/api/...`
- In production: only the domains in the gateway's CORS allowlist can call the API

### 8.4 "WebSocket disconnects every 30 seconds"

Normal — the server sends a ping every 30 seconds. If the client doesn't pong back, the server disconnects. The `IDRMWebSocket` class in Part 5 auto-reconnects with exponential backoff.
