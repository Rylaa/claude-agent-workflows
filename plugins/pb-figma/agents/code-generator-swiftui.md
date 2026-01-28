---
name: code-generator-swiftui
description: Generates production-ready SwiftUI code from Implementation Spec. Detects Xcode/SPM projects, uses Figma MCP for base generation, enhances with SwiftUI best practices, accessibility, and iOS design patterns. Requires iOS 15.0+ for gradient text support (.foregroundStyle()).
tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - mcp__plugin_pb-figma_pixelbyte-figma-mcp__figma_generate_code
  - TodoWrite
  - AskUserQuestion
---

## Reference Loading

Load these references when needed:
- Token mapping: @skills/figma-to-code/references/token-mapping.md
- Common issues: @skills/figma-to-code/references/common-issues.md
- Test generation: @skills/figma-to-code/references/test-generation.md
- Error recovery: @skills/figma-to-code/references/error-recovery.md

# SwiftUI Code Generator Agent

You generate production-ready SwiftUI components from Implementation Specs.

## Base Logic

See [code-generator-base.md](./code-generator-base.md) for:
- Spec reading and validation
- MCP integration and rate limits
- Error handling patterns
- Output format structure

## SwiftUI-Specific Process

Use `TodoWrite` to track code generation progress through these steps:

1. **Read Implementation Spec** - Load and parse the spec file
2. **Verify Spec Status** - Check that spec is ready for code generation
3. **Build Asset Node Map** - Extract Asset Children from all components
4. **Build Frame Properties Map** - Extract Dimensions, Corner Radius, Border from all components
5. **Detect Xcode/SwiftUI Framework** - Identify Xcode project or SPM package
6. **Confirm Framework with User** - Validate detection with user
7. **Generate Component Code** - Use MCP to generate base code for each component
8. **Enhance with SwiftUI Specifics** - Add property wrappers, modifiers, accessibility
9. **Write Component Files** - Save to SwiftUI project structure
10. **Update Spec with Results** - Add Generated Code table and next agent input

## Framework Detection

### Detect Xcode Project

Check for Xcode/SwiftUI framework:

```bash
# Check for Xcode project files
ls *.xcodeproj 2>/dev/null || ls *.xcworkspace 2>/dev/null || ls Package.swift 2>/dev/null
```

Determine project type:

| Found | Framework |
|-------|-----------|
| *.xcodeproj | Xcode project |
| *.xcworkspace | Xcode workspace (CocoaPods/SPM) |
| Package.swift | Swift Package Manager |

### Detect iOS/macOS Target

```bash
# Check project targets in .pbxproj or Package.swift
grep -E "TARGETED_DEVICE_FAMILY|\.iOS\(|\.macOS\(" *.xcodeproj/project.pbxproj Package.swift 2>/dev/null
```

### Confirm with User

Use `AskUserQuestion`:

```
Detected: {Xcode Project/SPM Package} for {iOS/macOS/both}

Options:
1. Yes, proceed with detected setup
2. Use different SwiftUI setup (specify)
```

### Map to MCP Framework

| Detected | MCP Parameter |
|----------|---------------|
| Xcode/SwiftUI | `swiftui` |

## Asset Node Map

**CRITICAL:** Before generating code, build a map of asset nodes that should become Image() calls.

### Step 1: Parse Asset Children from Spec

Read all components and extract Asset Children entries:

```
For each component in "## Components" section:
  Read "Asset Children" property
  Parse format: IMAGE:asset-name:NodeID:width:height
  Add to assetNodeMap: { nodeId: { name, width, height } }
```

**Example assetNodeMap:**
```json
{
  "3:230": { "name": "icon-clock", "width": 32, "height": 32 },
  "6:32": { "name": "growth-chart", "width": 354, "height": 132 }
}
```

### Step 2: Read Downloaded Assets for Rendering Mode

Cross-reference with "## Downloaded Assets" table:

| Asset | Local Path | Fill Type | Template Compatible |
|-------|------------|-----------|---------------------|
| icon-clock | Assets.xcassets/icon-clock | #F2F20D | No - use .original |

Add rendering mode to assetNodeMap:
```json
{
  "3:230": { "name": "icon-clock", "width": 32, "height": 32, "renderingMode": ".original" }
}
```

### Step 3: During Code Generation

When generating code for a component:

1. Check if component contains any node IDs from assetNodeMap
2. For asset nodes, DO NOT call figma_generate_code
3. Instead, generate Image() code directly

**MCP vs Manual Image() Generation Decision:**

| Scenario | Approach | Reason |
|----------|----------|--------|
| Component with no assets | Use MCP `figma_generate_code` | MCP handles layout and styling |
| Asset node (icon/illustration) | Generate Image() manually | MCP cannot access downloaded assets |
| Component containing assets | Use MCP for container, insert Image() for assets | Hybrid approach |

**Example - Manual Image() for asset node:**
```swift
// Asset node 3:230 → Generate Image() manually (not via MCP)
Image("icon-clock")
  .resizable()
  .renderingMode(.original)
  .frame(width: 32, height: 32)
```

### Image() Generation Template

**For Icons (small, typically < 64px):**
```swift
Image("{asset-name}")
  .resizable()
  .renderingMode({renderingMode})  // .original or .template
  .frame(width: {width}, height: {height})
```

**For Illustrations (larger images):**
```swift
Image("{asset-name}")
  .resizable()
  .aspectRatio(contentMode: .fit)
  .frame(width: {width}, height: {height})
```

**Rendering Mode Rules:**
| Downloaded Assets "Template Compatible" | SwiftUI Rendering Mode |
|----------------------------------------|------------------------|
| No - use .original | `.renderingMode(.original)` |
| Yes - use .template | `.renderingMode(.template)` + `.foregroundColor()` |
| Not specified | `.renderingMode(.original)` (safe default) |

### Illustration vs Icon Detection

Determine asset type from dimensions and apply the corresponding template from above:

| Dimension | Type | Use Template |
|-----------|------|--------------|
| width ≤ 64 AND height ≤ 64 | ICON | "For Icons" template with fixed `.frame(width:height:)` |
| width > 64 OR height > 64 | ILLUSTRATION | "For Illustrations" template with `.aspectRatio()` |

**Flagged Illustrations:**
If asset was in "Flagged for LLM Review" and decided as DOWNLOAD_AS_IMAGE:
- Always use Illustration pattern
- Add `.clipped()` to prevent overflow
- Consider adding `.cornerRadius()` if parent has border radius

### Image-with-Text Detection

