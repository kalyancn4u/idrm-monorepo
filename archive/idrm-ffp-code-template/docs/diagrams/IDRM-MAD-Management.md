# IDRM MAD Management
## Misuse, Abuse, and Discrepancy Detection & Response

**Type**: Flow + Class Diagram (created from LLD admin section)  
**Version**: 3.0  
**Purpose**: Shows how the system detects, escalates, and resolves misuse, abuse, and discrepancies

> 🔒 **Post-MVP — planned, not in the MVP.** The MAD (Misuse/Abuse/Discrepancy) module — including credibility scoring — is deferred to a later phase (it overlaps the Auditor credibility-scoring, also Post-MVP). Kept here for future reference; see `docs/development/IDRM-FS.md` for current MVP scope.

---

## MAD Management Flow

```mermaid
graph TD
    %% Trigger Sources
    UserReport([User Report])
    AutoDetect([Auto-Detection])
    AuditLog([Audit Log Anomaly])
    AdminFlag([Admin Manual Flag])

    %% Detection Layer
    MADAlerts[MAD Alerts Engine]
    CredibilityScore[Credibility Score Check]

    %% Assessment
    MADHandling[MAD Handling Module]
    ReVVView[ReVVView Assessment]
    EvidenceGather[Evidence Gathering]

    %% Decision Gate
    MADDecision{Outcome?}

    %% Outcomes
    MADWhitelists[Add to Whitelist]
    MADBlacklists[Add to Blacklist]
    RoleChange[Role Downgrade / Suspension]
    UserNotify[User Notification]
    AuditRecord[Audit Log Entry]
    Escalate[Escalate to DM Authority]

    %% Admin Management
    AdminDashboard[Admin Dashboard]
    AuditLogs[Audit Logs View]
    UserManagement[User Management]

    %% Flow
    UserReport --> MADAlerts
    AutoDetect --> MADAlerts
    AuditLog --> MADAlerts
    AdminFlag --> MADAlerts

    MADAlerts --> CredibilityScore
    CredibilityScore --> MADHandling

    MADHandling --> ReVVView
    MADHandling --> EvidenceGather
    ReVVView --> MADDecision
    EvidenceGather --> MADDecision

    MADDecision -->|Cleared| MADWhitelists
    MADDecision -->|Confirmed Abuse| MADBlacklists
    MADDecision -->|Partial Action| RoleChange
    MADDecision -->|Escalate| Escalate

    MADWhitelists --> UserNotify
    MADBlacklists --> UserNotify
    RoleChange --> UserNotify
    MADBlacklists --> AuditRecord
    MADWhitelists --> AuditRecord
    RoleChange --> AuditRecord

    AdminDashboard --> AuditLogs
    AdminDashboard --> UserManagement
    UserManagement --> RoleChange
    UserManagement --> MADBlacklists

    style MADAlerts fill:#fff3e0,stroke:#ff9800
    style MADBlacklists fill:#ffebee,stroke:#f44336
    style MADWhitelists fill:#e8f5e9,stroke:#4caf50
    style MADHandling fill:#e3f2fd,stroke:#2196f3
    style MADDecision fill:#f3e5f5,stroke:#9c27b0
```

---

## MAD Entity Classes

```mermaid
classDiagram
    class MADAlerts {
        +alert_id: UUID
        +user_id: UUID
        +alert_type: str
        +severity: str
        +source: str
        +created_at: datetime
        +generateAlert()
        +escalate()
    }

    class MADHandling {
        +case_id: UUID
        +alert_id: UUID
        +handler_id: UUID
        +status: str
        +resolution: str
        +handleCase()
        +resolveCase()
        +escalateToAuthority()
    }

    class MADBlacklists {
        +entry_id: UUID
        +user_id: UUID
        +reason: str
        +blacklisted_by: UUID
        +blacklisted_at: datetime
        +expires_at: datetime
        +addToBlacklist()
        +removeFromBlacklist()
        +isBlacklisted()
    }

    class MADWhitelists {
        +entry_id: UUID
        +user_id: UUID
        +approved_by: UUID
        +approved_at: datetime
        +addToWhitelist()
        +removeFromWhitelist()
        +isWhitelisted()
    }

    class CredibilityScore {
        +user_id: UUID
        +score: float
        +factors: dict
        +last_updated: datetime
        +calculateScore()
        +updateScore()
        +getHistoricalTrend()
    }

    class AuditLog {
        +log_id: UUID
        +user_id: UUID
        +action: str
        +resource_type: str
        +resource_id: UUID
        +timestamp: datetime
        +ip_address: str
        +logAction()
    }

    MADAlerts --> MADHandling
    MADHandling --> MADBlacklists
    MADHandling --> MADWhitelists
    CredibilityScore --> MADAlerts
    MADBlacklists --> AuditLog
    MADWhitelists --> AuditLog
```

---

## Admin API Operations

| Operation | Endpoint | Authorization | Effect |
|-----------|----------|--------------|--------|
| List users | `GET /api/v1/admin/users` | ADMIN | View all users with filters |
| Deactivate user | `PATCH /api/v1/admin/users/{id}` | ADMIN | `is_active: false` |
| Change role | `PATCH /api/v1/admin/users/{id}` | ADMIN | Downgrade/upgrade role |
| View audit logs | `GET /api/v1/admin/audit-logs` | ADMIN or DM_AUTHORITY | Full action history |

## Blacklisting via Redis

Token invalidation on blacklist action:
```python
# Blacklist active JWT token immediately
redis_client.setex(
    f"blacklist:{token_jti}",
    settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    "1"
)
```

## Credibility Scoring Factors

| Factor | Impact | Weight |
|--------|--------|--------|
| Successful services fulfilled | Positive | High |
| Service cancellation rate | Negative | Medium |
| Community reports against user | Negative | High |
| Verification status | Positive | Medium |
| Historical audit flag count | Negative | High |

## Alert Severity Levels

| Severity | Trigger | Default Action |
|----------|---------|---------------|
| INFO | Minor anomaly detected | Log only |
| WARNING | Pattern of suspicious activity | Review queue |
| HIGH | Active misuse confirmed | Suspend + notify admin |
| CRITICAL | Fraudulent activity | Immediate blacklist + DM Authority escalation |
