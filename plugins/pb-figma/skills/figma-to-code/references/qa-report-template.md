# QA Report Template (Claude Vision)

Bu şablon, Phase 4 Visual Validation sonrasında `.qa/report.md` dosyası için kullanılır.

> **Not:** Bu template Claude Vision yaklaşımını kullanır. RMSE/ImageMagick metodolojisi kullanılmaz.
> Detaylar için `visual-validation-loop.md` dosyasına bakın.

---

## Şablon: .qa/report.md

```markdown
# QA Validation Report (Claude Vision)

**Component:** [ComponentName]
**Date:** [YYYY-MM-DD HH:MM:SS]
**Validation Method:** Claude Vision
**Iterations:** [N/3]
**Status:** ✅ PASS / ⚠️ ACCEPTABLE / ❌ MANUAL REVIEW

---

## Summary

| Metric | Value |
|--------|-------|
| Validation Method | Claude Vision |
| Iterations Used | N/3 |
| Final Status | [PASS / ACCEPTABLE / MANUAL REVIEW] |
| Categories Checked | Typography, Spacing, Colors, Layout, Assets |

---

## Screenshots

| Type | Location | Notes |
|------|----------|-------|
| Figma Reference | `.qa/reference.png` | Figma MCP screenshot |
| Iteration 1 | `.qa/iteration-1.png` | Initial implementation |
| Iteration 2 | `.qa/iteration-2.png` | After first fixes |
| Iteration 3 | `.qa/iteration-3.png` | After second fixes (if needed) |
| Final | `.qa/implementation.png` | Final browser screenshot |

---

## Tolerance Criteria

| Category | Tolerance | Notes |
|----------|-----------|-------|
| Typography | ±2px font-size, exact weight/family | font-rendering farklılıkları kabul edilir |
| Spacing | ±4px padding/margin/gap | Subpixel farklılıklar kabul edilir |
| Colors | Exact match | Hex değerleri birebir eşleşmeli |
| Layout | Exact match | Flex direction, alignment, justify |
| Assets | Exact match | Icon size, color, border-radius |

---

## Iteration History

| # | Status | Differences Found | Fixes Applied |
|---|--------|-------------------|---------------|
| 1 | ❌ FAIL | [N differences] | Initial implementation |
| 2 | ⚠️ PARTIAL | [N differences] | [List of Tailwind fixes] |
| 3 | ✅ PASS | 0 differences | [List of final fixes] |

---

## Iteration 1 Analysis

**Screenshot:** `.qa/iteration-1.png`

### Claude Vision Comparison

| Category | Element | Figma | Implementation | Tailwind Fix |
|----------|---------|-------|----------------|--------------|
| Typography | Title | 32px bold | 28px medium | `text-3xl font-bold` |
| Typography | Description | 16px gray-500 | 14px gray-400 | `text-base text-gray-500` |
| Spacing | Card padding | 24px | 16px | `p-6` |
| Colors | Button bg | #FE4601 | #3B82F6 | `bg-orange-1` |

### TodoWrite Items Created

```
□ Title font-size: text-2xl → text-3xl
□ Title font-weight: font-medium → font-bold
□ Description text: text-sm → text-base
□ Card padding: p-4 → p-6
□ Button bg: bg-blue-500 → bg-orange-1
```

---

## Iteration 2 Analysis

**Screenshot:** `.qa/iteration-2.png`

### Claude Vision Comparison

| Category | Element | Figma | Implementation | Tailwind Fix |
|----------|---------|-------|----------------|--------------|
| Spacing | Button gap | 12px | 8px | `gap-3` |

### TodoWrite Items Created

```
□ Button gap: gap-2 → gap-3
```

---

## Iteration 3 Analysis (if needed)

**Screenshot:** `.qa/iteration-3.png`

### Claude Vision Comparison

| Category | Element | Figma | Implementation | Status |
|----------|---------|-------|----------------|--------|
| Typography | All elements | ✅ Match | ✅ Match | PASS |
| Spacing | All elements | ✅ Match | ✅ Match | PASS |
| Colors | All elements | ✅ Match | ✅ Match | PASS |
| Layout | All elements | ✅ Match | ✅ Match | PASS |
| Assets | All elements | ✅ Match | ✅ Match | PASS |

**Result:** ✅ All categories pass - No differences detected

---

## Check Categories Summary

| Category | Status | Notes |
|----------|--------|-------|
| Typography | ✅ | Font size, weight, color match |
| Spacing | ✅ | Padding, margin, gap match |
| Colors | ✅ | Background, border, text colors match |
| Layout | ✅ | Flex direction, alignment match |
| Assets | ✅ | Icon size, color, border-radius match |

---

## MCP Tools Used

### Figma Screenshot

```javascript
mcp__pixelbyte-figma-mcp__figma_get_screenshot({
  params: {
    file_key: "[FIGMA_FILE_KEY]",
    node_ids: ["[NODE_ID]"],
    format: "png",
    scale: 2
  }
})
```

### Browser Screenshot

```javascript
// 1. Get tab context
mcp__claude-in-chrome__tabs_context_mcp({
  createIfEmpty: true
})

