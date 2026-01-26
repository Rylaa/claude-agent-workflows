# Opacity, Gradient & Layer Order Support for pb-figma Agents

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add opacity, gradient text, and correct layer order support to pb-figma agents to accurately render Figma designs with semi-transparent colors, gradient text, and proper element stacking (overlay elements on top).

**Architecture:** Enhance Design Analyst to extract opacity/gradient data from MCP, update SwiftUI Generator to apply this data correctly in generated code.

**Tech Stack:** Markdown agent files, MCP design tokens, SwiftUI LinearGradient/AngularGradient

**Context:** Root cause analysis at `docs/plans/2026-01-25-border-color-inline-text-analysis.md` confirmed MCP server works correctly - agents need updates to use the extracted data.

---

## Task 1: Add Opacity Extraction to Design Analyst

**Files:**
- Modify: `plugins/pb-figma/agents/design-analyst.md:150-160` (after Token Application section)
- Test with: Figma file `bt65gbJ6sSdKRP4x3IY151`, node `10203-16369` (has 0.4 opacity border)

**Step 1: Add Opacity Handling section to design-analyst.md**

Insert after line 150 (end of Token Application section):

```markdown
#### Opacity Handling

Extract opacity for all visual properties from `figma_get_design_tokens`:

**Query Pattern:**
```typescript
const tokens = figma_get_design_tokens({
  file_key: "{file_key}",
  node_id: "{node_id}",
  include_colors: true
});

// Extract opacity from tokens
tokens.colors.forEach(colorToken => {
  if (colorToken.opacity && colorToken.opacity < 1.0) {
    // Document in Implementation Spec
  }
});
```

**In Implementation Spec - Add Opacity Column:**
```markdown
## Design Tokens (Ready to Use)

### Colors

| Property | Color | Opacity | Usage |
|----------|-------|---------|-------|
| Border | #ffffff | 0.4 | `.stroke(Color.white.opacity(0.4))` |
| Background | #150200 | 1.0 | `.background(Color(hex: "#150200"))` |
| Text | #333333 | 0.9 | `.foregroundColor(Color.primary.opacity(0.9))` |
```

**Warning Conditions:**

Add to Implementation Spec if detected:

```markdown
### Design Warnings

- ⚠️ **Semi-transparent border** (opacity: 0.4): Border may appear faded over dark backgrounds. Consider increasing opacity to 0.8+ for better visibility.
- ⚠️ **Semi-transparent text** (opacity < 1.0): Text readability may be reduced. Ensure WCAG contrast ratio compliance.
```

**Opacity extraction rules:**
- `opacity: 1.0` → Don't add opacity modifier (default)
- `opacity: 0.0 - 0.99` → Add opacity column and usage example
- Border/stroke opacity < 0.8 → Add warning
- Text opacity < 1.0 → Add warning
```

**Step 2: Verify opacity extraction works**

Run: `Task(subagent_type="general-purpose", prompt="Test design-analyst with Figma file bt65gbJ6sSdKRP4x3IY151 node 10203-16369, check if opacity 0.4 is extracted to Implementation Spec")`

Expected: Implementation Spec shows Border with opacity column: 0.4

**Step 3: Commit opacity extraction**

```bash
git add plugins/pb-figma/agents/design-analyst.md
git commit -m "feat(design-analyst): extract opacity from design tokens

- Add Opacity Handling section after Token Application
- Extract opacity values from figma_get_design_tokens
- Add opacity column to Design Tokens table in Implementation Spec
- Add warnings for semi-transparent borders and text
- Document opacity < 1.0 in Usage column with .opacity() modifier

Resolves border color issue: agents now know about 40% opacity"
```

---

## Task 2: Add Opacity Application to SwiftUI Generator

**Files:**
- Modify: `plugins/pb-figma/agents/code-generator-swiftui.md:171-180` (after Apply Design Tokens section)
- Test with: Implementation Spec from Task 1 (should have opacity column)

