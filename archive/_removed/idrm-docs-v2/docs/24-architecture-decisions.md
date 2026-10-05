> *Type: Document (specification) · Audience: Architects, reviewers · Status: Archived — v2 historical generation*

# IDRM MVP: Architecture Decisions & Upgrade Paths
<!-- IDRM-CLEANUP doc=v2-24-decisions status=ANNOTATED pass=2026-08-16 -->
> ## 🗺️ SECTION MAP (annotation pass, 2026-08-16)
> Gen-2 architecture decisions — prefigure the current ADRs. **Current ADRs = `docs/mvp/21` (14 ADRs)**; FFP ADRs
> = `docs/ffp/21`. *Legend:* ✅ covered · ⚠ nuanced · ⊘ FFP.
>
> | Snippet | Section | → Addressed in | Phase | Verdict |
> |---|---|---|---|---|
> | `v2-24§dr` | Decision Record | `docs/mvp/21` (ADR-001…014) | MVP | ✅ |
> | `v2-24§perf` | Performance Targets | `docs/mvp/10` §9 (NFRs) | MVP | ⚠ |
> | `v2-24§scale` | Scalability Roadmap · Deployment Evolution | `docs/ffp/11` + `docs/ffp/80` | FFP | ✅ (as FFP) |
> | `v2-24§test` | Testing Strategy Evolution | `docs/mvp/70` → `docs/ffp/70` | MVP/FFP | ✅ |
> | `v2-24§mig` | Migration Checklist Templates | Strangler Fig → `docs/ffp/20` | FFP | ⊘ (MVP) |
>
> *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

## Technical Design Rationale

> **Purpose**: Document key architectural decisions, trade-offs, and clear paths for future enhancement.

---

## Executive Summary

The IDRM MVP implements a **pragmatic monolith-first approach** optimized for solo development, with a clear upgrade path to the full distributed architecture outlined in the original PRD.

**Key Philosophy**: Ship working software fast, then scale based on real usage.

---

## Decision Record

### DR-001: Python-Only Backend (FastAPI)

**Status**: ✅ Decided for MVP

**Context**:
- Original PRD proposed Node.js (API Gateway) + Python (Services)
- Solo developer strongest in Python
- Need to ship MVP quickly

**Decision**: Use FastAPI for all backend services initially

**Rationale**:
- **Developer Efficiency**: One language = less context switching
- **FastAPI is Async**: Handles high concurrency like Node.js
- **Rich Ecosystem**: Excellent libraries for geospatial, data science
- **Type Safety**: Pydantic models catch errors early
- **Auto Documentation**: OpenAPI/Swagger built-in

**Trade-offs**:
- ❌ Less optimal for pure WebSocket scenarios (but adequate for MVP)
- ❌ Slightly higher memory usage per request vs Node.js
- ✅ Faster development time (critical for solo MVP)
- ✅ Single deployment pipeline
- ✅ Easier debugging

**Upgrade Path** (Post-MVP):
```
Phase 1 (MVP): FastAPI Monolith
    ↓
Phase 2: FastAPI Monolith + Node.js WebSocket Service (if needed)
    ↓
Phase 3: Split into FastAPI Microservices (Service Manager, Analytics, etc.)
    ↓
Phase 4: Add Node.js API Gateway if traffic demands
```

**When to Upgrade**:
- WebSocket requirements become critical (> 10k simultaneous connections)
- Need specialized Node.js libraries
- Team grows to include Node.js specialists

---

### DR-002: Monolith First, Microservices Later

**Status**: ✅ Decided for MVP

**Context**:
- Original PRD shows microservices architecture
- Solo developer needs simple deployment
- Unknown usage patterns

**Decision**: Build as a well-structured monolith with clear module boundaries

**Rationale**:
- **Simplicity**: Single codebase, single deployment
- **Speed**: Faster iteration without network overhead
- **Debugging**: Easier to trace issues
- **Refactoring**: Can extract services later using same interfaces

