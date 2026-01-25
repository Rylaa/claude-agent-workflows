# Responsive Validation Checklist

This document provides a systematic approach to multi-breakpoint validation for Phase 4: Visual Validation.

---

## 1. Viewport Breakpoints Table

Standard breakpoints for responsive validation:

| Breakpoint | Width | Height | Device Category | Common Devices |
|------------|-------|--------|-----------------|----------------|
| **Mobile S** | 320px | 568px | Small Phone | iPhone SE, older Android |
| **Mobile M** | 375px | 667px | Standard Phone | iPhone 12/13/14, Pixel |
| **Mobile L** | 425px | 812px | Large Phone | iPhone Plus/Max models |
| **Tablet** | 768px | 1024px | Tablet Portrait | iPad, Android tablets |
| **Laptop** | 1024px | 768px | Small Laptop | MacBook Air, small laptops |
| **Desktop** | 1440px | 900px | Standard Desktop | Most monitors |
| **4K** | 2560px | 1440px | Large Display | 27" monitors, 4K displays |

### Tailwind CSS Breakpoints Reference

| Tailwind | Min Width | CSS |
|----------|-----------|-----|
| `sm` | 640px | `@media (min-width: 640px)` |
| `md` | 768px | `@media (min-width: 768px)` |
| `lg` | 1024px | `@media (min-width: 1024px)` |
| `xl` | 1280px | `@media (min-width: 1280px)` |
| `2xl` | 1536px | `@media (min-width: 1536px)` |

---

## 2. Validation Workflow

Desktop-first validation flow with progressive narrowing:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RESPONSIVE VALIDATION WORKFLOW                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  STEP 1: DESKTOP (1440px)                                               │
│  ├─→ resize_window(1440, 900)                                           │
│  ├─→ Take screenshot                                                     │
│  ├─→ Compare with Figma desktop frame                                   │
│  └─→ Fix issues, mark completed                                         │
│         │                                                                │
│         ▼                                                                │
│  STEP 2: TABLET (768px)                                                 │
│  ├─→ resize_window(768, 1024)                                           │
│  ├─→ Take screenshot                                                     │
│  ├─→ Compare with Figma tablet frame (if exists)                        │
│  └─→ Fix issues, mark completed                                         │
│         │                                                                │
│         ▼                                                                │
│  STEP 3: MOBILE (375px)                                                 │
│  ├─→ resize_window(375, 667)                                            │
│  ├─→ Take screenshot                                                     │
│  ├─→ Compare with Figma mobile frame (if exists)                        │
│  └─→ Fix issues, mark completed                                         │
│         │                                                                │
│         ▼                                                                │
│  STEP 4: EDGE CASES (Optional)                                          │
│  ├─→ Test at 320px (smallest)                                           │
│  ├─→ Test at breakpoint boundaries (767px, 1023px)                      │
│  └─→ Test at 4K if required                                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Claude in Chrome MCP Commands

### Viewport Resize Examples

**Desktop (1440px):**
```javascript
mcp__claude-in-chrome__resize_window({
  width: 1440,
  height: 900,
  tabId: <tab-id>
})
```

**Tablet (768px):**
```javascript
mcp__claude-in-chrome__resize_window({
  width: 768,
  height: 1024,
  tabId: <tab-id>
})
```

**Mobile (375px):**
```javascript
mcp__claude-in-chrome__resize_window({
  width: 375,
  height: 667,
  tabId: <tab-id>
})
```

**Mobile Small (320px):**
```javascript
mcp__claude-in-chrome__resize_window({
  width: 320,
  height: 568,
  tabId: <tab-id>
})
```

**Large Desktop / 4K (2560px):**
```javascript
mcp__claude-in-chrome__resize_window({
  width: 2560,
  height: 1440,
  tabId: <tab-id>
})
```

### Screenshot After Resize

```javascript
// Wait for layout reflow after resize
mcp__claude-in-chrome__computer({
  action: "wait",
  duration: 1,
  tabId: <tab-id>
})

// Take screenshot
mcp__claude-in-chrome__computer({
  action: "screenshot",
  tabId: <tab-id>
})
```

### Complete Responsive Test Sequence