**Step 1: Add "Apply Opacity from Spec" section to code-generator-swiftui.md**

Insert after line 171 (end of Apply Design Tokens section):

```markdown
##### Apply Opacity from Spec

**Read opacity from Implementation Spec Design Tokens table:**

When Implementation Spec includes Opacity column:

```markdown
| Property | Color | Opacity | Usage |
|----------|-------|---------|-------|
| Border | #ffffff | 0.4 | `.stroke(Color.white.opacity(0.4))` |
```

**Generate SwiftUI code with opacity modifier:**

```swift
// Border with opacity from spec
RoundedRectangle(cornerRadius: 12)
    .stroke(Color.white.opacity(0.4), lineWidth: 1.0)

// Background with opacity
Rectangle()
    .fill(Color(hex: "#150200").opacity(0.8))

// Text with opacity
Text(title)
    .foregroundColor(Color(hex: "#333333").opacity(0.9))
```

**CRITICAL RULES:**

1. **Never ignore opacity values** - they are intentional design choices
2. **Read from Opacity column** - don't hardcode `opacity(1.0)`
3. **Default to 1.0** - if Opacity column missing, don't add `.opacity()` modifier
4. **Copy from Usage column** - Implementation Spec shows exact SwiftUI code

**Common mistake to avoid:**

```swift
// ❌ WRONG - Ignoring opacity from spec
.stroke(Color.white, lineWidth: 1.0)

// ✅ CORRECT - Applying opacity from spec
.stroke(Color.white.opacity(0.4), lineWidth: 1.0)
```
```

**Step 2: Test opacity application**

Run: `Task(subagent_type="code-generator-swiftui", prompt="Generate SwiftUI code for node 10203-16369 using Implementation Spec with opacity, verify border uses .opacity(0.4)")`

Expected: Generated code contains `.stroke(Color.white.opacity(0.4), lineWidth: 1.0)`

**Step 3: Commit opacity application**

```bash
git add plugins/pb-figma/agents/code-generator-swiftui.md
git commit -m "feat(code-generator-swiftui): apply opacity from Implementation Spec

- Add 'Apply Opacity from Spec' section after Apply Design Tokens
- Read opacity values from Design Tokens table
- Generate .opacity() modifier for colors with opacity < 1.0
- Add critical rules and common mistakes section
- Document exact SwiftUI syntax from Usage column

Resolves grimsi border rendering: generated code now includes .opacity(0.4)"
```

---

## Task 3: Add Gradient Detection to Design Analyst

**Files:**
- Modify: `plugins/pb-figma/agents/design-analyst.md:160-220` (after Opacity Handling section)
- Test with: Figma file `bt65gbJ6sSdKRP4x3IY151`, text node with 7-color angular gradient

**Step 1: Add Gradient Detection section to design-analyst.md**

Insert after Opacity Handling section:

```markdown
#### Gradient Detection

Extract gradient fills from text nodes via `figma_get_design_tokens`:

**Query Pattern:**
```typescript
const tokens = figma_get_design_tokens({
  file_key: "{file_key}",
  node_id: "{node_id}",
  include_typography: true
});

// Extract gradients from typography tokens
tokens.typography.forEach(textToken => {
  if (textToken.gradient) {
    // Document gradient in Implementation Spec
  }
});
```

**Gradient Types from Figma:**
- `LINEAR` - Linear gradient with angle
- `RADIAL` - Radial gradient from center
- `ANGULAR` - Conic/angular gradient (rainbow effect)
- `DIAMOND` - Diamond-shaped gradient

**In Implementation Spec - Add Gradient Section:**

```markdown
### Text with Gradient

