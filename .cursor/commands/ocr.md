/model Gemini 3 Pro

Before doing OCR, confirm you are running on Gemini 3 Pro. If the model switch fails or Gemini 3 Pro isn't available, tell me to select "Gemini 3 Pro" in the model picker and then rerun `/ocr`.

OCR the attached screenshot(s). If no screenshot is attached, ask me to attach one.

Hard rules:
- Only extract what is actually visible. Do not guess missing/blurred text.
- Preserve reading order and line breaks as much as possible.
- If a token is unclear, include your best guess with a trailing "?" and also list it under "uncertain".

Output EXACTLY this structure:

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
      "key_values": [
        { "key": "", "value": "" }
      ],
      "tables": [
        { "title": "", "headers": [], "rows": [] }
      ],
      "entities": [
        { "type": "email|phone|url|amount|date|error_code|other", "value": "" }
      ],
      "uncertain": [
        { "text": "", "reason": "blurred|cut_off|low_contrast|other" }
      ]
    }
  ]
}
```

