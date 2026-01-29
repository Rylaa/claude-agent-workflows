# Frame Properties Reference

Comprehensive guide for extracting Figma frame properties (dimensions, corner radius, borders) and mapping them to CSS/Tailwind and SwiftUI code.

---

## Frame Property Extraction

Extract frame properties for ALL container nodes (FRAME, COMPONENT, INSTANCE types) via `figma_get_node_details`.

### Figma Node Properties

| Property | Figma API Field | Description |
|----------|-----------------|-------------|
| Width | `absoluteBoundingBox.width` | Frame width in pixels |
| Height | `absoluteBoundingBox.height` | Frame height in pixels |
| Corner Radius (uniform) | `cornerRadius` | Single value for all corners |
| Corner Radius (per-corner) | `rectangleCornerRadii` | Array: [TL, TR, BR, BL] |
| Stroke Color | `strokes[].color` `{r, g, b, a}` | Border color |
| Stroke Weight | `strokeWeight` | Border thickness in pixels |
| Stroke Align | `strokeAlign` | INSIDE, OUTSIDE, or CENTER |

### Frame Properties Table Format

The design-validator outputs frame properties in this table format:

| Node ID | Node Name | Width | Height | Corner Radius | Border |
|---------|-----------|-------|--------|---------------|--------|
| 3:217 | OnboardingCard | 393 | 568 | 24px (uniform) | none |
| 3:230 | ChecklistItem | 361 | 80 | 12px (uniform) | 1px #FFFFFF40 inside |
| 3:306 | GrowthSection | 361 | 180 | 16px (TL/TR), 0 (BL/BR) | none |

### Output Formats

**Corner Radius:**
- Uniform: `16px (uniform)`
- Per-corner: `16px (TL/TR), 8px (BL/BR)` or `TL:16 TR:16 BL:8 BR:8`

**Border:**
- With border: `{width}px {color}{opacity} {align}` (e.g., `1px #FFFFFF40 inside`)
- Without: `none`

### Parsing Rules

**Corner Radius parsing:**

```
"24px (uniform)"              -> cornerRadius: 24
"16px (TL/TR), 0 (BL/BR)"    -> cornerRadius: { tl: 16, tr: 16, bl: 0, br: 0 }
"TL:16 TR:16 BL:8 BR:8"      -> cornerRadius: { tl: 16, tr: 16, bl: 8, br: 8 }
```

**Border parsing:**

```
"1px #FFFFFF40 inside"  -> border: { width: 1, color: "#FFFFFF", opacity: 0.4, align: "inside" }
"2px #000000 outside"   -> border: { width: 2, color: "#000000", opacity: 1.0, align: "outside" }
"none"                  -> border: null
```

---

## Dimensions Mapping

### CSS / Tailwind

| Spec Context | Tailwind Class | Use Case |
|--------------|----------------|----------|
| Fixed size (card, button) | `w-[361px] h-[80px]` | Exact Figma dimensions |
| Flexible container | `max-w-[361px]` | Responsive, shrinks on mobile |
| Full width with max | `w-full max-w-[361px]` | Fills container up to max |
| Height only | `h-[80px]` | Width determined by content |

**When to use fixed vs flexible:**

1. **Use fixed `w-[Xpx]`:** Icons, badges, exact design requirements
2. **Use `max-w-[Xpx]`:** Cards, containers that should be responsive
3. **Combine for responsive:** `w-full max-w-[361px]` for mobile-first

```tsx
// Fixed size (exact match to Figma)
<div className="w-[361px] h-[80px]">

// Flexible width (responsive)
<div className="w-full max-w-[361px] h-[80px]">

// Full-width card with max constraint
<div className="w-full max-w-sm h-auto">
```

### SwiftUI

| Spec Context | SwiftUI Modifier | Use Case |
|-------------|------------------|----------|
| Fixed size component | `.frame(width: 361, height: 80)` | Exact dimensions required |
| Flexible container | `.frame(maxWidth: 361)` | Adapts to smaller screens |
| Height-only constraint | `.frame(height: 80)` | Width determined by content |
| Full-width with max | `.frame(maxWidth: .infinity)` | Expand to available space |

**Decision rules:**

1. **Use fixed `width:`** when component must be exact size (icons, badges, specific design constraints)
2. **Use `maxWidth:`** when component should be responsive (screens narrower than design will shrink)
3. **Combine both** for responsive with constraints: `.frame(minWidth: 200, maxWidth: 361)`

