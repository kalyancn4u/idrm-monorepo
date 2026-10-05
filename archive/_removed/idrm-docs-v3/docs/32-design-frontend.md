> *Type: Document (specification) · Audience: Frontend developers · Status: Archived — v3 historical generation*

# IDRM: Complete Frontend Implementation Guide

<!-- IDRM-CLEANUP doc=v3-32-frontend status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — frontend design → `docs/mvp/60` (MVP) / `docs/ffp/61` (React=FFP)
> MVP web UI = HTML+Tailwind+vanilla-JS+Leaflet → [`../../../../docs/mvp/60-uidesign-web-interaction.md`](../../../../docs/mvp/60-uidesign-web-interaction.md).
> Any React/TypeScript/component-framework parts here are **FFP** → [`../../../../docs/ffp/61-frontend-engineering-standards.md`](../../../../docs/ffp/61-frontend-engineering-standards.md).
> *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Building the Web Interface from Scratch (For Complete Novices!)

**Version**: 3.0 Consolidated  
**Audience**: Complete beginners, junior developers, anyone new to web development  
**Technology**: HTML5 + Tailwind CSS + Vanilla JavaScript + Leaflet Maps  
**Reading Time**: 3-4 hours (do it step-by-step!)  
**Last Updated**: May 15, 2026

---

## 📚 **Table of Contents**