**Component:** HeadingText
- **Gradient Type:** ANGULAR
- **Stops:**
  - 0.1673: #bc82f3 (opacity: 1.0)
  - 0.2365: #f4b9ea (opacity: 1.0)
  - 0.3518: #8d98ff (opacity: 1.0)
  - 0.5815: #aa6eee (opacity: 1.0)
  - 0.697: #ff6777 (opacity: 1.0)
  - 0.8095: #ffba71 (opacity: 1.0)
  - 0.9241: #c686ff (opacity: 1.0)

**SwiftUI Mapping:** `AngularGradient` with 7 color stops
**Minimum iOS:** iOS 15.0+
```

**Add to Compliance Section:**

```markdown
### Platform Requirements

- **Gradient Text:** Requires iOS 15.0+ / macOS 12.0+ for `AngularGradient` on Text
- **Performance:** Complex gradients (5+ stops) may impact rendering performance

### Design Warnings

- ⚠️ **Gradient text detected:** Angular gradient with 7 color stops requires iOS 15+. Consider simpler gradients (2-3 stops) for better performance.
```

**Gradient extraction rules:**
- Text node with `gradient` field → Add "Text with Gradient" section
- Include ALL gradient stops with position, color, opacity
- Add platform requirement (iOS 15+) to Compliance section
- Warn if gradient has 5+ stops (performance impact)
- Map Figma gradient type to SwiftUI equivalent
```

**Step 2: Test gradient extraction**

Run: `Task(subagent_type="general-purpose", prompt="Test design-analyst with Figma file bt65gbJ6sSdKRP4x3IY151, find text node with gradient, verify all 7 color stops extracted to Implementation Spec")`

Expected: Implementation Spec has "Text with Gradient" section with 7 color stops

**Step 3: Commit gradient detection**

```bash
git add plugins/pb-figma/agents/design-analyst.md
git commit -m "feat(design-analyst): detect and extract gradient text

- Add Gradient Detection section after Opacity Handling
- Extract gradient type and color stops from figma_get_design_tokens
- Add 'Text with Gradient' section to Implementation Spec
- Document all gradient stops with positions and colors
- Add platform requirements (iOS 15+) to Compliance section
- Add performance warning for complex gradients (5+ stops)
- Map Figma gradient types to SwiftUI equivalents

Resolves gradient text extraction: agents now know about angular gradients"
```

---

## Task 4: Add Gradient Rendering to SwiftUI Generator

**Files:**
- Modify: `plugins/pb-figma/agents/code-generator-swiftui.md:180-250` (after Apply Opacity section)
- Test with: Implementation Spec from Task 3 (should have gradient section)

**Step 1: Add "Apply Gradients from Spec" section to code-generator-swiftui.md**

Insert after Apply Opacity section:

```markdown
##### Apply Gradients from Spec

**Read gradient from Implementation Spec "Text with Gradient" section:**

When Implementation Spec includes gradient on text:

```markdown
### Text with Gradient

**Component:** HeadingText
- **Gradient Type:** ANGULAR
- **Stops:**
  - 0.1673: #bc82f3
  - 0.9241: #c686ff
```

**Generate SwiftUI code with appropriate gradient:**

```swift
// Linear Gradient (2 stops)
Text("Gradient Text")
    .foregroundStyle(
        LinearGradient(
            stops: [
                Gradient.Stop(color: Color(hex: "#ff0000"), location: 0.0),
                Gradient.Stop(color: Color(hex: "#0000ff"), location: 1.0)
            ],
            startPoint: .leading,
            endPoint: .trailing
        )
    )

// Angular Gradient (rainbow effect)
Text("Type a scene to generate your video")
    .foregroundStyle(
        AngularGradient(
            stops: [
                Gradient.Stop(color: Color(hex: "#bc82f3"), location: 0.1673),
                Gradient.Stop(color: Color(hex: "#f4b9ea"), location: 0.2365),
                Gradient.Stop(color: Color(hex: "#8d98ff"), location: 0.3518),
                Gradient.Stop(color: Color(hex: "#aa6eee"), location: 0.5815),
                Gradient.Stop(color: Color(hex: "#ff6777"), location: 0.697),
                Gradient.Stop(color: Color(hex: "#ffba71"), location: 0.8095),
                Gradient.Stop(color: Color(hex: "#c686ff"), location: 0.9241)
            ],
            center: .center
        )
    )

