---
name: figma-to-code
description: This skill handles pixel-perfect Figma design conversion to production code (React/Tailwind, SwiftUI, Vue, Kotlin) using Pixelbyte Figma MCP Server. It should be used when a Figma URL or design selection needs to be converted to production-ready code. The skill employs a 5-phase workflow with framework detection and routing to framework-specific agents.
---

# Figma-to-Code Pixel-Perfect Conversion

## Documentation Index

For detailed references, load via Glob: `**/docs-index.md`

## CRITICAL: Agent Invocation Required

**DO NOT use MCP tools directly.** This skill orchestrates specialized agents via `Task` tool.

```
+-------------------------------------------------------------------+
|  YOU MUST USE Task TOOL TO INVOKE AGENTS                          |
|                                                                   |
|  WRONG: Calling mcp__pixelbyte-figma-mcp__* directly              |
|  RIGHT: Task(subagent_type="pb-figma:design-validator", ...)      |
+-------------------------------------------------------------------+
```

## Agent Pipeline

```
Figma URL
    |
    v
+-------------------------+
| 1. design-validator     | -> Validation Report
+-------------------------+
    |
    v
+-------------------------+
| 2. design-analyst       | -> Implementation Spec
+-------------------------+
    |
    +---> [PARALLEL] --------+
    |                         |
    v                         v
+-------------------+  +-------------------+
| 3a. asset-manager |  | 3b. font-manager  |  (background, haiku)
| (haiku/opus*)     |  +-------------------+
+-------------------+
* haiku if no flagged frames, opus if flagged frames exist
    |
    v
+---------------------------------------------+
| 4. Framework Detection & Routing            |
+---------------------------------------------+
| -> React/Next.js  -> code-generator-react   | ✅
| -> SwiftUI        -> code-generator-swiftui | ✅
| -> Vue/Nuxt       -> code-generator-vue     | 🚧 Placeholder
| -> Kotlin/Compose -> code-generator-kotlin  | 🚧 Placeholder
+---------------------------------------------+
| Fan-Out: >3 components → parallel batches   |
+---------------------------------------------+
    |
    v
+-------------------------------+
| 5a. compliance-pre-check      | -> Static + A11y (haiku)
+-------------------------------+
    | (if PASS/WARN)
    v
+-------------------------------+
| 5b. compliance-checker        | -> Gate 2+3 + Final Report (opus)
+-------------------------------+
```

## Invocation Sequence

```python
# Step 1: Design Validator
Task(subagent_type="pb-figma:design-validator",
     prompt="Validate Figma URL: {url}")

# Step 2: Design Analyst (MANDATORY - creates Implementation Spec)
Task(subagent_type="pb-figma:design-analyst",
     prompt="Create Implementation Spec from: docs/figma-reports/{file_key}-validation.md")

# Step 3: Asset Manager + Font Manager (PARALLEL)
# Launch BOTH in a single message with multiple Task calls.
#
# ASSET MANAGER MODEL SELECTION:
# Before invoking, read the spec and check for "Flagged for LLM Review" section.
# - If NO flagged frames (section absent or empty) → use model="haiku" (all tasks are mechanical)
# - If flagged frames exist → do NOT set model (defaults to opus for LLM Vision analysis)
#
# Check: Grep("## Flagged for LLM Review", path="docs/figma-reports/{file_key}-spec.md")

# Option A: No flagged frames (common case ~80% of designs)
Task(subagent_type="pb-figma:asset-manager",
     model="haiku",
     prompt="Download assets from spec: docs/figma-reports/{file_key}-spec.md")

# Option B: Flagged frames exist (complex designs with ambiguous elements)
Task(subagent_type="pb-figma:asset-manager",
     model="opus",
     prompt="Download assets from spec: docs/figma-reports/{file_key}-spec.md")

# Font Manager always runs on haiku (100% mechanical, defined in agent header)
Task(subagent_type="pb-figma:font-manager",
     prompt="Detect and setup fonts from spec: docs/figma-reports/{file_key}-spec.md",
     run_in_background=True)

# Step 4: Code Generator (after asset-manager completes; font-manager continues in background)

## Component Count Check
# Read the spec's Component Hierarchy to count top-level components.

## Option A: Sequential (≤3 components)
Task(subagent_type="pb-figma:code-generator-{framework}",
     prompt="Generate code from spec: docs/figma-reports/{file_key}-spec.md")

## Option B: Fan-Out (>3 components)

### Batching Algorithm (dependency-aware)

# 1. **Parse Component Hierarchy** from spec — extract parent-child tree
# 2. **Identify leaf components** — components with no children (e.g., Button, Badge, Icon)
# 3. **Identify composite components** — components that reference other components as children
# 4. **Group by subtree** — keep each parent with its direct children in the same batch
# 5. **Distribute leaf components** — fill remaining batch slots with independent leaf components
# 6. **Target batch size: 4** — aim for ~4 components per batch, but never split a parent from its children

### Batching Rules
# - A parent and ALL its direct children MUST be in the same batch
# - Leaf components (no children, not referenced by others) can go in any batch
# - If a subtree has >4 components, it gets its own batch (no size limit for subtrees)
# - Shared utility components (used by 2+ parents) go in the FIRST batch

### Example
# Hierarchy:
#   PageLayout
#   ├── Header (uses Logo, NavMenu)
#   ├── CardGrid (uses Card, Badge)
#   └── Footer
#
# Batching:
#   Batch 1: [Logo, NavMenu, Header]        ← subtree
#   Batch 2: [Badge, Card, CardGrid]         ← subtree
#   Batch 3: [Footer, PageLayout]            ← root + leaf

### Execution
for batch in dependency_aware_batches:
    Task(subagent_type="pb-figma:code-generator-{framework}",
         prompt=f"Generate ONLY these components: {batch}. "
                f"Read full spec for context: docs/figma-reports/{file_key}-spec.md")

# > **Important:** Each batch reads the FULL spec for shared context (tokens, assets).
# > Only component generation is scoped to the batch.

# Step 5a: Compliance Pre-Check (runs on haiku - mechanical checks only)
# Static checks (structure, tokens, assets) + Gate 1 (Accessibility)
# All checks are threshold-based, regex-based, or formula-based → zero quality loss on haiku
Task(subagent_type="pb-figma:compliance-pre-check",
     prompt="Run static compliance checks and accessibility gate on: docs/figma-reports/{file_key}-spec.md")

# Step 5b: Full Compliance Checker (runs on opus - visual validation)
# Only invoke if pre-check passed (PRE_CHECK_PASS or PRE_CHECK_WARN)
# Check: Read(".qa/pre-check-results.json") → if status != "PRE_CHECK_FAIL"
#
# If PRE_CHECK_FAIL → pipeline stops here, no need for expensive visual validation
# If PRE_CHECK_PASS/WARN → proceed to Gate 2 (Responsive) + Gate 3 (Visual)
Task(subagent_type="pb-figma:compliance-checker",
     prompt="Validate implementation against spec: docs/figma-reports/{file_key}-spec.md. "
            "NOTE: Static checks and Gate 1 already passed in pre-check (.qa/pre-check-results.json). "
            "Focus on Gate 2 (Responsive) and Gate 3 (Visual Validation).")
```

