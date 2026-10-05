# _removed CLEANUP + ELUCIDATION + PICS — control ledger

> **The resume point for a multi-session program.** It runs three clubbed tasks in one pass over each retired
> document, section by section. Read this + `../instructions.txt` §12, then continue from **▶ RESUME HERE**.

## The pipeline (one reading → three outputs)

For each `_removed` document, for each **section** (H2 granularity):
1. **① ANNOTATE** — add/extend the top-of-doc **Section Map** (where addressed in latest docs · phase · verdict · PICS ids).
2. **② ELUCIDATE** — if the section carries teaching value missing from latest docs, fold it in (Hybrid model):
   deep *component* elucidation → `guides/mvp/learn/tech-stack-101.md`; *module* elucidation → `docs/mvp/25-module-elucidation.md`
   + `docs/ffp/25-module-elucidation.md`; enrich an existing topic doc only for a genuine gap.
3. **③ PICS** — emit conformance rows into `docs/mvp/26-conformance-pics.md` + `docs/ffp/26-conformance-pics.md`.

## Tag system (all greppable)

- **Snippet ID:** `‹gen›-‹docnum›§‹sec›` → e.g. `v0-10§4.3`. gen ∈ {v0,v1,v2,v3}.
- **① annotation:** the doc's top **Section Map** table; each doc carries `<!-- IDRM-CLEANUP doc=‹gen›-‹slug› status=ANNOTATED pass=‹date› -->`.
- **② elucidation:** `<!-- IDRM-ELUCID src=v0-10§4.3 -->` beside folded content.
- **③ PICS row id:** `PICS-‹MOD›-‹NNN›` (modules) or `PICS-STK-‹COMPONENT›-‹NN›` (stack); each row has `src=`.
- **Verdict:** ✅ covered · ⚠ superseded/nuanced · ➕ novel→folded · ⊘ dropped.
- **Modules:** USR users · INC incidents · RES resources · LOC locations · ALR alerts · NTF notifications ·
  RPT reports · FIL files · AUD audit · ADM administration.

## Progress — `idrm-docs-v0/docs` (scope confirmed: v0 first; v1–v3 = decide later)

| # | Document | ① Annotate | ② Elucidate | ③ PICS | Notes |
|---|---|---|---|---|---|
| 1 | `10-requirements-prd.md` | ✅ done | ◐ seeded (INC module + stack pattern) | ◐ seeded (INC rows + stack) | 23 sections mapped; full-doc Section Map |
| 2 | `20-architecture-hld.md` | ✅ done | ✅ USR·LOC·NTF elucidated (MVP+FFP) | ✅ USR·LOC·NTF rows + VALID/REPO/POOL | 23 sections mapped; mostly FFP (microservices/DevOps) |
| 3 | `50-data-model.md` | ✅ done | ✅ RES·FIL·AUD·ADM elucidated (MVP+FFP) | ✅ RES·FIL·AUD·ADM rows + ENUM | 18 sections mapped; financial domain = FFP |
| 4 | `40-api-resource-mapping.md` | ✅ done | ✅ ALR·RPT elucidated (10/10 modules) | ✅ ALR·RPT rows + API-standards | 21 sections mapped; v0 paths superseded by canonical /api/v1 |
| 5 | `51-data-triggers-views.md` | ✅ done | ✅ (stance: logic-in-service) | ✅ PICS-STK-LOGIC-01 | 13 sections mapped; materialized views/analytics = FFP |
| 6 | `11-requirements-prd-devops.md` | ✅ done (variant) | n/a (dup) | n/a (dup) | variant banner → see v0-10; DevOps adds = FFP |
| 7 | `21-architecture-hld-devops.md` | ✅ done (variant) | n/a (dup) | n/a (dup) | variant banner → see v0-20; DevOps adds = FFP |
| 8 | `35-design-devops-components.md` | ✅ done (variant) | n/a (dup) | n/a (dup) | variant banner → modules=25/26; infra=FFP |
| 9 | `12-requirements-prd-alt.md` | ✅ done (variant) | n/a (dup) | n/a (dup) | variant banner → superseded by docs/mvp/10 |

