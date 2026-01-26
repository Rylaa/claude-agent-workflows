# Implementation Spec: OnboardingAnalysisView (ViralZ)

**Source:** ElHzcNWC8pSYTz2lhPP9h0-validation.md
**Generated:** 2026-01-26T19:00:00Z
**Status:** Code Generated

## Screenshot Reference
![Design Screenshot](/var/folders/xm/v1pm1qmj57s2k28dylbj0d9c0000gn/T/figma_screenshots/ElHzcNWC8pSYTz2lhPP9h0_6-46_20260126_184051_358840.png)

## Component Hierarchy

```
OnboardingAnalysisView (FRAME - main container)
├── BackgroundLayer (FRAME - #000000)
├── DecorativeVisualSection (GROUP)
│   ├── CircularGlow (ELLIPSE - green glow effect)
│   ├── AnimatedLines (GROUP - 11 VECTOR items)
│   │   ├── Vector 4-15 (decorative green strokes)
│   │   └── VectorBlur effect (4px layer blur)
│   ├── Ellipse 2 (ELLIPSE - outer ring)
│   └── Ellipse 3 (ELLIPSE - inner ring)
├── FloatingActionButton_Left (FRAME - chart icon)
│   └── ChartIcon (FRAME 6:187 - 49x62)
├── FloatingActionButton_Right (FRAME - sparkle icon)
│   └── SparkleIcon (FRAME 6:189 - 49x62)
├── ContentStack (FRAME - VERTICAL auto-layout)
│   ├── ProgressIndicator (FRAME - HORIZONTAL)
│   │   ├── Dot1 (ELLIPSE - inactive #858585)
│   │   ├── Dot2 (ELLIPSE - inactive)
│   │   ├── Dot3 (ELLIPSE - inactive)
│   │   ├── Dot4 (ELLIPSE - inactive)
│   │   ├── Dot5 (ELLIPSE - inactive)
│   │   └── Dot6 (ELLIPSE - active #f2f20d)
│   ├── HeaderSection (FRAME 2121316306 - VERTICAL gap:24px)
│   │   ├── TitleText (TEXT - "Ready for your **personalized** analysis?")
│   │   │   └── HighlightedSpan (inline - "personalized" #f2f20d)
│   │   └── DescriptionText (TEXT - white 16px)
│   ├── UsernameInputSection (FRAME 2121316832 - VERTICAL gap:12px)
│   │   ├── ProfileSelector (FRAME 2121316830 - HORIZONTAL space-between)
│   │   │   ├── ProfilePreview (FRAME)
│   │   │   │   ├── ProfileImage (IMAGE 213:269)
│   │   │   │   ├── BrandName (TEXT - "viralz")
│   │   │   │   └── Username (TEXT - "@viralz" #858585)
│   │   │   └── DropdownChevron (VECTOR 213:272)
│   │   └── TextInputField (FRAME 2121316831 - HORIZONTAL gap:10px)
│   │       ├── AtSymbol (TEXT - "@")
│   │       └── PlaceholderText (TEXT - "e.g. @viralz")
│   ├── TrustBadges (FRAME 2121316702 - HORIZONTAL gap:12px)
│   │   ├── SafeSecureBadge (FRAME)
│   │   │   ├── LockIcon (FRAME 6:133 - 16x16)
│   │   │   └── BadgeText (TEXT - "Safe & Secure")
│   │   └── OfficialAPIBadge (FRAME)
│   │       ├── TikTokIcon (FRAME 6:123 - 16x16)
│   │       └── BadgeText (TEXT - "Official Tiktok API")
│   └── CTAButton (FRAME 2121316743 - HORIZONTAL gap:16px padding:8px)
│       └── ButtonText (TEXT - "Analyze my account" #000000)
└── GradientBorders (decorative - LINEAR gradients)
```

## Layer Order

**Purpose:** Explicit z-index/layer hierarchy from Figma. Determines rendering order in code.