1. [What Is a Frontend?](#1-what-is-a-frontend)
2. [Technology Stack Overview](#2-technology-stack-overview)
3. [Prerequisites & Setup](#3-prerequisites--setup)
4. [Project Structure](#4-project-structure)
5. [Building Core Pages](#5-building-core-pages)
6. [Leaflet Map Integration](#6-leaflet-map-integration)
7. [API Integration](#7-api-integration)
8. [Authentication Flow](#8-authentication-flow)
9. [Component Library](#9-component-library)
10. [Deployment](#10-deployment)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. **What Is a Frontend?**

### 1.1 Simple Explanation (For Complete Novices)

**Frontend** = What users see and interact with in their web browser

**Think of a restaurant**:
- **Frontend** = The dining room, menu, tables (what customers see)
- **Backend** = The kitchen, storage, chef (what customers don't see)
- **Database** = The pantry, ingredients (stored data)

**In web terms**:
```
Frontend (This guide!)
↓
User's Browser → Shows HTML (structure) + CSS (style) + JavaScript (behavior)
↓
Backend (Python FastAPI) → Processes requests, business logic
↓
Database (PostgreSQL) → Stores data
```

### 1.2 What You'll Build

**IDRM Frontend** = A disaster response website with:
- ✅ **Homepage** - Welcome page with disaster info
- ✅ **Login/Register** - User authentication
- ✅ **Dashboard** - User's personal control panel
- ✅ **Map View** - Interactive map showing service requests
- ✅ **Service Request Form** - Create new emergency requests
- ✅ **Service List** - Browse all active requests
- ✅ **Profile Page** - Edit user information

**It looks like this**:
```
┌────────────────────────────────────────┐
│  🏠 IDRM Platform    Login | Register  │ ← Navigation Bar
├────────────────────────────────────────┤
│                                        │
│   🗺️  Interactive Map                 │
│   (Shows service requests as markers)  │ ← Main Content
│                                        │
│   📋 Recent Requests                   │
│   • Medical Emergency - 2 hours ago    │
│   • Food Needed - 5 hours ago          │
│                                        │
└────────────────────────────────────────┘
```

---

## 2. **Technology Stack Overview**

### 2.1 The Three Building Blocks of Web Development

#### **HTML** = Structure (The Skeleton)

**What it is**: Markup language that defines WHAT is on the page

**Simple example**:
```html
<h1>This is a heading</h1>
<p>This is a paragraph</p>
<button>Click me!</button>
```

**Think of it like**: Building a house frame - defines where rooms are, but no paint or furniture yet

---

#### **CSS** = Style (The Paint & Decoration)

**What it is**: Style language that defines HOW things look

**Simple example**:
```css
h1 {
  color: blue;
  font-size: 32px;
}

button {
  background-color: green;
  padding: 10px 20px;
  border-radius: 5px;
}
```

**Think of it like**: Painting the house, choosing colors, arranging furniture

---

#### **JavaScript** = Behavior (The Electricity & Plumbing)

**What it is**: Programming language that makes things WORK

**Simple example**:
```javascript
// When button is clicked, show alert
button.addEventListener('click', function() {
  alert('Button was clicked!');
});
```

**Think of it like**: Making lights turn on, water flow, doors open automatically

---

### 2.2 Why Tailwind CSS Instead of Plain CSS?

**Plain CSS** (the old way):
```css
/* You write custom CSS for every style */
.my-button {
  background-color: blue;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
}
```

**Tailwind CSS** (the modern way):
```html
<!-- You use pre-made classes directly in HTML -->
<button class="bg-blue-600 text-white px-5 py-2 rounded-lg">
  Click me
</button>
```

**Why Tailwind is better**:
- ✅ **Faster** - No switching between HTML and CSS files
- ✅ **Consistent** - Pre-defined spacing, colors, sizes
- ✅ **Readable** - See exactly what styles are applied
- ✅ **Smaller** - No duplicate CSS code

---

### 2.3 Why Leaflet for Maps?

**Alternatives**:
- Google Maps API (costs money after quota)
- Mapbox (costs money)
- OpenStreetMap (free but complex)

**Leaflet**:
- ✅ **Free and open source**
- ✅ **Simple to use**
- ✅ **Works with OpenStreetMap** (free map tiles)
- ✅ **Lightweight** (~38KB)
- ✅ **Mobile-friendly**

**What it looks like**:
```javascript
// Just 3 lines to create a map!
const map = L.map('map').setView([20.5937, 78.9629], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
L.marker([17.385, 78.4867]).addTo(map).bindPopup('Chennai');
```

---

## 3. **Prerequisites & Setup**

### 3.1 What You Need Before Starting

#### **Software Requirements**:

1. **Code Editor** (to write code)
   - ✅ **VS Code** (recommended, free)
   - Download: https://code.visualstudio.com/
   - OR VSCodium (open-source version)
   - OR any text editor (Sublime, Atom, Notepad++)

2. **Web Browser** (to test your website)
   - ✅ **Chrome** or **Firefox** (best for development)
   - Both have built-in developer tools (F12 key)

3. **No Node.js needed!** (for HTML/Tailwind approach)
   - We use CDN links (Content Delivery Network)
   - Files load directly from internet
   - No build process required

#### **Knowledge Requirements**:

**Must know**:
- ✅ How to create folders and files
- ✅ How to open files in a browser
- ✅ Basic computer skills

**Don't need to know** (we'll teach you!):
- ❌ HTML (we'll explain everything)
- ❌ CSS (Tailwind makes it easy)
- ❌ JavaScript (we provide copy-paste code)
- ❌ Git/GitHub (not required to start)

---

### 3.2 15-Minute Setup (Step-by-Step)

#### **Step 1: Create Project Folder** (2 minutes)

```bash
# On Windows (PowerShell or Command Prompt):
cd Desktop
mkdir idrm-frontend
cd idrm-frontend

# On Mac/Linux (Terminal):
cd ~/Desktop
mkdir idrm-frontend
cd idrm-frontend
```

**What this does**: Creates a folder called "idrm-frontend" on your Desktop

---

#### **Step 2: Create Folder Structure** (3 minutes)

Create these folders and files:

```
idrm-frontend/
├── index.html          ← Homepage
├── login.html          ← Login page
├── dashboard.html      ← Dashboard page
├── map.html            ← Map page
├── css/
│   └── custom.css      ← Custom styles
├── js/
│   ├── app.js          ← Main application
│   ├── api.js          ← API client
│   ├── auth.js         ← Authentication
│   ├── map.js          ← Map functions
│   └── utils.js        ← Utility functions
└── assets/
    └── images/         ← Images folder
```

**How to create** (easy way in VS Code):
1. Open VS Code
2. File → Open Folder → Select "idrm-frontend"
3. Click "New Folder" icon to create folders
4. Click "New File" icon to create files

---

#### **Step 3: Create Your First HTML File** (5 minutes)

**Create**: `index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IDRM - Disaster Response Platform</title>
    
    <!-- Tailwind CSS (styling) -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Custom styles -->
    <link rel="stylesheet" href="css/custom.css">
</head>
<body class="bg-gray-50">
    
    <!-- Navigation Bar -->
    <nav class="bg-blue-600 text-white shadow-lg">
        <div class="container mx-auto px-4 py-4">
            <div class="flex items-center justify-between">
                <h1 class="text-2xl font-bold">🏠 IDRM Platform</h1>
                <div class="space-x-4">
                    <a href="login.html" class="hover:underline">Login</a>
                    <a href="register.html" class="bg-white text-blue-600 px-4 py-2 rounded-lg hover:bg-gray-100">
                        Register
                    </a>
                </div>
            </div>
        </div>
    </nav>
    
    <!-- Hero Section -->
    <main class="container mx-auto px-4 py-12">
        <div class="text-center mb-12">
            <h2 class="text-4xl font-bold text-gray-900 mb-4">
                Integrated Disaster Response Management
            </h2>
            <p class="text-xl text-gray-600 mb-8">
                Coordinating emergency services across India during disasters
            </p>
            <a href="map.html" class="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700">
                View Live Map →
            </a>
        </div>
        
        <!-- Features Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
            
            <!-- Feature 1 -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="text-4xl mb-4">🚑</div>
                <h3 class="text-xl font-bold mb-2">Request Services</h3>
                <p class="text-gray-600">
                    Request emergency medical, food, shelter, and rescue services during disasters.
                </p>
            </div>
            
            <!-- Feature 2 -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="text-4xl mb-4">🗺️</div>
                <h3 class="text-xl font-bold mb-2">Live Map</h3>
                <p class="text-gray-600">
                    View real-time service requests and available resources on an interactive map.
                </p>
            </div>
            
            <!-- Feature 3 -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="text-4xl mb-4">💰</div>
                <h3 class="text-xl font-bold mb-2">Transparent Donations</h3>
                <p class="text-gray-600">
                    Track how donations are allocated and used with complete transparency.
                </p>
            </div>
            
        </div>
    </main>
    
    <!-- Footer -->
    <footer class="bg-gray-800 text-white mt-16 py-8">
        <div class="container mx-auto px-4 text-center">
            <p>&copy; 2026 IDRM Platform. All rights reserved.</p>
        </div>
    </footer>
    
</body>
</html>
```

---

#### **Step 4: Create Custom CSS** (2 minutes)

**Create**: `css/custom.css`

```css
/* Custom styles for IDRM */

/* Make map fill its container */
#map {
    height: 500px;
    width: 100%;
    border-radius: 8px;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #555;
}

/* Loading spinner */
.spinner {
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3b82f6;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
```

---

#### **Step 5: Test Your First Page!** (3 minutes)

1. **Save all files** (Ctrl+S or Cmd+S)
2. **Open `index.html` in browser**:
   - **Right-click** on `index.html` → Open With → Chrome/Firefox
   - OR just **drag** `index.html` into browser window
3. **You should see**:
   - Blue navigation bar with "IDRM Platform"
   - Big heading "Integrated Disaster Response Management"
   - Three feature cards
   - Gray footer at bottom

**If it works: CONGRATULATIONS! 🎉 You just built your first webpage!**

---

## 4. **Project Structure**

### 4.1 Understanding the File Organization

```
idrm-frontend/
│
├── index.html              # Homepage (what users see first)
├── login.html              # Login page
├── register.html           # Registration page
├── dashboard.html          # User dashboard (after login)
├── map.html                # Interactive map view
├── service-request.html    # Create new service request
├── service-list.html       # List all service requests
├── service-detail.html     # View one service request
├── profile.html            # User profile page
│
├── css/
│   └── custom.css          # Your custom styles
│
├── js/
│   ├── app.js              # Main application logic
│   ├── api.js              # API calls to backend
│   ├── auth.js             # Login/logout functions
│   ├── map.js              # Map initialization and markers
│   └── utils.js            # Helper functions (formatting, etc.)
│
└── assets/
    ├── images/
    │   ├── logo.png
    │   └── hero-image.jpg
    └── markers/            # Custom map marker icons
        ├── critical.png
        ├── high.png
        ├── medium.png
        └── low.png
```

**Why this structure?**:
- ✅ **Organized** - Easy to find files
- ✅ **Scalable** - Can add more pages easily
- ✅ **Standard** - Other developers understand it
- ✅ **Maintainable** - Separate concerns (HTML/CSS/JS)

---

### 4.2 File Naming Conventions

**Rules we follow**:
1. **Lowercase** - All files lowercase (index.html, not Index.html)
2. **Hyphens** - Use hyphens for spaces (service-list.html, not service_list.html)
3. **Descriptive** - Names explain purpose (dashboard.html is obvious)
4. **Extensions** - Always include (.html, .css, .js)

**Why these rules?**:
- Works on all operating systems (Windows, Mac, Linux)
- Avoids issues with web servers
- Industry standard

---

## 5. **Building Core Pages**

### 5.1 Homepage (index.html) - ALREADY DONE! ✅

You created this in Step 3 of setup. It has:
- Navigation bar
- Hero section (big title and button)
- Feature cards (3 services)
- Footer

---

### 5.2 Login Page (login.html)

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
    
    <!-- Navigation -->
    <nav class="bg-blue-600 text-white shadow-lg">
        <div class="container mx-auto px-4 py-4">
            <div class="flex items-center justify-between">
                <h1 class="text-2xl font-bold">
                    <a href="index.html" class="hover:underline">🏠 IDRM Platform</a>
                </h1>
                <div class="space-x-4">
                    <a href="index.html" class="hover:underline">Home</a>
                    <a href="register.html" class="hover:underline">Register</a>
                </div>
            </div>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-12">
        <div class="max-w-md mx-auto">
            
            <!-- Login Card -->
            <div class="bg-white rounded-lg shadow-lg p-8">
                
                <h2 class="text-3xl font-bold text-gray-900 mb-6 text-center">
                    Login to IDRM
                </h2>
                
                <!-- Error Message (hidden by default) -->
                <div id="error-message" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 hidden">
                    <p id="error-text"></p>
                </div>
                
                <!-- Login Form -->
                <form id="login-form" onsubmit="handleLogin(event)">
                    
                    <!-- Email Field -->
                    <div class="mb-4">
                        <label for="email" class="block text-gray-700 font-semibold mb-2">
                            Email Address
                        </label>
                        <input 
                            type="email" 
                            id="email" 
                            name="email"
                            required
                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="your.email@example.com"
                        >
                    </div>
                    
                    <!-- Password Field -->
                    <div class="mb-6">
                        <label for="password" class="block text-gray-700 font-semibold mb-2">
                            Password
                        </label>
                        <input 
                            type="password" 
                            id="password" 
                            name="password"
                            required
                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Enter your password"
                        >
                    </div>
                    
                    <!-- Remember Me Checkbox -->
                    <div class="flex items-center justify-between mb-6">
                        <label class="flex items-center">
                            <input type="checkbox" id="remember" class="mr-2">
                            <span class="text-gray-700 text-sm">Remember me</span>
                        </label>
                        <a href="#" class="text-blue-600 text-sm hover:underline">
                            Forgot password?
                        </a>
                    </div>
                    
                    <!-- Submit Button -->
                    <button 
                        type="submit" 
                        id="login-button"
                        class="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition duration-200"
                    >
                        Login
                    </button>
                    
                </form>
                
                <!-- Register Link -->
                <div class="text-center mt-6">
                    <p class="text-gray-600">
                        Don't have an account? 
                        <a href="register.html" class="text-blue-600 font-semibold hover:underline">
                            Register here
                        </a>
                    </p>
                </div>
                
            </div>
            
        </div>
    </main>
    
    <!-- Scripts -->
    <script src="js/api.js"></script>
    <script src="js/auth.js"></script>
    <script src="js/utils.js"></script>
    
    <script>
        // Handle login form submission
        async function handleLogin(event) {
            event.preventDefault(); // Stop form from reloading page
            
            // Get form values
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Get button and disable it during login
            const loginButton = document.getElementById('login-button');
            loginButton.disabled = true;
            loginButton.textContent = 'Logging in...';
            
            try {
                // Call login function from auth.js
                const response = await login(email, password);
                
                // Save tokens to localStorage
                saveTokens(response.access_token, response.refresh_token);
                
                // Show success message
                alert('Login successful!');
                
                // Redirect to dashboard
                window.location.href = 'dashboard.html';
                
            } catch (error) {
                // Show error message
                showError(error.message || 'Login failed. Please try again.');
                
                // Re-enable button
                loginButton.disabled = false;
                loginButton.textContent = 'Login';
            }
        }
        
        // Show error message on page
        function showError(message) {
            const errorDiv = document.getElementById('error-message');
            const errorText = document.getElementById('error-text');
            
            errorText.textContent = message;
            errorDiv.classList.remove('hidden');
            
            // Hide error after 5 seconds
            setTimeout(() => {
                errorDiv.classList.add('hidden');
            }, 5000);
        }
    </script>
    
</body>
</html>
```

**What this page does**:
- ✅ Shows email and password input fields
- ✅ Validates inputs (required fields)
- ✅ Calls backend API when form is submitted
- ✅ Shows error messages if login fails
- ✅ Redirects to dashboard if login succeeds
- ✅ Has link to registration page

**Tailwind classes explained**:
- `bg-white` = White background
- `rounded-lg` = Rounded corners (large)
- `shadow-lg` = Drop shadow (large)
- `p-8` = Padding 32px all sides
- `mb-4` = Margin bottom 16px
- `w-full` = Width 100%
- `focus:ring-2` = Show blue ring when focused

---

### 5.3 Dashboard Page (dashboard.html)

**Create**: `dashboard.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IDRM</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="css/custom.css">
</head>
<body class="bg-gray-50">
    
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm border-b">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between h-16">
                
                <!-- Logo and Title -->
                <div class="flex items-center space-x-4">
                    <h1 class="text-2xl font-bold text-blue-600">IDRM</h1>
                    <span class="text-gray-400">|</span>
                    <span class="text-gray-700 font-medium">Dashboard</span>
                </div>
                
                <!-- Navigation Links -->
                <div class="hidden md:flex items-center space-x-6">
                    <a href="dashboard.html" class="text-blue-600 font-medium">Dashboard</a>
                    <a href="map.html" class="text-gray-600 hover:text-blue-600">Map</a>
                    <a href="service-list.html" class="text-gray-600 hover:text-blue-600">Services</a>
                    <a href="profile.html" class="text-gray-600 hover:text-blue-600">Profile</a>
                </div>
                
                <!-- User Menu -->
                <div class="flex items-center space-x-4">
                    <span id="user-name" class="text-gray-700 font-medium"></span>
                    <button 
                        onclick="handleLogout()" 
                        class="text-red-600 hover:text-red-700 font-medium"
                    >
                        Logout
                    </button>
                </div>
                
            </div>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        
        <!-- Welcome Message -->
        <div class="mb-8">
            <h2 class="text-3xl font-bold text-gray-900 mb-2">
                Welcome back, <span id="user-name-display"></span>!
            </h2>
            <p class="text-gray-600">
                Here's an overview of disaster response activities.
            </p>
        </div>
        
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            
            <!-- Active Requests -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="text-gray-600 font-medium">Active Requests</h3>
                    <span class="text-3xl">📋</span>
                </div>
                <p class="text-3xl font-bold text-gray-900" id="stat-active">0</p>
                <p class="text-sm text-gray-500 mt-1">Awaiting response</p>
            </div>
            
            <!-- Critical Priority -->
            <div class="bg-red-50 rounded-lg shadow-md p-6 border border-red-200">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="text-red-700 font-medium">Critical</h3>
                    <span class="text-3xl">🚨</span>
                </div>
                <p class="text-3xl font-bold text-red-600" id="stat-critical">0</p>
                <p class="text-sm text-red-600 mt-1">Urgent attention needed</p>
            </div>
            
            <!-- Completed Today -->
            <div class="bg-green-50 rounded-lg shadow-md p-6 border border-green-200">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="text-green-700 font-medium">Completed Today</h3>
                    <span class="text-3xl">✅</span>
                </div>
                <p class="text-3xl font-bold text-green-600" id="stat-completed">0</p>
                <p class="text-sm text-green-600 mt-1">Services delivered</p>
            </div>
            
            <!-- Total Providers -->
            <div class="bg-blue-50 rounded-lg shadow-md p-6 border border-blue-200">
                <div class="flex items-center justify-between mb-2">
                    <h3 class="text-blue-700 font-medium">Active Providers</h3>
                    <span class="text-3xl">👥</span>
                </div>
                <p class="text-3xl font-bold text-blue-600" id="stat-providers">0</p>
                <p class="text-sm text-blue-600 mt-1">Ready to help</p>
            </div>
            
        </div>
        
        <!-- Recent Service Requests -->
        <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-xl font-bold text-gray-900">Recent Service Requests</h3>
                <a href="service-list.html" class="text-blue-600 hover:underline">View all →</a>
            </div>
            
            <!-- Service List -->
            <div id="recent-services" class="space-y-4">
                <!-- Services will be loaded here by JavaScript -->
                <div class="text-center py-8 text-gray-500">
                    <div class="spinner mx-auto mb-4"></div>
                    <p>Loading recent services...</p>
                </div>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <!-- Create Service Request -->
            <div class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-md p-8 text-white">
                <h3 class="text-2xl font-bold mb-2">Need Emergency Help?</h3>
                <p class="mb-4 opacity-90">Create a service request to get assistance immediately</p>
                <a 
                    href="service-request.html" 
                    class="inline-block bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100"
                >
                    Create Request
                </a>
            </div>
            
            <!-- View Map -->
            <div class="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow-md p-8 text-white">
                <h3 class="text-2xl font-bold mb-2">View Live Map</h3>
                <p class="mb-4 opacity-90">See all active service requests on an interactive map</p>
                <a 
                    href="map.html" 
                    class="inline-block bg-white text-green-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100"
                >
                    Open Map
                </a>
            </div>
            
        </div>
        
    </main>
    
    <!-- Scripts -->
    <script src="js/api.js"></script>
    <script src="js/auth.js"></script>
    <script src="js/utils.js"></script>
    
    <script>
        // Check if user is logged in
        if (!isAuthenticated()) {
            window.location.href = 'login.html';
        }
        
        // Load dashboard data when page loads
        document.addEventListener('DOMContentLoaded', async () => {
            try {
                // Get current user info
                const user = await getCurrentUser();
                document.getElementById('user-name').textContent = user.name;
                document.getElementById('user-name-display').textContent = user.name;
                
                // Load statistics
                await loadDashboardStats();
                
                // Load recent services
                await loadRecentServices();
                
            } catch (error) {
                console.error('Dashboard error:', error);
                alert('Failed to load dashboard. Please try refreshing.');
            }
        });
        
        // Load dashboard statistics
        async function loadDashboardStats() {
            try {
                const stats = await apiCall('/stats/dashboard');
                
                document.getElementById('stat-active').textContent = stats.active_requests || 0;
                document.getElementById('stat-critical').textContent = stats.critical_requests || 0;
                document.getElementById('stat-completed').textContent = stats.completed_today || 0;
                document.getElementById('stat-providers').textContent = stats.active_providers || 0;
                
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        // Load recent service requests
        async function loadRecentServices() {
            try {
                const services = await apiCall('/services?limit=5&sort=created_at:desc');
                
                const container = document.getElementById('recent-services');
                
                if (services.length === 0) {
                    container.innerHTML = '<p class="text-center text-gray-500 py-8">No service requests yet.</p>';
                    return;
                }
                
                container.innerHTML = services.map(service => `
                    <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <div class="flex items-center space-x-2 mb-2">
                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityClass(service.priority)}">
                                        ${service.priority}
                                    </span>
                                    <span class="text-sm text-gray-500">${formatServiceType(service.service_type)}</span>
                                </div>
                                <h4 class="font-semibold text-gray-900 mb-1">${service.title}</h4>
                                <p class="text-sm text-gray-600">${service.description.substring(0, 100)}...</p>
                                <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                                    <span>📍 ${service.location_name}</span>
                                    <span>🕐 ${formatTimeAgo(service.created_at)}</span>
                                </div>
                            </div>
                            <a href="service-detail.html?id=${service.id}" class="text-blue-600 hover:underline text-sm font-medium ml-4">
                                View →
                            </a>
                        </div>
                    </div>
                `).join('');
                
            } catch (error) {
                console.error('Error loading services:', error);
                document.getElementById('recent-services').innerHTML = 
                    '<p class="text-center text-red-500 py-8">Failed to load services.</p>';
            }
        }
        
        // Get Tailwind class for priority badge
        function getPriorityClass(priority) {
            const classes = {
                'CRITICAL': 'bg-red-100 text-red-700',
                'HIGH': 'bg-orange-100 text-orange-700',
                'MEDIUM': 'bg-yellow-100 text-yellow-700',
                'LOW': 'bg-blue-100 text-blue-700'
            };
            return classes[priority] || 'bg-gray-100 text-gray-700';
        }
        
        // Format service type for display
        function formatServiceType(type) {
            return type.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
        }
        
        // Format time ago (e.g., "2 hours ago")
        function formatTimeAgo(timestamp) {
            const now = new Date();
            const then = new Date(timestamp);
            const seconds = Math.floor((now - then) / 1000);
            
            if (seconds < 60) return 'Just now';
            if (seconds < 3600) return Math.floor(seconds / 60) + ' minutes ago';
            if (seconds < 86400) return Math.floor(seconds / 3600) + ' hours ago';
            return Math.floor(seconds / 86400) + ' days ago';
        }
        
        // Handle logout
        async function handleLogout() {
            if (!confirm('Are you sure you want to logout?')) return;
            
            try {
                await logout();
                window.location.href = 'index.html';
            } catch (error) {
                console.error('Logout error:', error);
                // Clear tokens anyway
                clearAuth();
                window.location.href = 'index.html';
            }
        }
    </script>
    
</body>
</html>
```

**What this page does**:
- ✅ Shows user's name in navigation
- ✅ Displays 4 statistic cards (active, critical, completed, providers)
- ✅ Lists 5 most recent service requests
- ✅ Has quick action buttons (Create Request, Open Map)
- ✅ Loads data from backend API
- ✅ Redirects to login if not authenticated

---

## 6. **Leaflet Map Integration**

### 6.1 What Is Leaflet? (For Complete Novices)

**Leaflet** = JavaScript library that creates interactive maps

**Think of it like**: Google Maps, but free and you control everything

**What you can do with it**:
- ✅ Show a map of any location
- ✅ Add markers (pins) at specific locations
- ✅ Draw shapes (circles, polygons)
- ✅ Show popups when markers are clicked
- ✅ Change map layers (satellite view, street view, etc.)

---

### 6.2 Map Page - Complete Implementation

**Create**: `map.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Map - IDRM</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Leaflet CSS (MUST come before Leaflet JS) -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="css/custom.css">
    
    <style>
        /* Make map full height minus navigation */
        #map {
            height: calc(100vh - 64px);
            width: 100%;
        }
    </style>
</head>
<body class="bg-gray-50">
    
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b h-16">
        <div class="container mx-auto px-4 h-full">
            <div class="flex items-center justify-between h-full">
                <div class="flex items-center space-x-4">
                    <h1 class="text-2xl font-bold text-blue-600">IDRM</h1>
                    <span class="text-gray-400">|</span>
                    <span class="text-gray-700 font-medium">Map View</span>
                </div>
                <div class="hidden md:flex items-center space-x-6">
                    <a href="dashboard.html" class="text-gray-600 hover:text-blue-600">Dashboard</a>
                    <a href="map.html" class="text-blue-600 font-medium">Map</a>
                    <a href="service-list.html" class="text-gray-600 hover:text-blue-600">Services</a>
                </div>
                <button onclick="handleLogout()" class="text-red-600 hover:text-red-700 font-medium">
                    Logout
                </button>
            </div>
        </div>
    </nav>
    
    <!-- Map Container -->
    <div id="map"></div>
    
    <!-- Leaflet JS Library -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <!-- Our Scripts -->
    <script src="js/api.js"></script>
    <script src="js/auth.js"></script>
    <script src="js/map.js"></script>
    
    <script>
        // Initialize map when page loads
        document.addEventListener('DOMContentLoaded', async () => {
            // Check authentication
            if (!isAuthenticated()) {
                window.location.href = 'login.html';
                return;
            }
            
            // Initialize the map
            initializeMap();
            
            // Load service markers
            await loadServiceMarkers();
        });
        
        let map; // Global map variable
        let markersLayer; // Layer for all markers
        
        // Initialize Leaflet map
        function initializeMap() {
            // Create map centered on India
            map = L.map('map').setView([20.5937, 78.9629], 5);
            
            // Add OpenStreetMap tiles (the actual map images)
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 18,
                minZoom: 4
            }).addTo(map);
            
            // Create layer group for markers (so we can clear/update them)
            markersLayer = L.layerGroup().addTo(map);
            
            console.log('Map initialized!');
        }
        
        // Load service requests and add markers
        async function loadServiceMarkers() {
            try {
                // Fetch services from API
                const services = await apiCall('/geo/services.geojson');
                
                // Clear existing markers
                markersLayer.clearLayers();
                
                // Add marker for each service
                services.features.forEach(feature => {
                    const props = feature.properties;
                    const coords = feature.geometry.coordinates;
                    
                    // Create marker
                    const marker = L.marker([coords[1], coords[0]], {
                        icon: getMarkerIcon(props.priority)
                    });
                    
                    // Create popup content
                    const popupContent = `
                        <div class="p-2" style="min-width: 200px;">
                            <div class="font-bold text-lg mb-1">${props.title}</div>
                            <div class="text-sm text-gray-600 mb-2">${props.description}</div>
                            <div class="flex items-center justify-between text-xs">
                                <span class="px-2 py-1 rounded ${getPriorityColorClass(props.priority)}">
                                    ${props.priority}
                                </span>
                                <span class="text-gray-500">${props.service_type}</span>
                            </div>
                            <div class="mt-2">
                                <a href="service-detail.html?id=${props.id}" 
                                   class="text-blue-600 hover:underline text-sm font-medium">
                                    View Details →
                                </a>
                            </div>
                        </div>
                    `;
                    
                    // Bind popup to marker
                    marker.bindPopup(popupContent);
                    
                    // Add to layer
                    markersLayer.addLayer(marker);
                });
                
                console.log(`Loaded ${services.features.length} service markers`);
                
            } catch (error) {
                console.error('Error loading service markers:', error);
                alert('Failed to load service locations. Please refresh the page.');
            }
        }
        
        // Get custom marker icon based on priority
        function getMarkerIcon(priority) {
            const iconColors = {
                'CRITICAL': 'red',
                'HIGH': 'orange',
                'MEDIUM': 'yellow',
                'LOW': 'blue'
            };
            
            const color = iconColors[priority] || 'gray';
            
            return L.icon({
                iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            });
        }
        
        // Get CSS class for priority badge
        function getPriorityColorClass(priority) {
            const classes = {
                'CRITICAL': 'bg-red-100 text-red-700',
                'HIGH': 'bg-orange-100 text-orange-700',
                'MEDIUM': 'bg-yellow-100 text-yellow-700',
                'LOW': 'bg-blue-100 text-blue-700'
            };
            return classes[priority] || 'bg-gray-100 text-gray-700';
        }
        
        // Handle logout
        async function handleLogout() {
            if (!confirm('Are you sure you want to logout?')) return;
            await logout();
            window.location.href = 'index.html';
        }
    </script>
    
</body>
</html>
```

**What this does**:
- ✅ Shows full-screen interactive map
- ✅ Centers on India
- ✅ Loads service requests from backend
- ✅ Adds colored markers based on priority:
  - 🔴 Red = Critical
  - 🟠 Orange = High
  - 🟡 Yellow = Medium
  - 🔵 Blue = Low
- ✅ Shows popup when marker is clicked
- ✅ Popup has link to service details

---

### 6.3 Leaflet Concepts Explained

#### **Concept 1: Map Initialization**

```javascript
// Create a map
const map = L.map('map').setView([latitude, longitude], zoomLevel);

// Latitude/Longitude = GPS coordinates
// [20.5937, 78.9629] = Center of India
// Zoom level 5 = Can see whole country
// Zoom level 15 = Can see street level
```

#### **Concept 2: Tile Layers** (The Actual Map)

```javascript
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
    maxZoom: 18
}).addTo(map);

// This loads the actual map images from OpenStreetMap
// Think of it like: Loading Google Maps imagery
// {z} = zoom level, {x}/{y} = tile coordinates
```

#### **Concept 3: Markers** (Pins on Map)

```javascript
// Add a simple marker
L.marker([17.385, 78.4867]).addTo(map);

// Add marker with popup
L.marker([17.385, 78.4867])
    .addTo(map)
    .bindPopup('Chennai, Tamil Nadu');

// When you click the marker, popup shows!
```

#### **Concept 4: Custom Icons**

```javascript
const redIcon = L.icon({
    iconUrl: 'path/to/red-marker.png',
    iconSize: [25, 41],      // Size of icon
    iconAnchor: [12, 41],    // Point that represents marker location
    popupAnchor: [1, -34]    // Point where popup should open
});

L.marker([17.385, 78.4867], { icon: redIcon }).addTo(map);
```

---

## 7. **API Integration**

### 7.1 What Is an API? (For Complete Novices)

**API** = Application Programming Interface

**Simple explanation**: A way for your website to talk to the backend server

**Restaurant analogy**:
- **You (Frontend)** = Customer at table
- **Waiter (API)** = Takes your order to kitchen
- **Kitchen (Backend)** = Prepares your food
- **Menu (API Documentation)** = Lists what you can order

**In web terms**:
```
Your Website (Frontend)
   ↓
   Sends request: "Give me list of services"
   ↓
API (Backend Server)
   ↓
   Queries database
   ↓
   Returns data: [service1, service2, service3]
   ↓
Your Website displays the services!
```

---

### 7.2 Creating API Client (js/api.js)

**Create**: `js/api.js`

```javascript
/**
 * IDRM API Client
 * Handles all communication with backend server
 */

// Backend API URL (change this to your backend URL)
const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Make API call to backend
 * @param {string} endpoint - API endpoint (e.g., '/services')
 * @param {object} options - Fetch options (method, headers, body)
 * @returns {Promise} - Response data
 */
async function apiCall(endpoint, options = {}) {
    try {
        // Get access token from localStorage
        const token = localStorage.getItem('accessToken');
        
        // Build full URL
        const url = `${API_BASE_URL}${endpoint}`;
        
        // Default headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Add authorization header if token exists
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Make fetch request
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        // Handle 401 Unauthorized (token expired)
        if (response.status === 401) {
            // Try to refresh token
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                // Retry original request with new token
                return apiCall(endpoint, options);
            } else {
                // Refresh failed, redirect to login
                clearAuth();
                window.location.href = 'login.html';
                throw new Error('Session expired. Please login again.');
            }
        }
        
        // Handle other error status codes
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Parse and return JSON response
        const data = await response.json();
        return data;
        
    } catch (error) {
        console.error('API Call Error:', error);
        throw error;
    }
}

/**
 * Refresh access token using refresh token
 * @returns {Promise<boolean>} - True if successful
 */
async function refreshAccessToken() {
    try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
            return false;
        }
        
        const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh_token: refreshToken })
        });
        
        if (!response.ok) {
            return false;
        }
        
        const data = await response.json();
        
        // Save new access token
        localStorage.setItem('accessToken', data.access_token);
        
        return true;
        
    } catch (error) {
        console.error('Token refresh error:', error);
        return false;
    }
}

/**
 * Upload file to backend
 * @param {string} endpoint - API endpoint
 * @param {File} file - File to upload
 * @returns {Promise} - Response data
 */
async function uploadFile(endpoint, file) {
    try {
        const token = localStorage.getItem('accessToken');
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        return await response.json();
        
    } catch (error) {
        console.error('File upload error:', error);
        throw error;
    }
}

// Export for use in other files (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        apiCall,
        uploadFile
    };
}
```

**What this does**:
- ✅ Handles all API requests to backend
- ✅ Automatically adds authentication token
- ✅ Refreshes token if expired
- ✅ Handles errors gracefully
- ✅ Supports file uploads

**How to use it**:
```javascript
// GET request
const services = await apiCall('/services');