// Radial Gradient
Text("Radial Text")
    .foregroundStyle(
        RadialGradient(
            stops: [
                Gradient.Stop(color: Color(hex: "#ff0000"), location: 0.0),
                Gradient.Stop(color: Color(hex: "#0000ff"), location: 1.0)
            ],
            center: .center,
            startRadius: 0,
            endRadius: 100
        )
    )
```

**Gradient Type Mapping:**

| Figma Type | SwiftUI Type | Parameters |
|------------|--------------|------------|
| `LINEAR` | `LinearGradient` | `startPoint`, `endPoint` (from angle) |
| `RADIAL` | `RadialGradient` | `center`, `startRadius: 0`, `endRadius` |
| `ANGULAR` | `AngularGradient` | `center` |
| `DIAMOND` | `AngularGradient` | `center` (closest equivalent) |

**Angle to StartPoint/EndPoint Conversion (for LINEAR):**

```swift
// 0° = left to right
angle == 0° → startPoint: .leading, endPoint: .trailing

// 90° = top to bottom
angle == 90° → startPoint: .top, endPoint: .bottom

// 180° = right to left
angle == 180° → startPoint: .trailing, endPoint: .leading

// 270° = bottom to top
angle == 270° → startPoint: .bottom, endPoint: .top
```

**Add iOS version requirement to file header:**

```swift
// MARK: - Component Name
// Requires iOS 15.0+ for gradient text support

import SwiftUI

struct ComponentName: View {
    var body: some View {
        Text("Gradient Text")
            .foregroundStyle(/* gradient from spec */)
    }
}
```

**CRITICAL RULES:**

1. **Read gradient stops from Implementation Spec** - include ALL stops with exact positions
2. **Use .foregroundStyle()** - NOT .foregroundColor() (iOS 15+)
3. **Add Color(hex:) extension** - if not already in project
4. **Document iOS 15+ requirement** - in file header comment
5. **Map gradient type correctly** - use table above

**Common mistakes to avoid:**

```swift
// ❌ WRONG - Using .foregroundColor() for gradient
Text("Gradient")
    .foregroundColor(Color.red) // Can't use gradient

// ✅ CORRECT - Using .foregroundStyle() for gradient
Text("Gradient")
    .foregroundStyle(
        AngularGradient(stops: [...], center: .center)
    )

// ❌ WRONG - Missing color stops from spec
AngularGradient(
    stops: [
        Gradient.Stop(color: Color(hex: "#bc82f3"), location: 0.0),
        Gradient.Stop(color: Color(hex: "#c686ff"), location: 1.0)
    ], // Only 2 stops, spec has 7!
    center: .center
)

// ✅ CORRECT - All 7 stops from spec
AngularGradient(
    stops: [
        Gradient.Stop(color: Color(hex: "#bc82f3"), location: 0.1673),
        Gradient.Stop(color: Color(hex: "#f4b9ea"), location: 0.2365),
        Gradient.Stop(color: Color(hex: "#8d98ff"), location: 0.3518),
        Gradient.Stop(color: Color(hex: "#aa6eee"), location: 0.5815),
        Gradient.Stop(color: Color(hex: "#ff6777"), location: 0.697),
        Gradient.Stop(color: Color(hex: "#ffba71"), location: 0.8095),
        Gradient.Stop(color: Color(hex: "#c686ff"), location: 0.9241)
    ],
    center: .center
)
```
```

**Step 2: Test gradient rendering**

Run: `Task(subagent_type="code-generator-swiftui", prompt="Generate SwiftUI code for text with 7-color angular gradient using Implementation Spec, verify all 7 stops included in AngularGradient")`

Expected: Generated code has `AngularGradient` with all 7 `Gradient.Stop` entries

