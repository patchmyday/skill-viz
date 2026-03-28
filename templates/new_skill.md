---
name: <%* const name = await tp.system.prompt("Skill name (lowercase-hyphens)") %><%* tR += name %>
description: <%* const purpose = await tp.system.prompt("What does this skill do? (one sentence)"); const trigger = await tp.system.prompt("When should Claude auto-start this? (e.g., 'user mentions .pdf files')"); tR += `Use when ${purpose}. TRIGGER when ${trigger}.` %>
tags:
  - skill
  - <%* const cat = await tp.system.suggester(["Document", "Dev Tool", "Creative", "Content", "Meta/Workflow", "API", "Other"], ["category/document", "category/dev", "category/creative", "category/content", "category/meta", "category/api", "category/other"]); tR += cat %>
---

# <% name %>

> <% `Use when ${purpose}. TRIGGER when ${trigger}.` %>

## Overview

[Describe what this skill does and when Claude should use it]

## Instructions

[Step-by-step instructions for Claude to follow]

## Examples

[Show example inputs and expected behavior]

## Gotchas

[Common pitfalls and how to avoid them]