// POST request
const newService = await apiCall('/services', {
    method: 'POST',
    body: JSON.stringify({
        title: 'Medical Emergency',
        priority: 'CRITICAL'
    })
});

// PUT request
const updated = await apiCall('/services/123', {
    method: 'PUT',
    body: JSON.stringify({ status: 'COMPLETED' })
});

// DELETE request
await apiCall('/services/123', {
    method: 'DELETE'
});
```

---

### 7.3 Authentication Functions (js/auth.js)

**Create**: `js/auth.js`

```javascript
/**
 * Authentication functions
 * Handles login, logout, token management
 */

/**
 * Login user with email and password
 * @param {string} email 
 * @param {string} password 
 * @returns {Promise<object>} - Token response
 */
async function login(email, password) {
    try {
        const response = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        return response; // { access_token, refresh_token, user }
        
    } catch (error) {
        throw new Error(error.message || 'Login failed');
    }
}

/**
 * Register new user
 * @param {object} userData - User registration data
 * @returns {Promise<object>} - User response
 */
async function register(userData) {
    try {
        const response = await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        return response;
        
    } catch (error) {
        throw new Error(error.message || 'Registration failed');
    }
}

/**
 * Logout current user
 */
async function logout() {
    try {
        await apiCall('/auth/logout', {
            method: 'POST'
        });
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        clearAuth();
    }
}

