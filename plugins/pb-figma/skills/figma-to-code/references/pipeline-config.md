# Pipeline Configuration Reference

> **Used by:** design-analyst, code-generator-*, compliance-checker

This document defines configurable values used across the pipeline. When the skill file or user specifies overrides, agents should use those values instead of defaults.

---

## Default Configuration

### Responsive Breakpoints

| Name | Width | Usage |
|------|-------|-------|
| mobile | 375px | Primary mobile viewport |
| tablet | 768px | Tablet/iPad viewport |
| desktop | 1440px | Desktop viewport |

### Visual Validation

| Setting | Default | Description |
|---------|---------|-------------|
| pass_threshold | 95% | Minimum visual match % for PASS |
| warn_threshold | 85% | Minimum visual match % for WARN |
| screenshot_scale | 2x | Figma screenshot scale factor |

### Asset Processing

| Setting | Default | Description |
|---------|---------|-------------|
| batch_size | 10 | Assets per API call |
| retry_count | 3 | Max retries per failed operation |
| retry_base_delay | 1s | Initial retry delay (exponential backoff) |
| rate_limit_delay | 2s | Delay between MCP calls |

### Asset Classification

| Setting | Default | Description |
|---------|---------|-------------|
| icon_max_size | 48px | Max dimension for icon classification |
| illustration_min_size | 50px | Min dimension for illustration classification |
| vector_complexity_threshold | 10 | Vector paths triggering complexity review |

### Accessibility

| Setting | Default | Description |
|---------|---------|-------------|
| min_touch_target | 44px | Minimum touch target size (mobile) |
| contrast_ratio_normal | 4.5 | WCAG AA contrast ratio for normal text |
| contrast_ratio_large | 3.0 | WCAG AA contrast ratio for large text |

---

## Overriding Defaults

Agents should check the skill invocation prompt for configuration overrides. Format:

```
Task(subagent_type="pb-figma:compliance-checker",
     prompt="Validate... Config: { pass_threshold: 90%, breakpoints: [360, 768, 1280] }")
```

If no overrides specified, use defaults from this document.
