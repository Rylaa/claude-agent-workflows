# pb-figma Best Practices Improvement Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Apply Claude Code best practices to pb-figma plugin - reduce context bloat, add verification loops, implement hooks, and consolidate unused content.

**Source:** Claude Code Best Practices documentation (https://code.claude.com/docs/best-practices)

**Analysis Method:** 4 parallel Explore agents analyzed agents, skills, hooks, and verification patterns.

---

## Executive Summary

| Category | Current State | Target State | Impact |
|----------|--------------|--------------|--------|
| Agent Size | 8,500+ lines total | ~5,500 lines | Context ↓ 35% |
| Hooks | 0 implemented | 5 key hooks | Reliability ↑↑ |
| Verification | Text/code only | + Visual verification | Quality ↑↑ |
| Unused Content | 1,074 lines | 0 lines | Clarity ↑ |

---

## Part 1: Context Reduction (CLAUDE.md Best Practice)

> "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!"

### Task 1.1: Extract Boilerplate from code-generator-react

**Files:** `plugins/pb-figma/agents/code-generator-react.md`

**Problem:** 1,423 lines with ~500 lines of pruneable boilerplate

**Sections to Extract:**
| Lines | Content | Move To |
|-------|---------|---------|
| 909-1071 | Component structure examples | `references/react-patterns.md` |
| 563-677 | CSS gradient syntax | `references/gradient-patterns.md` |
| 1191-1272 | Responsive Tailwind patterns | `references/responsive-patterns.md` |
| 973-1061 | CVA setup boilerplate | `references/cva-setup.md` |

**Expected Reduction:** ~400 lines → agent becomes ~1,000 lines

### Task 1.2: Extract Boilerplate from code-generator-swiftui

**Files:** `plugins/pb-figma/agents/code-generator-swiftui.md`

**Problem:** 1,475 lines with ~450 lines of pruneable boilerplate

**Sections to Extract:**
| Lines | Content | Move To |
|-------|---------|---------|
| 1108-1220 | Component structure examples | `references/swiftui-patterns.md` |
| 1223-1280 | Color+Hex, RoundedCorner extensions | `references/swiftui-extensions.md` |
| 721-809 | Gradient patterns | `references/gradient-patterns.md` (shared) |
| 529-565 | Modifier ordering rules | `references/swiftui-modifier-order.md` |

**Expected Reduction:** ~350 lines → agent becomes ~1,100 lines

### Task 1.3: Extract Platform Scripts from font-manager

**Files:** `plugins/pb-figma/agents/font-manager.md`

**Problem:** 1,082 lines with ~580 lines of platform-specific setup scripts

**Sections to Extract:**
| Lines | Content | Move To |
|-------|---------|---------|
| 255-361 | React/Next.js font setup | `references/font-setup-react.md` |
| 388-524 | SwiftUI Info.plist + extensions | `references/font-setup-swiftui.md` |
| 546-724 | Android/Kotlin font XML | `references/font-setup-kotlin.md` |
| 736-906 | Vue font configuration | `references/font-setup-vue.md` |

**Expected Reduction:** ~500 lines → agent becomes ~580 lines

### Task 1.4: Remove Unused Prompt Templates

**Files:** `plugins/pb-figma/skills/figma-to-code/references/prompts/`

**Problem:** 791 lines marked as "unused" but still in codebase

**Action:** Archive or delete:
- `analyze-design.md` (126 lines) - unused
- `generate-component.md` (118 lines) - unused
- `validate-refine.md` (218 lines) - unused
- `handoff.md` (143 lines) - unused

**Note:** Keep `mapping-planning.md` (186 lines) - referenced in design-analyst.md

**Expected Reduction:** 605 lines removed

### Task 1.5: Remove/Integrate ci-cd-integration.md

**Files:** `plugins/pb-figma/skills/figma-to-code/references/ci-cd-integration.md`

**Problem:** 283 lines, completely unused, no agent references it

**Options:**
1. **Delete** - If CI/CD integration isn't planned for v1.x
2. **Integrate** - Create hook that uses it for automated pipelines

**Recommendation:** Archive to `references/archive/` with deprecation note

---

## Part 2: Verification Improvements (Highest Leverage)

> "Give Claude a way to verify its work - this is the single highest-leverage thing you can do."

### Task 2.1: Add Visual Verification to Compliance Checker

**Files:** `plugins/pb-figma/agents/compliance-checker.md`

**Problem:** Compliance checking is text/code-based only. A component can pass compliance but look wrong on screen.

**Add Section:**
```markdown
## Visual Verification Gate (REQUIRED)

Before marking component as PASS:

1. **Take browser screenshot** of generated component
2. **Take Figma screenshot** of original design (figma_get_screenshot)
3. **Compare using Claude Vision**:
   - Typography matches? (±2px tolerance)
   - Colors match? (exact hex)
   - Spacing matches? (±4px tolerance)
   - Layout matches? (structure, alignment)
4. **If differences found:** Mark as WARN with visual diff notes
5. **Only PASS if visual match ≥95%**

```typescript
// Add to compliance-checker frontmatter:
tools:
  - mcp__plugin_pb-figma_pixelbyte-figma-mcp__figma_get_screenshot
  - mcp__claude-in-chrome__computer  // for browser screenshot
```
```

### Task 2.2: Add Test Execution Verification

**Files:** `plugins/pb-figma/agents/compliance-checker.md`

**Problem:** Test generation templates exist but tests aren't verified to:
- Compile
- Pass
- Achieve coverage targets

**Add Section:**
```markdown
## Test Verification Gate (REQUIRED)

Before marking component as PASS:

1. **Verify tests exist:**
   ```bash
   ls -la {component}/*.test.tsx {component}/*.spec.tsx
   ```

2. **Run tests:**
   ```bash
   npm test -- --testPathPattern={component} --coverage
   ```

3. **Check results:**
   - All tests pass? → Continue
   - Any test fails? → Mark FAIL with test output
   - Coverage < 80%? → Mark WARN

4. **Run type check:**
   ```bash
   npx tsc --noEmit
   ```
```

### Task 2.3: Add Asset Rendering Verification

**Files:** `plugins/pb-figma/agents/compliance-checker.md`

**Problem:** Asset Manager validates downloads but doesn't verify they render correctly.

**Add Section:**
```markdown
## Asset Rendering Verification

For each asset in Downloaded Assets table:

1. **Check file exists:**
   ```bash
   test -f {asset_path} && echo "EXISTS" || echo "MISSING"
   ```

2. **For SVG assets - verify valid XML:**
   ```bash
   xmllint --noout {asset_path}
   ```

3. **For images - verify dimensions:**
   ```bash
   file {asset_path} | grep -E "[0-9]+x[0-9]+"
   ```

4. **Visual check:** Take screenshot of component → verify assets visible
```

### Task 2.4: Enforce Accessibility Gate

**Files:** `plugins/pb-figma/agents/compliance-checker.md`

**Problem:** Accessibility validation is optional. Components can pass without a11y verification.

**Change from:**
```markdown
## Accessibility Verification (Optional)
```

**Change to:**
```markdown
## Accessibility Verification (REQUIRED for PASS)

Component CANNOT receive PASS status without:
- [ ] jest-axe run with 0 violations
- [ ] Semantic HTML verified (no div soup)
- [ ] All images have alt text
- [ ] Interactive elements keyboard accessible
- [ ] Color contrast ≥ 4.5:1 for text

**If any a11y check fails:** Maximum status = WARN
```

### Task 2.5: Enforce Responsive Gate

**Files:** `plugins/pb-figma/agents/compliance-checker.md`

**Problem:** Responsive validation is optional. Desktop-only components can pass.

**Add Section:**
```markdown
## Responsive Verification (REQUIRED for PASS)

Test at minimum 3 breakpoints:
- Mobile: 375px
- Tablet: 768px
- Desktop: 1440px

For each breakpoint:
1. Resize browser/viewport
2. Take screenshot
3. Compare with Figma responsive variants (if available)
4. Verify no overflow, broken layouts, or hidden content

**If responsive issues found:** Maximum status = WARN
```

---

## Part 3: Hook Implementation

> "Use hooks for actions that must happen every time with zero exceptions."

### Task 3.1: Create UserPromptSubmit Hook - Figma URL Validation

**Files:** Create `plugins/pb-figma/hooks/validate-figma-url.md`

**Purpose:** Validate Figma URL format before dispatching to agents

```markdown
---
event: UserPromptSubmit
match_regex: "figma\\.com"
---

# Figma URL Validation Hook

When user message contains a Figma URL:

1. Extract URL from message
2. Validate format: `https://www.figma.com/(design|file)/{file_key}/{name}?node-id={node_id}`
3. If invalid format:
   - Return: "Invalid Figma URL format. Expected: https://www.figma.com/design/{file_key}/..."
   - Block further processing
4. If valid: Allow message to proceed
```

### Task 3.2: Create PreToolUse Hook - MCP Rate Limiting

**Files:** Create `plugins/pb-figma/hooks/mcp-rate-limit.md`

**Purpose:** Prevent Figma API rate limit errors

```markdown
---
event: PreToolUse
tools:
  - mcp__plugin_pb-figma_pixelbyte-figma-mcp__*
---

# MCP Rate Limiting Hook

Before any Figma MCP tool call:

1. Check last call timestamp
2. If < 500ms since last call: Wait until 500ms elapsed
3. Log: "Rate limit: waiting {ms}ms before Figma API call"
4. Allow tool to proceed
```

### Task 3.3: Create PostToolUse Hook - Asset Download Verification

**Files:** Create `plugins/pb-figma/hooks/verify-asset-download.md`

**Purpose:** Automatically verify asset downloads succeeded

```markdown
---
event: PostToolUse
tools:
  - mcp__plugin_pb-figma_pixelbyte-figma-mcp__figma_export_assets
  - mcp__plugin_pb-figma_pixelbyte-figma-mcp__figma_get_images
---

# Asset Download Verification Hook

After asset download completes:

1. Parse tool result for file paths
2. For each path:
   - Verify file exists
   - Verify file size > 0
   - Log: "✓ Asset verified: {path} ({size} bytes)"
3. If any missing: Log warning and suggest retry
```

### Task 3.4: Create Stop Hook - Pipeline Cleanup

**Files:** Create `plugins/pb-figma/hooks/pipeline-cleanup.md`

**Purpose:** Clean up partial files when pipeline fails or user cancels

```markdown
---
event: Stop
---

# Pipeline Cleanup Hook

When session ends or agent fails:

1. Check for incomplete reports in `docs/figma-reports/`
2. If found partial files (no "## Final Status" section):
   - Move to `docs/figma-reports/incomplete/`
   - Log: "Moved incomplete report: {filename}"
3. Clean up any temporary assets in `/tmp/figma-assets/`
```

### Task 3.5: Create SessionStart Hook - Framework Detection Cache

**Files:** Create `plugins/pb-figma/hooks/detect-framework.md`

**Purpose:** Pre-detect framework once per session instead of in each agent

```markdown
---
event: SessionStart
---

# Framework Detection Hook

On session start:

1. Detect project framework:
   - Check for `package.json` → React/Vue
   - Check for `*.xcodeproj` or `Package.swift` → SwiftUI
   - Check for `build.gradle.kts` → Kotlin
2. Cache result in session state
3. Log: "Detected framework: {framework}"

Agents can read from session state instead of re-detecting.
```

---

## Part 4: Fresh Context Review (Writer/Reviewer Pattern)

> "A fresh context improves code review since Claude won't be biased toward code it just wrote."

### Task 4.1: Create Code Reviewer Agent

**Files:** Create `plugins/pb-figma/agents/code-reviewer.md`

**Purpose:** Review generated code with fresh context (no bias from generation)

```markdown
---
name: code-reviewer
description: Reviews generated code with fresh context for edge cases, performance, and quality
tools:
  - Read
  - Grep
  - Glob
model: opus
---

# Code Reviewer Agent

You review code generated by code-generator agents.
**You have NO context of how the code was written.**

## Review Checklist

### 1. Edge Cases
- [ ] Null/undefined handling
- [ ] Empty array/object handling
- [ ] Boundary conditions
- [ ] Error states

### 2. Performance
- [ ] Unnecessary re-renders (React)
- [ ] Memory leaks (event listeners, subscriptions)
- [ ] Bundle size concerns (large imports)

### 3. Code Quality
- [ ] Naming clarity
- [ ] DRY violations
- [ ] Dead code
- [ ] Hardcoded values that should be configurable

### 4. Security
- [ ] XSS vulnerabilities
- [ ] Unsafe innerHTML usage
- [ ] Exposed sensitive data

## Output Format

```markdown
## Code Review: {component}

### Issues Found

| Severity | File:Line | Issue | Recommendation |
|----------|-----------|-------|----------------|
| HIGH | ... | ... | ... |

### Summary
- Critical: {count}
- Warning: {count}
- Info: {count}

### Verdict: APPROVE / REQUEST_CHANGES
```
```

### Task 4.2: Add Review Step to Pipeline

**Files:** Update `plugins/pb-figma/skills/figma-to-code/SKILL.md`

**Change pipeline from:**
```
4. code-generator-* → 5. compliance-checker
```

**Change to:**
```
4. code-generator-* → 4.5. code-reviewer → 5. compliance-checker
```

---

## Part 5: Documentation Cleanup

### Task 5.1: Update docs-index.md

**Files:** `plugins/pb-figma/docs-index.md`

- Remove references to archived prompt templates
- Add new reference files created in Part 1
- Update "Used By" column for accuracy

### Task 5.2: Fix SKILL.md docs-index Reference

**Files:** `plugins/pb-figma/skills/figma-to-code/SKILL.md`

**Problem:** Says "see @docs-index.md" but file is at parent level

**Fix:** Change to `@../docs-index.md` or move docs-index.md to skill level

### Task 5.3: Version Bump and CHANGELOG

**Files:**
- `plugins/pb-figma/.claude-plugin/plugin.json` → 1.11.0
- `plugins/pb-figma/CHANGELOG.md`

---

## Implementation Order

| Phase | Tasks | Priority | Effort |
|-------|-------|----------|--------|
| 1 | 2.1, 2.4, 2.5 | 🔴 CRITICAL | Medium |
| 2 | 3.1, 3.2, 3.3 | 🔴 HIGH | Low |
| 3 | 1.1, 1.2, 1.3 | 🟡 MEDIUM | Medium |
| 4 | 4.1, 4.2 | 🟡 MEDIUM | Low |
| 5 | 1.4, 1.5, 5.* | 🟢 LOW | Low |

**Estimated Total:**
- Context reduction: ~1,800 lines saved
- New verification gates: 4 mandatory checks
- New hooks: 5 automation points
- New agent: 1 (code-reviewer)

---

## Success Criteria

After implementation:

1. **Context Test:** Agent files average < 800 lines each
2. **Verification Test:** No component can PASS without visual + a11y + responsive checks
3. **Hook Test:** Invalid Figma URLs blocked before agent dispatch
4. **Review Test:** Every generated component reviewed by fresh-context agent
5. **Cleanup Test:** No unused files in active references directory

---

## Notes

- Based on analysis of 4 Explore agents running in parallel
- All line numbers reference current codebase state (2026-01-28)
- Hooks implementation requires Claude Code 1.0.30+ for full hook support
- Code reviewer agent adds ~30 seconds to pipeline but improves quality significantly
