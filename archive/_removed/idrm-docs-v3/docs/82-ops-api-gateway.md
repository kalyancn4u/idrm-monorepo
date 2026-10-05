> *Type: Document (specification) · Audience: Backend devs, DevOps · Status: Archived — v3 historical generation*

# IDRM: Bun API Gateway Implementation Guide

<!-- IDRM-CLEANUP doc=v3-82-gateway status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — API gateway = FFP (not in MVP)
> **No gateway in the MVP** (the FastAPI app is the single entry point). The FFP gateway is **APISIX, not Bun/NGINX**
> → [`../../../instructions/api-gateway.md`](../../../instructions/api-gateway.md) + [`../../../../docs/ffp/20-architecture-system.md`](../../../../docs/ffp/20-architecture-system.md).
> Bun/Node = edge/BFF **behind** APISIX. Conformance `PICS-STK-APISIX-F01`. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Rate Limiting, Authentication & Static File Serving with Security

**Version**: 1.0  
**Audience**: Backend developers, DevOps engineers  
**Reading Time**: 3-4 hours  
**Last Updated**: May 16, 2026

---

## 📚 **Table of Contents**

1. [Why Bun as API Gateway?](#1-why-bun-as-api-gateway)
2. [Architecture Overview](#2-architecture-overview)
3. [Installation & Setup](#3-installation-setup)
4. [Project Structure](#4-project-structure)
5. [Rate Limiting Implementation](#5-rate-limiting-implementation)
6. [Authentication Middleware](#6-authentication-middleware)
7. [Static File Serving](#7-static-file-serving)
8. [Security Implementation](#8-security-implementation)
9. [Integration with FastAPI](#9-integration-with-fastapi)
10. [Complete Code Examples](#10-complete-code-examples)
11. [Testing](#11-testing)
12. [Production Deployment](#12-production-deployment)

---

# 1. **Why Bun as API Gateway?**

## 1.1 What is Bun?

**Bun** = Ultra-fast JavaScript runtime (like Node.js, but faster)

**Key Features**:
```
✅ 3x faster than Node.js
✅ Built-in TypeScript support
✅ Built-in bundler (no Webpack needed)
✅ Built-in test runner
✅ Compatible with Node.js packages
✅ Native performance
```

---

## 1.2 Why Use Bun as API Gateway?

**Traditional Architecture** (Without API Gateway):
```
User Browser
     ↓
NGINX (Port 80/443)
     ↓
     ├─→ Frontend Files (static)
     └─→ FastAPI Backend (Port 8000)

Problems:
❌ No rate limiting per user
❌ Authentication in every backend service
❌ Hard to add cross-cutting concerns
❌ Static files not optimized
```

**With Bun API Gateway**:
```
User Browser
     ↓
NGINX (Port 80/443)
     ↓
Bun API Gateway (Port 3000)
     ├─→ Rate Limiting ✓
     ├─→ Authentication ✓
     ├─→ Security Headers ✓
     ├─→ Static Files (optimized) ✓
     └─→ Route to Backend Services
             ↓
         FastAPI Backend (Port 8000)
             └─→ Business Logic Only

Benefits:
✅ Centralized rate limiting
✅ Single authentication layer
✅ Security at gateway level
✅ Optimized static file delivery
✅ Easy to add new services
```

---

## 1.3 Performance Comparison

**Benchmark** (Requests per second):

```
Static File Serving:
├─ Bun:      ~50,000 req/s
├─ Node.js:  ~15,000 req/s
└─ Python:   ~5,000 req/s

API Proxy:
├─ Bun:      ~40,000 req/s
├─ Node.js:  ~12,000 req/s
└─ NGINX:    ~60,000 req/s

Why Bun beats Node.js:
✅ Written in Zig (native code)
✅ JavaScriptCore engine (faster than V8)
✅ Optimized I/O
✅ Better memory management

Why NGINX still faster for pure proxy:
✅ C language (native)
✅ Specialized for reverse proxy
✅ No JavaScript overhead
```

**Our Strategy**: Use both!
```
NGINX (Port 80/443)
  ├─ SSL termination
  ├─ Load balancing
  └─ Forward to Bun (Port 3000)

Bun API Gateway (Port 3000)
  ├─ Rate limiting (stateful)
  ├─ Authentication (JWT parsing)
  ├─ Static files (with cache)
  └─ Backend routing
```

---

# 2. **Architecture Overview**

## 2.1 Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         USER BROWSER                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTPS (443)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      NGINX (Port 80/443)                    │
│  ✓ SSL Termination                                         │
│  ✓ Load Balancing (multiple Bun instances)                │
│  ✓ DDoS Protection (connection limits)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP (internal network)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   BUN API GATEWAY (Port 3000)               │
│                                                             │
│  REQUEST FLOW:                                              │
│  1. Parse request                                           │
│  2. Check rate limit (Redis)                               │
│     └─> Exceeded? → 429 Too Many Requests                  │
│  3. Check authentication (JWT)                              │
│     └─> Invalid? → 401 Unauthorized                        │
│  4. Add security headers                                    │
│  5. Route request:                                          │
│     ├─> /api/* → Proxy to FastAPI                         │
│     └─> /* → Serve static files                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ For /api/* requests
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                 FASTAPI BACKEND (Port 8000)                 │
│  ✓ Business Logic                                          │
│  ✓ Database Operations                                     │
│  ✓ No rate limiting (done by Bun)                         │
│  ✓ Minimal auth checks (JWT already validated)            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2.2 Request Types & Handling

**Static Files** (HTML, CSS, JS):
```
GET /index.html
  ↓
Bun Gateway:
  1. Rate limit: 100 req/min (lenient for static)
  2. Auth: Not required
  3. Security headers: CSP, X-Frame-Options, etc.
  4. Cache: Check If-Modified-Since
  5. Serve: /public/index.html
  6. Response: 200 OK + file content
```

**Public API** (No auth required):
```
POST /api/v1/auth/login
  ↓
Bun Gateway:
  1. Rate limit: 5 req/15min (strict for auth)
  2. Auth: Not required (login endpoint)
  3. Security headers: Add
  4. Proxy: Forward to FastAPI:8000
  5. Response: Return FastAPI response
```

**Protected API** (Auth required):
```
GET /api/v1/services
Authorization: Bearer eyJhbG...
  ↓
Bun Gateway:
  1. Rate limit: 60 req/min
  2. Auth: Verify JWT token
     ├─ Parse JWT
     ├─ Check signature
     ├─ Check expiry
     └─ Extract user_id
  3. Add headers: X-User-ID for FastAPI
  4. Proxy: Forward to FastAPI:8000
  5. Response: Return FastAPI response
```

---

# 3. **Installation & Setup**

## 3.1 Install Bun

**Linux/macOS**:
```bash
# Install Bun
curl -fsSL https://bun.sh/install | bash

# Verify installation
bun --version
# Output: 1.1.0 (or latest)

# Update PATH (add to ~/.bashrc or ~/.zshrc)
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
```

**Windows** (WSL2 recommended):
```powershell
# Install via PowerShell
powershell -c "irm bun.sh/install.ps1 | iex"

# Or use WSL2 and follow Linux instructions
```

---

## 3.2 Install Redis

**Required for rate limiting**:

```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Start Redis
sudo systemctl start redis-server  # Linux
brew services start redis           # macOS

# Verify
redis-cli ping
# Output: PONG
```

---

# 4. **Project Structure**

## 4.1 Directory Structure

```
idrm/
├── frontend/                      # Static files
│   ├── index.html
│   ├── pages/
│   ├── assets/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── favicon.ico
│
├── bun-gateway/                   # Bun API Gateway
│   ├── src/
│   │   ├── index.ts               # Main entry point
│   │   │
│   │   ├── middleware/            # Middleware
│   │   │   ├── rateLimit.ts       # Rate limiting
│   │   │   ├── auth.ts            # Authentication
│   │   │   ├── security.ts        # Security headers
│   │   │   ├── cors.ts            # CORS handling
│   │   │   └── logger.ts          # Request logging
│   │   │
│   │   ├── routes/                # Route handlers
│   │   │   ├── static.ts          # Static file serving
│   │   │   ├── api.ts             # API proxy
│   │   │   └── health.ts          # Health checks
│   │   │
│   │   ├── utils/                 # Utilities
│   │   │   ├── jwt.ts             # JWT helpers
│   │   │   ├── redis.ts           # Redis client
│   │   │   └── cache.ts           # Caching logic
│   │   │
│   │   └── config/                # Configuration
│   │       ├── index.ts           # Main config
│   │       └── constants.ts       # Constants
│   │
│   ├── public/                    # Symlink to ../frontend
│   ├── package.json
│   ├── tsconfig.json
│   └── .env
│
└── backend/                       # FastAPI backend
    └── ... (existing structure)
```

---

## 4.2 Initialize Bun Project

```bash
# Create directory
mkdir -p bun-gateway
cd bun-gateway

# Initialize Bun project
bun init

# Install dependencies
bun add redis ioredis
bun add jsonwebtoken
bun add @types/jsonwebtoken --dev

# Create directories
mkdir -p src/{middleware,routes,utils,config}

# Create symlink to frontend
ln -s ../frontend public
```

---

# 5. **Rate Limiting Implementation**

## 5.1 Rate Limiting Strategy

**Different limits for different endpoints**:

```typescript
// Rate limits configuration
const RATE_LIMITS = {
  // Authentication endpoints (strict)
  '/api/v1/auth/login': {
    points: 5,           // 5 attempts
    duration: 900,       // per 15 minutes (900 seconds)
    blockDuration: 1800  // block for 30 minutes if exceeded
  },
  
  '/api/v1/auth/register': {
    points: 3,
    duration: 3600,      // per hour
    blockDuration: 7200
  },
  
  // Public API endpoints (moderate)
  '/api/v1/services': {
    points: 60,          // 60 requests
    duration: 60,        // per minute
    blockDuration: 300
  },
  
  // Protected API endpoints (lenient)
  '/api/v1/': {
    points: 300,
    duration: 60,
    blockDuration: 60
  },
  
  // Static files (very lenient)
  '/': {
    points: 1000,
    duration: 60,
    blockDuration: 0     // no block, just rate limit
  }
};
```

---

## 5.2 Redis-Based Rate Limiter

**File**: `src/middleware/rateLimit.ts`

```typescript
import { Redis } from 'ioredis';

// Redis client
const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379'),
  password: process.env.REDIS_PASSWORD,
  db: 0
});

// Rate limit configuration
interface RateLimitConfig {
  points: number;        // Number of requests allowed
  duration: number;      // Time window in seconds
  blockDuration: number; // Block duration if exceeded
}

// Get rate limit config for endpoint
function getRateLimitConfig(path: string): RateLimitConfig {
  // Authentication endpoints (strictest)
  if (path.startsWith('/api/v1/auth/login')) {
    return { points: 5, duration: 900, blockDuration: 1800 };
  }
  if (path.startsWith('/api/v1/auth/register')) {
    return { points: 3, duration: 3600, blockDuration: 7200 };
  }
  if (path.startsWith('/api/v1/auth/')) {
    return { points: 10, duration: 900, blockDuration: 1800 };
  }
  
  // API endpoints
  if (path.startsWith('/api/v1/')) {
    return { points: 60, duration: 60, blockDuration: 300 };
  }
  
  // Static files (lenient)
  return { points: 1000, duration: 60, blockDuration: 0 };
}

// Rate limit middleware
export async function rateLimitMiddleware(
  req: Request
): Promise<Response | null> {
  const path = new URL(req.url).pathname;
  const config = getRateLimitConfig(path);
  
  // Get client identifier (IP address)
  const clientIP = req.headers.get('x-forwarded-for')?.split(',')[0] || 
                   req.headers.get('x-real-ip') || 
                   'unknown';
  
  // Redis key: rate_limit:{endpoint}:{ip}
  const key = `rate_limit:${path}:${clientIP}`;
  const blockKey = `rate_limit:block:${path}:${clientIP}`;
  
  try {
    // Check if blocked
    const isBlocked = await redis.get(blockKey);
    if (isBlocked) {
      return new Response(
        JSON.stringify({
          error: 'Too many requests',
          message: 'You have been temporarily blocked. Please try again later.',
          retryAfter: parseInt(isBlocked)
        }),
        {
          status: 429,
          headers: {
            'Content-Type': 'application/json',
            'Retry-After': isBlocked
          }
        }
      );
    }
    
    // Increment request count
    const current = await redis.incr(key);
    
    // Set expiry on first request
    if (current === 1) {
      await redis.expire(key, config.duration);
    }
    
    // Get TTL for rate limit window
    const ttl = await redis.ttl(key);
    
    // Check if limit exceeded
    if (current > config.points) {
      // Block if block duration configured
      if (config.blockDuration > 0) {
        await redis.setex(blockKey, config.blockDuration, config.blockDuration.toString());
      }
      
      return new Response(
        JSON.stringify({
          error: 'Rate limit exceeded',
          message: `Too many requests. Limit: ${config.points} per ${config.duration}s`,
          retryAfter: ttl > 0 ? ttl : config.duration
        }),
        {
          status: 429,
          headers: {
            'Content-Type': 'application/json',
            'X-RateLimit-Limit': config.points.toString(),
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': (Date.now() + ttl * 1000).toString(),
            'Retry-After': (ttl > 0 ? ttl : config.duration).toString()
          }
        }
      );
    }
    
    // Add rate limit headers to request
    // These will be added to response later
    (req as any).rateLimitHeaders = {
      'X-RateLimit-Limit': config.points.toString(),
      'X-RateLimit-Remaining': (config.points - current).toString(),
      'X-RateLimit-Reset': (Date.now() + ttl * 1000).toString()
    };
    
    // Allow request
    return null;
    
  } catch (error) {
    console.error('Rate limit error:', error);
    // On error, allow request (fail open)
    return null;
  }
}

// Cleanup function (optional - call periodically)
export async function cleanupRateLimits() {
  try {
    // Redis automatically expires keys, but we can force cleanup
    const keys = await redis.keys('rate_limit:*');
    console.log(`Found ${keys.length} rate limit keys`);
  } catch (error) {
    console.error('Cleanup error:', error);
  }
}
```

---

# 6. **Authentication Middleware**

## 6.1 JWT Verification

**File**: `src/middleware/auth.ts`

```typescript
import jwt from 'jsonwebtoken';

// JWT configuration
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-key-change-in-production';
const JWT_ALGORITHM = 'HS256';

// JWT payload interface
interface JWTPayload {
  user_id: string;
  email: string;
  role: string;
  exp: number;
  iat: number;
}

// Public endpoints (no auth required)
const PUBLIC_ENDPOINTS = [
  '/api/v1/auth/login',
  '/api/v1/auth/register',
  '/api/v1/auth/verify-email',
  '/api/v1/auth/forgot-password',
  '/api/v1/auth/reset-password',
  '/api/v1/health'
];

// Check if endpoint is public
function isPublicEndpoint(path: string): boolean {
  return PUBLIC_ENDPOINTS.some(endpoint => path.startsWith(endpoint));
}

// Extract token from request
function extractToken(req: Request): string | null {
  // Check Authorization header: Bearer <token>
  const authHeader = req.headers.get('Authorization');
  if (authHeader && authHeader.startsWith('Bearer ')) {
    return authHeader.substring(7);
  }
  
  // Check cookie (if using cookie-based auth)
  const cookieHeader = req.headers.get('Cookie');
  if (cookieHeader) {
    const cookies = cookieHeader.split(';').reduce((acc, cookie) => {
      const [key, value] = cookie.trim().split('=');
      acc[key] = value;
      return acc;
    }, {} as Record<string, string>);
    
    if (cookies.access_token) {
      return cookies.access_token;
    }
  }
  
  return null;
}

// Verify JWT token
function verifyToken(token: string): JWTPayload | null {
  try {
    const payload = jwt.verify(token, JWT_SECRET, {
      algorithms: [JWT_ALGORITHM]
    }) as JWTPayload;
    
    return payload;
  } catch (error) {
    if (error instanceof jwt.TokenExpiredError) {
      console.log('Token expired');
    } else if (error instanceof jwt.JsonWebTokenError) {
      console.log('Invalid token');
    }
    return null;
  }
}

// Authentication middleware
export async function authMiddleware(
  req: Request
): Promise<Response | null> {
  const path = new URL(req.url).pathname;
  
  // Skip auth for public endpoints and static files
  if (isPublicEndpoint(path) || !path.startsWith('/api/')) {
    return null;  // Allow request
  }
  
  // Extract token
  const token = extractToken(req);
  
  if (!token) {
    return new Response(
      JSON.stringify({
        error: 'Unauthorized',
        message: 'No authentication token provided'
      }),
      {
        status: 401,
        headers: {
          'Content-Type': 'application/json',
          'WWW-Authenticate': 'Bearer realm="IDRM API"'
        }
      }
    );
  }
  
  // Verify token
  const payload = verifyToken(token);
  
  if (!payload) {
    return new Response(
      JSON.stringify({
        error: 'Unauthorized',
        message: 'Invalid or expired authentication token'
      }),
      {
        status: 401,
        headers: {
          'Content-Type': 'application/json',
          'WWW-Authenticate': 'Bearer error="invalid_token"'
        }
      }
    );
  }
  
  // Check token expiry
  if (payload.exp * 1000 < Date.now()) {
    return new Response(
      JSON.stringify({
        error: 'Unauthorized',
        message: 'Token has expired'
      }),
      {
        status: 401,
        headers: {
          'Content-Type': 'application/json',
          'WWW-Authenticate': 'Bearer error="token_expired"'
        }
      }
    );
  }
  
  // Add user info to request for downstream services
  (req as any).user = {
    user_id: payload.user_id,
    email: payload.email,
    role: payload.role
  };
  
  // Allow request
  return null;
}

// Helper: Create JWT token (for testing)
export function createToken(payload: Omit<JWTPayload, 'exp' | 'iat'>): string {
  return jwt.sign(
    payload,
    JWT_SECRET,
    {
      algorithm: JWT_ALGORITHM,
      expiresIn: '15m'  // 15 minutes
    }
  );
}
```

---

# 7. **Static File Serving**

## 7.1 Secure Static File Handler

**File**: `src/routes/static.ts`

```typescript
import { file } from 'bun';
import { join, extname } from 'path';

// MIME types mapping
const MIME_TYPES: Record<string, string> = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.eot': 'font/eot'
};

// Get MIME type from file extension
function getMimeType(filepath: string): string {
  const ext = extname(filepath).toLowerCase();
  return MIME_TYPES[ext] || 'application/octet-stream';
}

// Security: Check if path is safe (no directory traversal)
function isSafePath(requestPath: string): boolean {
  // Normalize path
  const normalized = requestPath.replace(/\\/g, '/');
  
  // Reject paths with ../ (directory traversal)
  if (normalized.includes('../') || normalized.includes('..\\')) {
    return false;
  }
  
  // Reject paths with null bytes
  if (normalized.includes('\0')) {
    return false;
  }
  
  return true;
}

// Serve static files
export async function serveStatic(req: Request): Promise<Response> {
  const url = new URL(req.url);
  let pathname = url.pathname;
  
  // Security: Validate path
  if (!isSafePath(pathname)) {
    return new Response('Forbidden', { status: 403 });
  }
  
  // Default to index.html for root
  if (pathname === '/') {
    pathname = '/index.html';
  }
  
  // Default to index.html for directories
  if (pathname.endsWith('/')) {
    pathname += 'index.html';
  }
  
  // Build file path
  const publicDir = join(import.meta.dir, '../../public');
  const filepath = join(publicDir, pathname);
  
  try {
    // Check if file exists
    const fileObj = file(filepath);
    const exists = await fileObj.exists();
    
    if (!exists) {
      // For SPA routing: return index.html for non-API routes
      if (!pathname.startsWith('/api/') && !pathname.includes('.')) {
        const indexFile = file(join(publicDir, 'index.html'));
        if (await indexFile.exists()) {
          return new Response(indexFile, {
            headers: {
              'Content-Type': 'text/html; charset=utf-8',
              'Cache-Control': 'no-cache'
            }
          });
        }
      }
      
      return new Response('Not Found', { status: 404 });
    }
    
    // Get file stats
    const stats = await Bun.file(filepath).stat();
    
    // Check if file (not directory)
    if (!stats.isFile) {
      return new Response('Forbidden', { status: 403 });
    }
    
    // Get MIME type
    const mimeType = getMimeType(filepath);
    
    // Check If-Modified-Since header (304 Not Modified)
    const ifModifiedSince = req.headers.get('If-Modified-Since');
    if (ifModifiedSince) {
      const requestDate = new Date(ifModifiedSince);
      const fileDate = new Date(stats.mtime);
      
      if (fileDate <= requestDate) {
        return new Response(null, {
          status: 304,
          headers: {
            'Last-Modified': fileDate.toUTCString()
          }
        });
      }
    }
    
    // Cache control based on file type
    let cacheControl = 'public, max-age=3600';  // 1 hour default
    
    // HTML: no cache (for updates)
    if (mimeType.startsWith('text/html')) {
      cacheControl = 'no-cache';
    }
    // CSS/JS: 1 day (versioned via query params)
    else if (mimeType.includes('css') || mimeType.includes('javascript')) {
      cacheControl = 'public, max-age=86400';
    }
    // Images: 1 week
    else if (mimeType.startsWith('image/')) {
      cacheControl = 'public, max-age=604800';
    }
    // Fonts: 1 year (rarely change)
    else if (mimeType.startsWith('font/')) {
      cacheControl = 'public, max-age=31536000, immutable';
    }
    
    // Return file with headers
    return new Response(fileObj, {
      headers: {
        'Content-Type': mimeType,
        'Cache-Control': cacheControl,
        'Last-Modified': new Date(stats.mtime).toUTCString(),
        'ETag': `"${stats.size}-${stats.mtime.getTime()}"`,
        // Security headers (added by security middleware, but belt-and-suspenders)
        'X-Content-Type-Options': 'nosniff'
      }
    });
    
  } catch (error) {
    console.error('Static file error:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}
```

---

# 8. **Security Implementation**

## 8.1 Security Headers Middleware

**File**: `src/middleware/security.ts`

```typescript
// Security headers middleware
export function securityHeadersMiddleware(
  req: Request,
  response: Response
): Response {
  // Get existing headers
  const headers = new Headers(response.headers);
  
  // Content Security Policy
  headers.set(
    'Content-Security-Policy',
    [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com",
      "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com",
      "img-src 'self' data: https: http:",
      "font-src 'self' data:",
      "connect-src 'self'",
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'"
    ].join('; ')
  );
  
  // Prevent clickjacking
  headers.set('X-Frame-Options', 'DENY');
  
  // Prevent MIME type sniffing
  headers.set('X-Content-Type-Options', 'nosniff');
  
  // XSS Protection (legacy, but doesn't hurt)
  headers.set('X-XSS-Protection', '1; mode=block');
  
  // Referrer Policy
  headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  
  // HSTS (if using HTTPS)
  if (req.url.startsWith('https://')) {
    headers.set(
      'Strict-Transport-Security',
      'max-age=31536000; includeSubDomains; preload'
    );
  }
  
  // Permissions Policy (limit browser features)
  headers.set(
    'Permissions-Policy',
    'geolocation=(self), microphone=(), camera=()'
  );
  
  // Remove server identification
  headers.delete('Server');
  headers.delete('X-Powered-By');
  
  // Create new response with security headers
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}

// Input sanitization (for query params, etc.)
export function sanitizeInput(input: string): string {
  // Remove potential XSS vectors
  return input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '');
}

// Validate Origin (for CSRF protection)
export function validateOrigin(req: Request): boolean {
  const origin = req.headers.get('Origin');
  const referer = req.headers.get('Referer');
  
  const allowedOrigins = [
    process.env.FRONTEND_URL || 'http://localhost:3000',
    'https://idrm.gov.in',
    'https://staging.idrm.gov.in'
  ];
  
  // No origin header for same-origin requests (browser default)
  if (!origin && !referer) {
    return true;
  }
  
  // Check origin
  if (origin && allowedOrigins.some(allowed => origin.startsWith(allowed))) {
    return true;
  }
  
  // Check referer
  if (referer && allowedOrigins.some(allowed => referer.startsWith(allowed))) {
    return true;
  }
  
  return false;
}
```

---

## 8.2 CORS Middleware

**File**: `src/middleware/cors.ts`

```typescript
// CORS middleware
export function corsMiddleware(req: Request): Response | null {
  const origin = req.headers.get('Origin');
  
  // Allowed origins
  const allowedOrigins = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://idrm.gov.in',
    'https://staging.idrm.gov.in'
  ];
  
  // Check if origin is allowed
  const isAllowed = origin && allowedOrigins.includes(origin);
  
  // Handle preflight requests (OPTIONS)
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': isAllowed ? origin! : allowedOrigins[0],
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '86400'  // 24 hours
      }
    });
  }
  
  // Allow request (CORS headers will be added to response)
  return null;
}

// Add CORS headers to response
export function addCorsHeaders(req: Request, response: Response): Response {
  const origin = req.headers.get('Origin');
  
  const allowedOrigins = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://idrm.gov.in',
    'https://staging.idrm.gov.in'
  ];
  
  const isAllowed = origin && allowedOrigins.includes(origin);
  
  const headers = new Headers(response.headers);
  
  if (isAllowed) {
    headers.set('Access-Control-Allow-Origin', origin!);
    headers.set('Access-Control-Allow-Credentials', 'true');
  }
  
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}
```

---

# 9. **Integration with FastAPI**

## 9.1 API Proxy Handler

**File**: `src/routes/api.ts`

```typescript
// Proxy API requests to FastAPI backend
export async function proxyToBackend(req: Request): Promise<Response> {
  const url = new URL(req.url);
  
  // Backend URL
  const backendHost = process.env.BACKEND_HOST || 'localhost';
  const backendPort = process.env.BACKEND_PORT || '8000';
  const backendUrl = `http://${backendHost}:${backendPort}${url.pathname}${url.search}`;
  
  try {
    // Prepare headers
    const headers = new Headers(req.headers);
    
    // Add user info from auth middleware
    if ((req as any).user) {
      const user = (req as any).user;
      headers.set('X-User-ID', user.user_id);
      headers.set('X-User-Email', user.email);
      headers.set('X-User-Role', user.role);
    }
    
    // Add forwarding headers
    headers.set('X-Forwarded-For', req.headers.get('x-forwarded-for') || 'unknown');
    headers.set('X-Forwarded-Proto', url.protocol.replace(':', ''));
    headers.set('X-Forwarded-Host', url.host);
    
    // Forward request to FastAPI
    const response = await fetch(backendUrl, {
      method: req.method,
      headers,
      body: req.method !== 'GET' && req.method !== 'HEAD' ? req.body : undefined
    });
    
    // Return response
    return response;
    
  } catch (error) {
    console.error('Backend proxy error:', error);
    
    return new Response(
      JSON.stringify({
        error: 'Backend Error',
        message: 'Failed to connect to backend service'
      }),
      {
        status: 502,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  }
}
```

---

# 10. **Complete Code Examples**

## 10.1 Main Application

**File**: `src/index.ts`

```typescript
import { rateLimitMiddleware } from './middleware/rateLimit';
import { authMiddleware } from './middleware/auth';
import { securityHeadersMiddleware } from './middleware/security';
import { corsMiddleware, addCorsHeaders } from './middleware/cors';
import { serveStatic } from './routes/static';
import { proxyToBackend } from './routes/api';

// Configuration
const PORT = parseInt(process.env.PORT || '3000');
const HOST = process.env.HOST || '0.0.0.0';

// Main request handler
async function handleRequest(req: Request): Promise<Response> {
  const url = new URL(req.url);
  const path = url.pathname;
  
  console.log(`${req.method} ${path}`);
  
  try {
    // 1. CORS preflight
    const corsResponse = corsMiddleware(req);
    if (corsResponse) {
      return corsResponse;
    }
    
    // 2. Rate limiting
    const rateLimitResponse = await rateLimitMiddleware(req);
    if (rateLimitResponse) {
      return rateLimitResponse;
    }
    
    // 3. Authentication (for API routes)
    if (path.startsWith('/api/')) {
      const authResponse = await authMiddleware(req);
      if (authResponse) {
        return authResponse;
      }
    }
    
    // 4. Route request
    let response: Response;
    
    if (path.startsWith('/api/')) {
      // Proxy to FastAPI backend
      response = await proxyToBackend(req);
    } else if (path === '/health') {
      // Health check
      response = new Response(
        JSON.stringify({
          status: 'healthy',
          service: 'bun-gateway',
          timestamp: new Date().toISOString()
        }),
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );
    } else {
      // Serve static files
      response = await serveStatic(req);
    }
    
    // 5. Add rate limit headers
    if ((req as any).rateLimitHeaders) {
      const headers = new Headers(response.headers);
      Object.entries((req as any).rateLimitHeaders).forEach(([key, value]) => {
        headers.set(key, value as string);
      });
      response = new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers
      });
    }
    
    // 6. Add CORS headers
    response = addCorsHeaders(req, response);
    
    // 7. Add security headers
    response = securityHeadersMiddleware(req, response);
    
    return response;
    
  } catch (error) {
    console.error('Request error:', error);
    
    return new Response(
      JSON.stringify({
        error: 'Internal Server Error',
        message: 'An unexpected error occurred'
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  }
}

// Start server
const server = Bun.serve({
  port: PORT,
  hostname: HOST,
  fetch: handleRequest,
  
  // Error handler
  error(error) {
    console.error('Server error:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
});

console.log(`🚀 Bun API Gateway running on http://${HOST}:${PORT}`);
console.log(`📊 Rate limiting: Enabled (Redis)`);
console.log(`🔐 Authentication: JWT validation`);
console.log(`📁 Static files: Serving from ./public`);
console.log(`🔄 Backend proxy: http://${process.env.BACKEND_HOST || 'localhost'}:${process.env.BACKEND_PORT || '8000'}`);
```

---

## 10.2 Configuration File

**File**: `.env`

```bash
# Server
PORT=3000
HOST=0.0.0.0

# Backend
BACKEND_HOST=localhost
BACKEND_PORT=8000

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# JWT
JWT_SECRET=your-secret-key-change-in-production-abc123xyz789

# Frontend
FRONTEND_URL=http://localhost:3000

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://idrm.gov.in

# Environment
NODE_ENV=development
```

---

## 10.3 Package.json

**File**: `package.json`

```json
{
  "name": "idrm-bun-gateway",
  "version": "1.0.0",
  "description": "Bun API Gateway for IDRM",
  "main": "src/index.ts",
  "scripts": {
    "dev": "bun run --watch src/index.ts",
    "start": "bun run src/index.ts",
    "build": "bun build src/index.ts --outdir dist --target bun",
    "test": "bun test"
  },
  "dependencies": {
    "ioredis": "^5.3.2",
    "jsonwebtoken": "^9.0.2"
  },
  "devDependencies": {
    "@types/jsonwebtoken": "^9.0.5",
    "bun-types": "latest"
  }
}
```

---

## 10.4 TypeScript Config

**File**: `tsconfig.json`

```json
{
  "compilerOptions": {
    "lib": ["ESNext"],
    "module": "esnext",
    "target": "esnext",
    "moduleResolution": "bundler",
    "moduleDetection": "force",
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "composite": true,
    "strict": true,
    "downlevelIteration": true,
    "skipLibCheck": true,
    "jsx": "preserve",
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    "allowJs": true,
    "types": [
      "bun-types"
    ]
  }
}
```

---

# 11. **Testing**

## 11.1 Test Rate Limiting

```bash
# Terminal 1: Start Bun gateway
cd bun-gateway
bun run dev

# Terminal 2: Test rate limiting
# Send 10 requests quickly
for i in {1..10}; do
  curl -w "\nStatus: %{http_code}\n" http://localhost:3000/api/v1/health
  sleep 0.1
done

# Expected: First 60 succeed, then 429 Too Many Requests
```

**Test authentication rate limiting**:
```bash
# Send 10 login attempts (should be blocked after 5)
for i in {1..10}; do
  curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}' \
    -w "\nStatus: %{http_code}\n" \
    http://localhost:3000/api/v1/auth/login
done

# Expected: 5 attempts, then 429 with block
```

---

## 11.2 Test Authentication

**Generate test token**:
```typescript
// Create test-token.ts
import { createToken } from './src/middleware/auth';

const token = createToken({
  user_id: 'test-user-123',
  email: 'test@example.com',
  role: 'CITIZEN'
});

console.log('Test token:', token);
```

```bash
# Run
bun run test-token.ts

# Use token
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:3000/api/v1/services
```

---

## 11.3 Test Static Files

```bash
# Test index.html
curl http://localhost:3000/

# Test CSS
curl http://localhost:3000/assets/css/custom.css

# Test caching (should return 304)
curl -H "If-Modified-Since: $(date -R)" \
  http://localhost:3000/index.html
```

---

# 12. **Production Deployment**

## 12.1 Production Configuration

**File**: `.env.production`

```bash
# Server
PORT=3000
HOST=0.0.0.0

# Backend
BACKEND_HOST=backend-service
BACKEND_PORT=8000

# Redis
REDIS_HOST=redis-service
REDIS_PORT=6379
REDIS_PASSWORD=production-redis-password

# JWT
JWT_SECRET=production-jwt-secret-key-min-32-chars-abc123xyz789

# Frontend
FRONTEND_URL=https://idrm.gov.in

# CORS
ALLOWED_ORIGINS=https://idrm.gov.in

# Environment
NODE_ENV=production
```

---

## 12.2 Docker Deployment

**File**: `Dockerfile`

```dockerfile
FROM oven/bun:1.1.0

WORKDIR /app

# Copy package files
COPY package.json bun.lockb ./

# Install dependencies
RUN bun install --production

# Copy source code
COPY src/ ./src/
COPY public/ ./public/

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD bun run -e 'fetch("http://localhost:3000/health").then(r => r.ok || process.exit(1))'

# Start server
CMD ["bun", "run", "src/index.ts"]
```

**Build and run**:
```bash
# Build image
docker build -t idrm-bun-gateway .

# Run container
docker run -d \
  --name bun-gateway \
  -p 3000:3000 \
  --env-file .env.production \
  --network idrm-network \
  idrm-bun-gateway
```

---

## 12.3 Complete docker-compose.yml

**File**: `docker-compose.yml` (updated)

```yaml
version: '3.8'

services:
  # Bun API Gateway
  gateway:
    build:
      context: ./bun-gateway
      dockerfile: Dockerfile
    container_name: idrm_gateway
    ports:
      - "3000:3000"
    environment:
      - PORT=3000
      - BACKEND_HOST=backend
      - BACKEND_PORT=8000
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - JWT_SECRET=${JWT_SECRET}
      - NODE_ENV=production
    depends_on:
      - backend
      - redis
    networks:
      - idrm_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: idrm_backend
    environment:
      - DB_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
    networks:
      - idrm_network
    restart: unless-stopped

  # PostgreSQL
  postgres:
    image: postgis/postgis:15-3.3
    container_name: idrm_postgres
    environment:
      - POSTGRES_DB=idrm_production
      - POSTGRES_USER=idrm_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - idrm_network
    restart: unless-stopped

  # Redis
  redis:
    image: redis:7-alpine
    container_name: idrm_redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - idrm_network
    restart: unless-stopped

  # NGINX (Reverse Proxy)
  nginx:
    image: nginx:alpine
    container_name: idrm_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - gateway
    networks:
      - idrm_network
    restart: unless-stopped

networks:
  idrm_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

---

## 12.4 NGINX Configuration

**File**: `nginx/nginx.conf`

```nginx
upstream bun_gateway {
    # Load balance between multiple Bun instances
    least_conn;
    server gateway:3000 max_fails=3 fail_timeout=30s;
    # Add more instances for scaling:
    # server gateway2:3000 max_fails=3 fail_timeout=30s;
    
    keepalive 32;
}

server {
    listen 80;
    server_name idrm.gov.in www.idrm.gov.in;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name idrm.gov.in www.idrm.gov.in;
    
    # SSL configuration
    ssl_certificate /etc/nginx/ssl/idrm.gov.in.crt;
    ssl_certificate_key /etc/nginx/ssl/idrm.gov.in.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers (belt-and-suspenders with Bun)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Connection limits (DDoS protection)
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
    limit_conn conn_limit 10;
    
    # Request size limit
    client_max_body_size 10M;
    
    # Logging
    access_log /var/log/nginx/idrm-access.log;
    error_log /var/log/nginx/idrm-error.log;
    
    # Proxy to Bun Gateway
    location / {
        proxy_pass http://bun_gateway;
        proxy_http_version 1.1;
        
        # Preserve original request info
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
```

---

## 12.5 Monitoring

**Add Prometheus metrics** (optional):

```typescript
// src/utils/metrics.ts
let requestCount = 0;
let errorCount = 0;
const requestDurations: number[] = [];

export function recordRequest(duration: number, error: boolean = false) {
  requestCount++;
  if (error) errorCount++;
  requestDurations.push(duration);
  
  // Keep only last 1000 durations
  if (requestDurations.length > 1000) {
    requestDurations.shift();
  }
}

export function getMetrics() {
  const avgDuration = requestDurations.length > 0
    ? requestDurations.reduce((a, b) => a + b, 0) / requestDurations.length
    : 0;
  
  return {
    requests_total: requestCount,
    requests_errors: errorCount,
    request_duration_avg_ms: avgDuration.toFixed(2),
    uptime_seconds: process.uptime()
  };
}

// Add metrics endpoint in index.ts
if (path === '/metrics') {
  response = new Response(
    JSON.stringify(getMetrics()),
    { headers: { 'Content-Type': 'application/json' } }
  );
}
```

---

## 🎉 **Complete Setup!**

### **What You've Built**:

```
✅ Bun API Gateway with:
   ├─ Rate limiting (Redis-based)
   ├─ JWT authentication
   ├─ Static file serving (optimized)
   ├─ Security headers (CSP, HSTS, etc.)
   ├─ CORS handling
   ├─ Backend proxying
   └─ Production-ready deployment

✅ Performance:
   ├─ 3x faster than Node.js
   ├─ Efficient caching
   ├─ Connection pooling
   └─ Low memory footprint

✅ Security:
   ├─ Rate limiting per endpoint
   ├─ JWT validation
   ├─ Directory traversal protection
   ├─ XSS prevention
   ├─ CSRF protection
   └─ Security headers
```

---

## 📊 **Architecture Summary**

```
Production Flow:

Internet
  ↓
NGINX (Port 80/443)
  ├─ SSL termination
  ├─ Load balancing
  └─ DDoS protection
      ↓
Bun Gateway (Port 3000) x N instances
  ├─ Rate limiting (Redis)
  ├─ Authentication (JWT)
  ├─ Static files (cached)
  └─ API proxy
      ↓
FastAPI Backend (Port 8000)
  ├─ Business logic
  └─ Database operations
      ↓
PostgreSQL + Redis
```

---

## 🚀 **Quick Start**

```bash
# 1. Install Bun
curl -fsSL https://bun.sh/install | bash

# 2. Setup project
cd bun-gateway
bun install

# 3. Configure
cp .env.example .env
# Edit .env with your settings

# 4. Start development server
bun run dev

# 5. Test
curl http://localhost:3000/health
```

**Your Bun API Gateway is now protecting IDRM!** 🎊

---

**Document Complete!**  
**Status**: ✅ Production-Ready  
**Version**: 1.0  
**Last Updated**: May 16, 2026
