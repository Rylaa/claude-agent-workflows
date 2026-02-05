# Asset Classification Guide

> **Used by:** asset-manager

## Asset Type Classification

| Type | Criteria | Download Format |
|------|----------|-----------------|
| **SIMPLE_ICON** | <10 child vectors AND ≤50px max dimension | SVG, scale: 1 |
| **COMPLEX_VECTOR** | ≥10 vector children OR >50px max dimension | PNG, scale: 2 |
| **CHART_ILLUSTRATION** | Has exportSettings | PNG, scale: 2 |
| **RASTER_IMAGE** | Image fill or photo | PNG (original) |
| **IMAGE_FILL** | Node has imageRef property | Use figma_get_images |

## Classification Priority

When node matches multiple types:
1. CHART_ILLUSTRATION (highest - has exportSettings)
2. IMAGE_FILL (has imageRef property)
3. RASTER_IMAGE (bitmap/photo content)
4. COMPLEX_VECTOR (≥3 vector paths, >50px)
5. SIMPLE_ICON (lowest priority)

## Icon Position Classification

For card/list components:

| Position in HStack | Type | Usage |
|--------------------|------|-------|
| Leading (first child) | Thematic Icon | Represents card's purpose |
| Trailing (last child) | Status Indicator | Shows state (checkmark, arrow) |

**WARNING:** Never assign trailing checkmark as card's thematic icon.

## Card Icon Validation

Size limits:
- Minimum: 16x16px
- Maximum: 50x50px
- If icon > 50px → Likely an illustration, not card icon

Typical card icons have:
- Single fill color (usually white or accent)
- Simple shape

**REJECT as card icons if:**
- Multiple gradient fills
- Photo/image fills
- Hardcoded dark color on dark background

## Asset Children Format

```
IMAGE:{asset-name}:{NodeID}:{width}:{height}
```

Example: `IMAGE:icon-clock:3:230:32:32`

## Template Compatibility (SwiftUI)

| SVG Fill | Template Compatible | SwiftUI Rendering |
|----------|--------------------|--------------------|
| No fill attribute | Yes | `.renderingMode(.template)` |
| `fill="currentColor"` | Yes | `.renderingMode(.template)` |
| `fill="#XXXXXX"` (hardcoded) | No | `.renderingMode(.original)` |
| Multiple different fills | No | `.renderingMode(.original)` |

## Why PNG for COMPLEX_VECTOR?

- Complex SVGs have huge file sizes
- Rendering performance issues in browsers/apps
- Difficult to style individual elements
- Better as optimized raster at target resolution
