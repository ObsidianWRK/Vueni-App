---
name: ocr
description: Extract accurate text and structured information from screenshots/images. Use when the user provides a screenshot/photo and asks to OCR, transcribe, extract tables or key/value fields, capture UI/error text, or pull specific details from an image. Prioritize fidelity; avoid hallucination; output verbatim text plus structured JSON.
---

# OCR

<!-- markdownlint-disable MD033 -->

<purpose>
Turn screenshot(s) into (1) a faithful transcription and (2) structured data (key/values, tables, entities) without guessing.
</purpose>

<workflow>

## Platform-specific guidance

### Cursor (use Gemini 3 Pro)

- Prefer the Cursor slash command `/ocr` (it pins the model to Gemini 3 Pro).
- If the model is not Gemini 3 Pro, switch to it (or ask the user to) before extracting.

### Claude Code & Codex (no Gemini model switching)

- Do not attempt to switch to Gemini. Use the best available vision-capable model.
- If images cannot be attached/read directly, ask the user for a local file path (or to save the image into the workspace) and use a deterministic OCR fallback (e.g., `tesseract`) to extract text, then structure the output into the required JSON schema.

## 1) Confirm inputs

- If no image(s) are attached, ask the user to attach them.
- If the user asked for specific fields, focus extraction on those fields, but still include full transcription unless explicitly told not to.

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
