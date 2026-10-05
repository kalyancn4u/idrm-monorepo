# IDRM Session Management
## Authentication Flow and Session Lifecycle

**Type**: Flow + Class Diagram (created from HLD auth/session section)  
**Version**: 3.0  
**Purpose**: Shows how user sessions are created, stored, validated, and terminated across all three platforms

---

## Session Lifecycle Flow

```mermaid
graph TD
    %% Entry points
    WebLogin(["Web Login<br/>HTML/Tailwind"])
    SPALogin(["SPA Login<br/>React Admin"])
    MobileLogin(["Mobile Login<br/>React Native"])

    %% Auth Layer
    AuthEndpoint[POST /api/v1/auth/login]
    VerifyCredentials["Verify Credentials<br/>bcrypt cost=12"]
    GenerateTokens[Generate JWT Tokens]

    %% Token pair
    AccessToken["Access Token<br/>15 min TTL"]
    RefreshToken["Refresh Token<br/>7 day TTL"]

    %% Storage
    RedisSession[("Redis<br/>session:user_id<br/>7 day TTL")]
    ClientStorage[("Client Storage<br/>httpOnly cookie / AsyncStorage")]

    %% Request flow
    APIRequest[API Request with Bearer Token]
    GatewayValidate["Bun Gateway<br/>JWT Validation"]
    BlacklistCheck["Redis Blacklist Check<br/>blacklist:jti"]
    TokenExpired{"Access Token<br/>Expired?"}
    BackendProcess["FastAPI Backend<br/>Process Request"]

    %% Token refresh
    RefreshEndpoint[POST /api/v1/auth/refresh]
    NewAccessToken[New Access Token]

    %% Logout / termination
    LogoutRequest[POST /api/v1/auth/logout]
    BlacklistToken[Blacklist JTI in Redis]
    InvalidateSession[Remove from Redis]
    ClearClient[Clear Client Storage]

    %% Flow
    WebLogin --> AuthEndpoint
    SPALogin --> AuthEndpoint
    MobileLogin --> AuthEndpoint

    AuthEndpoint --> VerifyCredentials
    VerifyCredentials -->|Success| GenerateTokens
    VerifyCredentials -->|Failure| AuthEndpoint

    GenerateTokens --> AccessToken
    GenerateTokens --> RefreshToken

    AccessToken --> ClientStorage
    RefreshToken --> ClientStorage
    GenerateTokens --> RedisSession

    ClientStorage --> APIRequest
    APIRequest --> GatewayValidate
    GatewayValidate --> BlacklistCheck
    BlacklistCheck -->|Blacklisted| AuthEndpoint
    BlacklistCheck -->|Not blacklisted| TokenExpired
    TokenExpired -->|Yes - expired| RefreshEndpoint
    TokenExpired -->|No - valid| BackendProcess
    RefreshEndpoint --> NewAccessToken
    NewAccessToken --> APIRequest

    LogoutRequest --> BlacklistToken
    LogoutRequest --> InvalidateSession
    LogoutRequest --> ClearClient

    style AuthEndpoint fill:#e3f2fd,stroke:#2196f3
    style GatewayValidate fill:#e8f5e9,stroke:#4caf50
    style BlacklistCheck fill:#fff3e0,stroke:#ff9800
    style TokenExpired fill:#fff8e1,stroke:#ffc107
    style RedisSession fill:#f3e5f5,stroke:#9c27b0
    style LogoutRequest fill:#ffebee,stroke:#f44336
```

---

## Session Entity Classes

```mermaid
classDiagram
    class DrmSession {
        +session_id: UUID
        +user_id: UUID
        +access_token_jti: str
        +refresh_token_jti: str
        +created_at: datetime
        +expires_at: datetime
        +ip_address: str
        +user_agent: str
        +platform: str
        +createSession()
        +validateSession()
        +refreshSession()
        +terminateSession()
    }

    class SessionMgmt {
        +storeSession(session)
        +getSession(user_id)
        +invalidateSession(user_id)
        +listActiveSessions(user_id)
        +terminateAllSessions(user_id)
    }

    class CookieMgmt {
        +cookie_name: str
        +http_only: bool
        +secure: bool
        +same_site: str
        +setCookie(response, token)
        +getCookie(request)
        +clearCookie(response)
    }

    class SessionMapping {
        +user_id: UUID
        +sessions: list
        +mapUserToSession()
        +getActiveSessionCount()
        +enforceMaxSessions()
    }

    class Blacklisting {
        +jti: str
        +blacklisted_at: datetime
        +expires_at: datetime
        +addToBlacklist(jti, ttl)
        +isBlacklisted(jti)
        +cleanExpiredEntries()
    }

    class SessionSuspend {
        +user_id: UUID
        +suspended_by: UUID
        +reason: str
        +suspendedAt: datetime
        +suspendUser()
        +reinstateUser()
        +isSuspended()
    }

    DrmSession --> SessionMgmt
    DrmSession --> CookieMgmt
    SessionMgmt --> SessionMapping
    SessionMgmt --> Blacklisting
    SessionSuspend --> Blacklisting
```

---

## Redis Key Patterns

| Key Pattern | Value | TTL | Purpose |
|-------------|-------|-----|---------|
| `session:{user_id}` | JWT payload + metadata | 7 days | Active session store |
| `blacklist:{jti}` | `"1"` | Access token TTL | Invalidated token registry |
| `rate_limit:{endpoint}:{ip}` | Request count | 60 seconds | Rate limiting per IP |
| `realtime:{service_id}` | Status JSON | 5 minutes | Real-time pub/sub state |

## Client-Side Storage by Platform

| Platform | Storage Method | Token Location |
|----------|---------------|----------------|
| HTML/Tailwind | httpOnly cookie | Set-Cookie header (Bun gateway) |
| React SPA | httpOnly cookie | Set-Cookie header (Bun gateway) |
| React Native | AsyncStorage | Stored securely on device |

## Token Specifications

| Token | Algorithm | TTL | Stored In |
|-------|----------|-----|----------|
| Access Token | HS256 (JWT) | 15 minutes | httpOnly cookie / AsyncStorage |
| Refresh Token | HS256 (JWT) | 7 days | httpOnly cookie / AsyncStorage |
| Session Record | — | 7 days | Redis `session:{user_id}` |

## Session Security Properties

- **httpOnly**: Cookie inaccessible to JavaScript (prevents XSS token theft)
- **SameSite=Lax**: Blocks CSRF from cross-site POSTs
- **Secure**: Cookie sent only over HTTPS (enforced in staging/production)
- **bcrypt cost=12**: Password hash rounds — balances security and login latency
- **JWT blacklist**: Immediate invalidation on logout or suspension (Redis TTL mirrors token expiry)

## Multi-Session Behavior

A user can have concurrent sessions from different platforms (web, admin, mobile). Each session has its own JTI pair. Logout from one platform only blacklists that session's tokens, leaving other platform sessions intact. Admin suspension via `SessionSuspend` terminates all active sessions for a user.
