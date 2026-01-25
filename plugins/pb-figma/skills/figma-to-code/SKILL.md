---
name: figma-to-code
description: This skill handles pixel-perfect Figma design conversion to React/Next.js/Tailwind code using Pixelbyte Figma MCP Server. It should be used when a Figma URL or design selection needs to be converted to production-ready code. The skill employs a 5-phase workflow targeting 85%+ accuracy with Code Connect support for component mapping. Use cases include (1) generating code from Figma files, (2) design implementation with design tokens, (3) creating design system components with Code Connect, (4) pixel-perfect UI development, and (5) responsive web components. Automatic QA is performed via Claude in Chrome MCP for visual validation.
---

# Figma-to-Code Pixel-Perfect Conversion

This skill converts Figma designs to pixel-perfect React/Tailwind code using **Pixelbyte Figma MCP Server** with a **5-phase workflow** and **iterative validation**.

## Prerequisites

- **Pixelbyte Figma MCP** - Figma API integration
- **Figma Personal Access Token** - Required for API access
- **Claude in Chrome MCP** - Required for visual validation (browser automation)
- **Node.js** - Runtime environment

## MCP Server Configuration

### Pixelbyte Figma MCP Setup

Add to MCP configuration:

```json
{
  "mcpServers": {
    "pixelbyte-figma-mcp": {
      "command": "uvx",
      "args": ["pixelbyte-figma-mcp"],
      "env": {
        "FIGMA_PERSONAL_ACCESS_TOKEN": "your-figma-token"
      }
    }
  }
}
```

**Getting Figma Token:**
1. Figma → Settings → Personal Access Tokens
2. Click "Generate new token"
3. Save token as `FIGMA_PERSONAL_ACCESS_TOKEN`

## Core Principles

1. **Never guess** — Always extract design tokens from MCP
2. **Use semantic HTML** — Prefer correct elements over `<div>` soup
3. **Apply Claude Vision validation** — Visual comparison with TodoWrite tracking
4. **Match exactly** — No creative interpretation, match the design precisely
5. **Leverage Code Connect** — Map Figma components to existing codebase components
6. **Require Auto Layout** — Warn if source design lacks Auto Layout

## Agent Pipeline

This skill orchestrates a 5-agent pipeline for Figma-to-code conversion:

### Pipeline Flow

```
Figma URL
    │
    ▼
┌─────────────────────────┐
│ 1. design-validator     │ → Validation Report
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ 2. design-analyst       │ → Implementation Spec
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ 3. asset-manager        │ → Updated Spec + Assets
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ 4. code-generator       │ → Component Files
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│ 5. compliance-checker   │ → Final Report
└─────────────────────────┘
```

### Invoking the Pipeline

When a Figma URL is provided, invoke agents sequentially:

1. **Start:** Parse Figma URL, create report directory
2. **Agent 1:** Dispatch `design-validator` with URL
3. **Agent 2:** Dispatch `design-analyst` with validation report path
4. **Agent 3:** Dispatch `asset-manager` with spec path
5. **Agent 4:** Dispatch `code-generator` with updated spec path
6. **Agent 5:** Dispatch `compliance-checker` with spec and code paths
7. **Complete:** Present Final Report to user

### Report Directory

All reports saved to: `docs/figma-reports/`

```
docs/figma-reports/
├── {file_key}-validation.md   # Agent 1 output
├── {file_key}-spec.md         # Agent 2+3 output
└── {file_key}-final.md        # Agent 5 output
```

### Manual Override

Users can run individual agents:
- "Just validate this design" → Run only design-validator
- "Generate code from this spec" → Run only code-generator
- "Check compliance" → Run only compliance-checker

## Source Design Requirements

**Auto Layout is REQUIRED.** Designs without Auto Layout cannot be converted to proper HTML structure.

Design check:
- ✅ Auto Layout used → Proceed
- ❌ Absolute positioning → Warn user, request Auto Layout