/**
 * Save tokens to localStorage
 * @param {string} accessToken 
 * @param {string} refreshToken 
 */
function saveTokens(accessToken, refreshToken) {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
}

/**
 * Clear authentication data
 */
function clearAuth() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
}

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
function isAuthenticated() {
    return localStorage.getItem('accessToken') !== null;
}

/**
 * Get current logged-in user
 * @returns {Promise<object>} - User data
 */
async function getCurrentUser() {
    try {
        // Check if user data is cached
        const cachedUser = localStorage.getItem('user');
        if (cachedUser) {
            return JSON.parse(cachedUser);
        }
        
        // Fetch from API
        const user = await apiCall('/auth/me');
        
        // Cache for future use
        localStorage.setItem('user', JSON.stringify(user));
        
        return user;
        
    } catch (error) {
        console.error('Get current user error:', error);
        throw error;
    }
}

/**
 * Require authentication (redirect to login if not authenticated)
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
    }
}
```

**How to use it**:
```javascript
// In login page
const response = await login('user@example.com', 'password123');
saveTokens(response.access_token, response.refresh_token);

// Check if logged in
if (isAuthenticated()) {
    // User is logged in
}

// Get current user
const user = await getCurrentUser();
console.log(user.name); // "John Doe"

// Protect pages (add at top of dashboard.html, map.html, etc.)
requireAuth(); // Redirects to login if not authenticated

// Logout
await logout(); // Clears tokens and redirects
```

---

### 7.4 Utility Functions (js/utils.js)

**Create**: `js/utils.js`

```javascript
/**
 * Utility Functions
 * Helper functions used throughout the app
 */

