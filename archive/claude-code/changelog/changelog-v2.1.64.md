# Changelog for version 2.1.64


## Summary

This is a substantial release that introduces Remote Control server mode for multi-session management from claude.ai/code, an "ultraplan" mode for more thorough planning, scheduled skills, a `/reload-plugins` command for hot-reloading plugins without restart, and mouse-based text selection in the terminal. It also adds Claude Code Desktop integration, a new `InstructionsLoaded` hook event, built-in plugins, new bash security checks against command obfuscation, and updates the default model to Opus 4.6.


### Remote Control Server Mode

What: The `claude remote-control` command gains a `server` subcommand that runs as a persistent server accepting multiple concurrent sessions, with isolation and session management options.

Usage:
```bash
# Each session gets its own git worktree (up to N concurrent)
claude remote-control server --spawn-worktree-sessions [<N>]

# All sessions share the current directory (up to N concurrent)
claude remote-control server --spawn-same-dir-sessions [<N>]
```

Details:
- `--idle-timeout <ms>` controls how long detached sessions remain alive (0 = never)
- `--max-sessions <n>` caps concurrent sessions (0 = unlimited)
- `--auth-token <token>` adds bearer token authentication; auto-generates tokens with `sk-ant-cc-` prefix if omitted
- `--workspace <dir>` sets the default working directory for sessions
- `--host <string>` and `--port <number>` control bind address
- Sessions can connect via unix domain sockets using the `cc+unix://` protocol
- Session lifecycle is tracked in `server-sessions.json`
- The previous `claude remote-control` (without `server`) for single-session use still works

Evidence: Server session manager (search for `"--spawn-worktree-sessions"`, `"server-sessions.json"`, `"sk-ant-cc-"`)


### Ultraplan Mode

What: A new planning mode that delegates plan creation to a remote session for more thorough, multi-step planning before implementation begins.

Details:
- When triggered, Claude enters "ultraplan" mode and generates a comprehensive plan via a dedicated remote session
- The completed plan is written to the plan file and presented to the user for approval
- Users then review the ultraplan and Claude responds with a summary before proceeding
- Gated as a `prePlanMode` option alongside the existing plan mode

Evidence: Ultraplan orchestration (search for `"ultraplan"`, `"Ultraplanning…"`, `"Ultraplan complete"`)


### Scheduled Skills

What: Skills can now be scheduled to run on a cron-like schedule, executing automatically at specified intervals or times.

Details:
- Supports cron expression syntax with human-readable formatting (e.g., "Every hour", "Every day at 3:00 PM EST", "Weekdays at 9:00 AM EST")
- Schedule types include `load` (on startup), `every` (interval-based), and cron expressions
- The UI displays "1 scheduled skill" / "N scheduled skills" in the status area
- Users can view scheduled skill details and dismiss the notification

Evidence: Scheduling engine (search for `"scheduled skill"`, `"Every hour"`, `"Weekdays at"`)


### `/reload-plugins` Command

What: A new slash command that hot-reloads plugin changes in the current session without requiring a restart.

Usage:
```
/reload-plugins
```

Details:
- Activates pending plugin installations, configuration changes, and enable/disable toggling
- Throughout the plugin system, messages now say "Run /reload-plugins to activate" instead of the previous "Restart Claude Code to apply changes"
- Clears all plugin caches and reloads hooks, MCP servers, skills, commands, and agents

Evidence: Plugin hot-reload (search for `"/reload-plugins"`, `"Activate pending plugin changes"`)


### Mouse Text Selection and Copy

What: Terminal UI now supports mouse-based text selection with click-and-drag, and copying selected text to the clipboard.

Details:
- Click and drag to select text regions in the terminal output
- Selection is rendered with inverse colors to highlight the selected area
- Provides `copySelection()`, `clearSelection()`, and `hasSelection()` APIs
- Uses OSC 52 escape sequences to copy to the system clipboard

Evidence: Selection engine (search for `"copySelection"`, `"clearTextSelection"`, `"hasTextSelection"`)


### `InstructionsLoaded` Hook Event

What: A new hook event type that fires whenever an instruction file (CLAUDE.md or a rule file) is loaded during a session.

Details:
- Hook receives context about which instruction file was loaded
- Can be used for auditing, logging, or dynamically responding to instruction changes
- Follows the same async/sync hook response patterns as other hook events

Evidence: Hook registration (search for `"InstructionsLoaded"`, `"When an instruction file (CLAUDE.md or rule) is loaded"`)


### Built-in Plugins

What: Introduces the concept of built-in plugins that ship with Claude Code and cannot be uninstalled or updated by users.

Details:
- Built-in plugins are identified by the `@builtin` source suffix
- They can be enabled or disabled via user settings but not removed
- Attempting to update or uninstall shows: "Built-in plugins cannot be updated or uninstalled."
- Built-in plugins can provide skills, hooks, and MCP servers just like regular plugins