**Architecture**:
```
backend/
├── app/
│   ├── api/v1/           # API endpoints (future service boundaries)
│   │   ├── auth.py       → Future: Auth Service
│   │   ├── services.py   → Future: Service Manager Service
│   │   ├── analytics.py  → Future: Analytics Service
│   │   └── geo.py        → Future: Geospatial Service
│   ├── core/             # Shared utilities
│   ├── db/               # Database layer
│   ├── models/           # ORM models
│   ├── schemas/          # Pydantic schemas (API contracts)
│   └── services/         # Business logic (service layer)
```

**Module Design Principles**:
1. **Clear Boundaries**: Each API module is self-contained
2. **Dependency Injection**: Easy to mock for testing
3. **Interface Contracts**: Schemas define service APIs
4. **Stateless Logic**: No shared mutable state

**Upgrade Path**:
```python
# Current (Monolith):
from app.services.service_manager import ServiceManager
result = await ServiceManager.create_service(...)

# Future (Microservice):
# Just change implementation, API contract stays same
from app.clients.service_manager_client import ServiceManagerClient
result = await ServiceManagerClient.create_service(...)
```

**Extraction Checklist** (when ready to split):
1. Module has clear API boundary ✓
2. Heavy computational load or distinct scaling needs
3. Team size justifies operational overhead
4. Monitoring shows bottleneck

**When to Upgrade**:
- Single service causes CPU/memory bottleneck
- Need independent scaling (e.g., analytics heavy)
- Team grows to 5+ developers
- Clear ownership boundaries needed

---

### DR-003: PostgreSQL Sessions Instead of Redis

**Status**: ✅ Decided for MVP

**Context**:
- Original PRD uses Redis for sessions and caching
- Adds deployment complexity
- Solo developer managing multiple services

**Decision**: Use PostgreSQL for session management, defer Redis

**Rationale**:
- **Simplicity**: One less service to manage
- **ACID Guarantees**: Session data is transactional
- **Sufficient Performance**: JWT tokens reduce session lookups
- **Easy Migration**: Can add Redis later without API changes

**Implementation**:
```python
# Session stored in database (MVP)
class Session(Base):
    session_id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey('users.user_id'))
    token_jti = Column(String)  # JWT ID for blacklisting
    expires_at = Column(DateTime)
    created_at = Column(DateTime)

# JWT-based authentication minimizes session lookups
# Only query database on:
# - Login (create session)
# - Logout (blacklist token)
# - Token validation (check if blacklisted)
```

**Performance Optimization** (without Redis):
```sql
-- Index for fast blacklist checks
CREATE INDEX idx_sessions_token_jti ON sessions(token_jti);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at) 
    WHERE expires_at > CURRENT_TIMESTAMP;

-- Periodic cleanup of expired sessions
DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP;
```

**Upgrade Path**:
```
Phase 1 (MVP): PostgreSQL sessions
    ↓
Phase 2: Add Redis for hot session cache (read-through pattern)
    ↓
Phase 3: Add Redis for rate limiting
    ↓
Phase 4: Add Redis pub/sub for real-time features
```

**When to Upgrade**:
- Session queries become performance bottleneck (> 50ms p95)
- Need real-time pub/sub for WebSockets
- Rate limiting needs sub-millisecond performance
- Analytics need fast temporary data store

**Migration Complexity**: LOW (transparent to API clients)

---

### DR-004: Direct PostGIS Instead of GeoServer

**Status**: ✅ Decided for MVP

**Context**:
- Original PRD uses GeoServer for WMS/WFS
- Adds significant complexity
- MVP needs simple map rendering

**Decision**: Serve GeoJSON directly from PostGIS via FastAPI

**Rationale**:
- **Simplicity**: No separate map server to configure
- **Direct Control**: Custom API endpoints for exact needs
- **Performance**: Fewer hops (client → API → database)
- **Modern Web**: Leaflet consumes GeoJSON natively

