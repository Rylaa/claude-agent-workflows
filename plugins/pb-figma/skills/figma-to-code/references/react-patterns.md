# React Patterns Reference

> **Used by:** code-generator-react

This reference covers React/Tailwind-specific patterns including CVA (class-variance-authority) for component variants and required utility setups.

---

## Component Variants with CVA

For components with multiple variants (size, color, state), use class-variance-authority (cva):

**Install:**
```bash
npm install class-variance-authority
```

**Pattern:**
```tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  // Base classes (always applied)
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        primary: "bg-primary text-white hover:bg-primary/90 focus:ring-primary",
        secondary: "bg-secondary text-white hover:bg-secondary/90 focus:ring-secondary",
        outline: "border border-primary text-primary hover:bg-primary/10",
        ghost: "text-primary hover:bg-primary/10",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-base",
        lg: "h-12 px-6 text-lg",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant,
  size,
  className,
  children,
  ...props
}) => {
  return (
    <button
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    >
      {children}
    </button>
  );
};

// Usage
<Button variant="primary" size="lg">Click me</Button>
<Button variant="outline">Outlined</Button>
```

**When to use CVA:**

| Scenario | Use CVA? | Reason |
|----------|----------|--------|
| 2+ variants defined in spec | Yes | Cleaner than conditionals |
| Single variant | No | Simple conditional or prop |
| Complex state combinations | Yes | Manages compound variants |
| One-off component | No | Overkill for simple cases |

**Extract variants from spec:**

```markdown
## Components

### Button
| Property | Value |
|----------|-------|
| **Variants** | primary, secondary, outline, ghost |
| **Sizes** | sm (32px), md (40px), lg (48px) |
```

→ Map directly to CVA variants object.

---

## Required Utilities

**CRITICAL:** When generating React code, include these helper utilities if needed.

### cn() Utility (Class Name Merger)

If any generated code uses `cn()`, ensure this utility exists:

```tsx
// lib/utils.ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

**Dependencies required:**
```bash
npm install clsx tailwind-merge
```

**Usage:**
```tsx
import { cn } from '@/lib/utils';

<div className={cn(
  "flex flex-col",           // Base classes
  isActive && "bg-primary",  // Conditional
  className                  // Props override
)}>
```

### CSS Variables Setup

If spec uses CSS custom properties, ensure they're defined:

```css
/* styles/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --color-primary: #3B82F6;
    --color-secondary: #6B7280;
    --color-background: #FFFFFF;
    --color-foreground: #1F2937;
    --color-border: #E5E7EB;
    /* From Design Tokens section */
  }

  .dark {
    --color-primary: #60A5FA;
    --color-secondary: #9CA3AF;
    --color-background: #111827;
    --color-foreground: #F9FAFB;
    --color-border: #374151;
  }
}
```

**Usage in Tailwind:**
```tsx
<div className="bg-[var(--color-background)] text-[var(--color-foreground)]">
```

### Tailwind 4 Theme Setup (if using Tailwind v4)

```css
/* styles/globals.css */
@import "tailwindcss";

@theme {
  --color-primary: #3B82F6;
  --color-secondary: #6B7280;
  --color-accent: #F59E0B;
  /* Semantic colors from Design Tokens */

  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;
}
```

### When to Include Utilities

| Utility | Include When |
|---------|--------------|
| cn() | Any conditional class merging |
| CSS Variables | Design tokens used with `var(--...)` |
| Tailwind @theme | Tailwind v4 project with custom tokens |

**Check for existing setup:**
```bash
# Check if cn exists
Grep("export function cn", path="lib/utils.ts")
Grep("export function cn", path="src/lib/utils.ts")

# Check if CSS variables exist
Grep("--color-primary", path="styles/globals.css")
```
