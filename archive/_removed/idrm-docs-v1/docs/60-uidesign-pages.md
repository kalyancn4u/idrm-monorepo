> *Type: Document (specification) · Audience: Frontend devs, designers · Status: Archived — v1 historical generation*

# IDRM Platform Pages & Frontend Specification

> Comprehensive page-by-page breakdown with workflows, JavaScript libraries, and architecture details

<!-- IDRM-CLEANUP doc=v1-60-uipages status=ANNOTATED pass=2026-08-16 -->
> ## 🗺️ SECTION MAP (annotation pass, 2026-08-16)
> Gen-1 UI page designs → current source of truth is [`../../../../docs/mvp/60-uidesign-web-interaction.md`](../../../../docs/mvp/60-uidesign-web-interaction.md)
> (HTML+Tailwind+JS+Leaflet, WCAG 2.2 AA). Public/Authenticated pages · workflows · a11y all map there (⚠ MVP,
> specifics superseded); Performance/real-time bits → FFP. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

## Table of Contents

1. [Frontend Architecture](#frontend-architecture)
2. [Page Catalog](#page-catalog)
3. [JavaScript Libraries](#javascript-libraries)
4. [User Workflows](#user-workflows)
5. [Browser Requirements](#browser-requirements)

---

# Frontend Architecture

## Technology Stack

### Core Technologies
```javascript
{
  "runtime": "Bun 1.x",
  "bundler": "Vite 5.x",
  "language": "JavaScript ES6+ (Vanilla)",
  "styling": "TailwindCSS 3.x",
  "markup": "HTML5 Semantic"
}
```

### JavaScript Libraries

**Mapping & Geospatial**:
```javascript
{
  "leaflet": "1.9.4",              // Core mapping
  "leaflet.markercluster": "1.5.3", // Marker clustering
  "leaflet.draw": "1.0.4",          // Drawing tools
  "leaflet.routing-machine": "3.2.12" // Route calculation
}
```

**Communication**:
```javascript
{
  "socket.io-client": "4.6.0",   // Real-time WebSocket
  "axios": "1.6.0"                // HTTP client
}
```

**Utilities**:
```javascript
{
  "dayjs": "1.11.10",            // Date/time manipulation
  "chart.js": "4.4.0",           // Data visualization
  "validator": "13.11.0",        // Input validation
  "dompurify": "3.0.6"           // XSS protection
}
```

**Optional Enhancement**:
```javascript
{
  "alpinejs": "3.13.0"           // Lightweight reactivity (optional)
}
```

### Build Tools

```json
{
  "devDependencies": {
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "@tailwindcss/forms": "^0.5.0",
    "@tailwindcss/typography": "^0.5.0"
  }
}
```

---

# Page Catalog

## Public Pages (No Authentication Required)

### 1. Landing Page
**File**: `/pages/index.html`  
**Route**: `/`

**Purpose**: Platform introduction and quick access

**Sections**:
- Hero section with disaster alerts
- Quick service request button
- Active disaster zones map
- Statistics (total requests, providers, donations)
- How it works
- Login/Register buttons

**JavaScript Files**:
```javascript
import '/js/pages/landing.js';
import '/js/map/public-map.js';
import '/js/utils/stats-counter.js';
```

**Key Features**:
- Live disaster alerts ticker
- Quick emergency request (redirects to login/register)
- Public map showing active disasters
- Animated statistics counters
- Responsive hero section

**Data Flow**:
```
Page Load → Fetch active disasters (GET /disasters/events/active)
         → Fetch public stats (GET /analytics/public-stats)
         → Initialize public map
         → Display alerts
```

---

### 2. Login Page
**File**: `/pages/login.html`  
**Route**: `/login`

**JavaScript Files**:
```javascript
import '/js/auth/login.js';
import '/js/utils/validation.js';
```

**Form Fields**:
```javascript
{
  "email": {
    "type": "email",
    "required": true,
    "validation": "email format"
  },
  "password": {
    "type": "password",
    "required": true,
    "minLength": 8
  },
  "remember_me": {
    "type": "checkbox",
    "default": false
  }
}
```

**Workflow**:
```
1. User enters credentials
2. Client validates input
3. POST /api/v1/auth/login
4. On success:
   - Store JWT token in localStorage
   - Store refresh token
   - Redirect to role-specific dashboard
5. On failure:
   - Display error message
   - Increment failed attempt counter
   - Lock after 5 failed attempts
```

**Security Features**:
- Client-side validation
- Password visibility toggle
- Rate limiting (5 attempts/15min)
- CSRF token
- Remember me (extended session)

---

### 3. Registration Page
**File**: `/pages/register.html`  
**Route**: `/register`

**JavaScript Files**:
```javascript
import '/js/auth/register.js';
import '/js/map/location-picker.js';
import '/js/utils/validation.js';
```

**Multi-step Form**:

**Step 1: Basic Info**
```javascript
{
  "name": { "required": true, "minLength": 2, "maxLength": 100 },
  "email": { "required": true, "format": "email", "unique": true },
  "phone": { "required": true, "format": "E.164" },
  "password": { 
    "required": true, 
    "minLength": 8,
    "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])"
  }
}
```

**Step 2: Role Selection**
```javascript
{
  "role": {
    "options": ["citizen", "provider"],
    "default": "citizen"
  }
}
```

**Step 3: Location**
```javascript
{
  "location": {
    "latitude": { "required": true, "range": [-90, 90] },
    "longitude": { "required": true, "range": [-180, 180] },
    "address": { "required": true },
    "method": "map_picker | geolocation | manual"
  }
}
```

**Step 4: Provider Info** (if role = provider)
```javascript
{
  "organization_name": { "required": true },
  "registration_number": { "required": true },
  "services_offered": { "type": "array", "required": true }
}
```

**Workflow**:
```
1. Fill basic info → validate → next
2. Select role → conditional fields
3. Pick location on map / use geolocation
4. If provider → additional org info
5. Submit → POST /api/v1/auth/register
6. Auto-login → redirect to dashboard
```

---

## Authenticated Pages

### 4. Map View Page
**File**: `/pages/map.html`  
**Route**: `/map`  
**Access**: All authenticated users

**JavaScript Files**:
```javascript
import '/js/map/map-manager.js';
import '/js/map/layers.js';
import '/js/map/markers.js';
import '/js/map/realtime.js';
import '/js/map/controls.js';
import '/js/utils/websocket.js';
```

**Map Layers**:
```javascript
const layers = {
  "base": {
    "osm": "OpenStreetMap",
    "satellite": "Satellite View"
  },
  "overlays": {
    "disaster_zones": "Active Disaster Zones",
    "service_requests": "Service Requests",
    "providers": "Active Providers",
    "heatmap": "Request Density Heatmap"
  }
};
```

**Marker Types**:
```javascript
const markerTypes = {
  "service_critical": { icon: "red-marker.png", cluster: false },
  "service_high": { icon: "orange-marker.png", cluster: true },
  "service_medium": { icon: "yellow-marker.png", cluster: true },
  "service_low": { icon: "green-marker.png", cluster: true },
  "provider_available": { icon: "blue-marker.png", cluster: false },
  "provider_busy": { icon: "gray-marker.png", cluster: false },
  "disaster_zone": { icon: "disaster-marker.png", cluster: false }
};
```

**Controls**:
- Layer toggle panel
- Filter by type/status/priority
- Search location
- My location button
- Create request (quick access)
- Legend

**Real-time Updates**:
```javascript
// WebSocket listeners
socket.on('service:created', addServiceMarker);
socket.on('service:updated', updateServiceMarker);
socket.on('provider:location', updateProviderMarker);
socket.on('disaster:created', addDisasterZone);
```

**Data Flow**:
```
Page Load → GET /services/requests?status=pending,in-progress
         → GET /providers/available
         → GET /disasters/events/active
         → Initialize map with markers
         → Connect WebSocket
         → Subscribe to real-time updates
         → Update markers as events arrive
```

---

### 5. Create Service Request Page
**File**: `/pages/services/create.html`  
**Route**: `/services/create`  
**Access**: CITIZEN, COORDINATOR, ADMIN

**JavaScript Files**:
```javascript
import '/js/services/service-create.js';
import '/js/map/location-picker.js';
import '/js/utils/media-upload.js';
import '/js/utils/validation.js';
```

**Form Sections**:

**1. Service Type**
```javascript
{
  "type": {
    "options": [
      { "value": "medical", "icon": "medical.svg", "label": "Medical Emergency" },
      { "value": "food", "icon": "food.svg", "label": "Food & Water" },
      { "value": "shelter", "icon": "shelter.svg", "label": "Shelter" },
      { "value": "rescue", "icon": "rescue.svg", "label": "Rescue" },
      { "value": "evacuation", "icon": "evacuation.svg", "label": "Evacuation" },
      { "value": "supplies", "icon": "supplies.svg", "label": "Supplies" }
    ]
  }
}
```

**2. Priority & Category**
```javascript
{
  "priority": ["critical", "high", "medium", "low"],
  "category": ["emergency", "urgent", "normal"]
}
```

**3. Location**
- Interactive map with marker placement
- Current location button
- Address autocomplete
- Landmark field

**4. Contact Information**
```javascript
{
  "contact": {
    "name": { "required": true },
    "phone": { "required": true, "format": "E.164" },
    "alternate_phone": { "optional": true }
  }
}
```

**5. Details** (type-specific)

Medical:
```javascript
{
  "num_people": { "type": "number", "min": 1 },
  "age_group": ["infant", "child", "adult", "elderly"],
  "medical_condition": { "type": "text" },
  "mobility": ["mobile", "limited", "unable"]
}
```

Food:
```javascript
{
  "num_people": { "type": "number", "min": 1 },
  "duration_days": { "type": "number" },
  "dietary_restrictions": { "type": "array" }
}
```

**6. Media Upload**
- Photo upload (max 5 images, 5MB each)
- Client-side image compression
- Preview before upload

**7. Privacy Settings**
```javascript
{
  "is_anonymous": { "type": "boolean", "default": false },
  "share_location": { "type": "boolean", "default": true },
  "share_contact": { "type": "boolean", "default": true }
}
```

**Workflow**:
```
1. Select service type → Show type-specific form
2. Set priority/category
3. Pick location on map
4. Fill contact details
5. Fill type-specific details
6. Upload media (optional)
7. Set privacy preferences
8. Validate all fields
9. POST /api/v1/services/requests
10. On success:
    - Show success message with request ID
    - If anonymous: Show verification code (save prompt)
    - Redirect to service detail page
11. WebSocket: Broadcast new request to coordinators/providers
```

---

### 6. Service List Page
**File**: `/pages/services/list.html`  
**Route**: `/services`  
**Access**: All authenticated users

**JavaScript Files**:
```javascript
import '/js/services/service-list.js';
import '/js/utils/filters.js';
import '/js/utils/pagination.js';
```

**Filters**:
```javascript
{
  "status": {
    "type": "multi-select",
    "options": ["pending", "assigned", "in-progress", "completed", "cancelled"]
  },
  "type": {
    "type": "multi-select",
    "options": ["medical", "food", "shelter", "rescue", "evacuation", "supplies"]
  },
  "priority": {
    "type": "multi-select",
    "options": ["critical", "high", "medium", "low"]
  },
  "date_range": {
    "type": "date-range",
    "fields": ["start_date", "end_date"]
  },
  "location": {
    "type": "radius",
    "fields": ["latitude", "longitude", "radius_km"]
  }
}
```

**View Modes**:
- List view (default)
- Card view
- Map view

**Sorting**:
- Created date (newest/oldest)
- Priority (high to low)
- Distance (nearest first)
- Status

**Pagination**:
- Default: 20 items per page
- Options: 10, 20, 50, 100

**Data Flow**:
```
Page Load → Apply default filters
         → GET /services/requests?filters
         → Render list
         → Setup WebSocket
         → Listen for updates
         
Filter Change → Update URL params
             → GET /services/requests?filters
             → Re-render list
             
Real-time → socket.on('service:updated')
         → Update matching item in list
```

**Access Control**:
- **CITIZEN**: Only their own requests
- **PROVIDER**: Requests in their service area
- **COORDINATOR/ADMIN**: All requests

---

### 7. Service Detail Page
**File**: `/pages/services/detail.html`  
**Route**: `/services/:id`  
**Access**: Creator, Assigned Provider, COORDINATOR, ADMIN

**JavaScript Files**:
```javascript
import '/js/services/service-detail.js';
import '/js/map/single-marker-map.js';
import '/js/utils/timeline.js';
import '/js/utils/websocket.js';
```

**Layout Sections**:

**1. Header**
- Service type icon + name
- Status badge
- Priority indicator
- Request ID
- Created timestamp

**2. Location Map**
- Single marker showing request location
- Provider location (if assigned and tracking)
- Route visualization (if in-progress)

**3. Details Panel**
```javascript
{
  "basic": {
    "type": "medical",
    "category": "emergency",
    "priority": "high",
    "description": "..."
  },
  "location": {
    "address": "...",
    "landmark": "...",
    "coordinates": [lat, lng]
  },
  "contact": {
    "name": "...",
    "phone": "...",
    "visibility": "based_on_privacy_settings"
  },
  "type_specific": {
    // Medical/Food/Shelter specific fields
  }
}
```

**4. Timeline**
```javascript
[
  {
    "status": "created",
    "timestamp": "2024-12-22T10:30:00Z",
    "actor": "John Doe",
    "notes": null
  },
  {
    "status": "assigned",
    "timestamp": "2024-12-22T10:32:00Z",
    "actor": "Coordinator X",
    "assigned_to": "City Hospital",
    "notes": null
  },
  {
    "status": "accepted",
    "timestamp": "2024-12-22T10:33:00Z",
    "actor": "City Hospital",
    "notes": "Ambulance dispatched"
  },
  {
    "status": "in-progress",
    "timestamp": "2024-12-22T10:35:00Z",
    "actor": "City Hospital",
    "notes": "ETA 10 minutes"
  }
]
```

**5. Actions Panel** (role-based)

**For Creator (CITIZEN)**:
- Update details (if status = pending)
- Cancel request
- Track provider location (if assigned)
- Rate service (if completed)

**For Assigned Provider**:
- Update status
- Add notes
- Update location (auto via GPS)
- Mark as completed
- Request help

**For Coordinator/Admin**:
- Assign to provider
- Change priority
- Add notes
- Cancel
- Override status

**Real-time Updates**:
```javascript
socket.on('service:updated', (data) => {
  if (data.id === currentServiceId) {
    updateDetails(data);
    updateTimeline(data);
    updateMap(data);
  }
});

socket.on('provider:location', (data) => {
  if (data.provider_id === assignedProviderId) {
    updateProviderMarker(data.location);
    updateETA(data.location);
  }
});
```

---

### 8. Dashboard Pages

#### 8a. Citizen Dashboard
**File**: `/pages/dashboard/citizen.html`  
**Route**: `/dashboard`  
**Access**: CITIZEN

**Widgets**:

1. **My Active Requests** (max 5, recent)
2. **Nearby Alerts** (active disasters)
3. **Quick Actions**:
   - Create new request
   - View all my requests
   - Track donations
4. **Statistics**:
   - Total requests made
   - Completed requests
   - Active requests
   - Donations made

**JavaScript Files**:
```javascript
import '/js/dashboard/citizen.js';
import '/js/widgets/request-summary.js';
import '/js/widgets/alert-ticker.js';
```

---

#### 8b. Provider Dashboard
**File**: `/pages/dashboard/provider.html`  
**Route**: `/dashboard`  
**Access**: PROVIDER

**Widgets**:

1. **Assigned Requests** (pending action)
2. **In-Progress Services** (active)
3. **Nearby Requests** (available for assignment)
4. **Performance Metrics**:
   - Total completed
   - Average response time
   - Rating
   - Active capacity

**JavaScript Files**:
```javascript
import '/js/dashboard/provider.js';
import '/js/widgets/assignment-queue.js';
import '/js/map/provider-map.js';
```

**Real-time Features**:
- Auto-refresh assigned requests
- Sound notification for new assignments
- Live location tracking toggle
- Capacity status indicator

---

#### 8c. Coordinator Dashboard
**File**: `/pages/dashboard/coordinator.html`  
**Route**: `/dashboard`  
**Access**: COORDINATOR, ADMIN

**Widgets**:

1. **Critical Alerts** (high priority pending)
2. **Active Disaster Zones**
3. **Service Overview**:
   - Pending: 45
   - In Progress: 89
   - Completed today: 156
4. **Provider Status**:
   - Available: 120
   - Busy: 34
   - Offline: 12
5. **Heatmap** (request density)
6. **Analytics Charts**:
   - Requests by type (pie chart)
   - Requests over time (line chart)
   - Response times (bar chart)

**JavaScript Files**:
```javascript
import '/js/dashboard/coordinator.js';
import '/js/widgets/analytics-charts.js';
import '/js/map/coordinator-map.js';
import '/js/utils/chart-builder.js';
```

**Quick Actions**:
- Create disaster event
- Assign bulk requests
- Generate report
- Broadcast message

---

### 9. Donation Pages

#### 9a. Make Donation Page
**File**: `/pages/donations/donate.html`  
**Route**: `/donations/donate`  
**Access**: Public (GUEST allowed)

**JavaScript Files**:
```javascript
import '/js/donations/donation-form.js';
import '/js/utils/payment.js';
import '/js/utils/validation.js';
```

**Form Steps**:

**Step 1: Amount**
```javascript
{
  "amount": {
    "presets": [100, 500, 1000, 5000],
    "custom": true,
    "min": 10,
    "max": 1000000,
    "currency": "INR"
  }
}
```

**Step 2: Allocation**
```javascript
{
  "disaster_id": { "optional": true },
  "purpose": {
    "options": ["medical", "food", "shelter", "general"],
    "default": "general"
  },
  "specific_request": { "optional": true }
}
```

**Step 3: Donor Info**
```javascript
{
  "name": { "required": true },
  "email": { "required": true },
  "phone": { "required": true },
  "pan": { "required": false, "note": "For tax receipt" },
  "is_anonymous": { "default": false }
}
```

**Step 4: Payment**
```javascript
{
  "method": ["upi", "card", "netbanking"],
  "payment_gateway": "Razorpay/PayU",
  "auto_receipt": true
}
```

**Workflow**:
```
1. Enter amount → Validate
2. Select allocation → Optional
3. Fill donor info → Validate
4. Choose payment method
5. POST /donations/create → Get payment link
6. Redirect to payment gateway
7. Callback → Verify payment
8. Show success + receipt
9. Email receipt
```

---

#### 9b. Track Donation Page
**File**: `/pages/donations/track.html`  
**Route**: `/donations/track`  
**Access**: Public (with donation ID)

**JavaScript Files**:
```javascript
import '/js/donations/track.js';
import '/js/widgets/allocation-timeline.js';
```

**Input**:
```javascript
{
  "donation_id": "don_987654",
  "email": "donor@example.com" // For verification
}
```

**Display**:
1. **Donation Details**
   - Amount
   - Date
   - Status
   - Receipt download

2. **Allocation Timeline**
   - Received
   - Allocated to purpose
   - Distributed
   - Impact report

3. **Transparency Metrics**
   - Admin overhead: 0%
   - Processing fee: 2%
   - Net contribution: 98%

4. **Impact**
   - Beneficiaries count
   - Services enabled
   - Photos (if available)

---

### 10. Profile & Settings Page
**File**: `/pages/profile.html`  
**Route**: `/profile`  
**Access**: All authenticated users

**JavaScript Files**:
```javascript
import '/js/profile/profile-edit.js';
import '/js/map/location-picker.js';
```

**Tabs**:

**1. Profile**
- Name
- Email (read-only)
- Phone
- Profile photo
- Location

**2. Security**
- Change password
- Two-factor authentication
- Active sessions
- Login history

**3. Preferences**
- Language
- Notifications (email, SMS, push)
- Privacy settings
- Theme (light/dark)

**4. Activity Log**
- Recent actions
- Service requests
- Donations

---

## User Workflows

### Workflow 1: Citizen Reports Medical Emergency

```
Landing Page
    ↓
Login/Register
    ↓
Dashboard (Citizen)
    ↓ Click "Create Request"
Service Create Page
    ↓ Select "Medical"
Fill Medical Form
    ↓ Pick location on map
    ↓ Fill contact + details
    ↓ Upload photo (optional)
    ↓ Set privacy
Submit (POST /services/requests)
    ↓
Success Page
    ↓ Show request ID
    ↓ If anonymous: Show verification code
    ↓
Redirect to Service Detail Page
    ↓ Real-time status updates
    ↓ Provider assigned (notification)
    ↓ Provider en route (map tracking)
    ↓ Service completed
    ↓
Rate Provider
```

### Workflow 2: Provider Responds to Request

```
Login (Provider)
    ↓
Provider Dashboard
    ↓ New assignment notification (WebSocket)
    ↓ Sound alert
View Assignment Details
    ↓ Check location, priority, details
Accept Assignment
    ↓ POST /services/requests/{id}/status
    ↓ Status = "accepted"
Enable GPS Tracking
    ↓ socket.emit('location:update')
Navigate to Location
    ↓ Map shows route
    ↓ Auto-update location every 30s
Arrive at Location
    ↓ Update status = "in-progress"
Provide Service
    ↓ Add notes
    ↓ Upload completion photo
Complete Service
    ↓ Update status = "completed"
    ↓ Submit completion form
Done
    ↓ Return to dashboard
```

### Workflow 3: Coordinator Manages Disaster

```
Login (Coordinator)
    ↓
Coordinator Dashboard
    ↓ View critical alerts
    ↓ Check heatmap
Create Disaster Event
    ↓ POST /disasters/events
    ↓ Define affected area (draw polygon)
    ↓ Set severity, warnings
View Pending Requests in Zone
    ↓ Filter by disaster_zone
    ↓ Sort by priority
Assign to Providers
    ↓ Auto-match or manual assign
    ↓ POST /services/requests/{id}/assign
Monitor Progress
    ↓ Real-time map view
    ↓ WebSocket updates
Generate Report
    ↓ GET /analytics/dashboard
    ↓ Export as PDF
```

### Workflow 4: Anonymous Donation

```
Landing Page
    ↓ Click "Donate"
Donation Page (No login required)
    ↓ Select amount
    ↓ Choose disaster/purpose
    ↓ Fill donor info
    ↓ Select "Anonymous donation"
Payment
    ↓ POST /donations/create
    ↓ Redirect to payment gateway
    ↓ Complete payment
Success Page
    ↓ Show donation ID
    ↓ Email receipt
Track Donation
    ↓ Enter donation ID + email
    ↓ GET /donations/{id}/tracking
    ↓ View allocation timeline
    ↓ See impact report
```

---

## Browser Requirements

### Minimum Requirements

```javascript
{
  "chrome": "90+",
  "firefox": "88+",
  "safari": "14+",
  "edge": "90+",
  "mobile_safari": "14+",
  "chrome_mobile": "90+"
}
```

### Required Features

- **JavaScript**: ES6+ support
- **CSS**: Grid, Flexbox, CSS Variables
- **APIs**:
  - Geolocation API
  - Fetch API
  - LocalStorage
  - WebSocket
  - File API (for uploads)
  - Notification API (optional)

### Polyfills (for older browsers)

```javascript
// vite.config.js
export default {
  build: {
    target: 'es2015',
    polyfills: true
  }
};
```

---

## Performance Optimization

### Code Splitting
```javascript
// Lazy load heavy components
const Chart = () => import('./utils/chart-builder.js');
const MapManager = () => import('./map/map-manager.js');
```

### Image Optimization
```javascript
{
  "format": "WebP with JPEG fallback",
  "lazy_loading": true,
  "responsive_images": true,
  "compression": "TinyPNG/ImageOptim"
}
```

### Caching Strategy
```javascript
// Service Worker (optional)
{
  "static_assets": "Cache-First",
  "api_responses": "Network-First",
  "images": "Cache-First with expiry",
  "map_tiles": "Cache-First"
}
```

### Bundle Size
```javascript
{
  "target": "< 500KB initial bundle",
  "lazy_chunks": "< 200KB each",
  "total": "< 2MB including all libraries"
}
```

---

## Accessibility (a11y)

### WCAG 2.1 Level AA Compliance

**Keyboard Navigation**:
- All interactive elements tabbable
- Skip to main content link
- Focus indicators visible

**Screen Reader Support**:
- ARIA labels on all icons
- Role attributes
- Alt text on images
- Form field labels

**Color Contrast**:
- Minimum 4.5:1 for text
- 3:1 for UI components

**Responsive Design**:
- Mobile-first approach
- Touch targets min 44x44px
- Zoom up to 200%

---

**This specification provides a complete overview of all frontend pages, their workflows, JavaScript libraries, and architectural details for the IDRM platform.**