**Implementation**:
```python
@router.get("/services/map", response_class=GeoJSONResponse)
async def get_services_geojson(
    bounds: Optional[str] = None,
    service_type: Optional[ServiceType] = None,
    db: AsyncSession = Depends(get_db)
):
    """Return services as GeoJSON for map display"""
    query = select(
        ServiceRequest.service_id,
        ServiceRequest.service_type,
        ServiceRequest.priority,
        ServiceRequest.status,
        func.ST_AsGeoJSON(ServiceRequest.location).label('geometry')
    )
    
    if bounds:
        # Parse bounding box: "min_lng,min_lat,max_lng,max_lat"
        bbox = [float(x) for x in bounds.split(',')]
        bbox_polygon = func.ST_MakeEnvelope(*bbox, 4326)
        query = query.where(
            func.ST_Within(ServiceRequest.location, bbox_polygon)
        )
    
    if service_type:
        query = query.where(ServiceRequest.service_type == service_type)
    
    results = await db.execute(query)
    
    # Convert to GeoJSON
    features = []
    for row in results:
        features.append({
            "type": "Feature",
            "geometry": json.loads(row.geometry),
            "properties": {
                "service_id": str(row.service_id),
                "service_type": row.service_type,
                "priority": row.priority,
                "status": row.status
            }
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }
```

**Frontend (Leaflet)**:
```javascript
// Fetch and display GeoJSON
async function loadServices() {
    const response = await fetch('/api/v1/services/map?bounds=' + map.getBounds().toBBoxString());
    const geojson = await response.json();
    
    L.geoJSON(geojson, {
        pointToLayer: (feature, latlng) => {
            return L.circleMarker(latlng, {
                radius: 8,
                fillColor: getColorByType(feature.properties.service_type),
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            });
        },
        onEachFeature: (feature, layer) => {
            layer.bindPopup(createPopupContent(feature.properties));
        }
    }).addTo(map);
}
```

**Trade-offs**:
- ❌ No standard WMS protocol (but not needed for MVP)
- ❌ No advanced cartographic styling (SLD)
- ✅ Full API control and flexibility
- ✅ Easier debugging (standard HTTP JSON)
- ✅ Custom business logic in responses

**Upgrade Path**:
```
Phase 1 (MVP): Direct GeoJSON from PostGIS
    ↓
Phase 2: Add tile caching with Nginx
    ↓
Phase 3: Add GeoServer for standard OGC services (if needed)
    ↓
Phase 4: Vector tiles for better performance (optional)
```

**When to Upgrade**:
- Need standard WMS/WFS for GIS tool integration
- Complex cartographic requirements
- Serving very large datasets (> 1M points)
- Third-party integrations require OGC standards

**Migration Impact**: LOW (GeoJSON endpoint stays, add GeoServer alongside)

---

### DR-005: Email Notifications Only (No WebSockets)

**Status**: ✅ Decided for MVP

**Context**:
- Original PRD includes Socket.io for real-time updates
- Adds significant complexity
- MVP has low concurrent user count

**Decision**: Use email notifications only, defer real-time updates

**Rationale**:
- **Simplicity**: No persistent connection management
- **Reliability**: Email guaranteed delivery (via queue retry)
- **Universal**: Works for all users (no app open requirement)
- **Sufficient**: Disaster response has minutes-scale urgency, not seconds

**Implementation**:
```python
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# Email configuration
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_TLS=True,
    MAIL_SSL=False
)

async def send_notification(
    to_email: str,
    subject: str,
    template: str,
    context: dict
):
    """Send email notification"""
    message = MessageSchema(
        subject=subject,
        recipients=[to_email],
        template_body=context,
        subtype="html"
    )
    
    fm = FastMail(mail_config)
    await fm.send_message(message, template_name=template)

# Usage
await send_notification(
    to_email=provider.email,
    subject="New Service Request Assigned",
    template="service_assigned.html",
    context={
        "provider_name": provider.full_name,
        "service_type": service.service_type,
        "location": service.address
    }
)
```

