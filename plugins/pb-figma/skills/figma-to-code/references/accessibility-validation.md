# Accessibility Validation Reference

Bu dokuman, Phase 4'te accessibility (a11y) kontrollerini otomatiklestirmek icin kullanilir.

---

## A11y Validation Workflow

```
Generated Code → Browser Render → A11y Audit → Fix Issues → Re-check
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
    Semantic      Keyboard      Screen
      HTML        Navigation    Reader
```

---

## WCAG 2.1 AA Quick Checklist

### Perceivable

- [ ] **1.1.1** Images have alt text
- [ ] **1.3.1** Semantic HTML used (header, main, nav, footer)
- [ ] **1.4.3** Color contrast ratio ≥ 4.5:1 (text), ≥ 3:1 (large text)
- [ ] **1.4.4** Text resizable to 200% without loss

### Operable

- [ ] **2.1.1** All functionality keyboard accessible
- [ ] **2.4.1** Skip links provided (for complex pages)
- [ ] **2.4.4** Link purpose clear from text
- [ ] **2.4.7** Focus visible on interactive elements

### Understandable

- [ ] **3.1.1** Page language declared (`<html lang="en">`)
- [ ] **3.2.1** Focus doesn't change context unexpectedly
- [ ] **3.3.2** Form inputs have labels

### Robust

- [ ] **4.1.1** HTML is valid
- [ ] **4.1.2** ARIA attributes used correctly

---

## Automated Checks (jest-axe)

### Test Template

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';
import { render } from '@testing-library/react';

expect.extend(toHaveNoViolations);

it('has no accessibility violations', async () => {
  const { container } = render(<Component />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Common Violations

| Violation | Description | Fix |
|-----------|-------------|-----|
| `image-alt` | Image missing alt text | Add `alt="description"` |
| `button-name` | Button has no accessible name | Add text content or `aria-label` |
| `link-name` | Link has no accessible name | Add text content or `aria-label` |
| `color-contrast` | Insufficient contrast | Darken text or lighten background |
| `label` | Form input missing label | Add `<label>` or `aria-label` |
| `region` | Content not in landmark | Wrap in `<main>`, `<nav>`, etc. |

---

## Manual Checks (Claude Vision)

### Keyboard Navigation Test

```javascript
// In browser, execute keyboard navigation
mcp__claude-in-chrome__computer({
  action: "key",
  text: "Tab",
  repeat: 5,  // Tab through interactive elements
  tabId: <tab-id>
})

// Take screenshot to verify focus visibility
mcp__claude-in-chrome__computer({
  action: "screenshot",
  tabId: <tab-id>
})
```

**Check:**
- Focus indicator visible on each interactive element
- Logical tab order (left-to-right, top-to-bottom)
- No focus traps (can Tab away from any element)

### Color Contrast Check

Use Claude Vision to identify:
- Text on colored backgrounds
- Icon-only buttons
- Placeholder text
- Disabled states

**Contrast Requirements:**
| Element | Minimum Ratio |
|---------|---------------|
| Normal text | 4.5:1 |
| Large text (18px+ or 14px+ bold) | 3:1 |
| UI components | 3:1 |

---

## Claude in Chrome A11y Audit

### Read Accessibility Tree

```javascript
mcp__claude-in-chrome__read_page({
  tabId: <tab-id>,
  filter: "interactive"  // Focus on interactive elements
})
```

**Check output for:**
- Missing accessible names
- Incorrect roles
- Missing labels

### Find Specific Elements

```javascript
mcp__claude-in-chrome__find({
  query: "buttons without accessible name",
  tabId: <tab-id>
})
```

---

## Common A11y Fixes (Tailwind/React)

### Missing Button Name

```tsx
// ❌ Bad
<button onClick={handleClick}>
  <Icon name="close" />
</button>

// ✅ Good
<button onClick={handleClick} aria-label="Close dialog">
  <Icon name="close" />
</button>
```

### Missing Image Alt

```tsx
// ❌ Bad
<img src="/hero.jpg" />

// ✅ Good (informative)
<img src="/hero.jpg" alt="Team collaboration in modern office" />

// ✅ Good (decorative)
<img src="/hero.jpg" alt="" role="presentation" />
```

### Missing Form Label

```tsx
// ❌ Bad
<input type="email" placeholder="Email" />

// ✅ Good
<label>
  Email
  <input type="email" />
</label>

// ✅ Also good
<input type="email" aria-label="Email address" placeholder="Email" />
```

### Color Contrast

```tsx
// ❌ Bad - gray-400 on white ≈ 2.7:1
<p className="text-gray-400">Muted text</p>

// ✅ Good - gray-600 on white ≈ 5.7:1
<p className="text-gray-600">Muted text</p>
```

### Focus Visibility

```tsx
// ❌ Bad - removes focus outline
<button className="focus:outline-none">Click</button>

// ✅ Good - visible focus ring
<button className="focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
  Click
</button>
```

---

## TodoWrite for A11y Issues

```javascript
TodoWrite({
  todos: [
    {
      content: "A11y: Add aria-label to icon button (close)",
      status: "pending",
      activeForm: "Adding aria-label to close button"
    },
    {
      content: "A11y: Increase text contrast (text-gray-400 → text-gray-600)",
      status: "pending",
      activeForm: "Fixing text contrast"
    },
    {
      content: "A11y: Add focus:ring to interactive elements",
      status: "pending",
      activeForm: "Adding focus indicators"
    }
  ]
})
```

---

## Integration with Phase 4

Add to Phase 4 Visual Validation:

1. After visual comparison passes
2. Run jest-axe automated check (if test file exists)
3. Use Claude in Chrome for keyboard navigation test
4. Use Claude Vision for contrast check
5. Create todos for any violations
6. Fix and re-check
