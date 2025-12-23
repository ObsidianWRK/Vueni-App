# OCR Skill Test Scenarios

This document outlines test scenarios to verify the OCR skill's context detection and cross-platform functionality.

## Test Setup

These tests verify that when the OCR skill is invoked, it correctly:
1. Scans conversation context for file references
2. Detects OCR-suitable file extensions
3. Determines user intent correctly
4. Takes appropriate action (process, ask for clarification, or skip)

## Auto-Invocation & Output Contract Smoke Tests

### Scenario A: Auto-invoke on vague prompt (image attached)
- **Setup:** Attach `screenshot.png`; message: "what’s going on here?"
- **Expect:** Automatically treat OCR as active (no prompt for /ocr); perform OCR; output the two required sections with `text` then `json` fences; JSON matches SKILL schema; uncertainties listed.

### Scenario B: Multiple files (images + PDF) in auto mode
- **Setup:** Attach `screen1.png`, `screen2.jpg`, `doc.pdf`; message: "summarize these."
- **Expect:** Detect all OCR-suitable files; auto-run OCR; include per-image entries in JSON; preserve required headings/fences; note if any file cannot be processed; no missing JSON section.

### Scenario C: Non-Gemini / auto fallback
- **Setup:** Force non-Gemini or auto model; attach `receipt.png`; message: "what does this say?"
- **Expect:** If Gemini unavailable, still perform OCR with best available vision path; explicitly mention fallback if desired; still emit exact two-section format and schema-compliant JSON.

### Scenario D: Ambiguous intent with file-operation wording
- **Setup:** Attach `report.pdf`; message: "rename this file."
- **Expect:** Skip OCR (intent clearly non-content). Optionally ask to confirm OCR only if ambiguity; do not auto-run OCR.

### Scenario E: User explicitly declines OCR
- **Setup:** Attach `image.png`; message: "don’t OCR this, just move it."
- **Expect:** Do not run OCR; respect opt-out; no OCR output sections.

## Scenario 1: Single Image File Reference

### Test Case 1.1: PNG with Clear Intent
**User Message:** "Can you extract text from screenshot.png?"

**Expected Behavior:**
- ✅ Detect `screenshot.png` in message
- ✅ Recognize `.png` as OCR-suitable extension
- ✅ Identify OCR intent ("extract text")
- ✅ Acknowledge file: "I found screenshot.png"
- ✅ Check if file is in context
  - If not loaded: Use Read tool to load it
  - If loaded: Use existing context
- ✅ Proceed with OCR extraction

### Test Case 1.2: JPG with Content Query
**User Message:** "What does the error in error.jpg say?"

**Expected Behavior:**
- ✅ Detect `error.jpg` in message
- ✅ Recognize content query intent
- ✅ Load file if needed
- ✅ Proceed with OCR

### Test Case 1.3: Absolute Path
**User Message:** "Transcribe /Users/damon/Desktop/invoice.pdf"

**Expected Behavior:**
- ✅ Detect absolute path `/Users/damon/Desktop/invoice.pdf`
- ✅ Recognize `.pdf` extension
- ✅ Recognize "transcribe" as OCR intent
- ✅ Load and process file

## Scenario 2: Multiple Files

### Test Case 2.1: Multiple Images
**User Message:** "Compare data in chart1.png and chart2.png"

**Expected Behavior:**
- ✅ Detect both `chart1.png` and `chart2.png`
- ✅ Recognize comparison task (OCR needed)
- ✅ Load both files if not in context
- ✅ Process both files
- ✅ Output structured data for both (index: 1 and 2)

### Test Case 2.2: Mixed File Types
**User Message:** "Extract text from scan.tiff, data.csv, and report.pdf"

**Expected Behavior:**
- ✅ Detect all three files
- ✅ Recognize all extensions as OCR-suitable
- ✅ Process all files sequentially
- ✅ Output combined structured data

## Scenario 3: Ambiguous Intent

### Test Case 3.1: File Mentioned, Intent Unclear
**User Message:** "I have screenshot.png"

**Expected Behavior:**
- ✅ Detect `screenshot.png`
- ⚠️ Recognize unclear intent (no OCR keywords)
- ✅ Ask for clarification: "I see you mentioned screenshot.png. Would you like me to extract text/data from it?"
- ⏸️ Wait for user response

### Test Case 3.2: Multiple Files, No Clear Request
**User Message:** "These files might be useful: doc1.pdf, doc2.pdf"

**Expected Behavior:**
- ✅ Detect both PDF files
- ⚠️ Recognize vague intent
- ✅ Ask: "Would you like me to extract text from doc1.pdf and doc2.pdf?"

## Scenario 4: Non-OCR Intent (Should Skip)

### Test Case 4.1: File Operations
**User Message:** "Delete screenshot.png and move invoice.pdf to archive/"

**Expected Behavior:**
- ✅ Detect files
- ✅ Recognize file operation intent (delete, move)
- ❌ Skip OCR processing
- ✅ Exit skill gracefully or defer to file operations

### Test Case 4.2: File Metadata Query
**User Message:** "What's the file size of data.csv?"

**Expected Behavior:**
- ✅ Detect file
- ✅ Recognize metadata query (not content)
- ❌ Skip OCR
- ✅ Exit gracefully

## Scenario 5: Files Already in Context

### Test Case 5.1: Previously Loaded Image
**Setup:** User has already used Read tool on `screenshot.png` in previous message

**User Message:** "What text is in this image?"