**Notification Triggers**:
- Service request created → Authority notified
- Service approved → Requestor notified
- Service assigned → Provider notified
- Service completed → Requestor notified
- Status changed → Relevant parties notified

**Upgrade Path**:
```
Phase 1 (MVP): Email only
    ↓
Phase 2: Add in-app notification center (database-backed)
    ↓
Phase 3: Add WebSocket for real-time updates
    ↓
Phase 4: Add push notifications (mobile)
```

**When to Upgrade**:
- User feedback demands real-time updates
- Response time requirements drop to < 60 seconds
- Mobile app requires instant updates
- High concurrent user count (> 1000 simultaneous)

**Migration Impact**: LOW (add alongside email, don't replace)

---

### DR-006: Simple JWT Auth (No OAuth Initially)

**Status**: ✅ Decided for MVP

**Context**:
- Original PRD mentions OAuth 2.0 capability
- Adds complexity for solo developer
- MVP has limited user base

**Decision**: Implement simple JWT-based authentication

**Rationale**:
- **Simplicity**: No third-party integration
- **Control**: Full control over auth flow
- **Sufficient**: Adequate for internal users
- **Standard**: Easy to add OAuth later

**Implementation**:
```python
# Simple JWT tokens
access_token = create_access_token(
    data={
        "sub": str(user.user_id),
        "role": user.role.value,
        "email": user.email
    },
    expires_delta=timedelta(minutes=30)
)

# Dependency for protected routes
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await UserService.get_user_by_id(db, UUID(user_id))
    if user is None:
        raise credentials_exception
    
    return user
```

**Security Measures**:
- Bcrypt password hashing (cost 12)
- Short-lived tokens (30 minutes)
- Token blacklist on logout
- HTTPS only in production
- Rate limiting on login

**Upgrade Path**:
```
Phase 1 (MVP): Simple JWT
    ↓
Phase 2: Add OAuth 2.0 (Google, GitHub)
    ↓
Phase 3: Add SAML for enterprise SSO
    ↓
Phase 4: Add MFA (TOTP, SMS)
```

**When to Upgrade**:
- Need single sign-on (SSO)
- External users require OAuth
- Security audit recommends MFA
- Enterprise deployment needs SAML

---

## Performance Targets

### MVP Performance Benchmarks

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response (simple) | < 200ms | P95 latency |
| API Response (spatial) | < 500ms | P95 latency |
| Map load time | < 2s | Time to interactive |
| Database queries | < 100ms | P95 query time |
| Concurrent users | 100+ | Load test |
| Database records | 100,000+ | Service requests |

### Optimization Strategies

**Database**:
- Spatial indexes (GIST)
- Connection pooling
- Query optimization (EXPLAIN ANALYZE)
- Materialized views for analytics

**API**:
- Response pagination
- Field filtering (sparse fieldsets)
- Compression (gzip)
- HTTP caching headers

**Frontend**:
- Map marker clustering
- Lazy loading
- Asset compression
- CDN for static files

---

## Scalability Roadmap

### Vertical Scaling (Month 1-6)

**Single Server Optimization**:
- Optimize database queries
- Add database indexes
- Implement caching
- Tune connection pools
- Add compression

**Expected Capacity**:
- 500 concurrent users
- 5,000 requests/minute
- 1M+ database records

### Horizontal Scaling (Month 7-12)

**Add Services**:
- Load balancer (Nginx)
- Redis cache
- Read replicas (PostgreSQL)
- File storage (S3/MinIO)

**Expected Capacity**:
- 2,000+ concurrent users
- 20,000 requests/minute
- 10M+ database records

### Distributed Architecture (Month 13+)

**Microservices**:
- Extract services by domain
- Message queue (RabbitMQ/Kafka)
- Service mesh (optional)
- Multiple database instances

**Expected Capacity**:
- 10,000+ concurrent users
- 100,000+ requests/minute
- 100M+ database records

---

## Testing Strategy Evolution

### Phase 1 (MVP): Manual + Basic Automation

**Coverage**:
- Manual testing of critical paths
- Unit tests for business logic (70%+ coverage)
- Basic integration tests
- Postman/curl for API testing

### Phase 2: Comprehensive Automation

**Coverage**:
- Full unit test suite (80%+ coverage)
- Integration test suite
- End-to-end tests (Playwright/Selenium)
- Load testing (Locust/k6)
- Security scanning

### Phase 3: Continuous Testing

**Coverage**:
- CI/CD pipeline with automated tests
- Staging environment
- Canary deployments
- Production monitoring
- Automated rollback

---

## Deployment Evolution

### Phase 1 (MVP): Single Server Docker Compose

**Infrastructure**:
```
Single Ubuntu Server
├── Docker Compose
│   ├── PostgreSQL + PostGIS
│   ├── FastAPI
│   └── Nginx
└── Manual deployment
```

**Pros**: Simple, low cost, fast deployment
**Cons**: No redundancy, manual scaling

### Phase 2: Cloud Deployment with Managed Services

**Infrastructure**:
```
Cloud Provider (AWS/GCP/Azure)
├── Managed Database (RDS/CloudSQL)
├── Container Service (ECS/Cloud Run)
├── Load Balancer
├── Managed Redis
└── CI/CD Pipeline (GitHub Actions)
```

**Pros**: Managed backups, auto-scaling, high availability
**Cons**: Higher cost, vendor lock-in

### Phase 3: Kubernetes Orchestration

**Infrastructure**:
```
Kubernetes Cluster
├── Multiple Nodes
├── Auto-scaling
├── Service Mesh
├── Monitoring Stack (Prometheus/Grafana)
└── GitOps Deployment (ArgoCD)
```

**Pros**: Multi-cloud, advanced orchestration, enterprise-ready
**Cons**: Complex operations, requires expertise

---

## Migration Checklist Templates

### When Splitting a Service

- [ ] Service has clear API boundary
- [ ] Interface contract defined (Pydantic schemas)
- [ ] All dependencies identified
- [ ] Database migration strategy
- [ ] Monitoring/logging configured
- [ ] Load testing completed
- [ ] Rollback plan documented
- [ ] Team trained on new service

### When Adding Real-Time Features

- [ ] Assess user demand (usage analytics)
- [ ] Design WebSocket protocol
- [ ] Implement connection pooling
- [ ] Add reconnection logic
- [ ] Test with load
- [ ] Monitor connection count
- [ ] Plan for horizontal scaling
- [ ] Document client integration

### When Moving to Cloud

- [ ] Evaluate cloud providers
- [ ] Cost analysis
- [ ] Data export/import tested
- [ ] Environment parity (dev/staging/prod)
- [ ] Secrets management (Vault/KMS)
- [ ] Backup/restore tested
- [ ] Disaster recovery plan
- [ ] Team training completed

---

## Conclusion

These architecture decisions optimize for:

1. **Solo Developer Success**: Simple, manageable, shippable
2. **Clear Upgrade Paths**: Well-defined migration steps
3. **Production Readiness**: Robust foundation
4. **Community Contributions**: Clean boundaries, good documentation

**Remember**: The best architecture is the one that ships. Perfect is the enemy of done. Build, learn, iterate.

---

## Change Log

| Date | Decision | Status |
|------|----------|--------|
| 2024-12 | DR-001: Python-only backend | ✅ Active |
| 2024-12 | DR-002: Monolith first | ✅ Active |
| 2024-12 | DR-003: PostgreSQL sessions | ✅ Active |
| 2024-12 | DR-004: Direct PostGIS | ✅ Active |
| 2024-12 | DR-005: Email notifications | ✅ Active |
| 2024-12 | DR-006: Simple JWT | ✅ Active |

---

*This document will be updated as architectural decisions evolve.*
