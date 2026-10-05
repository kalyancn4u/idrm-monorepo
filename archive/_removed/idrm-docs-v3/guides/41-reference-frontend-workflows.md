> *Type: Guide (novice / how-to) · Audience: Frontend developers · Status: Archived — v3 historical generation*

# IDRM: Complete Frontend Workflows Reference

<!-- IDRM-CLEANUP doc=v3-g41-frontendflows status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — frontend workflows → `docs/mvp/60` / FFP
> MVP web workflows (HTML+JS+Leaflet) → [`../../../../docs/mvp/60-uidesign-web-interaction.md`](../../../../docs/mvp/60-uidesign-web-interaction.md);
> React/component-framework workflows → **FFP** [`../../../../docs/ffp/61-frontend-engineering-standards.md`](../../../../docs/ffp/61-frontend-engineering-standards.md). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## All Pages, Libraries, HTTP Methods & JSON Formats Explained for Beginners

**Version**: 3.0 Consolidated  
**Audience**: Frontend developers, Complete beginners, UI/UX designers  
**Reading Time**: 90 minutes  
**Last Updated**: May 16, 2026

---

## 📚 **Table of Contents**

1. [What are Frontend Workflows?](#1-what-are-frontend-workflows)
2. [Complete Page Inventory](#2-complete-page-inventory)
3. [JavaScript Libraries Used](#3-javascript-libraries-used)
4. [Authentication Workflows](#4-authentication-workflows)
5. [Service Request Workflows](#5-service-request-workflows)
6. [Provider Workflows](#6-provider-workflows)
7. [Admin/Dashboard Workflows](#7-admindashboard-workflows)
8. [Map & Geospatial Workflows](#8-map--geospatial-workflows)
9. [Common UI Patterns](#9-common-ui-patterns)
10. [Complete Workflow Diagrams](#10-complete-workflow-diagrams)

---

## 1. **What are Frontend Workflows?**

### 1.1 Simple Explanation

**Frontend Workflow** = The complete journey a user takes through your app!

**Real-World Analogy**:

```
Restaurant Experience (Physical):
┌─────────────────────────────────────┐
│ 1. Enter restaurant (Homepage)      │
│ 2. Look at menu (Browse page)       │
│ 3. Order food (Fill form)           │
│ 4. Wait for food (Loading screen)   │
│ 5. Eat food (View result)           │
└─────────────────────────────────────┘

IDRM Workflow (Digital):
┌─────────────────────────────────────┐
│ 1. Visit homepage (index.html)      │
│ 2. Login (login.html)               │
│ 3. View dashboard (dashboard.html)  │
│ 4. Create request (create-service.html) │
│ 5. Track status (service-detail.html)   │
└─────────────────────────────────────┘
```

**Each workflow involves**:
- 📄 **HTML Pages** (what you see)
- ⚡ **JavaScript** (what makes it interactive)
- 📨 **HTTP Requests** (talking to the server)
- 📦 **JSON Data** (data format sent/received)

---

### 1.2 Complete Flow Example

**Workflow: Creating a Service Request**

```
User Journey:
1. User on dashboard.html
2. Clicks "Request Help" button
3. Redirected to create-service.html
4. Fills form (service type, location, description)
5. Clicks "Submit"
   ↓
   JavaScript takes over:
   ↓
6. Validates form inputs (client-side)
7. Gets user's GPS location
8. Creates JSON payload
9. Sends POST request to /api/v1/services
   ↓
   Server responds:
   ↓
10. Receives JSON response
11. Shows success message
12. Redirects to service-detail.html?id=xxx

Technologies Used:
- HTML: create-service.html
- CSS: Tailwind utility classes
- JS Library: Leaflet (map), Axios (HTTP)
- HTTP Method: POST
- API Endpoint: /api/v1/services
- JSON: Service request object
```

---

## 2. **Complete Page Inventory**

### 2.1 All HTML Pages

**IDRM has 18 main pages** organized by function:

| # | Page | File | Purpose | Auth Required? |
|---|------|------|---------|----------------|
| **PUBLIC PAGES** |
| 1 | **Homepage** | `index.html` | Landing page, info | ❌ No |
| 2 | **About** | `about.html` | About IDRM | ❌ No |
| 3 | **Register** | `register.html` | Create account | ❌ No |
| 4 | **Login** | `login.html` | Sign in | ❌ No |
| 5 | **Forgot Password** | `forgot-password.html` | Reset password | ❌ No |
| **AUTHENTICATED PAGES** |
| 6 | **Dashboard** | `dashboard.html` | Main control panel | ✅ Yes |
| 7 | **Create Service** | `create-service.html` | Request help | ✅ Yes |
| 8 | **Service Detail** | `service-detail.html` | View/track request | ✅ Yes |
| 9 | **My Services** | `my-services.html` | User's requests | ✅ Yes |
| 10 | **Map View** | `map.html` | All services on map | ✅ Yes |
| 11 | **Profile** | `profile.html` | User settings | ✅ Yes |
| 12 | **Notifications** | `notifications.html` | Alerts & updates | ✅ Yes |
| **PROVIDER PAGES** |
| 13 | **Provider Dashboard** | `provider-dashboard.html` | Provider control panel | ✅ Provider |
| 14 | **Available Services** | `available-services.html` | Services to accept | ✅ Provider |
| 15 | **Active Services** | `active-services.html` | Assigned services | ✅ Provider |
| **ADMIN PAGES** |
| 16 | **Admin Dashboard** | `admin-dashboard.html` | Admin panel | ✅ Admin |
| 17 | **User Management** | `admin-users.html` | Manage users | ✅ Admin |
| 18 | **Analytics** | `admin-analytics.html` | Reports & metrics | ✅ Admin |

**Total**: 18 pages

---

### 2.2 Page Architecture

```
IDRM Frontend Structure:
/
├── index.html                    (Homepage)
├── about.html
├── auth/
│   ├── register.html
│   ├── login.html
│   └── forgot-password.html
├── app/
│   ├── dashboard.html
│   ├── create-service.html
│   ├── service-detail.html
│   ├── my-services.html
│   ├── map.html
│   ├── profile.html
│   └── notifications.html
├── provider/
│   ├── provider-dashboard.html
│   ├── available-services.html
│   └── active-services.html
├── admin/
│   ├── admin-dashboard.html
│   ├── admin-users.html
│   └── admin-analytics.html
├── assets/
│   ├── css/
│   │   └── tailwind.min.css
│   ├── js/
│   │   ├── app.js               (Main application logic)
│   │   ├── auth.js              (Authentication)
│   │   ├── services.js          (Service operations)
│   │   ├── map.js               (Map interactions)
│   │   └── utils.js             (Helper functions)
│   └── images/
└── components/
    ├── navbar.html              (Reusable nav)
    ├── footer.html              (Reusable footer)
    └── modals.html              (Popups)
```

---

## 3. **JavaScript Libraries Used**

### 3.1 Complete Library List

| Library | Version | Purpose | CDN/Local | Size |
|---------|---------|---------|-----------|------|
| **Tailwind CSS** | 3.4 | UI styling | CDN | ~100KB |
| **Axios** | 1.6 | HTTP requests | CDN | ~15KB |
| **Leaflet** | 1.9 | Interactive maps | CDN | ~145KB |
| **Chart.js** | 4.4 | Data visualization | CDN | ~200KB |
| **DOMPurify** | 3.0 | XSS protection | CDN | ~25KB |
| **Alpine.js** | 3.13 | Reactive UI (optional) | CDN | ~15KB |

**Total Size**: ~500KB (all libraries)

---

### 3.2 Library Details & Usage

#### **Tailwind CSS** (Styling)

**What it is**: Utility-first CSS framework

**Why we use it**:
- ✅ Fast development (no custom CSS)
- ✅ Responsive by default
- ✅ Small bundle size
- ✅ Consistent design

**Example Usage**:
```html
<!-- Traditional CSS -->
<button class="submit-button">Submit</button>

<!-- Tailwind CSS -->
<button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
  Submit
</button>
```

**CDN Include**:
```html
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.0/dist/tailwind.min.css" rel="stylesheet">
```

---

#### **Axios** (HTTP Requests)

**What it is**: Promise-based HTTP client

**Why we use it**:
- ✅ Simpler than fetch API
- ✅ Automatic JSON parsing
- ✅ Request/response interceptors
- ✅ Better error handling

**Example Usage**:
```javascript
// Fetch API (traditional)
fetch('/api/v1/services', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(data)
})
.then(res => res.json())
.then(data => console.log(data))

// Axios (simpler!)
axios.post('/api/v1/services', data)
  .then(response => console.log(response.data))
```

**CDN Include**:
```html
<script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"></script>
```

---

#### **Leaflet** (Maps)

**What it is**: Open-source interactive map library

**Why we use it**:
- ✅ Free (no API key needed!)
- ✅ Works offline
- ✅ Lightweight
- ✅ Easy to use

**Example Usage**:
```javascript
// Initialize map
const map = L.map('map').setView([17.3850, 78.4867], 13);

// Add tile layer (map background)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Add marker
L.marker([17.3850, 78.4867])
  .addTo(map)
  .bindPopup('Charminar, Hyderabad');
```

**CDN Include**:
```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```

---

#### **Chart.js** (Visualizations)

**What it is**: JavaScript charting library

**Why we use it**:
- ✅ Beautiful charts
- ✅ Responsive
- ✅ Simple API
- ✅ Many chart types

**Example Usage**:
```javascript
// Create bar chart
new Chart(document.getElementById('myChart'), {
  type: 'bar',
  data: {
    labels: ['Medical', 'Food', 'Shelter'],
    datasets: [{
      label: 'Service Requests',
      data: [45, 32, 28]
    }]
  }
});
```

**CDN Include**:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

---

#### **DOMPurify** (Security)

**What it is**: XSS sanitizer for HTML

**Why we use it**:
- ✅ Prevents XSS attacks
- ✅ Sanitizes user input
- ✅ Safe HTML rendering

**Example Usage**:
```javascript
// Dangerous! (XSS vulnerability)
element.innerHTML = userInput;

// Safe! (Sanitized)
element.innerHTML = DOMPurify.sanitize(userInput);
```

**CDN Include**:
```html
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.0.0/dist/purify.min.js"></script>
```

---

## 4. **Authentication Workflows**

### 4.1 Registration Workflow

**Page**: `register.html`

**User Journey**:
```
1. User visits register.html
2. Fills form (email, password, name, phone)
3. Clicks "Register"
4. JavaScript validates inputs
5. POST request to /api/v1/auth/register
6. Receives success response
7. Shows "Check email to verify" message
8. Redirects to login.html after 3 seconds
```

**HTML Structure**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Register - IDRM</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.0/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-50">
  <div class="max-w-md mx-auto mt-10 p-6 bg-white rounded shadow">
    <h1 class="text-2xl font-bold mb-6">Create Account</h1>
    
    <form id="registerForm">
      <!-- Email -->
      <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Email</label>
        <input type="email" id="email" required
               class="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500">
      </div>
      
      <!-- Password -->
      <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Password</label>
        <input type="password" id="password" required
               class="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500">
        <p class="text-xs text-gray-500 mt-1">Min 8 characters, 1 uppercase, 1 number</p>
      </div>
      
      <!-- Full Name -->
      <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Full Name</label>
        <input type="text" id="fullName" required
               class="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500">
      </div>
      
      <!-- Phone -->
      <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Phone</label>
        <input type="tel" id="phone" pattern="[0-9]{10}" required
               class="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500">
        <p class="text-xs text-gray-500 mt-1">10-digit mobile number</p>
      </div>
      
      <!-- Submit Button -->
      <button type="submit" id="submitBtn"
              class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded">
        Register
      </button>
    </form>
    
    <p class="mt-4 text-center text-sm">
      Already have an account? 
      <a href="login.html" class="text-blue-600 hover:underline">Login</a>
    </p>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"></script>
  <script src="assets/js/auth.js"></script>
</body>
</html>
```

**JavaScript** (`assets/js/auth.js`):
```javascript
// Registration form handler
document.getElementById('registerForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  // Get form values
  const formData = {
    email: document.getElementById('email').value,
    password: document.getElementById('password').value,
    full_name: document.getElementById('fullName').value,
    phone: document.getElementById('phone').value,
    role: 'CITIZEN'
  };
  
  // Client-side validation
  if (!validateEmail(formData.email)) {
    showError('Invalid email format');
    return;
  }
  
  if (!validatePassword(formData.password)) {
    showError('Password must be at least 8 characters with 1 uppercase and 1 number');
    return;
  }
  
  if (!validatePhone(formData.phone)) {
    showError('Phone must be 10 digits');
    return;
  }
  
  // Show loading state
  const submitBtn = document.getElementById('submitBtn');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Registering...';
  
  try {
    // POST request to API
    const response = await axios.post('/api/v1/auth/register', formData);
    
    // Success!
    showSuccess('Account created! Please check your email to verify.');
    
    // Redirect to login after 3 seconds
    setTimeout(() => {
      window.location.href = 'login.html';
    }, 3000);
    
  } catch (error) {
    // Handle errors
    if (error.response) {
      // Server responded with error
      const message = error.response.data.error.message;
      showError(message);
    } else {
      // Network error
      showError('Network error. Please try again.');
    }
    
    // Re-enable button
    submitBtn.disabled = false;
    submitBtn.textContent = 'Register';
  }
});

// Validation functions
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function validatePassword(password) {
  // Min 8 chars, 1 uppercase, 1 number
  const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
  return re.test(password);
}

function validatePhone(phone) {
  return /^[0-9]{10}$/.test(phone);
}

// UI feedback functions
function showError(message) {
  // Create error toast
  const toast = document.createElement('div');
  toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded shadow-lg';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  // Remove after 5 seconds
  setTimeout(() => toast.remove(), 5000);
}

function showSuccess(message) {
  const toast = document.createElement('div');
  toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded shadow-lg';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => toast.remove(), 5000);
}
```

**HTTP Request**:
```http
POST /api/v1/auth/register HTTP/1.1
Host: api.idrm.gov.in
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "phone": "9876543210",
  "role": "CITIZEN"
}
```

**HTTP Response**:
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "status": "success",
  "data": {
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "CITIZEN",
    "is_verified": false,
    "created_at": "2026-05-16T10:00:00Z"
  }
}
```

---

### 4.2 Login Workflow

**Page**: `login.html`

**User Journey**:
```
1. User visits login.html
2. Enters email & password
3. Clicks "Login"
4. POST request to /api/v1/auth/login
5. Receives JWT tokens
6. Stores tokens in sessionStorage
7. Redirects to dashboard.html
```

**JavaScript** (`assets/js/auth.js`):
```javascript
// Login form handler
document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const credentials = {
    email: document.getElementById('email').value,
    password: document.getElementById('password').value
  };
  
  const submitBtn = document.getElementById('submitBtn');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Logging in...';
  
  try {
    const response = await axios.post('/api/v1/auth/login', credentials);
    
    // Store tokens
    sessionStorage.setItem('access_token', response.data.data.access_token);
    sessionStorage.setItem('refresh_token', response.data.data.refresh_token);
    sessionStorage.setItem('user', JSON.stringify(response.data.data.user));
    
    // Redirect to dashboard
    window.location.href = 'app/dashboard.html';
    
  } catch (error) {
    if (error.response && error.response.status === 401) {
      showError('Invalid email or password');
    } else {
      showError('Login failed. Please try again.');
    }
    
    submitBtn.disabled = false;
    submitBtn.textContent = 'Login';
  }
});
```

**HTTP Request**:
```http
POST /api/v1/auth/login HTTP/1.1
Host: api.idrm.gov.in
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**HTTP Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "data": {
    "user": {
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "email": "john@example.com",
      "full_name": "John Doe",
      "role": "CITIZEN"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 900
  }
}
```

---

## 5. **Service Request Workflows**

### 5.1 Create Service Request Workflow

**Page**: `create-service.html`

**User Journey**:
```
1. User on dashboard, clicks "Request Help"
2. Redirected to create-service.html
3. Fills form:
   - Service type (dropdown)
   - Priority (dropdown)
   - Description (textarea)
   - Location (map pin or current GPS)
   - Privacy level (radio buttons)
4. Clicks "Submit Request"
5. JavaScript validates form
6. Gets GPS coordinates from map
7. POST request to /api/v1/services
8. Receives service_id
9. Shows success message
10. Redirects to service-detail.html?id={service_id}
```

**HTML** (`create-service.html`):
```html
<!DOCTYPE html>
<html>
<head>
  <title>Request Service - IDRM</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.0/dist/tailwind.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</head>
<body>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">Request Service</h1>
    
    <form id="serviceForm" class="max-w-2xl">
      <!-- Service Type -->
      <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Service Type *</label>
        <select id="serviceType" required
                class="w-full px-3 py-2 border rounded">
          <option value="">Select service type</option>
          <option value="MEDICAL">Medical</option>
          <option value="FOOD">Food</option>
          <option value="SHELTER">Shelter</option>
          <option value="RESCUE">Rescue</option>
          <option value="SANITATION">Sanitation</option>
          <option value="TRANSPORT">Transport</option>
          <option value="OTHER">Other</option>
        </select>
      </div>
      
      <!-- Priority -->
      <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Priority *</label>
        <select id="priority" required
                class="w-full px-3 py-2 border rounded">
          <option value="">Select priority</option>
          <option value="CRITICAL">Critical (Life-threatening)</option>
          <option value="HIGH">High (Urgent)</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>
      
      <!-- Description -->
      <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Description *</label>
        <textarea id="description" required rows="4"
                  class="w-full px-3 py-2 border rounded"
                  placeholder="Describe your situation..."></textarea>
        <p class="text-xs text-gray-500 mt-1">
          <span id="charCount">0</span>/2000 characters
        </p>
      </div>
      
      <!-- Location Map -->
      <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Location *</label>
        <div id="map" class="h-64 rounded border"></div>
        <p class="text-xs text-gray-500 mt-1">
          Click map to set location or 
          <button type="button" id="getCurrentLocation"
                  class="text-blue-600 hover:underline">
            use current location
          </button>
        </p>
        <input type="hidden" id="latitude" required>
        <input type="hidden" id="longitude" required>
      </div>
      
      <!-- Address -->
      <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Address</label>
        <input type="text" id="address"
               class="w-full px-3 py-2 border rounded"
               placeholder="Will be auto-filled from map">
      </div>
      
      <!-- Privacy Level -->
      <div class="mb-6">
        <label class="block text-sm font-medium mb-2">Privacy Level *</label>
        <div class="space-y-2">
          <label class="flex items-center">
            <input type="radio" name="privacy" value="PUBLIC" required
                   class="mr-2">
            <span>Public (Anyone can see)</span>
          </label>
          <label class="flex items-center">
            <input type="radio" name="privacy" value="PROTECTED" checked required
                   class="mr-2">
            <span>Protected (Hide sensitive details)</span>
          </label>
          <label class="flex items-center">
            <input type="radio" name="privacy" value="PRIVATE" required
                   class="mr-2">
            <span>Private (Only assigned provider can see)</span>
          </label>
        </div>
      </div>
      
      <!-- Submit -->
      <button type="submit" id="submitBtn"
              class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded">
        Submit Request
      </button>
    </form>
  </div>
  
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"></script>
  <script src="../assets/js/services.js"></script>
</body>
</html>
```

**JavaScript** (`assets/js/services.js`):
```javascript
// Initialize map
let map, marker;
let selectedLat, selectedLng;

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Leaflet map
  map = L.map('map').setView([17.3850, 78.4867], 13);
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);
  
  // Click map to select location
  map.on('click', (e) => {
    selectedLat = e.latlng.lat;
    selectedLng = e.latlng.lng;
    
    // Update hidden inputs
    document.getElementById('latitude').value = selectedLat;
    document.getElementById('longitude').value = selectedLng;
    
    // Add/move marker
    if (marker) {
      marker.setLatLng(e.latlng);
    } else {
      marker = L.marker(e.latlng).addTo(map);
    }
    
    // Reverse geocode to get address
    reverseGeocode(selectedLat, selectedLng);
  });
  
  // Use current location button
  document.getElementById('getCurrentLocation').addEventListener('click', () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        selectedLat = position.coords.latitude;
        selectedLng = position.coords.longitude;
        
        document.getElementById('latitude').value = selectedLat;
        document.getElementById('longitude').value = selectedLng;
        
        // Center map and add marker
        map.setView([selectedLat, selectedLng], 15);
        
        if (marker) {
          marker.setLatLng([selectedLat, selectedLng]);
        } else {
          marker = L.marker([selectedLat, selectedLng]).addTo(map);
        }
        
        reverseGeocode(selectedLat, selectedLng);
      });
    } else {
      alert('Geolocation is not supported by your browser');
    }
  });
  
  // Character counter
  document.getElementById('description').addEventListener('input', (e) => {
    document.getElementById('charCount').textContent = e.target.value.length;
  });
  
  // Form submission
  document.getElementById('serviceForm').addEventListener('submit', handleSubmit);
});

// Reverse geocode to get address
async function reverseGeocode(lat, lng) {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`
    );
    const data = await response.json();
    document.getElementById('address').value = data.display_name;
  } catch (error) {
    console.error('Geocoding failed:', error);
  }
}

// Handle form submission
async function handleSubmit(e) {
  e.preventDefault();
  
  // Get form values
  const formData = {
    service_type: document.getElementById('serviceType').value,
    priority: document.getElementById('priority').value,
    description: document.getElementById('description').value,
    location: {
      type: 'Point',
      coordinates: [
        parseFloat(document.getElementById('longitude').value),
        parseFloat(document.getElementById('latitude').value)
      ]
    },
    address: document.getElementById('address').value,
    privacy_level: document.querySelector('input[name="privacy"]:checked').value
  };
  
  // Validate location selected
  if (!document.getElementById('latitude').value) {
    alert('Please select a location on the map');
    return;
  }
  
  // Show loading
  const submitBtn = document.getElementById('submitBtn');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Submitting...';
  
  try {
    // Get auth token
    const token = sessionStorage.getItem('access_token');
    
    // POST request
    const response = await axios.post('/api/v1/services', formData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    // Success!
    const serviceId = response.data.data.service_id;
    
    showSuccess('Service request submitted successfully!');
    
    // Redirect to service detail page
    setTimeout(() => {
      window.location.href = `service-detail.html?id=${serviceId}`;
    }, 2000);
    
  } catch (error) {
    if (error.response) {
      alert(error.response.data.error.message);
    } else {
      alert('Failed to submit request. Please try again.');
    }
    
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit Request';
  }
}

function showSuccess(message) {
  const toast = document.createElement('div');
  toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded shadow-lg z-50';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}
```

**HTTP Request**:
```http
POST /api/v1/services HTTP/1.1
Host: api.idrm.gov.in
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "service_type": "MEDICAL",
  "priority": "CRITICAL",
  "location": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]
  },
  "address": "Charminar, Hyderabad, Telangana 500002",
  "description": "Urgent medical attention needed for elderly person with chest pain",
  "privacy_level": "PROTECTED"
}
```

**HTTP Response**:
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "status": "success",
  "data": {
    "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "status": "SUBMITTED",
    "created_at": "2026-05-16T10:00:00Z",
    "estimated_response_time": "30 minutes"
  }
}
```

---

## 6. **Provider Workflows**

### 6.1 Accept Service Workflow

**Page**: `available-services.html`

**User Journey**:
```
1. Provider on provider-dashboard.html
2. Clicks "Available Services"
3. Sees list of nearby approved services
4. Clicks "View Details" on a service
5. Modal opens with full details
6. Clicks "Accept Service"
7. POST request to /api/v1/services/{id}/accept
8. Service assigned to provider
9. Redirected to active-services.html
```

**JavaScript**:
```javascript
// Accept service button handler
async function acceptService(serviceId) {
  const confirmed = confirm('Are you sure you want to accept this service request?');
  if (!confirmed) return;
  
  const formData = {
    estimated_arrival: calculateETA(),  // Helper function
    notes: 'On my way'
  };
  
  try {
    const token = sessionStorage.getItem('access_token');
    
    const response = await axios.post(
      `/api/v1/services/${serviceId}/accept`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    showSuccess('Service accepted! Redirecting...');
    
    setTimeout(() => {
      window.location.href = 'active-services.html';
    }, 2000);
    
  } catch (error) {
    if (error.response && error.response.status === 409) {
      alert('This service has already been assigned to another provider');
    } else {
      alert('Failed to accept service. Please try again.');
    }
  }
}

function calculateETA() {
  // Calculate estimated arrival time (30 minutes from now)
  const eta = new Date();
  eta.setMinutes(eta.getMinutes() + 30);
  return eta.toISOString();
}
```

**HTTP Request**:
```http
POST /api/v1/services/f9e8d7c6-b5a4-3210-fedc-ba9876543210/accept HTTP/1.1
Host: api.idrm.gov.in
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "estimated_arrival": "2026-05-16T10:30:00Z",
  "notes": "On my way with medical kit"
}
```

**HTTP Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "data": {
    "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "status": "ASSIGNED",
    "assigned_to": "provider-uuid-here",
    "estimated_arrival": "2026-05-16T10:30:00Z"
  }
}
```

---

## 7. **Admin/Dashboard Workflows**

### 7.1 Dashboard View Workflow

**Page**: `dashboard.html`

**User Journey**:
```
1. User logs in
2. Redirected to dashboard.html
3. Dashboard loads:
   a. GET /api/v1/analytics/dashboard (metrics)
   b. GET /api/v1/services?limit=5 (recent services)
   c. GET /api/v1/geo/geojson (map data)
4. All data rendered simultaneously
5. Charts drawn with Chart.js
6. Map rendered with Leaflet
```

**JavaScript** (`assets/js/dashboard.js`):
```javascript
document.addEventListener('DOMContentLoaded', async () => {
  const token = sessionStorage.getItem('access_token');
  
  if (!token) {
    window.location.href = '../login.html';
    return;
  }
  
  // Axios configuration
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  
  try {
    // Fetch all data in parallel
    const [metricsRes, servicesRes, mapRes] = await Promise.all([
      axios.get('/api/v1/analytics/dashboard'),
      axios.get('/api/v1/services?limit=5'),
      axios.get('/api/v1/geo/geojson')
    ]);
    
    // Render metrics
    renderMetrics(metricsRes.data.data);
    
    // Render recent services
    renderRecentServices(servicesRes.data.data.services);
    
    // Render map
    renderMap(mapRes.data.data.geojson);
    
  } catch (error) {
    if (error.response && error.response.status === 401) {
      // Token expired, redirect to login
      sessionStorage.clear();
      window.location.href = '../login.html';
    } else {
      console.error('Dashboard load error:', error);
    }
  }
});

function renderMetrics(metrics) {
  // Update metric cards
  document.getElementById('totalRequests').textContent = metrics.total_requests;
  document.getElementById('criticalCount').textContent = metrics.by_priority.CRITICAL;
  document.getElementById('completedCount').textContent = metrics.by_status.COMPLETED;
  
  // Render chart
  new Chart(document.getElementById('requestsChart'), {
    type: 'doughnut',
    data: {
      labels: ['Medical', 'Food', 'Shelter', 'Other'],
      datasets: [{
        data: [
          metrics.by_type.MEDICAL,
          metrics.by_type.FOOD,
          metrics.by_type.SHELTER,
          metrics.by_type.OTHER
        ],
        backgroundColor: ['#EF4444', '#10B981', '#3B82F6', '#F59E0B']
      }]
    }
  });
}

function renderRecentServices(services) {
  const container = document.getElementById('recentServices');
  
  container.innerHTML = services.map(service => `
    <div class="border-b py-3 hover:bg-gray-50 cursor-pointer"
         onclick="window.location.href='service-detail.html?id=${service.service_id}'">
      <div class="flex justify-between items-start">
        <div>
          <span class="px-2 py-1 text-xs rounded ${getPriorityClass(service.priority)}">
            ${service.priority}
          </span>
          <span class="ml-2 text-sm font-medium">${service.service_type}</span>
        </div>
        <span class="text-xs text-gray-500">${formatTime(service.created_at)}</span>
      </div>
      <p class="text-sm text-gray-600 mt-1">${service.address}</p>
    </div>
  `).join('');
}

function renderMap(geojson) {
  const map = L.map('dashboardMap').setView([17.3850, 78.4867], 12);
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
  
  // Add GeoJSON layer
  L.geoJSON(geojson, {
    pointToLayer: (feature, latlng) => {
      return L.circleMarker(latlng, {
        radius: 8,
        fillColor: getMarkerColor(feature.properties.priority),
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
      });
    },
    onEachFeature: (feature, layer) => {
      layer.bindPopup(`
        <b>${feature.properties.service_type}</b><br>
        Priority: ${feature.properties.priority}<br>
        Status: ${feature.properties.status}
      `);
    }
  }).addTo(map);
}

// Helper functions
function getPriorityClass(priority) {
  const classes = {
    'CRITICAL': 'bg-red-100 text-red-800',
    'HIGH': 'bg-orange-100 text-orange-800',
    'MEDIUM': 'bg-yellow-100 text-yellow-800',
    'LOW': 'bg-green-100 text-green-800'
  };
  return classes[priority] || 'bg-gray-100 text-gray-800';
}

function getMarkerColor(priority) {
  const colors = {
    'CRITICAL': '#EF4444',
    'HIGH': '#F97316',
    'MEDIUM': '#EAB308',
    'LOW': '#22C55E'
  };
  return colors[priority] || '#6B7280';
}

function formatTime(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}
```

---

## 8. **Map & Geospatial Workflows**

### 8.1 Interactive Map View

**Page**: `map.html`

**Technologies Used**:
- Leaflet.js (map rendering)
- Leaflet.markercluster (clustering)
- GET /api/v1/geo/geojson (data)

**Features**:
1. Show all services on map
2. Cluster nearby markers
3. Click marker for details
4. Filter by service type
5. Filter by priority
6. Search location

**JavaScript** (`assets/js/map.js`):
```javascript
let map, markersLayer;

document.addEventListener('DOMContentLoaded', async () => {
  // Initialize map
  map = L.map('map').setView([17.3850, 78.4867], 12);
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map);
  
  // Load services
  await loadServices();
  
  // Setup filters
  document.getElementById('serviceTypeFilter').addEventListener('change', loadServices);
  document.getElementById('priorityFilter').addEventListener('change', loadServices);
});

async function loadServices() {
  const token = sessionStorage.getItem('access_token');
  
  // Get filter values
  const serviceType = document.getElementById('serviceTypeFilter').value;
  const priority = document.getElementById('priorityFilter').value;
  
  // Build query string
  let query = '/api/v1/geo/geojson?';
  if (serviceType) query += `service_type=${serviceType}&`;
  if (priority) query += `priority=${priority}`;
  
  try {
    const response = await axios.get(query, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    // Clear existing markers
    if (markersLayer) {
      map.removeLayer(markersLayer);
    }
    
    // Add new markers
    markersLayer = L.geoJSON(response.data.data, {
      pointToLayer: createMarker,
      onEachFeature: bindPopup
    }).addTo(map);
    
    // Fit map to markers
    if (markersLayer.getBounds().isValid()) {
      map.fitBounds(markersLayer.getBounds());
    }
    
  } catch (error) {
    console.error('Failed to load services:', error);
  }
}

function createMarker(feature, latlng) {
  const priority = feature.properties.priority;
  const color = {
    'CRITICAL': 'red',
    'HIGH': 'orange',
    'MEDIUM': 'yellow',
    'LOW': 'green'
  }[priority] || 'blue';
  
  return L.circleMarker(latlng, {
    radius: 10,
    fillColor: color,
    color: '#fff',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.7
  });
}

function bindPopup(feature, layer) {
  const props = feature.properties;
  
  const popupContent = `
    <div class="p-2">
      <h3 class="font-bold text-lg">${props.service_type}</h3>
      <p class="text-sm">
        <span class="font-medium">Priority:</span> ${props.priority}<br>
        <span class="font-medium">Status:</span> ${props.status}<br>
        <span class="font-medium">Address:</span> ${props.address}
      </p>
      <button onclick="viewService('${props.service_id}')"
              class="mt-2 bg-blue-600 text-white px-3 py-1 rounded text-sm">
        View Details
      </button>
    </div>
  `;
  
  layer.bindPopup(popupContent);
}

function viewService(serviceId) {
  window.location.href = `service-detail.html?id=${serviceId}`;
}
```

---

## 9. **Common UI Patterns**

### 9.1 Loading States

```javascript
// Show loading spinner
function showLoading() {
  document.getElementById('loadingSpinner').classList.remove('hidden');
}

function hideLoading() {
  document.getElementById('loadingSpinner').classList.add('hidden');
}

// Usage
showLoading();
await fetchData();
hideLoading();
```

### 9.2 Error Handling

```javascript
// Global error handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  showError('An unexpected error occurred');
});

// Axios error interceptor
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // Server error
      if (error.response.status === 401) {
        // Unauthorized - redirect to login
        sessionStorage.clear();
        window.location.href = '/login.html';
      } else if (error.response.status === 403) {
        showError('You don\'t have permission to perform this action');
      } else if (error.response.status === 429) {
        showError('Too many requests. Please wait and try again.');
      } else {
        showError(error.response.data.error.message || 'An error occurred');
      }
    } else if (error.request) {
      // Network error
      showError('Network error. Please check your connection.');
    } else {
      showError('An unexpected error occurred');
    }
    
    return Promise.reject(error);
  }
);
```

### 9.3 Form Validation

```javascript
// Generic form validator
function validateForm(formId, rules) {
  const form = document.getElementById(formId);
  const errors = [];
  
  for (const [field, validators] of Object.entries(rules)) {
    const input = form.elements[field];
    const value = input.value.trim();
    
    for (const validator of validators) {
      const error = validator(value);
      if (error) {
        errors.push({ field, message: error });
        input.classList.add('border-red-500');
      } else {
        input.classList.remove('border-red-500');
      }
    }
  }
  
  return errors;
}

