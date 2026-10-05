> *Type: Document (specification) · Audience: Designers, frontend devs · Status: Archived — v2 historical generation*

# IDRM Design System

<!-- IDRM-CLEANUP doc=v2-60-designsystem status=ANNOTATED pass=2026-08-16 -->
> ## 🗺️ SECTION MAP (annotation pass, 2026-08-16)
> Gen-2 design system (color/type/spacing/components/tokens). Current UI source of truth =
> [`../../../../docs/mvp/60-uidesign-web-interaction.md`](../../../../docs/mvp/60-uidesign-web-interaction.md)
> (HTML+Tailwind, WCAG 2.2 AA). Design-token/color/type/spacing/components/map-styling/responsive/a11y all map
> there (⚠ MVP — Tailwind expresses these; v2 specifics not normative). A mature design-token system is an FFP
> refinement. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

## Visual Language for Disaster Response

> **Philosophy**: Clear, urgent, accessible. Design for crisis, optimize for speed.

---

## Design Principles

### 1. **Urgency Without Panic**

- Use color to convey priority without causing alarm
- Critical information prominent but not overwhelming
- Progressive disclosure: show essentials first

### 2. **Clarity Under Stress**

- High contrast, readable typography
- Clear visual hierarchy
- Minimal cognitive load
- One primary action per screen

### 3. **Accessibility First**

- WCAG 2.1 AA compliant minimum
- Color-blind safe palette
- Screen reader friendly
- Keyboard navigable

### 4. **Mobile-First Reality**

- Most disaster response happens on phones
- Touch targets ≥ 44px
- Works on slow connections
- Offline-capable

---

## Color System

### Primary Palette

```javascript
// tailwind.config.js
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

### Color Usage Guidelines

#### Priority Colors

```html
<!-- Critical: Medical emergency, immediate rescue -->
<div class="bg-priority-critical-light border-l-4 border-priority-critical">
  <span class="text-priority-critical font-semibold">CRITICAL</span>
</div>

<!-- High: Urgent food, shelter needed -->
<div class="bg-priority-high-light border-l-4 border-priority-high">
  <span class="text-priority-high font-semibold">HIGH</span>
</div>

<!-- Medium: Non-urgent supplies -->
<div class="bg-priority-medium-light border-l-4 border-priority-medium">
  <span class="text-priority-medium font-semibold">MEDIUM</span>
</div>

<!-- Low: Information requests -->
<div class="bg-priority-low-light border-l-4 border-priority-low">
  <span class="text-priority-low font-semibold">LOW</span>
</div>
```

#### Status Colors

```html
<!-- Submitted -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-status-submitted-light text-status-submitted">
  Submitted
</span>

<!-- In Progress -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-status-in-progress-light text-status-in-progress">
  In Progress
</span>

<!-- Completed -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-status-completed-light text-status-completed">
  Completed
</span>
```

---

## Typography

### Font Stack

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

### Typography Scale

```html
<!-- Hero / Page Titles -->
<h1 class="text-4xl md:text-5xl font-bold text-neutral-900">
  Disaster Response Dashboard
</h1>

<!-- Section Headings -->
<h2 class="text-2xl md:text-3xl font-semibold text-neutral-900">
  Active Service Requests
</h2>

<!-- Subsection Headings -->
<h3 class="text-xl font-semibold text-neutral-800">
  Medical Services
</h3>

<!-- Card/Component Titles -->
<h4 class="text-lg font-medium text-neutral-800">
  Request Details
</h4>

<!-- Body Text -->
<p class="text-base text-neutral-700">
  Regular paragraph text with good readability.
</p>

<!-- Small Text / Metadata -->
<p class="text-sm text-neutral-600">
  Created 2 hours ago by John Doe
</p>

<!-- Captions / Helper Text -->
<p class="text-xs text-neutral-500">
  Optional helper text or footnotes