```javascript
// 1. Get tab context (FIRST!)
const tabContext = mcp__claude-in-chrome__tabs_context_mcp({
  createIfEmpty: true
})
const tabId = tabContext.tabs[0].id

// 2. Navigate to component
mcp__claude-in-chrome__navigate({
  url: "http://localhost:3000/component-preview",
  tabId: tabId
})

// 3. Desktop validation
mcp__claude-in-chrome__resize_window({ width: 1440, height: 900, tabId })
mcp__claude-in-chrome__computer({ action: "wait", duration: 1, tabId })
mcp__claude-in-chrome__computer({ action: "screenshot", tabId })
// → Compare with Figma desktop frame

// 4. Tablet validation
mcp__claude-in-chrome__resize_window({ width: 768, height: 1024, tabId })
mcp__claude-in-chrome__computer({ action: "wait", duration: 1, tabId })
mcp__claude-in-chrome__computer({ action: "screenshot", tabId })
// → Compare with Figma tablet frame

// 5. Mobile validation
mcp__claude-in-chrome__resize_window({ width: 375, height: 667, tabId })
mcp__claude-in-chrome__computer({ action: "wait", duration: 1, tabId })
mcp__claude-in-chrome__computer({ action: "screenshot", tabId })
// → Compare with Figma mobile frame
```

---

## 4. Responsive Check Categories

### Layout Changes by Breakpoint

| Element | Desktop (1440px) | Tablet (768px) | Mobile (375px) |
|---------|------------------|----------------|----------------|
| Grid columns | 3-4 columns | 2 columns | 1 column |
| Flex direction | `flex-row` | `flex-row` or `flex-col` | `flex-col` |
| Container width | `max-w-7xl` | `max-w-3xl` | `w-full px-4` |
| Sidebar | Visible, fixed | Collapsible | Hidden/drawer |
| Hero section | Side-by-side | Stacked | Stacked, smaller |
| Card layout | Horizontal | Horizontal | Vertical |

### Typography Scaling by Breakpoint

| Element | Desktop | Tablet | Mobile | Tailwind Classes |
|---------|---------|--------|--------|------------------|
| H1 | 64px | 48px | 32px | `text-3xl md:text-5xl lg:text-6xl` |
| H2 | 48px | 36px | 28px | `text-2xl md:text-4xl lg:text-5xl` |
| H3 | 32px | 28px | 24px | `text-xl md:text-2xl lg:text-3xl` |
| Body | 18px | 16px | 16px | `text-base lg:text-lg` |
| Small | 14px | 14px | 12px | `text-xs sm:text-sm` |
| Button | 16px | 16px | 14px | `text-sm md:text-base` |

### Spacing Adjustments by Breakpoint

| Property | Desktop | Tablet | Mobile | Tailwind Pattern |
|----------|---------|--------|--------|------------------|
| Section padding | 80px | 64px | 40px | `py-10 md:py-16 lg:py-20` |
| Container padding | 32px | 24px | 16px | `px-4 md:px-6 lg:px-8` |
| Card padding | 32px | 24px | 16px | `p-4 md:p-6 lg:p-8` |
| Grid gap | 32px | 24px | 16px | `gap-4 md:gap-6 lg:gap-8` |
| Stack gap | 24px | 20px | 16px | `space-y-4 md:space-y-5 lg:space-y-6` |

### Component Visibility by Breakpoint

| Component | Desktop | Tablet | Mobile | Tailwind Classes |
|-----------|---------|--------|--------|------------------|
| Desktop Nav | Visible | Visible | Hidden | `hidden lg:flex` |
| Mobile Nav | Hidden | Hidden | Visible | `flex lg:hidden` |
| Hamburger Menu | Hidden | Hidden | Visible | `block lg:hidden` |
| Sidebar | Visible | Collapsible | Hidden | `hidden md:block` |
| Desktop CTA | Visible | Visible | Hidden | `hidden sm:block` |
| Mobile CTA | Hidden | Hidden | Visible | `block sm:hidden` |
| Footer columns | 4 columns | 2 columns | 1 column | `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4` |

---

## 5. Validation Checklist

### Desktop (1440px) Checklist

```
DESKTOP VALIDATION (1440px)
===========================
[ ] Layout matches Figma desktop frame
[ ] Grid/flexbox alignment correct
[ ] Typography sizes match design
[ ] Spacing (padding, margin, gap) matches design
[ ] All navigation items visible
[ ] Sidebar visible and positioned correctly
[ ] Images at correct aspect ratio
[ ] Hover states work correctly
[ ] No content overflow
[ ] Maximum content width respected
```

### Tablet (768px) Checklist

```
TABLET VALIDATION (768px)
=========================
[ ] Layout adapts correctly from desktop
[ ] Grid columns reduce appropriately (3 -> 2)
[ ] Navigation still accessible (may collapse)
[ ] Touch targets minimum 44px
[ ] Typography scales down appropriately
[ ] Spacing reduces proportionally
[ ] Images responsive, no distortion
[ ] Sidebar behavior correct (collapse/hide)
[ ] No horizontal scroll
[ ] All content accessible without desktop features
```