// Validator functions
const validators = {
  required: (value) => value ? null : 'This field is required',
  email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? null : 'Invalid email',
  minLength: (min) => (value) => value.length >= min ? null : `Min ${min} characters`,
  maxLength: (max) => (value) => value.length <= max ? null : `Max ${max} characters`
};

// Usage
const errors = validateForm('myForm', {
  email: [validators.required, validators.email],
  password: [validators.required, validators.minLength(8)]
});

if (errors.length > 0) {
  showErrors(errors);
  return;
}
```

---

## 10. **Complete Workflow Diagrams**

### 10.1 End-to-End Citizen Workflow

```
CITIZEN JOURNEY:
═══════════════

1. Homepage (index.html)
   │
   ├─→ Click "Get Started"
   │
2. Register (register.html)
   │   ├─ Fill form
   │   ├─ POST /api/v1/auth/register
   │   └─ Receive verification email
   │
3. Login (login.html)
   │   ├─ Enter credentials
   │   ├─ POST /api/v1/auth/login
   │   └─ Receive JWT tokens
   │
4. Dashboard (dashboard.html)
   │   ├─ GET /api/v1/analytics/dashboard
   │   ├─ GET /api/v1/services (recent)
   │   └─ GET /api/v1/geo/geojson
   │
   ├─→ Click "Request Help"
   │