// 2. Navigate to dev server
mcp__claude-in-chrome__navigate({
  url: "http://localhost:3000/[component-path]",
  tabId: <tab-id>
})

// 3. Wait for load
mcp__claude-in-chrome__computer({
  action: "wait",
  duration: 2,
  tabId: <tab-id>
})

// 4. Take screenshot
mcp__claude-in-chrome__computer({
  action: "screenshot",
  tabId: <tab-id>
})
```

---

## Stuck Detection (If Applicable)

> ⚠️ Only include this section if 3 iterations completed without PASS

### Stuck Report

**Triggered After:** Iteration 3
**Final Status:** ⚠️ ACCEPTABLE (minor differences remain)
**Remaining Differences:** [N]

### Remaining Issues

| Category | Element | Issue | Reason |
|----------|---------|-------|--------|
| Typography | Body text | Slight font rendering difference | OS-level antialiasing |
| Spacing | Card margin | 1px difference | Subpixel rendering |

### Possible Causes

- [ ] **Font Mismatch:** Custom font not installed locally
- [ ] **Subpixel Rendering:** OS-level antialiasing differences
- [ ] **Viewport Size:** Browser viewport ≠ Figma frame size
- [ ] **Missing Assets:** Icons not exported from Figma

### Recommended Actions

1. Check if custom fonts are installed: `fc-list | grep [FontName]`
2. Verify all icon assets are exported from Figma
3. Resize browser viewport to match Figma frame
4. Consider adding `-webkit-font-smoothing: antialiased`

---

## Notes

[Any additional observations, known issues, or manual review requirements]

---

## Handoff Checklist

Before proceeding to Phase 5:

- [ ] All iteration screenshots are saved
- [ ] Check categories completed (Typography, Spacing, Colors, Layout, Assets)
- [ ] TodoWrite items all completed
- [ ] Final Claude Vision comparison shows no differences (or acceptable)
- [ ] Code changes are committed (if applicable)
- [ ] Any stuck detection notes are included
- [ ] Report is complete

---

*Generated by Figma-to-Code Skill - Phase 4 Visual Validation*
*Validation Method: Claude Vision*
*Report Template Version: 2.0*
```

---

## Örnek Doldurulmuş Rapor