</p>
```

---

## Spacing System

```javascript
// Consistent spacing scale
const spacing = {
  '0': '0px',
  '0.5': '0.125rem',  // 2px
  '1': '0.25rem',     // 4px
  '2': '0.5rem',      // 8px
  '3': '0.75rem',     // 12px
  '4': '1rem',        // 16px
  '5': '1.25rem',     // 20px
  '6': '1.5rem',      // 24px
  '8': '2rem',        // 32px
  '10': '2.5rem',     // 40px
  '12': '3rem',       // 48px
  '16': '4rem',       // 64px
  '20': '5rem',       // 80px
  '24': '6rem',       // 96px
}
```

### Spacing Guidelines

```html
<!-- Component Internal Spacing -->
<div class="p-4 md:p-6">        <!-- Padding inside cards -->
  <div class="space-y-4">       <!-- Vertical spacing between elements -->
    <!-- Content -->
  </div>
</div>

<!-- Stack Layout -->
<div class="space-y-2">         <!-- Tight spacing (related items) -->
<div class="space-y-4">         <!-- Normal spacing (separate items) -->
<div class="space-y-8">         <!-- Loose spacing (sections) -->

<!-- Inline Spacing -->
<div class="space-x-2">         <!-- Buttons in a row -->
<div class="space-x-4">         <!-- Form fields -->
```

---

## Component Library

### 1. Buttons

```html
<!-- Primary Button (Main Actions) -->
<button class="inline-flex items-center px-4 py-2 border border-transparent 
               text-sm font-medium rounded-lg text-white bg-brand-600 
               hover:bg-brand-700 focus:outline-none focus:ring-2 
               focus:ring-offset-2 focus:ring-brand-500
               transition-colors duration-200">
  Create Request
</button>

<!-- Secondary Button (Alternative Actions) -->
<button class="inline-flex items-center px-4 py-2 border border-neutral-300 
               text-sm font-medium rounded-lg text-neutral-700 bg-white 
               hover:bg-neutral-50 focus:outline-none focus:ring-2 
               focus:ring-offset-2 focus:ring-brand-500
               transition-colors duration-200">
  Cancel
</button>

<!-- Danger Button (Destructive Actions) -->
<button class="inline-flex items-center px-4 py-2 border border-transparent 
               text-sm font-medium rounded-lg text-white bg-error 
               hover:bg-red-700 focus:outline-none focus:ring-2 
               focus:ring-offset-2 focus:ring-error
               transition-colors duration-200">
  Delete
</button>

<!-- Icon Button -->
<button class="inline-flex items-center justify-center w-10 h-10 
               rounded-full bg-neutral-100 hover:bg-neutral-200
               text-neutral-600 hover:text-neutral-900
               transition-colors duration-200">
  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
  </svg>
</button>

<!-- Button Sizes -->
<button class="px-3 py-1.5 text-xs">Small</button>
<button class="px-4 py-2 text-sm">Medium (Default)</button>
<button class="px-6 py-3 text-base">Large</button>
```

### 2. Cards

```html
<!-- Basic Card -->
<div class="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
  <h3 class="text-lg font-medium text-neutral-900 mb-2">Card Title</h3>
  <p class="text-sm text-neutral-600">Card content goes here.</p>
</div>

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
      <div class="flex items-center text-xs text-neutral-500 space-x-4">
        <span class="flex items-center">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Mumbai, Maharashtra
        </span>
        <span class="flex items-center">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          2 hours ago
        </span>
      </div>
    </div>
    <button class="ml-4 text-brand-600 hover:text-brand-700 text-sm font-medium">
      View Details
    </button>
  </div>
</div>

<!-- Stat Card -->
<div class="bg-white rounded-lg shadow-sm border border-neutral-200 p-6">
  <div class="flex items-center">
    <div class="flex-shrink-0 bg-brand-100 rounded-lg p-3">
      <svg class="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    </div>
    <div class="ml-5 w-0 flex-1">
      <dl>
        <dt class="text-sm font-medium text-neutral-500 truncate">
          Active Requests
        </dt>
        <dd class="flex items-baseline">
          <div class="text-2xl font-semibold text-neutral-900">
            342
          </div>
          <div class="ml-2 flex items-baseline text-sm font-semibold text-success">
            <svg class="self-center flex-shrink-0 h-5 w-5 text-success" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
            <span class="sr-only">Increased by</span>
            12%
          </div>
        </dd>
      </dl>
    </div>
  </div>