5. Create Service (create-service.html)
   │   ├─ Select service type
   │   ├─ Set priority
   │   ├─ Pin location on map
   │   ├─ Write description
   │   ├─ POST /api/v1/services
   │   └─ Receive service_id
   │
6. Service Detail (service-detail.html?id=xxx)
   │   ├─ GET /api/v1/services/{id}
   │   ├─ Show status, provider, ETA
   │   └─ Live updates (WebSocket/polling)
   │
7. Service Completed
   │   ├─ POST /api/v1/services/{id}/verify
   │   └─ Rate provider

Total Pages: 7
Total API Calls: 8
Total Time: 5-10 minutes
```

### 10.2 End-to-End Provider Workflow

```
PROVIDER JOURNEY:
═════════════════

1. Login (login.html)
   │   └─ POST /api/v1/auth/login
   │
2. Provider Dashboard (provider-dashboard.html)
   │   ├─ GET /api/v1/analytics/dashboard
   │   └─ GET /api/v1/services?status=APPROVED
   │
   ├─→ Click "Available Services"
   │
3. Available Services (available-services.html)
   │   ├─ GET /api/v1/geo/nearby (location-based)
   │   ├─ See approved requests on map
   │   └─ Click "View Details"
   │
4. Service Details Modal
   │   ├─ Show full information
   │   ├─ Calculate distance
   │   └─ Click "Accept Service"
   │