```
WARNING: This design does not use Auto Layout.
Request the designer to restructure with Auto Layout
for pixel-perfect conversion.
```

## Pixelbyte Figma MCP Tools

### Primary Tools

**figma_get_file_structure** — Get file/node hierarchy
```
Parameters:
  - file_key: Figma file key (from URL)
  - depth: 1-10 (default: 2)
  - response_format: "markdown" | "json"
Returns: File structure with node IDs
```

**figma_get_node_details** — Get detailed node info
```
Parameters:
  - file_key: Figma file key
  - node_id: Node ID (e.g., "1:2")
  - response_format: "markdown" | "json"
Returns: Styles, fills, strokes, effects, layout properties
```

**figma_generate_code** — Generate code from node
```
Parameters:
  - file_key: Figma file key
  - node_id: Node ID to convert
  - framework: "react_tailwind" | "react" | "vue" | "html_css" | etc.
  - component_name: Optional custom name
Returns: Production-ready code
```

**figma_get_design_tokens** — Extract design tokens
```
Parameters:
  - file_key: Figma file key
  - node_id: Optional (specific node)
  - include_colors: true | false
  - include_typography: true | false
  - include_spacing: true | false
  - include_effects: true | false
Returns: Design tokens (colors, typography, spacing, effects)
```

**figma_get_screenshot** — Capture visual reference
```
Parameters:
  - file_key: Figma file key
  - node_ids: Array of node IDs ["1:2", "3:4"]
  - format: "png" | "svg" | "jpg" | "pdf"
  - scale: 0.01 - 4.0 (default: 2)
Returns: Image URLs (valid for 30 days)
```

### Specialized Token Tools

**figma_get_colors** — Extract color palette
```
Parameters:
  - file_key: Figma file key
  - node_id: Optional
  - include_fills: true | false
  - include_strokes: true | false
  - include_shadows: true | false
Returns: Colors in hex and rgba format
```

**figma_get_typography** — Extract typography styles
```
Parameters:
  - file_key: Figma file key
  - node_id: Optional
Returns: Font family, size, weight, line-height
```

**figma_get_spacing** — Extract spacing values
```
Parameters:
  - file_key: Figma file key
  - node_id: Optional
Returns: Padding, gap values from auto-layout frames
```

### Code Connect Tools

**figma_get_code_connect_map** — Get component mappings
```
Parameters:
  - file_key: Figma file key
  - node_id: Optional (specific mapping)
Returns: Component path, name, props mapping, variants
```

**figma_add_code_connect_map** — Add component mapping
```
Parameters:
  - file_key: Figma file key
  - node_id: Figma node ID to map
  - component_path: Code path (e.g., "src/components/Button.tsx")
  - component_name: Component name (e.g., "Button")
  - props_mapping: { "Variant": "variant", "Size": "size" }
  - variants: { "primary": { "variant": "primary" } }
  - example: Usage code snippet
Returns: Success status
```

**figma_remove_code_connect_map** — Remove mapping
```
Parameters:
  - file_key: Figma file key
  - node_id: Node ID to remove
Returns: Success status
```

## Figma URL Parsing

**Extracting file_key and node_id from URL:**

```
URL: figma.com/design/ABC123xyz/MyDesign?node-id=456-789

file_key: ABC123xyz (the part between design/ and / or ?)
node_id: 456:789 (convert hyphen "-" to colon ":")

⚠️ COMMON ERROR: URL format "456-789" must be used as "456:789"!
```

**Parsing example:**
```
URL: https://www.figma.com/design/xHgE5Ab7cD9fG1hI/ProjectName?node-id=123-456&t=abc

file_key: xHgE5Ab7cD9fG1hI
node_id: 123:456
```

## 5-Phase Workflow

### Phase 1: Context Acquisition

Upon receiving a Figma URL:

**Step 1: Parse URL and Get Structure**

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Extract file_key and node_id from URL                       │
│     → Convert hyphen "-" to colon ":"                           │
├─────────────────────────────────────────────────────────────────┤
│  2. figma_get_file_structure                                    │
│     → Get file structure                                        │
│     → Learn node IDs                                            │
│     → Depth: 2-3 is sufficient                                  │
├─────────────────────────────────────────────────────────────────┤
│  3. figma_get_node_details                                      │
│     → Get target node details                                   │
│     → Styles, fills, layout properties                          │
├─────────────────────────────────────────────────────────────────┤
│  4. figma_get_design_tokens                                     │
│     → Color tokens                                              │
│     → Typography tokens                                         │
│     → Spacing tokens                                            │
├─────────────────────────────────────────────────────────────────┤
│  5. figma_generate_code                                         │
│     → framework: "react_tailwind"                               │
│     → Initial code                                              │
├─────────────────────────────────────────────────────────────────┤
│  6. figma_get_code_connect_map                                  │
│     → Existing component mappings                               │
├─────────────────────────────────────────────────────────────────┤
│  7. figma_get_screenshot                                        │
│     → Visual reference (for Phase 4 validation)                 │
│     → scale: 2 recommended                                      │
└─────────────────────────────────────────────────────────────────┘
```

**Step 2: Codebase Analysis**

```
8. Read existing component files
   → Read paths from figma_get_code_connect_map
   → Analyze existing component patterns

