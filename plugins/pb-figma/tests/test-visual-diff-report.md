# Test: Visual Diff Report Generation

## Purpose
Verify that compliance-checker generates a visual diff report by comparing Figma screenshot against generated code.

## Input

- Figma screenshot of AI Analysis Complete screen (node 3:217)
- Generated SwiftUI code files

## Expected Output

File: `docs/figma-reports/{file_key}-visual-diff.md`

Should contain:
1. Header with screenshot path and code file list
2. At least one "Differences Found" section (if any visual differences exist)
3. Each diff has: Aspect, Figma (Visual), Code (Generated), Severity
4. Code location with file and line number
5. Suggested fix for HIGH/MEDIUM items

## Expected Detection (Known Bugs)

If the code has these bugs, the visual diff should catch them:

| Bug | Expected Detection |
|-----|-------------------|
| "Hook" text all white | HIGH: Text Color difference — "Hook" yellow in Figma |
| Description no opacity | MEDIUM: Text Opacity — description appears lighter in Figma |
| Wrong icon on Card 3 | HIGH: Icon difference — trending-up vs time icon |

## Verification Steps

1. [ ] compliance-checker calls figma_get_screenshot
2. [ ] Visual analysis describes each element from screenshot
3. [ ] Each code file is read and compared
4. [ ] Diff report written to correct path
5. [ ] Final report references diff report with summary
6. [ ] HIGH severity items cause FAIL status