```yaml
layerOrder:
  - layer: BackgroundLayer
    zIndex: 100
    position: full
    absoluteY: 0
    children: []
    notes: "Solid black #000000 fill"

  - layer: DecorativeVisualSection
    zIndex: 200
    position: center
    absoluteY: 180
    children:
      - CircularGlow
      - AnimatedLines (11 vectors)
      - Ellipse 2
      - Ellipse 3
    notes: "Green stroke vectors with 4px layer blur effect"

  - layer: FloatingActionButton_Left
    zIndex: 300
    position: center-left
    absoluteY: 400
    children:
      - ChartIcon
    notes: "49x62 icon frame, positioned bottom-left of visual"

  - layer: FloatingActionButton_Right
    zIndex: 350
    position: center-right
    absoluteY: 320
    children:
      - SparkleIcon
    notes: "49x62 icon frame, positioned right of visual"

  - layer: ContentStack
    zIndex: 400
    position: full
    absoluteY: 60
    children:
      - ProgressIndicator
      - HeaderSection
      - UsernameInputSection
      - TrustBadges
      - CTAButton
    notes: "Main content container with VERTICAL auto-layout"

  - layer: GradientBorders
    zIndex: 500
    position: overlay
    absoluteY: 0
    children: []
    notes: "Decorative gradient borders on input fields"
```

**Critical:** Layer order determines visual stacking. Code generators MUST respect this ordering to achieve pixel-perfect match with Figma design.

## Components

### OnboardingAnalysisView (Root)

| Property | Value |
|----------|-------|
| **Element** | `<main>` |
| **Layout** | `relative w-full h-screen overflow-hidden` |
| **Classes/Styles** | `bg-black flex flex-col items-center` |
| **Dimensions** | 390 x 844px (iPhone 13/14 viewport) |
| **Children** | BackgroundLayer, DecorativeVisualSection, FloatingButtons, ContentStack |
| **Notes** | Root container with clipped content, dark theme |

---

### ProgressIndicator

| Property | Value |
|----------|-------|
| **Element** | `<nav>` with `<span>` dots |
| **Layout** | `flex flex-row gap-2 items-center justify-center` |
| **Classes/Styles** | `pt-16` |
| **Props/Variants** | `currentStep: number` (1-6), `totalSteps: 6` |
| **Children** | 6 Dot components |
| **Notes** | Last dot (index 5) is active/yellow |

#### Dot Component

| Property | Value |
|----------|-------|
| **Element** | `<span>` |
| **Classes** | Inactive: `w-2 h-2 rounded-full bg-[#858585]` |
|            | Active: `w-2 h-2 rounded-full bg-[#f2f20d]` |

---

### HeaderSection

| Property | Value |
|----------|-------|
| **Element** | `<header>` |
| **Layout** | `flex flex-col gap-6` |
| **Classes/Styles** | `text-center px-6` |
| **Children** | TitleText, DescriptionText |
| **Notes** | Frame 2121316306 with VERTICAL gap:24px |

#### TitleText