**Step 3: Commit gradient rendering**

```bash
git add plugins/pb-figma/agents/code-generator-swiftui.md
git commit -m "feat(code-generator-swiftui): render gradient text from Implementation Spec

- Add 'Apply Gradients from Spec' section after Apply Opacity
- Support LinearGradient, RadialGradient, AngularGradient
- Map Figma gradient types to SwiftUI types
- Convert LINEAR angles to startPoint/endPoint
- Generate all gradient stops from Implementation Spec
- Add iOS 15+ requirement to file header
- Use .foregroundStyle() instead of .foregroundColor()
- Add critical rules and common mistakes section

Resolves gradient text rendering: generated code now includes AngularGradient"
```

---

## Task 5: Add Color(hex:) Extension Helper (if needed)

**Files:**
- Create: `Extensions/Color+Hex.swift` (in SwiftUI project, not in pb-figma plugin)
- Note: This is generated code output, not agent file

**Step 1: Check if Color(hex:) extension exists**

Run: `Grep(pattern="Color.*hex.*init", path="**/*.swift")`

**If NOT found:**

**Step 2: Add to code-generator-swiftui.md guidance**

Add to "Files Created" section template:

```markdown
### Extensions (if created)
- `Extensions/Color+Hex.swift` - Color hex initializer for design tokens
```

**Step 3: Document Color+Hex.swift generation**

Add to code-generator-swiftui.md after "SwiftUI Component Structure":

```markdown
### Color+Hex Extension

If generated code uses `Color(hex:)` and extension doesn't exist, create:

```swift
// Extensions/Color+Hex.swift
import SwiftUI

extension Color {
    /// Initialize Color from hex string
    /// - Parameter hex: Hex string (e.g., "#FF0000" or "FF0000")
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }

        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
```

Write this file to `Extensions/Color+Hex.swift` in detected SwiftUI project.
```

**Step 4: Commit Color+Hex documentation**

```bash
git add plugins/pb-figma/agents/code-generator-swiftui.md
git commit -m "docs(code-generator-swiftui): add Color+Hex extension template

- Add Color+Hex extension template for hex color parsing
- Support 3, 6, and 8 character hex strings
- Include in 'Extensions (if created)' section
- Auto-generate if Color(hex:) is used in generated code

Enables hex colors from design tokens in generated SwiftUI code"
```

---

## Task 6: Integration Test - Full Pipeline

**Files:**
- Test with: Figma file `bt65gbJ6sSdKRP4x3IY151`, node `10203-16369`
- Expected output: Implementation Spec + SwiftUI code with opacity and gradient

**Step 1: Run full pb-figma pipeline**

Run: `/figma-to-code` with URL `https://www.figma.com/design/bt65gbJ6sSdKRP4x3IY151/Muvi?node-id=10203-16369&m=dev`

**Step 2: Verify Implementation Spec contains:**

```markdown
## Design Tokens (Ready to Use)

### Colors
| Property | Color | Opacity | Usage |
|----------|-------|---------|-------|
| Border | #ffffff | 0.4 | `.stroke(Color.white.opacity(0.4))` |

### Text with Gradient
**Component:** TypeSceneText
- **Gradient Type:** ANGULAR
- **Stops:** (7 color stops with positions)
- **Minimum iOS:** iOS 15.0+
```

**Step 3: Verify generated SwiftUI code contains:**

```swift
// Border with opacity
.stroke(Color.white.opacity(0.4), lineWidth: 1.0)

// Text with angular gradient
Text("Type a scene to generate your video")
    .foregroundStyle(
        AngularGradient(
            stops: [
                Gradient.Stop(color: Color(hex: "#bc82f3"), location: 0.1673),
                // ... all 7 stops
            ],
            center: .center
        )
    )
```

**Step 4: Visual QA**

- Border should appear semi-transparent white (grayish over dark background) ✅
- Text should render with rainbow gradient effect ✅

