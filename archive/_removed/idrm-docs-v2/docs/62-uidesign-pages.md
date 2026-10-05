> *Type: Document (specification) · Audience: Frontend devs, designers · Status: Archived — v2 historical generation*

# IDRM Web Frontend - Complete Pages Reference

<!-- IDRM-CLEANUP doc=v2-62-pages status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — pages → `docs/mvp/60`
> Gen-2 page reference → current source of truth [`../../../../docs/mvp/60-uidesign-web-interaction.md`](../../../../docs/mvp/60-uidesign-web-interaction.md).
> ⚠ MVP; specifics not normative. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## All Pages with Full Code Examples

**Version**: 2.0  
**Last Updated**: May 10, 2026  
**Technology**: HTML/Tailwind CSS/JavaScript

---

## Table of Contents

1. [Page Structure Overview](#1-page-structure-overview)
2. [Login Page](#2-login-page)
3. [Register Page](#3-register-page)
4. [Dashboard Page](#4-dashboard-page)
5. [Map Page](#5-map-page)
6. [Create Service Request Page](#6-create-service-request-page)
7. [Service List Page](#7-service-list-page)
8. [Service Detail Page](#8-service-detail-page)
9. [Profile Page](#9-profile-page)
10. [Common Components](#10-common-components)

---

## 1. Page Structure Overview

### 1.1 File Structure

```
frontend/html-tailwind/
├── index.html              ← Landing/home page
├── login.html              ← Login page
├── register.html           ← Registration page
├── dashboard.html          ← Main dashboard
├── map.html                ← Interactive map
├── services-create.html    ← Create service request
├── services-list.html      ← List all services
├── service-detail.html     ← Service details
├── profile.html            ← User profile
│
├── js/
│   ├── api.js             ← API client (see instructions_api_v2.md)
│   ├── auth.js            ← Authentication logic
│   ├── map.js             ← Map functionality
│   ├── services.js        ← Service request logic
│   ├── utils.js           ← Utility functions
│   └── app.js             ← Main app initialization
│
├── css/
│   └── custom.css         ← Custom styles
│
└── assets/
    ├── images/
    └── markers/           ← Map marker icons
```

### 1.2 Common Layout Template

All pages use this base structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title - IDRM</title>
    
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="/css/custom.css">
</head>
<body class="bg-gray-50">
    <!-- Navigation (if logged in) -->
    <nav id="navbar"></nav>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <!-- Page-specific content here -->
    </main>
    
    <!-- Footer -->
    <footer id="footer"></footer>
    
    <!-- Scripts -->
    <script src="/js/api.js"></script>
    <script src="/js/auth.js"></script>
    <script src="/js/utils.js"></script>
    <script src="/js/app.js"></script>
    <!-- Page-specific scripts -->
</body>
</html>
```

---

## 2. Login Page

**File**: `login.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - IDRM</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="/css/custom.css">
</head>
<body class="bg-gradient-to-br from-blue-50 to-blue-100 min-h-screen">
    
    <div class="flex items-center justify-center min-h-screen">
        <div class="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
            
            <!-- Logo -->
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold text-blue-600">IDRM</h1>
                <p class="text-gray-600 mt-2">Integrated Disaster Response Management</p>
            </div>
            
            <!-- Login Form -->
            <form id="login-form" class="space-y-6">
                
                <!-- Email Input -->
                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                        Email Address
                    </label>
                    <input 
                        type="email" 
                        id="email" 
                        name="email"
                        required
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="you@example.com"
                    >
                </div>
                
                <!-- Password Input -->
                <div>
                    <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
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
                
                <!-- Remember Me & Forgot Password -->
                <div class="flex items-center justify-between">
                    <label class="flex items-center">
                        <input type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                        <span class="ml-2 text-sm text-gray-600">Remember me</span>
                    </label>
                    <a href="/forgot-password.html" class="text-sm text-blue-600 hover:text-blue-700">
                        Forgot password?
                    </a>
                </div>
                
                <!-- Error Message (hidden by default) -->
                <div id="error-message" class="hidden bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm">
                    <!-- Error text will be inserted here -->
                </div>
                
                <!-- Login Button -->
                <button 
                    type="submit"
                    id="login-btn"
                    class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition duration-200"
                >
                    Login
                </button>
                
                <!-- Register Link -->
                <div class="text-center text-sm text-gray-600">
                    Don't have an account? 
                    <a href="/register.html" class="text-blue-600 hover:text-blue-700 font-medium">
                        Register here
                    </a>
                </div>
                
            </form>
            
        </div>
    </div>
    
    <!-- Loading Overlay (hidden by default) -->
    <div id="loading-overlay" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 flex items-center space-x-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span class="text-gray-700">Logging in...</span>
        </div>
    </div>
    
    <!-- Scripts -->
    <script src="/js/api.js"></script>
    <script src="/js/auth.js"></script>
    <script src="/js/utils.js"></script>
    
    <script>
        // Login form handler
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const errorDiv = document.getElementById('error-message');
            const loadingOverlay = document.getElementById('loading-overlay');
            
            // Hide previous errors
            errorDiv.classList.add('hidden');
            
            // Show loading
            loadingOverlay.classList.remove('hidden');
            
            try {
                // Call API
                const user = await login(email, password);
                
                // Hide loading
                loadingOverlay.classList.add('hidden');
                
                // Redirect to dashboard
                window.location.href = '/dashboard.html';
                
            } catch (error) {
                // Hide loading
                loadingOverlay.classList.add('hidden');
                
                // Show error
                errorDiv.textContent = error.message || 'Invalid email or password';
                errorDiv.classList.remove('hidden');
            }
        });
    </script>
    
</body>
</html>
```

---

## 3. Register Page

**File**: `register.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register - IDRM</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="/css/custom.css">
</head>
<body class="bg-gradient-to-br from-green-50 to-green-100 min-h-screen py-8">
    
    <div class="container mx-auto px-4">
        <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-xl p-8">
            
            <!-- Header -->
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold text-green-600">Create Account</h1>
                <p class="text-gray-600 mt-2">Register for IDRM</p>
            </div>
            
            <!-- Registration Form -->
            <form id="register-form" class="space-y-6">
                
                <!-- Full Name -->
                <div>
                    <label for="full-name" class="block text-sm font-medium text-gray-700 mb-2">
                        Full Name *
                    </label>
                    <input 
                        type="text" 
                        id="full-name" 
                        required
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                        placeholder="John Doe"
                    >
                </div>
                
                <!-- Email -->
                <div>
                    <label for="reg-email" class="block text-sm font-medium text-gray-700 mb-2">
                        Email Address *
                    </label>
                    <input 
                        type="email" 
                        id="reg-email" 
                        required
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                        placeholder="you@example.com"
                    >
                    <p class="mt-1 text-xs text-gray-500">You'll need to verify this email</p>
                </div>
                
                <!-- Phone -->
                <div>
                    <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
                        Phone Number *
                    </label>
                    <input 
                        type="tel" 
                        id="phone" 
                        required
                        pattern="[0-9]{10}"
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                        placeholder="9876543210"
                    >
                    <p class="mt-1 text-xs text-gray-500">10 digits, no spaces</p>
                </div>
                
                <!-- Password -->
                <div>
                    <label for="reg-password" class="block text-sm font-medium text-gray-700 mb-2">
                        Password *
                    </label>
                    <input 
                        type="password" 
                        id="reg-password" 
                        required
                        minlength="8"
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                        placeholder="At least 8 characters"
                    >
                    <div class="mt-2 text-xs text-gray-600">
                        Password must contain:
                        <ul class="list-disc list-inside ml-2 mt-1">
                            <li>At least 8 characters</li>
                            <li>One uppercase letter</li>
                            <li>One lowercase letter</li>
                            <li>One number</li>
                        </ul>
                    </div>
                </div>
                
                <!-- Confirm Password -->
                <div>
                    <label for="confirm-password" class="block text-sm font-medium text-gray-700 mb-2">
                        Confirm Password *
                    </label>
                    <input 
                        type="password" 
                        id="confirm-password" 
                        required
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                        placeholder="Re-enter password"
                    >
                </div>
                
                <!-- Role Selection -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        I am a: *
                    </label>
                    <select 
                        id="role" 
                        required
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    >
                        <option value="CITIZEN">Citizen (Request Services)</option>
                        <option value="SERVICE_PROVIDER">Service Provider (Deliver Services)</option>
                    </select>
                </div>
                
                <!-- Terms & Conditions -->
                <div class="flex items-start">
                    <input 
                        type="checkbox" 
                        id="terms" 
                        required
                        class="mt-1 rounded border-gray-300 text-green-600 focus:ring-green-500"
                    >
                    <label for="terms" class="ml-2 text-sm text-gray-600">
                        I agree to the 
                        <a href="/terms.html" class="text-green-600 hover:text-green-700">Terms & Conditions</a> 
                        and 
                        <a href="/privacy.html" class="text-green-600 hover:text-green-700">Privacy Policy</a>
                    </label>
                </div>
                
                <!-- Error/Success Messages -->
                <div id="reg-error" class="hidden bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm"></div>
                <div id="reg-success" class="hidden bg-green-50 text-green-600 px-4 py-3 rounded-lg text-sm"></div>
                
                <!-- Register Button -->
                <button 
                    type="submit"
                    class="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition"
                >
                    Register
                </button>
                
                <!-- Login Link -->
                <div class="text-center text-sm text-gray-600">
                    Already have an account? 
                    <a href="/login.html" class="text-green-600 hover:text-green-700 font-medium">
                        Login here
                    </a>
                </div>
                
            </form>
            
        </div>
    </div>
    
    <!-- Loading Overlay -->
    <div id="loading-overlay" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
            <p class="mt-4 text-gray-700">Creating account...</p>
        </div>
    </div>
    
    <!-- Scripts -->
    <script src="/js/api.js"></script>
    <script src="/js/auth.js"></script>
    <script src="/js/utils.js"></script>
    
    <script>
        // Form handler
        document.getElementById('register-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const password = document.getElementById('reg-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            const errorDiv = document.getElementById('reg-error');
            const successDiv = document.getElementById('reg-success');
            
            // Hide previous messages
            errorDiv.classList.add('hidden');
            successDiv.classList.add('hidden');
            
            // Validate password match
            if (password !== confirmPassword) {
                errorDiv.textContent = 'Passwords do not match';
                errorDiv.classList.remove('hidden');
                return;
            }
            
            // Show loading
            document.getElementById('loading-overlay').classList.remove('hidden');
            
            try {
                const result = await registerUser({
                    email: document.getElementById('reg-email').value,
                    password: password,
                    fullName: document.getElementById('full-name').value,
                    phone: document.getElementById('phone').value,
                    role: document.getElementById('role').value
                });
                
                // Hide loading
                document.getElementById('loading-overlay').classList.add('hidden');
                
                // Show success
                successDiv.textContent = result.message;
                successDiv.classList.remove('hidden');
                
                // Redirect to login after 3 seconds
                setTimeout(() => {
                    window.location.href = '/login.html';
                }, 3000);
                
            } catch (error) {
                // Hide loading
                document.getElementById('loading-overlay').classList.add('hidden');
                
                // Show error
                const errorMessage = error.details?.errors 
                    ? error.details.errors.map(e => e.message).join(', ')
                    : error.message;
                    
                errorDiv.textContent = errorMessage;
                errorDiv.classList.remove('hidden');
            }
        });
    </script>
    
</body>
</html>
```

---

## 4. Dashboard Page

**File**: `dashboard.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - IDRM</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="/css/custom.css">
</head>
<body class="bg-gray-50">
    
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between h-16">
                
                <!-- Logo -->
                <div class="flex items-center space-x-4">
                    <h1 class="text-2xl font-bold text-blue-600">IDRM</h1>
                    <span class="text-gray-400">|</span>
                    <span class="text-gray-700 font-medium">Dashboard</span>
                </div>
                
                <!-- Navigation Links -->
                <div class="hidden md:flex items-center space-x-6">
                    <a href="/dashboard.html" class="text-blue-600 font-medium">Dashboard</a>
                    <a href="/map.html" class="text-gray-600 hover:text-blue-600">Map</a>
                    <a href="/services-list.html" class="text-gray-600 hover:text-blue-600">Services</a>
                    <a href="/profile.html" class="text-gray-600 hover:text-blue-600">Profile</a>
                </div>
                
                <!-- User Menu -->
                <div class="flex items-center space-x-4">
                    <span id="user-name" class="text-gray-700"></span>
                    <button id="logout-btn" class="text-red-600 hover:text-red-700">
                        Logout
                    </button>
                </div>
                
            </div>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        
        <!-- Welcome Section -->
        <div class="mb-8">
            <h2 class="text-3xl font-bold text-gray-800">Welcome back, <span id="dashboard-user-name"></span>!</h2>
            <p class="text-gray-600 mt-2">Here's what's happening in disaster response</p>
        </div>
        
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            
            <!-- Total Requests Card -->
            <div class="bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-medium">Total Requests</p>
                        <p id="total-requests" class="text-3xl font-bold text-gray-800 mt-2">-</p>
                    </div>
                    <div class="bg-blue-100 p-3 rounded-full">
                        <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </div>
                </div>
            </div>
            
            <!-- Critical Pending Card -->
            <div class="bg-white rounded-lg shadow-sm p-6 border-l-4 border-red-500">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-medium">Critical Pending</p>
                        <p id="critical-pending" class="text-3xl font-bold text-gray-800 mt-2">-</p>
                    </div>
                    <div class="bg-red-100 p-3 rounded-full">
                        <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    </div>
                </div>
            </div>
            
            <!-- Completion Rate Card -->
            <div class="bg-white rounded-lg shadow-sm p-6 border-l-4 border-green-500">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-medium">Completion Rate</p>
                        <p id="completion-rate" class="text-3xl font-bold text-gray-800 mt-2">-</p>
                    </div>
                    <div class="bg-green-100 p-3 rounded-full">
                        <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                </div>
            </div>
            
            <!-- Avg Response Time Card -->
            <div class="bg-white rounded-lg shadow-sm p-6 border-l-4 border-yellow-500">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-medium">Avg Response Time</p>
                        <p id="avg-response-time" class="text-3xl font-bold text-gray-800 mt-2">-</p>
                    </div>
                    <div class="bg-yellow-100 p-3 rounded-full">
                        <svg class="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                </div>
            </div>
            
        </div>
        
        <!-- Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            
            <!-- Status Distribution Chart -->
            <div class="bg-white rounded-lg shadow-sm p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Requests by Status</h3>
                <canvas id="status-chart"></canvas>
            </div>
            
            <!-- Priority Distribution Chart -->
            <div class="bg-white rounded-lg shadow-sm p-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Requests by Priority</h3>
                <canvas id="priority-chart"></canvas>
            </div>
            
        </div>
        
        <!-- Recent Services Table -->
        <div class="bg-white rounded-lg shadow-sm p-6">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-800">Recent Service Requests</h3>
                <a href="/services-list.html" class="text-blue-600 hover:text-blue-700 text-sm font-medium">
                    View All →
                </a>
            </div>
            
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-gray-50 border-b">
                        <tr>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Type</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Priority</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Status</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Location</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Created</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="recent-services" class="divide-y divide-gray-200">
                        <!-- Will be populated by JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>
        
    </main>
    
    <!-- Scripts -->
    <script src="/js/api.js"></script>
    <script src="/js/auth.js"></script>
    <script src="/js/utils.js"></script>
    
    <script>
        // Protect page
        protectPage();
        
        // Load user info
        const user = getCurrentUser();
        document.getElementById('user-name').textContent = user.full_name;
        document.getElementById('dashboard-user-name').textContent = user.full_name.split(' ')[0];
        
        // Load dashboard data
        const loadDashboard = async () => {
            try {
                const data = await getDashboardData();
                
                // Update stats
                document.getElementById('total-requests').textContent = data.total_requests;
                document.getElementById('critical-pending').textContent = data.by_priority.CRITICAL || 0;
                document.getElementById('completion-rate').textContent = `${(data.completion_rate * 100).toFixed(1)}%`;
                document.getElementById('avg-response-time').textContent = `${data.avg_response_time_minutes} min`;
                
                // Update charts
                updateStatusChart(data.by_status);
                updatePriorityChart(data.by_priority);
                
                // Load recent services
                loadRecentServices();
                
            } catch (error) {
                console.error('Failed to load dashboard:', error);
            }
        };
        
        // Update status chart
        const updateStatusChart = (statusData) => {
            new Chart(document.getElementById('status-chart'), {
                type: 'doughnut',
                data: {
                    labels: Object.keys(statusData),
                    datasets: [{
                        data: Object.values(statusData),
                        backgroundColor: ['#fbbf24', '#10b981', '#3b82f6', '#8b5cf6', '#059669']
                    }]
                }
            });
        };
        
        // Update priority chart
        const updatePriorityChart = (priorityData) => {
            new Chart(document.getElementById('priority-chart'), {
                type: 'bar',
                data: {
                    labels: Object.keys(priorityData),
                    datasets: [{
                        label: 'Requests',
                        data: Object.values(priorityData),
                        backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#6b7280']
                    }]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        };
        
        // Load recent services
        const loadRecentServices = async () => {
            try {
                const result = await getServiceRequests({ page: 1, perPage: 5 });
                const tbody = document.getElementById('recent-services');
                
                tbody.innerHTML = result.services.map(service => `
                    <tr>
                        <td class="px-4 py-3 text-sm">${service.service_type}</td>
                        <td class="px-4 py-3">
                            <span class="px-2 py-1 text-xs font-medium rounded-full ${getPriorityClass(service.priority)}">
                                ${service.priority}
                            </span>
                        </td>
                        <td class="px-4 py-3">
                            <span class="px-2 py-1 text-xs font-medium rounded-full ${getStatusClass(service.status)}">
                                ${service.status}
                            </span>
                        </td>
                        <td class="px-4 py-3 text-sm text-gray-600">${service.address.substring(0, 30)}...</td>
                        <td class="px-4 py-3 text-sm text-gray-600">${formatDate(service.created_at)}</td>
                        <td class="px-4 py-3">
                            <a href="/service-detail.html?id=${service.service_id}" class="text-blue-600 hover:text-blue-700 text-sm">
                                View
                            </a>
                        </td>
                    </tr>
                `).join('');
                
            } catch (error) {
                console.error('Failed to load recent services:', error);
            }
        };
        
        // Helper functions
        const getPriorityClass = (priority) => {
            const classes = {
                'CRITICAL': 'bg-red-100 text-red-700',
                'HIGH': 'bg-orange-100 text-orange-700',
                'MEDIUM': 'bg-blue-100 text-blue-700',
                'LOW': 'bg-gray-100 text-gray-700'
            };
            return classes[priority] || classes.MEDIUM;
        };
        
        const getStatusClass = (status) => {
            const classes = {
                'SUBMITTED': 'bg-yellow-100 text-yellow-700',
                'APPROVED': 'bg-green-100 text-green-700',
                'IN_PROGRESS': 'bg-blue-100 text-blue-700',
                'COMPLETED': 'bg-purple-100 text-purple-700',
                'VERIFIED': 'bg-green-100 text-green-700'
            };
            return classes[status] || classes.SUBMITTED;
        };
        
        const formatDate = (dateString) => {
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        };
        
        // Logout handler
        document.getElementById('logout-btn').addEventListener('click', logout);
        
        // Load dashboard on page load
        loadDashboard();
        
        // Auto-refresh every 30 seconds
        setInterval(loadDashboard, 30000);
    </script>
    
</body>
</html>
```

---

## 5. Map Page

**File**: `map.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Map - IDRM</title>
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    
    <link rel="stylesheet" href="/css/custom.css">
    
    <style>
        #map {
            height: calc(100vh - 120px);
            width: 100%;
        }
    </style>
</head>
<body class="bg-gray-50">
    
    <!-- Navigation (reuse from dashboard) -->
    <nav class="bg-white shadow-sm border-b">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between h-16">
                <div class="flex items-center space-x-4">
                    <h1 class="text-2xl font-bold text-blue-600">IDRM</h1>
                    <span class="text-gray-400">|</span>
                    <span class="text-gray-700 font-medium">Map</span>
                </div>
                <div class="hidden md:flex items-center space-x-6">
                    <a href="/dashboard.html" class="text-gray-600 hover:text-blue-600">Dashboard</a>
                    <a href="/map.html" class="text-blue-600 font-medium">Map</a>
                    <a href="/services-list.html" class="text-gray-600 hover:text-blue-600">Services</a>
                    <a href="/profile.html" class="text-gray-600 hover:text-blue-600">Profile</a>
                </div>
                <div class="flex items-center space-x-4">
                    <span id="user-name" class="text-gray-700"></span>
                    <button id="logout-btn" class="text-red-600 hover:text-red-700">Logout</button>
                </div>
            </div>
        </div>
    </nav>
    
    <!-- Map Container -->
    <div class="container mx-auto px-4 py-4">
        
        <!-- Filters -->
        <div class="bg-white rounded-lg shadow-sm p-4 mb-4">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Service Type</label>
                    <select id="filter-type" class="w-full px-3 py-2 border rounded-lg">
                        <option value="">All Types</option>
                        <option value="MEDICAL">Medical</option>
                        <option value="FOOD">Food</option>
                        <option value="SHELTER">Shelter</option>
                        <option value="RESCUE">Rescue</option>
                    </select>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                    <select id="filter-status" class="w-full px-3 py-2 border rounded-lg">
                        <option value="">All Statuses</option>
                        <option value="APPROVED">Approved</option>
                        <option value="IN_PROGRESS">In Progress</option>
                        <option value="COMPLETED">Completed</option>
                    </select>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                    <select id="filter-priority" class="w-full px-3 py-2 border rounded-lg">
                        <option value="">All Priorities</option>
                        <option value="CRITICAL">Critical</option>
                        <option value="HIGH">High</option>
                        <option value="MEDIUM">Medium</option>
                        <option value="LOW">Low</option>
                    </select>
                </div>
                
                <div class="flex items-end">
                    <button id="apply-filters" class="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                        Apply Filters
                    </button>
                </div>
                
            </div>
        </div>
        
        <!-- Map -->
        <div class="bg-white rounded-lg shadow-sm overflow-hidden">
            <div id="map"></div>
        </div>
        
    </div>
    
    <!-- Scripts -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="/js/api.js"></script>
    <script src="/js/auth.js"></script>
    <script src="/js/utils.js"></script>
    
    <script>
        // Protect page
        protectPage();
        
        // Load user
        const user = getCurrentUser();
        document.getElementById('user-name').textContent = user.full_name;
        
        // Initialize map centered on India
        const map = L.map('map').setView([20.5937, 78.9629], 5);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(map);
        
        // Store markers
        let markers = [];
        
        // Load services on map
        const loadServicesOnMap = async () => {
            try {
                const center = map.getCenter();
                const zoom = map.getZoom();
                
                // Get radius based on zoom level
                const radius = zoom < 8 ? 100000 : zoom < 12 ? 50000 : 10000;
                
                // Get filters
                const filters = {
                    lat: center.lat,
                    lng: center.lng,
                    radius: radius,
                    type: document.getElementById('filter-type').value,
                    status: document.getElementById('filter-status').value,
                    priority: document.getElementById('filter-priority').value
                };
                
                const result = await getServiceRequests(filters);
                
                // Clear existing markers
                markers.forEach(marker => map.removeLayer(marker));
                markers = [];
                
                // Add markers
                result.services.forEach(service => {
                    const [lng, lat] = service.location.coordinates;
                    
                    // Choose marker color by priority
                    const markerColor = {
                        'CRITICAL': 'red',
                        'HIGH': 'orange',
                        'MEDIUM': 'blue',
                        'LOW': 'gray'
                    }[service.priority];
                    
                    const marker = L.circleMarker([lat, lng], {
                        radius: 8,
                        fillColor: markerColor,
                        color: '#fff',
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(map);
                    
                    // Add popup
                    marker.bindPopup(`
                        <div class="p-2">
                            <h4 class="font-bold text-lg mb-2">${service.service_type}</h4>
                            <p class="text-sm mb-1"><strong>Priority:</strong> ${service.priority}</p>
                            <p class="text-sm mb-1"><strong>Status:</strong> ${service.status}</p>
                            <p class="text-sm mb-2">${service.description.substring(0, 100)}...</p>
                            <a href="/service-detail.html?id=${service.service_id}" class="text-blue-600 hover:text-blue-700 text-sm">
                                View Details →
                            </a>
                        </div>
                    `);
                    
                    markers.push(marker);
                });
                
            } catch (error) {
                console.error('Failed to load services:', error);
            }
        };
        
        // Apply filters button
        document.getElementById('apply-filters').addEventListener('click', loadServicesOnMap);
        
        // Reload when map moves
        map.on('moveend', loadServicesOnMap);
        
        // Initial load
        loadServicesOnMap();
        
        // Logout
        document.getElementById('logout-btn').addEventListener('click', logout);
    </script>
    
</body>
</html>
```

---

**Continue in next file due to length...**

---

**END OF PART 1**

**Next**: See remaining pages (Create Service, Service List, Service Detail, Profile) in continuation...

**Version**: 2.0  
**Last Updated**: May 10, 2026
