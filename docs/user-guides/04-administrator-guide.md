# Administrator Guide (System Administrators)

> **Part of:** IDRM Documentation · `user-guides/04-administrator-guide.md`
> **Answers:** How do I manage users, roles, organisations, settings, and keep the platform healthy?
> **Source posters:** Poster 8 (System Administrators persona), Poster 7 (Workflow)
> **Audience:** System administrators · **Depth:** Overview (task-oriented)
> **Status:** Draft

---

*As an administrator, IDRM lets you **manage users and roles, configure the platform, protect data and
privacy, and monitor health** — so everyone else can work reliably.*

## Get started (first time)

1. Sign in with your administrator account.
2. Open **Administration** to reach user management, roles, organisations, and settings.
3. Review the **audit log** to see recent activity.

## How to…

**Manage users**
1. Open **Administration → Users**.
2. **Add** a user (name, email, role, organisation) or **edit** an existing one.
3. Set a user **active** or **inactive**; users only ever see what their **role** allows.

**Manage roles & access**
1. Open **Roles** to review each role and what it can do (role-based access control).
2. Assign the appropriate role to each user — grant the **least access** needed.

**Manage organisations**
- Add and **verify** organisations (NGOs, agencies, responders) so they can be assigned and appear correctly.

**Configure settings**
- Adjust platform settings (e.g. notification channels, reference data such as incident and resource types).

**Protect data & privacy**
- Ensure privacy practices are followed (personal data minimised and access-controlled) per the DPDP Act; see
  [`../05-security.md`](../05-security.md).

**Monitor health**
- Check system **health, logs, and alerts** (see [`../07-operations.md`](../07-operations.md)); review the
  **audit log** for accountability.

## Reference

| Term | Meaning |
|---|---|
| **Role** | A named set of permissions (e.g. Citizen, Responder, Coordinator, Admin). |
| **RBAC** | Role-based access control — permissions follow the role. |
| **Audit log** | An immutable record of who did what, when. |
| **Verification** | Confirming an organisation before it's used in the system. |

## Understand

You keep IDRM **secure, correct, and available**. Careful role assignment (least privilege), verified
organisations, and regular attention to logs and health are what let citizens, responders, and coordinators
trust the platform during a real event. For the deeper technical picture, see
[`../05-security.md`](../05-security.md) and [`../07-operations.md`](../07-operations.md).
