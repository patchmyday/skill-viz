# skill-viz

An Obsidian plugin for browsing, viewing, and creating Claude Code skills — a rich interactive workbench that goes beyond static markdown.

## Features

### Browse Mode (Sidebar Panel)
- Scan all skill sources (local, installed, community repos)
- Card list with name, category chip, description quality indicator, component badges
- Filter by category, search by name/description
- Show install scope (user/project/local) per skill

### View Mode (Rich SKILL.md Renderer)
- Frontmatter rendered as styled metadata header (not raw YAML)
- Description displayed with dual-audience callout (humans + AI trigger)
- Body rendered with collapsible sections
- Structure panel showing scripts/, references/, agents/, assets/ tree
- Related skills via WikiLinks and dependency chains
- Action buttons: export, validate, open in Claude Code

### Create Mode (Guided Wizard)
- Step-by-step skill creation: name, category, description, body
- Description writing assistant with fill-in-the-blank + quality heuristic
- Template gallery with previews
- AI-assisted skill body generation via Claudian integration

### Vault Generator (Companion Script)
- Python script imports skills from any source into Obsidian vault
- Generates Canvas maps, Dataview dashboard, graph-view-ready WikiLinks
- Supports gstack .tmpl format, Anthropic standard, and community variants

## Requirements

- Obsidian 1.8.9+
- Recommended plugins: Dataview, Templater, Buttons

## Companion Tools

- [skill-lint](https://github.com/patchmyday/skill-lint) — Static analysis and scoring for SKILL.md files

## Status

Under development. See [design spec](docs/design.md) for full architecture.

## License

MIT