9. Analyze project environment:
   - tailwind.config.js → Existing theme/tokens
   - src/shared/components/ui/ → shadcn/ui components
   - src/features/*/components/ → Feature components
   - package.json → Libraries in use
```

**Analysis output:**
- Component structure from design
- Complete design tokens (colors, spacing, typography)
- Existing component mappings and their source code
- Layout info from generated code
- Screenshot for validation baseline

**Step 3: Code Connect Check**

Before generating new components, check for existing Code Connect mappings:

**Reference:** `references/code-connect-guide.md`

```javascript
mcp__pixelbyte-figma-mcp__figma_get_code_connect_map({
  params: { file_key: "FILE_KEY" }
})
```

**If mappings exist:**
- Document which Figma components are already mapped
- Note the component paths and prop mappings
- Flag these nodes as "use existing code" - do NOT regenerate
- Extract only unmapped nodes for code generation

**If no mappings exist:**
- Proceed with full code generation for all nodes
- After successful generation, offer to create Code Connect mappings
- Use `figma_add_code_connect_map` to establish future mappings

**Decision matrix:**

| Scenario | Action |
|----------|--------|
| Node has Code Connect mapping | Import existing component |
| Node has partial mapping (missing variants) | Extend existing component |
| Node has no mapping | Generate new component |
| Multiple nodes share same mapping | Reuse single component |

**Example output:**
```markdown
## Code Connect Analysis

### Mapped Components (skip generation)
- Button (node 123:456) → src/components/ui/button.tsx
- Badge (node 789:012) → src/components/ui/badge.tsx

### Unmapped Components (generate)
- HeroCard (node 345:678) → NEW
- PricingTable (node 901:234) → NEW
```

### Phase 2: Mapping & Planning

**Before writing code, create a plan:**

1. **Check Code Connect mappings:**
   - Use `figma_get_code_connect_map` data from Phase 1
   - Match Figma nodes to codebase components
   - If mapping exists → Use existing component
   - If no mapping → Plan new component creation

2. **Layout strategy:**
   - Analyze generated Tailwind classes from `figma_generate_code`
   - Plan responsive behavior adjustments

3. **Token mapping:**
   - Use `figma_get_design_tokens` data from Phase 1
   - Missing token → Mark with TODO comment

4. **Responsive planning:**
   - Width >1024px → Assume desktop view
   - Plan mobile-first overrides

**Mapping output:**
```json
{
  "codeConnectComponents": ["Button", "Input"],
  "newComponents": ["HeroCard"],
  "tokenMappings": {
    "colors/primary": "bg-primary",
    "spacing/lg": "p-6"
  },
  "layoutStrategy": "flex-col md:flex-row"
}
```

### Phase 3: Code Generation

**Start with `figma_generate_code` output, then refine:**

1. **Typography refinement** (if needed):
   ```
   font-size:      Figma px ÷ 16 = rem
   line-height:    Figma % ÷ 100 = value
   letter-spacing: Figma tracking ÷ 1000 = em
   ```

2. **Layout verification** (Auto Layout → Flexbox):

   | Figma | Tailwind |
   |-------|----------|
   | Direction: Horizontal | `flex-row` |
   | Direction: Vertical | `flex-col` |
   | Gap: 16px | `gap-4` |
   | Primary: Space Between | `justify-between` |
   | Counter: Center | `items-center` |
   | Fill Container | `flex-1` |
   | Hug Contents | `w-fit` |

3. **Design token integration:**
   - Use values from `figma_get_design_tokens`
   - Map to CSS variables or Tailwind theme

4. **Semantic HTML enforcement:**
   - Clickable → `<button>` or `<a>`
   - List → `<ul>/<ol>` + `<li>`
   - Navigation → `<nav>`
   - Form → `<form>` + `<input>/<select>`
   - Heading → `<h1>`-`<h6>` (hierarchical)

5. **Responsive breakpoints:**
   - Mobile-first approach: base → `sm:` → `md:` → `lg:`
   - Single size in design: Add reasonable responsive behavior

### Phase 4: Visual Validation (Claude Vision)

**Simple Approach:** Figma screenshot + Browser screenshot → Claude Vision comparison → TodoWrite difference list

⚠️ **Phase 4 is MANDATORY** - Must be completed before proceeding to Phase 5.

**5-STEP WORKFLOW:**

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Take Figma Screenshot                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Use Pixelbyte Figma MCP:                                  │  │
│  │                                                            │  │
│  │ mcp__pixelbyte-figma-mcp__figma_get_screenshot({          │  │
│  │   params: {                                                │  │
│  │     file_key: "ABC123xyz",  // Extract from URL           │  │
│  │     node_ids: ["456:789"],  // Convert hyphen to colon    │  │
│  │     format: "png",                                         │  │
│  │     scale: 2                                               │  │
│  │   }                                                        │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ → Download returned URL with WebFetch or view with Read   │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  STEP 2: Take Browser Screenshot (ELEMENT-SPECIFIC)            │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Use Claude in Chrome MCP:                                  │  │
│  │                                                            │  │
│  │ 1. Get tab context (ALWAYS FIRST STEP):                   │  │
│  │ mcp__claude-in-chrome__tabs_context_mcp({                 │  │
│  │   createIfEmpty: true                                      │  │
│  │ })                                                         │  │
│  │ → Use returned tabId for subsequent operations            │  │
│  │                                                            │  │
│  │ 2. Navigate to dev server:                                 │  │
│  │ mcp__claude-in-chrome__navigate({                          │  │
│  │   url: "http://localhost:3000/[component-path]",          │  │
│  │   tabId: <returned-tab-id>                                │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ 3. Wait for page to load:                                  │  │
│  │ mcp__claude-in-chrome__computer({                          │  │
│  │   action: "wait",                                          │  │
│  │   duration: 2,                                             │  │
│  │   tabId: <tab-id>                                         │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ 4. Get accessibility tree (to find element ref):          │  │
│  │ mcp__claude-in-chrome__read_page({                         │  │
│  │   tabId: <tab-id>                                         │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ Read page output example:                                  │  │
│  │ - main                                                     │  │
│  │   - div "container"                                        │  │
│  │     - article ref="ref_1" [data-testid="hero"]            │  │
│  │       - h2 "Title"                                         │  │
│  │       - p "Description"                                    │  │
│  │                                                            │  │
│  │ → Use ref="ref_1" (claude-in-chrome format)               │  │
│  │                                                            │  │
│  │ 5. Take full page SCREENSHOT:                              │  │
│  │ mcp__claude-in-chrome__computer({                          │  │
│  │   action: "screenshot",                                    │  │
│  │   tabId: <tab-id>                                         │  │
│  │ })                                                         │  │
│  │ → Returned imageId can be used to zoom to element         │  │
│  │                                                            │  │
│  │ 6. (Optional) ZOOM to element:                             │  │
│  │ mcp__claude-in-chrome__computer({                          │  │
│  │   action: "zoom",                                          │  │
│  │   region: [x0, y0, x1, y1],  // Element coordinates       │  │
│  │   tabId: <tab-id>                                         │  │
│  │ })                                                         │  │
│  │                                                            │  │
│  │ ⚠️ IMPORTANT: Target same element as Figma frame          │  │
│  │ → Use scroll_to to make element visible                   │  │
│  │ → Use zoom to focus on specific region                    │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  STEP 3: Compare with Claude Vision                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Compare both images side by side and detect differences   │  │
│  │ in these categories:                                       │  │
│  │                                                            │  │
│  │ 📝 TYPOGRAPHY                                              │  │
│  │    - Font family, size, weight                            │  │
│  │    - Line height, letter spacing                          │  │
│  │    - Text color                                            │  │
│  │                                                            │  │
│  │ 📐 SPACING                                                 │  │
│  │    - Padding (top, right, bottom, left)                   │  │
│  │    - Margin                                                │  │
│  │    - Gap between elements                                  │  │
│  │                                                            │  │
│  │ 🎨 COLORS                                                  │  │
│  │    - Background colors                                     │  │
│  │    - Border colors                                         │  │
│  │    - Text colors                                           │  │
│  │                                                            │  │
│  │ 📦 LAYOUT                                                  │  │
│  │    - Element alignment                                     │  │
│  │    - Flex direction                                        │  │
│  │    - Width/height                                          │  │
│  │                                                            │  │
│  │ 🖼️ ASSETS                                                  │  │
│  │    - Icons (size, color)                                   │  │
│  │    - Images (aspect ratio)                                 │  │
│  │    - Border radius                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  STEP 4: Create Difference List with TodoWrite                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Create a todo item for each difference:                   │  │
│  │                                                            │  │
│  │ Example format:                                            │  │
│  │ - "Title font-size: text-2xl → text-3xl"                  │  │
│  │ - "Card padding: p-4 → p-6"                               │  │
│  │ - "Button background: bg-blue-500 → bg-primary"           │  │
│  │ - "Gap between items: gap-2 → gap-4"                      │  │
│  │                                                            │  │
│  │ TodoWrite({                                                │  │
│  │   todos: [                                                 │  │
│  │     { content: "Fix title font-size", status: "pending" },│  │
│  │     { content: "Fix card padding", status: "pending" },   │  │
│  │     ...                                                    │  │
│  │   ]                                                        │  │
│  │ })                                                         │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  STEP 5: Fix and Re-check                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 1. Complete todos in order                                │  │
│  │ 2. Mark todo as "completed" after each fix                │  │
│  │ 3. When all todos are complete:                           │  │
│  │    - Take new browser screenshot                          │  │
│  │    - Re-check with Claude Vision                          │  │
│  │    - Add new todo if new differences found                │  │
│  │ 4. Proceed to Phase 5 when no differences remain          │  │
│  │                                                            │  │
│  │ ⚠️ Max 3 iterations - notify user afterwards              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Example Claude Vision Analysis Output:**

```markdown
## 🔍 Figma vs Implementation Comparison

### Typography Differences
| Element | Figma | Implementation | Fix |
|---------|-------|----------------|-----|
| Title | 32px bold | 28px medium | `text-3xl font-bold` |
| Subtitle | 16px gray-500 | 14px gray-400 | `text-base text-gray-500` |

### Spacing Differences
| Element | Figma | Implementation | Fix |
|---------|-------|----------------|-----|
| Card padding | 24px | 16px | `p-6` |
| Button gap | 12px | 8px | `gap-3` |

### Color Differences
| Element | Figma | Implementation | Fix |
|---------|-------|----------------|-----|
| Primary button | #FE4601 | #3B82F6 | `bg-orange-1` |

### Summary
✅ Layout: Correct
⚠️ Typography: 2 differences
⚠️ Spacing: 2 differences
❌ Colors: 1 difference
```

**Detailed instructions:** See `references/visual-validation-loop.md`

### Phase 5: Handoff

⚠️ **VALIDATION GATE:**
```
┌─────────────────────────────────────────────────────────────────┐
│  BEFORE PROCEEDING TO PHASE 5:                                  │
├─────────────────────────────────────────────────────────────────┤
│  Is Phase 4 complete?                                           │
│  ├── ✅ YES → Continue                                          │
│  └── ❌ NO → STOP! Return to Phase 4                            │
│                                                                  │
│  Are all todos complete?                                        │
│  ├── ✅ YES → Proceed to Phase 5                                │
│  └── ❌ NO → Complete remaining todos                           │
│                                                                  │
│  Was final Claude Vision check performed?                       │
│  ├── ✅ No differences → Continue                               │
│  └── ⚠️ Minor differences → Add "manual review recommended" note│
└─────────────────────────────────────────────────────────────────┘
```

**Final output format:**

```markdown
## ✅ Conversion Complete

**Component:** HeroCard.tsx
**Validation:** Verified by Claude Vision
**Iterations:** 2
**Status:** No critical differences

### Code Connect Components Used:
- Button (mapped via Code Connect)
- Badge (mapped via Code Connect)

### New Components Created:
- HeroCard.tsx

### Design Tokens Applied:
- colors/primary → var(--color-primary)
- spacing/lg → var(--spacing-lg)

### Assumptions Made:
- Font family assumed 'Inter'
- Hover state not in design, added standard opacity

### Manual Check Required:
- [ ] Icon asset not found, placeholder used
- [ ] `colors/accent` token unmatched → `// TODO: Check color`

### Files:
- src/components/HeroCard.tsx (new)
- src/components/HeroCard.stories.tsx (optional)
```

### 5.3 Test Generation

Generate tests for each component created in Phase 3:

**Reference:** `references/test-generation.md`

**Steps:**

1. **Analyze Component**
   - Read component file
   - Extract props interface
   - Identify variants, handlers, states

2. **Generate Unit Test**
   - Create `{ComponentName}.test.tsx`
   - Include rendering tests
   - Include props/variant tests
   - Include accessibility test (jest-axe)
   - Include interaction tests

3. **Generate Visual Test (Optional)**
   - Create `{ComponentName}.visual.spec.ts`
   - Include default state screenshot
   - Include mobile viewport screenshot
   - Include hover state screenshot

4. **Run Tests**
   ```bash
   npm run test -- {ComponentName}
   ```

5. **Add to Handoff Checklist**
   - [ ] Unit tests passing
   - [ ] Accessibility tests passing
   - [ ] Visual tests passing (if applicable)
   - [ ] Coverage meets minimum (80%)

### Phase 5 Handoff Checklist

Before finalizing the handoff, ensure all items are complete:

- [ ] All components generated
- [ ] Design tokens applied
- [ ] Assets downloaded and imported
- [ ] Compliance check passed
- [ ] **Unit tests generated and passing**
- [ ] **Accessibility tests passing**
- [ ] **Visual tests passing (if Playwright available)**
- [ ] Code committed
- [ ] Documentation updated

## Output Format

**React/TypeScript component template:**

```tsx
import React from 'react';

interface ComponentNameProps {
  // Props from Figma variants
}

export const ComponentName: React.FC<ComponentNameProps> = ({ ...props }) => {
  return (
    <div className="[Tailwind classes from design context]">
      {/* Semantic HTML structure */}
    </div>
  );
};
```

**Requirements:**
- TypeScript with typed props
- Tailwind CSS (use design tokens when available)
- Semantic HTML elements
- Accessibility: `aria-*`, `role`, `alt` attributes

## WCAG 2.1 AA Accessibility

| Criterion | Requirement | Tailwind Example |
|-----------|-------------|------------------|
| Color contrast | 4.5:1 (normal), 3:1 (large) | `text-gray-900` on `bg-white` |
| Focus indicator | Visible focus ring | `focus:ring-2 focus:ring-blue-500` |
| Touch target | Min 44x44px | `min-h-[44px] min-w-[44px]` |
| Alt text | All meaningful images | `<img alt="Description">` |
| Keyboard nav | Tab accessible | `tabindex="0"` (if needed) |

## Common Issues

Quick reference for common problems:

| Issue | Symptom | Solution |
|-------|---------|----------|
| Content overflow | Text overflows on mobile | Never use `w-[Xpx]` for text elements, use `w-full` or `max-w-` |
| Icon alignment | Vertical shift | Default to `flex items-center` |
| Color mismatch | Brand color different | Check `figma_get_design_tokens` output, use design tokens |
| Complex DOM | Unnecessary div layers | Apply flattening algorithm |
| Font weight | Font appears thin/bold | Verify against design tokens |
| Responsive break | Layout breaks on mobile | Write mobile-first, use `md:` for desktop override |

**Detailed solutions:** See `references/common-issues.md`

## DOM Flattening Rules

Skip unnecessary layers:
```
❌ SKIP:
- Frames used only for grouping (no bg/border/padding)
- Wrapper containers with single child
- Groups with no visual effect
- Default-named empty wrappers ("Frame 1", "Group 2")

