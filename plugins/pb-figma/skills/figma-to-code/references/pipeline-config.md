# Pipeline Configuration Reference

> **Used by:** design-analyst, code-generator-*, compliance-pre-check, compliance-checker

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
| batch_size | 5 | Assets per API call |
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

### Compliance Tolerance

| Setting | Default | Description |
|---------|---------|-------------|
| typography_tolerance_px | 2 | Font size tolerance in pixels (±) |
| spacing_tolerance_px | 4 | Padding/margin tolerance in pixels (±) |
| color_tolerance_pct | 1 | Color match tolerance percentage |
| dimension_tolerance_px | 2 | Width/height tolerance in pixels (±) |
| corner_radius_exact | true | Corner radius must match exactly (no tolerance) |
| shadow_blur_tolerance_px | 2 | Shadow blur/spread tolerance in pixels (±) |
| opacity_tolerance_pct | 5 | Opacity tolerance percentage |

### Gate Orchestration

| Setting | Default | Description |
|---------|---------|-------------|
| gate_order | accessibility,responsive,visual | Order of gate execution (fail-fast) |
| fail_fast_enabled | true | Stop execution on first gate failure |
| max_visual_iterations | 3 | Maximum visual verification loop iterations |
| visual_improvement_threshold | 10 | Minimum % improvement between iterations to continue |
| stall_detection_enabled | true | Exit loop if improvement < threshold |

### Deterministic Pipeline Flags

| Flag | Default | Description |
|------|---------|-------------|
| FIGMA_PIPELINE_V2_ENABLED | false | Enables deterministic runner (shadow mode when false) |
| FIGMA_PIPELINE_V2_SCOPE | react | Active framework scope for v2 |
| FIGMA_PIPELINE_CACHE_ENABLED | true | Enables stage-level cache in `.qa/cache` |
| FIGMA_PIPELINE_VISUAL_MODE | hybrid | Visual gate mode (`hybrid`, `pixel`, `vision`) |
| FIGMA_PIPELINE_STRICT_PIXEL_DEFAULT | true | Default mode selection when caller omits explicit mode |
| FIGMA_PIPELINE_AUTO_RENDER_ENABLED | true | Auto-render implementation screenshot for visual gate |
| FIGMA_PIPELINE_TARGET_MATCH | 0.95 | Target visual match ratio |
| FIGMA_PIPELINE_MAX_VISUAL_ITER | 3 | Max visual gate iterations |
| FIGMA_PIPELINE_PASS_THRESHOLD | 95 | PASS threshold score for static/visual gates |
| FIGMA_PIPELINE_WARN_THRESHOLD | 85 | WARN threshold score for static/visual gates |

### Component Scoring

| Setting | Default | Description |
|---------|---------|-------------|
| structure_weight | 20 | Structure score weight (%) |
| token_weight | 30 | Design token score weight (%) |
| asset_weight | 10 | Asset score weight (%) |
| a11y_weight | 20 | Accessibility score weight (%) |
| responsive_weight | 10 | Responsive score weight (%) |
| visual_weight | 10 | Visual match score weight (%) |
| pass_score_threshold | 95 | Minimum score for PASS (%) |
| warn_score_threshold | 85 | Minimum score for WARN (%) |

### Framework-Specific Overrides

#### SwiftUI

| Setting | Value | Reason |
|---------|-------|--------|
| typography_tolerance_px | 1 | SwiftUI font rendering more precise |
| dimension_tolerance_px | 0 | Frame sizes explicit in code |
| spacing_tolerance_px | 2 | SwiftUI padding more precise |

#### React/Tailwind

| Setting | Value | Reason |
|---------|-------|--------|
| spacing_tolerance_px | 4 | Tailwind spacing scale (rem → px conversion) |
| typography_tolerance_px | 2 | Browser rendering variations |
| dimension_tolerance_px | 2 | Flexbox calculation variations |

### Incremental Checkpointing

| Setting | Default | Description |
|---------|---------|-------------|
| checkpoint_batch_size | 10 | Components per checkpoint write |
| checkpoint_on_gate_complete | true | Write checkpoint after each gate |
| auto_resume_on_restart | true | Prompt to resume from last checkpoint |
| checkpoint_retention_hours | 48 | Keep checkpoint files for N hours |

---

## Overriding Defaults

Agents should check the skill invocation prompt for configuration overrides. Format:

```
Task(subagent_type="pb-figma:compliance-checker",
     prompt="Validate... Config: { pass_threshold: 90%, breakpoints: [360, 768, 1280] }")
```

If no overrides specified, use defaults from this document.
