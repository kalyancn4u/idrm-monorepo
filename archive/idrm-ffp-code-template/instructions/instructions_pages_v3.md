# IDRM v3 — Page-by-Page Reference
## Every Screen Across All Three Platforms

**Source**: backup/47-FRONTEND-WORKFLOWS-REFERENCE.md  
**Version**: 3.0  
**Audience**: Frontend developers, UI designers, QA engineers  
**Last Updated**: May 30, 2026

> **How to use this file**: Each page entry lists what it shows, what API calls it makes, who can access it, and what the user can do. Use this when adding a feature to a specific page or debugging a workflow.

---

## Platform Overview — Which Platform Serves Which User

| Platform | Location | Port | Primary User | Purpose |
|----------|----------|------|-------------|---------|
| **HTML/Tailwind** | `src/frontend/web-html/` | 5173 | Citizens in crisis | Fast, lightweight. Works in low-bandwidth emergencies |
| **React SPA** | `src/frontend/web-react/` | 5174 | Admins & Coordinators | Rich dashboards, data tables, charts, real-time maps |
| **React Native** | `src/frontend/mobile-expo/` | Expo | Field Workers | GPS, push notifications, offline-first, iOS + Android |

---

## Part 1 — HTML/Tailwind Pages (`src/frontend/web-html/`)

### Complete Page Inventory

```
src/frontend/web-html/src/
├── index.html                    # Homepage (public)
├── about.html                    # About IDRM (public)
├── auth/
│   ├── register.html             # Create account
│   ├── login.html                # Sign in
│   └── forgot-password.html      # Reset password
├── pages/
│   ├── app/
│   │   ├── dashboard.html        # Citizen dashboard
│   │   ├── create-service.html   # Request help form
│   │   ├── service-detail.html   # Track a request
│   │   ├── my-services.html      # All my requests
│   │   ├── map.html              # Live map of all requests
│   │   ├── profile.html          # User settings
│   │   └── notifications.html    # Alerts & updates
│   ├── provider/
│   │   ├── provider-dashboard.html  # Provider control panel
│   │   ├── available-services.html  # Services to accept
│   │   └── active-services.html     # Assigned services
│   └── admin/
│       ├── admin-dashboard.html     # Admin panel
│       ├── admin-users.html         # Manage users
│       └── admin-analytics.html     # Reports
```

---

### Page 1.1 — Homepage (`index.html`)

**Who sees it**: Everyone (no login required)  
**Purpose**: Landing page, explains IDRM, links to register/login  
**API calls**: None  
**Key elements**: Hero banner, "Request Help" CTA, "Register as Provider" CTA, emergency hotline numbers  
**Redirect logic**: If user is already logged in (token in storage), redirect to `dashboard.html`

---

### Page 1.2 — Register (`auth/register.html`)

**Who sees it**: New users (no login required)  
**API call**: `POST /api/v1/auth/register`  
**Form fields**: email, password, full_name, phone, role (CITIZEN default)  
**On success**: Show "check your email" message → redirect to `login.html` after 3 seconds  
**Validation**: Client-side before API call — email format, password strength (≥8 chars, 1 upper, 1 number), phone 10 digits  
**Error cases**: duplicate email (409), invalid phone format (422)

---

### Page 1.3 — Login (`auth/login.html`)

**Who sees it**: Existing users (no login required)  
**API call**: `POST /api/v1/auth/login`  
**Form fields**: email, password  
**On success**: Store `access_token` + `refresh_token` in `sessionStorage` → redirect to `dashboard.html`  
**On failure**: Show "Invalid email or password" toast (never say which field is wrong — security)  
**Auto-refresh**: JavaScript `setInterval` calls `/auth/refresh` 1 minute before token expiry

---

### Page 1.4 — Forgot Password (`auth/forgot-password.html`)

**Who sees it**: Users who forgot password (no login required)  
**API call**: `POST /api/v1/auth/forgot-password` → `POST /api/v1/auth/reset-password`  
**Flow**: Enter email → receive link → click link (has `?token=xxx` in URL) → enter new password  
**Note**: Reset token in URL is single-use, expires in 1 hour

