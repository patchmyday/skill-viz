# Skill Anatomy: The `pdf` Skill

Let's walk through a real, production skill to understand every part.

## The Directory

```
pdf/
├── SKILL.md        # Main skill file
├── forms.md        # Extra reference for PDF forms
├── reference.md    # Detailed library reference
├── scripts/        # Helper scripts
└── LICENSE.txt     # License terms
```

## The SKILL.md File

### 1. Frontmatter (YAML between `---` markers)

```yaml
---
name: pdf
description: Use this skill whenever the user wants to do anything
  with PDF files. This includes reading or extracting text/tables
  from PDFs, combining or merging multiple PDFs into one, splitting
  PDFs apart, rotating pages, adding watermarks, creating new PDFs,
  filling PDF forms, encrypting/decrypting PDFs, extracting images,
  and OCR on scanned PDFs to make them searchable. If the user
  mentions a .pdf file or asks to produce one, use this skill.
license: Proprietary. LICENSE.txt has complete terms
---
```

> [!info] The `name` field
> Lowercase, hyphen-separated. This is how Claude references the skill internally.

> [!important] The `description` field
> This is the **trigger**. Claude reads this to decide whether to activate the skill. List every specific action the skill handles. End with a catch-all like "If the user mentions a .pdf file, use this skill."

> [!note] Optional frontmatter fields
> - `license` — terms for redistribution
> - `benefits-from` — list of skills that complement this one

### 2. Body (Markdown after the frontmatter)

The body contains the actual instructions Claude follows. For `pdf`, it includes:

- **Overview** — What the skill covers
- **Quick Start** — Minimal code example
- **Library guides** — How to use pypdf, reportlab, etc.
- **Common patterns** — Merge, split, rotate, watermark
- **Form filling** — Links to the separate `forms.md` reference

### 3. Supporting Files

| File | Purpose |
|------|---------|
| `scripts/` | Python helpers Claude can execute directly |
| `reference.md` | Deep-dive on JavaScript PDF libraries |
| `forms.md` | Specialized guide for PDF form filling |

> [!tip] Keep references separate
> Put detailed API docs in reference files, not in SKILL.md. This keeps the main file focused on *instructions* while letting Claude pull in details when needed.

## What Makes This Skill Good

1. **Exhaustive description** — Lists every PDF operation explicitly
2. **Catch-all trigger** — "If the user mentions a .pdf file" ensures nothing slips through
3. **Structured body** — Quick start for simple tasks, deep references for complex ones
4. **Separate concerns** — Forms get their own file instead of bloating SKILL.md

## Next Steps

- [[writing_descriptions]] — Learn the patterns that make descriptions trigger reliably
- [[what_is_a_skill]] — Go back to basics
