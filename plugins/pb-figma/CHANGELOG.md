# Changelog

All notable changes to the pb-figma plugin will be documented in this file.

## [1.18.0] - 2026-02-06

### Changed
- **MCP Server** - Updated to pixelbyte-figma-mcp>=3.2.15,<4.0.0 (added upper bound for stability)
- **Package Version Sync** - Synchronized local MCP package version from 2.5.0 to 3.2.15 to match PyPI release
- **Plugin Version** - Bumped to 1.18.0 for dependency update

### Fixed
- **Version Inconsistency** - Resolved version mismatch between local package (2.5.0) and runtime constraint (3.2.13+)

## [1.17.0] - 2026-02-05

### Added
- **Inline Text Variations (React)** - React code generator now handles `characterStyleOverrides` for multi-color/multi-style inline text using `<span>` segments
- **Dependency-Aware Fan-Out Batching** - SKILL.md pipeline now groups parent+children components in same batch during parallel code generation (batch_size=4)
- **Pipeline Handoff Contract Validation** - All 5 pipeline agents now validate input contract (spec existence, required sections) before processing
- **Optional Test Generation Step** - React (Jest/RTL) and SwiftUI (XCTest) code generators include Step 12 for component test scaffolding
- **Component Dependencies in Subset Mode** - code-generator-base documents cross-batch dependency resolution for fan-out execution

### Changed
- **Code Connect Registration Timing** - Moved from Phase 4 (code-gen) to Phase 5 (compliance-checker post-validation) to ensure only verified components are registered
- **pipeline-handoff.md** - Now referenced by all 5 agents (was unreferenced); header updated accordingly
- **docs-index.md** - Updated "Used By" columns for pipeline-handoff and inline-text-variations entries

### Fixed
- **Asset Manager Batch Size** - Standardized to 5 assets per API call
- **Asset Manager Classification** - Spec-first classification, MCP only when ambiguous; resolved SIMPLE_ICON vs COMPLEX_VECTOR overlap
- **Asset Manager Node Dedup** - Added node_id deduplication before batch download
- **Asset Manager SVG Detection** - Made SVG fill detection mandatory step
- **Asset Manager Flagged Frames** - Added explicit flagged frame processing workflow and validation checklist
- **Asset Manager Table Format** - Unified Downloaded Assets table format matching code-gen expectations

### Improved
- **Compliance Checker v2.0** - Major optimizations for FAZ-5 phase
- **MCP Server** - Updated to pixelbyte-figma-mcp>=3.2.13

## [1.15.1] - 2026-01-30

### Fixed
- **Checkpoint Naming Conflict** - code-generator-react and code-generator-swiftui now write framework-specific checkpoint files (`checkpoint-4-code-generator-react.json` / `-swiftui.json`)
- **Orphaned Reference Headers** - Updated `Used by` headers for `figma-mcp-server.md`, `pipeline-config.md`, `pipeline-handoff.md` to reflect actual usage
- **CHANGELOG Dedup Attribution** - Clarified that dedup consolidation was done in v1.10.0
- **plugin.json Version Mismatch** - Synced plugin.json version with CHANGELOG (was 1.17.0)
- **asset-manager Frontmatter** - Removed non-standard `model: sonnet` field
- **SKILL.md References** - Added docs-index.md pointer for complete reference catalog
- **docs-index.md Used-by** - Synced columns with actual agent references

## [1.15.0] - 2026-01-30

### Added
- **Self-Verification Loops** - code-generator-react and code-generator-swiftui now verify their own output (TypeScript compilation, syntax validation, import resolution, spec compliance) before handing off to compliance-checker
- **Component Subset Mode** - Code generators support "Generate ONLY these components" mode for parallel fan-out execution
- **Component Fan-Out** - SKILL.md pipeline now supports parallel code generation when >3 components (batch size: 4)
- **JSON Checkpoint System** - All 5 pipeline agents write `.qa/checkpoint-{N}-{agent}.json` after completion, enabling pipeline resume from last successful phase
- **Pipeline Resume** - SKILL.md documents checkpoint-based resume for failed pipelines
- **Checkpoint-Based Recovery** - error-recovery.md documents checkpoint file structure and recovery workflow

### Changed
- **compliance-checker Pre-Check** - Reads self-verification results from spec to skip redundant checks (focus on WARN/FAIL items)
- **Asset Node Map Dedup** - Both code generators now reference `asset-node-mapping.md` (consolidation done in v1.10.0, pointer standardized here)
- **Frame Properties Dedup** - code-generator-swiftui now references `frame-properties.md` (consolidation done in v1.10.0, pointer standardized here)

## [1.14.0] - 2026-01-28

### Fixed
- **Hex Color Format** - Fixed RGBA vs ARGB inconsistency in documentation (now correctly documents ARGB format matching implementation)
- **MCP vs Image() Clarification** - Added decision table clarifying when to use MCP generation vs manual Image() calls
- **UnevenRoundedRectangle Order** - Fixed parameter order in examples to match Swift API signature