**Step 5: Commit integration test results**

```bash
git add docs/figma-reports/bt65gbJ6sSdKRP4x3IY151-spec.md
git add Views/Components/*.swift
git commit -m "test: verify opacity and gradient support in full pipeline

- Ran figma-to-code on file bt65gbJ6sSdKRP4x3IY151 node 10203-16369
- Implementation Spec correctly extracts opacity (0.4) and gradient (7 stops)
- Generated SwiftUI code applies opacity and AngularGradient
- Visual QA confirms border and text match Figma design

Closes border color and gradient text issues"
```

---

## Task 7: Fix Layer Order Extraction

**Files:**
- Modify: `plugins/pb-figma/agents/design-analyst.md:253-260` (Layer Order Analysis)
- Test with: Figma file `bt65gbJ6sSdKRP4x3IY151`, node `10203-16369` (PageControl overlay issue)

**Step 1: Update Layer Order extraction logic**

Replace lines 253-260 in design-analyst.md:

**Before (INCORRECT - sorts by Y coordinate):**
```typescript
// Sort by Y coordinate (top to bottom)
const sortedChildren = validChildren.sort((a, b) =>
  a.absoluteBoundingBox.y - b.absoluteBoundingBox.y
);

// Assign z-index values (higher = on top)
const layerOrder = sortedChildren.map((child, index) => ({
  layer: child.name,
  zIndex: 1000 - (index * 100),  // Top element gets highest zIndex
  position: determinePosition(child.absoluteBoundingBox.y, containerHeight),
  absoluteY: child.absoluteBoundingBox.y,
  children: child.children?.map(c => c.name) || []
}));
```

**After (CORRECT - uses children array order):**
```typescript
// Use Figma children array order (NOT Y coordinate)
// children[0] = back layer (lowest in Figma layer panel)
// children[n-1] = front layer (highest in Figma layer panel)
const layerOrder = nodeDetails.children.map((child, index) => ({
  layer: child.name,
  zIndex: (index + 1) * 100,  // First child = 100, last child = highest
  position: determinePosition(child.absoluteBoundingBox?.y, containerHeight),
  absoluteY: child.absoluteBoundingBox?.y,
  children: child.children?.map(c => c.name) || []
}));
```

**Step 2: Add Layer Order documentation**

Add explanation after the code block:

```markdown
**Why children array order, not Y coordinate?**

Figma's layer panel order != Y coordinate order. Overlay elements can have ANY Y coordinate but MUST render on top based on layer panel position.

**Example:**
- Background: Y=0 (full screen) + Layer Panel BOTTOM → zIndex 100
- PageControl: Y=60 (top of screen) + Layer Panel TOP → zIndex 300

If sorted by Y: Background gets zIndex 1000 ❌ WRONG
Using array order: Background (index 0) gets zIndex 100, PageControl (index 2) gets zIndex 300 ✅ CORRECT

**Critical:** Always use children array order for accurate layer hierarchy.
```

**Step 3: Update design-analyst.md example (line 355-381)**

Update example Implementation Spec to show correct zIndex assignment:

```yaml
layerOrder:
  - layer: Background
    zIndex: 100         # First child in Figma (index 0)
    position: full
    absoluteY: 0
    children: []

  - layer: HeroImage
    zIndex: 200         # Second child in Figma (index 1)
    position: center
    absoluteY: 300
    children: []

  - layer: PageControl
    zIndex: 300         # Third child in Figma (index 2)
    position: top
    absoluteY: 60
    children:
      - Dot1
      - Dot2
      - Dot3

  - layer: ContinueButton
    zIndex: 400         # Fourth child in Figma (index 3)
    position: bottom
    absoluteY: 800
    children: []
```

**Step 4: Verify SwiftUI Generator handles new order correctly**

SwiftUI Generator already has correct logic (no changes needed):

