# Illustration Detection Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automatically detect complex illustrations that should be downloaded as images rather than coded, using a two-stage system: fast complexity triggers + LLM vision analysis.

**Architecture:** Stage 1 uses rule-based heuristics to flag potentially complex frames (shadow+color siblings, multiple opacity fills, gradient overlays, high vector count). Stage 2 sends flagged frames to Claude vision for final decision: "illustration (download)" vs "codeable UI (generate)".

**Tech Stack:** Figma MCP tools, Claude vision API (via agent prompt), Markdown agent files

---

## Task 1: Add Complexity Triggers to design-validator.md

**Files:**
- Modify: `plugins/pb-figma/agents/design-validator.md`

**Step 1: Read current design-validator.md structure**

```bash
head -100 plugins/pb-figma/agents/design-validator.md
```

Understand where asset validation logic exists.

**Step 2: Add Complexity Detection section**

Add after the existing asset detection logic:

```markdown
### 2.3 Illustration Complexity Detection

**Purpose:** Flag frames that may be illustrations requiring LLM vision analysis.

**Complexity Triggers (if ANY match → flag for LLM review):**

| Trigger | Detection Method | Example |
|---------|------------------|---------|
| **Shadow + Color Siblings** | Frame has 2+ child frames where one has dark fills (#000-#444) and another has bright fills | Growth chart: 6:34 (black) + 6:38 (yellow) |
| **Multiple Opacity Fills** | Frame children have same color but 3+ different opacity values | Bars: 0.2, 0.4, 0.6, 0.8, 1.0 |
| **Gradient Overlay** | Vector child with gradient ending in opacity 0 | Trend arrow: white@10% → white@0% |
| **High Vector Count** | Frame contains >10 VECTOR type descendants | Complex illustration with many paths |
| **Deep Nesting** | Frame nesting depth > 3 levels | Frame > Frame > Frame > Frame |

**Detection Process:**

```
For each frame in Assets Required:
1. Query frame details: figma_get_node_details(file_key, node_id)
2. Check children count and types
3. For each trigger:
   a. Shadow+Color: Query sibling fills, check luminosity difference
   b. Multiple Opacity: Collect opacity values from children fills
   c. Gradient Overlay: Check for gradient with opacity → 0 stop
   d. Vector Count: Count VECTOR type descendants
   e. Deep Nesting: Track frame depth recursively
4. If ANY trigger matches:
   → Add to "Flagged for LLM Review" list
   → Include trigger reason
```

**Output Format:**

Add to Validation Report:

```markdown
## Flagged for LLM Review

| Node ID | Name | Trigger | Reason |
|---------|------|---------|--------|
| 6:32 | GrowthSection | Shadow+Color Siblings | Children 6:34 (dark) and 6:38 (bright) detected |
| 6:32 | GrowthSection | Multiple Opacity | 5 opacity values: 0.2, 0.4, 0.6, 0.8, 1.0 |
| 6:32 | GrowthSection | Gradient Overlay | Child 6:44 has transparent gradient |
```
```

**Step 3: Verify markdown syntax**

```bash
# Check file is valid markdown
head -50 plugins/pb-figma/agents/design-validator.md
```

**Step 4: Commit**

```bash
git add plugins/pb-figma/agents/design-validator.md
git commit -m "feat(design-validator): add illustration complexity triggers"
```

---

## Task 2: Add Shadow+Color Sibling Detection Logic

**Files:**
- Modify: `plugins/pb-figma/agents/design-validator.md`

**Step 1: Add detailed detection algorithm**

Add under the Complexity Triggers section:

```markdown
#### 2.3.1 Shadow+Color Sibling Detection

**Algorithm:**

```
1. Get frame children list
2. For each pair of sibling frames (A, B):
   a. Query A's children fills → extract hex colors
   b. Query B's children fills → extract hex colors
   c. Calculate luminosity for each:
      - luminosity = (R + G + B) / 3 / 255
      - DARK if luminosity < 0.27 (#000000-#444444 range)
      - BRIGHT if luminosity > 0.5 AND has saturation > 20%
   d. If A is DARK and B is BRIGHT (or vice versa):
      → TRIGGER: Shadow+Color Siblings
      → Record: "Dark frame: {A.id}, Bright frame: {B.id}"
```

**Luminosity Calculation:**

```python
def is_dark(hex_color):
    # Remove # prefix
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    luminosity = (r + g + b) / 3 / 255
    return luminosity < 0.27  # Below #444444

def is_bright(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    luminosity = (r + g + b) / 3 / 255
    # Check saturation (not grayscale)
    max_c, min_c = max(r, g, b), min(r, g, b)
    saturation = (max_c - min_c) / 255
    return luminosity > 0.5 and saturation > 0.2
```

**Example:**

```
Frame 6:32 children: [6:33, 6:34, 6:38, 6:44]

Check 6:34 vs 6:38:
- 6:34 children fills: #3c3c3c (luminosity: 0.24) → DARK ✓
- 6:38 children fills: #f2f20d (luminosity: 0.65, saturation: 0.90) → BRIGHT ✓
- Result: TRIGGER MATCHED

Record: "Shadow+Color Siblings: 6:34 (dark) paired with 6:38 (bright)"
```
```

**Step 2: Commit**

```bash
git add plugins/pb-figma/agents/design-validator.md
git commit -m "feat(design-validator): add shadow+color sibling detection algorithm"
```

---

## Task 3: Add Multiple Opacity Detection Logic

**Files:**
- Modify: `plugins/pb-figma/agents/design-validator.md`

**Step 1: Add opacity detection algorithm**

```markdown
#### 2.3.2 Multiple Opacity Fills Detection

**Algorithm:**

```
1. Get frame children list
2. Collect all fill opacity values from children:
   opacity_values = []
   for child in children:
       for fill in child.fills:
           if fill.opacity < 1.0:
               opacity_values.append(fill.opacity)
3. Remove duplicates and sort
4. If unique opacity count >= 3:
   → TRIGGER: Multiple Opacity Fills
   → Record opacity values
```

**Example:**

```
Frame 6:38 children fills:
- 6:39: #f2f20d opacity 0.2
- 6:40: #f2f20d opacity 0.4
- 6:41: #f2f20d opacity 0.6
- 6:42: #f2f20d opacity 0.8
- 6:43: #f2f20d opacity 1.0

Unique opacity values: [0.2, 0.4, 0.6, 0.8, 1.0] → 5 values >= 3
Result: TRIGGER MATCHED

Record: "Multiple Opacity: 5 values [0.2, 0.4, 0.6, 0.8, 1.0]"
```

**Note:** Same color with multiple opacities often indicates gradient-like decorative effect, not functional UI.
```

**Step 2: Commit**

```bash
git add plugins/pb-figma/agents/design-validator.md
git commit -m "feat(design-validator): add multiple opacity detection algorithm"
```

---

## Task 4: Add Gradient Overlay Detection Logic

**Files:**
- Modify: `plugins/pb-figma/agents/design-validator.md`

**Step 1: Add gradient overlay detection**

```markdown
#### 2.3.3 Gradient Overlay Detection

**Algorithm:**

```
1. For each child in frame:
   a. Check if child is VECTOR type
   b. Check if child has GRADIENT fill (LINEAR, RADIAL, or ANGULAR)
   c. Examine gradient stops:
      - Look for stop with opacity approaching 0 (< 0.1)
      - Look for stop with opacity > 0.05 at different position
   d. If gradient fades to transparent:
      → TRIGGER: Gradient Overlay
      → Record gradient details
```

**Detection Pattern:**

```
Gradient stops indicating overlay:
- Stop 1: color@0.1 (10% opacity)
- Stop 2: color@0.0 (0% opacity)

This creates a "fade out" effect typical of decorative overlays.
```

**Example:**

```
Node 6:44 (VECTOR):
- Fill: GRADIENT_LINEAR
- Stops:
  - position 0.0: rgba(255,255,255,0.1)  → 10% opacity
  - position 1.0: rgba(255,255,255,0.0)  → 0% opacity

Gradient fades from 10% to 0% → TRIGGER MATCHED

Record: "Gradient Overlay: 6:44 fades white from 10% to 0%"
```
```

**Step 2: Commit**

```bash
git add plugins/pb-figma/agents/design-validator.md
git commit -m "feat(design-validator): add gradient overlay detection algorithm"
```

---

## Task 5: Add LLM Vision Analysis to asset-manager.md

**Files:**
- Modify: `plugins/pb-figma/agents/asset-manager.md`

**Step 1: Read current asset-manager structure**

```bash
grep -n "### 2" plugins/pb-figma/agents/asset-manager.md | head -10
```

Find where to add LLM analysis section.

**Step 2: Add LLM Vision Analysis section**

Add after section 2.1.1 (Composite Illustration Detection):

```markdown
#### 2.1.2 LLM Vision Analysis for Flagged Frames

**Purpose:** Use Claude vision to make final decision on frames flagged by design-validator complexity triggers.

**When to Use:** Only for frames listed in "Flagged for LLM Review" section of the Implementation Spec.

**Process:**

```
1. Check Implementation Spec for "Flagged for LLM Review" table
2. For each flagged frame:
   a. Take screenshot: figma_get_screenshot(file_key, node_id)
   b. Analyze with vision prompt (see below)
   c. Record decision in spec
3. Apply decision to download strategy
```

**Vision Analysis Prompt:**

When analyzing a flagged frame, use this reasoning structure:

```
I'm looking at this Figma frame screenshot to determine if it should be:
A) Downloaded as an image (illustration/decorative)
B) Generated as code (UI component)