**Expected Behavior:**
- ✅ Check context for previously loaded images
- ✅ Find `screenshot.png` in previous Read tool call
- ✅ Acknowledge: "I can see screenshot.png in context"
- ✅ Process without re-loading
- ✅ Extract text

### Test Case 5.2: Attached Image
**Setup:** User has attached an image directly

**User Message:** "Extract text from this"

**Expected Behavior:**
- ✅ Detect attachment in context
- ✅ Recognize "extract text" intent
- ✅ Process attached image
- ✅ Output results

## Scenario 6: No OCR Files Detected

### Test Case 6.1: No Files Mentioned
**User Message:** "Can you help me with OCR?"

**Expected Behavior:**
- ❌ No files detected in message
- ✅ Ask user to provide files: "Please provide the image(s), PDF(s), or file paths you'd like me to process"
- ✅ Guide: "You can attach files, paste screenshots, or provide file paths"

### Test Case 6.2: Non-OCR File Types
**User Message:** "Extract data from config.json and main.py"

**Expected Behavior:**
- ✅ Detect files but with non-OCR extensions (`.json`, `.py`)
- ❌ Skip OCR (these are text files, not images/PDFs)
- ✅ Suggest alternative: "These are code files. Would you like me to read and analyze them instead?"

## Scenario 7: Relative Paths

### Test Case 7.1: Relative Path Reference
**User Message:** "Process ./images/scan.png and ../docs/invoice.pdf"

**Expected Behavior:**
- ✅ Detect `./images/scan.png` (relative)
- ✅ Detect `../docs/invoice.pdf` (relative)
- ✅ Load both using Read tool with proper path resolution
- ✅ Process both files

## Scenario 8: Special File Formats

### Test Case 8.1: HEIC/HEIF (Apple Photos)
**User Message:** "What's in photo.heic?"

**Expected Behavior:**
- ✅ Detect `.heic` extension
- ✅ Recognize as OCR-suitable image format
- ✅ Process if platform supports it
- ⚠️ Or fallback to tesseract/conversion if needed

### Test Case 8.2: WebP Images
**User Message:** "Extract text from banner.webp"

**Expected Behavior:**
- ✅ Detect `.webp` extension
- ✅ Process as image

### Test Case 8.3: CSV as Image (scanned table)
**User Message:** "OCR this scanned table in data.csv.png"

**Expected Behavior:**
- ✅ Detect `.png` extension (not fooled by .csv in filename)
- ✅ Process as image
- ✅ Extract table structure

## Scenario 9: Platform-Specific Behavior

### Test Case 9.1: Claude Code Invocation
**Platform:** Claude Code

**User Message:** "Use OCR skill on receipt.jpg"

**Expected Behavior:**
- ✅ Skill invoked via Skill tool
- ✅ Context detection works
- ✅ Uses Claude's vision model
- ✅ Outputs text + JSON

### Test Case 9.2: Cursor Slash Command
**Platform:** Cursor

**User Input:** `/ocr` (then mentions file)

**Expected Behavior:**
- ✅ Skill invoked
- ✅ Model switched to Gemini 3 Pro (if available)
- ✅ Context detection works
- ✅ Processes file

### Test Case 9.3: Codex Natural Request
**Platform:** Codex

**User Message:** "Run OCR on my screenshot"

**Expected Behavior:**
- ✅ Skill invoked via natural language
- ✅ Context detection scans for "screenshot.*\.(png|jpg|...)"
- ✅ Processes found file

## Scenario 10: Edge Cases

### Test Case 10.1: File Mentioned Multiple Times
**User Message:** "I have data.pdf. Can you process data.pdf and extract tables from data.pdf?"

**Expected Behavior:**
- ✅ Detect `data.pdf` (deduplicate, not process 3 times)
- ✅ Load once
- ✅ Process once
- ✅ Output results

### Test Case 10.2: File Path with Spaces
**User Message:** "Extract from /Users/damon/My Documents/scan report.pdf"

**Expected Behavior:**
- ✅ Detect path with spaces: `/Users/damon/My Documents/scan report.pdf`
- ✅ Properly handle spaces in Read tool call
- ✅ Process file

### Test Case 10.3: URL to Image (if supported)
**User Message:** "OCR this: https://example.com/invoice.png"

**Expected Behavior:**
- ✅ Detect URL with `.png` extension
- ⚠️ Attempt to fetch if platform allows
- ✅ Or ask user to download first

## Test Validation Checklist

For each scenario, verify:

- [ ] File detection works (correct files identified)
- [ ] Extension recognition works (OCR-suitable vs. not)
- [ ] Intent determination is accurate (OCR vs. file ops)
- [ ] Appropriate action taken (process, ask, or skip)
- [ ] File loading works (Read tool used when needed)
- [ ] No re-loading of already-loaded files
- [ ] Output format matches specification (text + JSON)
- [ ] Cross-platform compatibility maintained

## Manual Testing Instructions

1. **Start a new conversation** in your platform (Claude Code, Cursor, or Codex)
2. **Invoke the OCR skill** (via slash command, Skill tool, or natural request)
3. **Provide test scenario input** (user message from above)
4. **Verify expected behavior** matches the checklist
5. **Document any discrepancies** or unexpected behavior
6. **Test multiple scenarios** in sequence to verify context scanning works across messages

## Automated Testing (Future)

Consider creating:
- Unit tests for file path pattern matching
- Integration tests for Read tool usage
- End-to-end tests for each platform
- Regression tests for edge cases

---

**Last Updated:** 2025-12-23
**Version:** 1.0 (Skill-based context detection)