```swift
// Fixed size (exact match to Figma)
.frame(width: 361, height: 80)

// Flexible width (responsive)
.frame(maxWidth: 361)
.frame(height: 80)

// Full-width card with max constraint
.frame(maxWidth: .infinity)
.frame(height: 80)

// Responsive with minimum size
.frame(minWidth: 280, maxWidth: 361, minHeight: 60, maxHeight: 80)
```

**Default recommendation:** Use fixed `width:` for components, use `maxWidth:` for screen-level containers.

---

## Corner Radius (Border Radius)

### Uniform Radius

**CSS / Tailwind:**

```tsx
// Corner Radius: 12px -> Tailwind
<div className="rounded-xl">     // 12px = rounded-xl
// OR arbitrary value
<div className="rounded-[12px]">
```

**SwiftUI:**

```swift
// From spec: Corner Radius: 12px
.clipShape(RoundedRectangle(cornerRadius: 12))
// OR
.cornerRadius(12)
```

### Per-Corner Radius

**CSS / Tailwind:**

```tsx
// Corner Radius: TL:16 TR:16 BL:0 BR:0
<div className="rounded-tl-2xl rounded-tr-2xl rounded-bl-none rounded-br-none">
// OR shorthand
<div className="rounded-t-2xl rounded-b-none">
```

**SwiftUI (iOS 16+):**

```swift
// Corner Radius: TL:16 TR:16 BL:0 BR:0
.clipShape(
  UnevenRoundedRectangle(
    topLeadingRadius: 16,
    bottomLeadingRadius: 0,
    bottomTrailingRadius: 0,
    topTrailingRadius: 16
  )
)
```

**SwiftUI (iOS 15 compatibility):**

```swift
// Use custom Shape for iOS 15 support
.clipShape(RoundedCorner(radius: 16, corners: [.topLeft, .topRight]))
```

### Corner Terminology Mapping (Figma to SwiftUI)

Figma uses geometric corners (TopLeft, TopRight); SwiftUI uses reading direction (Leading, Trailing).

| Swift Parameter (API order) | Figma/Spec | Position |
|----------------------------|------------|----------|
| `topLeadingRadius` | TL (TopLeft) | Top-left corner |
| `bottomLeadingRadius` | BL (BottomLeft) | Bottom-left corner |
| `bottomTrailingRadius` | BR (BottomRight) | Bottom-right corner |
| `topTrailingRadius` | TR (TopRight) | Top-right corner |

**Example conversion:**

```
Spec: "TL:16 TR:16 BL:0 BR:0"
->
UnevenRoundedRectangle(
  topLeadingRadius: 16,     // TL=16
  bottomLeadingRadius: 0,   // BL=0
  bottomTrailingRadius: 0,  // BR=0
  topTrailingRadius: 16     // TR=16
)
```

### Tailwind Radius Reference Table

| Figma Value | Tailwind Class | CSS Value |
|-------------|----------------|-----------|
| 0 | `rounded-none` | 0px |
| 2px | `rounded-sm` | 0.125rem |
| 4px | `rounded` | 0.25rem |
| 6px | `rounded-md` | 0.375rem |
| 8px | `rounded-lg` | 0.5rem |
| 12px | `rounded-xl` | 0.75rem |
| 16px | `rounded-2xl` | 1rem |
| 24px | `rounded-3xl` | 1.5rem |
| 9999px | `rounded-full` | 9999px |

---

## Border / Stroke Handling

### Stroke Alignment

Figma supports three stroke alignment modes, each requiring different code patterns.

#### CSS / Tailwind

```tsx
// INSIDE stroke (default CSS box model with border-box)
<div className="border border-white/40">

// With specific width
<div className="border-2 border-primary">

// Bottom-only border
<div className="border-b border-gray-200">

// With CSS variable
<div className="border border-[var(--border-color)]">
```

**Hex-Alpha Color Parsing:**

```
#FFFFFF40 -> Color: #FFFFFF, Alpha: 0x40 = 64/255 ~ 0.25 opacity
```

In Tailwind, use opacity shorthand: `border-white/25`

#### SwiftUI