### Mobile (375px) Checklist

```
MOBILE VALIDATION (375px)
=========================
[ ] Layout fully stacked (single column)
[ ] Mobile navigation visible and functional
[ ] Hamburger menu present and working
[ ] Touch targets minimum 44x44px (Apple HIG)
[ ] Typography readable (min 16px body)
[ ] Adequate spacing for touch
[ ] Images scale to full width
[ ] No horizontal scroll (critical!)
[ ] Forms usable with mobile keyboard
[ ] Buttons full width or adequately sized
[ ] Critical content above the fold
[ ] Sticky elements don't obstruct content
```

### Mobile Small (320px) Edge Case

```
MOBILE SMALL VALIDATION (320px)
===============================
[ ] No text truncation breaking UI
[ ] No element overflow
[ ] Buttons still tappable
[ ] Images don't break layout
[ ] Long text wraps correctly
[ ] No horizontal scroll
```

---

## 6. Common Responsive Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| **Horizontal scroll** | Page scrolls left/right on mobile | Check for fixed widths, use `max-w-full overflow-x-hidden` |
| **Text overflow** | Text breaks container | Use `break-words` or `truncate`, check long content |
| **Touch targets too small** | Hard to tap buttons/links | Add `min-h-11 min-w-11` (44px) for touch elements |
| **Grid not collapsing** | Multiple columns on mobile | Add responsive classes `grid-cols-1 md:grid-cols-2 lg:grid-cols-3` |
| **Fixed widths** | Elements overflow viewport | Replace `w-[500px]` with `w-full max-w-[500px]` |
| **Hidden hamburger** | No mobile nav visible | Check `lg:hidden` class on mobile menu trigger |
| **Desktop nav on mobile** | Full nav shown on mobile | Add `hidden lg:flex` to desktop nav |
| **Images too large** | Images overflow container | Add `max-w-full h-auto` to images |
| **Fonts too large** | Headers dominate mobile | Add responsive font sizes `text-2xl md:text-4xl` |
| **Spacing too large** | Excessive whitespace mobile | Use responsive spacing `py-8 md:py-16 lg:py-24` |
| **Sidebar blocking** | Sidebar covers content | Hide on mobile `hidden md:block` or use drawer |
| **z-index issues** | Elements overlapping wrong | Check stacking context, use consistent z-index scale |
| **Position fixed issues** | Fixed elements misplaced | Test sticky/fixed behavior at each breakpoint |
| **Form inputs small** | Hard to type on mobile | Ensure `text-base` (16px) to prevent iOS zoom |

---

## 7. Figma Frame Sizes

### Checking for Multiple Viewport Frames

**Step 1: Get file structure**
```javascript
mcp__plugin_pb-figma_pixelbyte-figma-mcp__figma_get_file_structure({
  params: {
    file_key: "FIGMA_FILE_KEY",
    depth: 3
  }
})
```

**Look for frame patterns like:**
- `ComponentName - Desktop`
- `ComponentName - Tablet`
- `ComponentName - Mobile`
- `ComponentName / 1440` (width notation)
- `ComponentName / 768`
- `ComponentName / 375`

**Step 2: Get screenshot for each frame**
```javascript
// Desktop frame
mcp__plugin_pb-figma_pixelbyte-figma-mcp__figma_get_screenshot({
  params: {
    file_key: "FIGMA_FILE_KEY",
    node_ids: ["DESKTOP_NODE_ID"],
    format: "png",
    scale: 2
  }
})

// Tablet frame
mcp__plugin_pb-figma_pixelbyte-figma-mcp__figma_get_screenshot({
  params: {
    file_key: "FIGMA_FILE_KEY",
    node_ids: ["TABLET_NODE_ID"],
    format: "png",
    scale: 2
  }
})

// Mobile frame
mcp__plugin_pb-figma_pixelbyte-figma-mcp__figma_get_screenshot({
  params: {
    file_key: "FIGMA_FILE_KEY",
    node_ids: ["MOBILE_NODE_ID"],
    format: "png",
    scale: 2
  }
})
```

**Step 3: Check frame dimensions**
```javascript
mcp__plugin_pb-figma_pixelbyte-figma-mcp__figma_get_node_details({
  params: {
    file_key: "FIGMA_FILE_KEY",
    node_id: "NODE_ID"
  }
})
// → Returns width/height to confirm frame size
```

### Common Figma Frame Naming Conventions

| Pattern | Example |
|---------|---------|
| Breakpoint suffix | `Hero - Desktop`, `Hero - Mobile` |
| Width suffix | `Hero / 1440`, `Hero / 375` |
| Device suffix | `Hero / iPhone 14`, `Hero / iPad` |
| Nested frames | `Responsive / Desktop / Hero` |
| Variant property | Property: "Breakpoint" with Desktop/Tablet/Mobile |

