# OCR Skill - Cross-Platform Usage Guide

This OCR skill automatically detects OCR-suitable files in conversation context and extracts text and structured data from images, PDFs, and other documents.

## Workspace OCR Rule (auto-apply)
- If any OCR-suitable file (images/PDFs/CSV/TSV) is in context, the assistant **will directly apply** the OCR workflow—no explicit `/ocr` needed.
- OCR is skipped only when the user’s intent is clearly non-content-related (e.g., rename/delete files) or they explicitly decline OCR.
- Output must always include the two sections and fence languages from `skills/ocr/SKILL.md` (`text` block, then `json` block with the defined schema). Additional analysis may follow after those sections.

## Key Features

- **Automatic Context Detection**: Scans conversation history for file references
- **Smart File Loading**: Uses Read tool to load files that aren't yet in context
- **Intent Recognition**: Understands when OCR is needed vs. file operations
- **Cross-Platform**: Works in Claude Code, Cursor, and Codex
- **Structured Output**: Extracts text, tables, key-value pairs, and entities

## Supported File Types

### Images
`.png`, `.jpg`, `.jpeg`, `.gif`, `.tiff`, `.tif`, `.bmp`, `.webp`, `.heic`, `.heif`, `.svg`

### Documents
`.pdf`

### Structured Data
`.csv`, `.tsv`

## How to Use

### Claude Code

**Method 1: Skill Tool**
```
Simply invoke the OCR skill when you have images/PDFs in context:
User: "Can you extract text from screenshot.png?"
Assistant: [Invokes OCR skill via Skill tool]
```

**Method 2: Natural Request**
```
The assistant will suggest using OCR when it detects relevant files:
User: "I have an invoice at ~/documents/invoice.pdf"
Assistant: "I can use the OCR skill to extract the text and data. Would you like me to do that?"
```

### Cursor

**Method 1: Slash Command (Recommended)**
```
/ocr
```
This pins the model to Gemini 3 Pro (optimal for OCR) and invokes the skill.

**Method 2: Skill Invocation**
```
User: "Use the OCR skill on screenshot.png"
Assistant: [Invokes skill and processes the file]
```

**Method 3: Natural Request**
The `.cursorrules` file will help the assistant suggest OCR when appropriate.

### Codex

**Method 1: Direct Invocation**
```
User: "Run the OCR skill on my screenshot"
Assistant: [Invokes skill]
```

**Method 2: Natural Request**
```
User: "What does the error message in error.png say?"
Assistant: [Recognizes OCR need and invokes skill]
```

## How Context Detection Works

When the OCR skill is invoked, it automatically:

1. **Scans recent messages** (last 3-5) for file paths with OCR extensions
2. **Detects file path patterns**:
   - Absolute: `/path/to/file.png`, `~/docs/scan.pdf`
   - Relative: `./images/screenshot.png`
   - Filenames: `invoice.pdf`, `data.csv`
3. **Checks if files are loaded**:
   - Previous Read tool calls
   - Attachments or pasted images
   - IDE opened files or selections
4. **Loads files automatically** if referenced but not yet in context
5. **Determines intent**:
   - OCR-related: "extract text", "transcribe", "what does this say"
   - Content queries: "summarize screenshot", "what error is shown"
   - File operations (skips OCR): "delete file", "move screenshot.png"

## Usage Examples

### Example 1: Single Image
```
User: "Can you tell me what's in screenshot.png?"
Assistant: "I found screenshot.png. Let me use the OCR skill to extract the text..."
[Loads file if needed, then processes]
```

### Example 2: Multiple Files
```
User: "Compare the data in invoice1.pdf and invoice2.pdf"
Assistant: "I found 2 PDF files. Using OCR to extract data from both..."
[Processes both files]
```

### Example 3: Already Loaded Image
```
[User has already attached an image]
User: "What does this error say?"
Assistant: "I can see an image in context. Using OCR to extract the error text..."
[Processes the attached image directly]
```

### Example 4: File Path Reference
```
User: "Check /Users/damon/Desktop/receipt.jpg"
Assistant: "I'll use the OCR skill to extract text from the receipt..."
[Loads the file, then processes]
```

## Output Format

The skill always outputs:

### 1. Extracted Text (Verbatim)
```text
Faithful transcription preserving:
- Reading order
- Line breaks
- Punctuation and casing
- Exactly as seen (no cleanup)
```

### 2. Structured Data (JSON)
```json
{
  "images": [
    {
      "index": 1,
      "summary": "Brief description of image content",
      "text": "Full extracted text",
      "key_values": [
        {"key": "Invoice Number", "value": "INV-12345"}
      ],
      "tables": [
        {
          "title": "Order Items",
          "headers": ["Item", "Quantity", "Price"],
          "rows": [["Widget", "2", "$19.99"]]
        }
      ],
      "entities": [
        {"type": "email", "value": "support@example.com"},
        {"type": "amount", "value": "$39.98"}
      ],
      "uncertain": [
        {"text": "blurry?", "reason": "low_contrast"}
      ]
    }
  ]
}
```

## Platform-Specific Notes

### Claude Code
- Uses default vision model (Claude Sonnet with vision capabilities)
- No model switching needed
- Fallback to `tesseract` if direct image reading unavailable

### Cursor
- `/ocr` slash command pins to Gemini 3 Pro (best OCR performance)
- Can also invoke via standard skill mechanisms
- `.cursorrules` helps assistant suggest OCR proactively

### Codex
- Uses available vision model
- Skill invocation via natural language or direct request
- Same context detection logic applies

## Customization

### Add Support for New File Types

Edit [`SKILL.md`](./SKILL.md) and add extensions to the detection list:

```markdown
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.tiff`, `.tif`, `.bmp`, `.webp`, `.heic`, `.heif`, `.svg`, `.your_format`
```

### Modify Intent Detection

Edit the "Determine user intent" section in [`SKILL.md`](./SKILL.md) to add new trigger phrases or exclusions.

### Adjust Context Scanning Depth

Change "last 3-5 user messages" to scan more/fewer messages in the context detection section.

## Troubleshooting

**Skill doesn't detect my file:**
- Ensure filename has one of the supported extensions
- Try providing absolute path: `/full/path/to/file.png`
- Attach the file directly if it's local

**OCR quality is poor:**
- In Cursor, use `/ocr` to switch to Gemini 3 Pro
- Ensure image is high quality (not blurry or low resolution)
- Check the `uncertain` array in JSON output for flagged issues

**Skill asks for files that are already in context:**
- This can happen if files were mentioned in old messages
- Simply confirm: "Yes, process the files in context" or provide file paths again

**Skill runs when I don't want OCR:**
- Be explicit: "Delete screenshot.png" (not "Do something with screenshot.png")
- The skill checks intent and should skip file operations

## Performance

- **Context scanning**: Minimal overhead (simple pattern matching)
- **File loading**: Only loads files not already in context
- **Processing**: Depends on file size and platform model
- **Multi-file**: Processes files sequentially, batches structured output

## License

MIT License - See skill frontmatter for details.

## Compatibility

Designed for and tested on:
- ✅ Claude Code (Anthropic)
- ✅ Cursor IDE
- ✅ OpenAI Codex CLI

---

For implementation details, see [`SKILL.md`](./SKILL.md).
