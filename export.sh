#!/usr/bin/env bash
# Export a skill note from the Obsidian vault back to Claude Code's SKILL.md format.
# Usage: ./export.sh <path-to-obsidian-note.md>

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <skill-note.md>"
    echo "Exports an Obsidian skill note back to a valid SKILL.md"
    exit 1
fi

NOTE_PATH="$1"

if [[ ! -f "$NOTE_PATH" ]]; then
    echo "Error: File not found: $NOTE_PATH"
    exit 1
fi

# Extract the source path from frontmatter
SOURCE=$(awk '/^---$/{n++; next} n==1 && /^source:/{print $2; exit}' "$NOTE_PATH")

if [[ -z "$SOURCE" ]]; then
    echo "Error: No 'source' field found in frontmatter"
    exit 1
fi

if [[ ! -f "$SOURCE" ]]; then
    echo "Warning: Original source not found at $SOURCE"
    read -rp "Create it? [y/N] " confirm
    if [[ "$confirm" != [yY] ]]; then
        exit 1
    fi
    mkdir -p "$(dirname "$SOURCE")"
fi

# Extract original frontmatter fields (strip Obsidian-specific ones)
# and the body content (everything after "## Instructions" until "## Structure" or "## Related")
python3 -c "
import re, yaml, sys

text = open('$NOTE_PATH').read()
match = re.match(r'^---\n(.+?)\n---\n?(.*)', text, re.DOTALL)
if not match:
    print('Error: Cannot parse frontmatter', file=sys.stderr)
    sys.exit(1)

fm = yaml.safe_load(match.group(1))
body = match.group(2).strip()

# Strip Obsidian-specific fields
for key in ['tags', 'has_scripts', 'has_references', 'has_agents', 'has_assets', 'has_evals', 'last_synced', 'source']:
    fm.pop(key, None)

# Extract body: skip the title line, take content from Instructions to Structure/Related
lines = body.split('\n')
output_lines = []
in_instructions = False
for line in lines:
    if line.startswith('## Instructions'):
        in_instructions = True
        continue
    if in_instructions and line.startswith('## Structure'):
        break
    if in_instructions and line.startswith('## Related'):
        break
    if in_instructions:
        output_lines.append(line)

# If no Instructions section, use body after title
if not output_lines:
    skip_title = False
    for line in lines:
        if not skip_title and line.startswith('# '):
            skip_title = True
            continue
        if skip_title and line.startswith('> '):
            continue
        if line.startswith('## Structure') or line.startswith('## Related'):
            break
        output_lines.append(line)

body_text = '\n'.join(output_lines).strip()

# Reconstruct SKILL.md
print('---')
print(yaml.dump(fm, default_flow_style=False, sort_keys=False).strip())
print('---')
print()
print(body_text)
" > "$SOURCE"

echo "Exported to: $SOURCE"