</div>
```

### 3. Forms

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

<!-- Select Dropdown -->
<div class="space-y-1">
  <label for="service-type" class="block text-sm font-medium text-neutral-700">
    Service Type
  </label>
  <select
    id="service-type"
    class="block w-full px-3 py-2 border border-neutral-300 rounded-lg 
           text-neutral-900 bg-white
           focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent
           transition-shadow duration-200"
  >
    <option value="">Select service type</option>
    <option value="medical">Medical</option>
    <option value="food">Food</option>
    <option value="shelter">Shelter</option>
    <option value="rescue">Rescue</option>
  </select>
</div>

<!-- Textarea -->
<div class="space-y-1">
  <label for="description" class="block text-sm font-medium text-neutral-700">
    Description
  </label>
  <textarea
    id="description"
    rows="4"
    class="block w-full px-3 py-2 border border-neutral-300 rounded-lg 
           text-neutral-900 placeholder-neutral-400
           focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent
           transition-shadow duration-200"
    placeholder="Describe the assistance needed..."
  ></textarea>
</div>

<!-- Radio Group -->
<div class="space-y-1">
  <label class="block text-sm font-medium text-neutral-700 mb-2">
    Priority Level
  </label>
  <div class="space-y-2">
    <label class="inline-flex items-center">
      <input type="radio" name="priority" value="critical" class="form-radio text-brand-600 focus:ring-brand-500 h-4 w-4">
      <span class="ml-2 text-sm text-neutral-700">Critical</span>
    </label>
    <label class="inline-flex items-center">
      <input type="radio" name="priority" value="high" class="form-radio text-brand-600 focus:ring-brand-500 h-4 w-4">
      <span class="ml-2 text-sm text-neutral-700">High</span>
    </label>
    <label class="inline-flex items-center">
      <input type="radio" name="priority" value="medium" class="form-radio text-brand-600 focus:ring-brand-500 h-4 w-4">
      <span class="ml-2 text-sm text-neutral-700">Medium</span>
    </label>
  </div>
</div>

<!-- Checkbox -->
<div class="flex items-start">
  <input
    id="terms"
    type="checkbox"
    class="h-4 w-4 text-brand-600 focus:ring-brand-500 border-neutral-300 rounded"
  />
  <label for="terms" class="ml-2 block text-sm text-neutral-700">
    I agree to the terms and conditions
  </label>
</div>
```

### 4. Alerts & Notifications

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

<!-- Error Alert -->
<div class="bg-error/10 border-l-4 border-error rounded-r-lg p-4">
  <div class="flex items-start">
    <svg class="w-5 h-5 text-error flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
    </svg>
    <div class="ml-3">
      <h3 class="text-sm font-medium text-error">Error</h3>
      <p class="text-sm text-neutral-700 mt-1">Unable to submit request. Please try again.</p>
    </div>
  </div>
</div>

<!-- Warning Alert -->
<div class="bg-warning/10 border-l-4 border-warning rounded-r-lg p-4">
  <div class="flex items-start">
    <svg class="w-5 h-5 text-warning flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
    </svg>
    <div class="ml-3">
      <h3 class="text-sm font-medium text-warning">Warning</h3>
      <p class="text-sm text-neutral-700 mt-1">This action cannot be undone.</p>
    </div>
  </div>
</div>

<!-- Info Alert -->
<div class="bg-info/10 border-l-4 border-info rounded-r-lg p-4">
  <div class="flex items-start">
    <svg class="w-5 h-5 text-info flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
    </svg>
    <div class="ml-3">
      <h3 class="text-sm font-medium text-info">Information</h3>
      <p class="text-sm text-neutral-700 mt-1">Your request is being processed.</p>
    </div>
  </div>
</div>
```

### 5. Badges & Tags

```html
<!-- Status Badges -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-status-submitted-light text-status-submitted">
  Submitted
</span>

<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-status-approved-light text-status-approved">
  Approved
</span>

<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-status-in-progress-light text-status-in-progress">
  In Progress
</span>

<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-status-completed-light text-status-completed">
  Completed
</span>

