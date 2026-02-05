# Visual Validation Loop - Claude Vision Approach

> **Used by:** compliance-checker

This document explains the **Claude Vision-based simple approach** for Phase 4: Visual Validation.

## Core Principle

```
Figma Screenshot + Browser Screenshot → Claude Vision Comparison → TodoWrite
```

Instead of complex tools (ImageMagick, RMSE calculation), we use Claude's visual analysis capabilities to detect differences.

---

## Workflow Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    VISUAL VALIDATION LOOP                     │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. FIGMA SCREENSHOT                                          │
│     └─→ Pixelbyte Figma MCP: figma_get_screenshot            │
│                                                               │
│  2. BROWSER SCREENSHOT                                        │
│     └─→ Claude in Chrome MCP: computer({action: "screenshot"})│
│                                                               │
│  3. CLAUDE VISION COMPARISON                                  │
│     └─→ Analyze both images, list differences                │
│                                                               │
│  4. DIFFERENCE LIST WITH TODOWRITE                           │
│     └─→ One todo item for each difference                    │
│                                                               │
│  5. FIX AND RE-CHECK                                         │
│     └─→ Complete todos, take new screenshot if needed        │
│                                                               │
│  6. RESPONSIVE VALIDATION (Optional)                         │
│     └─→ Validate tablet (768px) and mobile (375px)          │
│                                                               │
│  7. ACCESSIBILITY VALIDATION                                 │
│     └─→ Keyboard nav, a11y tree, color contrast             │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Step 1: Take Figma Screenshot

**Use Pixelbyte Figma MCP:**

```javascript
mcp__pixelbyte-figma-mcp__figma_get_screenshot({
  params: {
    file_key: "FIGMA_FILE_KEY",  // From URL: figma.com/design/FILE_KEY/...
    node_ids: ["NODE_ID"],        // Node ID in 123:456 format
    format: "png",
    scale: 2                      // For 2x quality
  }
})
```

**Response:** Returns Figma CDN URL (e.g., `https://figma-alpha-api.s3.us-west-2.amazonaws.com/...`)

To view this URL with Claude Vision:
- Share URL directly in message → Claude views automatically
- Or fetch content with `WebFetch`

---

## Step 2: Take Browser Screenshot (Claude in Chrome MCP)

**⚠️ IMPORTANT:** Tab context MUST be obtained first!

**Screenshot with Claude in Chrome MCP:**

```javascript
// 1. Get tab context (ALWAYS FIRST STEP!)
mcp__claude-in-chrome__tabs_context_mcp({
  createIfEmpty: true
})
// → Save returned tabId and use for all subsequent operations

// 2. Navigate to dev server
mcp__claude-in-chrome__navigate({
  url: "http://localhost:3000/[component-path]",
  tabId: <returned-tab-id>
})

// 3. Wait for page to load
mcp__claude-in-chrome__computer({
  action: "wait",
  duration: 2,
  tabId: <tab-id>
})
```

**Get Accessibility Tree (to find element ref):**
```javascript
// 4. Get page accessibility tree
mcp__claude-in-chrome__read_page({
  tabId: <tab-id>
})
```

**read_page output example:**
```
- main
  - div "container"
    - article ref="ref_1" "HeroCard"    ← Use this ref
      - h2 "Title"
      - p "Description"
    - button ref="ref_2" "Submit"
```

**Take Screenshot:**
```javascript
// 5. Take full page screenshot
mcp__claude-in-chrome__computer({
  action: "screenshot",
  tabId: <tab-id>
})
// → Returns imageId, viewable by Claude Vision
```

**Focus on Specific Element:**
```javascript
// Scroll element into view
mcp__claude-in-chrome__computer({
  action: "scroll_to",
  ref: "ref_1",  // ref from read_page
  tabId: <tab-id>
})

// Zoom to specific region
mcp__claude-in-chrome__computer({
  action: "zoom",
  region: [100, 200, 500, 600],  // [x0, y0, x1, y1] coordinates
  tabId: <tab-id>
})
```

