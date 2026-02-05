# Pipeline Handoff Formats Reference

> **Used by:** design-analyst, asset-manager, code-generator-*, compliance-checker

This document defines the exact data contract between pipeline stages. Each agent must produce output matching the next agent's expected input.

---

## Stage 1 → Stage 2: Validation Report

**Producer:** design-validator
**Consumer:** design-analyst

**File:** `docs/figma-reports/{file_key}-validation.md`

### Required Sections

| Section | Required | Description |
|---------|----------|-------------|
| File Info | Yes | file_key, node_id, URL |
| Status | Yes | PASS / WARN / FAIL |
| Design Tokens | Yes | Colors, typography, spacing tables |
| Frame Properties | Yes | Dimensions, corner radius, borders |
| Assets | Yes | Asset list with node IDs |
| Auto Layout | Yes | Layout mode, padding, spacing |
| Flagged for LLM Review | Optional | Complex illustrations needing vision analysis |
| Inline Text Variations | Optional | characterStyleOverrides data |

---

## Stage 2 → Stage 3: Implementation Spec

**Producer:** design-analyst
**Consumer:** asset-manager

**File:** `docs/figma-reports/{file_key}-spec.md`

### Required Sections

| Section | Required | Description |
|---------|----------|-------------|
| Component Hierarchy | Yes | Tree structure with component types |
| Design Tokens | Yes | Mapped tokens (colors, typography, spacing) |
| Asset Requirements | Yes | Asset list with types, formats, node IDs |
| Frame Properties | Yes | Per-component dimension/style specs |
| Layer Order | Yes | zIndex assignments |
| Flagged for LLM Review | Pass-through | Copied verbatim from validator |
| Image-with-Text | Optional | [contains-text] annotations |
| Edge-to-Edge | Optional | Edge-to-edge child markers |
| Glass Effects | Optional | Glass/translucent effect annotations |

---

## Stage 3 → Stage 4: Updated Spec + Assets

**Producer:** asset-manager
**Consumer:** code-generator-*

**File:** `docs/figma-reports/{file_key}-spec.md` (updated in-place)

### Added Sections

| Section | Required | Description |
|---------|----------|-------------|
| Downloaded Assets | Yes | File paths, formats, dimensions |
| Asset Node Map | Yes | node_id → local file path mapping |
| Flagged Frame Decisions | Optional | DOWNLOAD_AS_IMAGE / GENERATE_AS_CODE |
| SVG Rendering Modes | Optional | .original vs .template per icon |

---

## Stage 4 → Stage 5: Generated Code

**Producer:** code-generator-*
**Consumer:** compliance-checker

**File:** `docs/figma-reports/{file_key}-spec.md` (updated in-place)

### Added Sections

| Section | Required | Description |
|---------|----------|-------------|
| Generated Code | Yes | File paths of generated components |
| Component File Map | Yes | Component name → file path |
| Framework | Yes | react / swiftui / vue / kotlin |
