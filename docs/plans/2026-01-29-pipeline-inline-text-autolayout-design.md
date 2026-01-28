# Pipeline Improvements: Inline Text Variations, Text Sizing & Adaptive Layout

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix pipeline gaps that cause inline text color loss, text truncation, and add tablet-adaptive layout support.

**Architecture:** Changes span 4 pipeline agents (design-validator, design-analyst, code-generator-swiftui, compliance-checker) with backward-compatible additions — no existing behavior removed.

**Tech Stack:** Figma REST API (characterStyleOverrides, styleOverrideTable, textAutoResize, Auto Layout), SwiftUI adaptive patterns (horizontalSizeClass, maxWidth, LazyVGrid)

---

## Background

Comparing Figma design vs generated code for the viralZ AI Analysis screen revealed 3 pipeline gaps:

1. **Inline text color lost:** "Hook" word should be yellow (#F2F20D) with underline, but generated as white. Root cause: design-analyst's `characterStyleOverrides` detection didn't trigger because design-validator didn't flag inline variations.

2. **Text truncation:** Description text shows as single truncated line instead of 2 full lines. Root cause: spec doesn't include `textAutoResize` mode or text frame dimensions for proper sizing.

3. **No tablet support:** Pipeline generates fixed-width layouts only. No adaptive patterns for iPad/tablet screen sizes.

Icon sizes (originally Madde 3) were verified correct — no pipeline change needed.

---

## Change 1: Inline Text Color Detection (characterStyleOverrides)

### Problem

Figma REST API provides per-character style overrides via:
- `characterStyleOverrides`: array mapping each character to a style override index
- `styleOverrideTable`: dictionary mapping override indices to style properties (fills, fontWeight, textDecoration, etc.)

The design-analyst agent (lines 565-639) already has logic to build an "Inline Text Variations" table from these fields. However, this logic only triggers when the design-validator flags the text node as having inline variations. Currently, design-validator does NOT check for `characterStyleOverrides`.

### Solution

**Agent: design-validator**

Add a check for `characterStyleOverrides` on text nodes. When a text node has a non-empty `characterStyleOverrides` array with at least one non-zero value, flag it in the validation report:

```markdown
### Inline Text Variations Detected
| Node ID | Text Content | Override Count | Unique Styles |
|---------|-------------|----------------|---------------|
| 3:150   | "Let's fix your Hook" | 4 chars | 1 unique override (fills: #F2F20D, textDecoration: UNDERLINE) |
```

**Agent: design-analyst**

No logic change needed — the existing Inline Text Variations detection (lines 565-639) already handles `characterStyleOverrides` correctly. It will trigger once design-validator provides the flag.

However, add a defensive note: if `styleOverrideTable` returns empty objects `{}` for some overrides (known Figma API bug), treat those characters as using the node's base style.

**Known Figma API Bug:** `styleOverrideTable` sometimes returns `{}` for default-value overrides instead of explicit values. The design-analyst should document this: when an override index maps to `{}`, use the text node's base style (fills, fontSize, fontWeight from the node itself).

---

## Change 2: Text Auto-Resize Mode & Frame Dimensions

### Problem

Text nodes in Figma have a `textAutoResize` property that controls sizing behavior:
- `NONE`: Fixed frame, text may clip
- `HEIGHT`: Width fixed, height auto-adjusts to content
- `WIDTH_AND_HEIGHT`: Both dimensions auto-adjust
- `TRUNCATE`: Fixed frame, text truncated with ellipsis

The spec currently doesn't include this property or the text frame's absolute dimensions. Without this info, the code generator can't determine if text should wrap, truncate, or auto-size.

### Solution

**Agent: design-analyst**

Add to text property extraction (in the component spec):

```markdown
- Auto-Resize: `HEIGHT` (width fixed at 311pt, height adjusts to content)
- Frame Dimensions: 311 × 38 (allows ~2 lines at font size 14)
- Line Count Hint: 2 lines (based on frame height / lineHeight)
```

Properties to extract from Figma API:
- `textAutoResize`: NONE | HEIGHT | WIDTH_AND_HEIGHT | TRUNCATE
- `absoluteBoundingBox.width` and `absoluteBoundingBox.height`: actual frame dimensions
- Calculate approximate line count: `floor(frameHeight / (fontSize * lineHeightMultiplier))`

**Agent: code-generator-swiftui**

When generating text views, use the auto-resize info:
- `HEIGHT` or `WIDTH_AND_HEIGHT`: No `.lineLimit()` needed (default behavior)
- `TRUNCATE`: Add `.lineLimit(N)` where N = calculated line count hint
- `NONE`: Add `.frame(width:height:)` with exact dimensions and `.clipped()`

Also: when frame dimensions suggest multi-line text (lineCountHint > 1), ensure no implicit `.lineLimit(1)` is applied and add `.fixedSize(horizontal: false, vertical: true)` if needed.

---

## Change 3: AutoLayout & Tablet Adaptive Support

### Problem

Current pipeline generates static layouts targeting iPhone screen width. On iPad:
- Content stretches to full width (poor readability)
- Card lists remain single-column (wasted space)
- No responsive breakpoints

### Solution — 3 Layers

#### Layer 1: Design-Validator — Auto Layout Property Detection

Add Figma Auto Layout properties to the validation checklist:

```markdown
### Auto Layout Properties
| Node ID | Layout Mode | Primary Axis | Counter Axis | Padding | Spacing | Min/Max Width |
|---------|-------------|-------------|--------------|---------|---------|---------------|
| 3:100   | VERTICAL    | SPACE_BETWEEN | CENTER      | 16,16,16,16 | 16 | min: 0, max: INF |
```

Properties to extract:
- `layoutMode`: NONE | HORIZONTAL | VERTICAL
- `primaryAxisAlignItems`: MIN | CENTER | MAX | SPACE_BETWEEN
- `counterAxisAlignItems`: MIN | CENTER | MAX | BASELINE
- `paddingLeft/Right/Top/Bottom`
- `itemSpacing`
- `constraints`: horizontal/vertical (MIN, CENTER, MAX, STRETCH, SCALE)
- `minWidth`, `maxWidth`, `minHeight`, `maxHeight`

#### Layer 2: Code-Generator-SwiftUI — Adaptive Layout Patterns

Add a new section to code-generator-swiftui.md for adaptive layout generation:

**Rule 1 — Content Width Cap:**
All top-level content containers get:
```swift
.frame(maxWidth: 600)
.frame(maxWidth: .infinity)
```
This centers content on iPad while filling iPhone screens.

**Rule 2 — Card Lists Adaptive Grid:**
When a VStack contains 3+ card-like children with identical structure:
```swift
let columns = [GridItem(.adaptive(minimum: 280, maximum: 400))]
LazyVGrid(columns: columns, spacing: 16) {
    ForEach(items) { item in
        CardView(item: item)
    }
}
```
This auto-adjusts to 2 columns on iPad, 1 column on iPhone.

**Rule 3 — Size Class Detection:**
When the spec contains responsive hints or the layout has major structural changes for tablet:
```swift
@Environment(\.horizontalSizeClass) var horizontalSizeClass

var body: some View {
    if horizontalSizeClass == .regular {
        // iPad layout
    } else {
        // iPhone layout (default)
    }
}
```

**Rule 4 — Safe Defaults:**
- Never use hardcoded screen-width values (`UIScreen.main.bounds.width`)
- Prefer `.frame(maxWidth: .infinity)` over fixed widths
- Use `.padding(.horizontal)` for edge spacing (auto-adjusts)

#### Layer 3: Compliance-Checker — Tablet Verification

Add optional iPad verification step:

```markdown
### Step 7 (Optional): Tablet Layout Verification
- Check that content containers have maxWidth cap (≤700pt)
- Verify no hardcoded UIScreen references
- Check that card lists use adaptive grid when 3+ items
- Flag any fixed-width values > 400pt as potential tablet issues
```

This is a code-level check (no iPad screenshot needed for v1).

---

## Summary

| Change | Agent(s) | Type | Risk |
|--------|----------|------|------|
| 1. Inline text color | design-validator, design-analyst | Bug fix | Low — additive check |
| 2. Text auto-resize | design-analyst, code-generator-swiftui | Bug fix | Low — new spec fields |
| 3. AutoLayout + tablet | all 4 agents | Feature | Medium — new layout patterns |

**Total files to modify:** 4 agent markdown files
**New files:** None (all changes are inline additions to existing agents)
**Backward compatible:** Yes — all changes are additive; existing behavior preserved