**Find Element with Natural Language:**
```javascript
// Find element using natural language
mcp__claude-in-chrome__find({
  query: "hero card component",
  tabId: <tab-id>
})
// → Returns refs of matching elements
```

**Tips:**
- If dev server not running → Run `npm run dev` with Bash
- If element ref not found → Check `read_page` output or use `find`
- Adding data-testid → Recommended for reliable element finding
- Full page screenshot → Take after making component visible

---

## Step 3: Compare with Claude Vision

Compare both images side by side to detect differences.

### Check Categories

| Category | Items to Check |
|----------|----------------|
| **Typography** | Font family, size, weight, line-height, letter-spacing, color |
| **Spacing** | Padding (all directions), margin, gap |
| **Colors** | Background, border, text, shadow colors |
| **Layout** | Flex direction, alignment, justify, width, height |
| **Assets** | Icon size/color, image aspect ratio, border-radius |

### Example Analysis Output

```markdown
## 🔍 Figma vs Implementation Comparison

### ❌ Typography Differences
| Element | Figma | Implementation | Tailwind Fix |
|---------|-------|----------------|--------------|
| Title | 32px bold | 28px medium | `text-3xl font-bold` |
| Description | 16px gray-500 | 14px gray-400 | `text-base text-gray-500` |

### ❌ Spacing Differences
| Element | Figma | Implementation | Tailwind Fix |
|---------|-------|----------------|--------------|
| Card padding | 24px | 16px | `p-6` |
| Button gap | 12px | 8px | `gap-3` |

### ❌ Color Differences
| Element | Figma | Implementation | Tailwind Fix |
|---------|-------|----------------|--------------|
| Primary button | #FE4601 | #3B82F6 | `bg-orange-1` |

### ✅ Layout
Correct - flexbox direction and alignment match.

### ✅ Assets
Correct - icon sizes and border-radius match.
```

---

## Step 4: Create Difference List with TodoWrite

Create a todo item for each detected difference:

```javascript
TodoWrite({
  todos: [
    {
      content: "Title font-size: text-2xl → text-3xl",
      status: "pending",
      activeForm: "Fixing title font-size"
    },
    {
      content: "Card padding: p-4 → p-6",
      status: "pending",
      activeForm: "Fixing card padding"
    },
    {
      content: "Button background: bg-blue-500 → bg-orange-1",
      status: "pending",
      activeForm: "Fixing button background"
    },
    {
      content: "Description text color: text-gray-400 → text-gray-500",
      status: "pending",
      activeForm: "Fixing description text color"
    }
  ]
})
```

### Recommended Todo Format

```
[Element] [Property]: [Current Value] → [Correct Value]
```

Examples:
- `Title font-size: text-2xl → text-3xl`
- `Card padding: p-4 → p-6`
- `Icon color: text-gray-500 → text-white`
- `Gap between buttons: gap-2 → gap-4`

---

## Step 5: Fix and Re-check

### Fix Process

1. **Set todo to in_progress**
2. **Fix the code** (using Edit tool)
3. **Mark todo as completed**
4. **Move to next todo**

### Re-check

When all todos are complete:

1. Take new browser screenshot
2. Compare with Figma screenshot again
3. If new differences found → Add new todo
4. If no differences → Proceed to Phase 5

**⚠️ Smart Termination Logic (v2.0):**

```
Iteration 1:
- Calculate match %
  - ≥95% (pass_threshold) → PASS, exit loop
  - <85% (warn_threshold) → Create todos, fix, → Iteration 2
  - 85-94% → WARN, ask user to continue or accept

Iteration 2:
- Re-check and calculate improvement delta
  - Delta ≥10% (visual_improvement_threshold) → Progress made, → Iteration 3
  - Delta <10% → STALLED (diminishing returns), mark ACCEPTABLE, exit loop
  - Match ≥95% → PASS, exit loop

Iteration 3:
- Final check (max_visual_iterations reached)
  - ≥95% → PASS
  - 85-94% → WARN (accept visual differences)
  - <85% → FAIL (manual review needed)
  - Exit loop

Termination Conditions:
1. Match ≥pass_threshold% (default 95%) → PASS, exit
2. max_visual_iterations reached (default 3) → ACCEPTABLE/WARN, exit
3. Improvement <visual_improvement_threshold% (default 10%) → STALLED, exit
4. User abort → MANUAL_REVIEW, exit
```