| Figma Alignment | SwiftUI Pattern | Notes |
|----------------|-----------------|-------|
| INSIDE | `.overlay()` with `.stroke()` | Default, no adjustment needed |
| OUTSIDE | `.padding()` then `.overlay()` | Add padding = strokeWidth/2 |
| CENTER | `.overlay()` with `.inset()` | Stroke centered on edge |

```swift
// INSIDE stroke (default - stroke inside bounds)
.overlay(
  RoundedRectangle(cornerRadius: 12)
    .stroke(Color.white.opacity(0.4), lineWidth: 1)
)

// OUTSIDE stroke (stroke outside bounds)
.padding(1)  // Half of stroke width
.overlay(
  RoundedRectangle(cornerRadius: 12)
    .stroke(Color.white.opacity(0.4), lineWidth: 2)
)

// CENTER stroke (stroke centered on edge)
.overlay(
  RoundedRectangle(cornerRadius: 12)
    .inset(by: 0.5)  // Half of stroke width
    .stroke(Color.white.opacity(0.4), lineWidth: 1)
)
```

**SwiftUI Hex-Alpha Note:**

The Color+Hex extension uses ARGB format for 8-character hex strings (alpha first):

```
#40FFFFFF -> Alpha: 0x40 = 0.25 opacity, Color: #FFFFFF (white)
#80FF0000 -> Alpha: 0x80 = 0.50 opacity, Color: #FF0000 (red)
```

For readability, prefer `.opacity()` modifier:

```swift
Color(hex: "#FFFFFF").opacity(0.25)
```

---

## Compliance Tolerance

The compliance-checker uses the following tolerances when verifying frame properties:

| Aspect | Tolerance | Check |
|--------|-----------|-------|
| Dimensions | +/-2px | Width, height match frame properties |
| Corner Radius | Exact match | All corners match spec values |
| Border/Stroke | Exact match | Border width, color, opacity match spec |
| Spacing | +/-4px | Padding, margin, gap values match design |
| Colors | Exact hex match | Background, text, border colors identical |

---

## Complete Example

### Implementation Spec Input

```markdown
### ChecklistItemView

| Property | Value |
|----------|-------|
| **Element** | HStack |
| **Layout** | horizontal, spacing: 16 |
| **Dimensions** | `width: 361, height: 80` |
| **Corner Radius** | `12px` |
| **Border** | `1px #FFFFFF opacity:0.4 inside` |
| **Background** | `#150200` |
```

### Tailwind Output

```tsx
<div className="w-[361px] h-[80px] rounded-xl border border-white/40 bg-[#150200] flex items-center gap-4 px-4">
  {/* children */}
</div>
```

### SwiftUI Output

```swift
HStack(spacing: 16) {
    // children
}
.frame(width: 361, height: 80)
.background(Color(hex: "#150200"))
.clipShape(RoundedRectangle(cornerRadius: 12))
.overlay(
    RoundedRectangle(cornerRadius: 12)
        .stroke(Color.white.opacity(0.4), lineWidth: 1)
)
```

---

## SwiftUI Modifier Ordering

SwiftUI modifiers apply in order. The correct sequence for frame properties:

```swift
.padding()           // 1. Internal padding (affects content)
.frame()             // 2. Size constraints
.background()        // 3. Background color/gradient
.clipShape()         // 4. Clip to shape (BEFORE overlay)
.overlay()           // 5. Border stroke (AFTER clipShape)
.shadow()            // 6. Shadow (outermost)
```

**Why order matters:**

| Wrong Order | Problem |
|-------------|---------|
| `.overlay()` before `.clipShape()` | Border gets clipped, corners cut off |
| `.background()` after `.clipShape()` | Background bleeds outside rounded corners |
| `.shadow()` before `.clipShape()` | Shadow shape doesn't match clipped shape |
| `.frame()` after `.clipShape()` | Frame size may not match clipped content |

**Example — Correct modifier chain:**

```swift
HStack(spacing: 16) {
    // content
}
.padding(.horizontal, 16)        // 1. Internal padding
.frame(width: 361, height: 80)   // 2. Size
.background(Color(hex: "#150200")) // 3. Background
.clipShape(RoundedRectangle(cornerRadius: 12)) // 4. Clip
.overlay(                        // 5. Border
    RoundedRectangle(cornerRadius: 12)
        .stroke(Color.white.opacity(0.4), lineWidth: 1)
)
.shadow(color: .black.opacity(0.1), radius: 4, y: 2) // 6. Shadow
```
