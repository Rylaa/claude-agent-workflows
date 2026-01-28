# pb-figma Plugin Cleanup & Audit Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Clean up 13 identified issues in pb-figma plugin - remove dead code, fix invalid references, consolidate duplicates, and ensure consistency across all agents.

**Architecture:** Sequential cleanup approach - fix CRITICAL issues first, then HIGH priority, then MEDIUM. Each task is atomic and independently committable. Duplicate content will be extracted to shared reference files.

**Tech Stack:** Markdown documentation, MCP tool references, agent configuration YAML frontmatter.

---

## Task Overview

| Priority | Tasks | Description |
|----------|-------|-------------|
| CRITICAL | 1 | Fix invalid `figma_find_children` tool reference |
| HIGH | 2-4 | Remove placeholder agents, clean unused prompts, fix handoff reference |
| MEDIUM | 5-10 | Fix path inconsistency, extract duplicates, clarify workflows |
| CLEANUP | 11 | Version bump and CHANGELOG |

---

## Task 1: Fix Invalid `figma_find_children` Tool Reference

**Files:**
- Modify: `plugins/pb-figma/agents/asset-manager.md:130-160`

**Problem:** `figma_find_children` tool is referenced but doesn't exist in Pixelbyte Figma MCP Server.

**Step 1: Read current asset-manager.md classification section**

```bash
Read("plugins/pb-figma/agents/asset-manager.md", offset=125, limit=50)
```

**Step 2: Replace with valid MCP approach**

Replace the `figma_find_children` call with `figma_get_node_details` approach:

```markdown
### 2.1 Asset Type Classification Algorithm

**Use `figma_get_node_details` to analyze node structure:**

```typescript
const nodeDetails = figma_get_node_details({
  file_key: "{file_key}",
  node_id: "{asset_node_id}",
  response_format: "json"
});

// Count children from response
const childrenCount = nodeDetails.children?.length ?? 0;
const hasVectorChildren = nodeDetails.children?.some(c => c.type === "VECTOR") ?? false;

// Classification based on structure
if (childrenCount >= 15 || hasVectorChildren && childrenCount >= 5) {
  return "COMPLEX_VECTOR";  // Download as PNG
} else if (nodeDetails.type === "VECTOR" || hasVectorChildren) {
  return "SIMPLE_ICON";     // Download as SVG
} else {
  return "RASTER_IMAGE";    // Download as PNG
}
```

**Note:** This replaces the non-existent `figma_find_children` with the valid `figma_get_node_details` tool.
```

**Step 3: Commit**

```bash
git add plugins/pb-figma/agents/asset-manager.md
git commit -m "fix(asset-manager): replace invalid figma_find_children with figma_get_node_details

The figma_find_children tool does not exist in Pixelbyte Figma MCP.
Rewritten classification to use figma_get_node_details which is valid.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Remove Placeholder Agents from Pipeline Docs

**Files:**
- Modify: `plugins/pb-figma/SKILL.md` (remove Vue/Kotlin references)
- Modify: `plugins/pb-figma/docs-index.md` (mark as placeholder)

**Problem:** `code-generator-vue.md` and `code-generator-kotlin.md` are placeholders ("COMING IN v1.2.0") but referenced in pipeline documentation as if functional.

**Step 1: Read SKILL.md to find Vue/Kotlin references**

```bash
Grep("vue|kotlin", path="plugins/pb-figma/SKILL.md", "-i": true)
```

**Step 2: Update SKILL.md - Framework Detection section**

Find framework detection table and update to only list implemented frameworks:

```markdown
## Supported Frameworks

| Framework | Agent | Status |
|-----------|-------|--------|
| React + Tailwind | code-generator-react | ✅ Available |
| SwiftUI (iOS/macOS) | code-generator-swiftui | ✅ Available |
| Vue 3 | code-generator-vue | 🚧 Coming Soon |
| Kotlin Compose | code-generator-kotlin | 🚧 Coming Soon |

**Note:** Vue and Kotlin generators are planned for future releases. Currently, use React or SwiftUI generators.
```

**Step 3: Update docs-index.md - Agents section**

Add status column to agents table:

```markdown
## Agents

