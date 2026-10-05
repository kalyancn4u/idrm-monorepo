> *Type: Document (specification) · Audience: Designers, frontend devs · Status: Archived — v2 historical generation*

# IDRM Frontend Interfaces Guide

<!-- IDRM-CLEANUP doc=v2-61-ui status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — UI → `docs/mvp/60`
> Gen-2 UI interfaces guide → current source of truth [`../../../../docs/mvp/60-uidesign-web-interaction.md`](../../../../docs/mvp/60-uidesign-web-interaction.md)
> (design-system detail in `v2-60-designsystem`). ⚠ MVP; specifics not normative. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Overview of All Three User Interfaces - Start Here

**Version**: 2.0  
**Last Updated**: May 10, 2026  
**Audience**: Beginners to Advanced Developers

---

## 📋 Quick Navigation

**You are here**: Frontend Overview (Hub Document)

**Detailed Guides**:
1. 📄 [**HTML/Tailwind Interface**](instructions_web_v2.md) - Pure web, lightweight
2. ⚛️ [**React SPA Interface**](instructions_react_v2.md) - Advanced web, admin dashboards
3. 📱 [**React Native Mobile**](instructions_mobile_v2.md) - iOS & Android apps

---

## 🎯 What is a Frontend?

### For Complete Beginners

**Simple Explanation**: The frontend is what users **see and interact with** in their browser or on their phone.

**Think of it like this**:
- **Backend** (servers, databases) = Kitchen in a restaurant
- **Frontend** (user interface) = Dining area where customers eat

The backend prepares the data (cooks food), and the frontend presents it beautifully (serves it to customers).

### IDRM Has THREE Frontends

**Why three?** Different users need different experiences:

1. **HTML/Tailwind** (Primary): Fast, simple, works everywhere
2. **React SPA** (Secondary): Rich dashboards for administrators
3. **React Native** (Mobile): Native mobile app for field workers

---

## 🤔 Which Frontend Should I Use?

### Decision Tree

```
START
  │
  ├─ Are you building for mobile (iOS/Android)?
  │   └─ YES → Use React Native Mobile ✅
  │   └─ NO → Continue...
  │
  ├─ Do you need complex dashboards with lots of data visualization?
  │   └─ YES → Use React SPA ✅
  │   └─ NO → Continue...
  │
  └─ Do you want the fastest, simplest option that works everywhere?
      └─ YES → Use HTML/Tailwind ✅
```

### Quick Comparison Table

| Feature | HTML/Tailwind | React SPA | React Native |
|---------|---------------|-----------|--------------|
| **Platform** | Web Browser | Web Browser | iOS + Android |
| **Speed** | ⚡⚡⚡ Fastest | ⚡⚡ Fast | ⚡⚡⚡ Native |
| **Learning Curve** | 🟢 Easy | 🟡 Medium | 🟡 Medium |
| **Build Step** | ❌ Not needed | ✅ Required | ✅ Required |
| **Best For** | Public users | Admins/Analysts | Field workers |
| **File Size** | 📦 Tiny (50KB) | 📦 Medium (500KB) | 📦 Large (20MB) |
| **Offline** | ❌ No | ⚠️ Partial | ✅ Full |
| **GPS** | ⚠️ Basic | ⚠️ Basic | ✅ Advanced |
| **Camera** | ⚠️ Basic | ⚠️ Basic | ✅ Full access |
| **Push Notifications** | ❌ No | ❌ No | ✅ Yes |

---

## 📱 Frontend #1: HTML/Tailwind (Primary)

### What Is It?

**Pure web interface** using:
- **HTML** - Structure (the skeleton)
- **CSS (Tailwind)** - Styling (the looks)
- **JavaScript** - Interactivity (the behavior)

**No React, No Build Tools** - Just simple files that work directly in browsers!

### Why Use It?

✅ **Fastest to load** (great for slow internet)  
✅ **Works on old devices** (Android 4.0+, IE11+)  
✅ **Easy to learn** (basic HTML/CSS/JS)  
✅ **No compilation needed** (edit and refresh!)  
✅ **Lightest weight** (~50KB total)

### Who Should Use It?

- Public users requesting disaster services
- Citizens viewing disaster information
- Volunteers in low-connectivity areas
- Anyone needing a simple, fast interface

### Example Page Structure

