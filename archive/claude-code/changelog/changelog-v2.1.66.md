# Changelog for version 2.1.66


## Summary

This release removes the ultraplan mode and the remote-control server subcommand, replaces the `/reload-plugins` workflow with a restart-based plugin activation model, and enhances the microcompaction system with boundary messages and tool result clearing. It also introduces a new `forkContext` property for agent definitions, improved parallel tool call error handling, and a redesigned Plugin Status UI.

### Sub-Agent Context Forking (`forkContext`)

What: Agents can now receive the full parent conversation context when spawned as sub-agents, enabling better awareness of what the user has been working on.

Details:
- New `forkContext` frontmatter field for agent `.md` definitions (set to `true` or `false`)
- When enabled, the sub-agent receives prior conversation messages as read-only context
- Agents with `forkContext: true` must use `model: inherit` to avoid context length mismatch
- A new `### FORKING CONVERSATION CONTEXT ###` boundary marker is injected to clearly separate inherited context from the sub-agent's own task
- The sub-agent is instructed to only use tools available in its own system prompt, even if context messages reference other tools

Evidence: Sub-agent entry system (search for `"sub_agent_entered"` and `"FORKING CONVERSATION CONTEXT"`)


### Plugin Status and Error UI

What: New interactive UI views for inspecting plugin installation status and diagnosing loading errors.

Details:
- **Plugin Status** view shows installation progress for marketplaces and plugins (pending, installing, installed, failed)
- **Plugin Loading Errors** view lists all plugin load failures with detailed error messages and actionable remediation hints
- Error types include: path-not-found, git-auth-failed, network-error, manifest-parse-error, marketplace-blocked-by-policy, and more
- Each error includes a `→` arrow hint suggesting how to fix the issue (e.g., "→ Check your internet connection and try again", "→ Configure SSH keys or use HTTPS URL instead")

Evidence: Plugin error UI (search for `"Plugin Loading Errors"` and `"Plugin Status"`)


### Background Plugin Installation

What: Plugins and marketplaces from settings are now automatically installed in the background when they are missing.

Details:
- On startup, Claude Code detects plugins referenced in settings that are not yet installed
- Missing marketplaces are installed first, then missing plugins from those marketplaces
- Installation progress is tracked per-plugin with states: pending → installing → installed/failed
- Plugins from unknown/unconfigured marketplaces are flagged as uninstallable with clear error messages
- New telemetry event `tengu_marketplace_background_install` tracks installation success/failure rates

Evidence: Background plugin installer (search for `"plugins automatically"` and `"Setting installation status"`)


### Plugin Enable/Disable with Scope Support

What: Plugins can now be enabled or disabled at specific scopes (user, project, local), with validation for managed plugins.

Details:
- Enabling/disabling a plugin now persists the setting at the appropriate scope
- Managed plugins (from enterprise policy) cannot be enabled or disabled — only updated
- If a `--scope` argument is provided but doesn't match the plugin's actual scope, a helpful error message is shown
- Success messages include the plugin name and scope: `"Successfully enabled plugin: X (scope: user)"`

Evidence: Plugin scope management (search for `"Managed plugins cannot be"` and `"is installed at"`)


### Restart-Based Plugin Activation (Replaces /reload-plugins)

The `/reload-plugins` command has been removed. After installing, enabling, disabling, or updating plugins, Claude Code now displays messages like:

- `"✓ Installed X. Restart Claude Code to load new plugins."`
- `"Configuration saved. Restart Claude Code for changes to take effect."`

This replaces the previous `"Run /reload-plugins to activate"` workflow with a cleaner restart model.

Evidence: Plugin restart messages (search for `"Restart Claude Code"`)


### Enhanced Microcompaction with Boundary Messages

The automatic context microcompaction system now produces visible boundary messages when it operates. When tool results are cleared to save context space, a `"Context microcompacted"` system message is inserted with metadata including token counts saved, number of tool results compacted, and images cleared. Old tool results are replaced with `"[Old tool result content cleared]"` markers that point to saved files on disk.