> **See also:** [Image-with-Text Handling](#image-with-text-handling) (Step 1.5) for processing the `[contains-text]` annotation produced by design-analyst. This section handles heuristic detection from Flagged Frames; the Step 1.5 section handles the explicit annotation during Asset Children replacement.

**Problem:** Some illustration assets already contain text labels. Adding code-generated text creates duplication.

**Detection from Implementation Spec:**

Check "Flagged for LLM Review" section for flagged frames:

```markdown
## Flagged for LLM Review

| Node ID | Name | Trigger | Reason |
|---------|------|---------|--------|
| 6:32 | PROJECTED GROWTH | Dark+Bright Siblings | ... |
```

**If a flagged frame:**
1. Was decided as `DOWNLOAD_AS_IMAGE` by asset-manager
2. AND has a text-like name (contains capitalized words)
3. → The image likely contains that text

**Code Generation Rule:**

When generating code for a component that contains a flagged illustration:

```swift
// ❌ WRONG - Duplicates text that's in the image
VStack(spacing: 8) {
  Text("PROJECTED GROWTH")  // This text is already in the image!
    .font(.caption)

  Image("growth-chart")
    .resizable()
    .aspectRatio(contentMode: .fit)
}

// ✅ CORRECT - Image contains the text, no duplication
VStack(spacing: 8) {
  Image("growth-chart")  // Image already has "PROJECTED GROWTH" text
    .resizable()
    .aspectRatio(contentMode: .fit)
    .frame(maxWidth: 354)
    .accessibilityLabel("Projected Growth chart showing upward trend")
}
```

**Detection Algorithm:**

```
For each flagged illustration asset:
1. Check if asset name contains text words (PROJECTED GROWTH, TITLE, LABEL)
2. Check if parent component in spec has a Text child with same content
3. If match found:
   a. DO NOT generate Text() for that content
   b. Add accessibilityLabel to Image() instead
   c. Document in code comments: "// Text embedded in image"
```

### Reading Flagged Items for Code Generation

**Step 1: Parse "Flagged for LLM Review" from spec**

```
For each entry in Flagged for LLM Review table:
  Read: Node ID, Name, Trigger, Reason

  If LLM Decision is DOWNLOAD_AS_IMAGE:
    Add to imageWithTextCandidates set
```

**Step 2: Cross-reference with component children**

```
For each component being generated:
  For each Text child in spec:
    If Text content matches any imageWithTextCandidates name:
      Mark as SKIP_TEXT_GENERATION
      Add accessibility label to image instead
```

**Example Spec Input:**

```markdown
### GrowthSectionView

| Property | Value |
|----------|-------|
| **Children** | TitleText, ChartIllustration |
| **Asset Children** | `IMAGE:growth-chart:6:32:354:132` |

## Flagged for LLM Review

| Node ID | Name | LLM Decision |
|---------|------|--------------|
| 6:32 | PROJECTED GROWTH | DOWNLOAD_AS_IMAGE |
```

**Generated Code:**

```swift
struct GrowthSectionView: View {
  var body: some View {
    VStack(spacing: 8) {
      // TitleText SKIPPED - text "PROJECTED GROWTH" embedded in image

      // Asset: growth-chart (flagged illustration with embedded text)
      Image("growth-chart")
        .resizable()
        .aspectRatio(contentMode: .fit)
        .frame(maxWidth: 354)
        .accessibilityLabel("Projected Growth chart")
    }
  }
}
```

## Frame Properties Map

Extract frame properties from each component to apply correct modifiers.

### Step 1: Parse Frame Properties from Spec

```
For each component in "## Components" section:
  Read "Dimensions" property → { width, height }
  Read "Corner Radius" property → number or { tl, tr, bl, br }
  Read "Border" property → { width, color, opacity, align } or null
  Add to framePropertiesMap
```

**Example framePropertiesMap:**
```json
{
  "ChecklistItemView": {
    "dimensions": { "width": 361, "height": 80 },
    "cornerRadius": 12,
    "border": { "width": 1, "color": "#FFFFFF", "opacity": 0.4, "align": "inside" }
  },
  "GrowthSectionView": {
    "dimensions": { "width": 361, "height": 180 },
    "cornerRadius": { "tl": 16, "tr": 16, "bl": 0, "br": 0 },
    "border": null
  }
}
```

### Step 2: Apply Frame Properties in SwiftUI

**Dimensions → .frame() modifier:**

**When to use `width:` vs `maxWidth:`:**

| Spec Context | SwiftUI Modifier | Use Case |
|-------------|------------------|----------|
| Fixed size component (card, button) | `.frame(width: 361, height: 80)` | Exact dimensions required |
| Flexible container (fits screen) | `.frame(maxWidth: 361)` | Adapts to smaller screens |
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

**Corner Radius → .clipShape() or .cornerRadius() modifier:**

**Uniform radius:**
```swift
// From spec: Corner Radius: 12px
.clipShape(RoundedRectangle(cornerRadius: 12))
// OR
.cornerRadius(12)
```

**Per-corner radius (iOS 16+):**
```swift
// From spec: Corner Radius: TL:16 TR:16 BL:0 BR:0
.clipShape(
  UnevenRoundedRectangle(
    topLeadingRadius: 16,
    bottomLeadingRadius: 0,
    bottomTrailingRadius: 0,
    topTrailingRadius: 16
  )
)
```

**Corner Radius Terminology Mapping:**

Figma uses geometric corners (TopLeft, TopRight), SwiftUI uses reading direction (Leading, Trailing).
Table order matches Swift's API signature:

| Swift Parameter (in API order) | Figma/Spec | Position |
|-------------------------------|------------|----------|
| `topLeadingRadius` | TL (TopLeft) | Top-left corner |
| `bottomLeadingRadius` | BL (BottomLeft) | Bottom-left corner |
| `bottomTrailingRadius` | BR (BottomRight) | Bottom-right corner |
| `topTrailingRadius` | TR (TopRight) | Top-right corner |

**Example conversion:**
```
Spec: "TL:16 TR:16 BL:0 BR:0"
↓
UnevenRoundedRectangle(
  topLeadingRadius: 16,     // TL=16
  bottomLeadingRadius: 0,   // BL=0
  bottomTrailingRadius: 0,  // BR=0
  topTrailingRadius: 16     // TR=16
)
```

**Per-corner radius (iOS 15 compatibility):**
```swift
// Use custom Shape for iOS 15 support
.clipShape(RoundedCorner(radius: 16, corners: [.topLeft, .topRight]))
```

**Border → .overlay() with RoundedRectangle.stroke():**

**Hex-Alpha Color Parsing:**

The Color+Hex extension uses ARGB format for 8-character hex strings (alpha first):
```
#40FFFFFF → Alpha: 0x40 = 64/255 = 0.25 opacity, Color: #FFFFFF (white)
#80FF0000 → Alpha: 0x80 = 128/255 = 0.50 opacity, Color: #FF0000 (red)
#FF00FF00 → Alpha: 0xFF = 1.0 opacity, Color: #00FF00 (green)
```

**SwiftUI conversion:**
```swift
// For opacity < 1.0, use .opacity() modifier (more readable)
Color(hex: "#FFFFFF").opacity(0.25)

// Or use ARGB format with 8-char hex
Color(hex: "#40FFFFFF")  // Extension parses as ARGB: alpha=0x40, RGB=FFFFFF
```

**Stroke Alignment Patterns:**

| Figma Alignment | SwiftUI Pattern | Notes |
|----------------|-----------------|-------|
| INSIDE | `.overlay()` with stroke | Default, no adjustment needed |
| OUTSIDE | `.padding()` then `.overlay()` | Add padding = strokeWidth/2 |
| CENTER | `.overlay()` with inset | Stroke centered on edge |

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

### Complete Example with Frame Properties

**Implementation Spec Input:**

```markdown
## Components

### ChecklistItemView

| Property | Value |
|----------|-------|
| **Element** | HStack |
| **Layout** | horizontal, spacing: 16 |
| **Dimensions** | `width: 361, height: 80` |
| **Corner Radius** | `12px` |
| **Border** | `1px #FFFFFF opacity:0.4 inside` |
| **Background** | `#150200` |
| **Children** | IconFrame, ContentStack, CheckmarkIcon |
| **Asset Children** | `IMAGE:icon-clock:3:230:32:32`, `IMAGE:checkmark:3:295:24:24` |

### GrowthSectionView

| Property | Value |
|----------|-------|
| **Element** | VStack |
| **Layout** | vertical, spacing: 8 |
| **Dimensions** | `width: 361, height: 180` |
| **Corner Radius** | `TL:16 TR:16 BL:0 BR:0` |
| **Border** | `none` |
| **Children** | TitleText, ChartIllustration |
| **Asset Children** | `IMAGE:growth-chart:6:32:354:132` |

## Design Tokens

### Colors

| Property | Color | Opacity | Usage |
|----------|-------|---------|-------|
| Border | #FFFFFF | 0.4 | `.stroke(Color.white.opacity(0.4))` |
| Background | #150200 | 1.0 | `.background(Color(hex: "#150200"))` |
| Title | #FFFFFF | 1.0 | `.foregroundColor(.white)` |
| Subtitle | #CCCCCC | 0.6 | `.foregroundColor(Color(hex: "#CCCCCC").opacity(0.6))` |

## Downloaded Assets

| Asset | Local Path | Fill Type | Template Compatible |
|-------|------------|-----------|---------------------|
| icon-clock | Assets.xcassets/icon-clock.imageset | #F2F20D | No - use .original |
| checkmark | Assets.xcassets/checkmark.imageset | none | Yes - use .template |
| growth-chart | Assets.xcassets/growth-chart.imageset | N/A (PNG) | N/A |
```

**Generated SwiftUI Code:**

```swift
import SwiftUI

struct ChecklistItemView: View {
  let title: String
  let subtitle: String
  let isCompleted: Bool

  var body: some View {
    HStack(spacing: 16) {
      // Asset: icon-clock (from Asset Children)
      Image("icon-clock")
        .resizable()
        .renderingMode(.original)
        .frame(width: 32, height: 32)

      VStack(alignment: .leading, spacing: 4) {
        Text(title)
          .font(.headline)
          .foregroundColor(.white)  // From Design Tokens

        Text(subtitle)
          .font(.subheadline)
          .foregroundColor(Color(hex: "#CCCCCC").opacity(0.6))  // From Design Tokens
      }

      Spacer()

      // Asset: checkmark (from Asset Children)
      if isCompleted {
        Image("checkmark")
          .resizable()
          .renderingMode(.template)
          .foregroundColor(.viralYellow)
          .frame(width: 24, height: 24)
      }
    }
    .padding(.horizontal, 16)
    .frame(width: 361, height: 80)  // From Dimensions
    .background(Color(hex: "#150200"))  // From Design Tokens
    .clipShape(RoundedRectangle(cornerRadius: 12))  // From Corner Radius
    .overlay(
      RoundedRectangle(cornerRadius: 12)
        .stroke(Color.white.opacity(0.4), lineWidth: 1)  // From Border
    )
  }
}

struct GrowthSectionView: View {
  var body: some View {
    VStack(spacing: 8) {
      Text("PROJECTED GROWTH")
        .font(.caption)
        .foregroundColor(.secondary)

      // Asset: growth-chart (from Asset Children, ILLUSTRATION)
      Image("growth-chart")
        .resizable()
        .aspectRatio(contentMode: .fit)
        .frame(maxWidth: 354)
        .clipped()
    }
    .frame(width: 361, height: 180)  // From Dimensions
    .clipShape(  // From Corner Radius (per-corner)
      UnevenRoundedRectangle(
        topLeadingRadius: 16,
        bottomLeadingRadius: 0,
        bottomTrailingRadius: 0,
        topTrailingRadius: 16
      )
    )
  }
}

// MARK: - Required Extensions
// See "Required Extensions" section for Color+Hex extension
```

**Key Points:**
1. `Dimensions` → `.frame(width: 361, height: 80)`
2. `Corner Radius` → `.clipShape(RoundedRectangle(cornerRadius: 12))` or `UnevenRoundedRectangle` for per-corner
3. `Border` → `.overlay(RoundedRectangle().stroke())`
4. `Design Tokens` → Copy Usage column directly
5. `Asset Children` → `Image()` calls with correct renderingMode
6. Include `Color+Hex` extension when using hex colors

**CRITICAL - Modifier Ordering:**

SwiftUI modifiers apply in order. The correct sequence for frame properties:

```swift
.padding()           // 1. Internal padding (affects content)
.frame()             // 2. Size constraints
.background()        // 3. Background color/gradient
.clipShape()         // 4. Clip to shape (BEFORE overlay)
.overlay()           // 5. Border stroke (AFTER clipShape)
.shadow()            // 6. Shadow (outermost)
```

**Why this order matters:**

| Wrong Order | Problem |
|-------------|---------|
| `.overlay()` before `.clipShape()` | Border gets clipped, corners cut off |
| `.background()` after `.clipShape()` | Background bleeds outside rounded corners |
| `.shadow()` before `.clipShape()` | Shadow shape doesn't match clipped shape |
| `.frame()` after `.clipShape()` | Frame size may not match clipped content |

**Example - Correct modifier chain:**
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

## Layer Order Parsing

Read Layer Order from Implementation Spec to determine ZStack ordering.

**SwiftUI ZStack:** Last child renders on top (opposite of HTML/React)

**Example spec:**
```yaml
layerOrder:
  - layer: PageControl (zIndex: 900)
  - layer: HeroImage (zIndex: 500)
  - layer: ContinueButton (zIndex: 100)
```

**Generated SwiftUI order:**
```swift
// ZStack renders bottom-to-top (last = on top)
ZStack(alignment: .top) {
    ContinueButton()  // zIndex 100 - first = bottom
    HeroImage()       // zIndex 500 - middle
    PageControl()     // zIndex 900 - last = on top
}
```

**CRITICAL:** Reverse zIndex sort for SwiftUI (lowest zIndex first in code)

**Fallback:** If `layerOrder` is missing from spec, render components in the order they appear in spec components list (no reordering needed).

### Frame Positioning

When spec includes `absoluteY`, use `.offset()` for y-axis positioning:

```swift
// PageControl at absoluteY: 60
PageControl()
    .offset(y: 60)
    .zIndex(900)

// ContinueButton at absoluteY: 800
ContinueButton()
    .offset(y: 800)
    .zIndex(100)
```

**Position context mapping:**
- `position: top` → `.frame(maxHeight: .infinity, alignment: .top)`
- `position: center` → `.frame(maxHeight: .infinity, alignment: .center)`
- `position: bottom` → `.frame(maxHeight: .infinity, alignment: .bottom)`

**Prefer alignment over absolute positioning** when possible (more responsive).

## Code Generation

### For Each Component

Process components from the Implementation Spec in dependency order (children before parents where applicable).

#### 0. Check for Asset Children (BEFORE MCP)

Before calling figma_generate_code, check if component has Asset Children.

```
Read component's "Asset Children" property from spec
If Asset Children exist:
  → Component contains assets that need Image() calls
  → Note asset positions for manual insertion
```

#### 1. Generate Base Code via MCP

For each component with a Node ID:

```
figma_generate_code:
  - file_key: {file_key}
  - node_id: {node_id}
  - framework: swiftui
  - component_name: {ComponentName}
```

**Note:** MCP may generate placeholder or broken code for asset nodes. This will be fixed in step 1.5.

See [code-generator-base.md](./code-generator-base.md) for rate limit handling and MCP integration details.

#### 1.5. Replace Asset Nodes with Image() Calls

**CRITICAL:** After MCP generation, replace asset node code with proper Image() calls.

For each entry in component's Asset Children:
1. Parse: `IMAGE:asset-name:NodeID:width:height`
2. Look up renderingMode from assetNodeMap
3. Generate Image() code:
   ```swift
   Image("{asset-name}")
       .resizable()
       .renderingMode({renderingMode})
       .frame(width: {width}, height: {height})
   ```
4. Insert into component at correct position in layout

**Position Determination:**
- Read component's Layout property (HStack, VStack, ZStack)
- Asset Children order matches visual order (left-to-right, top-to-bottom)
- First Asset Child = first in HStack/top in VStack

#### Image-with-Text Handling

> **See also:** [Image-with-Text Detection](#image-with-text-detection) for the heuristic-based detection from Flagged Frames. This section handles the explicit `[contains-text]` annotation path during Asset Children replacement.

When an Asset Children entry includes `[contains-text: "..."]` annotation:

1. **Do NOT** generate a separate `Text()` view for the contained text
2. **Do** use the text content as `accessibilityLabel` for the `Image()` view
3. **Do** add a code comment explaining the text is embedded in the image

**Example:**

Spec input:
```
**Asset Children** | `IMAGE:growth-chart:6:32:354:132 [contains-text: "PROJECTED GROWTH"]`
```

Generated code:
```swift
// "PROJECTED GROWTH" text is embedded in the growth-chart image asset
Image("growth-chart")
    .resizable()
    .aspectRatio(contentMode: .fit)
    .frame(maxWidth: .infinity)
    .accessibilityLabel("PROJECTED GROWTH chart showing upward trend")
```

**NOT generated** (suppressed):
```swift
Text("PROJECTED GROWTH")  // ← This would duplicate text in image
```

#### Unresolved Icon Handling

When the spec contains an "Unresolved Assets" section with icon entries:

1. Generate a placeholder with `// TODO` marker:
```swift
// TODO: Unresolved icon asset (Node ID: 3:400)
// Visual reference: See figma-reports/{file_key}-spec.md Unresolved Assets section
Image(systemName: "questionmark.square.dashed")
    .resizable()
    .aspectRatio(contentMode: .fit)
    .frame(width: 32, height: 32)
```

2. Do NOT use a different icon as fallback — wrong icon is worse than placeholder
3. The compliance-checker MUST flag this as a FAIL condition

#### 2. Enhance with SwiftUI Specifics

Take the MCP-generated code and enhance it with SwiftUI patterns:

##### Apply Design Tokens

Replace hardcoded values with semantic color names from Asset Catalog or Color extensions:

```swift
// Before (MCP output)
Color(red: 0.231, green: 0.510, blue: 0.965)

// After (with tokens)
Color("PrimaryColor")
// Or with Color extension:
Color.primary
```

##### Apply Opacity from Spec

See: @skills/figma-to-code/references/opacity-extraction.md for calculation details.

**Copy Usage column from Design Tokens table** - it contains the complete SwiftUI modifier chain.

```markdown
| Property | Color | Opacity | Usage |
|----------|-------|---------|-------|
| Border | #ffffff | 0.4 | `.stroke(Color.white.opacity(0.4))` |
```

**Key rules:**
1. **Primary source: Usage column** - Copy exactly as shown
2. **Never ignore opacity modifiers** - If Usage shows `.opacity(X)`, include it
3. **opacity: 1.0** - No `.opacity()` modifier needed (SwiftUI default)
4. **opacity: 0.0** - Element is invisible, verify intentional

##### Apply Gradients from Spec

**Read gradient from Implementation Spec "Text with Gradient" section:**

```markdown
### Text with Gradient
- **Gradient Type:** ANGULAR
- **Stops:** 7 color stops with positions
  - Position 0.1673: #bc82f3 (purple)
  - Position 0.2365: #f4b9ea (pink)
  ...
```

**Map to SwiftUI gradient:**

```swift
Text("Type a scene to generate your video")
    .font(.system(size: 14, weight: .regular))
    .foregroundStyle(
        AngularGradient(
            stops: [
                Gradient.Stop(color: Color(hex: "#bc82f3"), location: 0.1673),
                Gradient.Stop(color: Color(hex: "#f4b9ea"), location: 0.2365),
                Gradient.Stop(color: Color(hex: "#8d98ff"), location: 0.3518),
                Gradient.Stop(color: Color(hex: "#aa6eee"), location: 0.5815),
                Gradient.Stop(color: Color(hex: "#ff6777"), location: 0.6970),
                Gradient.Stop(color: Color(hex: "#ffba71"), location: 0.8095),
                Gradient.Stop(color: Color(hex: "#c686ff"), location: 0.9241)
            ],
            center: .center
        )
    )
```

**Gradient type mapping:**

| Figma Type | SwiftUI Type | Example |
|------------|---------------|---------|
| LINEAR | `LinearGradient` | `LinearGradient(stops: [...], startPoint: .top, endPoint: .bottom)` |
| RADIAL | `RadialGradient` | `RadialGradient(stops: [...], center: .center, startRadius: 0, endRadius: 100)` |
| ANGULAR | `AngularGradient` | `AngularGradient(stops: [...], center: .center)` |
| DIAMOND | `AngularGradient` | `AngularGradient(stops: [...], center: .center)` (treat as angular) |

**Important - Preserve exact 4-decimal precision in gradient stop locations:**

```swift
// ❌ WRONG - Dropping trailing zero
Gradient.Stop(color: Color(hex: "#ff6777"), location: 0.697)

// ✅ CORRECT - Exact 4-decimal precision from spec
Gradient.Stop(color: Color(hex: "#ff6777"), location: 0.6970)
```

**Rules:**
1. **Preserve ALL gradient stops** - Every stop from Implementation Spec must appear in output
2. **4-decimal precision** - Use exactly 4 decimal places (0.1673, not 0.17 or 0.167)
3. **Keep trailing zeros** - 0.6970 NOT 0.697 (maintains precision from Figma)
4. **Never round** - Use exact location values from spec

**For LINEAR gradients, convert angle to startPoint/endPoint:**

| Angle | startPoint | endPoint | Direction |
|-------|------------|----------|-----------|
| 0° | `.leading` | `.trailing` | Left to right |
| 90° | `.top` | `.bottom` | Top to bottom |
| 180° | `.trailing` | `.leading` | Right to left |
| 270° | `.bottom` | `.top` | Bottom to top |
| 45° | `.topLeading` | `.bottomTrailing` | Diagonal |
| 135° | `.topTrailing` | `.bottomLeading` | Diagonal |

**Example LINEAR gradient:**

```swift
Text("Gradient text")
    .foregroundStyle(
        LinearGradient(
            stops: [
                Gradient.Stop(color: Color(hex: "#FF0000"), location: 0.0),
                Gradient.Stop(color: Color(hex: "#0000FF"), location: 1.0)
            ],
            startPoint: .leading,
            endPoint: .trailing
        )
    )
```

**Example RADIAL gradient:**

```swift
Text("Radial gradient")
    .foregroundStyle(
        RadialGradient(
            stops: [
                Gradient.Stop(color: Color(hex: "#FFFF00"), location: 0.0),
                Gradient.Stop(color: Color(hex: "#FF00FF"), location: 1.0)
            ],
            center: .center,
            startRadius: 0,
            endRadius: 100
        )
    )
```

**Critical rules:**

1. **Read ALL stops from Implementation Spec** - don't truncate gradient (some have 7+ stops)
2. **Use `.foregroundStyle()` NOT `.foregroundColor()`** - `.foregroundColor()` doesn't support gradients
3. **Preserve exact stop positions** - don't round to 0.0/0.5/1.0, use exact values from spec (e.g., 0.1673)
4. **Use `Color(hex:)` for stop colors** - requires Color+Hex extension from Task 5
5. **Minimum iOS 15** - `.foregroundStyle()` requires iOS 15+, add `@available(iOS 15.0, *)` if needed

**Common mistakes:**

❌ `.foregroundColor(LinearGradient(...))` → Won't compile
✅ `.foregroundStyle(LinearGradient(...))`

❌ Hardcoding only 2-3 stops → Loses gradient fidelity
✅ Reading all stops from spec

❌ Rounding positions to 0.0, 0.5, 1.0 → Shifts gradient balance
✅ Using exact positions like 0.1673, 0.2365

❌ Using `.opacity()` with gradients → Applies to entire gradient uniformly
✅ Using hex colors with alpha channel for per-stop opacity (e.g., `#80FF0000`)

##### Apply Text Decoration from Spec

Read text decoration from the **"Text Decoration"** section of Implementation Spec and apply `.underline()` or `.strikethrough()` modifiers with color from spec.

**Input format (Implementation Spec):**

```markdown
### Text Decoration

**Component:** HookText
- **Decoration:** Underline | Strikethrough
- **Color:** #ffd100 (opacity: 1.0)
- **Thickness:** 1.0

**SwiftUI Mapping:** `.underline(color: Color(hex: "#ffd100"))`
```

**Example outputs:**

```swift
// Underline with custom color (iOS 16+)
@available(iOS 16.0, *)
struct HookText: View {
  var body: some View {
    Text("Hook")
      .font(.system(size: 14, weight: .regular))
      .underline(color: Color(hex: "#ffd100"))
  }
}

// Strikethrough with color and opacity (iOS 16+)
@available(iOS 16.0, *)
struct StrikeText: View {
  var body: some View {
    Text("Strike")
      .font(.system(size: 14, weight: .regular))
      .strikethrough(color: Color(hex: "#ff0000").opacity(0.8))
  }
}

// Basic underline without color (iOS 15 compatible)
struct BasicUnderline: View {
  var body: some View {
    Text("Basic")
      .font(.system(size: 14, weight: .regular))
      .underline()
  }
}
```

**iOS version handling with fallback:**

```swift
// Option 1: iOS 16+ only (recommended for new apps)
@available(iOS 16.0, *)
struct HookText: View {
  var body: some View {
    Text("Hook")
      .underline(color: Color(hex: "#ffd100"))
  }
}

// Option 2: With iOS 15 fallback (for backward compatibility)
struct HookText: View {
  var body: some View {
    if #available(iOS 16.0, *) {
      Text("Hook")
        .font(.system(size: 14, weight: .regular))
        .underline(color: Color(hex: "#ffd100"))
    } else {
      Text("Hook")
        .font(.system(size: 14, weight: .regular))
        .underline()  // No color on iOS 15
    }
  }
}
```

**Critical rules:**

1. **Apply after .font() modifier** - Decoration goes after typography, never before
2. **Use exact color from spec** - Copy hex value from "Color" field, don't approximate or use system colors
3. **Include opacity if < 1.0** - Add `.opacity(0.8)` to Color when decoration color has opacity < 1.0
4. **iOS 16+ API** - Add `@available(iOS 16.0, *)` when using color parameter (required)
5. **Fallback for iOS 15** - Use `.underline()` or `.strikethrough()` without color for older iOS versions

**Common mistakes:**

❌ `.underline()` before `.font()` → Wrong modifier order
✅ `.font().underline()` → Typography first, then decoration

❌ `.underline(color: .yellow)` → Using system color instead of spec color
✅ `.underline(color: Color(hex: "#ffd100"))` → Exact color from spec

❌ `.underline(color: Color(hex: "#ff0000"))` when opacity is 0.8 → Missing opacity
✅ `.underline(color: Color(hex: "#ff0000").opacity(0.8))` → Includes opacity

❌ Using color parameter without `@available(iOS 16.0, *)` → Compilation error on iOS 15
✅ Adding `@available(iOS 16.0, *)` to struct → Proper iOS version guard

❌ `.underline(color: Color(hex: "#ffd100").opacity(1.0))` → Unnecessary .opacity()
✅ `.underline(color: Color(hex: "#ffd100"))` → No modifier when opacity = 1.0

##### Apply Inline Text Variations from Spec

**Read from Implementation Spec:**

Check for "### Inline Text Variations" section in Components:

```markdown
### Inline Text Variations

**Component:** TitleText
**Full Text:** "Let's fix your Hook"
**Variations:**
| Range | Text | Color | Weight | Decoration |
|-------|------|-------|--------|------------|
| 0-15 | "Let's fix your " | #FFFFFF | 600 | none |
| 15-19 | "Hook" | #F2F20D | 600 | underline |
```

**SwiftUI Code Generation:**

When Inline Text Variations exist, generate Text concatenation:

```swift
// Single-color text (no variations)
Text("Simple text")
  .foregroundColor(.white)

// Multi-color text (with variations from spec)
(
  Text("Let's fix your ")
    .font(.system(size: 24, weight: .semibold))
    .foregroundColor(.white)
  +
  Text("Hook")
    .font(.system(size: 24, weight: .semibold))
    .foregroundColor(Color(hex: "#F2F20D"))
    .underline()
)
```

**Generation Rules:**

1. **Wrap in parentheses** when using + operator for Text concatenation
2. **Each Text segment** gets its own modifiers based on variation table
3. **Font applies to each segment** (cannot be applied to concatenated result)
4. **Decoration (underline/strikethrough)** applies only to relevant segment
5. **Color from hex** when variation color differs from primary

**Template:**

```swift
// For each variation row in table:
Text("{variation.text}")
  .font(.system(size: {fontSize}, weight: .{weight}))
  .foregroundColor({colorModifier})
  {decorationModifier}

// colorModifier:
// - #FFFFFF → .white
// - #000000 → .black
// - other → Color(hex: "{color}")

// decorationModifier:
// - underline → .underline()
// - strikethrough → .strikethrough()
// - none → (omit)
```

**Example Output:**

Input spec:
```markdown
| Range | Text | Color | Weight | Decoration |
|-------|------|-------|--------|------------|
| 0-15 | "Let's fix your " | #FFFFFF | 600 | none |
| 15-19 | "Hook" | #F2F20D | 600 | underline |
```

Generated SwiftUI:
```swift
private var titleText: some View {
  (
    Text("Let's fix your ")
      .font(.system(size: 24, weight: .semibold))
      .foregroundColor(.white)
    +
    Text("Hook")
      .font(.system(size: 24, weight: .semibold))
      .foregroundColor(Color(hex: "#F2F20D"))
      .underline()
  )
}
```

**Common mistakes:**

❌ Applying font to concatenated result → Compilation error
✅ Apply font to each Text segment individually

❌ Missing parentheses around concatenation → Modifier scope issues
✅ Wrap entire concatenation in parentheses

❌ Using + without parentheses as body → Type inference issues
✅ Wrap in `Group { }` or parentheses when returning from body

##### Apply Text Sizing from Spec

**Read from Implementation Spec:**

Check for text sizing properties in each component's property table:

```markdown
| Property | Value |
|----------|-------|
| **Auto-Resize** | `HEIGHT` |
| **Frame Dimensions** | `311 × 38` |
| **Line Count Hint** | `2` |
```

**SwiftUI Code Generation by Auto-Resize Mode:**

**1. `HEIGHT` (width fixed, height adjusts):**
```swift
// Default behavior — no lineLimit needed
Text("Description text that may wrap to multiple lines")
    .font(.system(size: 14))
    .foregroundColor(.white.opacity(0.7))
// Do NOT add .lineLimit() — let text wrap naturally
```

**2. `TRUNCATE` (fixed frame, text truncated):**
```swift
Text("Text that should truncate if too long")
    .font(.system(size: 14))
    .foregroundColor(.white.opacity(0.7))
    .lineLimit(2) // lineCountHint from spec
    .truncationMode(.tail)
```

**3. `NONE` (fixed frame, text may clip):**
```swift
Text("Fixed frame text")
    .font(.system(size: 14))
    .foregroundColor(.white.opacity(0.7))
    .frame(width: 311, height: 38) // exact frame dimensions from spec
    .clipped()
```

**4. `WIDTH_AND_HEIGHT` (both dimensions adjust):**
```swift
// No constraints — text sizes to content
Text("Auto-sizing text")
    .font(.system(size: 14))
    .foregroundColor(.white.opacity(0.7))
    .fixedSize() // prevent truncation in both dimensions
```

**Rules:**
1. If `Auto-Resize` is `HEIGHT` → do NOT add `.lineLimit()` (let text wrap freely)
2. If `Auto-Resize` is `TRUNCATE` → add `.lineLimit(N)` using `Line Count Hint` value (default to `1` if not provided)
3. If `Auto-Resize` is `NONE` → add `.frame(width:height:)` and `.clipped()`
4. If `Auto-Resize` is `WIDTH_AND_HEIGHT` → add `.fixedSize()` (both axes)
5. If no `Auto-Resize` property in spec → default to `HEIGHT` behavior (no lineLimit)
6. When `Line Count Hint` > 1 and no explicit `Auto-Resize` → ensure no `.lineLimit(1)` is applied

**Common mistakes:**

❌ Adding `.lineLimit(1)` when Auto-Resize is `HEIGHT` → Text truncated unexpectedly
✅ No `.lineLimit()` when Auto-Resize is `HEIGHT` → Text wraps naturally

❌ Missing `.truncationMode(.tail)` with `.lineLimit()` → Default may vary
✅ Always pair `.lineLimit(N)` with `.truncationMode(.tail)` for TRUNCATE mode

❌ Using `.frame(maxHeight:)` for `NONE` mode → Text may overflow
✅ Using `.frame(width:height:).clipped()` for `NONE` mode → Clean clipping

##### Use Proper View Structure

Ensure proper SwiftUI View protocol implementation:

```swift
// Before (MCP output)
struct CardView {
  var body: some View {
    // ...
  }
}

// After (proper structure)
struct CardView: View {
  var body: some View {
    // ...
  }
}
```

##### Add Property Wrappers

Add appropriate state management based on component needs:

```swift
struct ButtonView: View {
  /// Button variant style
  let variant: ButtonVariant
  /// Button size
  let size: ButtonSize
  /// Disabled state
  @Binding var isDisabled: Bool
  /// Tap action handler
  let action: () -> Void

  var body: some View {
    Button(action: action) {
      // Button content
    }
    .disabled(isDisabled)
  }
}
```

##### Add Accessibility

Include accessibility modifiers for VoiceOver:

```swift
Button("Submit") {
  submitAction()
}
.accessibilityLabel("Submit form")
.accessibilityHint("Double tap to submit the form")
.accessibilityAddTraits(.isButton)
```

##### Icon Rendering Mode Selection

**CRITICAL:** Check Downloaded Assets table for fill information to determine correct rendering mode.

**Read from Implementation Spec:**

```markdown
## Downloaded Assets

| Asset | Local Path | Fill Type | Template Compatible |
|-------|------------|-----------|---------------------|
| icon-clock.svg | `.../icon-clock.svg` | #F2F20D | No - use .original |
| icon-search.svg | `.../icon-search.svg` | none | Yes - use .template |
```

**Apply correct rendering mode based on Template Compatible column:**

```swift
// Downloaded Assets shows: icon-clock.svg has fill="#F2F20D" → Template Compatible: No
Image("icon-clock")
    .resizable()
    .renderingMode(.original)  // Preserves hardcoded fill color from SVG
    .frame(width: 32, height: 32)

// Downloaded Assets shows: icon-search.svg has no fill → Template Compatible: Yes
Image("icon-search")
    .resizable()
    .renderingMode(.template)
    .foregroundColor(.viralYellow)  // Apply color via SwiftUI
    .frame(width: 32, height: 32)
```

**Rules:**

1. **If Template Compatible = No (hardcoded fill):**
   - Use `.renderingMode(.original)`
   - Do NOT apply `.foregroundColor()` - it will be ignored
   - SVG's embedded fill color will be used

2. **If Template Compatible = Yes (no fill or currentColor):**
   - Use `.renderingMode(.template)`
   - Apply `.foregroundColor()` from design tokens
   - Color comes from SwiftUI, not SVG

3. **If Downloaded Assets table missing Template Compatible column:**
   - Default to `.renderingMode(.template)` with color from spec
   - If icon appears wrong color, switch to `.renderingMode(.original)`

**Common mistakes:**

```swift
// ❌ WRONG - Using template mode with hardcoded fill SVG
Image("icon-clock")  // SVG has fill="#F2F20D"
    .renderingMode(.template)
    .foregroundColor(.viralYellow)  // Will show solid yellow, loses detail

// ✅ CORRECT - Using original mode for hardcoded fill SVG
Image("icon-clock")  // SVG has fill="#F2F20D"
    .renderingMode(.original)  // SVG's #F2F20D will render correctly

// ❌ WRONG - No rendering mode specified for icon
Image("icon-clock")  // May render incorrectly in different contexts
    .frame(width: 32, height: 32)

// ✅ CORRECT - Always specify rendering mode explicitly
Image("icon-clock")
    .renderingMode(.original)  // or .template based on spec
    .frame(width: 32, height: 32)
```

#### 3. Write Component Files

##### Detect Existing Directory Structure

Before writing files, detect existing SwiftUI project conventions:

```bash
# SwiftUI: Check for existing view directories
Glob("**/*View.swift") || Glob("Views/**/*.swift") || Glob("Sources/**/*.swift")
```

Use the detected structure to determine where to place new components. If no existing structure is found, use the default structure below.

##### SwiftUI Directory Structure

```
ProjectName/
├── Views/
│   ├── Components/          # Reusable UI components
│   │   ├── ButtonView.swift
│   │   ├── CardView.swift
│   │   └── BadgeView.swift
│   └── Screens/             # Screen-level views
│       ├── HomeView.swift
│       └── DetailView.swift
├── Models/
│   └── ComponentModel.swift
├── ViewModels/
│   └── ComponentViewModel.swift
├── Extensions/
│   └── Color+Theme.swift
└── Resources/
    └── Assets.xcassets
```

For SPM packages:

```
Sources/
└── {PackageName}/
    ├── Views/
    ├── Models/
    └── Extensions/
```

## SwiftUI Component Structure

### Component Example

```swift
import SwiftUI

/// A card component displaying title, description, and optional image
struct CardView: View {
  // MARK: - Properties

  /// Card title
  let title: String

  /// Card description
  let description: String?

  /// Optional image name from asset catalog
  let imageName: String?

  /// Card variant style
  let variant: CardVariant

  // MARK: - Body

  var body: some View {
    VStack(alignment: .leading, spacing: 16) {
      if let imageName = imageName {
        Image(imageName)
          .resizable()
          .aspectRatio(contentMode: .fill)
          .frame(height: 200)
          .clipped()
          .cornerRadius(12)
      }

      VStack(alignment: .leading, spacing: 8) {
        Text(title)
          .font(.title2)
          .fontWeight(.semibold)
          .foregroundColor(Color("TextPrimary"))

        if let description = description {
          Text(description)
            .font(.body)
            .foregroundColor(Color("TextSecondary"))
            .lineLimit(3)
        }
      }
    }
    .padding(24)
    .background(backgroundColor)
    .cornerRadius(16)
    .shadow(color: Color.black.opacity(0.1), radius: 8, x: 0, y: 4)
    .accessibilityElement(children: .combine)
    .accessibilityLabel(accessibilityDescription)
  }

  // MARK: - Computed Properties

  private var backgroundColor: Color {
    switch variant {
    case .elevated:
      return Color("CardBackground")
    case .outlined:
      return Color.clear
    }
  }

  private var accessibilityDescription: String {
    var desc = "Card: \(title)"
    if let description = description {
      desc += ". \(description)"
    }
    return desc
  }
}

// MARK: - Supporting Types

enum CardVariant {
  case elevated
  case outlined
}

// MARK: - Preview (iOS 17+)

#Preview("Light Mode") {
  CardView(
    title: "Sample Card",
    description: "This is a sample description for the card component.",
    imageName: "sample-image",
    variant: .elevated
  )
  .padding()
}

#Preview("Dark Mode") {
  CardView(
    title: "Sample Card",
    description: "This is a sample description for the card component.",
    imageName: "sample-image",
    variant: .elevated
  )
  .preferredColorScheme(.dark)
  .padding()
}

// MARK: - Preview (iOS 13-16 fallback)

struct CardView_Previews: PreviewProvider {
  static var previews: some View {
    Group {
      CardView(
        title: "Sample Card",
        description: "This is a sample description for the card component.",
        imageName: "sample-image",
        variant: .elevated
      )
      .previewLayout(.sizeThatFits)
      .padding()
      .previewDisplayName("Light Mode")

      CardView(
        title: "Sample Card",
        description: "This is a sample description for the card component.",
        imageName: "sample-image",
        variant: .elevated
      )
      .preferredColorScheme(.dark)
      .previewLayout(.sizeThatFits)
      .padding()
      .previewDisplayName("Dark Mode")
    }
  }
}
```

## Required Extensions

When generating SwiftUI code, include these helper extensions if needed.

### Color+Hex Extension

If any generated code uses `Color(hex:)`, include this extension:

```swift
extension Color {
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
      blue: Double(b) / 255,
      opacity: Double(a) / 255
    )
  }
}
```

### RoundedCorner Shape (iOS 15 Compatible)

If spec has per-corner radius and project targets iOS 15, include this shape:

```swift
struct RoundedCorner: Shape {
  var radius: CGFloat = .infinity
  var corners: UIRectCorner = .allCorners

  func path(in rect: CGRect) -> Path {
    let path = UIBezierPath(
      roundedRect: rect,
      byRoundingCorners: corners,
      cornerRadii: CGSize(width: radius, height: radius)
    )
    return Path(path.cgPath)
  }
}

// Usage:
.clipShape(RoundedCorner(radius: 16, corners: [.topLeft, .topRight]))
```

### When to Include Extensions

| Extension | Include When |
|-----------|--------------|
| Color+Hex | Any `Color(hex: "#...")` usage |
| RoundedCorner | Per-corner radius AND iOS 15 target |

**Note:** For iOS 16+, use native `UnevenRoundedRectangle` instead of RoundedCorner.

### Component Checklist

For each generated component, verify:

- [ ] **Hierarchy matches spec** - Component structure follows the spec hierarchy
- [ ] **View protocol conforms** - Proper `View` protocol implementation with `body` property
- [ ] **Tokens applied** - Uses Color/Font from Asset Catalog or extensions
- [ ] **Property wrappers** - Appropriate @State, @Binding, @StateObject usage
- [ ] **Accessibility** - VoiceOver labels, hints, traits
- [ ] **Dynamic Type support** - Uses system font sizes or .dynamicTypeSize modifier
- [ ] **Assets referenced** - Images/icons use Asset Catalog names or SF Symbols
- [ ] **Asset Children processed** - All IMAGE: entries converted to Image() calls
- [ ] **Rendering modes correct** - .original for colored SVGs, .template for tintable
- [ ] **Illustrations sized** - Large assets use aspectRatio, not fixed frame
- [ ] **Frame dimensions applied** - .frame() modifiers match spec Dimensions
- [ ] **Corner radius applied** - .clipShape() or .cornerRadius() match spec
- [ ] **Border applied** - .overlay() with .stroke() for spec Border property
- [ ] **Preview provider** - Includes PreviewProvider for Xcode previews

## SwiftUI-Specific Error Handling

### Compilation Errors

1. Identify the compilation error from Xcode/compiler output
2. Fix the code issue
3. Re-validate with Swift compiler:
   ```bash
   swift build 2>&1 || xcodebuild -scheme {SchemeName} -dry-run 2>&1
   ```
4. If errors persist:
   - Document in Generated Code table with status "WARN"
   - Add fix instructions in summary

### Missing Assets

1. Check if asset exists in Downloaded Assets section
2. If missing:
   - Use SF Symbol as fallback: `Image(systemName: "photo")`
   - Add TODO comment in code:
     ```swift
     // TODO: Replace with actual asset from Asset Catalog
     Image(systemName: "photo")
       .foregroundColor(.secondary)
     ```
   - Document in Generated Code table with status "WARN - Missing asset"
   - Add to summary: "Asset {name} not found - using SF Symbol fallback"

## Manual Generation Fallback

When MCP generation is unavailable, generate SwiftUI code from spec:

### Extract from Spec

1. **Component properties** from Components section
2. **Layout information** from Classes/Styles field
3. **Semantic element** from Element field
4. **Children** from Children field
5. **Design tokens** from Design Tokens (Ready to Use) section

### Generate SwiftUI Structure

```swift
// From spec:
// Element: Card Container
// Layout: vertical stack with 16pt spacing
// Background: white with shadow
// Corner radius: 12pt

struct {ComponentName}View: View {
  // Properties from spec
  let title: String
  let description: String?

  var body: some View {
    VStack(alignment: .leading, spacing: 16) {
      // Children from spec hierarchy
      Text(title)
        .font(.title2)
        .fontWeight(.semibold)

      if let description = description {
        Text(description)
          .font(.body)
          .foregroundColor(.secondary)
      }
    }
    .padding(24)
    .background(Color.white)
    .cornerRadius(12)
    .shadow(radius: 8)
  }
}
```

## SwiftUI Guidelines

### Naming Conventions

- **View names**: PascalCase with "View" suffix (e.g., `CardView`, `ButtonView`)
- **File names**: Match view name (e.g., `CardView.swift`)
- **Properties**: camelCase (e.g., `titleText`, `isEnabled`)
- **Enums**: PascalCase (e.g., `ButtonVariant`, `CardStyle`)

### Code Quality Standards

- Use MARK comments to organize code sections
- Include DocC documentation comments for public APIs
- Extract complex views into computed properties or subviews
- Keep View body under 10 lines when possible
- Use ViewBuilder for conditional content
- Prefer composition over large conditional blocks

### SwiftUI Best Practices

- Use semantic color names from Asset Catalog
- Prefer SF Symbols over custom icons when applicable
- Use `.font(.system(.body, design: .rounded))` for consistent typography
- Group related modifiers together
- Use `.padding()` and `.spacing()` for consistent layout
- Leverage SwiftUI's automatic layout system

### Accessibility Requirements

- All images must have `.accessibilityLabel()`
- Interactive elements should have `.accessibilityHint()` when needed
- Use `.accessibilityAddTraits()` for semantic meaning
- Support Dynamic Type with system fonts
- Ensure color contrast meets WCAG AA (4.5:1)
- Test with VoiceOver enabled
- Use `.accessibilityElement(children: .combine)` for grouped content

### State Management

Choose appropriate property wrappers:

| Wrapper | Use Case |
|---------|----------|
| `@State` | View-local state |
| `@Binding` | Two-way binding to parent state |
| `@StateObject` | View owns the ObservableObject |
| `@ObservedObject` | Parent owns the ObservableObject |
| `@EnvironmentObject` | Shared state across view hierarchy |
| `@Environment` | System-provided values |

## Output

Update the Implementation Spec at: `docs/figma-reports/{file_key}-spec.md`

### Sections Added to Spec

```markdown
## Generated Code

| Component | File | Status |
|-----------|------|--------|
| CardView | `Views/Components/CardView.swift` | OK |
| ButtonView | `Views/Components/ButtonView.swift` | OK |
| HeroSection | `Views/Screens/HeroView.swift` | OK |
| NavigationBar | `Views/Components/NavigationBarView.swift` | WARN - Manual adjustments needed |

## Code Generation Summary

- **Framework:** SwiftUI (iOS/macOS)
- **Components generated:** {count}
- **Files created:** {count}
- **Warnings:** {count}
- **Generation timestamp:** {YYYYMMDD-HHmmss}

## Files Created

### Views
- `Views/Components/CardView.swift`
- `Views/Components/ButtonView.swift`
- `Views/Screens/HeroView.swift`

### Extensions (if created)
- `Extensions/Color+Theme.swift`

## Next Agent Input

Ready for: Compliance Checker Agent
Input file: `docs/figma-reports/{file_key}-spec.md`
Components generated: {count}
Framework: SwiftUI (iOS/macOS)
```