```markdown
# QA Validation Report (Claude Vision)

**Component:** HeroCard
**Date:** 2025-01-08 14:32:15
**Validation Method:** Claude Vision
**Iterations:** 2/3
**Status:** ✅ PASS

---

## Summary

| Metric | Value |
|--------|-------|
| Validation Method | Claude Vision |
| Iterations Used | 2/3 |
| Final Status | PASS |
| Categories Checked | Typography, Spacing, Colors, Layout, Assets |

---

## Screenshots

| Type | Location | Notes |
|------|----------|-------|
| Figma Reference | `.qa/reference.png` | Figma MCP screenshot |
| Iteration 1 | `.qa/iteration-1.png` | Initial implementation |
| Iteration 2 | `.qa/iteration-2.png` | After first fixes |
| Final | `.qa/implementation.png` | Final browser screenshot |

---

## Iteration History

| # | Status | Differences Found | Fixes Applied |
|---|--------|-------------------|---------------|
| 1 | ❌ FAIL | 5 differences | Initial implementation |
| 2 | ✅ PASS | 0 differences | pt-6→pt-8, font-medium→font-semibold, gap-4→gap-6 |

---

## Iteration 1 Analysis

**Screenshot:** `.qa/iteration-1.png`

### Claude Vision Comparison

| Category | Element | Figma | Implementation | Tailwind Fix |
|----------|---------|-------|----------------|--------------|
| Typography | Title | 32px semibold | 24px medium | `text-3xl font-semibold` |
| Spacing | Header padding | 32px top | 24px top | `pt-8` |
| Spacing | Content gap | 24px | 16px | `gap-6` |
| Colors | CTA button | #FE4601 | #3B82F6 | `bg-orange-1` |
| Assets | Icon size | 24px | 20px | `w-6 h-6` |

### TodoWrite Items Created

```
✅ Title font-size: text-2xl → text-3xl
✅ Title font-weight: font-medium → font-semibold
✅ Header padding: pt-6 → pt-8
✅ Content gap: gap-4 → gap-6
✅ Button bg: bg-blue-500 → bg-orange-1
✅ Icon size: w-5 h-5 → w-6 h-6
```

---

## Iteration 2 Analysis

**Screenshot:** `.qa/iteration-2.png`

### Claude Vision Comparison

| Category | Element | Figma | Implementation | Status |
|----------|---------|-------|----------------|--------|
| Typography | All elements | ✅ Match | ✅ Match | PASS |
| Spacing | All elements | ✅ Match | ✅ Match | PASS |
| Colors | All elements | ✅ Match | ✅ Match | PASS |
| Layout | All elements | ✅ Match | ✅ Match | PASS |
| Assets | All elements | ✅ Match | ✅ Match | PASS |

**Result:** ✅ All categories pass - No differences detected

---

## Check Categories Summary

| Category | Status | Notes |
|----------|--------|-------|
| Typography | ✅ | Font size, weight, color match |
| Spacing | ✅ | Padding, margin, gap match |
| Colors | ✅ | Background, border, text colors match |
| Layout | ✅ | Flex direction, alignment match |
| Assets | ✅ | Icon size, color, border-radius match |

---

## Notes

- Minor subpixel differences remain in font rendering (expected behavior)
- All major layout and color issues resolved
- Component ready for Phase 5 handoff

---

## Handoff Checklist

- [x] All iteration screenshots are saved
- [x] Check categories completed (Typography, Spacing, Colors, Layout, Assets)
- [x] TodoWrite items all completed
- [x] Final Claude Vision comparison shows no differences
- [x] Code changes are committed
- [x] Report is complete

---

*Generated by Figma-to-Code Skill - Phase 4 Visual Validation*
*Validation Method: Claude Vision*
```

---

## Kullanım

Phase 4 tamamlandığında bu şablonu kullanarak `.qa/report.md` dosyasını oluştur:

1. Şablonu kopyala
2. `[placeholder]` değerlerini gerçek değerlerle değiştir
3. Her iteration için Claude Vision karşılaştırma tablosunu doldur
4. TodoWrite item'larını listele
5. Check categories summary'yi güncelle
6. Kullanılmayan bölümleri kaldır (örn: stuck detection yoksa o bölümü sil)
7. `.qa/report.md` olarak kaydet
