# Changelog

All notable changes to the pb-figma plugin will be documented in this file.

## [1.4.3] - 2026-01-27

### Fixed
- **Large File Overflow** - Design Validator now uses depth=3 (was 10) to prevent response size errors
- **MCP Response Size** - Added error handling for responses >256KB with recovery strategies
- **New File Write Error** - Agents now use Bash to create files before Write tool

### Added
- Bash tool to design-validator and design-analyst agents
- Large file handling documentation with progressive depth reduction
- File creation steps before Write operations

## [1.4.2] - 2026-01-27

### Fixed
- **Agent Invocation Bug** - Skill now correctly invokes agents via Task tool instead of calling MCP tools directly
- **SKILL.md Structure** - Added CRITICAL section at top requiring Task tool usage for agent invocation
- **5-Phase Workflow Clarification** - Marked as "Agent Reference Documentation" to prevent direct execution

### Changed
- SKILL.md now has clear separation between orchestration instructions and agent reference documentation
- Each workflow phase now indicates which agent uses it (e.g., "Used by: design-validator")

## [1.4.1] - 2026-01-26

### Added
- **Card Icon Classification** - Design Analyst now classifies icons by position (leading=thematic, trailing=status indicator)
- **Figma MCP Access for Design Analyst** - Agent can now query Figma API directly to verify ambiguous assets
- **Duplicate Icon Handling** - Design Validator detects and classifies duplicate-named icons
- **Asset Position/Type Columns** - Validation Report now includes `Position` and `Icon Type` for each asset
- **TODO.md** - Plugin improvement roadmap with figma_list_assets enhancement proposals

### Fixed
- **Wrong Card Icons Bug** - Design Analyst no longer assigns trailing checkmark icons as card thematic icons
- **HStack Layout Analysis** - Agents now correctly identify leading vs trailing elements in card layouts

### Changed
- Design Analyst process now includes "Validate Card Icons" step (Step 7)
- Design Validator process now includes "Classify Duplicate Icons" step (Step 6)
- Asset inventory format extended with Position and Icon Type columns

## [1.4.0] - 2026-01-26

### Added
- **Text Decoration Support** - Design Analyst now extracts underline/strikethrough colors
- **COMPLEX_VECTOR Classification** - Asset Manager detects multi-path vectors (≥10 paths, >100px) and downloads as PNG
- **SwiftUI Text Decoration** - Code Generator applies `.underline(color:)` and `.strikethrough(color:)` modifiers
- **E2E Test Suite** - Complete test coverage for TypeSceneText and OnboardingAnalysisView components

### Fixed
- **Opacity Extraction** - Design Analyst now correctly calculates compound opacity (fill opacity × node opacity)
- **Gradient Detection** - All gradient stops preserved with exact positions (was only keeping first/last)
- **SwiftUI Opacity Application** - Code Generator now applies `.opacity()` modifiers from spec
- **SwiftUI Gradient Rendering** - AngularGradient/LinearGradient now include all color stops with exact locations

### Changed
- Asset Manager classification table updated with clear criteria for SIMPLE_ICON vs COMPLEX_VECTOR vs RASTER_IMAGE
- Design Analyst opacity column now shows "Usage" context (fill, stroke, overlay, etc.)

## [1.3.0] - 2026-01-25

### Added
- Initial 5-agent pipeline architecture
- Design Validator agent
- Design Analyst agent
- Asset Manager agent
- Code Generator agents (React, SwiftUI, Vue, Kotlin)
- Compliance Checker agent
- figma-to-code skill with framework detection

### Features
- Pixelbyte Figma MCP Server integration
- Auto Layout validation
- Design token extraction
- Code Connect support
- Visual validation with Claude Vision
