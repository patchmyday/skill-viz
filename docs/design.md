# skill-viz: Obsidian Skill Workbench for Claude Code

**Date:** 2026-03-26
**Status:** Draft
**Repo:** github.com/patchmyday/skill-viz (to be created)

---

## Problem

Claude Code skills are markdown files with YAML frontmatter — powerful but invisible. There's no way to browse installed skills visually, see how they relate, or quickly create/modify skills without manually editing files. Beginners don't know where to start; power users want a faster workflow.

## Solution

An Obsidian vault generator that turns Claude Code skill directories into an interactive workbench. Browse skills in a graph view, query them with Dataview, create new ones with guided Templater templates, and export back to Claude Code with a button click.

## Audiences

1. **Beginners** — guided skill creation with templates, annotated examples, dashboard overview
2. **Daily users** — quick browse/search/modify cycle without touching the filesystem
3. **Advanced/community** — extend with custom Dataview queries, share vaults via Quartz

## Architecture

```
skill-viz/
├── generate.py              # Main vault generator
├── config.yaml              # Skill source directories to scan
├── templates/
│   └── new-skill.md         # Templater template for skill creation
├── scripts/
│   ├── export_skill.py      # Export skill note → SKILL.md in Claude Code directory
│   └── validate_skill.py    # Validate frontmatter and structure
├── README.md
└── .gitignore
```

### Generated Vault Structure

```
skill-viz-vault/
├── .obsidian/
│   ├── app.json                  # Editor settings (YAML frontmatter visible)
│   ├── graph.json                # Graph color groups by tag
│   ├── community-plugins.json    # ["dataview", "templater-obsidian", "buttons"]
│   └── plugins/                  # Plugin config (not plugin code — user installs)
│       ├── dataview/
│       ├── templater-obsidian/
│       └── buttons/
├── skills/
│   ├── pdf.md                    # One note per skill
│   ├── webapp-testing.md
│   ├── skill-creator.md
│   └── ...
├── _Dashboard.md                 # Main entry point with Dataview tables + buttons
├── _Skill Map.canvas             # Visual Canvas layout
├── _templates/
│   └── New Skill.md              # Templater template
├── _guides/
│   ├── What Is A Skill.md        # Beginner explainer
│   ├── Skill Anatomy.md          # Annotated walkthrough of a real skill
│   └── Writing Good Descriptions.md  # The #1 skill creation pitfall
└── _Export Guide.md              # How to push skills back to Claude Code
```

## Component Details

### 1. generate.py — Vault Generator

**Input:** One or more skill source directories (configured in `config.yaml`):

```yaml
# config.yaml
sources:
  - path: ~/.claude/skills/
    label: "Installed Skills"
  - path: ~/Documents/cyber/agents/skills/skills/
    label: "Official Skills Repo"
output: ~/skill-viz-vault/
```

**For each SKILL.md found, generate an Obsidian note:**

```markdown
---
name: pdf
description: "Use this skill whenever the user wants to do anything with PDF files..."
source: ~/.claude/skills/pdf/SKILL.md
tags:
  - skill
  - category/document
has_scripts: true
has_references: true
has_agents: false
last_synced: 2026-03-26
---

# pdf

> Use this skill whenever the user wants to do anything with PDF files...

## Body

[Full SKILL.md body content here]

## Structure

- Scripts: `forms.py`, `merge.py`
- References: `reference.md`

## Actions

```button
name: Export to Claude Code
type: command
action: Templater: Insert templates/export.md
```

```button
name: Validate Frontmatter
type: command
action: Templater: Insert templates/validate.md
```

## Related Skills

[[docx]] | [[pptx]] | [[xlsx]]
```

**Link detection:** Parse skill bodies for references to other skills (explicit mentions, shared tags, same category). Generate `[[WikiLinks]]` so the graph view connects them.

**Tag extraction:** Map skill names/descriptions to categories:
- `category/document` — pdf, docx, pptx, xlsx
- `category/dev` — webapp-testing, frontend-design, mcp-builder
- `category/creative` — canvas-design, brand-guidelines, slack-gif-creator
- `category/meta` — skill-creator, doc-coauthoring

### 2. _Dashboard.md — Main Entry Point

