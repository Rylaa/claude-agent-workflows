# pb-figma Agents

Agents for the Figma-to-Code pipeline.

## Pipeline Order

1. **design-validator** - Validates design completeness
2. **design-analyst** - Creates implementation spec
3. **asset-manager** - Downloads and organizes assets
4. **code-generator** - Generates production code
5. **compliance-checker** - Verifies code matches spec

## Usage

Agents are invoked automatically by the `figma-to-code` skill when a Figma URL is provided.

### Individual Agent Usage

```
@design-validator validate https://figma.com/...
@design-analyst analyze docs/figma-reports/abc123-validation.md
@asset-manager download docs/figma-reports/abc123-spec.md
@code-generator generate docs/figma-reports/abc123-spec.md
@compliance-checker verify docs/figma-reports/abc123-spec.md
```

## Reports

All outputs saved to `docs/figma-reports/`:
- `{file_key}-validation.md` - Design validation results
- `{file_key}-spec.md` - Implementation specification
- `{file_key}-final.md` - Compliance check results

## Background Agents

### font-manager

Runs in background after Design Validator completes. Does not block the main pipeline.

**Trigger:** Design Validator status is PASS or WARN

**Function:**
- Detects fonts from Figma typography tokens
- Downloads from Google Fonts, Font Squirrel
- Sets up fonts for detected platform (React, SwiftUI, Kotlin, Vue)
- Updates spec with "Fonts Setup" section

**Usage:**
```
Pipeline runs automatically:
Design Validator ──┬──► Design Analyst ──► ...
                   │
                   └──► Font Manager (background)
```

Manual trigger:
```
@font-manager setup docs/figma-reports/{file_key}-validation.md
```

