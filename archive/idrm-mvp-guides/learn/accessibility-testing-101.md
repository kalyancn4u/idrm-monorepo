# Accessibility Testing 101

> *Type: Guide (101 / foundational) · Audience: all stakeholders → developers/QA · Status: MVP — current · Track: Quality (#30)*
> *In a disaster, IDRM may be used one-handed, on a cracked phone, in bright sun, by someone injured, elderly, or
> using a screen reader. If the interface excludes them, it fails at its job. Accessibility testing makes sure it
> doesn't.*

---

## 1. What accessibility means (and why it's non-negotiable here)

**Accessibility (often "a11y")** means people with disabilities — visual, motor, hearing, cognitive — can use
the software. For IDRM it's broader still: **situational** limits (one hand free, glare, panic, a slow network)
affect *everyone* in an emergency. Designing for the hardest case makes the product better for all.

The global standard is **WCAG — Web Content Accessibility Guidelines**. IDRM targets **WCAG 2.2 AA** across
**both** phases (raised from 2.1 in the T3 standards alignment). "AA" is the widely-adopted conformance level;
2.2 adds criteria like target size, focus appearance, consistent help, and accessible authentication.

---

## 2. The four WCAG principles: POUR

- **Perceivable** — users can perceive the content (text alternatives for images, sufficient colour contrast,
  captions).
- **Operable** — usable by keyboard, not just mouse/touch; enough time; no seizure-inducing flashes.
- **Understandable** — clear language, predictable behaviour, helpful error messages.
- **Robust** — works with assistive technologies (screen readers) via correct HTML/ARIA.

---

## 3. What to test in IDRM

- **Keyboard only** — unplug the mouse: can you report a help request, navigate the list, submit forms? Is focus
  visible and in a logical order?
- **Screen reader** — do images have alt text? Are form fields labelled? Are errors announced?
- **Colour & contrast** — text contrast ≥ 4.5:1; **never rely on colour alone** — critical for incident
  **priority** and **status** (red/amber/green must also carry text/icons for colour-blind users).
- **The map alternative** — IDRM's map must always be paired with an accessible **list/table** of the same
  incidents, so a screen-reader user can do the whole job without the map. **Test that path explicitly.**
- **Forms** — labels tied to inputs, errors linked with `aria-describedby`, focus moves to the first error.

---

## 4. How to test (a layered approach)

- **Automated** — tools like **axe** catch a large share of issues fast (missing labels, low contrast). Run them
  in CI so regressions are caught automatically.
- **Manual** — automation can't judge *usability*; do keyboard walkthroughs and a real screen-reader pass
  (NVDA/VoiceOver) on the key flows.
- **Semantic HTML first** — most accessibility comes free from using the right elements (`<button>`, `<label>`,
  headings in order); ARIA only patches the gaps.

> Automated tools find *maybe* a third to a half of issues. They're necessary, not sufficient — manual testing of
> the core journeys is what proves real usability.

---

## 5. Mastery check

1. Explain accessibility and why **situational** limits make it universal in IDRM.
2. State the WCAG level IDRM targets (**2.2 AA, both phases**) and the **POUR** principles.
3. Describe a keyboard-only and a screen-reader test of reporting a help request.
4. Explain "never rely on colour alone" using incident priority.
5. Say why the **map must have a list alternative**, and why automation isn't enough.

---

## 6. Go deeper

- WCAG 2.2 — w3.org/TR/WCAG22 · WAI-ARIA Authoring Practices — w3.org/WAI/ARIA/apg · axe — deque.com/axe
- IDRM UI: [`../../idrm-mvp-docs/60-uidesign-web-interaction.md`](../../idrm-mvp-docs/60-uidesign-web-interaction.md) ·
  FFP frontend a11y [`../../idrm-ffp-docs/61-frontend-engineering-standards.md`](../../idrm-ffp-docs/61-frontend-engineering-standards.md) §11
- Related: [Testing 101](testing-101.md) · [GIS for Emergency Response](gis-for-emergency-response.md)

---
*Next:* Linux 101 (Operations track) · *Up:* [Learning Paths](../00-start-learning-paths.md)
