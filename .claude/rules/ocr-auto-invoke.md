# OCR Auto-Invocation Policy

**Priority:** High
**Applies to:** All operations involving OCR-suitable files
**Path scope:** `**/*.{png,jpg,jpeg,gif,bmp,tiff,pdf}`

## Auto-Invocation Rule

When any OCR-suitable file (per `skills/ocr/SKILL.md` extensions) is present in context, the assistant **MUST** treat the `ocr` skill as active and follow its workflow automatically, even if the user does not type `/ocr`.

## Behavior Requirements

### MUST (Hard Requirements)

1. **Automatic activation**: Treat `ocr` skill as active when OCR-suitable files are in context
2. **Follow workflow**: Execute all instructions in `skills/ocr/SKILL.md` exactly
3. **Output format**: Produce exactly the two sections defined in the skill:
   - Extracted Text (```text fenced block)
   - Structured Data (```json fenced block)
4. **Never omit sections**: Both sections are required, never skip the JSON output
5. **Preserve headings**: Use exact heading names from the skill specification

### Skill Priority

If multiple skills could apply, **prefer `ocr`** whenever the question involves anything that could plausibly be on the image/PDF:
- UI text
- Error messages
- Tables
- Receipts
- Documents
- Screenshots
- Scans

### Defer Conditions

Defer OCR only when:
- User's intent is clearly non-content-related (e.g., delete/rename file)
- User explicitly declines OCR
- Operation is purely file management

## Model Selection Mode

In **auto model-selection mode**, if OCR-suitable files are present:
- Assistant **MUST** treat the `ocr` skill as active
- Assistant **MUST** follow all instructions in `skills/ocr/SKILL.md` as hard constraints
- This applies regardless of which model runs

## Enforcement

This is a **hard requirement (MUST/ALWAYS)**, not best-effort.

**Correct behavior:**
```
User uploads screenshot.png
Agent: [Automatically invokes OCR skill]
Agent: [Produces Extracted Text + Structured Data sections]
```

**Incorrect behavior:**
```
User uploads screenshot.png
Agent: "What would you like me to do with this image?"
[Fails to auto-invoke OCR]
```

## References

- Full OCR skill specification: `skills/ocr/SKILL.md`
- Supported file extensions defined in skill
- Output format examples in skill documentation