| Agent | Description | Status |
|-------|-------------|--------|
| design-validator | Validates Figma designs | ✅ Active |
| design-analyst | Creates Implementation Specs | ✅ Active |
| asset-manager | Downloads and organizes assets | ✅ Active |
| code-generator-react | React + Tailwind code generation | ✅ Active |
| code-generator-swiftui | SwiftUI code generation | ✅ Active |
| code-generator-vue | Vue 3 code generation | 🚧 Placeholder |
| code-generator-kotlin | Kotlin Compose code generation | 🚧 Placeholder |
| compliance-checker | Validates generated code | ✅ Active |
```

**Step 4: Commit**

```bash
git add plugins/pb-figma/SKILL.md plugins/pb-figma/docs-index.md
git commit -m "docs(pb-figma): mark Vue/Kotlin generators as placeholder status

These agents show 'COMING IN v1.2.0' but were listed as functional.
Updated documentation to clearly show their placeholder status.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Clean Up Unused Prompt Templates

**Files:**
- Modify: `plugins/pb-figma/docs-index.md` (remove unused prompt references)

**Problem:** 4 prompt templates listed as "used by" agents but never actually referenced:
- `analyze-design.md`
- `generate-component.md`
- `validate-refine.md`
- `handoff.md`

**Step 1: Read docs-index.md Prompt Templates section**

```bash
Grep("Prompt Templates", path="plugins/pb-figma/docs-index.md", "-A": 20)
```

**Step 2: Update Prompt Templates section**

Replace with accurate listing or remove entirely:

```markdown
## Prompt Templates

> **Note:** The following prompt templates were designed for earlier versions but are not currently used by any agent. They are preserved for reference.

| Template | Original Purpose | Status |
|----------|-----------------|--------|
| analyze-design.md | Design analysis prompts | ⚠️ Unused |
| generate-component.md | Component generation prompts | ⚠️ Unused |
| validate-refine.md | Validation prompts | ⚠️ Unused |
| handoff.md | Handoff documentation | ⚠️ Unused |

**Active agents load references directly** - see "Reference Files" section below.
```

**Step 3: Commit**

```bash
git add plugins/pb-figma/docs-index.md
git commit -m "docs(pb-figma): mark unused prompt templates as inactive

These prompts are listed but never loaded by any agent.
Preserved for reference but clearly marked as unused.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Fix Non-Existent "handoff" Agent Reference

**Files:**
- Modify: `plugins/pb-figma/docs-index.md`

**Problem:** `ci-cd-integration.md` reference claims to be "used by: handoff" but no handoff agent exists.

**Step 1: Find the ci-cd-integration reference**

```bash
Grep("ci-cd-integration|handoff", path="plugins/pb-figma/docs-index.md")
```

**Step 2: Update the reference**

Change "used by" to indicate it's not currently integrated:

```markdown
| CI/CD Integration | @skills/figma-to-code/references/ci-cd-integration.md | ⚠️ Not integrated (no agent uses this) |
```

**Step 3: Commit**

```bash
git add plugins/pb-figma/docs-index.md
git commit -m "docs(pb-figma): fix ci-cd-integration reference to non-existent handoff agent

The 'handoff' agent does not exist. Updated reference to show
this file is not currently integrated with any agent.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Fix Reference Path Inconsistency

**Files:**
- Modify: `plugins/pb-figma/agents/code-generator-base.md:250-252`

**Problem:** Uses `@references/` path format instead of `@skills/figma-to-code/references/`.

**Step 1: Find inconsistent paths**

```bash
Grep("@references/", path="plugins/pb-figma/agents/code-generator-base.md")
```

**Step 2: Replace with correct path format**

Change:
```markdown
- **Token conversion issues?** → Read @references/token-mapping.md
- **Layout problems?** → Read @references/common-issues.md
- **Error during generation?** → Read @references/error-recovery.md
```

To:
```markdown
- **Token conversion issues?** → Read @skills/figma-to-code/references/token-mapping.md
- **Layout problems?** → Read @skills/figma-to-code/references/common-issues.md
- **Error during generation?** → Read @skills/figma-to-code/references/error-recovery.md
```

**Step 3: Commit**

```bash
git add plugins/pb-figma/agents/code-generator-base.md
git commit -m "fix(code-generator-base): use correct reference path format

Changed @references/ to @skills/figma-to-code/references/
for consistency with all other agents.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Extract Duplicate Opacity Documentation

**Files:**
- Create: `plugins/pb-figma/skills/figma-to-code/references/opacity-extraction.md`
- Modify: `plugins/pb-figma/agents/design-analyst.md` (replace with reference)
- Modify: `plugins/pb-figma/agents/code-generator-swiftui.md` (replace with reference)

**Problem:** ~200 lines of identical opacity handling documentation in 2 files.

**Step 1: Create shared opacity-extraction.md reference**

```markdown
# Opacity Extraction Reference

