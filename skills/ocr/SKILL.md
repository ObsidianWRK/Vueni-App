---
name: ocr
description: Extract accurate text and structured information from screenshots/images. Use when the user provides a screenshot/photo and asks to OCR, transcribe, extract tables or key/value fields, capture UI/error text, or pull specific details from an image. Prioritize fidelity; avoid hallucination; output verbatim text plus structured JSON.
license: MIT
compatibility: Designed for Cursor, Claude Code, and Codex
---

# OCR

<!-- markdownlint-disable MD033 -->

<purpose>
Turn screenshot(s) into (1) a faithful transcription and (2) structured data (key/values, tables, entities) without guessing.
</purpose>

## Contract (applies to all models, including auto/fallback)
- If **any** OCR-suitable file is present in context (see extensions below), you **MUST** run the context-scanning steps and perform OCR.
- This applies to **Gemini 3 Pro, Claude Code, Codex, and any auto-selected/ fallback model**. If Gemini 3 Pro cannot be used, still perform OCR with the best available vision-capable path and follow the same output format; you may inform the user that Gemini was unavailable, but do **not** relax the structure.
- Output is **non-optional**: always return both sections with the exact headings and fenced languages:
  - `## Extracted Text (verbatim)` followed by a ```text fenced block.
  - `## Structured Output (JSON)` followed by a ```json fenced block matching the schema below.
- Never omit the JSON section, never rename the headings, and never change the fence languages. Summaries or extra analysis may follow **after** these two sections.

<workflow>

## Platform-specific guidance

### Cursor (use Gemini 3 Pro)

- Prefer the Cursor slash command `/ocr` (it pins the model to Gemini 3 Pro).
- If the model is not Gemini 3 Pro, switch to it (or ask the user to) before extracting.

### Claude Code & Codex (no Gemini model switching)

- Do not attempt to switch to Gemini. Use the best available vision-capable model.
- If images cannot be attached/read directly, ask the user for a local file path (or to save the image into the workspace) and use a deterministic OCR fallback (e.g., `tesseract`) to extract text, then structure the output into the required JSON schema.

## 1) Auto-detect and confirm inputs

### Context Scanning (happens automatically every time)

**IMPORTANT**: Before asking the user for files, ALWAYS scan the conversation context first:

1. **Check recent messages** (last 3-5 user messages) for file references with OCR-suitable extensions:
   - Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.tiff`, `.tif`, `.bmp`, `.webp`, `.heic`, `.heif`, `.svg`
   - Documents: `.pdf`
   - Structured data: `.csv`, `.tsv`

2. **Look for file path patterns**:
   - Absolute paths: `/path/to/file.png`, `~/documents/scan.pdf`, `C:\files\image.jpg`
   - Relative paths: `./images/screenshot.png`, `../docs/invoice.pdf`
   - Simple filenames: `screenshot.png`, `invoice.pdf`, `data.csv`

3. **Check if files are already in context**:
   - Look for previous Read tool calls with image/PDF file paths
   - Check for attachments or images that were provided
   - Scan for `<ide_opened_file>` or `<ide_selection>` tags with OCR-suitable files

4. **Determine user intent**:
   - OCR-related queries: "extract text", "what does this say", "transcribe", "read the image", "OCR this", "what's in the PDF"
   - Content queries: "summarize the screenshot", "what error is shown", "extract the table"
   - File operation queries (skip OCR): "delete this file", "move screenshot.png", "rename invoice.pdf"

### Action Based on Detection

**If OCR-suitable files are detected AND user intent is OCR/content-related:**
- Acknowledge the detected files: "I found these OCR-suitable files: [list files]"
- If files are not yet loaded (just mentioned), use Read tool to load them first
- Proceed with OCR extraction automatically

**If files are mentioned but intent is unclear:**
- Ask for clarification: "I see you mentioned [files]. Would you like me to extract text/data from them?"

**If no OCR-suitable files are detected:**
- Ask user to provide files: "Please provide the image(s), PDF(s), or file paths you'd like me to process."
- Guide them: "You can attach files, paste screenshots, or provide file paths."

**If user explicitly requested specific fields:**
- Focus extraction on those fields, but still include full transcription unless told otherwise

## 2) Transcribe (OCR)

- Preserve reading order and line breaks.
- Keep punctuation and casing as seen.
- Do not “clean up” wording.

## 3) Structure

- Extract obvious key/value pairs (labels + values).
- Convert obvious tables into headers + rows.
- Extract common entities (emails, phones, URLs, dates, amounts, error codes).

## 4) Handle uncertainty safely

- If text is unclear, output your best guess with a trailing "?" in the transcription.
- Also include unclear snippets in an `uncertain` list with a short reason.
- Do not invent missing/cut-off text.

## 5) Output (required)

Always output:

## Extracted Text (verbatim)

```text
<full transcription, with line breaks>
```

## Structured Output (JSON)

```json
{
  "images": [
    {
      "index": 1,
      "summary": "",
      "text": "",
      "key_values": [{ "key": "", "value": "" }],
      "tables": [{ "title": "", "headers": [], "rows": [] }],
      "entities": [{ "type": "email|phone|url|amount|date|error_code|other", "value": "" }],
      "uncertain": [{ "text": "", "reason": "blurred|cut_off|low_contrast|other" }]
    }
  ]
}
```

</workflow>
