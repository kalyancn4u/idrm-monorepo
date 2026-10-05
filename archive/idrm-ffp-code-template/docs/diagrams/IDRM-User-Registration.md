# IDRM User Registration Use Case
## Registration and Authentication Use Cases by Role

**Source**: DRM_Registration.png (re-modelled to the v3 canonical role set)  
**Type**: Use Case Diagram  
**Version**: 3.0 (reconciled 2026-05-30)  
**Purpose**: Registration and authentication capabilities per role. Canonical roles: [`docs/development/IDRM-FS.md`](../development/IDRM-FS.md) §3.3.

---

```mermaid
graph TB
    Public((Public / Prospective))
    Citizen((Citizen))
    Provider((Service Provider))
    Volunteer((Volunteer))
    Admin((System Admin))

    subgraph IDRM["IDRM Registration & Auth"]
        Register[Register: email + password]
        QuickStart[Quick-start: phone + OTP]
        VerifyEmail[Verify Email]
        Login[Login / Logout]
        Reset[Reset Password]
        ManageProfile[Manage Profile]
        Preferences[Set Preferences: language, notifications]
        GrantRole[Grant / Assign Elevated Role]
        AccessControl[Whitelist / Blacklist]
    end

    Public --> Register
    Public --> QuickStart
    Register --> VerifyEmail

    Citizen --> Login
    Citizen --> Reset
    Citizen --> ManageProfile
    Citizen --> Preferences
    Volunteer --> Login
    Provider --> Login
    Provider --> ManageProfile

    Admin --> GrantRole
    Admin --> AccessControl

    QuickStart -.->|creates lightweight verified CITIZEN| Citizen

    style Register fill:#e8f5e9,stroke:#4caf50
    style QuickStart fill:#e8f5e9,stroke:#4caf50
    style Login fill:#e3f2fd,stroke:#2196f3
    style AccessControl fill:#fff3e0,stroke:#ff9800
```

---

## Role Capabilities

| Use Case | Public | Citizen | Volunteer | Service Provider | System Admin |
|----------|:-----:|:------:|:--------:|:---------------:|:-----------:|
| Register (email + password) | ✅ | — | — | — | — |
| Quick-start (phone + OTP) → CITIZEN | ✅ | — | — | — | — |
| Verify email | ✅ | ✅ | ✅ | ✅ | ✅ |
| Login / Logout | — | ✅ | ✅ | ✅ | ✅ |
| Reset password | — | ✅ | ✅ | ✅ | ✅ |
| Manage profile | — | ✅ | ✅ | ✅ | ✅ |
| Set preferences (language `en`/`hi`/`te`) | — | ✅ | ✅ | ✅ | ✅ |
| Grant / assign elevated role | — | — | — | — | ✅ |
| Whitelist / Blacklist (🔒 Post-MVP) | — | — | — | — | ✅ |

## Self-Service vs Granted Roles

- **Self-registration** is limited to `CITIZEN`, `PROVIDER`, `VOLUNTEER`.
- **All elevated roles** (`ORGANIZER`, `MANAGER`, `EVENT_MANAGER`, `EXECUTIVE` 🔒, `DM_AUTHORITY`, `AUDITOR`, `ADMIN`) are **granted by a System Admin** via `POST /users/{id}/role` — they cannot be self-assigned. (`EXECUTIVE` is Post-MVP.)
- The **`DM_AUTHORITY`** ("Event Admin") role may be granted to a Government Org **or** a vetted NGO.

## Notes

- Emergency fast-path: a citizen in crisis uses **phone + OTP quick-start**, which instantly creates a lightweight verified `CITIZEN` account (no long form).
- JWT auth: **15-minute access token + 7-day refresh**; token sent as `Authorization: Bearer`.
- **Whitelisting / blacklisting** belongs to the MAD module — **🔒 Post-MVP**.
- Canonical roles & permissions: `docs/development/IDRM-FS.md` §3.3.