---

### Page 1.5 — Dashboard (`pages/app/dashboard.html`)

**Who sees it**: Any authenticated user  
**Auth required**: ✅ Yes — redirect to login if no token  
**API calls**:
- `GET /api/v1/users/me` — load user's name and role
- `GET /api/v1/services/requests?status=SUBMITTED,IN_PROGRESS` — user's active requests
- `GET /api/v1/notifications?read=false` — unread count badge
- `GET /api/v1/analytics/dashboard` (coordinators/admins only)

**What it shows**:
- Welcome message with user's name
- Count of active requests
- Quick action buttons: "Request Help", "View Map", "My Requests"
- Recent notifications panel
- Mini-map showing user's own requests

**Role-based content**:
- `CITIZEN` → shows own requests, "Request Help" button prominent
- `PROVIDER` → shows assigned/available requests, accept/reject actions
- `DM_AUTHORITY/ADMIN` → shows full analytics summary, pending approvals

---

### Page 1.6 — Create Service Request (`pages/app/create-service.html`)

**Who sees it**: Citizens and Volunteers  
**Auth required**: ✅ Yes  
**API calls**:
- `GET /api/v1/users/me` — pre-fill contact phone
- `POST /api/v1/services/requests` — submit the request

**Form fields**:

| Field | Input Type | Required | Validation |
|-------|-----------|----------|-----------|
| service_type | dropdown | ✅ | Must select from enum list |
| priority | dropdown | ✅ | Must select from enum list |
| description | textarea | ✅ | 10–500 characters |
| location | Leaflet map pin | ✅ | Click map or "Use my location" button |
| address | text input | ❌ | Auto-filled from reverse geocode |
| privacy_level | radio buttons | ✅ | PUBLIC / PROTECTED / PRIVATE |
| num_people_affected | number | ❌ | 1–1000, default 1 |
| contact_phone | tel input | ❌ | Defaults to user's phone |

**On success**: Show success toast with request ID → redirect to `service-detail.html?id={id}`  
**GPS flow**: "Use my location" calls `navigator.geolocation.getCurrentPosition()` → reverse geocodes via Nominatim API

---

### Page 1.7 — Service Detail (`pages/app/service-detail.html?id={uuid}`)

**Who sees it**: Requestor, assigned provider, coordinators, admins  
**Auth required**: ✅ Yes  
**API calls**:
- `GET /api/v1/services/requests/{id}` — load full request object
- `PUT /api/v1/services/requests/{id}/status` (providers/coordinators only)
- WebSocket subscription to `service_requests` channel — real-time status updates

**What it shows**:
- Request status badge (with colour: CRITICAL=red, HIGH=orange, etc.)
- Full description, location on mini-map
- Timeline of status changes
- Assigned provider card (name, org, phone, ETA) when status ≥ `ACCEPTED`
- Rating form (1–5 stars) when status = `COMPLETED`

**Role-based actions**:
- `CITIZEN` → "Cancel Request" (if SUBMITTED), "Confirm Completion" + rating form (if COMPLETED)
- `PROVIDER` → "Accept Request" (if APPROVED), "Mark In Progress", "Mark Complete"
- `DM_AUTHORITY/ADMIN` → "Approve", "Reject", "Reassign Provider"

---

### Page 1.8 — My Services (`pages/app/my-services.html`)

**Who sees it**: Any authenticated user  
**Auth required**: ✅ Yes  
**API call**: `GET /api/v1/services/requests` with server-side filtering by `requestor_id`  
**Filters available**: status, service_type, date range  
**Pagination**: 20 per page  
**Quick actions**: Link to service detail, cancel button (if SUBMITTED)

---

### Page 1.9 — Map View (`pages/app/map.html`)

**Who sees it**: Any authenticated user  
**Auth required**: ✅ Yes  
**API calls**:
- `GET /api/v1/geo/nearby?latitude=...&longitude=...&radius=10` — initial load
- `GET /api/v1/geo/cluster?zoom={n}&bounds={...}` — when zoomed out
- WebSocket `service_requests` channel — real-time marker updates