✅ CONVERT TO DIV:
- Has background color
- Has border or shadow
- Has padding/margin
- Has border-radius
```

## TODO Comment Strategy

For missing or ambiguous values:
```tsx
// TODO: Check color - Design token 'colors/accent' not in theme
const accentColor = "text-blue-500"; // Temporary value

// TODO: Check font - 'Custom Font' not installed
const fontFamily = "font-sans"; // Fallback

// TODO: Check icon - Asset not found
<PlaceholderIcon className="w-6 h-6" />
```

## References

### Core References
- **Pixelbyte MCP details**: `references/figma-mcp-server.md`
- **Token conversion formulas**: `references/token-mapping.md`
- **Validation guide**: `references/validation-guide.md`
- **Visual validation loop**: `references/visual-validation-loop.md`
- **Common issues**: `references/common-issues.md`
- **Preview route setup**: `references/preview-setup.md`
- **Test generation guide**: `references/test-generation.md`
- **Code Connect guide**: `references/code-connect-guide.md`
- **Responsive validation**: `references/responsive-validation.md`
- **Accessibility validation**: `references/accessibility-validation.md`
- **Error recovery patterns**: `references/error-recovery.md`

### Prompt Templates
Phase-specific prompts located in `references/prompts/`:
- `analyze-design.md` — Phase 1 analysis
- `mapping-planning.md` — Phase 2 planning
- `generate-component.md` — Phase 3 generation
- `validate-refine.md` — Phase 4 validation
- `handoff.md` — Phase 5 handoff

### Templates
- **React component template**: `assets/templates/component.tsx.hbs`

## Critical Rules

- Always use `figma_generate_code` as starting point for code generation
- Check `figma_get_code_connect_map` before creating new components
- Extract design tokens with `figma_get_design_tokens`
- Use `figma_get_screenshot` for validation baseline
- Run visual validation, check differences
- Clearly document TODO comments
