# Emergency Communications 101

> *Type: Guide (101 / foundational) · Audience: all stakeholders → developers · Status: Domain — phase-neutral · Track: Domain (#7)*
> *In a disaster, the right message to the right people at the right time saves lives; a missed one costs them.
> This guide covers emergency communications and how IDRM's alerts and notifications deliver it.*

---

## 1. Why communication is a lifeline

Disaster response is a coordination problem, and coordination is communication. People need to be **warned**
(danger is coming), **informed** (what to do, where to go), and **connected** (responders to needs, agencies to
each other). When communication fails — networks down, messages unclear, channels siloed — the whole response
degrades.

---

## 2. The main flows

- **Alerting / early warning** — pushing urgent messages *out* to many people fast ("evacuate zone 3 now").
- **Two-way coordination** — responders and coordinators exchanging updates.
- **Public information** — clear, calm guidance to affected citizens.
- **Inter-agency** — different organisations sharing a picture and tasking.

**Interoperability** — different systems/agencies being able to exchange information — is a recurring challenge;
open standards (e.g. **CAP**, the Common Alerting Protocol) exist precisely to bridge them.

---

## 3. Principles that matter

- **Timeliness** — late is often useless.
- **Clarity** — plain language, one clear action; no jargon in a crisis.
- **Reach & redundancy** — multiple channels, because any one may fail.
- **Trust** — messages must be authoritative and verified (misinformation is dangerous).
- **Accessibility & language** — reach everyone, in their language (critical in India's multilingual context).

---

## 4. How IDRM handles it

| Comms need | In IDRM |
|---|---|
| Push urgent messages | the **alerts** module |
| Per-user updates (status changes) | the **notifications** module |
| Clear public guidance | UI copy + accessible design |
| Record of what was sent | the **audit** trail |

- **MVP:** in-app alerts and notifications tied to incident lifecycle events (e.g. "your request was accepted"),
  kept simple.
- **FFP:** multi-channel intake and delivery (SMS, push, email), deeper real-time push, standards-based alerting
  (CAP), and full localization — deferred until the phase justifies it.

---

## 5. Mastery check

1. Explain why communication is central to disaster response.
2. Name the main communication flows.
3. State the principles (timeliness, clarity, redundancy, trust, accessibility).
4. Explain **interoperability** and why standards like CAP exist.
5. Map IDRM's alerts vs notifications, and MVP vs FFP scope.

---

## 6. Go deeper

- Common Alerting Protocol (CAP) — oasis-open.org · WMO/ITU early-warning guidance
- Related: [Common Operational Picture 101](common-operational-picture-101.md) · [Incident Command 101](incident-command-101.md)

---
*Next:* [Incident Command 101](incident-command-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
