# Border Color & Inline Text Color Issue Analysis

> **Created:** 2026-01-25
> **Problem:** Generated SwiftUI code shows incorrect border colors (grayish instead of white) and fails to capture inline text color variations

## Problem Statement

Two visual discrepancies between Figma designs and generated SwiftUI code:

### Issue 1: Border Color Inaccuracy
- **Expected:** Pure white border (as in Figma design)
- **Actual:** Grayish border in generated SwiftUI code
- **Impact:** Visual fidelity compromised, brand colors incorrect

### Issue 2: Inline Text Color Not Captured
- **Expected:** Text with one word in different color preserved
- **Actual:** All text rendered in single color
- **Impact:** Rich text formatting lost, design intent not communicated

## Root Cause Analysis

### pb-figma Architecture Review

The pb-figma system uses a 5-agent pipeline:

```
Figma URL
    ↓
1. Design Validator → Validation Report
    ↓
2. Design Analyst → Implementation Spec (extracts design tokens)
    ↓
3. Asset Manager → Updated Spec + Downloaded Assets
    ↓
4. Code Generator (SwiftUI) → Component Files
    ↓
5. Compliance Checker → Final Report
```

**Critical Integration Point:** Step 4 uses Pixelbyte Figma MCP Server's `figma_generate_code` tool to generate base SwiftUI code, then enhances with SwiftUI-specific patterns.

### Issue 1: Border Color - Potential Root Causes

**Hypothesis 1: MCP Color Extraction Issue**
- `figma_generate_code` may be extracting incorrect RGB/opacity values
- Color space conversion (Figma → SwiftUI) could introduce errors
- Opacity handling might be defaulting to < 1.0 (causing gray tint)

**Hypothesis 2: Design Token Mapping Issue**
- Design Analyst (`design-analyst.md:116-150`) maps Figma tokens to implementation
- Incorrect mapping: `white` → `Color.white.opacity(0.8)` instead of `Color.white`
- Token extraction from `figma_get_design_tokens` may miss exact color values

**Hypothesis 3: SwiftUI Enhancement Issue**
- Code Generator (`code-generator-swiftui.md:160-171`) replaces hardcoded values with semantic tokens
- Semantic color substitution may introduce incorrect Asset Catalog reference
- Example: `Color("BorderWhite")` pointing to gray color in Asset Catalog

**Evidence Required:**
- [ ] Examine Implementation Spec's Design Tokens section for border color values
- [ ] Check `figma_get_node_details` output for stroke color properties
- [ ] Verify generated SwiftUI code's actual Color() values
- [ ] Test `figma_generate_code` directly on border nodes

### Issue 2: Inline Text Color - Architectural Limitation

**Analysis:**

Figma supports **rich text** with inline styling (different colors/fonts within single text node). Current pb-figma architecture does NOT capture this:

**Evidence from codebase:**
1. **Design Analyst** (`design-analyst.md:116-150`): Extracts typography tokens as single values:
   ```
   Font: Inter → font-family: 'Inter'
   Size: 24px → font-size: 1.5rem
   ```
   No mention of inline text variations.

2. **MCP Tools:** `figma_generate_code` generates code for entire node, but unclear if it preserves rich text attributes.

3. **SwiftUI Generator** (`code-generator-swiftui.md:279-388`): Component template shows:
   ```swift
   Text(title)
     .font(.title2)
     .foregroundColor(Color("TextPrimary"))
   ```
   Single Text() with single color - no AttributedString usage.

**Root Cause:** System architecture treats text as atomic (single style), not composite (mixed styles).

**Required Capabilities:**
- [ ] Figma API must expose inline text runs with individual formatting
- [ ] Design Analyst must extract text segments with color attributes
- [ ] SwiftUI Generator must use AttributedString for mixed-color text
- [ ] MCP `figma_generate_code` must return rich text structure

## Recommended Investigation Path

### Phase 1: Isolate Border Color Issue (Est: 30 min)

1. **Test MCP Directly:**
   ```bash
   # Call figma_get_node_details on border node
   # Examine stroke color RGB values
   ```

2. **Examine Implementation Spec:**
   - Check Design Tokens → Colors section
   - Look for border color extraction
   - Verify RGB values match Figma (255, 255, 255 for white)

3. **Review Generated Code:**
   - Find `.stroke()` or `.border()` modifiers
   - Check Color() initialization values
   - Verify Asset Catalog references

**Decision Point:** If MCP returns correct values → Issue in Design Analyst or Code Generator. If MCP returns wrong values → MCP bug.

