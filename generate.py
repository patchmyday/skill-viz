#!/usr/bin/env python3
"""Skill-viz vault generator v0.1 — creates an Obsidian vault from skill directories."""

import json
import re
import shutil
from datetime import date
from pathlib import Path

import yaml


def load_config(config_path: Path) -> dict:
    """Load and resolve paths in config.yaml."""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    config["output"] = Path(config["output"]).expanduser().resolve()
    for source in config.get("sources", []):
        source["path"] = Path(source["path"]).expanduser().resolve()
    return config


def parse_skill_md(skill_md_path: Path) -> dict | None:
    """Parse a SKILL.md file into frontmatter dict + body string."""
    text = skill_md_path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.+?)\n---\n?(.*)", text, re.DOTALL)
    if not match:
        return None
    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    if not isinstance(frontmatter, dict):
        return None
    return {
        "frontmatter": frontmatter,
        "body": match.group(2).strip(),
        "path": skill_md_path,
    }


def scan_sources(config: dict) -> list[dict]:
    """Find all SKILL.md files across configured sources."""
    skills = []
    for source in config.get("sources", []):
        source_path = source["path"]
        if not source_path.exists():
            continue
        for skill_md in sorted(source_path.rglob("SKILL.md")):
            parsed = parse_skill_md(skill_md)
            if parsed:
                parsed["source_label"] = source.get("label", str(source_path))
                skills.append(parsed)
    return skills


def detect_structure(skill_dir: Path) -> dict:
    """Detect which optional components a skill directory has."""
    return {
        "scripts": list(skill_dir.glob("scripts/*")) if (skill_dir / "scripts").is_dir() else [],
        "references": [
            p for p in skill_dir.iterdir()
            if p.suffix == ".md" and p.name not in ("SKILL.md", "LICENSE.txt")
        ] + (list((skill_dir / "reference").iterdir()) if (skill_dir / "reference").is_dir() else [])
        + (list((skill_dir / "references").iterdir()) if (skill_dir / "references").is_dir() else []),
        "agents": list((skill_dir / "agents").iterdir()) if (skill_dir / "agents").is_dir() else [],
        "assets": list((skill_dir / "assets").iterdir()) if (skill_dir / "assets").is_dir() else [],
        "evals": [p for p in skill_dir.rglob("*.eval.yaml")] + [p for p in skill_dir.rglob("*.eval.yml")],
    }


def assign_category(skill_name: str, description: str, config: dict) -> str:
    """Assign a category to a skill based on config mapping or keyword heuristics."""
    categories = config.get("categories", {})
    for category, names in categories.items():
        if skill_name in names:
            return category
    # Keyword fallback
    desc_lower = description.lower()
    keyword_map = {
        "document": ["pdf", "docx", "pptx", "xlsx", "spreadsheet", "word", "slide", "presentation"],
        "dev": ["test", "debug", "playwright", "mcp", "frontend", "webapp", "build"],
        "creative": ["art", "design", "gif", "canvas", "brand", "theme", "visual"],
        "content": ["write", "author", "documentation", "comms", "communication"],
        "api": ["api", "sdk", "endpoint"],
        "meta": ["skill", "creator", "meta"],
    }
    for category, keywords in keyword_map.items():
        if any(kw in desc_lower for kw in keywords):
            return category
    return "other"


def find_related_skills(skill: dict, all_skills: list[dict], config: dict) -> list[str]:
    """Find related skills: same category, mentioned in body, or benefits-from."""
    name = skill["frontmatter"].get("name", "")
    desc = skill["frontmatter"].get("description", "")
    category = assign_category(name, desc, config)
    related = set()

    # Same category
    for other in all_skills:
        other_name = other["frontmatter"].get("name", "")
        if other_name == name:
            continue
        other_desc = other["frontmatter"].get("description", "")
        if assign_category(other_name, other_desc, config) == category:
            related.add(other_name)

    # Mentioned in body
    for other in all_skills:
        other_name = other["frontmatter"].get("name", "")
        if other_name == name:
            continue
        if other_name in skill["body"]:
            related.add(other_name)

    # benefits-from field
    benefits = skill["frontmatter"].get("benefits-from", [])
    if isinstance(benefits, list):
        related.update(benefits)

    return sorted(related)