### Changed
- **Reduced CRITICAL Markers** - Reduced from 10 to 5 truly critical warnings (improves signal-to-noise ratio)
- **Standardized Code Indentation** - All SwiftUI examples now use 2-space indentation consistently
- **Removed Duplicate Extensions** - Consolidated Color+Hex extension (removed ~15 duplicate lines)
- **Removed Duplicate Templates** - Consolidated Image() generation templates (removed ~20 duplicate lines)

### Added
- **iOS 17+ #Preview Pattern** - Added modern `#Preview` macro alongside deprecated PreviewProvider for iOS 13-16 compatibility

## [1.13.0] - 2026-01-28

### Added
- **Inline Text Color Detection** - Design Analyst now detects `characterStyleOverrides` and produces Inline Text Variations table with per-segment colors
- **Fill Opacity Extraction** - Design Validator extracts both fill opacity and node opacity separately, calculates effective opacity
- **Icon Name Pattern Detection** - Design Validator detects icon library naming patterns (e.g., `mynaui:arrow-right`) and classifies as thematic icons
- **Text Concatenation** - Code Generator SwiftUI produces `Text(...) + Text(...)` for inline color/style variations
- **Image-with-Text Detection** - Code Generator SwiftUI skips duplicate Text() when illustration contains embedded text (flagged as DOWNLOAD_AS_IMAGE)
- **test-inline-text-color.md** - Test case for inline text color detection and SwiftUI concatenation
- **test-image-with-text.md** - Test case for image-with-text duplication prevention

