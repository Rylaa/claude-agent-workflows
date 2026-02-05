# Checkpoint Schema Reference

> **Used by:** compliance-checker (v2.0+)

This document defines the checkpoint file format for incremental progress tracking and resume support in Phase 5: Compliance Checker.

---

## Purpose

Checkpoints enable:
1. **Interruption Recovery:** Resume from last completed batch on restart
2. **Progress Tracking:** Monitor compliance run progress in real-time
3. **Debugging:** Inspect intermediate state when issues occur
4. **Audit Trail:** Record compliance run history and results

---

## File Location

Checkpoints are written to: `.qa/checkpoint-5-compliance-checker.json`

**Directory creation:**
```bash
mkdir -p .qa
```

---

## Schema Versions

### v2.0 - Complete Checkpoint (Final State)

Written when compliance checking finishes successfully.

```json
{
  "phase": 5,
  "agent": "compliance-checker",
  "version": "2.0",
  "status": "complete",
  "output_file": "docs/figma-reports/{file_key}-final.md",
  "overall_status": "PASS|WARN|FAIL",
  "overall_score": 97.5,
  "timestamp": "2026-02-05T14:32:15Z",

  "gate_results": {
    "accessibility": {
      "status": "PASS",
      "duration_ms": 2340,
      "score": 100,
      "checks_run": ["jest-axe", "semantic-html", "aria-labels", "focus-states"],
      "violations": []
    },
    "responsive": {
      "status": "PASS",
      "duration_ms": 4820,
      "score": 100,
      "breakpoints_tested": ["375px", "768px", "1440px"],
      "passing_breakpoints": 3,
      "failing_breakpoints": 0
    },
    "visual": {
      "status": "PASS",
      "duration_ms": 12150,
      "score": 98,
      "iterations": 1,
      "final_match_pct": 98,
      "stalled": false,
      "user_aborted": false
    }
  },

  "component_scores": [
    {
      "name": "HeroCard",
      "file_path": "src/components/HeroCard.tsx",
      "structure_score": 100,
      "token_score": 95,
      "asset_score": 100,
      "a11y_score": 100,
      "responsive_score": 100,
      "visual_score": 98,
      "overall_score": 98.3,
      "status": "PASS"
    },
    {
      "name": "Button",
      "file_path": "src/components/Button.tsx",
      "structure_score": 100,
      "token_score": 90,
      "asset_score": 100,
      "a11y_score": 100,
      "responsive_score": 67,
      "visual_score": 92,
      "overall_score": 91.5,
      "status": "WARN"
    }
  ],

  "config_used": {
    "typography_tolerance_px": 2,
    "spacing_tolerance_px": 4,
    "color_tolerance_pct": 1,
    "pass_score_threshold": 95,
    "warn_score_threshold": 85,
    "fail_fast_enabled": true,
    "max_visual_iterations": 3,
    "visual_improvement_threshold": 10
  },

  "performance": {
    "total_duration_ms": 19310,
    "pre_flight_ms": 420,
    "static_checks_ms": 1540,
    "gate_total_ms": 19310,
    "reporting_ms": 870
  }
}
```

---

### v2.0 - Incremental Checkpoint (In-Progress State)

Written after each batch during long-running compliance runs.

```json
{
  "phase": 5,
  "agent": "compliance-checker",
  "version": "2.0",
  "status": "in_progress",
  "current_batch": 2,
  "total_batches": 5,
  "completed_components": [
    "Component1",
    "Component2",
    "Component3",
    "Component4",
    "Component5",
    "Component6",
    "Component7",
    "Component8",
    "Component9",
    "Component10"
  ],
  "pending_components": [
    "Component11",
    "Component12",
    "...",
    "Component50"
  ],
  "last_checkpoint": "2026-02-05T14:32:15Z",

  "gates_completed": ["accessibility", "responsive"],
  "gates_pending": ["visual"],

  "partial_results": {
    "passed": 8,
    "warned": 2,
    "failed": 0,
    "total_checked": 10
  },

  "partial_scores": [
    {
      "name": "Component1",
      "overall_score": 98.5,
      "status": "PASS"
    },
    {
      "name": "Component2",
      "overall_score": 87.2,
      "status": "WARN"
    }
  ],

  "resume_data": {
    "last_completed_component": "Component10",
    "next_component_index": 10,
    "static_checks_complete": true,
    "gate_1_complete": true,
    "gate_2_complete": true,
    "gate_3_complete": false
  }
}
```