**Libraries**: Leaflet 1.9.4, OpenStreetMap tiles (free, no API key)

**Map features**:
- Colour-coded markers by priority (red=CRITICAL, orange=HIGH, yellow=MEDIUM, green=LOW)
- Cluster circles when zoomed out (count shown, colour = highest priority inside)
- Click marker → sidebar shows request summary + link to service detail
- "Request here" button on right-click
- "Find nearest provider" search within radius
- Filter panel (by service type, status, priority)

---

### Page 1.10 — Notifications (`pages/app/notifications.html`)

**Who sees it**: Any authenticated user  
**Auth required**: ✅ Yes  
**API calls**:
- `GET /api/v1/notifications` — list all notifications
- `PUT /api/v1/notifications/{id}/read` — mark as read
- `PUT /api/v1/notifications/read-all` — mark all as read

**What it shows**: Sorted by newest first. Unread notifications highlighted. Click to navigate to related request.

---

### Page 1.11 — Profile (`pages/app/profile.html`)

**Who sees it**: Any authenticated user  
**Auth required**: ✅ Yes  
**API calls**:
- `GET /api/v1/users/me` — load current profile
- `PUT /api/v1/users/me` — save changes

**Editable fields**: full_name, phone, language_preference  
**Non-editable on this page**: email, role (requires admin action)  
**Password change**: separate form that calls `POST /api/v1/auth/change-password`

---

### Pages 1.12–1.14 — Provider Pages

| Page | Auth | API Calls | Purpose |
|------|------|-----------|---------|
| `provider-dashboard.html` | PROVIDER role | `/users/me`, `/services?provider=me` | Overview of assigned work |
| `available-services.html` | PROVIDER role | `GET /geo/nearby` filtered by provider's service_types | Browse and accept open requests |
| `active-services.html` | PROVIDER role | `GET /services?status=ACCEPTED,IN_PROGRESS&provider=me` | Manage ongoing assignments |

**Accept flow**: Provider taps "Accept" → `POST /services/{id}/accept` → map updates for requestor in real-time via WebSocket

---

### Pages 1.15–1.17 — Admin Pages (React SPA only — not in HTML/Tailwind)

> Admin pages live in `src/frontend/web-react/` (Port 5174), not in the HTML/Tailwind platform. See Part 2.

---

## Part 2 — React SPA Pages (`src/frontend/web-react/`, Port 5174)

**Framework**: React 18 + TypeScript + Vite  
**Routing**: React Router v6  
**State**: React Query (server state) + Zustand (client state)  
**Charts**: Recharts  
**Maps**: Leaflet + react-leaflet

### Page Inventory

```
src/frontend/web-react/src/
├── pages/
│   ├── auth/
│   │   └── Login.tsx             # Admin login
│   ├── dashboard/
│   │   └── Dashboard.tsx         # Main overview with live stats
│   ├── requests/
│   │   ├── RequestList.tsx       # All service requests, filterable
│   │   ├── RequestDetail.tsx     # Full request + audit trail
│   │   └── RequestApproval.tsx   # Bulk approve/reject queue
│   ├── users/
│   │   ├── UserList.tsx          # All users with search
│   │   └── UserDetail.tsx        # User profile + actions
│   ├── providers/
│   │   ├── ProviderList.tsx      # All organizations
│   │   └── ProviderDetail.tsx    # Org profile + verify action
│   ├── analytics/
│   │   ├── Overview.tsx          # Top-level stats
│   │   ├── ByRegion.tsx          # Geographic heatmaps
│   │   └── Reports.tsx           # Exportable reports
│   └── map/
│       └── LiveMap.tsx           # Full-screen real-time map
```

