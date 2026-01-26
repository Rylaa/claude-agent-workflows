# pb-figma Documentation Index

> **Usage:** Bu dosya tüm pb-figma dokümantasyonunun haritasıdır.
> Agent'lar sadece ihtiyaç duydukları referansları @path ile yükler.

## Quick Start

- **Figma-to-Code Workflow:** @skills/figma-to-code/SKILL.md
- **Agent Pipeline:** @agents/README.md

## Agents

| Agent | Path | Purpose |
|-------|------|---------|
| design-validator | @agents/design-validator.md | Tasarım bütünlüğünü doğrula |
| design-analyst | @agents/design-analyst.md | Implementation spec oluştur |
| asset-manager | @agents/asset-manager.md | Asset'leri indir ve organize et |
| code-generator-react | @agents/code-generator-react.md | React/Tailwind kodu üret |
| code-generator-swiftui | @agents/code-generator-swiftui.md | SwiftUI kodu üret |
| code-generator-vue | @agents/code-generator-vue.md | Vue 3 kodu üret (v1.2.0) |
| code-generator-kotlin | @agents/code-generator-kotlin.md | Kotlin Compose kodu üret (v1.2.0) |
| compliance-checker | @agents/compliance-checker.md | Spec'e uyumu doğrula |
| font-manager | @agents/font-manager.md | Font'ları indir ve kur |

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
| CI/CD Integration | @skills/figma-to-code/references/ci-cd-integration.md | handoff |

## Prompt Templates

| Phase | Path | Used By |
|-------|------|---------|
| Analyze Design | @skills/figma-to-code/references/prompts/analyze-design.md | design-analyst |
| Mapping & Planning | @skills/figma-to-code/references/prompts/mapping-planning.md | design-analyst |
| Generate Component | @skills/figma-to-code/references/prompts/generate-component.md | code-generator-* |
| Validate & Refine | @skills/figma-to-code/references/prompts/validate-refine.md | compliance-checker |
| Handoff | @skills/figma-to-code/references/prompts/handoff.md | compliance-checker |

## Examples & Templates

| Type | Path |
|------|------|
| Card Component Example | @skills/figma-to-code/assets/examples/card-component.md |
| Component Template | @skills/figma-to-code/assets/templates/component.tsx.hbs |
| Stories Template | @skills/figma-to-code/assets/templates/component.stories.tsx.hbs |