## Compound Opacity Calculation

Figma stores opacity at multiple levels. Calculate effective opacity:

```typescript
effectiveOpacity = fillOpacity * nodeOpacity
```

**Example:**
- Fill opacity: 0.8
- Node opacity: 0.5
- Effective: 0.8 * 0.5 = 0.4

## Opacity Sources

| Source | Figma Property | Priority |
|--------|---------------|----------|
| Fill | `fills[0].opacity` | Primary |
| Node | `opacity` | Multiplier |
| Effect | `effects[].opacity` | Additive |

## Warning Conditions

Flag for review when:
- `effectiveOpacity < 0.1` → Nearly invisible
- `effectiveOpacity !== 1.0 AND effectiveOpacity !== 0.0` → Partial transparency
- Multiple opacity sources combined

## SwiftUI Application

```swift
// Color-level opacity (for fills, strokes)
Color(hex: "#FFFFFF").opacity(0.4)

// View-level opacity (for gradients, overlays)
LinearGradient(...)
    .opacity(0.2)
```
```

**Step 2: Update design-analyst.md - replace duplicate section**

Replace the ~100 line opacity section with:

```markdown
### Opacity Handling

See: @skills/figma-to-code/references/opacity-extraction.md

**Key rule:** Always calculate `effectiveOpacity = fillOpacity * nodeOpacity`
```

**Step 3: Update code-generator-swiftui.md - replace duplicate section**

Replace the opacity application section with:

```markdown
##### Apply Opacity from Spec

See: @skills/figma-to-code/references/opacity-extraction.md for calculation details.

**Copy Usage column from Design Tokens table** - it contains the complete SwiftUI modifier chain.
```

**Step 4: Commit**

```bash
git add plugins/pb-figma/skills/figma-to-code/references/opacity-extraction.md
git add plugins/pb-figma/agents/design-analyst.md
git add plugins/pb-figma/agents/code-generator-swiftui.md
git commit -m "refactor(pb-figma): extract duplicate opacity documentation to shared reference

Moved ~200 lines of duplicated opacity handling to single source of truth.
Both design-analyst and code-generator-swiftui now reference it.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Extract Duplicate Layer Order Documentation

**Files:**
- Create: `plugins/pb-figma/skills/figma-to-code/references/layer-order-hierarchy.md`
- Modify: `plugins/pb-figma/agents/design-analyst.md`
- Modify: `plugins/pb-figma/agents/code-generator-react.md`
- Modify: `plugins/pb-figma/agents/compliance-checker.md`

**Problem:** Same layer order algorithm explained 3 times.

**Step 1: Create shared layer-order-hierarchy.md reference**

```markdown
# Layer Order & Hierarchy Reference

## Core Principle

**Layer order = children array order, NOT Y coordinate.**

Figma's children array is already sorted by visual stacking order:
- First child = bottom layer (rendered first)
- Last child = top layer (rendered last, visually on top)

## Why NOT Y Coordinate?

Y coordinate determines vertical position, not layer order:
- A button at Y=100 could be ABOVE an image at Y=50
- Only the children array order determines visual stacking

## Framework-Specific Rendering

| Framework | Order Rule | Example |
|-----------|------------|---------|
| React/HTML | First element = bottom | `<Background /><Foreground />` |
| SwiftUI ZStack | Last element = top | Same as React |
| CSS z-index | Higher = top | Explicit override |

## Extracting Layer Order

```typescript
// From Figma node children array
const layerOrder = node.children.map((child, index) => ({
  name: child.name,
  zIndex: (index + 1) * 100,  // 100, 200, 300...
  position: getPositionContext(child)  // top/center/bottom
}));
```

## Spec Output Format

```yaml
layerOrder:
  - layer: Background (zIndex: 100)
  - layer: ContentCard (zIndex: 200)
  - layer: FloatingButton (zIndex: 300)
```
```

**Step 2: Update all 3 agents to reference shared file**

In each agent, replace the layer order section with:

```markdown
### Layer Order

See: @skills/figma-to-code/references/layer-order-hierarchy.md

**Key rule:** Use children array order, not Y coordinate.
```