---

## Field Definitions

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `phase` | number | ✅ | Always 5 (Phase 5: Compliance Checker) |
| `agent` | string | ✅ | Always "compliance-checker" |
| `version` | string | ✅ | Checkpoint schema version (e.g., "2.0") |
| `status` | string | ✅ | "in_progress" or "complete" |
| `output_file` | string | ✅ | Path to final report (complete only) |
| `overall_status` | string | ✅ | "PASS", "WARN", or "FAIL" (complete only) |
| `overall_score` | number | ✅ | Overall compliance score 0-100 (complete only) |
| `timestamp` | string | ✅ | ISO-8601 timestamp of checkpoint write |

### Gate Results (complete only)

Each gate has:

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "PASS", "WARN", or "FAIL" |
| `duration_ms` | number | Gate execution time in milliseconds |
| `score` | number | Gate score 0-100 |
| `checks_run` | array | List of checks executed |
| `violations` | array | List of violations found (empty if pass) |

**Gate-Specific Fields:**

**Accessibility:**
- `checks_run`: ["jest-axe", "semantic-html", "aria-labels", "focus-states", "color-contrast"]
- `violations`: Array of jest-axe violation objects

**Responsive:**
- `breakpoints_tested`: ["375px", "768px", "1440px"]
- `passing_breakpoints`: Number of passing breakpoints (0-3)
- `failing_breakpoints`: Number of failing breakpoints

**Visual:**
- `iterations`: Number of visual validation iterations run (1-3)
- `final_match_pct`: Final visual match percentage
- `stalled`: Boolean indicating if loop exited due to stall detection
- `user_aborted`: Boolean indicating if user manually aborted

### Component Scores

Array of component score objects:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Component name |
| `file_path` | string | Path to component file |
| `structure_score` | number | Structure check score 0-100 |
| `token_score` | number | Design token score 0-100 |
| `asset_score` | number | Asset integration score 0-100 |
| `a11y_score` | number | Accessibility score (0 or 100) |
| `responsive_score` | number | Responsive score 0-100 |
| `visual_score` | number | Visual match score 0-100 |
| `overall_score` | number | Weighted average score |
| `status` | string | "PASS", "WARN", or "FAIL" |

### Config Used

Records the configuration values used during the run:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `typography_tolerance_px` | number | 2 | Font size tolerance |
| `spacing_tolerance_px` | number | 4 | Spacing tolerance |
| `color_tolerance_pct` | number | 1 | Color match tolerance |
| `pass_score_threshold` | number | 95 | Minimum score for PASS |
| `warn_score_threshold` | number | 85 | Minimum score for WARN |
| `fail_fast_enabled` | boolean | true | Fail-fast gate orchestration |
| `max_visual_iterations` | number | 3 | Max visual loop iterations |
| `visual_improvement_threshold` | number | 10 | Stall detection threshold |

### Incremental Checkpoint Fields

| Field | Type | Description |
|-------|------|-------------|
| `current_batch` | number | Current batch number (1-indexed) |
| `total_batches` | number | Total number of batches |
| `completed_components` | array | Components already checked |
| `pending_components` | array | Components not yet checked |
| `gates_completed` | array | Gates that have finished |
| `gates_pending` | array | Gates not yet run |
| `partial_results` | object | Intermediate pass/warn/fail counts |
| `resume_data` | object | State needed to resume execution |