```html
<!DOCTYPE html>
<html>
<head>
    <title>IDRM - Request Service</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-blue-600 text-white p-4">
        <h1 class="text-2xl font-bold">IDRM Platform</h1>
    </nav>
    
    <!-- Main Content -->
    <main class="container mx-auto p-4">
        <div id="map" class="h-96 rounded-lg shadow-lg"></div>
        
        <button onclick="requestService()" 
                class="bg-blue-600 text-white px-6 py-3 rounded-lg">
            Request Emergency Service
        </button>
    </main>
    
    <!-- Scripts -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="/js/app.js"></script>
</body>
</html>
```

### Quick Start

**Time**: 15 minutes

```bash
# 1. Create folder
mkdir idrm-web
cd idrm-web

# 2. Create index.html
# (Copy example above)

# 3. Create js/app.js
mkdir js
echo 'console.log("IDRM Web Ready!");' > js/app.js

# 4. Open in browser
open index.html  # macOS
# OR
start index.html  # Windows
# OR
xdg-open index.html  # Linux
```

**➡️ Full Guide**: [instructions_web_v2.md](instructions_web_v2.md)

---

## ⚛️ Frontend #2: React SPA (Secondary)

### What Is It?

**Modern web application** using:
- **React 18** - Component-based UI library
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **TypeScript** - Type-safe JavaScript

**For Advanced Users**: Requires Node.js/Bun and a build process.

### Why Use It?

✅ **Rich components** (reusable UI pieces)  
✅ **Better state management** (complex data handling)  
✅ **Advanced interactions** (real-time updates)  
✅ **Developer tools** (debugging, testing)  
✅ **Modern ecosystem** (thousands of libraries)

### Who Should Use It?

- **Administrators** managing disaster events
- **Analysts** viewing dashboards and reports
- **Coordinators** tracking multiple services
- **Power users** needing advanced features

### Example Component

```tsx
// ServiceCard.tsx - React Component
import { useState } from 'react';

interface Service {
  id: string;
  type: string;
  priority: string;
  location: string;
}

export function ServiceCard({ service }: { service: Service }) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-bold">{service.type}</h3>
        <span className={`px-3 py-1 rounded-full text-sm ${
          service.priority === 'CRITICAL' ? 'bg-red-600 text-white' :
          service.priority === 'HIGH' ? 'bg-orange-600 text-white' :
          'bg-blue-600 text-white'
        }`}>
          {service.priority}
        </span>
      </div>
      
      <p className="text-gray-600 mt-2">{service.location}</p>
      
      <button 
        onClick={() => setExpanded(!expanded)}
        className="mt-4 text-blue-600 hover:underline"
      >
        {expanded ? 'Show Less' : 'Show More'}
      </button>
      
      {expanded && (
        <div className="mt-4 p-4 bg-gray-50 rounded">
          <p>Additional service details here...</p>
        </div>
      )}
    </div>
  );
}
```

### Quick Start

**Time**: 30 minutes

```bash
# 1. Create React app with Vite
bun create vite idrm-react-spa --template react-ts
cd idrm-react-spa

# 2. Install dependencies
bun install

# 3. Install Tailwind CSS
bun add -D tailwindcss postcss autoprefixer
bunx tailwindcss init -p

# 4. Start development server
bun run dev

# Open browser to: http://localhost:5173
```

**➡️ Full Guide**: [instructions_react_v2.md](instructions_react_v2.md)

---

## 📱 Frontend #3: React Native Mobile (iOS + Android)

### What Is It?

**Native mobile application** using:
- **React Native** - Build real mobile apps with JavaScript
- **Expo** - Tooling for easier development
- **NativeWind** - Tailwind for React Native
- **Native APIs** - Access GPS, camera, notifications

**Real Apps**: Compiles to actual iOS and Android apps (not just web in a wrapper!)

### Why Use It?

✅ **Native performance** (smooth 60fps)  
✅ **Device features** (GPS, camera, push notifications)  
✅ **Offline support** (works without internet)  
✅ **One codebase** (iOS + Android together)  
✅ **App store distribution** (professional apps)

### Who Should Use It?

- **Field workers** reporting from disaster zones
- **Emergency responders** coordinating on-site
- **Volunteers** collecting data with GPS
- **Anyone needing offline mobile access**

### Example Component