Evidence: Built-in plugin system (search for `"Built-in plugin"`, `"@builtin"`, `"Built-in plugins cannot be updated or uninstalled"`)


### Claude Code Desktop Integration

What: New UI elements promote and integrate with Claude Code Desktop, a companion application with visual diffs, live app preview, and parallel sessions.

Details:
- "Try Claude Code Desktop" dialog appears as a suggestion
- "Open in Claude Code Desktop" option available in menus
- "Continue your session in Claude Code Desktop" enables session handoff
- Described as: "Same Claude Code with visual diffs, live app preview, parallel sessions, and more."

Evidence: Desktop integration (search for `"Claude Code Desktop"`, `"Open in Claude Code Desktop"`)


### Git Subdirectory Plugin Source

What: A new `git-subdir` plugin source type that allows installing plugins from a subdirectory within a larger git repository (monorepo).

Details:
- Uses git sparse-checkout with `--filter=tree:0` to minimize bandwidth
- Requires git version 2.25 or later for cone mode support
- Supports pinning to a specific branch or SHA
- Falls back to unshallow fetch if shallow SHA fetch fails
- Accepts GitHub `owner/repo` shorthand, HTTPS, or SSH URLs

Evidence: Monorepo plugin source (search for `"git-subdir"`, `"sparse-checkout"`, `"--filter=tree:0"`)


### `asyncRewake` Hook Option

What: A new hook configuration option that allows hooks to run in the background and wake the model when they encounter a blocking error (exit code 2).

Details:
- When `asyncRewake: true`, the hook runs asynchronously like `async: true`
- If the hook exits with code 2, it signals a blocking error that wakes the model
- The blocking error message from the hook command is surfaced to the user
- New `"Stop hook blocking error"` notification type when this occurs

Evidence: Async rewake hooks (search for `"asyncRewake"`, `"If true, hook runs in background and wakes the model on exit code 2"`)


### `commitWorkflowInstructions` Setting

What: A new boolean setting that controls whether Claude's system prompt includes built-in commit and PR workflow instructions.

Usage:
```json
{
  "commitWorkflowInstructions": false
}
```

Details:
- Default: `true` (instructions are included)
- When disabled, Claude will not receive the built-in guidance for git commit messages and PR creation
- Useful for teams that have their own commit/PR conventions via CLAUDE.md

Evidence: Setting definition (search for `"Include built-in commit and PR workflow instructions"`)


### `showThinkingSummaries` Setting

What: A new boolean setting that controls whether thinking summaries are displayed in the transcript view.

Details:
- Default: `false`
- When enabled, thinking process summaries appear in the transcript view (ctrl+o)
- Also gated behind the `tengu_quiet_hollow` feature flag

Evidence: Setting definition (search for `"Show thinking summaries in the transcript view"`)


### Bash Command Security Checks

What: New security checks detect and flag potentially obfuscated bash commands that could bypass permission checks.

Details:
- Detects commands containing quoted newlines followed by `#`-prefixed lines, which can hide arguments from line-based permission scanning
- Detects consecutive quote characters at word start (potential obfuscation)
- Detects empty quote pairs adjacent to quoted dashes (flag obfuscation)
- Sanitizes redirects to Windows `NUL` device by replacing with `/dev/null`
- Flagged commands trigger an "ask" behavior requiring explicit user approval

Evidence: Security checks (search for `"potential obfuscation"`, `"quoted newline"`, `"$1/dev/null"`)


### Default Model Updated to Opus 4.6

The model promotion banner now reads "Model updated to Opus 4.6" (previously "Opus 4.5"), reflecting the new default model.

Evidence: Model banner (search for `"Opus 4.6"`)


### Simplified Output Brevity System

The previous three-tier brevity system (`tengu_swann_brevity` with `strict`/`focused`/`polished` levels) has been replaced by a single `tengu_sotto_voce` feature flag that, when enabled, injects a streamlined output efficiency instruction. This simplifies server-side control of model verbosity.

Evidence: Brevity flag (search for `"tengu_sotto_voce"`)


### Parallel Plugin Loading

Plugin commands, skills, and agents are now loaded using `Promise.all` for concurrent processing, improving startup time when multiple plugins are installed. Previously, plugins were loaded sequentially in `for` loops.

Evidence: Parallel loading (search for `"Promise.all"` in the plugin loading functions)


### Parallel Async Hook Processing

The hook response system now uses `Promise.allSettled` to check all pending async hooks concurrently rather than sequentially. Failed hook callbacks are caught and logged individually without blocking other hooks.

Evidence: Hook processing (search for `"checkForAsyncHookResponses callback rejected"`)


### Improved Parallel Tool Call Error Handling

When a parallel tool call fails, sibling tool calls now receive a clearer cancellation message: "Cancelled: parallel tool call \<name\> errored" — replacing the previous generic "Sibling tool call errored" message. This helps identify which specific tool caused the failure.