**Analysis Criteria:**

1. **Visual Complexity:**
   - Does it have overlapping decorative layers?
   - Are there effects that would be hard to replicate in code?
   - Is it a stylized graphic rather than standard UI?

2. **Data Representation:**
   - Does it show real/dynamic data? → Code it (data can change)
   - Is it purely decorative/conceptual? → Download it

3. **Interactivity Potential:**
   - Would users interact with individual parts? → Code it
   - Is it a static visual element? → Download it

4. **Code Complexity Estimate:**
   - Would coding this take >50 lines? → Consider downloading
   - Is it achievable with simple shapes/gradients? → Code it

**My Decision:** [DOWNLOAD_AS_IMAGE | GENERATE_AS_CODE]
**Reason:** [1-2 sentence explanation]
```

**Decision Recording:**

Update the flagged frame entry in spec:

```markdown
## Flagged Frames - LLM Decisions

| Node ID | Name | Decision | Reason |
|---------|------|----------|--------|
| 6:32 | GrowthSection | DOWNLOAD_AS_IMAGE | Decorative chart with shadow+color overlay effects, not representing real data |
```

**Download Strategy Based on Decision:**

| Decision | Action |
|----------|--------|
| DOWNLOAD_AS_IMAGE | Use `figma_get_screenshot` at 2x scale, save as PNG |
| GENERATE_AS_CODE | Pass to code-generator, exclude from asset downloads |
```

**Step 3: Commit**

```bash
git add plugins/pb-figma/agents/asset-manager.md
git commit -m "feat(asset-manager): add LLM vision analysis for flagged illustrations"
```

---

## Task 6: Add Flagged Frame Reading Logic to asset-manager.md

**Files:**
- Modify: `plugins/pb-figma/agents/asset-manager.md`

**Step 1: Add spec reading instruction**

Add to the "Input" section or create new subsection:

```markdown
### Reading Flagged Frames from Spec

Before processing assets, check for flagged frames:

```
1. Read Implementation Spec
2. Look for "## Flagged for LLM Review" section
3. If section exists AND has entries:
   → Process each flagged frame with LLM Vision Analysis (2.1.2)
   → Record decisions
4. If section doesn't exist or is empty:
   → Proceed with normal asset classification
```

**Spec Section to Look For:**

```markdown
## Flagged for LLM Review

| Node ID | Name | Trigger | Reason |
|---------|------|---------|--------|
| 6:32 | GrowthSection | Shadow+Color Siblings | ... |
```

**If Found:**
- Extract Node IDs from table
- Run LLM Vision Analysis for each
- Add decisions to "Flagged Frames - LLM Decisions" table
- Use decisions in download strategy
```

**Step 2: Commit**

```bash
git add plugins/pb-figma/agents/asset-manager.md
git commit -m "feat(asset-manager): add flagged frame reading from spec"
```

---

## Task 7: Update design-analyst.md to Pass Flags Through

**Files:**
- Modify: `plugins/pb-figma/agents/design-analyst.md`

**Step 1: Add instruction to preserve flagged frames**

Add to the output section:

```markdown
### Preserving Flagged Frames

When creating Implementation Spec, if Validation Report contains "Flagged for LLM Review" section:

1. **Copy the entire section** to Implementation Spec
2. Keep all columns: Node ID, Name, Trigger, Reason
3. Place after "Assets Required" section
4. Do NOT make decisions here - asset-manager will use LLM vision

**Example:**

From Validation Report:
```markdown
## Flagged for LLM Review
| Node ID | Name | Trigger | Reason |
|---------|------|---------|--------|
| 6:32 | GrowthSection | Shadow+Color Siblings | Dark 6:34 + Bright 6:38 |
```

Copy to Implementation Spec as-is.
```

**Step 2: Commit**

```bash
git add plugins/pb-figma/agents/design-analyst.md
git commit -m "feat(design-analyst): preserve flagged frames in implementation spec"
```

---

## Task 8: Test the Full Flow with 6:32

**Files:**
- No file changes - manual testing

**Step 1: Simulate design-validator complexity check**

Use MCP to check if 6:32 would trigger:

```
figma_get_node_details(file_key, "6:32")
figma_get_node_details(file_key, "6:34")  # Check for dark fills
figma_get_node_details(file_key, "6:38")  # Check for bright fills
figma_get_node_details(file_key, "6:44")  # Check for gradient overlay
```

Verify triggers match expected:
- Shadow+Color Siblings: 6:34 + 6:38 ✓
- Gradient Overlay: 6:44 ✓

**Step 2: Simulate LLM vision analysis**

```
figma_get_screenshot(file_key, "6:32")
```

Apply vision analysis prompt mentally/manually:
- Expected decision: DOWNLOAD_AS_IMAGE
- Reason: Decorative growth chart, shadow+color effects, not real data

**Step 3: Verify download would be correct**

```
figma_get_screenshot(file_key, "6:32", scale=2)
```

Confirm screenshot captures the complete illustration correctly.

**Step 4: Document test results**

Add to plan file or create test report showing:
- Triggers detected correctly
- LLM decision matches expected
- Downloaded image is correct

---

## Summary

| Task | Component | Purpose |
|------|-----------|---------|
| 1 | design-validator | Add complexity trigger framework |
| 2 | design-validator | Shadow+Color sibling detection |
| 3 | design-validator | Multiple opacity detection |
| 4 | design-validator | Gradient overlay detection |
| 5 | asset-manager | LLM vision analysis integration |
| 6 | asset-manager | Flagged frame reading from spec |
| 7 | design-analyst | Pass flags through to spec |
| 8 | Manual test | Verify full flow with 6:32 |

**After Implementation:**

The pipeline will:
1. **design-validator**: Detect complex frames → Flag for review
2. **design-analyst**: Pass flags to Implementation Spec
3. **asset-manager**: Run LLM vision on flagged frames → Download or generate
4. **code-generator**: Skip downloaded illustrations, generate UI components

---

## Task 8 Test Results (2026-01-27)

### Trigger Detection Results

| Trigger | Status | Details |
|---------|--------|---------|
| **Gradient Overlay** | ✅ MATCHED | Node 6:44: `LINEAR Gradient rgba(255,255,255,0.10) → rgba(255,255,255,0.00)` |
| **Dark+Bright Siblings** | ✅ MATCHED | 6:34 (dark #3c3c3c, luminosity 0.24) + 6:38 (bright #f2f20d, luminosity 0.65) |

### LLM Vision Analysis Simulation

**Node:** 6:32 (GrowthSection)

**Analysis:**
1. **Visual Complexity:** Overlapping decorative layers (black shadow bars + yellow primary bars), 3D shadow effect
2. **Data Representation:** Purely decorative/conceptual, not real data
3. **Interactivity:** Static visual element, no user interaction expected
4. **Code Complexity:** >50 lines estimated, complex shadow/overlay effects

**Decision:** `DOWNLOAD_AS_IMAGE`
**Reason:** Decorative growth chart with overlapping shadow/color bar layers and gradient overlay. Not representing real data.

### Screenshot Verification

- Screenshot captured at 2x scale: ✅
- Complete illustration visible: ✅
- All visual elements preserved: ✅

### Conclusion

**Full flow test PASSED.** The complexity triggers correctly identified node 6:32 as requiring LLM review, and the vision analysis correctly determined it should be downloaded as an image rather than generated as code.