```tsx
// MapScreen.tsx - React Native
import { View, Text, Button } from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import * as Location from 'expo-location';
import { useState, useEffect } from 'react';

export function MapScreen() {
  const [location, setLocation] = useState(null);
  
  useEffect(() => {
    (async () => {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        let loc = await Location.getCurrentPositionAsync({});
        setLocation(loc.coords);
      }
    })();
  }, []);
  
  return (
    <View className="flex-1">
      <MapView
        className="flex-1"
        initialRegion={{
          latitude: location?.latitude || 20.5937,
          longitude: location?.longitude || 78.9629,
          latitudeDelta: 0.0922,
          longitudeDelta: 0.0421,
        }}
      >
        {location && (
          <Marker
            coordinate={{
              latitude: location.latitude,
              longitude: location.longitude
            }}
            title="Your Location"
          />
        )}
      </MapView>
      
      <View className="absolute bottom-4 self-center">
        <Button title="Request Service" onPress={() => {
          // Request service with current location
        }} />
      </View>
    </View>
  );
}
```

### Quick Start

**Time**: 45 minutes

```bash
# 1. Install Expo CLI globally
bun add -g expo-cli

# 2. Create new Expo app
bun create expo-app idrm-mobile
cd idrm-mobile

# 3. Install dependencies
bun install

# 4. Install NativeWind
bun add nativewind
bun add -D tailwindcss

# 5. Start development
bun start

# Scan QR code with Expo Go app on your phone!
```

**➡️ Full Guide**: [instructions_mobile_v2.md](instructions_mobile_v2.md)

---

## 🔗 Common Concepts (All Frontends)

### API Integration

All three frontends connect to the same **IDRM Backend API**.

**API Base URL**:
```javascript
// Development
const API_URL = 'http://localhost:3000/api';

// Staging
const API_URL = 'https://staging.idrm.gov.in/api';

// Production
const API_URL = 'https://idrm.gov.in/api';
```

**Example API Call** (works in all three frontends):

```javascript
// Fetch services from API
async function getServices() {
  const response = await fetch(`${API_URL}/services`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch services');
  }
  
  const data = await response.json();
  return data.services;
}
```

---

### Authentication Flow

**Same for all frontends**:

```javascript
// 1. Login
async function login(email, password) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  // Store tokens
  localStorage.setItem('accessToken', data.access_token);
  localStorage.setItem('refreshToken', data.refresh_token);
  
  return data;
}

// 2. Make authenticated requests
async function getProfile() {
  const token = localStorage.getItem('accessToken');
  
  const response = await fetch(`${API_URL}/users/me`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return response.json();
}

// 3. Logout
async function logout() {
  const token = localStorage.getItem('accessToken');
  
  await fetch(`${API_URL}/auth/logout`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  // Clear tokens
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
}
```

---

### Map Integration

All frontends use **Leaflet** (web) or **react-native-maps** (mobile) to show service locations.

**Web (HTML/Tailwind & React)**:
```javascript
// Initialize Leaflet map
const map = L.map('map').setView([20.5937, 78.9629], 5);

// Add tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Add marker
L.marker([17.385, 78.4867])
  .addTo(map)
  .bindPopup('Service Request: Medical Emergency');
```

**Mobile (React Native)**:
```tsx
import MapView, { Marker } from 'react-native-maps';

<MapView
  initialRegion={{
    latitude: 20.5937,
    longitude: 78.9629,
    latitudeDelta: 10,
    longitudeDelta: 10,
  }}
>
  <Marker
    coordinate={{ latitude: 17.385, longitude: 78.4867 }}
    title="Medical Emergency"
  />
</MapView>
```

---

## 🛠️ Development Workflow

### Typical Development Day

**HTML/Tailwind** (Simplest):
```bash
1. Edit HTML/CSS/JS files
2. Refresh browser (F5)
3. See changes instantly
4. Repeat!
```

**React SPA**:
```bash
1. Run: bun run dev
2. Edit React components
3. Hot reload (automatic refresh)
4. Build: bun run build (for production)
```

**React Native**:
```bash
1. Run: bun start
2. Scan QR code on phone
3. Edit components
4. Fast refresh on phone (automatic)
5. Build: eas build (for app stores)
```

---

## 📦 File Structure Overview

### HTML/Tailwind

```
idrm-web/
├── index.html           # Homepage
├── login.html          # Login page
├── dashboard.html      # User dashboard
├── map.html            # Map view
├── css/
│   └── custom.css      # Custom styles
├── js/
│   ├── app.js          # Main application
│   ├── api.js          # API client
│   └── auth.js         # Authentication
└── assets/
    └── images/
```