def generate_skill_note(skill: dict, structure: dict, related: list[str], config: dict) -> str:
    """Generate an Obsidian note for a single skill."""
    fm = skill["frontmatter"]
    name = fm.get("name", "unknown")
    description = fm.get("description", "")
    category = assign_category(name, description, config)
    today = date.today().isoformat()

    # Build frontmatter
    note_fm = {
        "name": name,
        "description": description,
        "source": str(skill["path"]),
        "tags": ["skill", f"category/{category}"],
        "has_scripts": bool(structure["scripts"]),
        "has_references": bool(structure["references"]),
        "has_agents": bool(structure["agents"]),
        "has_assets": bool(structure["assets"]),
        "has_evals": bool(structure["evals"]),
        "last_synced": today,
    }

    lines = ["---"]
    lines.append(yaml.dump(note_fm, default_flow_style=False, sort_keys=False).strip())
    lines.append("---")
    lines.append("")
    lines.append(f"# {name}")
    lines.append("")

    # Description as blockquote
    if description:
        lines.append(f"> {description}")
        lines.append("")

    # Body
    if skill["body"]:
        lines.append("## Instructions")
        lines.append("")
        lines.append(skill["body"])
        lines.append("")

    # Structure table
    components = []
    if structure["scripts"]:
        files = ", ".join(f"`{p.name}`" for p in structure["scripts"])
        components.append(("Scripts", files))
    if structure["references"]:
        files = ", ".join(f"`{p.name}`" for p in structure["references"])
        components.append(("References", files))
    if structure["agents"]:
        files = ", ".join(f"`{p.name}`" for p in structure["agents"])
        components.append(("Agents", files))
    if structure["assets"]:
        files = ", ".join(f"`{p.name}`" for p in structure["assets"])
        components.append(("Assets", files))
    if structure["evals"]:
        files = ", ".join(f"`{p.name}`" for p in structure["evals"])
        components.append(("Evals", files))

    if components:
        lines.append("## Structure")
        lines.append("")
        lines.append("| Component | Files |")
        lines.append("|-----------|-------|")
        for comp_name, comp_files in components:
            lines.append(f"| {comp_name} | {comp_files} |")
        lines.append("")

    # Related skills
    if related:
        lines.append("## Related Skills")
        lines.append("")
        lines.append(" | ".join(f"[[{r}]]" for r in related))
        lines.append("")

    return "\n".join(lines)


def generate_dashboard(skills: list[dict], config: dict) -> str:
    """Generate _Dashboard.md with Dataview queries."""
    categories = config.get("categories", {})
    category_labels = {
        "document": "Document Skills",
        "dev": "Dev Tools",
        "creative": "Creative Skills",
        "content": "Content Skills",
        "meta": "Meta / Workflow",
        "api": "API Skills",
        "other": "Other",
    }

    lines = ["# Skill Dashboard", ""]

    lines.append("## All Skills")
    lines.append("")
    lines.append("```dataview")
    lines.append('TABLE description AS "Trigger", has_scripts AS "Scripts", has_references AS "Refs", join(tags, ", ") AS "Tags"')
    lines.append('FROM "skills"')
    lines.append('WHERE contains(tags, "skill")')
    lines.append("SORT name ASC")
    lines.append("```")
    lines.append("")

    lines.append("## By Category")
    lines.append("")

    # Collect all categories that have skills
    seen_categories = set()
    for skill in skills:
        name = skill["frontmatter"].get("name", "")
        desc = skill["frontmatter"].get("description", "")
        seen_categories.add(assign_category(name, desc, config))

    for cat in ["document", "dev", "creative", "content", "meta", "api", "other"]:
        if cat not in seen_categories:
            continue
        label = category_labels.get(cat, cat.title())
        lines.append(f"### {label}")
        lines.append("")
        lines.append("```dataview")
        lines.append(f'TABLE WITHOUT ID link(file.link, name) AS "Skill", description AS "Trigger"')
        lines.append(f'FROM "skills"')
        lines.append(f'WHERE contains(tags, "category/{cat}")')
        lines.append("SORT name ASC")
        lines.append("```")
        lines.append("")

    lines.append("## Recently Synced")
    lines.append("")
    lines.append("```dataview")
    lines.append('TABLE last_synced AS "Last Synced"')
    lines.append('FROM "skills"')
    lines.append("SORT last_synced DESC")
    lines.append("LIMIT 10")
    lines.append("```")

    return "\n".join(lines)


def generate_canvas(skills: list[dict], config: dict) -> str:
    """Generate _Skill Map.canvas in JSON Canvas format."""
    nodes = []
    edges = []
    groups = []

    # Group skills by category
    by_category: dict[str, list[dict]] = {}
    for skill in skills:
        name = skill["frontmatter"].get("name", "")
        desc = skill["frontmatter"].get("description", "")
        cat = assign_category(name, desc, config)
        by_category.setdefault(cat, []).append(skill)

    category_colors = {
        "document": "1",  # blue
        "dev": "4",       # green
        "creative": "3",  # purple
        "content": "6",   # orange
        "meta": "0",      # gray
        "api": "5",       # cyan
        "other": "0",
    }

    node_positions = {}  # name -> (x, y) for edge routing
    col_spacing = 320
    row_spacing = 120
    group_padding = 40

    col = 0
    for cat, cat_skills in sorted(by_category.items()):
        x_base = col * (col_spacing + 200)
        color = category_colors.get(cat, "0")

        # Place skills in a column
        for i, skill in enumerate(cat_skills):
            name = skill["frontmatter"].get("name", "")
            desc = skill["frontmatter"].get("description", "")
            first_line = desc.split(".")[0] if desc else ""
            if len(first_line) > 80:
                first_line = first_line[:77] + "..."

            node_x = x_base + group_padding
            node_y = 80 + i * row_spacing
            node_id = f"skill-{name}"

            nodes.append({
                "id": node_id,
                "type": "text",
                "x": node_x,
                "y": node_y,
                "width": 280,
                "height": 80,
                "color": color,
                "text": f"**{name}**\n{first_line}",
            })
            node_positions[name] = (node_x, node_y, node_id)

        # Group node
        group_height = max(len(cat_skills) * row_spacing + group_padding, 160)
        groups.append({
            "id": f"group-{cat}",
            "type": "group",
            "x": x_base,
            "y": 0,
            "width": 280 + group_padding * 2,
            "height": group_height + 80,
            "color": color,
            "label": cat.title(),
        })
        col += 1

    # Edges between related skills
    edge_id = 0
    for skill in skills:
        name = skill["frontmatter"].get("name", "")
        desc = skill["frontmatter"].get("description", "")
        related = find_related_skills(skill, skills, config)
        for rel in related:
            if rel in node_positions and name in node_positions:
                # Only add edge once (alphabetical order)
                if name < rel:
                    edges.append({
                        "id": f"edge-{edge_id}",
                        "fromNode": f"skill-{name}",
                        "toNode": f"skill-{rel}",
                    })
                    edge_id += 1

    canvas = {
        "nodes": groups + nodes,
        "edges": edges,
    }
    return json.dumps(canvas, indent=2)