### Key Admin API calls (not available to CITIZEN role)

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/admin/users` | List all users with filters |
| `PATCH /api/v1/admin/users/{id}` | Deactivate, change role |
| `GET /api/v1/admin/audit-logs` | Full action history |
| `POST /api/v1/services/requests/{id}/approve` | Approve a pending request |
| `POST /api/v1/services/requests/{id}/reject` | Reject with reason |
| `GET /api/v1/analytics/dashboard` | Aggregated stats |

---

## Part 3 — React Native / Expo Pages (`src/frontend/mobile-expo/`)

**Framework**: React Native 0.74 + Expo SDK 51  
**Navigation**: React Navigation 6 (Stack + Tab)  
**Maps**: React Native Maps  
**Storage**: AsyncStorage (tokens), MMKV (offline data)  
**Push notifications**: Expo Notifications

### Screen Inventory

```
src/frontend/mobile-expo/src/
├── screens/
│   ├── auth/
│   │   ├── WelcomeScreen.tsx     # App launch, login/register CTAs
│   │   ├── LoginScreen.tsx
│   │   └── RegisterScreen.tsx
│   ├── citizen/
│   │   ├── HomeScreen.tsx        # Quick action buttons, status overview
│   │   ├── MapScreen.tsx         # Full-screen live map
│   │   ├── CreateRequestScreen.tsx  # Multi-step request form
│   │   └── MyRequestsScreen.tsx  # List of own requests
│   ├── provider/
│   │   ├── ProviderHomeScreen.tsx   # Incoming request notifications
│   │   ├── NearbyScreen.tsx         # Map of nearby requests
│   │   └── ActiveScreen.tsx         # Current assignment
│   ├── shared/
│   │   ├── RequestDetailScreen.tsx  # Works for both citizen & provider
│   │   ├── NotificationsScreen.tsx
│   │   └── ProfileScreen.tsx
│   └── coordinator/
│       └── ApprovalQueueScreen.tsx  # Quick approve/reject on mobile
```

### Mobile-specific features

| Feature | How it works |
|---------|-------------|
| **GPS location** | `expo-location` — used when creating requests and for provider proximity |
| **Push notifications** | `expo-notifications` — receives `request_assigned`, `status_update` events |
| **Offline mode** | MMKV caches last-known requests. Queue POST requests for when connectivity returns |
| **Background sync** | `expo-task-manager` — provider location updates every 30 seconds while active |
| **Biometric auth** | `expo-local-authentication` — optional PIN/fingerprint for returning users |

### Mobile token storage

**Never use `sessionStorage` on mobile** — it doesn't exist in React Native. Instead:
```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

// Store
await AsyncStorage.setItem('access_token', token);

// Retrieve
const token = await AsyncStorage.getItem('access_token');

// Clear on logout
await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
```

---

## Part 4 — Cross-Platform Rules

### Authentication guard pattern

Every protected page must check for a valid token on mount. If missing or expired:

**HTML/Tailwind**:
```javascript
// At top of every protected page's script
const token = sessionStorage.getItem('access_token');
if (!token) { window.location.href = '/auth/login.html'; }
```

**React (SPA)**:
```typescript
// ProtectedRoute component wrapping all authenticated routes
if (!auth.token) return <Navigate to="/login" replace />;
```

**React Native**:
```typescript
// In navigation stack — user stack vs auth stack split
if (!auth.token) return <AuthNavigator />;
return <AppNavigator />;
```

### Role-based access

| Role | HTML platform | React SPA | Mobile |
|------|--------------|-----------|--------|
| CITIZEN | All citizen pages | Read-only dashboard | Full citizen flow |
| VOLUNTEER | Same as CITIZEN | Same as CITIZEN | Same as CITIZEN |
| SERVICE_PROVIDER | Provider pages | Provider tab | Full provider flow |
| DM_AUTHORITY | All citizen + approve actions | Full coordinator view | Approval queue |
| ADMIN | All pages | All pages incl. user management | Approval queue |
| DM_AUTHORITY | Same as ADMIN | Same as ADMIN | Same as ADMIN |

### Real-time WebSocket integration

All three platforms connect to `ws://localhost:3001` (dev) / `wss://api.idrm.gov.in/ws` (prod).

Subscribe immediately after login:
```javascript
const ws = new WebSocket('ws://localhost:3001');
ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'subscribe', channel: 'service_requests' }));
};
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Update UI based on data.type: 'request_created' | 'request_updated' | 'request_deleted'
};
```
