# IDRM — Definition of Done (docs & guides)

> Cross-cutting **finalization checklist** for every document and guide in this archive. Referenced from the
> workflow ([`../instructions.txt`](../instructions.txt) §7) and the governance docs
> ([`../idrm-mvp-docs/90-governance-and-raci.md`](../idrm-mvp-docs/90-governance-and-raci.md) +
> its FFP delta). Source: documentation blueprint §32 (adopted as blueprint task **T4**).

> **The rule:** a document is not "done" because it *exists*. It is Done only when it passes the checklist below.
> Apply it before marking any doc/guide complete or updating a CHANGELOG to "done."

---

## 1. Blueprint criteria (all 14 must hold)

A doc/guide is **Done** when:

1. **Purpose** is explicit (stated up front).
2. **Scope** is explicit (what's in / out — and which **phase**, MVP vs FFP).
3. **Owner** is identified (the Accountable owner — see [`../idrm-mvp-docs/90-governance-and-raci.md`](../idrm-mvp-docs/90-governance-and-raci.md)).
4. **Inputs** are identified (what it draws on / depends on).
5. **Outputs** are identified (what it produces / feeds).
6. **Dependencies** are identified (linked, not assumed).
7. **Terminology** is consistent (matches the [domain card](domain.md); e.g. "help request" == `incident`).
8. **Diagrams agree with the text** (no diagram contradicts prose; both current).
9. **Requirements are traceable** (links into [`../idrm-mvp-docs/13-requirements-traceability-matrix.md`](../idrm-mvp-docs/13-requirements-traceability-matrix.md)).
10. **Security implications** are addressed (or explicitly "none").
11. **Accessibility implications** are addressed where relevant (WCAG; the map→list rule).
12. **Operational consequences** are documented (deploy/run/observe/backup impact).
13. **Test implications** are identified (for guides: a **mastery check** instead).
14. **Version/history** is maintained (dated **CHANGELOG** entry).
15. **Relevant stakeholders have reviewed it** (at minimum the Accountable owner + the user for locked decisions).

## 2. IDRM conventions (also required here)

Enforced across this archive — check these too:

- **Header line** present: `> *Type: … · Audience: … · Status: MVP|FFP — …*`.
- **Phase-honest:** MVP stays lean; advanced tech is tagged **FFP**, never smuggled into the MVP (respects the
  [locked decisions](../instructions.txt) §4).
- **Cross-link, don't duplicate:** one source of truth per fact; when a doc and this checklist conflict, the
  doc wins and is corrected. No parallel copies (the guardrail that drove the hub-and-spoke split + the guides).
- **CHANGELOG updated** (Keep-a-Changelog: Added/Changed/Removed/Decided, dated) in the relevant set.
- **For guides — the quality bar:** clear and precise yet lucid; a complete novice can reach **mastery**
  (define terms, worked examples, explain the *why*, end with a mastery check).

## 3. Copy-paste checklist

```
DoD — [doc/guide name]
[ ] Purpose explicit        [ ] Scope + phase explicit   [ ] Owner named
[ ] Inputs / Outputs        [ ] Dependencies linked      [ ] Terminology consistent
[ ] Diagrams match text     [ ] Requirements traceable   [ ] Security addressed
[ ] Accessibility (if rel.) [ ] Operational consequences [ ] Tests / mastery-check
[ ] CHANGELOG entry (dated) [ ] Reviewed (owner + user)
IDRM: [ ] header line  [ ] phase-honest  [ ] cross-linked (no dup)  [ ] quality bar (guides)
```

## 4. Status of the existing archive

The MVP/FFP doc sets and the guide library were authored to these conventions (headers, traceability, cross-
links, CHANGELOGs, phase-tags, mastery checks), so they broadly **already satisfy** this DoD. Use the checklist
going forward for every new or changed doc/guide, and as a periodic audit gate.

---
*Related:* workflow [`../instructions.txt`](../instructions.txt) §7 · governance
[`../idrm-mvp-docs/90-governance-and-raci.md`](../idrm-mvp-docs/90-governance-and-raci.md) · traceability
[`../idrm-mvp-docs/13-requirements-traceability-matrix.md`](../idrm-mvp-docs/13-requirements-traceability-matrix.md).
