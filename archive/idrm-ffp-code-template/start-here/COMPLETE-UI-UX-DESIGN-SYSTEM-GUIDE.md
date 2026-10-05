# IDRM Design System v3.0
## Visual Language for Disaster Response - Multi-Platform Edition

**Version**: 3.0  
**Last Updated**: May 24, 2026  
**Status**: Multi-Platform Design System  
**Platforms**: HTML/Tailwind (Web) + React SPA (Admin) + React Native (Mobile)

> **Philosophy**: Clear, urgent, accessible. Design for crisis, optimize for speed across **all platforms**.
>
> **Palette (reconciled 2026-05-30)**: **Slate** (neutrals) + **Emerald** (primary), Light Mode. The `brand` scale below = emerald; `neutral` = slate. **Canonical application rulebook**: [`instructions/instructions_ui_v3.md`](../instructions/instructions_ui_v3.md) — Tailwind component recipes + IDRM enum→color mapping. Enums (roles, statuses, service types) follow `docs/development/IDRM-FS.md` §3.3.

---

## 🎯 What's New in v3.0

### Three Frontend Interfaces Support

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

## 📱 Platform-Specific Approach

### When to Use Which Platform

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

## Design Principles

### 1. **Urgency Without Panic**
- Use color to convey priority without causing alarm
- Critical information prominent but not overwhelming
- Progressive disclosure: show essentials first
- **Platform adaptation**: 
  - Web: Subtle animations, clear hierarchy
  - Mobile: Haptic feedback, larger touch targets

### 2. **Clarity Under Stress**
- High contrast, readable typography
- Clear visual hierarchy
- Minimal cognitive load
- One primary action per screen
- **Platform adaptation**:
  - Web: Keyboard shortcuts, breadcrumbs
  - Mobile: Thumb-zone optimization, gesture hints

### 3. **Accessibility First**
- WCAG 2.1 AA compliant minimum (AAA target)
- Color-blind safe palette
- Screen reader friendly
- Keyboard navigable (web), VoiceOver/TalkBack (mobile)
- **Platform adaptation**:
  - Web: Focus indicators, skip links
  - Mobile: Dynamic type, reduced motion support

### 4. **Mobile-First Reality**
- Most disaster response happens on phones
- Touch targets ≥ 44px (iOS/Android HIG)
- Works on slow connections (3G)
- Offline-capable
- **Platform adaptation**:
  - Web: Responsive down to 320px
  - Mobile: Native platform controls

---

## Color System

### Primary Palette

```javascript
// tailwind.config.js (Web)
// Also exported as JS/TS for React SPA
// Converted to React Native StyleSheet

module.exports = {
  theme: {
    extend: {
      colors: {
        // Brand Colors
        // Brand = Emerald (primary). Use brand-600 (#059669) as the primary action color.
        brand: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',  // Primary brand (emerald)
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
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
          low: {            // green (emerald)
            light: '#d1fae5',
            DEFAULT: '#059669',
            dark: '#047857',
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
          accepted: {
            light: '#e0f2fe',
            DEFAULT: '#0284c7',
            dark: '#075985',
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
            light: '#f1f5f9',
            DEFAULT: '#64748b',
            dark: '#475569',
          },
          disputed: {
            light: '#fee2e2',
            DEFAULT: '#dc2626',
            dark: '#991b1b',
          },
          expired: {
            light: '#f1f5f9',
            DEFAULT: '#94a3b8',
            dark: '#64748b',
          },
        },
        
        // Service Type Colors
        service: {            // canonical 6 (IDRM-FS §3.3) — no clothing/transport
          rescue: '#dc2626',       // red-600
          medical: '#f43f5e',      // rose-500
          food: '#f59e0b',         // amber-500
          shelter: '#8b5cf6',      // violet-500
          water: '#3b82f6',        // blue-500
          other: '#64748b',        // slate-500
        },
        
        // Neutral Colors = Slate (extended)
        neutral: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        
        // Semantic Colors
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6',
        review: '#8b5cf6',
      }
    }
  }
}
```

### React Native Color Tokens

```typescript
// design-tokens/colors.ts (React Native)
export const Colors = {
  brand: {
    50: '#ecfdf5',
    100: '#d1fae5',
    200: '#a7f3d0',
    300: '#6ee7b7',
    400: '#34d399',
    500: '#10b981',
    600: '#059669',  // Primary brand (emerald)
    700: '#047857',
    800: '#065f46',
    900: '#064e3b',
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
      light: '#d1fae5',
      default: '#059669',
      dark: '#047857',
    },
  },
  
  // ... same structure as web
  
  // Platform-specific additions
  system: {
    background: '#ffffff',
    backgroundSecondary: '#f1f5f9',
    label: '#0f172a',
    secondaryLabel: '#64748b',
    tertiaryLabel: '#94a3b8',
    separator: '#e2e8f0',
  },
};
```

### Color Usage Guidelines

#### Priority Colors

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

## Typography

### Font Stack

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

### Typography Scale Examples

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

## Spacing System

### Base Spacing Scale

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

## 📱 Mobile-Specific Design Tokens (NEW in v3)

### Touch Targets

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

### Safe Area Insets

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

### Platform-Specific Elevations

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

## 🎨 Component Library - Multi-Platform

### Component Mapping Table

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

### 1. Buttons

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

### 2. Cards

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

### 3. Forms

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

### 4. Alerts & Notifications

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

## 🌐 Responsive Breakpoints

### Breakpoint System

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

### Responsive Usage

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

## ♿ Accessibility Guidelines

### WCAG 2.1 Compliance

All three platforms must meet **WCAG 2.1 AA minimum**, targeting **AAA** where possible.

#### Color Contrast

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

#### Screen Reader Support

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

#### Keyboard Navigation (Web)

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

## 🗺️ Map Styling (Cross-Platform)

### Marker Colors & Sizes

```javascript
// Shared across all platforms
const serviceColors = {
  rescue: '#dc2626',   // red-600
  medical: '#f43f5e',  // rose-500
  food: '#f59e0b',     // amber-500
  shelter: '#8b5cf6',  // violet-500
  water: '#3b82f6',    // blue-500
  other: '#64748b'     // slate-500
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

## 📦 Design Token Export

### JavaScript/TypeScript Export

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

## 🎯 Platform-Specific Implementation Notes

### HTML/Tailwind (Primary Web)
- **Target**: General public, works everywhere
- **Approach**: Progressive enhancement
- **Features**: Server-rendered, works without JS
- **Testing**: Chrome, Firefox, Safari, Edge (last 2 versions)

### React SPA (Admin Web)
- **Target**: Administrators, coordinators
- **Approach**: Rich client-side app
- **Features**: Complex interactions, data visualizations
- **Testing**: Desktop browsers primarily

### React Native (Mobile)
- **Target**: Field workers, mobile-first users
- **Approach**: Native performance
- **Features**: Offline-first, GPS, push notifications
- **Testing**: iOS 14+, Android 10+

---

## ✅ Cross-Platform Checklist

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

## 📚 Additional Resources

### Documentation
- [Tailwind CSS Docs](https://tailwindcss.com)
- [React Native Docs](https://reactnative.dev)
- [iOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design Guidelines](https://material.io/design)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

### Tools
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