## Framework Detection

Before dispatching code generator (Step 4):

1. **Swift/Xcode:** `ls *.xcodeproj *.xcworkspace Package.swift` -> `code-generator-swiftui` ✅
2. **Android/Kotlin:** Find `build.gradle.kts` with `androidx.compose` -> `code-generator-kotlin` 🚧 (placeholder, use React)
3. **Node.js:** Check `package.json` for react/next -> `code-generator-react` ✅
4. **Vue/Nuxt:** Check `package.json` for vue/nuxt -> `code-generator-vue` 🚧 (placeholder, use React)
5. **Default:** `code-generator-react` with warning

> **Note:** Vue and Kotlin generators are planned for future releases. Currently, use React or SwiftUI generators.

## Report Directory

All reports saved to: `docs/figma-reports/`

```
docs/figma-reports/
+-- {file_key}-validation.md   # Agent 1 output
+-- {file_key}-spec.md         # Agent 2+3 output
+-- {file_key}-final.md        # Agent 5 output
```

## Pipeline Resume

To resume a failed pipeline, check checkpoint files before starting:

```python
# Check for existing checkpoints
checkpoints = Glob(".qa/checkpoint-*.json")

if checkpoints:
    # Find highest completed phase
    highest = max(checkpoint.phase for checkpoint in checkpoints)
    # Resume from next phase using existing output files
    # Example: if highest == 2, skip design-validator and design-analyst,
    # start from asset-manager using the spec file from checkpoint-2
```

**Checkpoint files location:** `.qa/checkpoint-{N}-{agent}.json`

| Phase | Checkpoint | Resume From |
|-------|-----------|-------------|
| 1 complete | `checkpoint-1-design-validator.json` | Phase 2: design-analyst |
| 2 complete | `checkpoint-2-design-analyst.json` | Phase 3: asset-manager |
| 3 complete | `checkpoint-3-asset-manager.json` | Phase 4: code-generator |
| 4 complete | `checkpoint-4-code-generator-{framework}.json` | Phase 5a: compliance-pre-check |
| 5a complete | `checkpoint-5a-compliance-pre-check.json` | Phase 5b: compliance-checker (if PASS/WARN) |
| 5b complete | `checkpoint-5-compliance-checker.json` | Pipeline complete |

**Clean start:** Delete `.qa/checkpoint-*.json` to force full pipeline re-run.

## Figma URL Parsing

```
URL: figma.com/design/ABC123xyz/MyDesign?node-id=456-789

file_key: ABC123xyz
node_id: 456:789 (convert hyphen "-" to colon ":")

NOTE: URL format "456-789" must be used as "456:789"!
```

## Prerequisites

- Pixelbyte Figma MCP with `FIGMA_PERSONAL_ACCESS_TOKEN`
- Claude in Chrome MCP for visual validation
- Node.js runtime

## Core Principles

1. **Never guess** - Always extract design tokens from MCP
2. **Use semantic HTML** - Prefer correct elements over `<div>` soup
3. **Apply Claude Vision validation** - Visual comparison with TodoWrite tracking
4. **Match exactly** - No creative interpretation, match the design precisely
5. **Leverage Code Connect** - Map Figma components to existing codebase components

## References

**How to load references:** Use `Glob("**/references/{filename}.md")` to find the absolute path, then `Read()` the result.

> **Complete catalog:** See `docs-index.md` (`Glob("**/pb-figma/docs-index.md")`) for all 30+ references organized by category.

| Topic | Reference File | Glob Pattern |
|-------|---------------|--------------|
| Token conversion | `token-mapping.md` | `**/references/token-mapping.md` |
| Common issues | `common-issues.md` | `**/references/common-issues.md` |
| Visual validation | `visual-validation-loop.md` | `**/references/visual-validation-loop.md` |
| Error recovery | `error-recovery.md` | `**/references/error-recovery.md` |
| Figma MCP tools | `figma-mcp-server.md` | `**/references/figma-mcp-server.md` |
| Code Connect | `code-connect-guide.md` | `**/references/code-connect-guide.md` |
| Framework detection | `framework-detection.md` | `**/references/framework-detection.md` |