<!-- Priority Badges -->
<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-priority-critical-light text-priority-critical border border-priority-critical">
  CRITICAL
</span>

<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-priority-high-light text-priority-high">
  HIGH
</span>

<!-- Removable Tags -->
<span class="inline-flex items-center pl-2.5 pr-1 py-0.5 rounded-full text-xs font-medium bg-brand-100 text-brand-700">
  Medical
  <button type="button" class="flex-shrink-0 ml-1.5 h-4 w-4 rounded-full inline-flex items-center justify-center text-brand-400 hover:bg-brand-200 hover:text-brand-500 focus:outline-none focus:bg-brand-500 focus:text-white">
    <svg class="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
      <path stroke-linecap="round" stroke-width="1.5" d="M1 1l6 6m0-6L1 7" />
    </svg>
  </button>
</span>
```

---

## Layout Patterns

### 1. Dashboard Layout

```html
<div class="min-h-screen bg-neutral-50">
  <!-- Header -->
  <header class="bg-white shadow-sm border-b border-neutral-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo/Title -->
        <div class="flex items-center">
          <h1 class="text-xl font-bold text-brand-600">IDRM</h1>
        </div>
        <!-- Navigation -->
        <nav class="hidden md:flex space-x-8">
          <a href="#" class="text-brand-600 border-b-2 border-brand-600 px-1 pt-1 text-sm font-medium">
            Dashboard
          </a>
          <a href="#" class="text-neutral-600 hover:text-neutral-900 px-1 pt-1 text-sm font-medium">
            Requests
          </a>
          <a href="#" class="text-neutral-600 hover:text-neutral-900 px-1 pt-1 text-sm font-medium">
            Map
          </a>
        </nav>
        <!-- User Menu -->
        <div class="flex items-center space-x-4">
          <button class="text-neutral-600 hover:text-neutral-900">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </button>
          <div class="flex items-center space-x-2">
            <img class="h-8 w-8 rounded-full" src="https://ui-avatars.com/api/?name=John+Doe" alt="">
            <span class="text-sm font-medium text-neutral-700">John Doe</span>
          </div>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Page Header -->
    <div class="mb-8">
      <h2 class="text-3xl font-bold text-neutral-900">Dashboard</h2>
      <p class="mt-1 text-sm text-neutral-600">
        Overview of active disaster response operations
      </p>
    </div>

    <!-- Content Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Cards go here -->
    </div>
  </main>
</div>
```

### 2. Map View Layout

```html
<div class="h-screen flex flex-col">
  <!-- Header (fixed) -->
  <header class="bg-white shadow-sm border-b border-neutral-200 z-10">
    <!-- Header content -->
  </header>

  <!-- Map Container (flex-grow) -->
  <div class="flex-1 relative">
    <!-- Map -->
    <div id="map" class="absolute inset-0"></div>
  
    <!-- Floating Controls -->
    <div class="absolute top-4 left-4 z-20 space-y-2">
      <!-- Search -->
      <div class="bg-white rounded-lg shadow-lg p-2 w-80">
        <input
          type="text"
          placeholder="Search location..."
          class="w-full px-3 py-2 border-none focus:ring-0 text-sm"
        />
      </div>
    
      <!-- Filters -->
      <div class="bg-white rounded-lg shadow-lg p-4">
        <h3 class="text-sm font-medium text-neutral-900 mb-2">Filters</h3>
        <!-- Filter controls -->
      </div>
    </div>
  
    <!-- Legend (bottom-left) -->
    <div class="absolute bottom-4 left-4 z-20 bg-white rounded-lg shadow-lg p-4">
      <h4 class="text-sm font-medium text-neutral-900 mb-2">Legend</h4>
      <!-- Legend items -->
    </div>
  </div>
</div>
```

---

## Map Styling

### Marker Colors

```javascript
// Map service types to colors
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

