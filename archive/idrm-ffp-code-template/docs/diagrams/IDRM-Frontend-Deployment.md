# IDRM Three-Frontend Deployment Diagram
## v3 — Platform-by-Platform Build & Runtime

**Source**: IDRM-DEPLOYMENT-GUIDE.md · IDRM-DEVELOPMENT-GUIDE.md  
**Type**: Deployment Diagram  
**Version**: 3.0  
**Purpose**: Shows how each of the three frontend platforms is built, served, and deployed across Development, Staging, and Production environments

---

```mermaid
flowchart LR
    subgraph SRC["Source Code  —  src/frontend/"]
        WH["web-html/<br/>HTML · Tailwind · Vanilla JS<br/>Citizens (fast, low-connectivity)"]
        WR["web-react/<br/>React 18 · TypeScript · Vite<br/>Admins & Coordinators"]
        ME["mobile-expo/<br/>React Native · Expo SDK<br/>Field Workers (iOS + Android)"]
    end

    subgraph DEV["Development  —  Local Terminals"]
        D1["Terminal 3<br/>bun run dev<br/>Port 5173<br/>Vite HMR"]
        D2["Terminal 4<br/>bun run dev<br/>Port 5174<br/>Vite HMR"]
        D3["Terminal 5<br/>npx expo start<br/>Expo Dev Client<br/>LAN / Tunnel"]
    end

    subgraph BUILD["Build Step  —  CI/CD"]
        B1["bun run build<br/>→ dist/ (static HTML/CSS/JS)"]
        B2["bun run build<br/>→ dist/ (SPA bundle)"]
        B3["eas build<br/>→ .apk / .ipa"]
    end

    subgraph STAG["Staging  —  Docker Compose"]
        S1["frontend-web container<br/>NGINX :5173→:80<br/>staging.idrm.gov.in"]
        S2["frontend-admin container<br/>NGINX :5174→:80<br/>admin.staging.idrm.gov.in"]
        S3["Expo Go / TestFlight<br/>Internal testers only"]
    end

    subgraph PROD["Production  —  Docker + NGINX"]
        P1["NGINX replicas ×2<br/>idrm.gov.in<br/>HTTPS · gzip · cache headers"]
        P2["NGINX replicas ×2<br/>admin.idrm.gov.in<br/>HTTPS · CSP headers"]
        P3["App Store (iOS)<br/>Google Play (Android)<br/>via Expo EAS Submit"]
    end

    WH --> D1
    WR --> D2
    ME --> D3

    WH --> B1
    WR --> B2
    ME --> B3

    B1 --> S1
    B2 --> S2
    B3 --> S3

    S1 --> P1
    S2 --> P2
    S3 --> P3

    style WH fill:#e3f2fd,stroke:#2196f3
    style WR fill:#e3f2fd,stroke:#2196f3
    style ME fill:#e3f2fd,stroke:#2196f3
    style D1 fill:#fff9c4,stroke:#f9a825
    style D2 fill:#fff9c4,stroke:#f9a825
    style D3 fill:#fff9c4,stroke:#f9a825
    style B1 fill:#f3e5f5,stroke:#9c27b0
    style B2 fill:#f3e5f5,stroke:#9c27b0
    style B3 fill:#f3e5f5,stroke:#9c27b0
    style S1 fill:#fce4ec,stroke:#e91e63
    style S2 fill:#fce4ec,stroke:#e91e63
    style S3 fill:#fce4ec,stroke:#e91e63
    style P1 fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style P2 fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style P3 fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
```

---

## Platform Comparison

| Attribute | HTML/Tailwind (`web-html`) | React SPA (`web-react`) | React Native (`mobile-expo`) |
|-----------|--------------------------|------------------------|------------------------------|
| **Primary users** | Citizens in crisis | Admins · Coordinators | Field workers |
| **Dev command** | `bun run dev` | `bun run dev` | `npx expo start` |
| **Dev port** | 5173 | 5174 | Expo auto (LAN) |
| **Build tool** | Vite | Vite | Expo EAS / Metro |
| **Build output** | `dist/` (static files) | `dist/` (SPA bundle) | `.apk` / `.ipa` |
| **Production server** | NGINX in Docker | NGINX in Docker | App stores (EAS Submit) |
| **Offline support** | Graceful degradation | Partial | Full (offline-first) |
| **JavaScript runtime** | Vanilla (no framework) | React 18 + TypeScript | React Native (Hermes) |

---

## Startup Commands — Quick Reference

```bash
# HTML/Tailwind (Citizens)
cd src/frontend/web-html
bun run dev           # → http://localhost:5173

# React SPA (Admins)
cd src/frontend/web-react
bun run dev           # → http://localhost:5174

# React Native (Field Workers)
cd src/frontend/mobile-expo
bun install           # first time only
npx expo start        # → scan QR with Expo Go app
```

---

## Dockerfile Summary

### `web-html` & `web-react` — Multi-Stage NGINX Build

```
Stage 1 (builder): oven/bun:latest
  └─ bun install --frozen-lockfile
  └─ bun run build → dist/

Stage 2 (runtime): nginx:alpine
  └─ COPY dist/ → /usr/share/nginx/html
  └─ EXPOSE 80 443
```

### `mobile-expo` — No Dockerfile (Managed by EAS)

```
Local dev  → Expo Go app (scan QR code)
Staging    → Internal Distribution (TestFlight / APK direct)
Production → eas build + eas submit → App Stores
```

---

## NGINX Routing (Staging & Production)

```
https://idrm.gov.in
  └─ /          → frontend-web container (HTML/Tailwind)
  └─ /api/*     → api-gateway:3000 (proxied)
  └─ /ws        → api-gateway:3001 (WebSocket upgrade)

https://admin.idrm.gov.in
  └─ /          → frontend-admin container (React SPA)
  └─ /api/*     → api-gateway:3000 (proxied)
```

---

> **Why three frontends?** Each platform serves a distinct audience with fundamentally different capability requirements. HTML/Tailwind prioritises minimal payload and reliability in low-connectivity disaster zones. The React SPA delivers rich dashboard features (charts, data tables, real-time maps) for admin work. The mobile app provides GPS access, push notifications, and offline-first operation for field workers — none of which can be adequately served by a single approach.