**All thresholds configurable in `pipeline-config.md`.** Some differences (font rendering, subpixel) may be unfixable.

---

## Quick Reference

### Claude in Chrome MCP Tools

| Tool | Usage |
|------|-------|
| `tabs_context_mcp` | Get tab context (FIRST STEP!) |
| `tabs_create_mcp` | Create new tab |
| `navigate` | Navigate to URL |
| `computer({action: "screenshot"})` | Take full page screenshot |
| `computer({action: "zoom"})` | Zoom to specific region |
| `computer({action: "scroll_to"})` | Scroll to element |
| `computer({action: "wait"})` | Wait for specified duration |
| `read_page` | Get accessibility tree |
| `find` | Find element with natural language |
| `javascript_tool` | Execute JS on page |

### Pixelbyte Figma MCP Tools

| Tool | Usage |
|------|-------|
| `figma_get_screenshot` | Take node screenshot |
| `figma_get_node_details` | Get node details |
| `figma_get_design_tokens` | Get design tokens |

---

## Step 6: Responsive Validation (Optional but Recommended)

After desktop validation passes, validate responsive breakpoints:

**Reference:** `references/responsive-validation.md`

### Viewport Order

1. **Desktop (1440px)** - Already validated
2. **Tablet (768px)** - Validate next
3. **Mobile (375px)** - Validate last

### Process

For each breakpoint:

1. **Resize viewport**
```javascript
mcp__claude-in-chrome__resize_window({
  width: 768,  // or 375 for mobile
  height: 1024,
  tabId: <tab-id>
})
```

2. **Wait for reflow**
```javascript
mcp__claude-in-chrome__computer({
  action: "wait",
  duration: 1,
  tabId: <tab-id>
})
```

3. **Take screenshot**
```javascript
mcp__claude-in-chrome__computer({
  action: "screenshot",
  tabId: <tab-id>
})
```

4. **Compare with Claude Vision**
- Check layout changes
- Check typography scaling
- Check component visibility
- Check spacing adjustments

5. **Create todos for differences**

6. **Fix and re-check**

### Skip Conditions

Skip responsive validation if:
- Figma design has only desktop frame
- User explicitly requests desktop-only
- Time constraints (document in report)

---

## Step 7: Accessibility Validation

After visual validation, check accessibility:

**Reference:** `references/accessibility-validation.md`

### Automated Check (if test exists)

```bash
npm run test:a11y -- {ComponentName}
```

### Manual Checks

1. **Keyboard Navigation**
```javascript
mcp__claude-in-chrome__computer({
  action: "key",
  text: "Tab",
  repeat: 5,
  tabId: <tab-id>
})

mcp__claude-in-chrome__computer({
  action: "screenshot",
  tabId: <tab-id>
})
```

2. **Accessibility Tree**
```javascript
mcp__claude-in-chrome__read_page({
  tabId: <tab-id>,
  filter: "interactive"
})
```

### Check For

- [ ] All images have alt text
- [ ] All buttons have accessible names
- [ ] Focus visible on interactive elements
- [ ] Color contrast sufficient
- [ ] Semantic HTML used

### Create Todos

For each a11y issue found:
```
"A11y: [Issue description] → [Fix]"
```

### Fix and Verify

1. Fix each a11y todo
2. Re-run automated check
3. Re-test keyboard navigation
4. Proceed to Phase 5

---

## Console Log Debugging

Read console logs for debugging:

```javascript
mcp__claude-in-chrome__read_console_messages({
  tabId: <tab-id>,
  pattern: "error|warning",  // Filter only errors and warnings
  onlyErrors: true           // Or get only errors
})
```

---

## Final Checklist

```
□ Tab context obtained
□ Figma screenshot taken
□ Browser screenshot taken
□ Visual comparison done
□ Visual differences fixed
□ Desktop validation passed
□ Responsive validation passed (optional)
□ Accessibility validation passed
□ All todos completed
□ Ready for Phase 5
```