/**
 * Format date/time for display
 * @param {string} isoString - ISO date string
 * @returns {string} - Formatted date
 */
function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Format time ago (e.g., "2 hours ago")
 * @param {string} isoString - ISO date string
 * @returns {string} - Formatted relative time
 */
function formatTimeAgo(isoString) {
    const now = new Date();
    const then = new Date(isoString);
    const seconds = Math.floor((now - then) / 1000);
    
    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };
    
    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return interval === 1 ? `1 ${unit} ago` : `${interval} ${unit}s ago`;
        }
    }
    
    return 'Just now';
}

/**
 * Get Tailwind CSS class for priority
 * @param {string} priority - Priority level
 * @returns {string} - CSS class
 */
function getPriorityClass(priority) {
    const classes = {
        'CRITICAL': 'bg-red-100 text-red-700 border-red-200',
        'HIGH': 'bg-orange-100 text-orange-700 border-orange-200',
        'MEDIUM': 'bg-yellow-100 text-yellow-700 border-yellow-200',
        'LOW': 'bg-blue-100 text-blue-700 border-blue-200'
    };
    return classes[priority] || 'bg-gray-100 text-gray-700 border-gray-200';
}

/**
 * Get Tailwind CSS class for status
 * @param {string} status - Status value
 * @returns {string} - CSS class
 */