### Fixed
- **"Hook" Text Color** - Inline text color now extracted correctly (was white, now yellow #F2F20D with underline)
- **Card Background Opacity** - Fill opacity now extracted separately from node opacity (was missing 0.05 opacity)
- **Card Icon Classification** - Icons with library naming patterns now classified correctly (was using wrong icon)
- **Duplicate Text in Image** - Text embedded in flagged illustrations no longer duplicated as separate Text() components
- **Card Height Missing** - Height now mandatory in Frame Properties table (was optional)

### Changed
- Design Validator Colors table now has Fill Opacity, Node Opacity, and Effective columns
- Design Analyst Frame Properties table now requires Height field
- Code Generator SwiftUI includes Image-with-Text Detection section in process

## [1.12.0] - 2026-01-28

### Added
- **Visual Verification Gate** - Mandatory Figma vs browser screenshot comparison (≥95% match required for PASS)
- **Accessibility Gate** - jest-axe, semantic HTML, keyboard accessibility, color contrast checks now REQUIRED for PASS
- **Responsive Gate** - Mandatory testing at 3 breakpoints (375px, 768px, 1440px)
- **figma_get_screenshot tool** - Added to compliance-checker for visual verification

### Changed
- Compliance Checker now has 3 mandatory gates before PASS status
- Final Report Template includes Visual and Responsive columns
- Pass/Fail criteria updated with explicit verification requirements

## [1.11.0] - 2026-01-28

### Added
- **Asset Node Map** - React agent now builds asset node map for proper Image/img generation
- **Frame Properties Map** - Tailwind dimension, border-radius, border patterns from spec
- **Opacity Handling** - Tailwind opacity modifiers (`/25`, `/50`, etc.) from Design Tokens
- **Gradient Support** - CSS linear-gradient, radial-gradient, conic-gradient mapping
- **Text Decoration** - Underline/strikethrough with custom colors via Tailwind
- **Required Utilities** - cn() utility, CSS variables setup, Tailwind 4 @theme
- **Icon/SVG Patterns** - lucide-react, SVG components, next/image selection guide
- **CVA Variants** - class-variance-authority pattern for multi-variant components
- **Responsive Patterns** - Figma constraints to Tailwind breakpoints mapping

### Changed
- React agent process steps expanded from 8 to 10 (includes Asset Node Map, Frame Properties Map)
- Component checklist expanded from 6 to 20 items matching SwiftUI agent
- React agent now matches SwiftUI agent's comprehensiveness (~1500 lines)

## [1.10.0] - 2026-01-28

### Fixed
- **Asset Manager** - Replaced invalid `figma_find_children` tool with `figma_get_node_details`
- **Tool Declarations** - Added missing Read tool to design-validator agent frontmatter
- **Reference Paths** - Standardized to `@skills/figma-to-code/references/` format in code-generator-base

### Changed
- **Vue/Kotlin Generators** - Marked as placeholder status in documentation
- **Prompt Templates** - Marked unused prompts as inactive with explanatory note
- **CI/CD Reference** - Fixed reference to non-existent "handoff" agent

### Added
- **opacity-extraction.md** - Shared reference for opacity handling (extracted from 2 agents)
- **layer-order-hierarchy.md** - Shared reference for layer order algorithm (extracted from 3 agents)
- **asset-classification-guide.md** - Shared reference for asset classification (extracted from 3 agents)
- **Flagged Frames Workflow** - Explicit documentation of decision flow across agents

### Removed
- Duplicate opacity documentation (~200 lines consolidated)
- Duplicate layer order documentation (~300 lines consolidated)
- Duplicate asset classification documentation (~150 lines consolidated)

## [1.9.1] - 2026-01-28

### Fixed
- **Compliance Checker** - Added SwiftUI-specific verification patterns for `.frame()`, `.clipShape()`, `.overlay()`, and color tokens
- **Hex-Alpha Parsing** - Documented `#RRGGBBAA` format conversion (e.g., `#FFFFFF40` → 0.25 opacity)
- **CENTER Stroke Alignment** - Added SwiftUI pattern using `.inset(by:)` modifier
- **Corner Radius Terminology** - Added mapping table: Figma TL/TR/BL/BR → SwiftUI topLeading/topTrailing/bottomLeading/bottomTrailing
- **Dimension Rules** - Clarified when to use `width:` vs `maxWidth:` in `.frame()` modifier
- **Modifier Ordering** - Documented correct sequence: padding→frame→background→clipShape→overlay→shadow

## [1.9.0] - 2026-01-28

### Added
- **Frame Properties Extraction** - Design Validator extracts dimensions, cornerRadius, and border/stroke from all container nodes
- **Frame Properties Spec Format** - Design Analyst includes width, height, cornerRadius, border in component property tables
- **Frame Properties Application** - Code Generator SwiftUI applies `.frame()`, `.clipShape()`, `.overlay(.stroke())` modifiers
- **Per-Corner Radius Support** - UnevenRoundedRectangle (iOS 16+) and RoundedCorner custom Shape (iOS 15) for non-uniform corners
- **Color+Hex Extension** - Swift extension for initializing Color from hex strings
- **RoundedCorner Shape** - Custom Shape for per-corner radius on iOS 15

### Changed
- Design Validator checklist includes frame dimensions, corner radius, border/stroke items
- Design Analyst component property table extended with Dimensions, Corner Radius, Border columns
- Code Generator SwiftUI process includes "Build Frame Properties Map" step
- Compliance Checker design tokens checklist includes frame properties verification

### Fixed
- Cell sizes now match Figma design specifications exactly
- Corner radius values properly extracted and applied (uniform and per-corner)
- Border/stroke color, width, and alignment preserved from Figma

## [1.8.0] - 2026-01-27

### Added
- Asset Children marking in Implementation Spec (design-analyst)
- Asset Node Map for Image() generation (code-generator-swiftui)
- Automatic Image() code generation for asset nodes
- Illustration vs Icon detection based on dimensions
- Rendering mode selection from Downloaded Assets table

### Fixed
- Icons and illustrations now properly rendered in SwiftUI via Image() calls
- Asset nodes no longer generate broken Path/Shape code

## [1.7.0] - 2026-01-27

### Added
- **Illustration Detection** - Complexity-based triggers identify potential illustrations (≥15 descendant nodes, ≥5 unique colors, ≥3 gradients)
- **LLM Vision Analysis** - Asset Manager uses Claude Vision to analyze flagged frames and determine if they are illustrations
- **Flagged Frame Reading** - Asset Manager reads illustration flags from implementation spec
- **Dark+Bright Sibling Detection** - Design Validator detects dark/bright color pairs that may indicate overlays
- **Multiple Opacity Detection** - Design Validator identifies nodes with multiple opacity values applied
- **Gradient Overlay Detection** - Design Validator detects gradient fills that may be overlay effects
- **Flag Preservation** - Design Analyst preserves flagged illustration frames in implementation spec

### Changed
- Design Validator now includes illustration complexity analysis in validation report
- Asset Manager classification enhanced with LLM-assisted illustration detection
- Design Analyst spec output includes `flaggedForIllustrationReview` field

## [1.6.0] - 2026-01-27

### Fixed
- **Chart/Illustration Detection** - MCP now properly detects nodes with `exportSettings` (fixes bar chart not downloading)
- **Asset Classification** - Relaxed COMPLEX_VECTOR criteria (≥3 children, >50px) to catch smaller charts
- **Icon Misclassification** - Nodes with exportSettings no longer incorrectly classified as icons

### Added
- `_is_chart_or_illustration()` helper function in MCP for improved asset detection
- `CHART_ILLUSTRATION` asset type in asset-manager classification
- `Has Export Settings` column in design-validator Assets Inventory
- `Illustrations & Charts` validation checklist in design-validator

### Changed
- MCP version bumped to 2.5.0
- Classification priority now places CHART_ILLUSTRATION highest

## [1.5.0] - 2026-01-27

### Added
- Documentation index (`docs-index.md`) for lazy-loading references
- Reference loading sections in all agents

### Changed
- Reduced SKILL.md from 1000 lines to ~150 lines (estimated 60-70% reduction in initial context loading)
- Moved DOM flattening rules to code-generator-base.md
- Moved TODO comment strategy to code-generator-base.md
- Agents now load references on-demand instead of upfront

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