---

## Usage Patterns

### Writing Complete Checkpoint

```typescript
// After compliance run completes
const checkpoint = {
  phase: 5,
  agent: "compliance-checker",
  version: "2.0",
  status: "complete",
  output_file: `docs/figma-reports/${file_key}-final.md`,
  overall_status: calculateOverallStatus(),
  overall_score: calculateOverallScore(),
  timestamp: new Date().toISOString(),
  gate_results: gatherGateResults(),
  component_scores: gatherComponentScores(),
  config_used: loadedConfig,
  performance: gatherPerformanceMetrics()
};

Write(".qa/checkpoint-5-compliance-checker.json", JSON.stringify(checkpoint, null, 2));
```

### Writing Incremental Checkpoint

```typescript
// After each batch (every 10 components by default)
const checkpoint = {
  phase: 5,
  agent: "compliance-checker",
  version: "2.0",
  status: "in_progress",
  current_batch: currentBatch,
  total_batches: totalBatches,
  completed_components: completedComponents,
  pending_components: pendingComponents,
  last_checkpoint: new Date().toISOString(),
  gates_completed: completedGates,
  gates_pending: pendingGates,
  partial_results: {
    passed: passedCount,
    warned: warnedCount,
    failed: failedCount,
    total_checked: completedComponents.length
  },
  partial_scores: gatherPartialScores(),
  resume_data: {
    last_completed_component: completedComponents[completedComponents.length - 1],
    next_component_index: completedComponents.length,
    static_checks_complete: staticChecksComplete,
    gate_1_complete: gate1Complete,
    gate_2_complete: gate2Complete,
    gate_3_complete: gate3Complete
  }
};

Write(".qa/checkpoint-5-compliance-checker.json", JSON.stringify(checkpoint, null, 2));
```

### Reading and Resuming

```typescript
// On agent start
const checkpointPath = ".qa/checkpoint-5-compliance-checker.json";

if (fileExists(checkpointPath)) {
  const checkpoint = JSON.parse(Read(checkpointPath));

  if (checkpoint.status === "in_progress") {
    // Prompt user to resume
    const resume = AskUserQuestion({
      questions: [{
        question: `Resume from batch ${checkpoint.current_batch}/${checkpoint.total_batches}?`,
        header: "Resume",
        options: [
          { label: "Yes, resume", description: `Continue from component ${checkpoint.resume_data.last_completed_component}` },
          { label: "No, start fresh", description: "Discard checkpoint and start over" }
        ],
        multiSelect: false
      }]
    });

    if (resume === "Yes, resume") {
      // Load resume data
      const componentsToCheck = checkpoint.pending_components;
      const completedComponents = checkpoint.completed_components;
      const gatesCompleted = checkpoint.gates_completed;

      // Skip to pending work
      startFromIndex(checkpoint.resume_data.next_component_index);
    } else {
      // Overwrite checkpoint
      startFresh();
    }
  } else {
    // Previous run complete, start fresh
    startFresh();
  }
} else {
  // No checkpoint, start fresh
  startFresh();
}
```

---

## Checkpoint Retention

**Retention Policy (from pipeline-config.md):**
- `checkpoint_retention_hours`: 48 (default)

**Cleanup:**
```bash
# Remove checkpoints older than 48 hours
find .qa -name "checkpoint-*.json" -mtime +2 -delete
```

---

## Validation

**Schema Validation:**
```typescript
function validateCheckpoint(checkpoint: any): boolean {
  // Required top-level fields
  if (!checkpoint.phase || checkpoint.phase !== 5) return false;
  if (!checkpoint.agent || checkpoint.agent !== "compliance-checker") return false;
  if (!checkpoint.version || checkpoint.version !== "2.0") return false;
  if (!checkpoint.status || !["in_progress", "complete"].includes(checkpoint.status)) return false;
  if (!checkpoint.timestamp) return false;

  // Status-specific validation
  if (checkpoint.status === "complete") {
    if (!checkpoint.overall_status) return false;
    if (!checkpoint.overall_score) return false;
    if (!checkpoint.gate_results) return false;
    if (!checkpoint.component_scores) return false;
  }

  if (checkpoint.status === "in_progress") {
    if (!checkpoint.current_batch) return false;
    if (!checkpoint.total_batches) return false;
    if (!checkpoint.pending_components) return false;
  }

  return true;
}
```