```swift
// code-generator-swiftui.md line 100-108
// CRITICAL: Reverse zIndex sort for SwiftUI (lowest zIndex first in code)
ZStack {
    Background()      // zIndex 100 - first = bottom
    HeroImage()       // zIndex 200 - middle
    PageControl()     // zIndex 300 - on top of HeroImage
    ContinueButton()  // zIndex 400 - last = on top ✅ CORRECT
}
```

**Step 5: Test with overlay scenario**

Run figma-to-code on file bt65gbJ6sSdKRP4x3IY151, node 10203-16369:

Expected Implementation Spec:
- layerOrder section uses children array order (not Y sort)
- PageControl has higher zIndex than background elements
- Layer order matches Figma layer panel exactly

Expected SwiftUI code:
- ZStack order: background elements first, PageControl last
- PageControl renders on top (visible to user)

**Step 6: Commit layer order fix**

```bash
git add plugins/pb-figma/agents/design-analyst.md
git commit -m "fix(design-analyst): use Figma children array order for layerOrder

BREAKING: Changes how layerOrder is extracted from Figma

Before: Sorted by absoluteBoundingBox.y coordinate
After: Uses Figma children array order directly

Why: Y coordinate != layer panel order for overlays. Overlay elements
can have any Y coordinate but must render on top based on layer panel
position. Figma API children array order represents true layer hierarchy.

Fixes PageControl overlay placement issue where controls appeared behind
content instead of on top.

Example:
- Background (children[0]) = zIndex 100 (bottom)
- PageControl (children[2]) = zIndex 300 (top)

Closes layer ordering issue in bt65gbJ6sSdKRP4x3IY151

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Success Criteria

✅ **Opacity Support:**
- [ ] Design Analyst extracts opacity from `figma_get_design_tokens`
- [ ] Implementation Spec has Opacity column in Design Tokens table
- [ ] SwiftUI Generator reads opacity and adds `.opacity()` modifier
- [ ] Generated code: `.stroke(Color.white.opacity(0.4), lineWidth: 1.0)`
- [ ] Visual QA: Border matches Figma (semi-transparent)

✅ **Gradient Support:**
- [ ] Design Analyst extracts gradient type and stops from `figma_get_design_tokens`
- [ ] Implementation Spec has "Text with Gradient" section
- [ ] SwiftUI Generator maps gradient type to SwiftUI gradient
- [ ] Generated code: `AngularGradient` with all 7 color stops
- [ ] File header includes iOS 15+ requirement
- [ ] Visual QA: Text matches Figma (rainbow gradient)

✅ **Layer Order Support:**
- [ ] Design Analyst uses children array order (NOT Y coordinate sort)
- [ ] Implementation Spec layerOrder section has correct zIndex values
- [ ] First child in Figma = lowest zIndex (100)
- [ ] Last child in Figma = highest zIndex
- [ ] SwiftUI Generator reverse sorts (lowest zIndex first in ZStack)
- [ ] Generated code: Overlay elements appear last in ZStack (on top)
- [ ] Visual QA: PageControl visible on top, matches Figma layer panel order

✅ **Integration:**
- [ ] Full pipeline (`/figma-to-code`) extracts and renders all three features
- [ ] No MCP changes needed (agents use existing MCP data correctly)
- [ ] Documentation updated with examples and common mistakes
- [ ] Overlay elements (buttons, controls) render correctly on top of content

## Related Files

- Analysis: `docs/plans/2026-01-25-border-color-inline-text-analysis.md`
- Design Analyst: `plugins/pb-figma/agents/design-analyst.md`
- SwiftUI Generator: `plugins/pb-figma/agents/code-generator-swiftui.md`

## Notes

- **No MCP changes needed** - MCP already extracts opacity and gradients correctly
- **Agent layer only** - All changes are in markdown agent instruction files
- **Backward compatible** - Existing designs without opacity/gradients unaffected
- **iOS 15+ requirement** - Gradient text requires modern SwiftUI
