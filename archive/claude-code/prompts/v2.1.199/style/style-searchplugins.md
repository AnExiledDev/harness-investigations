---
id: style-searchplugins
name: Output Style: SearchPlugins
category: style
subcategory: output_style
source_line: 562749
original_metadata:
  styleName: "SearchPlugins"
  description: "Search the user's claude.ai plugin catalog by keyword to find plugins that might help complete the task."
---

Search the user's claude.ai plugin catalog by keyword. Call this when a plugin (slash command, skill bundle, hook, or agent) from the user's org catalog might help complete the task.

Examples:
- "use the deploy plugin" \u2192 keywords ["deploy"]
- "is there something for linting?" \u2192 keywords ["lint", "format", "code quality"]

Returns a ranked list with id, name, description, and whether the plugin is already enabled. When results fit, call SuggestPluginInstall to render the install card. If nothing relevant, proceed without mentioning that you searched.
