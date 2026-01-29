# SwiftUI Patterns Reference

> **Used by:** code-generator-swiftui

This reference covers SwiftUI-specific patterns including Glass Effect (iOS 26+), Layer Order parsing for ZStack, and Adaptive Layout patterns for iPad support.

---

## Glass Effect (iOS 26+ Liquid Glass)

When a component has `Glass Effect: true` in the spec, generate iOS 26 Liquid Glass code with backward-compatible fallback.

**Detection:** Look for `| **Glass Effect** | true` and `| **Glass Tint** | {color} at {opacity} |` in the component's property table.

**Button Pattern (most common):**

```swift
// For buttons with Glass Effect: true
if #available(iOS 26.0, *) {
    Button(action: { /* action */ }) {
        Text("Save with Pro")
            .font(.system(size: 16, weight: .semibold))
            .foregroundStyle(.white)
    }
    .buttonStyle(.glassProminent)
    .tint(Color(hex: "#ffae96"))  // Glass Tint color from spec
    .frame(width: 311, height: 48)
    .clipShape(Capsule())
} else {
    // Fallback for iOS < 26
    Button(action: { /* action */ }) {
        Text("Save with Pro")
            .font(.system(size: 16, weight: .semibold))
            .foregroundStyle(.white)
    }
    .frame(width: 311, height: 48)
    .background(
        .ultraThinMaterial,
        in: Capsule()
    )
    .overlay(
        Capsule()
            .fill(Color(hex: "#ffae96").opacity(0.10))
    )
}
```

**Container Pattern (non-button glass):**

```swift
// For non-button containers with Glass Effect: true
if #available(iOS 26.0, *) {
    content
        .glassEffect(.regular)
        .tint(Color(hex: "{glass_tint_color}"))
} else {
    content
        .background(.ultraThinMaterial)
        .overlay(
            RoundedRectangle(cornerRadius: {radius})
                .fill(Color(hex: "{glass_tint_color}").opacity({glass_tint_opacity}))
        )
        .clipShape(RoundedRectangle(cornerRadius: {radius}))
}
```

**Rules:**
1. Always use `#available(iOS 26.0, *)` check — never use `@available` at struct level for this
2. For buttons: use `.buttonStyle(.glassProminent)` with `.tint()` for the glass tint color
3. For containers: use `.glassEffect(.regular)` with `.tint()`
4. Fallback uses `.ultraThinMaterial` as background + overlay with the tint color at original opacity
5. If corner radius >= height/2, use `Capsule()` instead of `RoundedRectangle`
6. Glass Tint color comes from the spec's `Glass Tint` property (produced by design-analyst when `fill.opacity <= 0.3 AND cornerRadius > 0`)

---

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
- `position: top` -> `.frame(maxHeight: .infinity, alignment: .top)`
- `position: center` -> `.frame(maxHeight: .infinity, alignment: .center)`
- `position: bottom` -> `.frame(maxHeight: .infinity, alignment: .bottom)`

**Prefer alignment over absolute positioning** when possible (more responsive).

---

## Adaptive Layout Patterns (iPad/Tablet Support)

**Read from Implementation Spec:**

Check for Auto Layout and responsive properties in component specs:

```markdown
| Property | Value |
|----------|-------|
| **Auto Layout** | `VERTICAL, primaryAxis: MIN, counterAxis: CENTER` |
| **Constraints** | `horizontal: STRETCH, vertical: MIN` |
| **Responsive** | `content stretches to fill parent` |
```

**Rule 1 — Content Width Cap:**

All top-level content containers (the outermost VStack/ScrollView) MUST include a width cap for iPad readability:

```swift
VStack(spacing: 16) {
    // content
}
.frame(maxWidth: 600) // prevent over-stretching on iPad
.frame(maxWidth: .infinity) // center within parent
```

**When to apply:**
- The root container of ANY generated view
- Only at the top level (not nested containers)

**Rule 2 — Card Lists with 3+ Items:**

When a VStack contains 3 or more card-like children with identical structure (same component type repeated), use adaptive grid:

```swift
private let columns = [GridItem(.adaptive(minimum: 280, maximum: 400))]

var body: some View {
    LazyVGrid(columns: columns, spacing: 16) {
        ForEach(items) { item in
            CardView(item: item)
        }
    }
}
```

**When to apply:**
- Spec shows a repeating card pattern (ForEach over items)
- 3+ items with identical structure
- NOT for 1-2 items (keep VStack)

**Rule 3 — Safe Layout Defaults:**

ALWAYS follow these defaults in generated code:

```swift
// DO: Use flexible widths
.frame(maxWidth: .infinity)

// DON'T: Use screen-dependent widths
.frame(width: UIScreen.main.bounds.width)
.frame(width: 393) // hardcoded iPhone width

// DO: Use horizontal padding for edge spacing
.padding(.horizontal, 16)

// DON'T: Calculate padding from screen width
.padding(.horizontal, (UIScreen.main.bounds.width - 361) / 2)
```

**Rule 4 — Size Class (Optional, for complex layouts):**

Only use when the spec explicitly mentions different tablet layout OR the design has major structural differences for wider screens:

```swift
@Environment(\.horizontalSizeClass) var horizontalSizeClass

var body: some View {
    if horizontalSizeClass == .regular {
        // iPad: side-by-side layout
        HStack(spacing: 24) {
            leftContent
            rightContent
        }
    } else {
        // iPhone: stacked layout
        VStack(spacing: 16) {
            leftContent
            rightContent
        }
    }
}
```

**Common mistakes:**

- Hardcoding `UIScreen.main.bounds.width` -> Breaks on iPad and landscape
- Missing maxWidth cap on root container -> Content stretches too wide on iPad
- Using VStack for 5+ repeating cards -> Wasted horizontal space on iPad

**Correct patterns:**
- `.frame(maxWidth: .infinity)` -> Works on all screen sizes
- `.frame(maxWidth: 600).frame(maxWidth: .infinity)` -> Capped and centered
- `LazyVGrid(.adaptive(...))` -> Auto-adjusts columns by screen width

---

## Text Sizing from Spec

Read `Auto-Resize` and `Line Count Hint` properties from component specs to generate correct text behavior.

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
1. If `Auto-Resize` is `HEIGHT` -> do NOT add `.lineLimit()` (let text wrap freely)
2. If `Auto-Resize` is `TRUNCATE` -> add `.lineLimit(N)` using `Line Count Hint` value (default to `1` if not provided)
3. If `Auto-Resize` is `NONE` -> add `.frame(width:height:)` and `.clipped()`
4. If `Auto-Resize` is `WIDTH_AND_HEIGHT` -> add `.fixedSize()` (both axes)
5. If no `Auto-Resize` property in spec -> default to `HEIGHT` behavior (no lineLimit)
6. When `Line Count Hint` > 1 and no explicit `Auto-Resize` -> ensure no `.lineLimit(1)` is applied

**Common mistakes:**

- Adding `.lineLimit(1)` when Auto-Resize is `HEIGHT` -> Text truncated unexpectedly
- Missing `.truncationMode(.tail)` with `.lineLimit()` -> Default may vary
- Using `.frame(maxHeight:)` for `NONE` mode -> Text may overflow

---

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