Evidence: Microcompaction boundaries (search for `"Context microcompacted"` and `"[Old tool result content cleared]"`)


### Sibling Tool Call Error Handling

When multiple tools run in parallel and one fails, the remaining sibling tool calls now receive a clean error message (`"Sibling tool call errored"`) instead of hanging or producing ambiguous results. This improves reliability when using parallel tool execution.

Evidence: Parallel tool error handling (search for `"Sibling tool call errored"`)


### Updated Input Guides

New contextual keyboard shortcut hints appear during various interactions:
- `"ctrl+c to interrupt · Esc again to clear"` during active operations
- `"Tab to complete · Enter to add · Esc to cancel"` in settings input
- `"↑/↓ to select · Enter to confirm · Esc to cancel"` in selection lists

Evidence: Input guides (search for `"ctrl+c to interrupt"`)


### Remote Control Simplified

The `claude remote-control` command has been simplified. The `server` subcommand and its associated options (`--spawn-worktree-sessions`, `--spawn-same-dir-sessions`, `--max-sessions`, `--idle-timeout`, `--workspace`, `--host`, `--port`) have been removed. The `--name` option has also been removed. Remote control now focuses solely on connecting a single terminal for remote sessions via claude.ai/code.

Evidence: Simplified remote-control help text (search for `"Remote Control - Connect your local environment"`)


### Output Efficiency System Upgraded [Gradual Rollout]

The output brevity system has been upgraded from a single on/off toggle (`tengu_sotto_voce`) to a three-tier system (`tengu_swann_brevity`) with modes:
- **strict**: Extremely concise — "Use the fewest words necessary. Omit preamble, filler, pleasantries."
- **focused**: Extra concise — "Lead with the answer or action, not the reasoning."
- **polished**: Balanced — "Concise and polished. Never omit important information."

Evidence: Output efficiency modes (search for `"tengu_swann_brevity"`)


### Model Update Notification

The model migration notification has changed from "Model updated to Opus 4.6" to "Model updated to Opus 4.5", reflecting changes in default model availability for certain account types.

Evidence: Model migration notification (search for `"Model updated to Opus 4.5"`)


### Ultraplan Mode Removed

The `ultraplan` mode has been completely removed. This includes the `ultraplan` and `ultraplan-mode` identifiers, the ultraplan completion messages, and the verification specialist agent that was part of the ultraplan workflow.

Evidence: All `"ultraplan"` references removed from source


### Scheduled Skills Removed

The scheduled skills system (cron-based skill execution) has been removed. This includes the schedule display formatting (`"Every hour"`, `"Every day at"`, `"Weekdays at"`), the scheduled skills UI, and the scheduled skills status line.

Evidence: All `"scheduled skill"` and `"Scheduled skill"` references removed


### Voice Mode Tip Removed

The tip `"Voice mode is now available · /voice to enable"` has been removed.

Evidence: String `"Voice mode is now available"` removed


### Claude Code Desktop Cross-Promotion Removed

The following promotional elements have been removed:
- `"Try Claude Code Desktop"` callout
- `"Open in Claude Code Desktop"` button/link
- `"Same Claude Code with visual diffs, live app preview, parallel sessions, and more"` description

Evidence: All Desktop cross-promotion strings removed


### /btw Side Question Tip Removed

The tip text `"Use /btw to ask a quick side question without interrupting Claude's current work"` has been removed. Note: The `/btw` command itself still exists and functions — only the tip promoting it has been removed.

Evidence: Tip string `"Use /btw to ask a quick side question"` removed; `/btw` regex pattern still present (search for `"/btw"`)


### Code Intelligence Description Removed

The description string `"code intelligence (definitions, references, symbols, hover)"` for LSP features has been removed from the codebase.

Evidence: String `"code intelligence (definitions, references, symbols, hover)"` removed