### React SPA

```
idrm-react-spa/
├── src/
│   ├── components/     # Reusable components
│   │   ├── Map/
│   │   ├── Services/
│   │   └── common/
│   ├── pages/          # Page components
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   └── MapView.tsx
│   ├── hooks/          # Custom hooks
│   ├── services/       # API services
│   ├── App.tsx         # Main app
│   └── main.tsx        # Entry point
├── package.json
└── vite.config.ts
```

### React Native

```
idrm-mobile/
├── app/
│   ├── (auth)/         # Auth screens
│   │   └── login.tsx
│   ├── (tabs)/         # Tab navigation
│   │   ├── index.tsx   # Home
│   │   ├── map.tsx     # Map
│   │   └── profile.tsx # Profile
│   └── service/
│       └── [id].tsx    # Service detail
├── components/         # Shared components
├── services/           # API services
├── app.json           # Expo config
└── package.json
```

---

## 🎨 Design System (Shared)

All three frontends use the **same design tokens** for consistency.

### Colors

```javascript
const colors = {
  primary: {
    50:  '#eff6ff',
    100: '#dbeafe',
    500: '#3b82f6',  // Main blue
    600: '#2563eb',  // Hover blue
    900: '#1e3a8a',  // Dark blue
  },
  
  emergency: {
    critical: '#dc2626',  // Red
    high: '#ea580c',      // Orange
    medium: '#f59e0b',    // Yellow
    low: '#3b82f6',       // Blue
  }
};
```

### Typography

```css
/* Headings */
h1 { font-size: 2.25rem; font-weight: 700; }
h2 { font-size: 1.875rem; font-weight: 700; }
h3 { font-size: 1.5rem; font-weight: 600; }

/* Body */
body { font-size: 1rem; line-height: 1.5; }
```

### Spacing

```javascript
const spacing = {
  xs: '0.25rem',  // 4px
  sm: '0.5rem',   // 8px
  md: '1rem',     // 16px
  lg: '1.5rem',   // 24px
  xl: '2rem',     // 32px
};
```

---

## 🚀 Deployment

### HTML/Tailwind

**Easiest** - Just upload files:

```bash
# 1. Upload all files to server
scp -r * user@server:/var/www/idrm/

# 2. Configure NGINX to serve files

# 3. Done! ✅
```

### React SPA

**Build first**, then upload:

```bash
# 1. Build for production
bun run build
# Creates: dist/ folder

# 2. Upload dist folder
scp -r dist/* user@server:/var/www/idrm/

# 3. Configure NGINX

# 4. Done! ✅
```

### React Native

**Publish to app stores**:

```bash
# 1. Build for iOS
eas build --platform ios

# 2. Build for Android
eas build --platform android

# 3. Submit to App Store & Google Play
eas submit

# 4. Wait for approval (~1-2 weeks)

# 5. Done! ✅
```

---

## 🧪 Testing

### HTML/Tailwind

**Manual testing** (simplest):
```bash
# Just open in different browsers
- Chrome
- Firefox
- Safari
- Edge

# Test on different devices
- Desktop
- Tablet
- Mobile
```

### React SPA

**Automated testing**:
```bash
# Unit tests
bun test

# E2E tests (Playwright)
bun run test:e2e

# Component tests (Storybook)
bun run storybook
```

### React Native

**Device testing**:
```bash
# Test on iOS simulator
bun run ios

# Test on Android emulator
bun run android

# Test on real device (Expo Go)
bun start
# Scan QR code with phone
```

---

## 📚 Learning Resources

### For HTML/Tailwind

