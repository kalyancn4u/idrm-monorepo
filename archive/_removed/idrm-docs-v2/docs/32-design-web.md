> *Type: Document (specification) · Audience: Frontend devs · Status: Archived — v2 historical generation*

# IDRM HTML/Tailwind Web Interface

<!-- IDRM-CLEANUP doc=v2-32-web status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — HTML/Tailwind web design → `docs/mvp/60` (MVP-aligned)
> Gen-2 web interface using **HTML + Tailwind** — the same stack as the MVP (ADR-004). Current source of truth =
> [`../../../../docs/mvp/60-uidesign-web-interaction.md`](../../../../docs/mvp/60-uidesign-web-interaction.md).
> ✅ MVP-aligned; specifics not normative. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

## Complete Guide for Building the Primary Web Frontend

**Version**: 2.0
**Last Updated**: May 10, 2026
**Difficulty**: 🟢 Beginner-Friendly
**Time to Complete**: 2-4 hours

---

## 📋 Table of Contents

1. [What You&#39;ll Build](#what-youll-build)
2. [Prerequisites](#prerequisites)
3. [Setup](#setup)
4. [Project Structure](#project-structure)
5. [Building Pages](#building-pages)
6. [Map Integration](#map-integration)
7. [API Integration](#api-integration)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

**🔙 Back to**: [Frontend Overview](instructions_ui_v2.md)

---

## 🎯 What You'll Build

### The Primary IDRM Web Interface

A **fast, lightweight web application** where users can:

- ✅ View disaster services on a map
- ✅ Request emergency services
- ✅ Track service status
- ✅ View their service history
- ✅ Update their profile

### What Makes This "Pure" HTML/Tailwind?

**"Pure" means NO complex build tools**:

- ❌ No React
- ❌ No npm/Bun compilation
- ❌ No webpack/Vite
- ✅ Just HTML, CSS, and JavaScript files
- ✅ Edit and refresh browser = instant changes!

---

## 🤔 What is HTML, CSS, and JavaScript?

### For Complete Beginners

Think of building a house:

**HTML** = The Structure (walls, rooms, doors)

```html
<div class="room">
  <h1 class="sign">Kitchen</h1>
  <p class="description">Where we cook food</p>
</div>
```

**CSS** = The Decoration (paint, furniture, style)

```css
.room {
  background: white;
  padding: 20px;
}
.sign {
  font-size: 24px;
  color: blue;
}
```

**JavaScript** = The Behavior (lights turn on/off, doors open/close)

```javascript
function openDoor() {
  door.style.display = 'open';
  alert('Welcome!');
}
```

### What is Tailwind CSS?

**Tailwind** = Pre-made decoration styles you can use directly in HTML

**Without Tailwind**:

```html
<style>
  .my-button {
    background-color: blue;
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
  }
</style>
<button class="my-button">Click Me</button>
```

**With Tailwind** (much easier!):

```html
<button class="bg-blue-600 text-white px-6 py-3 rounded-lg">
  Click Me
</button>
```

**Result**: Same beautiful button, less code! 🎉

---

## ✅ Prerequisites

### What You Need

**Required**:

- [X] A computer (Windows, Mac, or Linux)
- [X] A code editor (VS Code recommended - it's free!)
- [X] A web browser (Chrome, Firefox, Safari, or Edge)
- [X] Basic computer skills (create folders, edit text files)

**Optional** (for development server):

- [ ] Python 3 (for local server) OR
- [ ] Bun (if you have it installed)

**No Installation Needed**:

- ❌ No Node.js
- ❌ No build tools
- ❌ No npm packages

### Download VS Code (Free Code Editor)

1. Go to: https://code.visualstudio.com/
2. Click "Download"
3. Install for your operating system
4. Open VS Code

---

## 🚀 Setup (15 minutes)

### Step 1: Create Project Folder

```bash
# Create project folder
mkdir idrm-web
cd idrm-web

# Create subfolders
mkdir js
mkdir css
mkdir assets
mkdir assets/images
```

**What you should have**:

```
idrm-web/
├── js/
├── css/
└── assets/
    └── images/
```

### Step 2: Create index.html

**Create**: `index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IDRM - Integrated Disaster Response Management</title>
  
    <!-- Tailwind CSS (from CDN - no installation needed!) -->
    <script src="https://cdn.tailwindcss.com"></script>
  
    <!-- Leaflet CSS (for maps) -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  
    <!-- Custom styles -->
    <link rel="stylesheet" href="css/custom.css">
</head>
<body class="bg-gray-50">
    <!-- Navigation Bar -->
    <nav class="bg-blue-600 text-white shadow-lg">
        <div class="container mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <h1 class="text-2xl font-bold">🛡️ IDRM Platform</h1>
                <div class="space-x-4">
                    <a href="index.html" class="hover:underline">Home</a>
                    <a href="map.html" class="hover:underline">Map</a>
                    <a href="services.html" class="hover:underline">Services</a>
                    <a href="login.html" class="hover:underline">Login</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <main class="container mx-auto px-4 py-8">
        <div class="bg-white rounded-lg shadow-lg p-8 text-center">
            <h2 class="text-4xl font-bold text-gray-800 mb-4">
                Emergency Response Made Simple
            </h2>
            <p class="text-xl text-gray-600 mb-8">
                Request services, track disasters, coordinate response - all in one platform.
            </p>
            <div class="space-x-4">
                <a href="map.html" class="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 text-lg font-semibold">
                    View Map
                </a>
                <a href="services.html" class="inline-block bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 text-lg font-semibold">
                    Request Service
                </a>
            </div>
        </div>

        <!-- Features Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <!-- Feature 1 -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="text-4xl mb-4">🗺️</div>
                <h3 class="text-xl font-bold mb-2">Real-Time Map</h3>
                <p class="text-gray-600">
                    View all active services and disaster zones on an interactive map.
                </p>
            </div>

            <!-- Feature 2 -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="text-4xl mb-4">🚨</div>
                <h3 class="text-xl font-bold mb-2">Quick Response</h3>
                <p class="text-gray-600">
                    Request emergency services with just a few clicks.
                </p>
            </div>

            <!-- Feature 3 -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="text-4xl mb-4">📊</div>
                <h3 class="text-xl font-bold mb-2">Track Progress</h3>
                <p class="text-gray-600">
                    Monitor service status and response times in real-time.
                </p>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white mt-12 py-6">
        <div class="container mx-auto px-4 text-center">
            <p>© 2026 IDRM Platform. Serving disaster response across India.</p>
        </div>
    </footer>

    <!-- Scripts -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

### Step 3: Create Custom CSS

**Create**: `css/custom.css`

```css
/* Custom styles for IDRM */

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Priority colors for services */
.priority-critical {
  background-color: #dc2626;
  color: white;
}

.priority-high {
  background-color: #ea580c;
  color: white;
}

.priority-medium {
  background-color: #f59e0b;
  color: white;
}

.priority-low {
  background-color: #3b82f6;
  color: white;
}

/* Map container */
#map {
  height: 500px;
  width: 100%;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Loading spinner */
.spinner {
  border: 3px solid rgba(59, 130, 246, 0.3);
  border-top-color: #3b82f6;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### Step 4: Create JavaScript File

**Create**: `js/app.js`

```javascript
// IDRM Web Application - Main JavaScript

// Configuration
const API_URL = 'http://localhost:3000/api';

// Utility function: Show loading spinner
function showLoading(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = '<div class="spinner mx-auto"></div>';
  }
}

// Utility function: Show error message
function showError(message) {
  alert(`Error: ${message}`);
}

// Utility function: Show success message
function showSuccess(message) {
  alert(`Success: ${message}`);
}

// Get authentication token
function getAuthToken() {
  return localStorage.getItem('accessToken');
}

// Set authentication token
function setAuthToken(token) {
  localStorage.setItem('accessToken', token);
}

// Clear authentication
function clearAuth() {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
}

// Check if user is logged in
function isLoggedIn() {
  return !!getAuthToken();
}

// API call wrapper
async function apiCall(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;
  const token = getAuthToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers
    });
  
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Request failed');
    }
  
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
  console.log('IDRM Web Application Loaded!');
  
  // Update navigation based on login status
  updateNavigation();
});

// Update navigation based on auth state
function updateNavigation() {
  // This will be expanded when we build the login page
  if (isLoggedIn()) {
    console.log('User is logged in');
  } else {
    console.log('User is not logged in');
  }
}
```

### Step 5: Test Your Setup

**Open `index.html` in your browser**:

**Option A - Double-click**: Just double-click `index.html` file

**Option B - VS Code**: Right-click → "Open with Live Server" (if you have the extension)

**Option C - Command line**:

```bash
# If you have Python installed
python3 -m http.server 8000
# Then open: http://localhost:8000

# OR if you have Bun
bun --watch index.html
```

**What you should see**:

- Blue navigation bar at top
- Hero section with "Emergency Response Made Simple"
- Three feature cards
- Gray footer at bottom

**If you see this: ✅ Success! You're ready to continue!**

---

## 📁 Project Structure

### Complete File Organization

```
idrm-web/
├── index.html              # Homepage
├── login.html             # Login page
├── register.html          # Registration page
├── dashboard.html         # User dashboard
├── map.html               # Interactive map
├── services.html          # Service request form
├── service-list.html      # List of services
├── service-detail.html    # Individual service details
├── profile.html           # User profile
│
├── css/
│   └── custom.css         # Custom styles
│
├── js/
│   ├── app.js             # Main application
│   ├── api.js             # API client functions
│   ├── auth.js            # Authentication functions
│   ├── map.js             # Map functions
│   └── services.js        # Service functions
│
└── assets/
    └── images/
        ├── logo.png
        └── placeholder.png
```

---

## 🏗️ Building Pages

### Page 1: Login Page

**Create**: `login.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IDRM</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="css/custom.css">
</head>
<body class="bg-gray-50">
    <!-- Navigation (same as index.html) -->
    <nav class="bg-blue-600 text-white shadow-lg">
        <div class="container mx-auto px-4 py-4">
            <h1 class="text-2xl font-bold">🛡️ IDRM Platform</h1>
        </div>
    </nav>

    <!-- Login Form -->
    <main class="container mx-auto px-4 py-12">
        <div class="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8">
            <h2 class="text-3xl font-bold text-center mb-8">Login to IDRM</h2>
          
            <!-- Error message (hidden by default) -->
            <div id="error-message" class="hidden bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                <span id="error-text"></span>
            </div>
          
            <!-- Login Form -->
            <form id="login-form" onsubmit="handleLogin(event)">
                <!-- Email -->
                <div class="mb-4">
                    <label class="block text-gray-700 font-bold mb-2" for="email">
                        Email Address
                    </label>
                    <input 
                        type="email" 
                        id="email" 
                        name="email"
                        required
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                        placeholder="your.email@example.com"
                    >
                </div>

                <!-- Password -->
                <div class="mb-6">
                    <label class="block text-gray-700 font-bold mb-2" for="password">
                        Password
                    </label>
                    <input 
                        type="password" 
                        id="password" 
                        name="password"
                        required
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                        placeholder="••••••••"
                    >
                </div>

                <!-- Remember Me -->
                <div class="mb-6">
                    <label class="flex items-center">
                        <input type="checkbox" id="remember" class="mr-2">
                        <span class="text-gray-700">Remember me</span>
                    </label>
                </div>

                <!-- Submit Button -->
                <button 
                    type="submit" 
                    id="login-button"
                    class="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-bold text-lg"
                >
                    Login
                </button>
            </form>

            <!-- Links -->
            <div class="mt-6 text-center space-y-2">
                <a href="forgot-password.html" class="text-blue-600 hover:underline block">
                    Forgot Password?
                </a>
                <p class="text-gray-600">
                    Don't have an account? 
                    <a href="register.html" class="text-blue-600 hover:underline">Register</a>
                </p>
            </div>
        </div>
    </main>

    <!-- JavaScript -->
    <script src="js/app.js"></script>
    <script src="js/auth.js"></script>
</body>
</html>
```

**Create**: `js/auth.js`

```javascript
// Authentication Functions

// Handle login form submission
async function handleLogin(event) {
  event.preventDefault(); // Prevent form from reloading page
  
  // Get form values
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  // Disable submit button
  const loginButton = document.getElementById('login-button');
  loginButton.disabled = true;
  loginButton.textContent = 'Logging in...';
  
  try {
    // Call login API
    const data = await apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  
    // Save tokens
    setAuthToken(data.access_token);
    localStorage.setItem('refreshToken', data.refresh_token);
  
    // Show success
    showSuccess('Login successful!');
  
    // Redirect to dashboard
    window.location.href = 'dashboard.html';
  
  } catch (error) {
    // Show error
    showErrorMessage(error.message);
  
    // Re-enable button
    loginButton.disabled = false;
    loginButton.textContent = 'Login';
  }
}

// Show error message on page
function showErrorMessage(message) {
  const errorDiv = document.getElementById('error-message');
  const errorText = document.getElementById('error-text');
  
  errorText.textContent = message;
  errorDiv.classList.remove('hidden');
  
  // Hide after 5 seconds
  setTimeout(() => {
    errorDiv.classList.add('hidden');
  }, 5000);
}

// Handle logout
async function handleLogout() {
  if (!confirm('Are you sure you want to logout?')) {
    return;
  }
  
  try {
    // Call logout API
    await apiCall('/auth/logout', {
      method: 'POST'
    });
  
    // Clear local storage
    clearAuth();
  
    // Redirect to home
    window.location.href = 'index.html';
  
  } catch (error) {
    console.error('Logout error:', error);
    // Clear anyway
    clearAuth();
    window.location.href = 'index.html';
  }
}
```

---

### Page 2: Map Page (Interactive)

**Create**: `map.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Service Map - IDRM</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="css/custom.css">
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-blue-600 text-white shadow-lg">
        <div class="container mx-auto px-4 py-4">
            <h1 class="text-2xl font-bold">🗺️ Service Map</h1>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-6">
        <!-- Filter Controls -->
        <div class="bg-white rounded-lg shadow-md p-4 mb-4">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <!-- Service Type Filter -->
                <div>
                    <label class="block text-sm font-bold mb-2">Service Type</label>
                    <select id="filter-type" onchange="filterServices()" class="w-full border rounded px-3 py-2">
                        <option value="">All Types</option>
                        <option value="MEDICAL">Medical</option>
                        <option value="FOOD">Food</option>
                        <option value="SHELTER">Shelter</option>
                        <option value="RESCUE">Rescue</option>
                        <option value="WATER">Water</option>
                    </select>
                </div>

                <!-- Priority Filter -->
                <div>
                    <label class="block text-sm font-bold mb-2">Priority</label>
                    <select id="filter-priority" onchange="filterServices()" class="w-full border rounded px-3 py-2">
                        <option value="">All Priorities</option>
                        <option value="CRITICAL">Critical</option>
                        <option value="HIGH">High</option>
                        <option value="MEDIUM">Medium</option>
                        <option value="LOW">Low</option>
                    </select>
                </div>

                <!-- Status Filter -->
                <div>
                    <label class="block text-sm font-bold mb-2">Status</label>
                    <select id="filter-status" onchange="filterServices()" class="w-full border rounded px-3 py-2">
                        <option value="">All Status</option>
                        <option value="SUBMITTED">Submitted</option>
                        <option value="APPROVED">Approved</option>
                        <option value="IN_PROGRESS">In Progress</option>
                        <option value="COMPLETED">Completed</option>
                    </select>
                </div>

                <!-- Refresh Button -->
                <div class="flex items-end">
                    <button onclick="loadServices()" class="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                        🔄 Refresh
                    </button>
                </div>
            </div>
        </div>

        <!-- Map Container -->
        <div id="map"></div>

        <!-- Stats -->
        <div class="bg-white rounded-lg shadow-md p-4 mt-4">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                    <div class="text-3xl font-bold text-blue-600" id="stat-total">0</div>
                    <div class="text-sm text-gray-600">Total Services</div>
                </div>
                <div>
                    <div class="text-3xl font-bold text-red-600" id="stat-critical">0</div>
                    <div class="text-sm text-gray-600">Critical</div>
                </div>
                <div>
                    <div class="text-3xl font-bold text-green-600" id="stat-completed">0</div>
                    <div class="text-sm text-gray-600">Completed</div>
                </div>
                <div>
                    <div class="text-3xl font-bold text-orange-600" id="stat-pending">0</div>
                    <div class="text-sm text-gray-600">Pending</div>
                </div>
            </div>
        </div>
    </main>

    <!-- Scripts -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="js/app.js"></script>
    <script src="js/map.js"></script>
</body>
</html>
```

**Create**: `js/map.js`

```javascript
// Map Functions for IDRM

let map = null;
let markers = [];
let allServices = [];

// Initialize map
function initMap() {
  // Create map centered on India
  map = L.map('map').setView([20.5937, 78.9629], 5);
  
  // Add OpenStreetMap tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map);
  
  // Load services
  loadServices();
}

// Load services from API
async function loadServices() {
  try {
    const data = await apiCall('/services');
    allServices = data.services || [];
  
    // Update stats
    updateStats(allServices);
  
    // Show on map
    displayServicesOnMap(allServices);
  
  } catch (error) {
    showError('Failed to load services: ' + error.message);
  }
}

// Display services on map
function displayServicesOnMap(services) {
  // Clear existing markers
  markers.forEach(marker => map.removeLayer(marker));
  markers = [];
  
  // Add marker for each service
  services.forEach(service => {
    if (service.location && service.location.coordinates) {
      const [lng, lat] = service.location.coordinates;
    
      // Get marker color based on priority
      const color = getPriorityColor(service.priority);
    
      // Create custom icon
      const icon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="background-color: ${color}; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white;"></div>`,
        iconSize: [30, 30]
      });
    
      // Create marker
      const marker = L.marker([lat, lng], { icon })
        .bindPopup(createPopupContent(service))
        .addTo(map);
    
      markers.push(marker);
    }
  });
}

// Get color for priority
function getPriorityColor(priority) {
  const colors = {
    'CRITICAL': '#dc2626',
    'HIGH': '#ea580c',
    'MEDIUM': '#f59e0b',
    'LOW': '#3b82f6'
  };
  return colors[priority] || '#6b7280';
}

// Create popup content
function createPopupContent(service) {
  return `
    <div class="p-2">
      <h3 class="font-bold text-lg mb-2">${service.service_type}</h3>
      <p class="text-sm mb-1">
        <strong>Priority:</strong> 
        <span class="priority-${service.priority.toLowerCase()} px-2 py-1 rounded text-xs">
          ${service.priority}
        </span>
      </p>
      <p class="text-sm mb-1"><strong>Status:</strong> ${service.status}</p>
      <p class="text-sm mb-2">${service.description || 'No description'}</p>
      <a href="service-detail.html?id=${service.id}" class="text-blue-600 hover:underline text-sm">
        View Details →
      </a>
    </div>
  `;
}

// Update statistics
function updateStats(services) {
  const total = services.length;
  const critical = services.filter(s => s.priority === 'CRITICAL').length;
  const completed = services.filter(s => s.status === 'COMPLETED').length;
  const pending = services.filter(s => 
    s.status === 'SUBMITTED' || s.status === 'APPROVED'
  ).length;
  
  document.getElementById('stat-total').textContent = total;
  document.getElementById('stat-critical').textContent = critical;
  document.getElementById('stat-completed').textContent = completed;
  document.getElementById('stat-pending').textContent = pending;
}

// Filter services
function filterServices() {
  const typeFilter = document.getElementById('filter-type').value;
  const priorityFilter = document.getElementById('filter-priority').value;
  const statusFilter = document.getElementById('filter-status').value;
  
  let filtered = allServices;
  
  if (typeFilter) {
    filtered = filtered.filter(s => s.service_type === typeFilter);
  }
  
  if (priorityFilter) {
    filtered = filtered.filter(s => s.priority === priorityFilter);
  }
  
  if (statusFilter) {
    filtered = filtered.filter(s => s.status === statusFilter);
  }
  
  displayServicesOnMap(filtered);
  updateStats(filtered);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
  initMap();
});
```

---

## 🔌 API Integration

### Create API Client

**Create**: `js/api.js`

```javascript
// API Client for IDRM Backend

const API_CONFIG = {
  baseURL: 'http://localhost:3000/api',
  timeout: 30000
};

// Generic API request function
async function request(endpoint, options = {}) {
  const url = `${API_CONFIG.baseURL}${endpoint}`;
  const token = localStorage.getItem('accessToken');
  
  const config = {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers
    },
    ...options
  };
  
  if (options.body && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body);
  }
  
  try {
    const response = await fetch(url, config);
  
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
  
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// Authentication APIs
const authAPI = {
  login: (email, password) =>
    request('/auth/login', {
      method: 'POST',
      body: { email, password }
    }),
  
  register: (userData) =>
    request('/auth/register', {
      method: 'POST',
      body: userData
    }),
  
  logout: () =>
    request('/auth/logout', {
      method: 'POST'
    })
};

// Services APIs
const servicesAPI = {
  getAll: (filters = {}) => {
    const params = new URLSearchParams(filters).toString();
    return request(`/services${params ? '?' + params : ''}`);
  },
  
  getById: (id) =>
    request(`/services/${id}`),
  
  create: (serviceData) =>
    request('/services', {
      method: 'POST',
      body: serviceData
    }),
  
  update: (id, serviceData) =>
    request(`/services/${id}`, {
      method: 'PUT',
      body: serviceData
    })
};

// User APIs
const userAPI = {
  getProfile: () =>
    request('/users/me'),
  
  updateProfile: (userData) =>
    request('/users/me', {
      method: 'PUT',
      body: userData
    })
};
```

---

## 🚀 Deployment

### Deploy to Production Server

**Option 1: Static File Hosting** (Easiest)

```bash
# 1. Upload all files to your server
scp -r * user@server.com:/var/www/html/idrm/

# 2. Configure NGINX (see below)

# 3. Open browser to: https://your-domain.com
```

**Option 2: GitHub Pages** (Free)

```bash
# 1. Create GitHub repository
# 2. Push code to main branch
# 3. Enable GitHub Pages in Settings
# 4. Site live at: https://username.github.io/idrm-web
```

### NGINX Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html/idrm;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 🐛 Troubleshooting

### Issue 1: Map Not Showing

**Problem**: Blank space where map should be

**Solution**:

```javascript
// Make sure Leaflet CSS is loaded
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

// Make sure map div has height
#map { height: 500px; }

// Initialize after DOM is ready
document.addEventListener('DOMContentLoaded', initMap);
```

### Issue 2: API Calls Failing (CORS Error)

**Problem**: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solution**: Backend needs to allow your domain:

```javascript
// Backend should have:
app.use(cors({
  origin: 'http://localhost:8000',  // Your frontend URL
  credentials: true
}));
```

### Issue 3: Login Not Working

**Check**:

1. Is backend running? (http://localhost:3000)
2. Is API_URL correct in `js/app.js`?
3. Open browser console (F12) - any errors?
4. Check Network tab - is request reaching server?

---

## ✅ Summary

**You've learned how to**:

- ✅ Set up pure HTML/Tailwind project
- ✅ Create beautiful pages with Tailwind CSS
- ✅ Integrate Leaflet maps
- ✅ Connect to IDRM backend API
- ✅ Handle authentication
- ✅ Deploy to production

**Next Steps**:

- Build remaining pages (dashboard, service-list, profile)
- Add more features (filters, search, notifications)
- Test on different devices
- Deploy to production

**🔙 Back to**: [Frontend Overview](instructions_ui_v2.md)

**➡️ Next**: Build admin dashboard with [React SPA](instructions_react_v2.md)