function getStatusClass(status) {
    const classes = {
        'SUBMITTED': 'bg-purple-100 text-purple-700',
        'APPROVED': 'bg-blue-100 text-blue-700',
        'ASSIGNED': 'bg-yellow-100 text-yellow-700',
        'IN_PROGRESS': 'bg-orange-100 text-orange-700',
        'COMPLETED': 'bg-green-100 text-green-700',
        'VERIFIED': 'bg-green-200 text-green-800',
        'REJECTED': 'bg-red-100 text-red-700'
    };
    return classes[status] || 'bg-gray-100 text-gray-700';
}

/**
 * Format service type for display
 * @param {string} serviceType - Service type enum
 * @returns {string} - Human-readable format
 */
function formatServiceType(serviceType) {
    return serviceType
        .replace(/_/g, ' ')
        .toLowerCase()
        .replace(/\b\w/g, letter => letter.toUpperCase());
}

/**
 * Show toast notification
 * @param {string} message - Notification message
 * @param {string} type - Type (success, error, info, warning)
 */
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-4 rounded-lg shadow-lg z-50 ${getToastClass(type)}`;
    toast.textContent = message;
    
    // Add to body
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function getToastClass(type) {
    const classes = {
        'success': 'bg-green-600 text-white',
        'error': 'bg-red-600 text-white',
        'warning': 'bg-orange-600 text-white',
        'info': 'bg-blue-600 text-white'
    };
    return classes[type] || classes.info;
}

/**
 * Validate email format
 * @param {string} email 
 * @returns {boolean}
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Debounce function (limit how often function can be called)
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
```