**Beginners**:
- 📖 [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Learn)
- 🎥 [FreeCodeCamp HTML/CSS](https://www.freecodecamp.org/)
- 📘 [Tailwind CSS Docs](https://tailwindcss.com/docs)

**Intermediate**:
- 📖 [JavaScript.info](https://javascript.info/)
- 🎥 [Traversy Media YouTube](https://www.youtube.com/@TraversyMedia)

### For React SPA

**Beginners**:
- 📖 [React Official Tutorial](https://react.dev/learn)
- 🎥 [React for Beginners](https://reactforbeginners.com/)
- 📘 [Vite Guide](https://vitejs.dev/guide/)

**Intermediate**:
- 📖 [React Patterns](https://reactpatterns.com/)
- 📘 [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)

### For React Native

**Beginners**:
- 📖 [React Native Docs](https://reactnative.dev/docs/getting-started)
- 📘 [Expo Documentation](https://docs.expo.dev/)
- 🎥 [React Native Tutorial](https://www.youtube.com/watch?v=0-S5a0eXPoc)

**Intermediate**:
- 📖 [React Native School](https://www.reactnativeschool.com/)
- 📘 [Expo Router](https://docs.expo.dev/router/introduction/)

---

## ❓ Frequently Asked Questions

### Q1: Which frontend should I learn first?

**Answer**: Start with **HTML/Tailwind** - it's the easiest and teaches you the fundamentals. Once comfortable, move to React SPA, then React Native.

### Q2: Can I use all three frontends together?

**Answer**: **Yes!** They all connect to the same backend API. You can have:
- Public users → HTML/Tailwind
- Admins → React SPA
- Field workers → React Native mobile app

### Q3: Do I need to know JavaScript for all three?

**Answer**: **Yes**, JavaScript is the foundation for all three:
- HTML/Tailwind → Vanilla JavaScript
- React SPA → JavaScript/TypeScript
- React Native → JavaScript/TypeScript

### Q4: How long to learn each?

**Answer** (rough estimates):
- HTML/Tailwind → 1-2 weeks (basics)
- React SPA → 3-4 weeks (after HTML)
- React Native → 2-3 weeks (after React)

### Q5: Can I build just one frontend?

**Answer**: **Yes!** Start with HTML/Tailwind only. Add others as needed:
- Phase 1: HTML/Tailwind (MVP)
- Phase 2: Add React SPA (advanced features)
- Phase 3: Add React Native (mobile app)

---

## ✅ Next Steps

### Complete Beginner Path

```
Week 1: Learn HTML/CSS/JavaScript basics
  ├─ Resources: FreeCodeCamp, MDN
  └─ Practice: Build simple pages

Week 2: Learn Tailwind CSS
  ├─ Resources: Tailwind docs
  └─ Practice: Style your pages

Week 3-4: Build HTML/Tailwind IDRM interface
  ├─ Follow: instructions_web_v2.md
  └─ Build: Login, Dashboard, Map pages

Week 5-8: Learn React (optional)
  ├─ Resources: React.dev
  └─ Follow: instructions_react_v2.md

Week 9-12: Learn React Native (optional)
  ├─ Resources: React Native docs
  └─ Follow: instructions_mobile_v2.md
```

### Experienced Developer Path

```
Day 1: Read all three detailed guides
  ├─ instructions_web_v2.md
  ├─ instructions_react_v2.md
  └─ instructions_mobile_v2.md

Day 2-3: Setup all three environments
  ├─ HTML/Tailwind project
  ├─ React SPA project
  └─ React Native project

Week 1-2: Build HTML/Tailwind (primary)
Week 3-4: Build React SPA (secondary)
Week 5-6: Build React Native (mobile)
```

---

## 📖 Detailed Guides

Choose your frontend and dive deep:

### 1️⃣ HTML/Tailwind (Pure Web)
**📄 [instructions_web_v2.md](instructions_web_v2.md)**
- Full setup guide
- Page-by-page building instructions
- Leaflet map integration
- API integration examples
- Deployment guide

### 2️⃣ React SPA (Advanced Web)
**⚛️ [instructions_react_v2.md](instructions_react_v2.md)**
- React + Vite setup
- Component architecture
- State management
- React Leaflet integration
- TypeScript guide
- Testing & deployment

### 3️⃣ React Native (Mobile App)
**📱 [instructions_mobile_v2.md](instructions_mobile_v2.md)**
- Expo setup
- Native features (GPS, camera, notifications)
- Offline support
- App store deployment
- Publishing guide

---

## 🎯 Summary

**You have three frontend options**:

| Choose | If You Need |
|--------|-------------|
| **HTML/Tailwind** | Fast, simple, works everywhere |
| **React SPA** | Rich dashboards, admin tools |
| **React Native** | Native mobile app with GPS/camera |

**All three**:
- ✅ Connect to same IDRM backend
- ✅ Use same API endpoints
- ✅ Share design system
- ✅ Can work together

**Start with HTML/Tailwind**, then add others as needed!

---

**Ready to build? Pick your frontend and start coding! 🚀**
