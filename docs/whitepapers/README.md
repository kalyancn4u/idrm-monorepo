# IDRM Technical White Papers — the Intelligence Engines (*design-now / build-FFP*)

> *Type: White-paper hub · Audience: complete novices → data scientists, architects & product owners · Status:
> design-now / build-FFP.*
> *Six papers describing the "intelligent" engines IDRM will grow into. The **engines themselves are FFP**
> (Full-Fledged Product — the enterprise phase); we **author them now** so the MVP is built with the right
> **seams** in place, and so the reasoning, privacy stance, and evaluation plan are settled before a line of ML
> code is written. Each paper cross-links the MVP decisions in [`../mvp/21-architecture-decisions.md`](../mvp/21-architecture-decisions.md)
> (ADRs), [`../mvp/25-module-elucidation.md`](../mvp/25-module-elucidation.md) (modules) and
> [`../mvp/26-conformance-pics.md`](../mvp/26-conformance-pics.md) (the conformance checklist).*

---

## 0. What "design-now, build-FFP" means (read this first)

**IDRM** (Integrated Disaster Response Management) ships in two phases. The **MVP** (Minimum Viable Product) is a
deliberately simple, single-server app that works today. The **FFP** is the enterprise evolution it grows into
*without a rewrite*. The six engines below — a real chatbot, anomaly detection, credibility scoring, two
recommenders, churn detection — are **FFP features**. So why write about them now?

Because the cheapest time to leave a **seam** for a future feature is *while you build the wall around it*. A
**seam** here means a small, deliberate hook in the MVP code — a stub endpoint, a logged event, a nullable column —
that the future engine plugs into instead of forcing a redesign. Every paper names the **seam already present in
the MVP** so that, when the trigger to build the engine finally arrives, the work is *addition*, not *surgery*.

> **A word on caution.** IDRM operates in disasters, where a wrong automated answer or a mis-ranked responder can
> cost time when time is life. So every engine here is designed **human-in-the-loop** (a person stays in control of
> consequential decisions), **explainable-first** (you can always ask *"why did it say that?"*), and **fail-safe**
> (when unsure, it defers to a human or a known-safe default). None of these engines is a black box that acts alone.

---

## 1. Cross-cutting principles (true of all six papers)

| Principle | What it means for a novice | Why it matters here |
|---|---|---|
| **Classical-first, DL upgrade path** | Start with simple, cheap, *explainable* methods (word-counting, correlation, rules, small models); only reach for deep learning / large language models when the simple method's limits are proven. | Cheap to run on modest hardware (India-scale, on-prem), easy to audit, hard to fool silently, and quick to ship. |
| **DPDP-by-design** | The **Digital Personal Data Protection Act 2023** is India's privacy law. We minimise personal data, get consent, and never send it to third parties. | Disaster data is sensitive (health, location, identity). Privacy is a legal *and* ethical hard requirement. |
| **On-premises models** | The ML runs on IDRM's own servers, not an external cloud AI API. | No citizen data leaves the platform; works even with patchy connectivity. |
| **Human-in-the-loop** | A person approves or can override any consequential output. | Automation *assists* coordinators; it does not replace their judgement. |
| **Every engine has an MVP seam** | The MVP already logs the events / exposes the stub / stores the fields the engine will need. | The FFP build is incremental, on a trigger — never a rewrite (Strangler-Fig, see [`../mvp/21-architecture-decisions.md`](../mvp/21-architecture-decisions.md)). |

Each paper follows the **same eight-part template**, so once you've read one you can navigate any of them:

1. **The problem** (plain language) → 2. **Where it fits** (the MVP seam) → 3. **Data inputs** →
4. **Method options + recommendation** (classical-first ladder) → 5. **Architecture** (a diagram) →
6. **Privacy / DPDP** → 7. **MVP-seam vs FFP-build** → 8. **Metrics** (how we'll know it works).

---

## 2. The six papers

| # | Paper | In one line | Feeds / evolves | Status |
|---|---|---|---|---|
| 1 | [`1-faq-chatbot.md`](1-faq-chatbot.md) | Evolve the Task-L stub into a real, grounded FAQ assistant | `POST /notifications/chat` stub (Task L) | 🟢 written |
| 2 | [`2-anomaly-detection-rate-limiting.md`](2-anomaly-detection-rate-limiting.md) | Adaptive traffic rate-limiting, session/user prioritisation, smart allow/deny lists | the static in-process rate-limiter (roadmap §8.4) | 🟢 written |
| 3 | [`3-credibility-assessment.md`](3-credibility-assessment.md) | Score the trustworthiness of reporters / incidents / providers | the audit trail + verification fields | 🟢 written |
| 4 | [`4-recommender-financial-charity.md`](4-recommender-financial-charity.md) | A donations/charity module that recommends where funds do most good | (money is → FFP; no MVP money) | 🟢 written |
| 5 | [`5-recommender-incident-notification-routing.md`](5-recommender-incident-notification-routing.md) | Route each incident/notification to the right responder & channel per persona | the notifications module + org matching | 🟢 written |
| 6 | [`6-churn-detection.md`](6-churn-detection.md) | Detect when citizens, providers, or volunteers are disengaging | the audit trail + activity timestamps | 🟢 written |

*All six papers are written. Each follows the same 8-part template; the engines remain **→ FFP**, built on a
trigger, on the MVP seams named in each paper.*

**Companion note (not one of the six):** [`face-quality-gate.md`](face-quality-gate.md) — the face-**detection**-
only photo-quality gate (ADR-011): client-side detection **implemented**, FaceNet **recognition** → FFP.

---

## 3. Reference material (the source notebooks)

Two prior data-science notebooks (kept for reference in `../../archive/analyses/notebooks/`) supply the method
backbone that Papers 1, 4 and 5 build on — reused here so we design with proven techniques rather than re-deriving:

- **`dsml_faqs_chatbot.ipynb`** — two-stage FAQ bot: TF-IDF / BM25 retrieval (+ FAISS), Word2Vec/LDA for semantics,
  DistilGPT-2 generation, quantization for CPU, and NER-based PII detection. → **Paper 1**.
- **`Zee_Recommender_*.ipynb`** — the recommender toolkit: collaborative filtering (Pearson / cosine / KNN), matrix
  factorization (SVD, ALS), regression + ensemble, cold-start, evaluated with RMSE / MAE / MAPE. → **Papers 4 & 5**.

---

## Related

- [`../mvp/21-architecture-decisions.md`](../mvp/21-architecture-decisions.md) — the MVP ADRs (why things are deferred to FFP)
- [`../mvp/25-module-elucidation.md`](../mvp/25-module-elucidation.md) — what each MVP module does
- [`../mvp/26-conformance-pics.md`](../mvp/26-conformance-pics.md) — the conformance checklist (where engine rows will land)
- [`../mvp/27-implementation-roadmap.md`](../mvp/27-implementation-roadmap.md) §15 — the full "deferred to FFP" catalogue

---

## Changelog

- **2026-08-17** — Created the white-paper hub + shared 8-part template; decisions locked (standalone
  `docs/whitepapers/` folder, one paper at a time, full depth with diagram + worked example, classical-first with a
  DL upgrade path). **Paper 1 (FAQ chatbot) written.** Papers 2–6 to follow, one at a time.
- **2026-08-17** — **Paper 2 (Anomaly-Detection Engine #1 — adaptive rate-limiting, prioritisation & smart lists)
  written.** Papers 3–6 to follow.
- **2026-08-17** — **Paper 3 (Anomaly-Detection Engine #2 — Credibility Assessment: reporters/incidents/providers)
  written.** Papers 4–6 to follow.
- **2026-08-17** — **Paper 4 (Recommender #1 — Financial / Charity module)** written, on the Zee-notebook CF/MF
  backbone, re-centred on impact/equity over revenue. Papers 5–6 to follow.
- **2026-08-17** — **Paper 5 (Recommender #2 — Incident-Notification Routing)** written (responder matching +
  persona/channel routing + escalation); Paper 3's forward link re-linked. Paper 6 to follow.
- **2026-08-17** — **Paper 6 (Churn Detection)** written (persona-aware, readiness-not-engagement, no dark
  patterns). ***All six white papers complete (Task M).*** Engines remain → FFP.
- **2026-08-17** — Added companion note **`face-quality-gate.md`** + shipped the client-side detection gate
  (`code/frontend/static/js/face-quality.js`, ADR-011): on-device, advisory, nothing biometric stored. Server
  `passes_face_quality_gate` documented as an intentional no-op. `PICS-FIL-005` stays Planned pending a manual
  browser check.
