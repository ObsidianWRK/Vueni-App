# Skill Test Matrix (2025-12-23)

## Inventory

### Claude Code (.claude/skills)

- algorithmic-art
- brand-guidelines
- canvas-design
- deep-research
- doc-coauthoring
- docx
- expo-ios-designer
- frontend-design
- internal-comms
- mcp-builder
- ocr
- pdf
- plan-mode
- pptx
- shadcn-ui
- skill-creator
- slack-gif-creator
- template
- theme-factory
- web-artifacts-builder
- webapp-testing
- xlsx

### Codex (.codex/skills)

- algorithmic-art
- brand-guidelines
- canvas-design
- deep-research
- doc-coauthoring
- docx
- expo-ios-designer
- frontend-design
- internal-comms
- mcp-builder
- ocr
- pdf
- plan-mode
- pptx
- shadcn-ui
- skill-creator
- slack-gif-creator
- template
- theme-factory
- web-artifacts-builder
- webapp-testing
- xlsx

### Cursor (skills/)

- algorithmic-art
- brand-guidelines
- canvas-design
- deep-research
- doc-coauthoring
- docx
- frontend-design
- internal-comms
- mcp-builder
- ocr
- pdf
- plan-mode
- pptx
- skill-creator
- slack-gif-creator
- theme-factory
- web-artifacts-builder
- webapp-testing
- xlsx

## Validation Results

- validate_repo.py: pass (Validation passed)
- validate_skills.py --all: pass (22 validated, 0 errors, 0 warnings)
- validate_skills.py --codex: pass (22 validated, 0 errors, 0 warnings)
- validate_skills.py --cursor: pass with warning (19 validated, 0 errors, 1 warning: skills/mcp-builder uses reference/ not references/)

## Matrix