**Step 3: Commit**

```bash
git add plugins/pb-figma/skills/figma-to-code/references/layer-order-hierarchy.md
git add plugins/pb-figma/agents/design-analyst.md
git add plugins/pb-figma/agents/code-generator-react.md
git add plugins/pb-figma/agents/compliance-checker.md
git commit -m "refactor(pb-figma): extract duplicate layer order documentation to shared reference

Layer order algorithm was explained 3 times identically.
Now single source of truth referenced by all agents.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Extract Duplicate Asset Classification Documentation

**Files:**
- Create: `plugins/pb-figma/skills/figma-to-code/references/asset-classification-guide.md`
- Modify: `plugins/pb-figma/agents/design-validator.md`
- Modify: `plugins/pb-figma/agents/design-analyst.md`
- Modify: `plugins/pb-figma/agents/asset-manager.md`

**Problem:** Card icon validation and asset classification rules repeated across 3 agents.

**Step 1: Create shared asset-classification-guide.md**

```markdown
# Asset Classification Guide

## Icon Position Classification

| Position in HStack | Type | Usage |
|--------------------|------|-------|
| Leading (first child) | Thematic Icon | Represents card's purpose |
| Trailing (last child) | Status Indicator | Shows state (checkmark, arrow) |

## Asset Type Classification

| Type | Criteria | Download Format |
|------|----------|-----------------|
| SIMPLE_ICON | Single vector, < 64px | SVG |
| COMPLEX_VECTOR | ≥15 descendants OR ≥5 colors | PNG |
| RASTER_IMAGE | Image fill or photo | PNG (original) |
| CHART_ILLUSTRATION | Has exportSettings | PNG |

## Asset Children Format

```
IMAGE:{asset-name}:{NodeID}:{width}:{height}
```

Example: `IMAGE:icon-clock:3:230:32:32`

## Template Compatibility