---

## Migration from v1.0

**v1.0 Checkpoint (Legacy):**
```json
{
  "phase": 5,
  "agent": "compliance-checker",
  "status": "complete",
  "output_file": "docs/figma-reports/{file_key}-final.md",
  "overall_status": "PASS",
  "timestamp": "2026-02-05T14:32:15Z"
}
```

**v2.0 Enhancements:**
- ✅ Added `version` field
- ✅ Added `overall_score` (granular scoring)
- ✅ Added `gate_results` (detailed gate execution)
- ✅ Added `component_scores` (per-component breakdown)
- ✅ Added `config_used` (reproducibility)
- ✅ Added `performance` metrics
- ✅ Added `in_progress` status (incremental checkpoints)
- ✅ Added `resume_data` (interruption recovery)

**Backward Compatibility:**
- Agents should check for `version` field
- If missing → treat as v1.0 (complete only, no scores)
- If v2.0 → full checkpoint support

---

## Examples

### Example 1: All Gates Pass

```json
{
  "phase": 5,
  "agent": "compliance-checker",
  "version": "2.0",
  "status": "complete",
  "output_file": "docs/figma-reports/ABC123-final.md",
  "overall_status": "PASS",
  "overall_score": 98.3,
  "timestamp": "2026-02-05T14:45:30Z",
  "gate_results": {
    "accessibility": { "status": "PASS", "score": 100 },
    "responsive": { "status": "PASS", "score": 100 },
    "visual": { "status": "PASS", "score": 98 }
  }
}
```

### Example 2: Accessibility Fails (Fail-Fast)

```json
{
  "phase": 5,
  "agent": "compliance-checker",
  "version": "2.0",
  "status": "complete",
  "overall_status": "FAIL",
  "overall_score": 67.2,
  "gate_results": {
    "accessibility": {
      "status": "FAIL",
      "score": 0,
      "violations": [
        { "id": "image-alt", "impact": "critical", "nodes": [...] }
      ]
    },
    "responsive": { "status": "SKIPPED", "score": null },
    "visual": { "status": "SKIPPED", "score": null }
  }
}
```

### Example 3: In-Progress (Batch 2/5)

```json
{
  "phase": 5,
  "agent": "compliance-checker",
  "version": "2.0",
  "status": "in_progress",
  "current_batch": 2,
  "total_batches": 5,
  "completed_components": ["Component1", "...", "Component10"],
  "pending_components": ["Component11", "...", "Component50"],
  "partial_results": {
    "passed": 8,
    "warned": 2,
    "failed": 0
  }
}
```

---

## Troubleshooting

### Checkpoint Corrupted

**Symptoms:** JSON parse error when reading checkpoint

**Fix:**
```bash
# Backup corrupted checkpoint
mv .qa/checkpoint-5-compliance-checker.json .qa/checkpoint-5-corrupted-backup.json

# Start fresh (checkpoint will be regenerated)
```

### Checkpoint Out of Sync

**Symptoms:** Resume attempts to check already-checked components

**Fix:**
```bash
# Remove checkpoint and restart
rm .qa/checkpoint-5-compliance-checker.json
```

### Performance Issues

**Symptoms:** Checkpoint writes slow down execution

**Fix:** Increase `checkpoint_batch_size` in `pipeline-config.md`:
```markdown
checkpoint_batch_size: 20  # Write less frequently
```

---

**Version:** 2.0
**Last Updated:** 2026-02-05