Evidence: Error message (search for `"Cancelled: parallel tool call"`)


### Hook Context Fields for Subagents

Hook event payloads now include `agent_type` and `agent_id` fields, providing context about whether the hook fired from a subagent and which agent type triggered it. This allows hook scripts to behave differently based on agent context.

Evidence: Hook schema (search for `"Agent type name"`, `"Subagent identifier"`)


### TaskCompleted and TeammateIdle Hooks Can Block Continuation

The `TaskCompleted` and `TeammateIdle` hook events can now prevent the session from continuing when they return a blocking response, surfacing messages like "TaskCompleted hook prevented continuation".

Evidence: Hook blocking (search for `"TaskCompleted hook prevented continuation"`, `"TeammateIdle hook prevented continuation"`)


### ToolSearch Multi-Select

The ToolSearch tool now supports comma-separated tool names for loading multiple tools in a single call (e.g., `select:Read,Edit,Grep`), reducing the number of round-trips needed to load tools.

Evidence: ToolSearch docs (search for `"select:Read,Edit,Grep"`)


### Binary Content Handling for MCP

Binary content from MCP tool results is now saved to disk with proper MIME type detection and file extension mapping, rather than being displayed inline. Supports a comprehensive set of MIME types including Office documents, audio, video, and archives.

Evidence: Binary content handling (search for `"Binary content ("`, `"application/vnd.openxmlformats"`)


### Plugin Trust Message Policy Setting

Enterprise administrators can now configure a custom `pluginTrustMessage` in policy settings (managed-settings.json / MDM) that is appended to the plugin trust warning shown before installation.

Evidence: Trust message (search for `"pluginTrustMessage"`, `"Custom message to append to the plugin trust warning"`)


### Plugin Error UI Redesigned

The plugin error view has been completely rewritten with actionable guidance for each error type. Errors now show the source scope (user/project/local/managed), provide specific remediation actions (navigate to settings, remove marketplace, contact admin), and allow direct resolution from the error list.

Evidence: Error UI (search for `"Managed by your organization — contact your admin"`, `"Restart to retry loading plugins"`)


### `pathPattern` for Marketplace Source Matching

A new `pathPattern` field in `strictKnownMarketplaces` settings allows regex-based matching against file and directory plugin sources, complementing the existing `hostPattern` for network sources.

Evidence: Path matching (search for `"pathPattern"`, `"Regex pattern matched against the .path field"`)


### Voice Mode Notification Banner

A new notification banner "Voice mode is now available · /voice to enable" appears when voice mode is detected as available, improving discoverability of the feature.

Evidence: Voice notification (search for `"Voice mode is now available"`)


### Improved Worktree File Copying

The `.worktreeinclude` file processing for worktree sessions now uses `ignore` pattern matching (similar to `.gitignore`) instead of simple file list comparison, supporting glob patterns and directory matching for more flexible file copying into worktrees.

Evidence: Worktree include (search for `".worktreeinclude"`)


### Fast Mode Network Error Handling

When fast mode status cannot be determined due to network connectivity issues, it now defaults to `disabled (network_error)` with the message "Fast mode unavailable due to network connectivity issues" instead of silently failing.

Evidence: Fast mode fallback (search for `"Fast mode unavailable due to network connectivity issues"`)


## Bug Fixes

- Fixed stale lock file handling: lock files can now be force-removed when they become stale, with logging of the cleanup (search for `"Force-removed lock file at"`)
- LSP diagnostics state is now properly reset when clearing state, preventing stale diagnostic data from persisting (search for `"LSP Diagnostics: Resetting all state"`)
- MCP config validation now produces clearer error messages: `"--mcp-config validation failed"` and `"MCP config is not valid JSON"` replace generic parse errors (search for `"--mcp-config validation failed"`)
- Symlink-aware path resolution added for filesystem operations, properly following symlinks through intermediate path components (search for `"isSymbolicLink"` in function `Oiq`)


### Search Hints in Tool List [Gradual Rollout]

What: Tool names in the deferred tool list can display alongside a short description hint (e.g., "Read — read files, images, PDFs, notebooks"), making it easier to identify the right tool.

Status: Feature-flagged behind `tengu_tst_hint_m7r` and overridable via `CLAUDE_CODE_SEARCH_HINTS_IN_LIST` env var.

Details:
- Every built-in tool now has a `searchHint` property with a short plain-English description
- When enabled, the tool list displays `"ToolName — description"` format
- Hints include descriptions like "execute shell commands", "search file contents with regex (ripgrep)", "delegate work to a subagent"
- Environment variable takes precedence over feature flag (set to `1` to enable, `0` to disable)

Evidence: Search hints (gated by `tengu_tst_hint_m7r`, search for `"searchHint"`, `"CLAUDE_CODE_SEARCH_HINTS_IN_LIST"`)
