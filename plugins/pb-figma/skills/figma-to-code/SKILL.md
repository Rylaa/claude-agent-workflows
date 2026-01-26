---
name: figma-to-code
description: This skill handles pixel-perfect Figma design conversion to production code (React/Tailwind, SwiftUI, Vue, Kotlin) using Pixelbyte Figma MCP Server. It should be used when a Figma URL or design selection needs to be converted to production-ready code. The skill employs a 5-phase workflow with framework detection and routing to framework-specific agents.
---

# Figma-to-Code Pixel-Perfect Conversion

## Documentation Index

For detailed references, see @docs-index.md

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
    v
+-------------------------+
| 3. asset-manager        | -> Updated Spec + Assets
+-------------------------+
    |
    v
+---------------------------------------------+
| 4. Framework Detection & Routing            |
+---------------------------------------------+
| -> React/Next.js  -> code-generator-react   |
| -> SwiftUI        -> code-generator-swiftui |
| -> Vue/Nuxt       -> code-generator-vue     |
| -> Kotlin/Compose -> code-generator-kotlin  |
+---------------------------------------------+
    |
    v
+-------------------------+
| 5. compliance-checker   | -> Final Report
+-------------------------+
```

## Invocation Sequence

```python
# Step 1: Design Validator
Task(subagent_type="pb-figma:design-validator",
     prompt="Validate Figma URL: {url}")

# Step 2: Design Analyst (MANDATORY - creates Implementation Spec)
Task(subagent_type="pb-figma:design-analyst",
     prompt="Create Implementation Spec from: docs/figma-reports/{file_key}-validation.md")

# Step 3: Asset Manager
Task(subagent_type="pb-figma:asset-manager",
     prompt="Download assets from spec: docs/figma-reports/{file_key}-spec.md")

# Step 4: Code Generator (framework-specific)
Task(subagent_type="pb-figma:code-generator-{framework}",
     prompt="Generate code from spec: docs/figma-reports/{file_key}-spec.md")

# Step 5: Compliance Checker
Task(subagent_type="pb-figma:compliance-checker",
     prompt="Validate implementation against spec: docs/figma-reports/{file_key}-spec.md")
```

## Framework Detection

Before dispatching code generator (Step 4):

1. **Swift/Xcode:** `ls *.xcodeproj *.xcworkspace Package.swift` -> `code-generator-swiftui`
2. **Android/Kotlin:** Find `build.gradle.kts` with `androidx.compose` -> `code-generator-kotlin`
3. **Node.js:** Check `package.json` for react/next/vue/nuxt -> route accordingly
4. **Default:** `code-generator-react` with warning

## Report Directory

All reports saved to: `docs/figma-reports/`

```
docs/figma-reports/
+-- {file_key}-validation.md   # Agent 1 output
+-- {file_key}-spec.md         # Agent 2+3 output
+-- {file_key}-final.md        # Agent 5 output
```

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

For detailed information on specific topics:

| Topic | Reference |
|-------|-----------|
| Token conversion | @references/token-mapping.md |
| Common issues | @references/common-issues.md |
| Visual validation | @references/visual-validation-loop.md |
| Error recovery | @references/error-recovery.md |
| Figma MCP tools | @references/figma-mcp-server.md |
| Code Connect | @references/code-connect-guide.md |
