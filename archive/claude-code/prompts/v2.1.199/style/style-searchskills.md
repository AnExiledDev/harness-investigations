---
id: style-searchskills
name: Output Style: SearchSkills
category: style
subcategory: output_style
source_line: 562763
original_metadata:
  styleName: "SearchSkills"
  description: "Search the user's claude.ai skills by keyword to find skills that might help complete the task."
---

Search the user's claude.ai skills by keyword. Call this when a skill (a reference document or instruction set the user has uploaded or enabled) might help complete the task.

Examples:
- "follow the team's PR guidelines" \u2192 keywords ["pr", "review", "guidelines"]
- "export this as a slide deck" \u2192 keywords ["pptx", "slides", "presentation"]

Returns a ranked list with id, name, description, and whether the skill is enabled. When results fit, call SuggestSkills to render the add card. If nothing relevant, proceed without mentioning that you searched.