**How to use it**:
```javascript
// Format dates
formatDate('2026-05-15T10:30:00Z'); // "May 15, 2026"
formatTimeAgo('2026-05-15T10:30:00Z'); // "2 hours ago"

// Get CSS classes
getPriorityClass('CRITICAL'); // "bg-red-100 text-red-700 border-red-200"
getStatusClass('COMPLETED'); // "bg-green-100 text-green-700"

// Format service types
formatServiceType('MEDICAL_EMERGENCY'); // "Medical Emergency"

// Show notifications
showToast('Service request created!', 'success');
showToast('Error occurred', 'error');

// Validate email
isValidEmail('test@example.com'); // true
isValidEmail('invalid-email'); // false

// Debounce search input
const debouncedSearch = debounce(searchFunction, 300);
inputElement.addEventListener('input', debouncedSearch);
```

---

## 8. **Authentication Flow**

### 8.1 How Authentication Works (For Novices)

**Authentication** = Proving you are who you say you are

**Real-world analogy**:
1. You show your ID card at entrance (Login)
2. Security gives you a visitor badge (Access Token)
3. You wear badge while inside building (Include token in requests)
4. Badge expires after 8 hours (Token expires)
5. You renew badge at reception (Refresh token)
6. You return badge when leaving (Logout)

**In IDRM**:
```
1. User enters email & password
   ↓
2. Backend verifies credentials
   ↓
3. Backend generates JWT tokens:
   - Access Token (1 hour expiry)
   - Refresh Token (7 days expiry)
   ↓
4. Frontend saves tokens in localStorage
   ↓
5. Frontend includes Access Token in every API request
   ↓
6. If Access Token expires, use Refresh Token to get new one
   ↓
7. Logout clears both tokens
```

---

### 8.2 JWT Tokens Explained

**JWT** = JSON Web Token

**What it looks like**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImV4cCI6MTY4ODU2ODAwMH0.xyz123abc456
```

**It has 3 parts** (separated by `.`):
1. **Header** - Algorithm info
2. **Payload** - User data (user_id, email, expiry)
3. **Signature** - Security signature

**Why use JWT?**:
- ✅ **Stateless** - Server doesn't need to store sessions
- ✅ **Secure** - Can't be tampered with (signature verification)
- ✅ **Self-contained** - Contains all user info needed
- ✅ **Scalable** - Works across multiple servers

---

### 8.3 Complete Login Flow Example

```javascript
// --- On login.html ---

async function handleLogin(event) {
    event.preventDefault();
    
    // 1. Get user input
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        // 2. Call backend login API
        const response = await login(email, password);
        // Response: {
        //   access_token: "eyJhbGc...",
        //   refresh_token: "eyJhbGc...",
        //   user: { id: 123, email: "test@example.com", name: "John" }
        // }
        
        // 3. Save tokens to localStorage
        saveTokens(response.access_token, response.refresh_token);
        
        // 4. Save user info
        localStorage.setItem('user', JSON.stringify(response.user));
        
        // 5. Redirect to dashboard
        window.location.href = 'dashboard.html';
        
    } catch (error) {
        // Show error to user
        alert('Login failed: ' + error.message);
    }
}

// --- On dashboard.html ---

// 1. Check if user is logged in
if (!isAuthenticated()) {
    window.location.href = 'login.html';
}

// 2. Make authenticated API request
const services = await apiCall('/services');
// api.js automatically includes: Authorization: Bearer <access_token>

// 3. If token expired, api.js automatically:
//    a. Calls refresh endpoint with refresh token
//    b. Gets new access token
//    c. Retries original request
//    d. If refresh fails, redirects to login

// --- On any page when logout button clicked ---

async function handleLogout() {
    // 1. Call backend logout API
    await logout();
    
    // 2. Clear tokens from localStorage
    clearAuth();
    
    // 3. Redirect to homepage
    window.location.href = 'index.html';
}
```

---

## 9. **Component Library**

### 9.1 Reusable Priority Badge

**HTML + Tailwind**:
```html
<!-- Critical Priority Badge -->
<span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-700">
    CRITICAL
</span>

<!-- High Priority Badge -->
<span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold bg-orange-100 text-orange-700">
    HIGH
</span>

<!-- Medium Priority Badge -->
<span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">
    MEDIUM
</span>

<!-- Low Priority Badge -->
<span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-700">
    LOW
</span>
```

**JavaScript Function**:
```javascript
function createPriorityBadge(priority) {
    const badge = document.createElement('span');
    badge.className = `inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold ${getPriorityClass(priority)}`;
    badge.textContent = priority;
    return badge;
}

// Usage
const badge = createPriorityBadge('CRITICAL');
container.appendChild(badge);
```

---

### 9.2 Service Request Card

**HTML**:
```html
<div class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
        <div class="flex-1">
            <!-- Priority Badge -->
            <span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-700 mb-2">
                CRITICAL
            </span>
            <!-- Title -->
            <h3 class="text-lg font-bold text-gray-900">
                Medical Emergency - Injured Person
            </h3>
        </div>
        <!-- Service Type Icon -->
        <span class="text-3xl">🚑</span>
    </div>
    
    <!-- Description -->
    <p class="text-sm text-gray-600 mb-4">
        Person fell from height, bleeding heavily, needs immediate medical attention.
    </p>
    
    <!-- Meta Information -->
    <div class="flex items-center justify-between text-sm text-gray-500">
        <div class="flex items-center">
            <span class="mr-4">📍 Chennai, Tamil Nadu</span>
            <span>🕐 2 hours ago</span>
        </div>
        <span class="px-2 py-1 rounded bg-purple-100 text-purple-700 text-xs font-medium">
            SUBMITTED
        </span>
    </div>
    
    <!-- Action Button -->
    <div class="mt-4 pt-4 border-t border-gray-200">
        <a href="service-detail.html?id=123" 
           class="block w-full text-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium">
            View Details
        </a>
    </div>
</div>
```

---

### 9.3 Loading Spinner

**HTML**:
```html
<div class="flex items-center justify-center py-8">
    <div class="spinner"></div>
    <p class="ml-3 text-gray-600">Loading...</p>
