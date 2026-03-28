# What Is a Skill?

A **skill** teaches Claude Code a reusable behavior. It's a markdown file (`SKILL.md`) that lives in a directory, optionally alongside scripts, references, and other assets.

When Claude encounters a task that matches a skill's description, it automatically loads that skill and follows its instructions. Think of skills as "plugins for Claude's brain."

## Before Skills

```
You: "Create a PDF report from this data"
Claude: *writes basic code, misses edge cases, forgets about tables*
```

## After Installing the `pdf` Skill

```
You: "Create a PDF report from this data"
Claude: *automatically loads pdf skill*
       *uses pypdf for generation*
       *handles tables, images, fonts correctly*
       *adds page numbers and headers*
```

## The Key Insight

The **description** field is everything. It's not just documentation — it's the trigger that tells Claude *when* to activate the skill. A vague description means Claude won't know when to use it. A precise description means it fires reliably.

```yaml
# Bad — too vague
description: Helps with documents

# Good — specific triggers
description: Use this skill whenever the user wants to do anything
  with PDF files. This includes reading, merging, splitting,
  rotating pages, adding watermarks, creating new PDFs, filling
  forms, encrypting/decrypting, and OCR on scanned PDFs.
  If the user mentions a .pdf file or asks to produce one,
  use this skill.
```

## Anatomy at a Glance

```
my-skill/
├── SKILL.md          # Required: frontmatter + instructions
├── scripts/          # Optional: helper scripts Claude can run
├── references/       # Optional: reference docs Claude can read
├── agents/           # Optional: sub-agent definitions
└── assets/           # Optional: images, templates, etc.
```

## Where Skills Live

- **Installed skills:** `~/.claude/skills/` — skills you've added to your setup
- **Project skills:** `.claude/skills/` in any repo — skills scoped to that project
- **Official skills:** The Anthropic skills repo — curated, production-ready

## Next Steps

- [[skill_anatomy]] — See a real skill broken down piece by piece
- [[writing_descriptions]] — Master the most important part of any skill