| SVG Fill | Template Compatible | SwiftUI Rendering |
|----------|--------------------|--------------------|
| Hardcoded color (#F2F20D) | No | `.renderingMode(.original)` |
| None or currentColor | Yes | `.renderingMode(.template)` |
```

**Step 2: Update all 3 agents to reference shared file**

**Step 3: Commit**

```bash
git add plugins/pb-figma/skills/figma-to-code/references/asset-classification-guide.md
git add plugins/pb-figma/agents/design-validator.md
git add plugins/pb-figma/agents/design-analyst.md
git add plugins/pb-figma/agents/asset-manager.md
git commit -m "refactor(pb-figma): extract duplicate asset classification to shared reference

Asset classification rules were repeated in 3 agents.
Now single source of truth for consistency.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Clarify Flagged Frames Workflow

**Files:**
- Modify: `plugins/pb-figma/agents/design-analyst.md` (add clarification)
- Modify: `plugins/pb-figma/agents/asset-manager.md` (add clarification)

**Problem:** Unclear who makes final decision on flagged frames.

**Step 1: Add workflow clarification to design-analyst.md**

Add at the top of Flagged Frames section:

```markdown
### Flagged Frames Handling

**Workflow clarification:**
1. **Design Validator** → Flags complex frames based on heuristics
2. **Design Analyst** → Copies flags verbatim to spec (NO decision made here)
3. **Asset Manager** → Makes final decision using LLM Vision analysis

**This agent (Design Analyst) is a PASS-THROUGH** - do not interpret or modify flags.
```

**Step 2: Add workflow clarification to asset-manager.md**

Add at the top of LLM Vision section:

```markdown
### LLM Vision Analysis for Flagged Frames

**Workflow clarification:**
- Design Validator flagged these frames as potentially complex
- Design Analyst passed them through without interpretation
- **This agent (Asset Manager) makes the FINAL decision**

Use Claude Vision to analyze each flagged frame and decide:
- `DOWNLOAD_AS_IMAGE` → Download as PNG, treat as illustration
- `GENERATE_CODE` → Let code generator handle as normal component
```

**Step 3: Commit**

```bash
git add plugins/pb-figma/agents/design-analyst.md
git add plugins/pb-figma/agents/asset-manager.md
git commit -m "docs(pb-figma): clarify flagged frames workflow across agents

Added explicit documentation showing:
- Design Validator: flags
- Design Analyst: passes through (no decision)
- Asset Manager: makes final decision with LLM Vision

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Fix Tool Declarations Consistency

**Files:**
- Modify: `plugins/pb-figma/agents/design-validator.md` (add Read tool)
- Modify: `plugins/pb-figma/agents/code-generator-react.md` (add Write tool)
- Modify: `plugins/pb-figma/agents/code-generator-swiftui.md` (add Write tool)

**Problem:** Some agents missing tools they logically need.

**Step 1: Add Read tool to design-validator.md frontmatter**

```yaml
tools:
  - Read  # Added - needs to read previous reports
  - Write
  - Glob
  - Grep
  - Bash
  - TodoWrite
  # ... MCP tools
```

**Step 2: Add Write tool to code-generator-react.md frontmatter**

```yaml
tools:
  - Read
  - Write  # Added - needs to write component files
  - Glob
  - Grep
  - Bash
  - TodoWrite
  # ... MCP tools
```

**Step 3: Add Write tool to code-generator-swiftui.md frontmatter**

```yaml
tools:
  - Read
  - Write  # Added - needs to write component files
  - Glob
  - Grep
  - Bash
  - TodoWrite
  # ... MCP tools
```

**Step 4: Commit**

```bash
git add plugins/pb-figma/agents/design-validator.md
git add plugins/pb-figma/agents/code-generator-react.md
git add plugins/pb-figma/agents/code-generator-swiftui.md
git commit -m "fix(pb-figma): add missing tools to agent frontmatter declarations

- design-validator: added Read (needs to read reports)
- code-generator-react: added Write (needs to write files)
- code-generator-swiftui: added Write (needs to write files)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Version Bump and CHANGELOG

**Files:**
- Modify: `plugins/pb-figma/.claude-plugin/plugin.json`
- Modify: `plugins/pb-figma/CHANGELOG.md`

**Step 1: Bump version to 1.10.0**

```json
{
  "version": "1.10.0"
}
```

**Step 2: Add CHANGELOG entry**

```markdown
## [1.10.0] - 2026-01-28

### Fixed
- **Asset Manager** - Replaced invalid `figma_find_children` tool with `figma_get_node_details`
- **Tool Declarations** - Added missing Read/Write tools to agent frontmatter

### Changed
- **Vue/Kotlin Generators** - Marked as placeholder status in documentation
- **Prompt Templates** - Marked unused prompts as inactive
- **CI/CD Reference** - Fixed reference to non-existent "handoff" agent
- **Reference Paths** - Standardized to `@skills/figma-to-code/references/` format

### Added
- **opacity-extraction.md** - Shared reference for opacity handling
- **layer-order-hierarchy.md** - Shared reference for layer order algorithm
- **asset-classification-guide.md** - Shared reference for asset classification
- **Flagged Frames Workflow** - Explicit documentation of decision flow

### Removed
- Duplicate opacity documentation (~200 lines)
- Duplicate layer order documentation (~300 lines)
- Duplicate asset classification documentation (~150 lines)
```

**Step 3: Commit**

```bash
git add plugins/pb-figma/.claude-plugin/plugin.json
git add plugins/pb-figma/CHANGELOG.md
git commit -m "chore(pb-figma): bump version to 1.10.0 - cleanup audit complete

Resolved 13 issues from structure audit:
- 1 CRITICAL (invalid tool reference)
- 3 HIGH (placeholders, unused prompts, missing agent)
- 6 MEDIUM (duplicates, inconsistencies, workflow clarity)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Summary

| Task | Priority | Files Changed | Lines Changed (est.) |
|------|----------|---------------|---------------------|
| 1 | CRITICAL | 1 | ~30 |
| 2 | HIGH | 2 | ~20 |
| 3 | HIGH | 1 | ~15 |
| 4 | HIGH | 1 | ~5 |
| 5 | MEDIUM | 1 | ~6 |
| 6 | MEDIUM | 3 | ~250 (net: -150) |
| 7 | MEDIUM | 4 | ~200 (net: -100) |
| 8 | MEDIUM | 4 | ~150 (net: -80) |
| 9 | MEDIUM | 2 | ~30 |
| 10 | MEDIUM | 3 | ~6 |
| 11 | CLEANUP | 2 | ~30 |
| **Total** | | **~15 files** | **Net: ~-300 lines** |

**Expected outcome:** Cleaner, more maintainable plugin with single source of truth for shared concepts.
