# pb-figma Documentation Index

> **Usage:** This file is the documentation map for the entire pb-figma plugin. Agents load only the references they need via @path.

## Quick Start

- **Figma-to-Code Workflow:** @skills/figma-to-code/SKILL.md
- **Agent Pipeline:** @agents/README.md

## Agents

| Agent | Path | Purpose | Status |
|-------|------|---------|--------|
| design-validator | @agents/design-validator.md | Validate design completeness | ✅ Active |
| design-analyst | @agents/design-analyst.md | Create Implementation Spec | ✅ Active |
| asset-manager | @agents/asset-manager.md | Download and organize assets | ✅ Active |
| code-generator-react | @agents/code-generator-react.md | Generate React/Tailwind code | ✅ Active |
| code-generator-swiftui | @agents/code-generator-swiftui.md | Generate SwiftUI code | ✅ Active |
| code-generator-vue | @agents/code-generator-vue.md | Generate Vue 3 code | 🚧 Placeholder |
| code-generator-kotlin | @agents/code-generator-kotlin.md | Generate Kotlin Compose code | 🚧 Placeholder |
| compliance-checker | @agents/compliance-checker.md | Validate spec compliance | ✅ Active |
| font-manager | @agents/font-manager.md | Download and configure fonts | ✅ Active |

> **Note:** Vue and Kotlin generators are planned for future releases. Use React or SwiftUI generators for now.

## References (Lazy Load)

### Core References
| Topic | Path | Used By |
|-------|------|---------|
| Token Mapping | @skills/figma-to-code/references/token-mapping.md | code-generator-* |
| Common Issues | @skills/figma-to-code/references/common-issues.md | code-generator-* |
| Error Recovery | @skills/figma-to-code/references/error-recovery.md | all agents |

### Validation References
| Topic | Path | Used By |
|-------|------|---------|
| Validation Guide | @skills/figma-to-code/references/validation-guide.md | design-validator |
| Visual Validation | @skills/figma-to-code/references/visual-validation-loop.md | compliance-checker |
| Responsive Validation | @skills/figma-to-code/references/responsive-validation.md | compliance-checker |
| Accessibility Validation | @skills/figma-to-code/references/accessibility-validation.md | compliance-checker |
| QA Report Template | @skills/figma-to-code/references/qa-report-template.md | compliance-checker |

### Design Knowledge References
| Topic | Path | Used By |
|-------|------|---------|
| Gradient Handling | @skills/figma-to-code/references/gradient-handling.md | design-analyst, design-validator, code-generator-*, compliance-checker |
| Color Extraction | @skills/figma-to-code/references/color-extraction.md | design-analyst, design-validator, code-generator-*, compliance-checker |
| Opacity Extraction | @skills/figma-to-code/references/opacity-extraction.md | design-analyst, design-validator, code-generator-*, compliance-checker |
| Font Handling | @skills/figma-to-code/references/font-handling.md | design-analyst, code-generator-*, font-manager |
| Frame Properties | @skills/figma-to-code/references/frame-properties.md | design-analyst, design-validator, code-generator-*, compliance-checker |
| Text Decoration | @skills/figma-to-code/references/text-decoration.md | design-analyst, code-generator-* |
| Shadow & Blur Effects | @skills/figma-to-code/references/shadow-blur-effects.md | design-analyst, design-validator, code-generator-*, compliance-checker |
| Asset Node Mapping | @skills/figma-to-code/references/asset-node-mapping.md | design-analyst, code-generator-*, asset-manager |
| Illustration Detection | @skills/figma-to-code/references/illustration-detection.md | design-analyst, design-validator, code-generator-* |
| Image with Text | @skills/figma-to-code/references/image-with-text.md | design-analyst, design-validator |
| Layer Order & Hierarchy | @skills/figma-to-code/references/layer-order-hierarchy.md | design-analyst, code-generator-* |
| Accessibility Patterns | @skills/figma-to-code/references/accessibility-patterns.md | code-generator-*, compliance-checker |
| Responsive Patterns | @skills/figma-to-code/references/responsive-patterns.md | code-generator-*, compliance-checker |
| React Patterns (CVA, Utilities) | @skills/figma-to-code/references/react-patterns.md | code-generator-react |
| SwiftUI Patterns (Glass, Layer, Adaptive) | @skills/figma-to-code/references/swiftui-patterns.md | code-generator-swiftui |

### Development References
| Topic | Path | Used By |
|-------|------|---------|
| Code Connect Guide | @skills/figma-to-code/references/code-connect-guide.md | design-analyst |
| Figma MCP Server | @skills/figma-to-code/references/figma-mcp-server.md | all agents |
| Preview Setup | @skills/figma-to-code/references/preview-setup.md | compliance-checker |
| Test Generation | @skills/figma-to-code/references/test-generation.md | code-generator-* |
| Testing Strategy | @skills/figma-to-code/references/testing-strategy.md | code-generator-* |

### CI/CD & Integration
| Topic | Path | Used By |
|-------|------|---------|
| Storybook Integration | @skills/figma-to-code/references/storybook-integration.md | code-generator-react |
| CI/CD Integration | @skills/figma-to-code/references/ci-cd-integration.md | ⚠️ Not integrated (no agent uses this) |

## Prompt Templates

> **Note:** These prompt templates were designed for previous versions and are not currently used by any agent. Kept for reference.

| Template | Original Purpose | Status |
|----------|------------------|--------|
| analyze-design.md | Design analysis prompts | ⚠️ Unused |
| mapping-planning.md | Mapping & planning prompts | ⚠️ Unused |
| generate-component.md | Component generation prompts | ⚠️ Unused |
| validate-refine.md | Validation prompts | ⚠️ Unused |
| handoff.md | Handoff documentation | ⚠️ Unused |

**Active agents load references directly** — see the "References" section above.

## Examples & Templates

| Type | Path |
|------|------|
| Card Component Example | @skills/figma-to-code/assets/examples/card-component.md |
| Component Template | @skills/figma-to-code/assets/templates/component.tsx.hbs |
| Stories Template | @skills/figma-to-code/assets/templates/component.stories.tsx.hbs |