5. Accept Service
   │   ├─ POST /api/v1/services/{id}/accept
   │   └─ Service assigned
   │
6. Active Services (active-services.html)
   │   ├─ GET /api/v1/services?assigned_to=me
   │   ├─ Navigate to location (GPS)
   │   └─ Arrive at scene
   │
7. Complete Service
   │   ├─ POST /api/v1/services/{id}/complete
   │   ├─ Upload proof photo (optional)
   │   └─ Wait for verification

Total Pages: 5
Total API Calls: 6
Total Time: 30-60 minutes (including travel)
```

---

## 🎯 **Summary for Beginners**

### **What You Learned**:

1. ✅ **18 HTML Pages** - Complete page inventory
2. ✅ **6 JavaScript Libraries** - What each does
3. ✅ **All Workflows** - Step-by-step user journeys
4. ✅ **HTTP Methods** - When to use GET vs POST
5. ✅ **JSON Formats** - What data looks like
6. ✅ **Real Code Examples** - Copy-paste ready

### **Key Technologies**:

```
HTML/CSS:    Structure & Style
Tailwind:    Fast UI development
JavaScript:  Interactivity
Axios:       HTTP requests
Leaflet:     Maps
Chart.js:    Visualizations
```

### **Most Common Operations**:

```javascript
// 1. Authenticate
await axios.post('/api/v1/auth/login', credentials);

// 2. Get data
await axios.get('/api/v1/services');

// 3. Create resource
await axios.post('/api/v1/services', data);

// 4. Update resource
await axios.post(`/api/v1/services/${id}`, updates);

// 5. Show on map
L.geoJSON(geojson).addTo(map);
```

---

**Document Complete!**  
**Total Pages Documented**: 18  
**Total Workflows**: 10+  
**Code Examples**: 20+  
**Ready for Development**: ✅ YES

**See Also:**
- [44-API-REFERENCE-MATRIX.md](44-API-REFERENCE-MATRIX-v3.1-SECURITY.md) - API endpoints
- [40-DATA-FORMATS.md](40-DATA-FORMATS.md) - JSON schemas
- [24-FRONTEND-IMPLEMENTATION.md](24-FRONTEND-IMPLEMENTATION.md) - Detailed implementation
