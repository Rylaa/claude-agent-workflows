# Implementation Spec: iPhone 13 & 14 - 202

**File:** bt65gbJ6sSdKRP4x3IY151
**Node:** 10203:16369
**Component:** TypeSceneText
**Framework:** SwiftUI
**Date:** 2026-01-26

## Overview

Mobile screen design (390x844px) for Muvi app featuring a text input prompt with gradient styling and semi-transparent border elements.

## Design Tokens (Ready to Use)

### Colors

| Property | Color | Opacity | Usage |
|----------|-------|---------|-------|
| Background (Solid) | #150200 | 1.0 | `.fill(Color(hex: "#150200"))` |
| Background (Radial Gradient) | #f02912 → #150200 | 0.2 | Radial gradient overlay |
| Border | #ffffff | 0.4 | `.stroke(Color.white.opacity(0.4))` |
| Gold Accent | #ffd100 | 1.0 | `.fill(Color(hex: "#ffd100"))` |
| Orange Accent | #ff9500 | 1.0 | `.fill(Color(hex: "#ff9500"))` |

### Text with Gradient

**Component:** TypeSceneText
**Text:** "Type a scene to generate your video"

- **Gradient Type:** ANGULAR
- **Stops:** 7 color stops with positions
  - Position 0.1673: #bc82f3 (purple)
  - Position 0.2365: #f4b9ea (pink)
  - Position 0.3518: #8d98ff (blue)
  - Position 0.5815: #aa6eee (lavender)
  - Position 0.697: #ff6777 (coral)
  - Position 0.8095: #ffba71 (peach)
  - Position 0.9241: #c686ff (violet)
- **Font Family:** Inter
- **Font Weight:** 400
- **Font Size:** 14px
- **Line Height:** 16.94px (121%)
- **Text Align:** CENTER
- **Minimum iOS:** iOS 15.0+ (AngularGradient requires iOS 15+)

**SwiftUI Implementation:**
```swift
Text("Type a scene to generate your video")
    .font(.system(size: 14, weight: .regular))
    .multilineTextAlignment(.center)
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
```

### Typography

| Element | Font | Weight | Size | Line Height | Color/Gradient |
|---------|------|--------|------|-------------|----------------|
| "Create" | SF Pro | 590 | 18px | 21.48px | #ffffff |
| "10" (coins) | SF Pro | 590 | 16px | 19.09px | #ffffff |
| "PRO" | SF Pro | 510 | 12px | 14.32px | #ffffff |
| "Image to Video" | Poppins | 400 | 14px | 21px | #ffffff |
| Gradient Text | Inter | 400 | 14px | 16.94px | Angular Gradient (7 stops) |
| "10000" | Inter | 500 | 10px | 12.10px | #ffffff |
| "Veo 3" | Poppins | 500 | 14px | 21px | #ffffff |
| "5s" | Poppins | 500 | 14px | 21px | #ffffff |
| "720P" | Poppins | 500 | 14px | 21px | #ffffff |

### Spacing (Auto Layout)

| Component | Mode | Padding | Gap | Align |
|-----------|------|---------|-----|-------|
| Frame 2121316293 | Horizontal | 0 | 8px | Left, Center |
| Frame 2121316339 | Horizontal | 0 | 16px | Right, Center |
| Frame 2121316339 | Horizontal | 0 | 8px | Left, Center |
| Frame 2121315086 | Horizontal | 4/4/4/8px | 4px | Right, Center |
| Frame 2121315084 | Horizontal | 0 | 4px | Left, Center |
| Settings Icon | Horizontal | 4/8/4/8px | 10px | Left, Center |
| Frame 2121316547 | Vertical | 0 | 16px | Top, Left |
| Frame 2121316297 | Vertical | 0 | 12px | Top, Left |
| Frame 2121316767 | Horizontal | 4/12/4/4px | 4px | Space Between, Center |
| Frame 2121316299 | Horizontal | 2/8/2/8px | 8px | Center, Center |

### Effects

| Name | Type | Value |
|------|------|-------|
| Blur S | Layer Blur | 4px |
| Blur M | Layer Blur | 8px |
| Blur L | Layer Blur | 12px |
| Blur XL | Layer Blur | 16px |

## Component Structure

```
iPhone 13 & 14 - 202 (390x844px)
├── Frame 2121316293 (Header - 358x32px)
│   ├── Navigation elements
│   └── Status bar items
└── Frame 2121316547 (Content - 358x1004px)
    └── Text input with gradient styling
```

## Key Implementation Notes

### Opacity Support
- Border stroke uses `.opacity(0.4)` modifier
- Apply to Color: `Color.white.opacity(0.4)`
- Stroke weight: 1.0px
- Stroke alignment: CENTER

### Gradient Support
- AngularGradient requires iOS 15.0+
- Uses 7 color stops for rainbow effect
- Center point: `.center`
- All stops have opacity: 1.0

### Border Rendering
```swift
RoundedRectangle(cornerRadius: someValue)
    .stroke(Color.white.opacity(0.4), lineWidth: 1.0)
```

### Radial Gradient Background
```swift
RadialGradient(
    gradient: Gradient(stops: [
        .init(color: Color(hex: "#f02912").opacity(0.2), location: 0.0),
        .init(color: Color(hex: "#150200").opacity(0.2), location: 1.0)
    ]),
    center: .center,
    startRadius: 0,
    endRadius: 200
)
```

## Color Extension Helper

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
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
```

## Validation Checklist

- [x] Opacity extraction (0.4 for border)
- [x] Gradient extraction (ANGULAR, 7 stops)
- [x] Color stops with positions
- [x] Font properties
- [x] Spacing values
- [x] Border properties

## Test Results

### Expected Border
- Color: white with 40% opacity
- Visual: Semi-transparent grayish border over dark background
- Implementation: `.stroke(Color.white.opacity(0.4), lineWidth: 1.0)`

### Expected Text Gradient
- Type: Angular (conic/rainbow effect)
- Stops: 7 colors (purple → pink → blue → lavender → coral → peach → violet)
- Visual: Rainbow gradient text effect
- Implementation: `AngularGradient` with 7 `Gradient.Stop` values

## Files Generated

- Implementation Spec: `docs/figma-reports/bt65gbJ6sSdKRP4x3IY151-spec.md`
- SwiftUI Component: `Views/Components/TypeSceneText.swift` (to be generated)
- Screenshot Reference: `/var/folders/.../figma_screenshots/bt65gbJ6sSdKRP4x3IY151_10203-16369_*.png`

## References

- Figma File: https://www.figma.com/design/bt65gbJ6sSdKRP4x3IY151/Muvi?node-id=10203-16369
- Framework: SwiftUI (iOS 15.0+)
- Opacity support: Verified in design tokens
- Gradient support: Verified with 7 color stops
