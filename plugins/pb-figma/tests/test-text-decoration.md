# Test: Text Decoration Color Extraction

## Input
Figma node with:
- Text: "Hook"
- textDecoration: UNDERLINE
- Text fill color: #ffd100 (yellow, opacity: 1.0)

## Expected Output in Implementation Spec

```markdown
### Text Decoration

**Component:** HookText
- **Decoration:** Underline
- **Color:** #ffd100 (uses text color)

**SwiftUI Mapping:** `.underline(color: Color(hex: "#ffd100"))`
```
