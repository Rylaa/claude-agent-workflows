# Test: Inline Text Color Detection

## Purpose
Verify that design-analyst detects and documents inline text color variations.

## Input

Figma TEXT node with character style overrides:
- Node ID: 3:260
- Full text: "Let's fix your Hook"
- Characters 0-15: white (#FFFFFF)
- Characters 15-19: yellow (#F2F20D) + underline

## Expected Output (Implementation Spec)

### Inline Text Variations

**Component:** TitleText
**Full Text:** "Let's fix your Hook"
**Variations:**
| Range | Text | Color | Weight | Decoration |
|-------|------|-------|--------|------------|
| 0-15 | "Let's fix your " | #FFFFFF | 600 | none |
| 15-19 | "Hook" | #F2F20D | 600 | underline |

## Expected Code (SwiftUI)

```swift
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

## Verification Steps

1. [ ] design-analyst queries TEXT node for characterStyleOverrides
2. [ ] Variations table appears in spec with correct ranges
3. [ ] code-generator produces Text concatenation
4. [ ] Each segment has correct color and decoration