### Phase 2: Assess Inline Text Feasibility (Est: 45 min)

1. **Check Figma API Capabilities:**
   - Call `figma_get_node_details` on multi-color text node
   - Look for `characters` field with style runs
   - Determine if API exposes inline formatting

2. **Review MCP Implementation:**
   - Test `figma_generate_code` on rich text node
   - Check if output includes AttributedString or multiple Text() views

3. **Evaluate Architecture Gaps:**
   - Design Analyst: Can it extract text segments?
   - Implementation Spec: Can it represent mixed-color text?
   - Code Generator: Can it produce AttributedString?

**Decision Point:** If Figma API supports → Enhancement needed. If Figma API doesn't support → Limitation documented.

## Proposed Solutions

### Solution 1A: Fix Border Color - MCP Layer Issue

**If MCP returns incorrect values:**

**Changes:**
- File: Pixelbyte Figma MCP Server (external dependency)
- Fix: Correct color extraction in `figma_generate_code`
- Workaround: Use `figma_get_node_details` to extract strokes manually, bypass MCP generation for borders

### Solution 1B: Fix Border Color - Agent Layer Issue

**If agents mishandle correct MCP values:**

**Changes:**
- **Design Analyst** (`design-analyst.md`):
  - Enhance token extraction logic for stroke colors
  - Ensure exact RGB values preserved (no rounding)
  - Add validation: white should be (255, 255, 255, 1.0)

- **SwiftUI Generator** (`code-generator-swiftui.md`):
  - Fix token application for borders
  - Ensure Color.white used instead of Color("White") when appropriate
  - Add opacity verification (should be 1.0 for solid colors)

### Solution 2A: Add Inline Text Color Support

**If Figma API exposes rich text:**

**Architecture Changes:**

1. **Design Analyst Enhancement:**
   ```markdown
   ### Text with Inline Styling

   Extract text runs with individual colors:

   | Segment | Text | Color | Weight |
   |---------|------|-------|--------|
   | Run 1 | "Hello " | #000000 | 400 |
   | Run 2 | "World" | #FF0000 | 700 |
   ```

2. **Implementation Spec Extension:**
   ```markdown
   ## Text Segments

   Component: WelcomeText
   - Segment 1: "Welcome to " (color: textPrimary, weight: regular)
   - Segment 2: "Figma" (color: brandOrange, weight: bold)
   ```

3. **SwiftUI Generator Enhancement:**
   ```swift
   // Generate AttributedString for mixed-color text
   var attributedTitle: AttributedString {
       var str = AttributedString("Hello ")
       str.foregroundColor = .black

       var worldStr = AttributedString("World")
       worldStr.foregroundColor = .red
       worldStr.font = .boldSystemFont(ofSize: 24)

       str.append(worldStr)
       return str
   }

   Text(attributedTitle)
   ```

**Implementation Effort:** High (3-5 days)

### Solution 2B: Document Limitation

**If Figma API doesn't support:**

**Changes:**
- Add to README.md → Known Limitations
- Design Analyst outputs warning when detecting mixed-color text
- Compliance Checker flags rich text as "Not Supported"
- Documentation recommends breaking into separate Text() views in Figma

**Implementation Effort:** Low (1 hour)

## Next Steps

1. **Immediate:** Run diagnostic on specific Figma nodes with issues
2. **Test MCP:** Call tools directly to isolate layer of failure
3. **Document Findings:** Update this document with test results
4. **Choose Solution:** Based on root cause, implement fix
5. **Validate:** Re-generate code and verify visual accuracy

## Success Criteria

✅ **Border Color Fix:**
- Generated SwiftUI code produces pure white borders
- RGB values match Figma exactly: (255, 255, 255, alpha: 1.0)
- Visual QA passes: Screenshot comparison shows identical borders

✅ **Inline Text Color (if implementing 2A):**
- Multi-color text preserved in generated code
- AttributedString used with correct color segments
- Visual QA passes: Text rendering matches Figma

✅ **Documentation (if implementing 2B):**
- Known limitation clearly stated
- Workaround provided (split text nodes in Figma)
- Compliance Checker warns on rich text detection

## Related Files

- `/plugins/pb-figma/agents/design-analyst.md` - Token extraction logic
- `/plugins/pb-figma/agents/code-generator-swiftui.md` - SwiftUI code generation
- `/plugins/pb-figma/agents/code-generator-base.md` - MCP integration
- `/plugins/pb-figma/skills/figma-to-code/SKILL.md` - Pipeline orchestration

---

**Status:** Investigation pending - requires actual Figma file URL and node IDs to diagnose