| Skill | Platform | Prompt Type | Prompt | Expected Invocation | Pass/Fail | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| algorithmic-art | Claude Code | specific | Create a p5.js flow-field sketch with seeded randomness and interactive controls. | algorithmic-art |  |  |
| brand-guidelines | Claude Code | specific | Apply Anthropic official colors and typography to a one-page product brief. | brand-guidelines |  |  |
| canvas-design | Claude Code | specific | Create a bold event poster and export as .png and .pdf. | canvas-design |  |  |
| deep-research | Claude Code | specific | Investigate lithium supply chain risks and produce a cited report. | deep-research |  |  |
| doc-coauthoring | Claude Code | specific | Help me draft a technical design doc with a structured workflow. | doc-coauthoring |  |  |
| docx | Claude Code | specific | Open report.docx and add tracked changes plus comments. | docx |  |  |
| expo-ios-designer | Claude Code | specific | Design an iOS-first Expo/React Native onboarding screen. | expo-ios-designer |  |  |
| frontend-design | Claude Code | specific | Create a distinctive, production-grade landing page UI. | frontend-design |  |  |
| internal-comms | Claude Code | specific | Draft a leadership update for Q4 roadmap progress. | internal-comms |  |  |
| mcp-builder | Claude Code | specific | Create a FastMCP server integrating the GitHub API. | mcp-builder |  |  |
| ocr | Claude Code | specific | Extract text and tables from receipt.png. | ocr |  |  |
| pdf | Claude Code | specific | Populate fields in form.pdf and return the filled PDF. | pdf |  |  |
| plan-mode | Claude Code | specific | Create a structured implementation plan for a notification system. | plan-mode |  |  |
| pptx | Claude Code | specific | Build a 5-slide pitch deck in .pptx with speaker notes. | pptx |  |  |
| shadcn-ui | Claude Code | specific | Install shadcn/ui and add a Dialog component in Next.js. | shadcn-ui |  |  |
| skill-creator | Claude Code | specific | Write a SKILL.md for a new 'log-parser' skill with metadata. | skill-creator |  |  |
| slack-gif-creator | Claude Code | specific | Create a Slack-optimized GIF of a spinning logo. | slack-gif-creator |  |  |
| template | Claude Code | specific | Generate the internal skill template files, not a custom skill. | template |  |  |
| theme-factory | Claude Code | specific | Apply a preset theme to an HTML report. | theme-factory |  |  |
| web-artifacts-builder | Claude Code | specific | Create a multi-component React artifact with routing and state using Tailwind and shadcn/ui. | web-artifacts-builder |  |  |
| webapp-testing | Claude Code | specific | Use Playwright to test localhost:3000 and capture a screenshot. | webapp-testing |  |  |
| xlsx | Claude Code | specific | Analyze sales.xlsx, update formulas, and add a summary sheet. | xlsx |  |  |
| algorithmic-art | Codex | keyword | Need algorithmic art with p5.js. | algorithmic-art |  |  |
| algorithmic-art | Codex | specific | Create a p5.js flow-field sketch with seeded randomness and interactive controls. | algorithmic-art |  |  |
| algorithmic-art | Codex | disambiguation | Generate p5.js algorithmic art, not a static poster. | algorithmic-art |  |  |
| brand-guidelines | Codex | keyword | Apply Anthropic brand guidelines. | brand-guidelines |  |  |
| brand-guidelines | Codex | specific | Apply Anthropic official colors and typography to a one-page product brief. | brand-guidelines |  |  |
| brand-guidelines | Codex | disambiguation | Use Anthropic brand guidelines, not a custom theme. | brand-guidelines |  |  |
| canvas-design | Codex | keyword | Design a poster as PNG and PDF. | canvas-design |  |  |
| canvas-design | Codex | specific | Create a bold event poster and export as .png and .pdf. | canvas-design |  |  |
| canvas-design | Codex | disambiguation | Design a static poster, not generative art. | canvas-design |  |  |
| deep-research | Codex | keyword | Deep research this topic with citations. | deep-research |  |  |
| deep-research | Codex | specific | Investigate lithium supply chain risks and produce a cited report. | deep-research |  |  |
| deep-research | Codex | disambiguation | Do deep research with citations, not a memo. | deep-research |  |  |
| doc-coauthoring | Codex | keyword | Co-author a technical spec. | doc-coauthoring |  |  |
| doc-coauthoring | Codex | specific | Help me draft a technical design doc with a structured workflow. | doc-coauthoring |  |  |
| doc-coauthoring | Codex | disambiguation | Use the documentation co-authoring workflow, not a status update. | doc-coauthoring |  |  |
| docx | Codex | keyword | Edit a .docx file with tracked changes. | docx |  |  |
| docx | Codex | specific | Open report.docx and add tracked changes plus comments. | docx |  |  |
| docx | Codex | disambiguation | Work with a DOCX file, not a PDF. | docx |  |  |
| expo-ios-designer | Codex | keyword | Expo iOS UI design. | expo-ios-designer |  |  |
| expo-ios-designer | Codex | specific | Design an iOS-first Expo/React Native onboarding screen. | expo-ios-designer |  |  |
| expo-ios-designer | Codex | disambiguation | Design an Expo iOS screen, not a web page. | expo-ios-designer |  |  |
| frontend-design | Codex | keyword | Design a web landing page. | frontend-design |  |  |
| frontend-design | Codex | specific | Create a distinctive, production-grade landing page UI. | frontend-design |  |  |
| frontend-design | Codex | disambiguation | Design a single-page web UI, no complex state. | frontend-design |  |  |
| internal-comms | Codex | keyword | Write an internal status update. | internal-comms |  |  |
| internal-comms | Codex | specific | Draft a leadership update for Q4 roadmap progress. | internal-comms |  |  |
| internal-comms | Codex | disambiguation | Create internal comms, not a technical spec. | internal-comms |  |  |
| mcp-builder | Codex | keyword | Build an MCP server. | mcp-builder |  |  |
| mcp-builder | Codex | specific | Create a FastMCP server integrating the GitHub API. | mcp-builder |  |  |
| mcp-builder | Codex | disambiguation | Build an MCP server, not a web UI. | mcp-builder |  |  |
| ocr | Codex | keyword | OCR this screenshot. | ocr |  |  |
| ocr | Codex | specific | Extract text and tables from receipt.png. | ocr |  |  |
| ocr | Codex | disambiguation | Extract text from an image, not a PDF. | ocr |  |  |
| pdf | Codex | keyword | Fill a PDF form. | pdf |  |  |
| pdf | Codex | specific | Populate fields in form.pdf and return the filled PDF. | pdf |  |  |
| pdf | Codex | disambiguation | Work with a PDF, not a DOCX. | pdf |  |  |
| plan-mode | Codex | keyword | Plan mode: how would you approach this? | plan-mode |  |  |
| plan-mode | Codex | specific | Create a structured implementation plan for a notification system. | plan-mode |  |  |
| plan-mode | Codex | disambiguation | Provide a plan with steps and risks, not brainstorming. | plan-mode |  |  |
| pptx | Codex | keyword | Create a .pptx deck. | pptx |  |  |
| pptx | Codex | specific | Build a 5-slide pitch deck in .pptx with speaker notes. | pptx |  |  |
| pptx | Codex | disambiguation | Make a PPTX deck, not an HTML report. | pptx |  |  |
| shadcn-ui | Codex | keyword | Use shadcn/ui. | shadcn-ui |  |  |
| shadcn-ui | Codex | specific | Install shadcn/ui and add a Dialog component in Next.js. | shadcn-ui |  |  |
| shadcn-ui | Codex | disambiguation | Use shadcn/ui components, not custom CSS only. | shadcn-ui |  |  |
| skill-creator | Codex | keyword | Create a new Codex skill. | skill-creator |  |  |
| skill-creator | Codex | specific | Write a SKILL.md for a new 'log-parser' skill with metadata. | skill-creator |  |  |
| skill-creator | Codex | disambiguation | Create a new skill, not just use the template. | skill-creator |  |  |
| slack-gif-creator | Codex | keyword | Make a Slack GIF. | slack-gif-creator |  |  |
| slack-gif-creator | Codex | specific | Create a Slack-optimized GIF of a spinning logo. | slack-gif-creator |  |  |
| slack-gif-creator | Codex | disambiguation | Create an animated GIF, not a static poster. | slack-gif-creator |  |  |
| template | Codex | keyword | Use the skill template scaffold. | template |  |  |
| template | Codex | specific | Generate the internal skill template files, not a custom skill. | template |  |  |
| template | Codex | disambiguation | Use the template scaffold, not skill-creator. | template |  |  |
| theme-factory | Codex | keyword | Apply a preset theme. | theme-factory |  |  |
| theme-factory | Codex | specific | Apply a preset theme to an HTML report. | theme-factory |  |  |
| theme-factory | Codex | disambiguation | Use theme-factory, not brand guidelines. | theme-factory |  |  |
| web-artifacts-builder | Codex | keyword | Build a complex web artifact with state. | web-artifacts-builder |  |  |
| web-artifacts-builder | Codex | specific | Create a multi-component React artifact with routing and state using Tailwind and shadcn/ui. | web-artifacts-builder |  |  |
| web-artifacts-builder | Codex | disambiguation | Build a complex artifact, not a simple static page. | web-artifacts-builder |  |  |
| webapp-testing | Codex | keyword | Test a web app with Playwright. | webapp-testing |  |  |
| webapp-testing | Codex | specific | Use Playwright to test localhost:3000 and capture a screenshot. | webapp-testing |  |  |
| webapp-testing | Codex | disambiguation | Test an app, not design a UI. | webapp-testing |  |  |
| xlsx | Codex | keyword | Edit an .xlsx spreadsheet. | xlsx |  |  |
| xlsx | Codex | specific | Analyze sales.xlsx, update formulas, and add a summary sheet. | xlsx |  |  |
| xlsx | Codex | disambiguation | Work with an XLSX file, not a PDF. | xlsx |  |  |
| algorithmic-art | Cursor | specific | Create a p5.js flow-field sketch with seeded randomness and interactive controls. | algorithmic-art |  |  |
| brand-guidelines | Cursor | specific | Apply Anthropic official colors and typography to a one-page product brief. | brand-guidelines |  |  |
| canvas-design | Cursor | specific | Create a bold event poster and export as .png and .pdf. | canvas-design |  |  |
| deep-research | Cursor | specific | Investigate lithium supply chain risks and produce a cited report. | deep-research |  |  |
| doc-coauthoring | Cursor | specific | Help me draft a technical design doc with a structured workflow. | doc-coauthoring |  |  |
| docx | Cursor | specific | Open report.docx and add tracked changes plus comments. | docx |  |  |
| frontend-design | Cursor | specific | Create a distinctive, production-grade landing page UI. | frontend-design |  |  |
| internal-comms | Cursor | specific | Draft a leadership update for Q4 roadmap progress. | internal-comms |  |  |
| mcp-builder | Cursor | specific | Create a FastMCP server integrating the GitHub API. | mcp-builder |  |  |
| ocr | Cursor | specific | Extract text and tables from receipt.png. | ocr |  |  |
| pdf | Cursor | specific | Populate fields in form.pdf and return the filled PDF. | pdf |  |  |
| plan-mode | Cursor | specific | Create a structured implementation plan for a notification system. | plan-mode |  |  |
| pptx | Cursor | specific | Build a 5-slide pitch deck in .pptx with speaker notes. | pptx |  |  |
| skill-creator | Cursor | specific | Write a SKILL.md for a new 'log-parser' skill with metadata. | skill-creator |  |  |
| slack-gif-creator | Cursor | specific | Create a Slack-optimized GIF of a spinning logo. | slack-gif-creator |  |  |
| theme-factory | Cursor | specific | Apply a preset theme to an HTML report. | theme-factory |  |  |
| web-artifacts-builder | Cursor | specific | Create a multi-component React artifact with routing and state using Tailwind and shadcn/ui. | web-artifacts-builder |  |  |
| webapp-testing | Cursor | specific | Use Playwright to test localhost:3000 and capture a screenshot. | webapp-testing |  |  |
| xlsx | Cursor | specific | Analyze sales.xlsx, update formulas, and add a summary sheet. | xlsx |  |  |