def generate_obsidian_config() -> dict[str, str]:
    """Generate .obsidian/ configuration files."""
    graph_json = json.dumps({
        "colorGroups": [
            {"query": "tag:#category/document", "color": {"a": 1, "r": 68, "g": 138, "b": 255}},
            {"query": "tag:#category/dev", "color": {"a": 1, "r": 72, "g": 199, "b": 116}},
            {"query": "tag:#category/creative", "color": {"a": 1, "r": 168, "g": 85, "b": 247}},
            {"query": "tag:#category/content", "color": {"a": 1, "r": 255, "g": 153, "b": 51}},
            {"query": "tag:#category/meta", "color": {"a": 1, "r": 153, "g": 153, "b": 153}},
            {"query": "tag:#category/api", "color": {"a": 1, "r": 0, "g": 200, "b": 200}},
        ]
    }, indent=2)

    community_plugins = json.dumps(["dataview", "templater-obsidian", "buttons"], indent=2)

    app_json = json.dumps({
        "showFrontmatter": True,
        "livePreview": True,
        "defaultViewMode": "preview",
    }, indent=2)

    return {
        "graph.json": graph_json,
        "community-plugins.json": community_plugins,
        "app.json": app_json,
    }


def generate_vault(config_path: Path):
    """Main entry point: generate the full Obsidian vault."""
    config = load_config(config_path)
    output = config["output"]

    # Clean and create output directory
    skills_dir = output / "skills"
    guides_dir = output / "_guides"
    templates_dir = output / "_templates"
    obsidian_dir = output / ".obsidian"

    for d in [skills_dir, guides_dir, templates_dir, obsidian_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Scan all skills
    skills = scan_sources(config)
    print(f"Found {len(skills)} skills across {len(config['sources'])} sources")

    # Generate skill notes
    for skill in skills:
        name = skill["frontmatter"].get("name", "unknown")
        skill_dir = skill["path"].parent
        structure = detect_structure(skill_dir)
        related = find_related_skills(skill, skills, config)
        note = generate_skill_note(skill, structure, related, config)

        note_path = skills_dir / f"{name}.md"
        note_path.write_text(note, encoding="utf-8")
        print(f"  Generated: skills/{name}.md")

    # Dashboard
    dashboard = generate_dashboard(skills, config)
    (output / "_Dashboard.md").write_text(dashboard, encoding="utf-8")
    print("  Generated: _Dashboard.md")

    # Canvas
    canvas = generate_canvas(skills, config)
    (output / "_Skill Map.canvas").write_text(canvas, encoding="utf-8")
    print("  Generated: _Skill Map.canvas")

    # Guides
    script_dir = Path(__file__).parent
    for guide_file in (script_dir / "guides").iterdir():
        if guide_file.suffix == ".md":
            shutil.copy2(guide_file, guides_dir / guide_file.name)
            print(f"  Generated: _guides/{guide_file.name}")

    # Template
    template_src = script_dir / "templates" / "new_skill.md"
    if template_src.exists():
        shutil.copy2(template_src, templates_dir / "New Skill.md")
        print("  Generated: _templates/New Skill.md")

    # Obsidian config
    obsidian_files = generate_obsidian_config()
    for filename, content in obsidian_files.items():
        (obsidian_dir / filename).write_text(content, encoding="utf-8")
        print(f"  Generated: .obsidian/{filename}")

    print(f"\nVault generated at: {output}")
    print(f"Open in Obsidian: File → Open Vault → {output}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        config_file = Path(sys.argv[1])
    else:
        config_file = Path(__file__).parent / "config.yaml"

    if not config_file.exists():
        print(f"Config not found: {config_file}")
        sys.exit(1)

    generate_vault(config_file)
