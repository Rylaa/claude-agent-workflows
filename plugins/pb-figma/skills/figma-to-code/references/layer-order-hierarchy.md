# Layer Order & Hierarchy Reference

## Core Principle

**Layer order = children array order, NOT Y coordinate.**

Figma's children array is already sorted by visual stacking order:
- First child (index 0) = bottom layer (rendered first)
- Last child (index n-1) = top layer (rendered last, visually on top)

## Why NOT Y Coordinate?

Y coordinate determines vertical position, not layer order:
- A button at Y=100 could be ABOVE an image at Y=50
- Only the children array order determines visual stacking
- Figma's layer panel order is authoritative

**Example:**
- Background: Y=0 (full screen) + Layer Panel BOTTOM → zIndex 100
- PageControl: Y=60 (top of screen) + Layer Panel TOP → zIndex 300

## Extracting Layer Order

```typescript
// From Figma node children array
const layerOrder = node.children.map((child, index) => ({
  name: child.name,
  zIndex: (index + 1) * 100,  // 100, 200, 300...
  position: getPositionContext(child)  // top/center/bottom
}));
```

## zIndex Assignment Rules

| Array Index | zIndex | Rendering |
|-------------|--------|-----------|
| 0 (first) | 100 | Bottom (back) |
| 1 | 200 | Middle |
| n-1 (last) | n * 100 | Top (front) |

**Note:** Multiplying by 100 leaves room for intermediate layers (150, 250, etc.)

## Spec Output Format

```yaml
layerOrder:
  - layer: Background (zIndex: 100)
  - layer: ContentCard (zIndex: 200)
  - layer: FloatingButton (zIndex: 300)
```

## Framework-Specific Rendering

| Framework | Order Rule | Code Pattern |
|-----------|------------|--------------|
| React/HTML | Last element = top (CSS stacking) | Render highest zIndex last |
| SwiftUI ZStack | Last element = top | Sort by zIndex ascending |
| CSS z-index | Higher value = top | Explicit z-index property |

### React Example

```jsx
// Render in zIndex ascending order (lowest first)
<div className="relative">
  <Background />      {/* zIndex 100 - renders first (bottom) */}
  <HeroImage />       {/* zIndex 500 - middle */}
  <PageControl />     {/* zIndex 900 - renders last (top) */}
</div>
```

### SwiftUI Example

```swift
ZStack {
    Background()      // zIndex 100 - first = bottom
    HeroImage()       // zIndex 500 - middle
    PageControl()     // zIndex 900 - last = on top
}
```

## Critical Rules

1. **Higher zIndex = renders on top**
2. **Never sort by Y coordinate** - Use Figma children array order
3. **Always query ALL nodes** - Layer order matters for overlays, headers, FABs
4. **Missing layerOrder?** - Use document order as fallback
5. **Same zIndex?** - Components can render in any relative order