---

## 8. TodoWrite for Responsive Issues

When responsive issues are found, create structured todos:

```javascript
TodoWrite({
  todos: [
    // Desktop issues
    {
      content: "[Desktop] Hero grid: grid-cols-2 -> grid-cols-3 for 1440px",
      status: "pending",
      activeForm: "Fixing desktop hero grid columns"
    },
    // Tablet issues
    {
      content: "[Tablet] Sidebar: hidden md:block not applied, showing on tablet",
      status: "pending",
      activeForm: "Fixing tablet sidebar visibility"
    },
    // Mobile issues
    {
      content: "[Mobile] Horizontal scroll detected - check fixed widths in card component",
      status: "pending",
      activeForm: "Fixing mobile horizontal scroll"
    },
    {
      content: "[Mobile] Touch target too small: button is 32px, needs min 44px",
      status: "pending",
      activeForm: "Fixing mobile button touch target"
    },
    {
      content: "[Mobile] Nav hamburger missing - add lg:hidden mobile menu trigger",
      status: "pending",
      activeForm: "Adding mobile hamburger menu"
    },
    // Cross-breakpoint issues
    {
      content: "[All] Typography not scaling - add text-2xl md:text-4xl lg:text-6xl to H1",
      status: "pending",
      activeForm: "Adding responsive typography classes"
    }
  ]
})
```

### Todo Format for Responsive Issues

```
[Breakpoint] [Element]: [Current state] -> [Required fix]
```

**Examples:**
- `[Mobile] Button height: h-8 -> min-h-11 for touch target`
- `[Tablet] Grid columns: grid-cols-3 -> grid-cols-2`
- `[Desktop] Container max-width: w-full -> max-w-7xl mx-auto`
- `[All] Font size: text-4xl -> text-2xl md:text-3xl lg:text-4xl`

---

## 9. Quick Reference

### Essential Responsive Patterns

```tsx
// Grid that collapses
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">

// Stack that becomes row
<div className="flex flex-col md:flex-row gap-4">

// Hide on mobile, show on desktop
<nav className="hidden lg:flex">

// Show on mobile, hide on desktop
<button className="lg:hidden">

// Responsive typography
<h1 className="text-2xl md:text-4xl lg:text-6xl">

// Responsive spacing
<section className="py-8 md:py-16 lg:py-24 px-4 md:px-6 lg:px-8">

// Touch-friendly button
<button className="min-h-11 min-w-11 px-4 py-2">

// Responsive container
<div className="w-full max-w-7xl mx-auto px-4 md:px-6">

// Image that scales
<img className="w-full max-w-full h-auto" />
```

### Minimum Touch Target Sizes

| Platform | Minimum Size |
|----------|--------------|
| Apple HIG | 44 x 44 px |
| Material Design | 48 x 48 dp |
| WCAG 2.5.5 | 44 x 44 CSS px |

### Breakpoint Decision Tree

```
Is content visible at 320px without horizontal scroll?
├─ No → Fix fixed widths, add overflow handling
│
Is touch target >= 44px on mobile?
├─ No → Add min-h-11 min-w-11 to interactive elements
│
Does layout collapse to single column on mobile?
├─ No → Add grid-cols-1 for mobile breakpoint
│
Is mobile navigation accessible?
├─ No → Add hamburger menu with lg:hidden trigger
│
Are fonts readable on mobile (>= 16px body)?
├─ No → Add responsive font classes, min text-base for inputs
```

---

## 10. Validation Complete Checklist

```
RESPONSIVE VALIDATION COMPLETE
==============================

Desktop (1440px)
[ ] Screenshot taken
[ ] Compared with Figma desktop frame
[ ] All issues fixed
[ ] Re-verified after fixes

Tablet (768px)
[ ] Screenshot taken
[ ] Compared with Figma tablet frame (if exists)
[ ] All issues fixed
[ ] Re-verified after fixes

Mobile (375px)
[ ] Screenshot taken
[ ] Compared with Figma mobile frame (if exists)
[ ] All issues fixed
[ ] Re-verified after fixes

Edge Cases
[ ] Tested at 320px (no horizontal scroll)
[ ] Tested at breakpoint boundaries (767px, 1023px)
[ ] Touch targets verified (>= 44px)

Final Verification
[ ] No horizontal scroll at any breakpoint
[ ] All navigation accessible at each breakpoint
[ ] Typography readable at all sizes
[ ] Images responsive, no distortion
[ ] Ready for Phase 5
```