```markdown
# Skill Dashboard

## Create
```button
name: Create New Skill
type: command
action: Templater: Insert _templates/New Skill.md
```

## All Skills

```dataview
TABLE description AS "Trigger", has_scripts AS "Scripts", has_references AS "Refs"
FROM "skills"
SORT name ASC
```

## By Category

```dataview
TABLE WITHOUT ID
  link(file.link, name) AS "Skill",
  description AS "Trigger"
FROM "skills"
WHERE contains(tags, "category/document")
SORT name ASC
```

(Repeat for each category)

## Recently Modified

```dataview
TABLE last_synced AS "Last Synced"
FROM "skills"
SORT last_synced DESC
LIMIT 10
```
```

### 3. _Skill Map.canvas — Visual Overview

Auto-generated JSON Canvas (jsoncanvas.org format). Layout:
- One card node per skill, positioned in category clusters
- Edges between related skills (from WikiLinks)
- Color-coded by category tag
- Cards show: skill name + first line of description

### 4. Templater Template — Guided Skill Creation

The `New Skill.md` template prompts the user step by step:

**Step 1: Name**
```
<%* const name = await tp.system.prompt("Skill name (lowercase, hyphens)") %>
```

**Step 2: Description (the critical field)**
Reframed as: "When should Claude automatically start this skill?"
Shows fill-in-the-blank:
```
<%*
const trigger = await tp.system.prompt(
  "Complete: 'Use when the user [asks about / wants to / is working on] ___'"
)
const context = await tp.system.prompt(
  "Any specific context? (e.g., 'mentions .pdf files', 'imports anthropic SDK')"
)
const description = `Use when ${trigger}. Trigger when user ${context}.`
%>
```

**Step 3: Category**
```
<%*
const category = await tp.system.suggester(
  ["Document", "Dev Tool", "Creative", "Meta/Workflow", "Other"],
  ["category/document", "category/dev", "category/creative", "category/meta", "category/other"]
)
%>
```

**Step 4: Body** — pre-populated with a starter template, not blank.

### 5. Export Script

`scripts/export_skill.py`:
- Reads an Obsidian skill note
- Strips Obsidian-specific metadata (buttons, Dataview, last_synced)
- Reconstructs valid SKILL.md with proper frontmatter (name, description)
- Writes to the configured skill directory
- Optionally creates the skill folder structure (scripts/, references/)

### 6. Validate Script

`scripts/validate_skill.py`:
- Checks YAML frontmatter has required fields (name, description)
- Warns if description is < 15 words (likely too vague)
- Warns if description contains only generic words
- Checks description < 1024 chars
- Validates name is kebab-case, < 64 chars

### 7. Beginner Guides

Three short notes in `_guides/`:

**What Is A Skill.md** — "A skill is a reusable behavior you teach Claude. It's a markdown file with 3 parts..." (with a concrete before/after example)

**Skill Anatomy.md** — An annotated real skill (e.g., doc-coauthoring) with callout blocks explaining each section

**Writing Good Descriptions.md** — The #1 pitfall, with good/bad examples, the fill-in-the-blank template, and the specificity heuristic

## Tech Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Generator language | Python | Jason's stack, simple file I/O, no build step |
| Graph visualization | Obsidian native graph view | Zero code, automatic from WikiLinks |
| Interactive queries | Dataview plugin | SQL-like queries over frontmatter, zero code |
| Skill creation | Templater plugin | Step-by-step prompts, JS scripting |
| Action buttons | Buttons plugin | One-click export/validate on each skill note |
| Canvas format | JSON Canvas (jsoncanvas.org) | Open spec, native Obsidian support |
| Sharing | Quartz (future) | Free static site from Obsidian vault |

## Required Obsidian Plugins

Users must install (community plugins):
1. **Dataview** — dashboard queries
2. **Templater** — skill creation wizard
3. **Buttons** — action buttons on skill notes

The vault `.obsidian/` config will pre-configure these but users install the plugins themselves (Obsidian doesn't support bundling plugin code).

## Out of Scope (for now)

- Auto-sync / file watcher (manual `python generate.py` for now)
- MCP bridge (Claude Code ↔ Obsidian)
- Quartz deployment
- Trigger simulation preview
- VS Code extension

## Success Criteria

1. Run `python generate.py` → opens a working Obsidian vault with all installed skills
2. Dashboard shows all skills, searchable/filterable by category
3. Graph view shows skill relationships with color-coded nodes
4. Create a new skill entirely in Obsidian in under 10 minutes
5. Export a skill back to Claude Code with one button click
