# Writing Skill Descriptions

The `description` field is the single most important line in your skill. It serves double duty:

1. **Human UI text** — shown in skill browsers and dashboards
2. **AI trigger** — Claude reads it to decide when to activate the skill

Get it wrong and your skill never fires. Get it right and it activates reliably every time.

## The #1 Pitfall: Being Too Vague

```yaml
# BAD — Claude has no idea when to use this
description: Helps with documents

# BAD — too broad, will conflict with other skills
description: Use for any coding task

# BAD — describes what it is, not when to use it
description: A collection of PDF utilities
```

## The Pattern That Works

**Formula:** `Use this skill when [specific conditions]. This includes [exhaustive list of actions]. Trigger when [catch-all pattern].`

```yaml
# GOOD — specific, exhaustive, with catch-all
description: >
  Use this skill whenever the user wants to create, read, edit,
  or manipulate Word documents (.docx files). Triggers include:
  any mention of 'Word doc', 'word document', '.docx', or requests
  to produce professional documents with formatting like tables of
  contents, headings, page numbers, or letterheads. Do NOT use for
  PDFs, spreadsheets, or Google Docs.
```

## Fill-in-the-Blank Template

Copy this and fill in the blanks:

```yaml
description: >
  Use this skill when the user wants to [PRIMARY ACTION].
  This includes [ACTION 1], [ACTION 2], [ACTION 3], and [ACTION 4].
  Trigger when the user mentions [KEYWORD 1], [KEYWORD 2],
  or [FILE EXTENSION]. Do NOT use for [EXCLUSION 1] or [EXCLUSION 2].
```

## Good vs Bad: Side by Side

| Bad | Good | Why |
|-----|------|-----|
| "PDF tools" | "Use when the user wants to do anything with PDF files. This includes reading, merging, splitting..." | Lists specific actions |
| "Helps test things" | "Toolkit for testing local web apps using Playwright. Supports verifying frontend functionality..." | Names the tool and scope |
| "For presentations" | "Use any time a .pptx file is involved — as input, output, or both. This includes creating slide decks..." | Covers all directions |

## Pro Tips

1. **List file extensions explicitly** — `.pdf`, `.docx`, `.pptx` are strong triggers
2. **Include synonyms** — "Word doc", "word document", ".docx" all mean the same thing to users but Claude needs them listed
3. **Add exclusions** — "Do NOT use for PDFs" prevents false positives
4. **Use the TRIGGER keyword** — Some skills use `TRIGGER when:` and `DO NOT TRIGGER when:` for extra clarity
5. **Test it** — Use the skill-creator's eval system to measure trigger accuracy

## Next Steps

- [[what_is_a_skill]] — Review the basics
- [[skill_anatomy]] — See how description fits into the full skill structure
