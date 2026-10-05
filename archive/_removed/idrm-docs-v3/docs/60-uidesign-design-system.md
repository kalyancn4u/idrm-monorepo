# IDRM v3 · Design System

<!-- IDRM-CLEANUP doc=v3-60-designsystem status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — design system → `docs/mvp/60`
> → [`../../../../docs/mvp/60-uidesign-web-interaction.md`](../../../../docs/mvp/60-uidesign-web-interaction.md)
> (HTML+Tailwind, WCAG 2.2 AA). ⚠ MVP; token/component specifics not normative (a mature token system is an FFP
> refinement). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
*Type: Document (specification) · Audience: Designers, frontend devs · Status: Archived — v3 historical generation*
*Consolidated from: 12-DESIGN-SYSTEM.md, design-system-v3.md*

## Contents
- [IDRM: Complete Design System](#idrm-complete-design-system)
- [IDRM Design System v3.0](#idrm-design-system-v30)

---

## IDRM: Complete Design System

### Visual Language, Color Theory, Accessibility & UI Components

**Version**: 3.0 Consolidated  
**Audience**: Designers, developers, complete novices  
**Reading Time**: 45-60 minutes  
**Last Updated**: May 15, 2026

---

### 📚 **Table of Contents**

1. [Design System Overview](#1-design-system-overview)
2. [Color Theory Fundamentals](#2-color-theory-fundamentals)
3. [IDRM Color Palette](#3-idrm-color-palette)
4. [WCAG Accessibility Guidelines](#4-wcag-accessibility-guidelines)
5. [Typography System](#5-typography-system)
6. [Visual Hierarchy](#6-visual-hierarchy)
7. [Spacing & Layout](#7-spacing--layout)
8. [Component Library](#8-component-library)
9. [Responsive Design](#9-responsive-design)
10. [Implementation Guide](#10-implementation-guide)

---

### 1. **Design System Overview**

#### 1.1 What Is a Design System? (For Complete Nov

ices)

**Simple Explanation**:
Think of a design system like a **LEGO instruction manual** for building a website:
- It tells you what colors to use (like which LEGO bricks)
- It tells you what sizes to use (how big each brick should be)
- It tells you how to arrange things (where each brick goes)
- It makes sure everything looks consistent (all follow the same pattern)

**Why IDRM Needs a Design System**:
- ✅ **Consistency**: All pages look like they belong together
- ✅ **Speed**: Designers/developers don't reinvent the wheel
- ✅ **Accessibility**: Works for people with disabilities
- ✅ **Scalability**: Easy to add new pages/features

#### 1.2 IDRM Design Principles

**1. Urgency Without Panic**
```
Problem: Disasters are urgent, but panic doesn't help
Solution: Use color to show priority clearly but calmly
Example: Red for "critical" but not flashing/alarming
```

**2. Clarity Under Stress**
```
Problem: People in disasters are stressed and distracted
Solution: Simple, clear, easy to understand at a glance
Example: Big buttons, clear labels, minimal clutter
```

**3. Accessibility First**
```
Problem: Not everyone can see colors or use a mouse
Solution: Works for colorblind, screen readers, keyboard-only
Example: Text explains what color alone shows
```

**4. Mobile-First**
```
Problem: Most disaster response happens on phones
Solution: Design for phones first, then adapt to desktop
Example: Big touch targets, vertical scrolling
```

---

### 2. **Color Theory Fundamentals**

#### 2.1 What Is Color Theory? (Complete Novice Explanation)

**Color theory** = Rules about how colors work together

**Think of it like music**:
- Some colors "harmonize" (look good together)
- Some colors "clash" (look bad together)
- Some colors have "meaning" (red = danger, green = safe)

#### 2.2 The Color Wheel (Basics)

```
        🟡 Yellow
       /    \
      /      \
   🟠          🟢
  Orange      Green
     \          /
      \        /
       🔴   🔵
       Red  Blue
        \  /
         \/
        🟣
      Purple
```

**Color Relationships**:

**1. Complementary Colors** (opposite on wheel):
```
Red ↔ Green
Blue ↔ Orange  
Yellow ↔ Purple

Use for: High contrast (buttons, alerts)
```

**2. Analogous Colors** (next to each other):
```
Red → Orange → Yellow
Blue → Purple → Red

Use for: Harmonious, calming designs
```

**3. Triadic Colors** (triangle on wheel):
```
Red + Yellow + Blue
Orange + Green + Purple

Use for: Vibrant, balanced designs
```

#### 2.3 Color Psychology (What Colors Mean)

| Color | Psychological Association | IDRM Use Case |
|-------|---------------------------|---------------|
| **Red** | Danger, urgency, stop | Critical service requests |
| **Orange** | Warning, caution | High priority requests |
| **Yellow** | Attention, medium alert | Medium priority |
| **Green** | Safe, complete, success | Completed services |
| **Blue** | Trust, calm, professional | Brand color, low priority |
| **Purple** | Authority, dignity | Admin/management |
| **Gray** | Neutral, balanced | Secondary information |

#### 2.4 Color Properties (HSL Explained)

**HSL** = Hue, Saturation, Lightness (easier to understand than RGB)

**Hue** = The color itself (red, blue, green)
```
0°   = Red
120° = Green  
240° = Blue
```

**Saturation** = How vivid the color is
```
0%   = Gray (no color)
50%  = Muted color
100% = Vivid, pure color
```

**Lightness** = How bright the color is
```
0%   = Black
50%  = True color
100% = White
```

**Example**:
```css
/* Vivid red */
hsl(0, 100%, 50%)  /* Hue=Red, Saturation=100%, Lightness=50% */

/* Muted red */
hsl(0, 40%, 50%)   /* Same hue, less saturated */

/* Dark red */
hsl(0, 100%, 30%)  /* Same hue, darker */
```

---

### 3. **IDRM Color Palette**

#### 3.1 Brand Colors (Primary Identity)

**Brand Blue** = Trust, calm, professional

```css
/* Tailwind CSS configuration */
brand: {
  50:  '#f0f9ff',  /* Lightest - backgrounds */
  100: '#e0f2fe',
  200: '#bae6fd',
  300: '#7dd3fc',
  400: '#38bdf8',
  500: '#0ea5e9',  /* ⭐ PRIMARY - main brand color */
  600: '#0284c7',  /* Hover states */
  700: '#0369a1',  /* Active states */
  800: '#075985',
  900: '#0c4a6e',  /* Darkest - text */
}
```

**When to use**:
- `500`: Main buttons, links, headers
- `600`: Hover state for buttons
- `50-100`: Light backgrounds
- `700-900`: Dark text on light backgrounds

#### 3.2 Priority Colors (Service Urgency)

**These colors communicate how urgent a service request is**:

##### **Critical** (Life-threatening)
```css
critical: {
  light: '#fee2e2',    /* Background */
  DEFAULT: '#dc2626',  /* Text/border */
  dark: '#991b1b',     /* Hover */
}
```
**Use for**: Medical emergencies, immediate rescue
**Example**: "Injured person needs ambulance NOW"

##### **High** (Urgent, not life-threatening)
```css
high: {
  light: '#fed7aa',    /* Background */
  DEFAULT: '#ea580c',  /* Text/border */
  dark: '#c2410c',     /* Hover */
}
```
**Use for**: Food for hungry families, shelter needed
**Example**: "Family of 5 needs food and shelter"

##### **Medium** (Important but can wait)
```css
medium: {
  light: '#fef3c7',    /* Background */
  DEFAULT: '#f59e0b',  /* Text/border */
  dark: '#d97706',     /* Hover */
}
```
**Use for**: Supply requests, general assistance
**Example**: "Need blankets and basic supplies"

##### **Low** (Information/Non-urgent)
```css
low: {
  light: '#dbeafe',    /* Background */
  DEFAULT: '#3b82f6',  /* Text/border */
  dark: '#1e40af',     /* Hover */
}
```
**Use for**: Information requests, status updates
**Example**: "Where can I get information?"

#### 3.3 Status Colors (Service Progress)

**These colors show what stage a service request is in**:

##### **Submitted** (Just created)
```css
submitted: {
  light: '#e0e7ff',
  DEFAULT: '#6366f1',  /* Purple-blue */
  dark: '#4338ca',
}
```

##### **Approved** (Authority approved)
```css
approved: {
  light: '#dbeafe',
  DEFAULT: '#2563eb',  /* Blue */
  dark: '#1e40af',
}
```

##### **In Progress** (Being worked on)
```css
in_progress: {
  light: '#fef3c7',
  DEFAULT: '#f59e0b',  /* Amber/yellow */
  dark: '#d97706',
}
```

##### **Completed** (Work done)
```css
completed: {
  light: '#d1fae5',
  DEFAULT: '#10b981',  /* Green */
  dark: '#059669',
}
```

##### **Verified** (Confirmed complete)
```css
verified: {
  light: '#d1fae5',
  DEFAULT: '#059669',  /* Dark green */
  dark: '#047857',
}
```

---

### 4. **WCAG Accessibility Guidelines**

#### 4.1 What Is WCAG? (For Complete Novices)

**WCAG** = Web Content Accessibility Guidelines

**Simple explanation**: Rules to make websites usable by everyone, including:
- People who can't see well (or at all)
- People who can't use a mouse
- People with color blindness
- People with dyslexia

**IDRM Target**: WCAG 2.1 Level AA (industry standard)

#### 4.2 Color Contrast Requirements

**Contrast Ratio** = Difference between text and background

**WCAG Requirements**:
```
Normal text (< 18pt):     4.5:1 minimum ✅
Large text (≥ 18pt):      3:1 minimum ✅
UI components (buttons):  3:1 minimum ✅
```

**What the numbers mean**:
- `21:1` = Black on white (maximum contrast)
- `4.5:1` = Minimum for readability
- `2:1` = Too low, hard to read

**IDRM Color Contrast Examples**:

✅ **Good Contrast** (passes WCAG):
```html
<!-- White text on brand-600 background -->
<button class="bg-brand-600 text-white">
  Submit Request (Contrast: 6.2:1) ✅
</button>

<!-- Gray-900 text on white background -->
<p class="text-gray-900">
  Service description (Contrast: 15.8:1) ✅
</p>
```

❌ **Bad Contrast** (fails WCAG):
```html
<!-- Light gray text on white background -->
<p class="text-gray-300">
  Hard to read text (Contrast: 1.8:1) ❌
</p>

<!-- Yellow text on white background -->
<p class="text-yellow-400">
  Also hard to read (Contrast: 1.4:1) ❌
</p>
```

#### 4.3 Color Blindness Considerations

**8% of men** and **0.5% of women** have color blindness

**Common Types**:

**1. Red-Green Color Blindness** (Most common)
```
Problem: Can't distinguish red from green
IDRM Solution: Never use ONLY color to show meaning
Example: Critical (red) + "CRITICAL" label + icon
```

**2. Blue-Yellow Color Blindness** (Rare)
```
Problem: Can't distinguish blue from yellow  
IDRM Solution: Use different lightness levels
Example: Dark blue vs bright yellow (lightness differs)
```

**IDRM Accessibility Rule**:
```
❌ Bad:  Color only
   "Red dot = critical, Green dot = completed"
   → Color blind users can't tell the difference!

✅ Good: Color + Icon + Text
   "🔴 Red dot + ⚠️ icon + 'CRITICAL' text"
   → Everyone understands!
```

#### 4.4 Keyboard Navigation

**Why it matters**: Not everyone can use a mouse
- People with motor disabilities
- Power users (faster with keyboard)
- Screen reader users

**WCAG Requirements**:
```
✅ All interactive elements keyboard-accessible
✅ Visible focus indicators
✅ Logical tab order
✅ Skip navigation links
```

**IDRM Implementation**:
```html
<!-- Focus ring visible -->
<button class="focus:ring-2 focus:ring-brand-500 focus:ring-offset-2">
  Click or Press Enter
</button>

<!-- Skip to main content (for screen readers) -->
<a href="#main-content" class="sr-only focus:not-sr-only">
  Skip to main content
</a>
```

#### 4.5 Screen Reader Support

**What are screen readers?**
Software that reads websites aloud for blind users

**WCAG Requirements**:
```
✅ Alt text for images
✅ ARIA labels for icons
✅ Semantic HTML (headings, lists, etc.)
✅ Form labels associated with inputs
```

**IDRM Examples**:
```html
<!-- Image with alt text -->
<img src="ambulance.jpg" alt="Ambulance icon" />

<!-- Icon button with ARIA label -->
<button aria-label="Close dialog">
  <svg aria-hidden="true">...</svg>
</button>

<!-- Form with proper labels -->
<label for="email">Email Address</label>
<input id="email" type="email" />
```

---

### 5. **Typography System**

#### 5.1 Font Family

**Primary Font**: **Inter** (modern, highly readable)

```css
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

**Why Inter?**
- ✅ Designed for screens (not print)
- ✅ Excellent readability at small sizes
- ✅ Open source (free)
- ✅ Great multilingual support (Hindi, Tamil, etc.)

**Fallback Fonts**:
```
Inter → system-ui → -apple-system → sans-serif
  ↓         ↓            ↓              ↓
Custom   OS font    Apple font    Generic
```

#### 5.2 Font Sizes (Tailwind Scale)

| Class | Size | Use For |
|-------|------|---------|
| `text-xs` | 12px | Small labels, timestamps |
| `text-sm` | 14px | Secondary text, captions |
| `text-base` | 16px | ⭐ Body text (default) |
| `text-lg` | 18px | Prominent paragraphs |
| `text-xl` | 20px | Section headings |
| `text-2xl` | 24px | Page subheadings |
| `text-3xl` | 30px | Card titles |
| `text-4xl` | 36px | Page headings |
| `text-5xl` | 48px | Hero headings |

**Accessibility Rule**: Base text must be ≥ 16px for readability

#### 5.3 Font Weights

| Class | Weight | Use For |
|-------|--------|---------|
| `font-normal` | 400 | Body text |
| `font-medium` | 500 | Emphasized text |
| `font-semibold` | 600 | Headings, buttons |
| `font-bold` | 700 | Strong emphasis |

**IDRM Rule**: Use `font-semibold` for headings, `font-medium` for buttons

#### 5.4 Line Height (Leading)

**Line height** = Space between lines of text

```css
/* Too tight - hard to read */
line-height: 1.0;  /* Cramped */

/* Perfect for body text */
line-height: 1.5;  /* Comfortable ✅ */

/* Good for headings */
line-height: 1.2;  /* Compact but readable */
```

**Tailwind Classes**:
- `leading-none` (1.0) - Headings only
- `leading-tight` (1.25) - Large headings
- `leading-normal` (1.5) - ⭐ Body text default
- `leading-relaxed` (1.625) - Long-form content

---

### 6. **Visual Hierarchy**

#### 6.1 What Is Visual Hierarchy? (For Novices)

**Visual hierarchy** = Making important things look more important

**Like a newspaper**:
- Headline: Biggest, boldest (most important)
- Subheading: Medium size
- Body text: Smallest (details)

**Your eyes naturally go**: Big → Bold → Colorful → First

#### 6.2 Hierarchy Techniques

##### **1. Size** (Bigger = More Important)
```html
<h1 class="text-4xl">Most Important</h1>
<h2 class="text-2xl">Less Important</h2>
<p class="text-base">Least Important</p>
```

##### **2. Weight** (Bolder = More Important)
```html
<p class="font-bold">Important</p>
<p class="font-medium">Less Important</p>
<p class="font-normal">Least Important</p>
```

##### **3. Color** (High Contrast = More Important)
```html
<p class="text-gray-900">Dark text stands out</p>
<p class="text-gray-600">Medium text recedes</p>
<p class="text-gray-400">Light text fades</p>
```

##### **4. Spacing** (More Space = More Important)
```html
<h1 class="mb-8">Title with lots of space below</h1>
<p class="mb-4">Paragraph with medium space</p>
<span class="mb-1">Small text with little space</span>
```

#### 6.3 IDRM Hierarchy Pattern

```html
<!-- Page structure showing hierarchy -->
<div class="space-y-8">
  <!-- Level 1: Page title -->
  <h1 class="text-4xl font-bold text-gray-900">
    Disaster Response Dashboard
  </h1>

  <!-- Level 2: Section title -->
  <h2 class="text-2xl font-semibold text-gray-800">
    Active Service Requests
  </h2>

  <!-- Level 3: Card title -->
  <div class="card">
    <h3 class="text-lg font-medium text-gray-900">
      Critical: Medical Emergency
    </h3>
    
    <!-- Level 4: Body text -->
    <p class="text-base text-gray-600 mt-2">
      Person injured, needs immediate medical attention.
    </p>
    
    <!-- Level 5: Meta information -->
    <span class="text-sm text-gray-500 mt-1">
      Submitted 2 hours ago
    </span>
  </div>
</div>
```

**Notice the pattern**:
- Font size decreases (4xl → 2xl → lg → base → sm)
- Font weight decreases (bold → semibold → medium)
- Color lightens (gray-900 → gray-800 → gray-600 → gray-500)
- Spacing decreases (mb-8 → mb-4 → mt-2 → mt-1)

---

### 7. **Spacing & Layout**

#### 7.1 Spacing Scale (Tailwind)

**Tailwind uses a consistent 4px scale**:

| Class | Pixels | Use For |
|-------|--------|---------|
| `space-1` | 4px | Tiny gaps |
| `space-2` | 8px | Small gaps |
| `space-4` | 16px | ⭐ Default gap |
| `space-6` | 24px | Medium gap |
| `space-8` | 32px | Large gap |
| `space-12` | 48px | XL gap |
| `space-16` | 64px | XXL gap |

**IDRM Rule**: Use multiples of 4 for consistency (4, 8, 12, 16, 24, 32...)

#### 7.2 Container & Layout

```html
<!-- Max-width container (centered) -->
<div class="container mx-auto px-4 max-w-7xl">
  <!-- Content stays within 1280px -->
</div>

<!-- Responsive grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <!-- 1 column on mobile, 2 on tablet, 3 on desktop -->
</div>
```

---

### 8. **Component Library**

#### 8.1 Buttons

```html
<!-- Primary button -->
<button class="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 focus:ring-2 focus:ring-brand-500">
  Primary Action
</button>

<!-- Secondary button -->
<button class="px-4 py-2 bg-gray-100 text-gray-900 rounded-lg hover:bg-gray-200">
  Secondary Action
</button>

<!-- Danger button -->
<button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
  Delete
</button>
```

#### 8.2 Priority Badges

```html
<!-- Critical -->
<span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium bg-priority-critical-light text-priority-critical">
  CRITICAL
</span>

<!-- High -->
<span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium bg-priority-high-light text-priority-high">
  HIGH
</span>

<!-- Medium -->
<span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium bg-priority-medium-light text-priority-medium">
  MEDIUM
</span>

<!-- Low -->
<span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium bg-priority-low-light text-priority-low">
  LOW
</span>
```

#### 8.3 Service Request Card

```html
<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
  <!-- Header with priority badge -->
  <div class="flex items-start justify-between">
    <h3 class="text-lg font-medium text-gray-900">
      Medical Emergency - Injured Person
    </h3>
    <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-priority-critical-light text-priority-critical">
      CRITICAL
    </span>
  </div>
  
  <!-- Description -->
  <p class="mt-2 text-sm text-gray-600">
    Person fell from height, bleeding, needs immediate medical attention.
  </p>
  
  <!-- Location -->
  <div class="mt-4 flex items-center text-sm text-gray-500">
    <svg class="w-4 h-4 mr-1">...</svg>
    Chennai, Tamil Nadu
  </div>
  
  <!-- Timestamp -->
  <div class="mt-2 text-xs text-gray-500">
    Submitted 45 minutes ago
  </div>
  
  <!-- Action button -->
  <button class="mt-4 w-full px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700">
    Accept Request
  </button>
</div>
```

---

### 9. **Responsive Design**

#### 9.1 Mobile-First Approach

**Mobile-first** = Design for phones first, then add features for larger screens

```html
<!-- Stack on mobile, side-by-side on desktop -->
<div class="flex flex-col md:flex-row gap-4">
  <div class="w-full md:w-1/2">Left content</div>
  <div class="w-full md:w-1/2">Right content</div>
</div>

<!-- Small text on mobile, larger on desktop -->
<h1 class="text-2xl md:text-3xl lg:text-4xl font-bold">
  Responsive Heading
</h1>
```

#### 9.2 Breakpoints

| Breakpoint | Width | Device |
|------------|-------|--------|
| `(default)` | < 640px | Mobile |
| `sm:` | ≥ 640px | Large mobile |
| `md:` | ≥ 768px | Tablet |
| `lg:` | ≥ 1024px | Desktop |
| `xl:` | ≥ 1280px | Large desktop |

---

### 10. **Implementation Guide**

#### 10.1 Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        brand: {/* as defined above */},
        priority: {/* as defined above */},
        status: {/* as defined above */},
      },
    },
  },
};
```

#### 10.2 Quick Start Checklist

- [ ] Install Tailwind CSS
- [ ] Configure custom colors
- [ ] Set up Inter font
- [ ] Create reusable components
- [ ] Test with screen readers
- [ ] Verify color contrast (use WebAIM tool)
- [ ] Test keyboard navigation
- [ ] Test on mobile devices

---

### ✅ **Design System Summary**

**Created**:
- ✅ Complete color palette (brand, priority, status)
- ✅ Color theory explained for novices
- ✅ WCAG 2.1 Level AA accessibility
- ✅ Typography system
- ✅ Visual hierarchy fundamentals
- ✅ Spacing system
- ✅ Component library
- ✅ Responsive patterns

**Novice-Friendly Features**:
- ✅ Every concept explained simply
- ✅ Real-world examples
- ✅ "Why" explained for every choice
- ✅ Visual comparisons (good vs bad)
- ✅ Copy-paste ready code

---

### 📖 **What's Next?**

**To implement frontend**:
→ [24-FRONTEND-IMPLEMENTATION.md](24-FRONTEND-IMPLEMENTATION.md) - Build the UI

**To understand architecture**:
→ [11-ARCHITECTURE-DECISIONS.md](11-ARCHITECTURE-DECISIONS.md) - Why these choices

**To see technical details**:
→ [21-TECHNICAL-DESIGN.md](21-TECHNICAL-DESIGN.md) - Implementation patterns

---

**Document Information**  
**Version**: 3.0 Consolidated  
**Created**: May 15, 2026  
**Part of**: IDRM Consolidated Documentation Suite  
**Previous**: [11-ARCHITECTURE-DECISIONS.md](11-ARCHITECTURE-DECISIONS.md)  
**Next**: [24-FRONTEND-IMPLEMENTATION.md](24-FRONTEND-IMPLEMENTATION.md)  
**Feedback**: Open an issue or submit a PR on GitHub

---

## IDRM Design System v3.0

### Visual Language for Disaster Response - Multi-Platform Edition

**Version**: 3.0  
**Last Updated**: May 24, 2026  
**Status**: Multi-Platform Design System  
**Platforms**: HTML/Tailwind (Web) + React SPA (Admin) + React Native (Mobile)

> **Philosophy**: Clear, urgent, accessible. Design for crisis, optimize for speed across **all platforms**.

---

### 🎯 What's New in v3.0

#### Three Frontend Interfaces Support

IDRM v3.0 design system supports **three distinct frontend platforms**:

1. **HTML/Tailwind (Primary Web)** - Main citizen-facing interface
   - Lightweight, fast-loading
   - Progressive enhancement
   - Works on any device
   - Target: General public, emergency situations

2. **React SPA (Advanced Web)** - Admin and advanced features
   - Rich interactions
   - Complex data visualizations
   - Advanced form handling
   - Target: Administrators, coordinators, analysts

3. **React Native (Mobile Apps)** - iOS and Android native apps
   - Native performance
   - Offline-first capability
   - Location services integration
   - Target: Field workers, responders, mobile-first users

---

### 📱 Platform-Specific Approach

#### When to Use Which Platform

```
┌─────────────────────────────────────────────────────────┐
│  Use Case                     Platform                  │
├─────────────────────────────────────────────────────────┤
│  Citizen requests help        HTML/Tailwind             │
│  Quick status check           HTML/Tailwind             │
│  View service map             HTML/Tailwind or RN       │
│  Submit service request       HTML/Tailwind or RN       │
│  ─────────────────────────────────────────────────────  │
│  Admin dashboard              React SPA                 │
│  Analytics & reports          React SPA                 │
│  User management              React SPA                 │
│  Complex workflows            React SPA                 │
│  ─────────────────────────────────────────────────────  │
│  Field worker updates         React Native              │
│  Offline service delivery     React Native              │
│  GPS location tracking        React Native              │
│  Push notifications           React Native              │
└─────────────────────────────────────────────────────────┘
```

---

### Design Principles

#### 1. **Urgency Without Panic**
- Use color to convey priority without causing alarm
- Critical information prominent but not overwhelming
- Progressive disclosure: show essentials first
- **Platform adaptation**: 
  - Web: Subtle animations, clear hierarchy
  - Mobile: Haptic feedback, larger touch targets

#### 2. **Clarity Under Stress**
- High contrast, readable typography
- Clear visual hierarchy
- Minimal cognitive load
- One primary action per screen
- **Platform adaptation**:
  - Web: Keyboard shortcuts, breadcrumbs
  - Mobile: Thumb-zone optimization, gesture hints

#### 3. **Accessibility First**
- WCAG 2.1 AA compliant minimum (AAA target)
- Color-blind safe palette
- Screen reader friendly
- Keyboard navigable (web), VoiceOver/TalkBack (mobile)
- **Platform adaptation**:
  - Web: Focus indicators, skip links
  - Mobile: Dynamic type, reduced motion support

#### 4. **Mobile-First Reality**
- Most disaster response happens on phones
- Touch targets ≥ 44px (iOS/Android HIG)
- Works on slow connections (3G)
- Offline-capable
- **Platform adaptation**:
  - Web: Responsive down to 320px
  - Mobile: Native platform controls

---

### Color System

#### Primary Palette

```javascript
// tailwind.config.js (Web)
// Also exported as JS/TS for React SPA
// Converted to React Native StyleSheet

module.exports = {
  theme: {
    extend: {
      colors: {
        // Brand Colors
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',  // Primary brand
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        
        // Priority Colors (Service Urgency)
        priority: {
          critical: {
            light: '#fee2e2',    // bg
            DEFAULT: '#dc2626',  // text/border
            dark: '#991b1b',     // hover
          },
          high: {
            light: '#fed7aa',
            DEFAULT: '#ea580c',
            dark: '#c2410c',
          },
          medium: {
            light: '#fef3c7',
            DEFAULT: '#f59e0b',
            dark: '#d97706',
          },
          low: {
            light: '#dbeafe',
            DEFAULT: '#3b82f6',
            dark: '#1e40af',
          },
        },
        
        // Status Colors (Service Status)
        status: {
          submitted: {
            light: '#e0e7ff',
            DEFAULT: '#6366f1',
            dark: '#4338ca',
          },
          approved: {
            light: '#dbeafe',
            DEFAULT: '#2563eb',
            dark: '#1e40af',
          },
          assigned: {
            light: '#fef3c7',
            DEFAULT: '#f59e0b',
            dark: '#d97706',
          },
          'in-progress': {
            light: '#fef3c7',
            DEFAULT: '#f59e0b',
            dark: '#d97706',
          },
          completed: {
            light: '#d1fae5',
            DEFAULT: '#10b981',
            dark: '#059669',
          },
          verified: {
            light: '#d1fae5',
            DEFAULT: '#059669',
            dark: '#047857',
          },
          rejected: {
            light: '#fee2e2',
            DEFAULT: '#ef4444',
            dark: '#dc2626',
          },
          cancelled: {
            light: '#f3f4f6',
            DEFAULT: '#6b7280',
            dark: '#4b5563',
          },
        },
        
        // Service Type Colors
        service: {
          medical: '#ef4444',      // Red
          food: '#f59e0b',         // Orange
          shelter: '#8b5cf6',      // Purple
          rescue: '#dc2626',       // Dark red
          water: '#3b82f6',        // Blue
          clothing: '#06b6d4',     // Cyan
          transport: '#84cc16',    // Lime
          other: '#6b7280',        // Gray
        },
        
        // Neutral Colors (Extended)
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
        },
        
        // Semantic Colors
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6',
      }
    }
  }
}
```

#### React Native Color Tokens

```typescript
// design-tokens/colors.ts (React Native)
export const Colors = {
  brand: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    200: '#bae6fd',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9',
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e',
  },
  
  priority: {
    critical: {
      light: '#fee2e2',
      default: '#dc2626',
      dark: '#991b1b',
    },
    high: {
      light: '#fed7aa',
      default: '#ea580c',
      dark: '#c2410c',
    },
    medium: {
      light: '#fef3c7',
      default: '#f59e0b',
      dark: '#d97706',
    },
    low: {
      light: '#dbeafe',
      default: '#3b82f6',
      dark: '#1e40af',
    },
  },
  
  // ... same structure as web
  
  // Platform-specific additions
  system: {
    background: '#ffffff',
    backgroundSecondary: '#f5f5f5',
    label: '#000000',
    secondaryLabel: '#737373',
    tertiaryLabel: '#a3a3a3',
    separator: '#e5e5e5',
  },
};
```

#### Color Usage Guidelines

##### Priority Colors

**HTML/Tailwind**:
```html
<!-- Critical: Medical emergency, immediate rescue -->
<div class="bg-priority-critical-light border-l-4 border-priority-critical">
  <span class="text-priority-critical font-semibold">CRITICAL</span>
</div>

<!-- High: Urgent food, shelter needed -->
<div class="bg-priority-high-light border-l-4 border-priority-high">
  <span class="text-priority-high font-semibold">HIGH</span>
</div>
```

**React SPA**:
```tsx
// Using CSS-in-JS or styled-components
import { colors } from '@/design-tokens';

const CriticalBadge = styled.div`
  background-color: ${colors.priority.critical.light};
  border-left: 4px solid ${colors.priority.critical.default};
  padding: 1rem;
`;
```

**React Native**:
```tsx
import { Colors } from '@/design-tokens/colors';
import { View, Text, StyleSheet } from 'react-native';

const CriticalBadge = () => (
  <View style={styles.critical}>
    <Text style={styles.criticalText}>CRITICAL</Text>
  </View>
);

const styles = StyleSheet.create({
  critical: {
    backgroundColor: Colors.priority.critical.light,
    borderLeftWidth: 4,
    borderLeftColor: Colors.priority.critical.default,
    padding: 16,
  },
  criticalText: {
    color: Colors.priority.critical.default,
    fontWeight: '600',
  },
});
```

---

### Typography

#### Font Stack

**HTML/Tailwind**:
```javascript
// tailwind.config.js
theme: {
  extend: {
    fontFamily: {
      sans: [
        'Inter',
        'system-ui',
        '-apple-system',
        'BlinkMacSystemFont',
        'Segoe UI',
        'Roboto',
        'sans-serif',
      ],
      mono: [
        'JetBrains Mono',
        'Monaco',
        'Courier New',
        'monospace',
      ],
    },
    fontSize: {
      '2xs': ['0.625rem', { lineHeight: '0.875rem' }],  // 10px
      'xs': ['0.75rem', { lineHeight: '1rem' }],        // 12px
      'sm': ['0.875rem', { lineHeight: '1.25rem' }],    // 14px
      'base': ['1rem', { lineHeight: '1.5rem' }],       // 16px
      'lg': ['1.125rem', { lineHeight: '1.75rem' }],    // 18px
      'xl': ['1.25rem', { lineHeight: '1.75rem' }],     // 20px
      '2xl': ['1.5rem', { lineHeight: '2rem' }],        // 24px
      '3xl': ['1.875rem', { lineHeight: '2.25rem' }],   // 30px
      '4xl': ['2.25rem', { lineHeight: '2.5rem' }],     // 36px
      '5xl': ['3rem', { lineHeight: '1' }],             // 48px
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      extrabold: '800',
    },
  }
}
```

**React Native Typography**:
```typescript
// design-tokens/typography.ts
export const Typography = {
  fontSize: {
    '2xs': 10,
    'xs': 12,
    'sm': 14,
    'base': 16,
    'lg': 18,
    'xl': 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
    '5xl': 48,
  },
  
  fontWeight: {
    normal: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
    extrabold: '800' as const,
  },
  
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
  
  // Platform-specific font families
  fontFamily: {
    ios: {
      regular: 'System',
      medium: 'System',
      semibold: 'System',
      bold: 'System',
    },
    android: {
      regular: 'Roboto',
      medium: 'Roboto-Medium',
      semibold: 'Roboto-Medium',
      bold: 'Roboto-Bold',
    },
  },
};
```

#### Typography Scale Examples

**HTML/Tailwind**:
```html
<!-- Hero / Page Titles -->
<h1 class="text-4xl md:text-5xl font-bold text-neutral-900">
  Disaster Response Dashboard
</h1>

<!-- Section Headings -->
<h2 class="text-2xl md:text-3xl font-semibold text-neutral-900">
  Active Service Requests
</h2>

<!-- Body Text -->
<p class="text-base text-neutral-700">
  Regular paragraph text with good readability.
</p>
```

**React Native**:
```tsx
import { Text, StyleSheet } from 'react-native';
import { Typography, Colors } from '@/design-tokens';

<Text style={styles.h1}>Disaster Response Dashboard</Text>
<Text style={styles.h2}>Active Service Requests</Text>
<Text style={styles.body}>Regular paragraph text with good readability.</Text>

const styles = StyleSheet.create({
  h1: {
    fontSize: Typography.fontSize['4xl'],
    fontWeight: Typography.fontWeight.bold,
    color: Colors.neutral[900],
  },
  h2: {
    fontSize: Typography.fontSize['2xl'],
    fontWeight: Typography.fontWeight.semibold,
    color: Colors.neutral[900],
  },
  body: {
    fontSize: Typography.fontSize.base,
    color: Colors.neutral[700],
    lineHeight: Typography.fontSize.base * Typography.lineHeight.normal,
  },
});
```

---

### Spacing System

#### Base Spacing Scale

```javascript
// Consistent across all platforms
const spacing = {
  '0': 0,
  '0.5': 2,     // 2px / 2dp
  '1': 4,       // 4px / 4dp
  '2': 8,       // 8px / 8dp
  '3': 12,      // 12px / 12dp
  '4': 16,      // 16px / 16dp
  '5': 20,      // 20px / 20dp
  '6': 24,      // 24px / 24dp
  '8': 32,      // 32px / 32dp
  '10': 40,     // 40px / 40dp
  '12': 48,     // 48px / 48dp
  '16': 64,     // 64px / 64dp
  '20': 80,     // 80px / 80dp
  '24': 96,     // 96px / 96dp
}
```

**HTML/Tailwind**:
```html
<div class="p-4 md:p-6">        <!-- Padding inside cards -->
  <div class="space-y-4">       <!-- Vertical spacing between elements -->
    <!-- Content -->
  </div>
</div>
```

**React Native**:
```tsx
const styles = StyleSheet.create({
  card: {
    padding: 16,  // spacing[4]
  },
  stack: {
    gap: 16,      // spacing[4] - React Native 0.71+
  },
});
```

---

### 📱 Mobile-Specific Design Tokens (NEW in v3)

#### Touch Targets

```typescript
// design-tokens/touch.ts
export const TouchTargets = {
  // Minimum touch target sizes (iOS HIG / Material Design)
  minimum: {
    width: 44,   // iOS minimum
    height: 44,
  },
  recommended: {
    width: 48,   // Material Design recommended
    height: 48,
  },
  comfortable: {
    width: 56,   // Large, easy to tap
    height: 56,
  },
  
  // Interactive element sizing
  button: {
    small: { height: 32, paddingHorizontal: 12 },
    medium: { height: 44, paddingHorizontal: 16 },
    large: { height: 56, paddingHorizontal: 24 },
  },
  
  // Form inputs
  input: {
    height: 48,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
};
```

#### Safe Area Insets

```typescript
// design-tokens/safe-area.ts
import { useSafeAreaInsets } from 'react-native-safe-area-context';

export const SafeAreaLayout = () => {
  const insets = useSafeAreaInsets();
  
  return {
    paddingTop: insets.top,
    paddingBottom: insets.bottom,
    paddingLeft: insets.left,
    paddingRight: insets.right,
  };
};
```

#### Platform-Specific Elevations

```typescript
// design-tokens/elevation.ts
import { Platform, ViewStyle } from 'react-native';

export const Elevation = {
  // iOS shadows
  ios: {
    small: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
    },
    medium: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 8,
    },
    large: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.2,
      shadowRadius: 16,
    },
  },
  
  // Android elevation
  android: {
    small: { elevation: 2 },
    medium: { elevation: 4 },
    large: { elevation: 8 },
  },
  
  // Cross-platform helper
  get: (size: 'small' | 'medium' | 'large'): ViewStyle => {
    return Platform.select({
      ios: Elevation.ios[size],
      android: Elevation.android[size],
      default: {},
    });
  },
};
```

---

### 🎨 Component Library - Multi-Platform

#### Component Mapping Table

| Component | HTML/Tailwind | React SPA | React Native | Notes |
|-----------|---------------|-----------|--------------|-------|
| **Buttons** | ✅ Native | ✅ Shared | ✅ Touchable | Same visual style |
| **Cards** | ✅ Divs | ✅ Shared | ✅ View | Same layout |
| **Forms** | ✅ Native | ✅ Controlled | ✅ TextInput | Different APIs |
| **Alerts** | ✅ Divs | ✅ Portal | ✅ Modal/Toast | Platform UX |
| **Badges** | ✅ Spans | ✅ Shared | ✅ Text | Same style |
| **Navigation** | ✅ Links | ✅ Router | ✅ Navigator | Different paradigms |
| **Tables** | ✅ Native | ✅ Library | ✅ FlatList | RN: List-based |
| **Modals** | ✅ Dialog | ✅ Portal | ✅ Modal | Platform UX |
| **Maps** | ✅ Leaflet | ✅ Leaflet | ✅ react-native-maps | Different libraries |
| **Tabs** | ✅ Manual | ✅ Headless UI | ✅ Tab Navigator | Platform navigation |

---

#### 1. Buttons

**HTML/Tailwind**:
```html
<!-- Primary Button -->
<button class="inline-flex items-center px-4 py-2 border border-transparent 
               text-sm font-medium rounded-lg text-white bg-brand-600 
               hover:bg-brand-700 focus:outline-none focus:ring-2 
               focus:ring-offset-2 focus:ring-brand-500
               transition-colors duration-200">
  Create Request
</button>

<!-- Secondary Button -->
<button class="inline-flex items-center px-4 py-2 border border-neutral-300 
               text-sm font-medium rounded-lg text-neutral-700 bg-white 
               hover:bg-neutral-50 focus:outline-none focus:ring-2 
               focus:ring-offset-2 focus:ring-brand-500
               transition-colors duration-200">
  Cancel
</button>

<!-- Danger Button -->
<button class="inline-flex items-center px-4 py-2 border border-transparent 
               text-sm font-medium rounded-lg text-white bg-error 
               hover:bg-red-700 focus:outline-none focus:ring-2 
               focus:ring-offset-2 focus:ring-error
               transition-colors duration-200">
  Delete
</button>
```

**React SPA**:
```tsx
// components/Button.tsx
import { ButtonHTMLAttributes, ReactNode } from 'react';
import { clsx } from 'clsx';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  children: ReactNode;
}

export const Button = ({ 
  variant = 'primary', 
  size = 'medium',
  className,
  children,
  ...props 
}: ButtonProps) => {
  const baseClasses = 'inline-flex items-center border font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'border-transparent text-white bg-brand-600 hover:bg-brand-700 focus:ring-brand-500',
    secondary: 'border-neutral-300 text-neutral-700 bg-white hover:bg-neutral-50 focus:ring-brand-500',
    danger: 'border-transparent text-white bg-error hover:bg-red-700 focus:ring-error',
  };
  
  const sizeClasses = {
    small: 'px-3 py-1.5 text-xs',
    medium: 'px-4 py-2 text-sm',
    large: 'px-6 py-3 text-base',
  };
  
  return (
    <button 
      className={clsx(baseClasses, variantClasses[variant], sizeClasses[size], className)}
      {...props}
    >
      {children}
    </button>
  );
};

// Usage
<Button variant="primary">Create Request</Button>
<Button variant="secondary">Cancel</Button>
<Button variant="danger">Delete</Button>
```

**React Native**:
```tsx
// components/Button.tsx
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { Colors, Typography, TouchTargets } from '@/design-tokens';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  onPress: () => void;
  children: string;
  loading?: boolean;
  disabled?: boolean;
}

export const Button = ({ 
  variant = 'primary',
  size = 'medium',
  onPress,
  children,
  loading = false,
  disabled = false,
}: ButtonProps) => {
  const containerStyle = [
    styles.base,
    styles[`${variant}Container`],
    styles[`${size}Container`],
    disabled && styles.disabledContainer,
  ];
  
  const textStyle = [
    styles.text,
    styles[`${variant}Text`],
    styles[`${size}Text`],
    disabled && styles.disabledText,
  ];
  
  return (
    <TouchableOpacity
      style={containerStyle}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.7}
    >
      {loading ? (
        <ActivityIndicator color={variant === 'secondary' ? Colors.brand[600] : '#fff'} />
      ) : (
        <Text style={textStyle}>{children}</Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  base: {
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 8,
    minHeight: TouchTargets.button.medium.height,
  },
  
  // Variants
  primaryContainer: {
    backgroundColor: Colors.brand[600],
  },
  primaryText: {
    color: '#ffffff',
  },
  
  secondaryContainer: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: Colors.neutral[300],
  },
  secondaryText: {
    color: Colors.neutral[700],
  },
  
  dangerContainer: {
    backgroundColor: Colors.error,
  },
  dangerText: {
    color: '#ffffff',
  },
  
  // Sizes
  smallContainer: {
    paddingHorizontal: TouchTargets.button.small.paddingHorizontal,
    minHeight: TouchTargets.button.small.height,
  },
  smallText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: Typography.fontWeight.medium,
  },
  
  mediumContainer: {
    paddingHorizontal: TouchTargets.button.medium.paddingHorizontal,
    minHeight: TouchTargets.button.medium.height,
  },
  mediumText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.medium,
  },
  
  largeContainer: {
    paddingHorizontal: TouchTargets.button.large.paddingHorizontal,
    minHeight: TouchTargets.button.large.height,
  },
  largeText: {
    fontSize: Typography.fontSize.base,
    fontWeight: Typography.fontWeight.medium,
  },
  
  // States
  disabledContainer: {
    opacity: 0.5,
  },
  disabledText: {
    opacity: 0.5,
  },
  
  text: {
    textAlign: 'center',
  },
});

// Usage
<Button variant="primary" onPress={() => console.log('Create')}>
  Create Request
</Button>
<Button variant="secondary" onPress={() => console.log('Cancel')}>
  Cancel
</Button>
<Button variant="danger" onPress={() => console.log('Delete')}>
  Delete
</Button>
```

---

#### 2. Cards

**HTML/Tailwind**:
```html
<!-- Service Request Card -->
<div class="bg-white rounded-lg shadow-sm border-l-4 border-priority-high p-6">
  <div class="flex items-start justify-between">
    <div class="flex-1">
      <div class="flex items-center space-x-2 mb-2">
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-priority-high-light text-priority-high">
          HIGH PRIORITY
        </span>
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-status-submitted-light text-status-submitted">
          Submitted
        </span>
      </div>
      <h3 class="text-lg font-medium text-neutral-900 mb-1">
        Medical supplies needed
      </h3>
      <p class="text-sm text-neutral-600 mb-3">
        Urgent need for first aid kits and medicines at Relief Center Alpha.
      </p>
    </div>
  </div>
</div>
```

**React SPA**:
```tsx
// components/ServiceCard.tsx
interface ServiceCardProps {
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: string;
  title: string;
  description: string;
}

export const ServiceCard = ({ priority, status, title, description }: ServiceCardProps) => (
  <div className="bg-white rounded-lg shadow-sm border-l-4 border-priority-high p-6">
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <div className="flex items-center space-x-2 mb-2">
          <Badge variant="priority" level={priority} />
          <Badge variant="status" status={status} />
        </div>
        <h3 className="text-lg font-medium text-neutral-900 mb-1">{title}</h3>
        <p className="text-sm text-neutral-600 mb-3">{description}</p>
      </div>
    </div>
  </div>
);
```

**React Native**:
```tsx
// components/ServiceCard.tsx
import { View, Text, StyleSheet } from 'react-native';
import { Colors, Typography, Elevation } from '@/design-tokens';

interface ServiceCardProps {
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: string;
  title: string;
  description: string;
}

export const ServiceCard = ({ priority, status, title, description }: ServiceCardProps) => {
  const borderColor = Colors.priority[priority].default;
  
  return (
    <View style={[styles.card, { borderLeftColor: borderColor }]}>
      <View style={styles.badges}>
        <Badge variant="priority" level={priority} />
        <Badge variant="status" status={status} />
      </View>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.description}>{description}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 24,
    borderLeftWidth: 4,
    ...Elevation.get('small'),
  },
  badges: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 8,
  },
  title: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.neutral[900],
    marginBottom: 4,
  },
  description: {
    fontSize: Typography.fontSize.sm,
    color: Colors.neutral[600],
    lineHeight: Typography.fontSize.sm * 1.5,
  },
});
```

---

#### 3. Forms

**HTML/Tailwind**:
```html
<!-- Text Input -->
<div class="space-y-1">
  <label for="name" class="block text-sm font-medium text-neutral-700">
    Full Name
  </label>
  <input
    type="text"
    id="name"
    class="block w-full px-3 py-2 border border-neutral-300 rounded-lg 
           text-neutral-900 placeholder-neutral-400
           focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent
           transition-shadow duration-200"
    placeholder="Enter your full name"
  />
</div>
```

**React SPA**:
```tsx
// components/Input.tsx
interface InputProps {
  label: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
}

export const Input = ({ label, placeholder, value, onChange, error }: InputProps) => (
  <div className="space-y-1">
    <label className="block text-sm font-medium text-neutral-700">
      {label}
    </label>
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className={clsx(
        "block w-full px-3 py-2 border rounded-lg",
        "text-neutral-900 placeholder-neutral-400",
        "focus:outline-none focus:ring-2 transition-shadow duration-200",
        error 
          ? "border-error focus:ring-error focus:border-transparent"
          : "border-neutral-300 focus:ring-brand-500 focus:border-transparent"
      )}
    />
    {error && <p className="text-sm text-error">{error}</p>}
  </div>
);
```

**React Native**:
```tsx
// components/Input.tsx
import { View, Text, TextInput, StyleSheet } from 'react-native';
import { Colors, Typography, TouchTargets } from '@/design-tokens';

interface InputProps {
  label: string;
  placeholder?: string;
  value: string;
  onChangeText: (text: string) => void;
  error?: string;
}

export const Input = ({ label, placeholder, value, onChangeText, error }: InputProps) => (
  <View style={styles.container}>
    <Text style={styles.label}>{label}</Text>
    <TextInput
      value={value}
      onChangeText={onChangeText}
      placeholder={placeholder}
      placeholderTextColor={Colors.neutral[400]}
      style={[styles.input, error && styles.inputError]}
    />
    {error && <Text style={styles.error}>{error}</Text>}
  </View>
);

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    fontSize: Typography.fontSize.sm,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.neutral[700],
    marginBottom: 4,
  },
  input: {
    height: TouchTargets.input.height,
    paddingHorizontal: TouchTargets.input.paddingHorizontal,
    paddingVertical: TouchTargets.input.paddingVertical,
    borderWidth: 1,
    borderColor: Colors.neutral[300],
    borderRadius: 8,
    fontSize: Typography.fontSize.base,
    color: Colors.neutral[900],
    backgroundColor: '#ffffff',
  },
  inputError: {
    borderColor: Colors.error,
  },
  error: {
    fontSize: Typography.fontSize.sm,
    color: Colors.error,
    marginTop: 4,
  },
});
```

---

#### 4. Alerts & Notifications

**HTML/Tailwind**:
```html
<!-- Success Alert -->
<div class="bg-success/10 border-l-4 border-success rounded-r-lg p-4">
  <div class="flex items-start">
    <svg class="w-5 h-5 text-success flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
    </svg>
    <div class="ml-3">
      <h3 class="text-sm font-medium text-success">Success</h3>
      <p class="text-sm text-neutral-700 mt-1">Service request submitted successfully.</p>
    </div>
  </div>
</div>
```

**React Native** (Using react-native-toast-message):
```tsx
// utils/toast.ts
import Toast from 'react-native-toast-message';
import { Colors } from '@/design-tokens';

export const showToast = {
  success: (message: string) => {
    Toast.show({
      type: 'success',
      text1: 'Success',
      text2: message,
      position: 'top',
      visibilityTime: 3000,
    });
  },
  
  error: (message: string) => {
    Toast.show({
      type: 'error',
      text1: 'Error',
      text2: message,
      position: 'top',
      visibilityTime: 4000,
    });
  },
  
  warning: (message: string) => {
    Toast.show({
      type: 'info',
      text1: 'Warning',
      text2: message,
      position: 'top',
      visibilityTime: 3500,
    });
  },
};

// Usage
showToast.success('Service request submitted successfully');
```

---

### 🌐 Responsive Breakpoints

#### Breakpoint System

```javascript
// Tailwind breakpoints (web)
const breakpoints = {
  'sm': '640px',   // Mobile landscape
  'md': '768px',   // Tablet
  'lg': '1024px',  // Desktop
  'xl': '1280px',  // Large desktop
  '2xl': '1536px', // Extra large
};

// React Native breakpoints (using react-native-responsive-screen)
import { widthPercentageToDP as wp } from 'react-native-responsive-screen';

const mobileBreakpoints = {
  small: wp('100%') < 375,   // Small phones
  medium: wp('100%') >= 375 && wp('100%') < 768,  // Standard phones
  tablet: wp('100%') >= 768,  // Tablets
};
```

#### Responsive Usage

**HTML/Tailwind**:
```html
<!-- Responsive grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
  <!-- Cards -->
</div>

<!-- Responsive padding -->
<div class="p-4 md:p-6 lg:p-8">
  <!-- Content -->
</div>

<!-- Responsive text -->
<h1 class="text-2xl md:text-3xl lg:text-4xl font-bold">
  Title
</h1>
```

**React Native** (using useWindowDimensions):
```tsx
import { useWindowDimensions, StyleSheet } from 'react-native';

const MyComponent = () => {
  const { width } = useWindowDimensions();
  const isTablet = width >= 768;
  
  return (
    <View style={isTablet ? styles.tabletContainer : styles.phoneContainer}>
      {/* Content */}
    </View>
  );
};

const styles = StyleSheet.create({
  phoneContainer: {
    padding: 16,
  },
  tabletContainer: {
    padding: 32,
  },
});
```

---

### ♿ Accessibility Guidelines

#### WCAG 2.1 Compliance

All three platforms must meet **WCAG 2.1 AA minimum**, targeting **AAA** where possible.

##### Color Contrast

**Minimum Requirements**:
- Normal text: 4.5:1 contrast ratio
- Large text (18pt+): 3:1 contrast ratio
- UI components: 3:1 contrast ratio

**HTML/Tailwind**:
```html
<!-- Good contrast -->
<p class="text-neutral-900 bg-white">High contrast text</p>

<!-- Bad contrast (avoid) -->
<p class="text-neutral-400 bg-white">Low contrast text</p>
```

**React Native**:
```tsx
// Use Colors from design tokens (pre-validated for contrast)
<Text style={{ color: Colors.neutral[900], backgroundColor: '#ffffff' }}>
  High contrast text
</Text>
```

##### Screen Reader Support

**HTML/Tailwind**:
```html
<!-- Accessible button -->
<button aria-label="Create service request" class="...">
  <svg aria-hidden="true" class="...">...</svg>
  Create
</button>

<!-- Skip to main content -->
<a href="#main-content" class="sr-only focus:not-sr-only">
  Skip to main content
</a>
```

**React Native**:
```tsx
// Accessible button
<TouchableOpacity
  accessible={true}
  accessibilityLabel="Create service request"
  accessibilityRole="button"
  accessibilityHint="Opens form to create a new service request"
>
  <Text>Create</Text>
</TouchableOpacity>

// Accessible image
<Image
  source={logo}
  accessible={true}
  accessibilityLabel="IDRM logo"
/>
```

##### Keyboard Navigation (Web)

```html
<!-- Tab order -->
<div class="space-y-2">
  <button tabindex="0" class="...">First</button>
  <button tabindex="0" class="...">Second</button>
  <button tabindex="0" class="...">Third</button>
</div>

<!-- Focus indicators -->
<button class="focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2">
  Visible focus
</button>
```

---

### 🗺️ Map Styling (Cross-Platform)

#### Marker Colors & Sizes

```javascript
// Shared across all platforms
const serviceColors = {
  medical: '#ef4444',    // red
  food: '#f59e0b',       // orange
  shelter: '#8b5cf6',    // purple
  rescue: '#dc2626',     // dark red
  water: '#3b82f6',      // blue
  clothing: '#06b6d4',   // cyan
  transport: '#84cc16',  // lime
  other: '#6b7280'       // gray
};

const prioritySizes = {
  critical: 16,  // Largest
  high: 12,
  medium: 10,
  low: 8        // Smallest
};
```

**HTML/Tailwind (Leaflet)**:
```javascript
// Create custom icon
const createMarkerIcon = (serviceType, priority) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div class="marker-pin" style="
        background-color: ${serviceColors[serviceType]};
        width: ${prioritySizes[priority]}px;
        height: ${prioritySizes[priority]}px;
      "></div>
    `,
  });
};
```

**React Native (react-native-maps)**:
```tsx
import MapView, { Marker } from 'react-native-maps';
import { Colors } from '@/design-tokens';

<MapView style={styles.map}>
  <Marker
    coordinate={{ latitude: 19.0760, longitude: 72.8777 }}
    pinColor={Colors.service.medical}
  >
    <View style={[styles.marker, { 
      backgroundColor: Colors.service.medical,
      width: prioritySizes.critical,
      height: prioritySizes.critical,
    }]} />
  </Marker>
</MapView>
```

---

### 📦 Design Token Export

#### JavaScript/TypeScript Export

```typescript
// design-tokens/index.ts
export const designTokens = {
  colors: {
    brand: { /* ... */ },
    priority: { /* ... */ },
    status: { /* ... */ },
    service: { /* ... */ },
    neutral: { /* ... */ },
  },
  
  typography: {
    fontFamily: { /* ... */ },
    fontSize: { /* ... */ },
    fontWeight: { /* ... */ },
    lineHeight: { /* ... */ },
  },
  
  spacing: { /* ... */ },
  
  borderRadius: {
    sm: 4,
    DEFAULT: 8,
    lg: 12,
    xl: 16,
    full: 9999,
  },
  
  shadow: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    DEFAULT: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },
  
  // Platform-specific tokens
  mobile: {
    touchTargets: { /* ... */ },
    safeArea: { /* ... */ },
    elevation: { /* ... */ },
  },
};

// Type-safe exports
export type DesignTokens = typeof designTokens;
export type ColorScale = keyof typeof designTokens.colors.brand;
export type FontSize = keyof typeof designTokens.typography.fontSize;
```

---

### 🎯 Platform-Specific Implementation Notes

#### HTML/Tailwind (Primary Web)
- **Target**: General public, works everywhere
- **Approach**: Progressive enhancement
- **Features**: Server-rendered, works without JS
- **Testing**: Chrome, Firefox, Safari, Edge (last 2 versions)

#### React SPA (Admin Web)
- **Target**: Administrators, coordinators
- **Approach**: Rich client-side app
- **Features**: Complex interactions, data visualizations
- **Testing**: Desktop browsers primarily

#### React Native (Mobile)
- **Target**: Field workers, mobile-first users
- **Approach**: Native performance
- **Features**: Offline-first, GPS, push notifications
- **Testing**: iOS 14+, Android 10+

---

### ✅ Cross-Platform Checklist

Before implementing any component:

- [ ] Design works on all three platforms
- [ ] Color tokens consistent across platforms
- [ ] Typography scales appropriately
- [ ] Touch targets ≥ 44px on mobile
- [ ] Accessibility tested (screen readers, keyboard)
- [ ] Dark mode considered (future)
- [ ] Offline behavior defined (mobile)
- [ ] Performance validated
- [ ] Responsive at all breakpoints

---

### 📚 Additional Resources

#### Documentation
- [Tailwind CSS Docs](https://tailwindcss.com)
- [React Native Docs](https://reactnative.dev)
- [iOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design Guidelines](https://material.io/design)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

#### Tools
- **Color Contrast**: WebAIM Contrast Checker
- **Accessibility**: axe DevTools, Lighthouse
- **React Native**: React Native Debugger, Flipper
- **Design**: Figma, Sketch

---

**Version History**:
- **v3.0** (May 24, 2026): Added three frontend platform support, mobile design tokens
- **v2.0** (May 10, 2026): Updated to match v2 architecture
- **v1.0** (Earlier): Initial design system

---

**IDRM Design System v3.0 - One Design Language, Three Platforms** 🎨📱💻