Legend: ✅ done · ◐ partial/seeded · ▶ next up · ▷ pending.

**Modules elucidated: ✅ 10 of 10** — INC · USR · LOC · NTF · RES · FIL · AUD · ADM · ALR · RPT (both phases).
Later passes deepen worked examples + add code/test evidence as the MVP is built.

**▶ RESUME HERE:** ✅ **`idrm-docs-v0/docs` is COMPLETE** — all 9 docs annotated (5 full Section Maps + 4 variant
banners); 25/26 (MVP+FFP) cover all 10 modules + core stack. **Next decision (ask user):** whether to extend the
program to `idrm-docs-v1/`, `-v2/`, `-v3/`, or treat v0 as sufficient and move on (e.g. to task I sign-off / the
MVP build gate). Backup: scratchpad `v0-docs-backup/`.

## Full passes on v1 / v2 / v3 (user chose FULL PASSES, 2026-08-16)

Same pipeline + tags. Since v0 already produced all 10 modules + core stack, later generations mostly **confirm
coverage** (Section Maps / variant banners) and add elucidation/PICS **only when genuinely new**. Full Section Maps
for distinct docs; variant banners for near-duplicates and setup guides.

**v1 (`idrm-docs-v1`) — ✅ COMPLETE (6 docs + 4 guides).** Nothing new for modules/PICS (v0 covered it). Confirmed:
FSD/TypeScript/Zod frontend = FFP (`docs/ffp/61`); CI/CD + staging/prod multi-env = FFP.
- docs: 10-prd (variant→v0-10) · 20-web-platform · 30-eng-spec · 40-api · 60-uipages · 80-ci-cd — all annotated.
- guides: 10/11/12/13 setup — variant banners → current guides + `docs/mvp/80`.

**v2 (`idrm-docs-v2`) — ✅ COMPLETE (14 content docs + 8 guides).** v2 is the generation that reached the current
MVP shape (**native monolith + HTML/Tailwind**), so it largely **confirms** the current docs (mostly ✅). Section
Maps: 11-funcspec, 20-monolith, 24-decisions, 41-json-formats, 60-design-system. Banners: 10,21,22,23,32,40,61,62,80
+ 8 guides. Nothing new for modules/PICS. (NB: some original v2 docs contain pre-existing broken links to
`instructions_*_v2.md` — legacy content, left as-is.)

**v3 (`idrm-docs-v3`) — ✅ COMPLETE (20 content docs + 9 guides).** FFP-rich generation. FFP banners: 81-redis
(no Redis in MVP, ADR-005), 82-api-gateway (APISIX not Bun/NGINX), 92-migration (Strangler Fig = FFP), 80-cicd.
Mapping banners for the rest. **NEW conformance rows added from v3:** `PICS-STK-QUALITY-01` (black/flake8/mypy +
type hints, from `71-code-standards`) and `PICS-STK-OPENAPI-01` (OpenAPI validated, from `72-data-formats`) → in
`docs/mvp/26`.

**▶ PROGRAM COMPLETE (2026-08-16):** ✅ all four generations annotated — v0 (9), v1 (10), v2 (22), v3 (29) =
**70 files** carry greppable Section Maps / variant banners. Elucidation (docs 25 MVP+FFP) covers all 10 modules;
PICS (docs 26 MVP+FFP) has all 10 modules + core stack (58 MVP + 29 FFP rows). Net-new from later generations:
only 2 stack rows (QUALITY-01, OPENAPI-01) — confirming v0 already captured the substance.
**NEXT:** the task-I **PICS sign-off** (completeness/quality review of docs 26, both phases) — the MUST-DO gate
before building the MVP code (task G). See `../instructions.txt` §9-I, §12.

## Later
- Deepen 25/26 with worked examples + code/test evidence once the MVP code (task G) exists.
- PICS completeness review = the task-I sign-off gate before coding (`../instructions.txt` §9-I, §12).