// Priority sizes
const prioritySizes = {
  critical: 16,  // Largest
  high: 12,
  medium: 10,
  low: 8        // Smallest
};
```

### Custom Map Markers

```javascript
// Create custom icon
const createMarkerIcon = (serviceType, priority) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div class="marker-wrapper">
        <div class="marker-pin" style="
          background-color: ${serviceColors[serviceType]};
          width: ${prioritySizes[priority]}px;
          height: ${prioritySizes[priority]}px;
        ">
          <svg class="marker-icon" viewBox="0 0 24 24" fill="white">
            ${getServiceIcon(serviceType)}
          </svg>
        </div>
        <div class="marker-pulse"></div>
      </div>
    `,
    iconSize: [prioritySizes[priority] * 2, prioritySizes[priority] * 2],
    iconAnchor: [prioritySizes[priority], prioritySizes[priority] * 2]
  });
};
```

### Map Popup Styling

```html
<!-- Leaflet Popup -->
<div class="map-popup min-w-[280px]">
  <div class="popup-header bg-service-medical text-white p-3 -m-2 mb-2 rounded-t-lg">
    <div class="flex items-center justify-between">
      <span class="text-xs font-medium uppercase">Medical</span>
      <span class="text-xs">HIGH PRIORITY</span>
    </div>
    <h4 class="text-sm font-semibold mt-1">Emergency Medical Supplies</h4>
  </div>
  
  <div class="popup-body space-y-2 text-sm">
    <p class="text-neutral-700">
      Urgent need for first aid kits and medicines.
    </p>
  
    <div class="flex items-center text-xs text-neutral-500">
      <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      2 hours ago
    </div>
  
    <div class="pt-2 border-t border-neutral-200">
      <button class="w-full px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700">
        View Details
      </button>
    </div>
  </div>
</div>
```

---

## Responsive Breakpoints

```javascript
// Tailwind breakpoints
screens: {
  'sm': '640px',   // Mobile landscape
  'md': '768px',   // Tablet
  'lg': '1024px',  // Desktop
  'xl': '1280px',  // Large desktop
  '2xl': '1536px', // Extra large
}
```

### Mobile-First Approach

```html
<!-- Stack on mobile, grid on desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- Cards -->
</div>

<!-- Hide on mobile, show on desktop -->
<div class="hidden md:block">
  <!-- Desktop-only content -->
</div>

<!-- Show on mobile, hide on desktop -->
<div class="md:hidden">
  <!-- Mobile-only content -->
</div>

<!-- Responsive sizing -->
<h1 class="text-2xl md:text-3xl lg:text-4xl font-bold">
  Responsive Title
</h1>

<!-- Responsive padding -->
<div class="p-4 md:p-6 lg:p-8">
  <!-- Content -->
</div>
```

---

## Accessibility Checklist

### Must-Have

- [ ] All interactive elements keyboard accessible
- [ ] Focus states visible (ring-2 ring-brand-500)
- [ ] Color contrast ≥ 4.5:1 for text
- [ ] Alt text for images
- [ ] ARIA labels for icons
- [ ] Skip to main content link
- [ ] Form labels associated with inputs
- [ ] Error messages clear and specific

### HTML Examples

```html
<!-- Button with ARIA -->
<button aria-label="Close dialog" class="...">
  <svg aria-hidden="true" class="w-5 h-5" ...>
    <path ... />
  </svg>
</button>

<!-- Input with label -->
<label for="email" class="sr-only">Email address</label>
<input id="email" type="email" placeholder="Email" ... />

<!-- Skip link -->
<a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:z-50 focus:p-4 focus:bg-brand-600 focus:text-white">
  Skip to main content
</a>
```

---

## Design Token Export

```javascript
// design-tokens.js
export const designTokens = {
  colors: {
    brand: { ... },
    priority: { ... },
    status: { ... },
    service: { ... },
  },
  typography: {
    fontFamily: { ... },
    fontSize: { ... },
    fontWeight: { ... },
  },
  spacing: { ... },
  borderRadius: {
    sm: '0.25rem',
    DEFAULT: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    DEFAULT: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  },
};
```

---

## Next Steps

1. ✅ Review this design system

2. [ ] Set up Tailwind config with these tokens
3. [ ] Build component library in Storybook (optional)
4. [ ] Create design mockups in Figma/Sketch
5. [ ] Start implementing components

This design system ensures **consistency, accessibility, and rapid development** throughout the project! 🎨