| Property | Value |
|----------|-------|
| **Element** | `<h1>` |
| **Typography** | `font-poppins text-2xl font-semibold leading-[36px] text-white` |
| **Special** | Word "personalized" has yellow highlight (#f2f20d) |
| **Implementation** | Use `<span class="text-[#f2f20d]">personalized</span>` inline |

#### DescriptionText

| Property | Value |
|----------|-------|
| **Element** | `<p>` |
| **Typography** | `font-poppins text-base font-normal leading-6 text-white` |
| **Classes** | `opacity-90` (if needed for subtle hierarchy) |

---

### DecorativeVisualSection

| Property | Value |
|----------|-------|
| **Element** | `<div>` (decorative, `aria-hidden="true"`) |
| **Layout** | `absolute inset-0 flex items-center justify-center` |
| **Classes/Styles** | `pointer-events-none` |
| **Children** | CircularGlow, AnimatedLines, Ellipse rings |
| **Notes** | Complex vector artwork - recommend PNG/SVG export |

#### AnimatedLines

| Property | Value |
|----------|-------|
| **Type** | Vector group (11 items: Vector 4-15) |
| **Stroke** | `#00ff33` (green) |
| **Effect** | `blur-[4px]` (LAYER_BLUR radius: 4px) |
| **Notes** | Decorative animated lines - export as optimized PNG |

---

### FloatingActionButton

| Property | Value |
|----------|-------|
| **Element** | `<button>` |
| **Layout** | `absolute flex items-center justify-center` |
| **Dimensions** | 49 x 62px |
| **Variants** | Left (chart icon), Right (sparkle icon) |
| **Classes** | `rounded-xl bg-transparent` |

#### Variants
- **Left Button**: `left-4 bottom-[280px]` - contains chart icon
- **Right Button**: `right-4 bottom-[360px]` - contains sparkle icon

---

### UsernameInputSection

| Property | Value |
|----------|-------|
| **Element** | `<section>` |
| **Layout** | `flex flex-col gap-3` |
| **Classes/Styles** | `w-full px-6` |
| **Children** | ProfileSelector, TextInputField |
| **Notes** | Frame 2121316832 with VERTICAL gap:12px |

#### ProfileSelector

| Property | Value |
|----------|-------|
| **Element** | `<button>` (dropdown trigger) |
| **Layout** | `flex flex-row justify-between items-center w-full` |
| **Classes/Styles** | `p-3 rounded-xl border border-[#1e1e1e]` |
| **Children** | ProfilePreview, DropdownChevron |
| **Notes** | Frame 2121316830 with HORIZONTAL space-between |

#### ProfilePreview

| Property | Value |
|----------|-------|
| **Element** | `<div>` |
| **Layout** | `flex flex-row gap-2 items-center` |
| **Children** | ProfileImage, TextStack (BrandName, Username) |

| Sub-component | Classes |
|---------------|---------|
| ProfileImage | `w-8 h-8 rounded-full object-cover` |
| BrandName | `font-poppins text-[11.8px] font-bold leading-[12.6px] text-black` |
| Username | `font-poppins text-[10.1px] font-normal leading-[12.6px] text-[#858585]` |

#### TextInputField

| Property | Value |
|----------|-------|
| **Element** | `<div>` containing `<input>` |
| **Layout** | `flex flex-row gap-[10px] items-center` |
| **Classes/Styles** | `pl-4 py-3 rounded-xl border` |
| **Border** | Gradient border (see Gradients section) |
| **Children** | AtSymbol, Input element |
| **Notes** | Frame 2121316831 with HORIZONTAL gap:10px, padding:16/0/0/0 |

| Sub-component | Implementation |
|---------------|----------------|
| AtSymbol | `<span class="text-white">@</span>` |
| Input | `<input type="text" placeholder="e.g. @viralz" class="bg-transparent text-white placeholder-white/50 font-poppins text-sm">` |

---

### TrustBadges

| Property | Value |
|----------|-------|
| **Element** | `<div>` |
| **Layout** | `flex flex-row gap-3 justify-center` |
| **Children** | SafeSecureBadge, OfficialAPIBadge |
| **Notes** | Frame 2121316702 with HORIZONTAL gap:12px |

#### Badge Component

| Property | Value |
|----------|-------|
| **Element** | `<span>` |
| **Layout** | `flex flex-row gap-1 items-center` |
| **Typography** | `font-poppins text-sm font-medium text-[#f2f20d]` |
| **Children** | Icon (16x16), Text |

| Badge | Icon Node | Text |
|-------|-----------|------|
| SafeSecure | lucide/lock (6:133) | "Safe & Secure" |
| OfficialAPI | TikTok icon (6:123) | "Official Tiktok API" |

---

### CTAButton

| Property | Value |
|----------|-------|
| **Element** | `<button>` |
| **Layout** | `flex flex-row gap-4 justify-center items-center` |
| **Classes/Styles** | `w-full py-4 px-8 rounded-full bg-[#f2f20d]` |
| **Typography** | `font-poppins text-xl font-semibold text-black` |
| **Children** | ButtonText |
| **Notes** | Frame 2121316743 with padding:8px all sides |

#### Variants
- **Default**: `bg-[#f2f20d] text-black`
- **Hover**: `bg-[#e5e50c]` (slightly darker yellow)
- **Active**: `bg-[#d4d40b] scale-[0.98]`
- **Disabled**: `bg-[#f2f20d]/50 cursor-not-allowed`

---

## Design Tokens (Ready to Use)

### Colors

| Property | Color | Opacity | Usage |
|----------|-------|---------|-------|
| Background | #000000 | 1.0 | `.background(Color.black)` |
| Yellow Accent | #f2f20d | 1.0 | `.foregroundColor(Color(hex: "#f2f20d"))` |
| White | #ffffff | 1.0 | `.foregroundColor(Color.white)` |
| Green Stroke | #00ff33 | 1.0 | `.stroke(Color(hex: "#00ff33"))` |
| Gray | #858585 | 1.0 | `.foregroundColor(Color(hex: "#858585"))` |
| Dark Gray | #1e1e1e | 1.0 | `.stroke(Color(hex: "#1e1e1e"))` |

### Gradients

| Name | Type | Stops | Usage |
|------|------|-------|-------|
| Border Gradient 1 | LINEAR | #1e1e1e @ 0% (opacity: 0.0) -> #1e1e1e @ 100% (opacity: 1.0) | Input field border fade-in |
| Border Gradient 2 | LINEAR | #f2f20d @ 0% (opacity: 1.0) -> #f2f20d @ 100% (opacity: 0.0) | Yellow accent border fade-out |

**SwiftUI Implementation:**
```swift
LinearGradient(
    stops: [
        .init(color: Color(hex: "#1e1e1e").opacity(0), location: 0),
        .init(color: Color(hex: "#1e1e1e"), location: 1)
    ],
    startPoint: .leading,
    endPoint: .trailing
)
```

### CSS Custom Properties

```css
:root {
  /* Colors */
  --color-background: #000000;
  --color-accent-yellow: #f2f20d;
  --color-text-primary: #ffffff;
  --color-text-secondary: #858585;
  --color-stroke-green: #00ff33;
  --color-border-dark: #1e1e1e;

  /* Typography - Poppins */
  --font-family: 'Poppins', sans-serif;
  --font-size-xs: 0.63rem;    /* 10.1px */
  --font-size-sm: 0.74rem;    /* 11.8px */
  --font-size-base: 0.875rem; /* 14px */
  --font-size-md: 1rem;       /* 16px */
  --font-size-lg: 1.25rem;    /* 20px */
  --font-size-xl: 1.5rem;     /* 24px */

  /* Font Weights */
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Line Heights */
  --line-height-tight: 1.07;  /* 12.6px for 11.8px */
  --line-height-normal: 1.5;  /* 24px for 16px, 30px for 20px, 36px for 24px */

  /* Spacing */
  --spacing-xs: 0.25rem;  /* 4px */
  --spacing-sm: 0.5rem;   /* 8px */
  --spacing-md: 0.75rem;  /* 12px */
  --spacing-lg: 1rem;     /* 16px */
  --spacing-xl: 1.5rem;   /* 24px */

  /* Effects */
  --blur-decorative: 4px;
  --radius-full: 9999px;
  --radius-xl: 0.75rem;   /* 12px */
}
```

### Tailwind Token Map

| Token | Tailwind Class | CSS Value |
|-------|----------------|-----------|
| background | `bg-black` | #000000 |
| accent-yellow | `bg-[#f2f20d]` | #f2f20d |
| text-primary | `text-white` | #ffffff |
| text-secondary | `text-[#858585]` | #858585 |
| stroke-green | `stroke-[#00ff33]` | #00ff33 |
| border-dark | `border-[#1e1e1e]` | #1e1e1e |
| heading | `text-2xl font-semibold leading-[36px]` | 24px / 600 / 36px |
| body | `text-base font-normal leading-6` | 16px / 400 / 24px |
| button-text | `text-xl font-semibold leading-[30px]` | 20px / 600 / 30px |
| label | `text-sm font-medium leading-[21px]` | 14px / 500 / 21px |
| blur-effect | `blur-[4px]` | 4px layer blur |

### Typography Styles

| Style | Font | Size | Weight | Line Height | Letter Spacing |
|-------|------|------|--------|-------------|----------------|
| Button CTA | Poppins | 20px | 600 | 30px | 0 |
| Heading | Poppins | 24px | 600 | 36px | 0 |
| Body | Poppins | 16px | 400 | 24px | 0 |
| Label | Poppins | 14px | 500 | 21px | 0 |
| Input Hint | Poppins | 14px | 400 | 21px | 0 |
| Brand Name | Poppins | 11.8px | 700 | 12.6px | 0 |
| Username | Poppins | 10.1px | 400 | 12.6px | 0 |

---

## Assets Required

| Asset | Filename | Format | Node ID | Size | Classification | Optimization Notes |
|-------|----------|--------|---------|------|----------------|-------------------|
| Profile Image | `profile-viralz.webp` | WebP | 213:269 | 32x32 | IMAGE | Lazy load, provide @2x/@3x variants |
| Chart Icon | `icon-chart.svg` | SVG | 6:187 | 49x62 | ICON | Export as SVG for scalability |
| Sparkle Icon | `icon-sparkle.svg` | SVG | 6:189 | 49x62 | ICON | Export as SVG for scalability |
| Lock Icon | `icon-lock.svg` | SVG | 6:133 | 16x16 | ICON | Use lucide-react or export SVG |
| TikTok Icon | `icon-tiktok.svg` | SVG | 6:123 | 16x16 | ICON | Export as SVG |
| Decorative Visual | `visual-green-lines.png` | PNG | 6:175 | 300x300 | COMPLEX_VECTOR | **Export as PNG @2x/@3x** - too complex for inline SVG |
| Vector Decorations | `decorative-vectors.png` | PNG | 6:176-6:186 | varies | COMPLEX_VECTOR | **11 items - batch export as single PNG** |
| Dropdown Chevron | `icon-chevron-down.svg` | SVG | 213:272 | 12x12 | ICON | Simple vector, export SVG |
| Outer Ellipse | `ellipse-outer.svg` | SVG | 6:198 | varies | SHAPE | Part of decorative visual |
| Inner Ellipse | `ellipse-inner.svg` | SVG | 6:199 | varies | SHAPE | Part of decorative visual |

### Asset Classification Notes

**COMPLEX_VECTOR - Must export as PNG:**
- `visual-green-lines.png` - Contains 11 vector paths with layer blur effect (4px). Too complex for inline SVG. Export at 2x and 3x for retina displays.
- Decorative visual section has blur effects that don't translate well to CSS/SVG filters.

**ICON - Export as SVG:**
- All 16x16 and 49x62 icon frames are simple enough for SVG export.
- Lock icon may use lucide-react library alternative.

---

## Downloaded Assets

| Asset | Local Path | Size | Status |
|-------|------------|------|--------|
| Decorative Visual @2x | `Assets.xcassets/Images/DecorativeVisual.imageset/decorative-visual@2x.png` | 148.8 KB | OK |
| Decorative Visual @3x | `Assets.xcassets/Images/DecorativeVisual.imageset/decorative-visual@3x.png` | 293.5 KB | OK |
| Chart Icon | `Assets.xcassets/Icons/IconChart.imageset/icon-chart.svg` | 1.3 KB | OK |
| Sparkle Icon | `Assets.xcassets/Icons/IconSparkle.imageset/icon-sparkle.svg` | 1.0 KB | OK |
| Lock Icon | `Assets.xcassets/Icons/IconLock.imageset/icon-lock.svg` | 2.1 KB | OK |
| TikTok Icon | `Assets.xcassets/Icons/IconTikTok.imageset/icon-tiktok.svg` | 1.7 KB | OK |
| Chevron Down Icon | `Assets.xcassets/Icons/IconChevronDown.imageset/icon-chevron-down.svg` | 0.9 KB | OK |
| Profile Image | `Assets.xcassets/Images/ProfileViralz.imageset/profile-viralz.png` | 1.2 MB | OK |

## Asset Import Statements

### SwiftUI Usage

```swift
// Icons (use Image with asset name)
Image("IconChart")
Image("IconSparkle")
Image("IconLock")
Image("IconTikTok")
Image("IconChevronDown")

// Images (use Image with asset name)
Image("DecorativeVisual")
Image("ProfileViralz")
```

### Asset Catalog Structure

```
Assets.xcassets/
├── Contents.json
├── Icons/
│   ├── Contents.json
│   ├── IconChart.imageset/
│   │   ├── Contents.json
│   │   └── icon-chart.svg
│   ├── IconSparkle.imageset/
│   │   ├── Contents.json
│   │   └── icon-sparkle.svg
│   ├── IconLock.imageset/
│   │   ├── Contents.json
│   │   └── icon-lock.svg
│   ├── IconTikTok.imageset/
│   │   ├── Contents.json
│   │   └── icon-tiktok.svg
│   └── IconChevronDown.imageset/
│       ├── Contents.json
│       └── icon-chevron-down.svg
└── Images/
    ├── Contents.json
    ├── DecorativeVisual.imageset/
    │   ├── Contents.json
    │   ├── decorative-visual@2x.png
    │   └── decorative-visual@3x.png
    └── ProfileViralz.imageset/
        ├── Contents.json
        └── profile-viralz.png
```

## Asset Download Summary

- **Total assets:** 8
- **Successfully downloaded:** 8
- **Failed:** 0
- **Warnings:** 0
- **Download timestamp:** 20260126-184545

### Asset Classification Validation

| Asset | Node ID | Classification | Format | Scales | Status |
|-------|---------|----------------|--------|--------|--------|
| Decorative Visual | 6:175 | COMPLEX_VECTOR | PNG | @2x, @3x | CORRECT - Exported as PNG with retina scales |
| Chart Icon | 6:187 | ICON | SVG | 1x | CORRECT - Vector scalable |
| Sparkle Icon | 6:189 | ICON | SVG | 1x | CORRECT - Vector scalable |
| Lock Icon | 6:133 | ICON | SVG | 1x | CORRECT - Vector scalable |
| TikTok Icon | 6:123 | ICON | SVG | 1x | CORRECT - Vector scalable |
| Chevron Down | 213:272 | ICON | SVG | 1x | CORRECT - Vector scalable |
| Profile Image | 213:269 | IMAGE_FILL | PNG | 1x | OK - Source image preserved |

---

## Implementation Checklist

### Setup
- [x] Create assets directory structure: `Assets.xcassets/Icons/`, `Assets.xcassets/Images/`
- [x] Create component file: `OnboardingAnalysisView.swift` (SwiftUI)
- [ ] Add CSS custom properties to global styles
- [ ] Import Poppins font (weights: 400, 500, 600, 700)

### Spec Validation (Self-Check)
- [x] Implementation Spec file created at correct path
- [x] Component Hierarchy section complete
- [x] Layer Order section complete with zIndex values
- [x] absoluteY coordinates documented for all layers
- [x] Design Tokens extracted and mapped
- [x] Asset List generated with all required assets
- [x] Asset classification marked (COMPLEX_VECTOR for PNG export)

### Component Development

#### Root Container
- [x] Implement OnboardingAnalysisView root with black background
- [x] Set up 390x844 viewport constraints
- [x] Apply overflow clipping

#### Progress Indicator
- [x] Create reusable Dot component with active/inactive states
- [x] Implement ProgressIndicator with 6 dots
- [x] Wire up currentStep prop

#### Header Section
- [x] Implement TitleText with inline yellow highlight span
- [x] Apply Poppins 24px SemiBold typography
- [x] Implement DescriptionText with 16px Regular

#### Decorative Visual
- [x] Export green lines visual as PNG @2x/@3x
- [x] Position absolutely in center
- [x] Apply layer blur effect (4px)
- [x] Mark as aria-hidden for accessibility

#### Floating Action Buttons
- [x] Implement left button with chart icon (49x62)
- [x] Implement right button with sparkle icon (49x62)
- [x] Position absolutely relative to visual section

#### Username Input Section
- [x] Implement ProfileSelector dropdown button
- [x] Add profile image, brand name, username display
- [x] Implement TextInputField with gradient border
- [x] Handle @ symbol prefix styling

#### Trust Badges
- [x] Implement SafeSecure badge with lock icon
- [x] Implement OfficialAPI badge with TikTok icon
- [x] Apply yellow text (#f2f20d)

#### CTA Button
- [x] Implement full-width yellow button
- [x] Apply Poppins 20px SemiBold black text
- [ ] Add hover, active, disabled state variants (SwiftUI button states)

### Assets
- [x] Export decorative visual as PNG (Node 6:175) at @2x/@3x
- [x] Export chart icon as SVG (Node 6:187)
- [x] Export sparkle icon as SVG (Node 6:189)
- [x] Export lock icon as SVG (Node 6:133) or use lucide
- [x] Export TikTok icon as SVG (Node 6:123)
- [x] Export profile image as PNG (Node 213:269)
- [x] Export dropdown chevron as SVG (Node 213:272)

### Quality Assurance
- [ ] Verify visual match with design screenshot
- [ ] Test on iPhone 13/14 viewport (390x844)
- [x] Validate accessibility (semantic HTML, ARIA labels)
- [ ] Check keyboard navigation for interactive elements
- [x] Verify contrast ratios (yellow on black: 17.48:1 - PASS)
- [ ] Test input field focus states

---

## Design Warnings

- **Gradient borders:** Input field uses linear gradient borders. Ensure proper implementation using CSS `border-image` or pseudo-elements.
- **Layer blur effect:** The decorative vectors use 4px layer blur. This may impact performance if implemented as CSS filter. Recommend exporting as pre-blurred PNG.
- **Small text sizes:** Brand name (11.8px) and username (10.1px) are below recommended minimum. Ensure legibility on all devices.

---

## Assumptions Made

1. **Progress indicator position:** Assumed 6 dots based on design description, with last dot active (step 6 of 6).
2. **Floating button interaction:** Assumed buttons are interactive. May be decorative - clarify with designer.
3. **Gradient border direction:** Assumed left-to-right gradient based on typical patterns. Verify with Figma inspection.
4. **Input validation:** Assumed username input accepts TikTok handle format (@username).
5. **Profile selector behavior:** Assumed dropdown shows account selection. Implementation details TBD.

---

## Items Flagged for Review

1. **Floating action buttons purpose:** Are the chart and sparkle icons interactive or purely decorative?
2. **Profile selector data source:** Where does the profile list come from? Pre-populated or user accounts?
3. **Animation requirements:** Are the green decorative lines animated? If so, what animation style?
4. **Input validation rules:** What are the validation rules for TikTok username input?
5. **Error states:** Design needed for invalid input, API errors, loading states.

---

## Platform Requirements

- **Minimum iOS:** iOS 15.0+ (for gradient support and modern SwiftUI features)
- **Font:** Poppins must be bundled or loaded from Google Fonts
- **Viewport:** Optimized for iPhone 13/14 (390x844) - test on other sizes

---

## Generated Code

| Component | File | Status |
|-----------|------|--------|
| OnboardingAnalysisView | `Views/Components/OnboardingAnalysisView.swift` | OK |

## Code Generation Summary

- **Framework:** SwiftUI (iOS 15.0+)
- **Components generated:** 1
- **Files created:** 1
- **Warnings:** 0
- **Generation timestamp:** 20260126-195500

## Files Created

### Views
- `Views/Components/OnboardingAnalysisView.swift`

### Extensions (included in component)
- `Color+Hex` extension (inline in component file)
- `View+Placeholder` extension (inline in component file)

## Component Features Implemented

### OnboardingAnalysisView.swift

**Properties:**
- `currentStep: Int` - Current step in onboarding flow (1-6)
- `usernameInput: Binding<String>` - Two-way binding for username text field
- `selectedProfile: String` - Display name for selected profile
- `selectedUsername: String` - Username handle for selected profile
- `onAnalyzeTapped: () -> Void` - Callback for CTA button tap
- `onProfileSelectorTapped: () -> Void` - Callback for profile dropdown tap

**Subviews:**
- `decorativeVisualSection` - Blurred decorative image with proper z-ordering
- `floatingActionButtons` - Chart and sparkle icons positioned absolutely
- `contentStack` - Main content VStack with all form elements
- `progressIndicator` - 6-dot progress indicator with active state
- `headerSection` - Title with highlighted "personalized" and description
- `usernameInputSection` - Profile selector and text input
- `profileSelector` - Dropdown button with profile preview
- `textInputField` - Input with @ prefix and gradient border
- `trustBadges` - Safe & Secure and Official TikTok API badges
- `ctaButton` - Yellow full-width analyze button

**Accessibility:**
- VoiceOver labels on all interactive elements
- Accessibility hints for buttons
- Combined accessibility elements for grouped content
- Decorative visual hidden from accessibility tree

---

## Next Agent Input

**Ready for:** Compliance Checker Agent

**Input file:** `docs/figma-reports/ElHzcNWC8pSYTz2lhPP9h0-spec.md`

**Components generated:** 1

**Framework:** SwiftUI (iOS 15.0+)

**Files to review:**
- `Views/Components/OnboardingAnalysisView.swift`