</div>
```

**CSS** (already in custom.css):
```css
.spinner {
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3b82f6;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
```

---

### 9.4 Alert Messages

**Success Alert**:
```html
<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
    <p class="font-semibold">Success!</p>
    <p class="text-sm">Your service request has been submitted.</p>
</div>
```

**Error Alert**:
```html
<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
    <p class="font-semibold">Error!</p>
    <p class="text-sm">Failed to submit service request. Please try again.</p>
</div>
```

**Warning Alert**:
```html
<div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
    <p class="font-semibold">Warning!</p>
    <p class="text-sm">Your session will expire in 5 minutes.</p>
</div>
```

---

## 10. **Deployment**

### 10.1 What Is Deployment? (For Novices)

**Deployment** = Making your website available on the internet

**Think of it like**:
- **Development** (what we've been doing) = Cooking in your kitchen
- **Deployment** = Opening a restaurant so everyone can eat your food

**Before deployment**: Only you can see website (on localhost)  
**After deployment**: Everyone with the URL can see it

---

### 10.2 Deployment Option 1: Netlify (Easiest!)

**Netlify** = Free hosting for static websites

**Steps** (5 minutes):

1. **Create account**: Go to https://netlify.com → Sign up (free)

2. **Drag & drop**:
   - Click "Sites" → "Add new site" → "Deploy manually"
   - Drag your entire `idrm-frontend` folder into the upload area
   - Wait 30 seconds while it deploys
   - Done! Your site is live at `your-site-name.netlify.app`

**That's it!** ✅ No server setup, no configuration needed.

---

### 10.3 Deployment Option 2: GitHub Pages (Free)

**Steps**:

1. **Create GitHub account**: https://github.com (if you don't have one)

2. **Create repository**:
   - Click "New repository"
   - Name: `idrm-frontend`
   - Public
   - Create repository

3. **Upload files**:
   - Click "Upload files"
   - Drag all your files
   - Commit changes

4. **Enable GitHub Pages**:
   - Go to Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: `main` → `/root`
   - Save

5. **Access your site**:
   - Your site will be at: `https://your-username.github.io/idrm-frontend`
   - Takes ~2 minutes to deploy

---

### 10.4 Deployment Option 3: Own Server (Advanced)

**Requirements**:
- Ubuntu/Debian server
- NGINX installed
- Domain name (optional)

**Steps**:

1. **Upload files to server**:
```bash
# On your computer
scp -r idrm-frontend/* user@your-server.com:/var/www/idrm/
```

2. **Configure NGINX**:
```nginx
# /etc/nginx/sites-available/idrm
server {
    listen 80;
    server_name your-domain.com;
    
    root /var/www/idrm;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

3. **Enable site**:
```bash
sudo ln -s /etc/nginx/sites-available/idrm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

4. **Access your site**: http://your-domain.com

---

### 10.5 Update API URL for Production

**IMPORTANT**: Before deploying, update API URL in `js/api.js`

**Development** (local backend):
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

**Production** (deployed backend):
```javascript
const API_BASE_URL = 'https://api.idrm.example.com/api';
// OR if backend is on same domain:
const API_BASE_URL = '/api';
```

---

## 11. **Troubleshooting**

### 11.1 Map Not Showing (Blank Area)

**Problem**: Map container is blank/white

**Solutions**:

1. **Check Leaflet CSS is loaded**:
```html
<!-- MUST be before Leaflet JS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
```

2. **Check map has height**:
```css
#map {
    height: 500px; /* MUST have explicit height */
    width: 100%;
}
```

3. **Check initialization happens after DOM loads**:
```javascript
document.addEventListener('DOMContentLoaded', () => {
    initializeMap(); // Initialize AFTER DOM ready
});
```

4. **Check console for errors** (F12 → Console tab)

---

### 11.2 CORS Error (API Calls Failing)

**Problem**: Console shows "CORS policy: No 'Access-Control-Allow-Origin' header"

**What is CORS?**: Cross-Origin Resource Sharing - browser security feature

**Solution**: Backend must allow your frontend domain

**Backend needs** (in Python FastAPI):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "https://your-frontend.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Quick workaround for development**:
```python
allow_origins=["*"]  # Allow all origins (ONLY for development!)
```

---

### 11.3 Login Not Working

**Checklist**:

1. **Is backend running?**
   - Test: Open `http://localhost:8000/docs` in browser
   - Should show FastAPI docs

2. **Is API_BASE_URL correct?**
   - Check `js/api.js`
   - Should match backend URL

3. **Check browser console** (F12 → Console)
   - Any error messages?
   - Red error text?

4. **Check network tab** (F12 → Network)
   - Is request reaching server?
   - What status code? (200 = OK, 401 = Unauthorized, 500 = Server error)

5. **Test with curl**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

---

### 11.4 Map Markers Not Showing

**Checklist**:

1. **Check API response**:
```javascript
console.log('Services:', services); // Add this in loadServiceMarkers()
```

2. **Check GeoJSON format**:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [78.4867, 17.385]  // [longitude, latitude] ⚠️ Order matters!
      },
      "properties": {
        "id": 123,
        "title": "Medical Emergency"
      }
    }
  ]
}
```

3. **Check coordinates order**:
   - Leaflet expects: `[latitude, longitude]`
   - GeoJSON uses: `[longitude, latitude]`
   - Make sure to reverse if needed!

---

### 11.5 Styling Not Applied

**Checklist**:

1. **Check Tailwind CDN is loaded**:
```html
<script src="https://cdn.tailwindcss.com"></script>
```

2. **Check class names are correct**:
```html
<!-- Correct -->
<div class="bg-blue-600 text-white">...</div>

<!-- Wrong (typos) -->
<div class="bg-blue-600 text-whit">...</div>
```

3. **Clear browser cache**:
   - Ctrl+Shift+R (Windows/Linux)
   - Cmd+Shift+R (Mac)

---

## ✅ **Summary**

### What You've Learned

**You can now**:
- ✅ Understand what frontend, HTML, CSS, JavaScript are
- ✅ Use Tailwind CSS for styling
- ✅ Create beautiful, responsive web pages
- ✅ Integrate Leaflet maps
- ✅ Connect to backend API
- ✅ Handle user authentication (login/logout)
- ✅ Build reusable components
- ✅ Deploy to production

### Pages You Built

1. ✅ **Homepage** (`index.html`) - Welcome page with features
2. ✅ **Login Page** (`login.html`) - User authentication
3. ✅ **Dashboard** (`dashboard.html`) - Stats and recent services
4. ✅ **Map View** (`map.html`) - Interactive map with markers

### Files You Created

- 📄 `index.html` - Homepage
- 📄 `login.html` - Login page
- 📄 `dashboard.html` - Dashboard
- 📄 `map.html` - Map view
- 📁 `css/custom.css` - Custom styles
- 📁 `js/api.js` - API client
- 📁 `js/auth.js` - Authentication
- 📁 `js/utils.js` - Utilities

---

## 📖 **What's Next?**

### Build More Pages

**You still need to create**:
- `register.html` - User registration
- `service-request.html` - Create new service request
- `service-list.html` - List all services
- `service-detail.html` - View one service
- `profile.html` - Edit user profile

**Follow the same pattern**:
1. Create HTML structure
2. Add Tailwind styles
3. Add JavaScript functionality
4. Connect to backend API
5. Test and deploy

### Add More Features

**Ideas for enhancement**:
- Real-time notifications (WebSocket)
- Search and filters
- Dark mode toggle
- Multi-language support
- Offline mode (Service Workers)
- Push notifications
- File uploads (photos of disaster)

### Learn More

**Resources**:
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Leaflet**: https://leafletjs.com/reference.html
- **JavaScript**: https://javascript.info/
- **MDN Web Docs**: https://developer.mozilla.org/

---

## 🎓 **Congratulations!**

**You built a production-ready disaster response frontend from scratch!** 🎉

This is a REAL application that:
- ✅ Connects to actual backend API
- ✅ Shows real-time disaster service requests
- ✅ Has interactive maps
- ✅ Handles user authentication
- ✅ Is mobile-responsive
- ✅ Can be deployed to production

**You are now a frontend developer!** Keep building, keep learning! 🚀

---

**Document Information**  
**Version**: 3.0 Consolidated  
**Created**: May 15, 2026  
**Part of**: IDRM Consolidated Documentation Suite  
**Previous**: [23-API-SPECIFICATION.md](23-API-SPECIFICATION.md)  
**Next**: [25-BACKEND-IMPLEMENTATION.md](25-BACKEND-IMPLEMENTATION.md)  
**Feedback**: Open an issue or submit a PR on GitHub
