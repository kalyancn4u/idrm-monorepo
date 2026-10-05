# IDRM — Role-Mastery Guides

Twelve **per-role learning journeys** (blueprint §25). Where the [101 library](../learn/README.md) is organised
by *topic*, these are organised by *job* — each takes one role from novice to mastery by **sequencing** the right
101 guides and specification docs in the right order, then stating the **mastery test** (the capability that
proves you've arrived).

**How to use:** find your role, follow its path top to bottom. Every rung links to the 101 guide or doc that
teaches it. Rungs are **phase-tagged** — MVP rungs are what you need to build/run IDRM now; FFP rungs come when
that phase begins.

**The universal ladder** (all roles share its shape — blueprint §24):
`Complete Novice → IDRM Orientation → Domain Literacy → Role Fundamentals → Tools & Technology → Guided Tasks →
Independent Tasks → Cross-Functional → Production Responsibility → Failure Handling → Design/Review → Mentor → Mastery.`

| # | Role | Guide | One-line mastery test |
|---|------|-------|------------------------|
| 1 | Product Manager / Owner | [product-manager.md](product-manager.md) | explain what IDRM solves, for whom, why, what's next, how success is measured |
| 2 | Business / Domain Analyst | [business-analyst.md](business-analyst.md) | turn ambiguous operational problems into precise, testable requirements |
| 3 | Solution / Software Architect | [solution-architect.md](solution-architect.md) | justify the structure against quality attributes + failure modes (ADRs) |
| 4 | Backend Engineer | [backend-engineer.md](backend-engineer.md) | ship a module end-to-end: API → domain → data → tests → observability |
| 5 | Frontend Engineer | [frontend-engineer.md](frontend-engineer.md) | build accessible, offline-aware UI on the API (MVP: HTML/JS; FFP: React) |
| 6 | GIS / Geospatial Engineer | [gis-engineer.md](gis-engineer.md) | model + query spatial data (PostGIS) and drive the map/COP |
| 7 | QA / SDET | [qa-sdet.md](qa-sdet.md) | design tests from requirements through E2E, security, resilience, drills |
| 8 | Security Engineer | [security-engineer.md](security-engineer.md) | reason networking → IAM → OIDC/OAuth → threat modeling → response |
| 9 | DevOps / SRE | [devops-sre.md](devops-sre.md) | own deploy → observability → SLOs → incident response → backup/DR |
| 10 | Data Engineer | [data-engineer.md](data-engineer.md) | model, quality-check, and govern operational + spatial data |
| 11 | Incident / Operations Manager | [incident-ops-manager.md](incident-ops-manager.md) | run the lifecycle: assess → command → task → close → after-action |
| 12 | Technical / Application Support | [technical-support.md](technical-support.md) | triage from logs/dashboards → runbooks → escalation → RCA |

*Status:* **12 of 12 COMPLETE** — all role-mastery guides written. *Start with:*
[Learning Paths](../00-start-learning-paths.md) · [Disaster Management 101](../learn/disaster-management-101.md).
