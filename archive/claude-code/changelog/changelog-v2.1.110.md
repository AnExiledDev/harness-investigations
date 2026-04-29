# Changelog for version 2.1.110

## Summary

This release adds five new remote workflow slash commands (`/autopilot`, `/bugfix`, `/dashboard`, `/docs`, `/investigate`), a `/tui` command to switch between the classic and flicker-free fullscreen renderer, a `/focus` command for a minimal transcript view, a PushNotification tool (feature-flagged) for terminal and mobile alerts, plugin favorites, transcript undo, new settings for auto-scroll and external editor context, and the `/recap` command is now enabled by default. The idle-return ("You've been away") dialog has been removed.


### `/tui` Command — Switch Terminal Renderers

What: New slash command to switch between the classic main-screen renderer and the flicker-free fullscreen alt-screen renderer at runtime, without restarting.

Usage:
```
/tui fullscreen    # Switch to flicker-free alt-screen rendering (mouse support included)
/tui default       # Switch back to the classic renderer
```

Details:
- The fullscreen renderer is equivalent to setting `CLAUDE_CODE_NO_FLICKER=1` but can now be toggled within a session
- A new `tui` setting is persisted in global config, accepting `"default"` or `"fullscreen"`
- When switching to fullscreen, you'll see hints about mouse support: click to move your cursor, click to expand collapsed tool results, and text auto-copies on selection
- A new tip ("Try flicker-free rendering, now with mouse support · /tui fullscreen") will appear for users on the classic renderer

Evidence: `/tui` command handler (search for `"Usage: /tui <"` and `"Set the terminal UI renderer"`)


### `/focus` Command — Minimal Transcript View

What: New slash command that toggles a focus view, showing only your prompt, a tool summary, and the final response — hiding intermediate tool calls and verbose output.

Usage:
```
/focus    # Toggle focus view on/off
```

Details:
- Only available in the fullscreen TUI renderer
- When enabled, displays "Focus view enabled"; when disabled, displays "Focus view disabled"
- Backed by the existing `briefTranscript` state, now exposed as a convenient slash command

Evidence: Focus command definition (search for `"Toggle focus view"`)


### Remote Workflow Commands (`/autopilot`, `/bugfix`, `/dashboard`, `/docs`, `/investigate`)

What: Five new slash commands that spawn remote Claude Code sessions pre-configured for specific workflows. Each runs headlessly on Anthropic's infrastructure.

Usage:
```
/autopilot <task description>    # General-purpose autonomous agent
/bugfix <bug description>        # Reproduce, root-cause, fix, and regression-test a bug
/dashboard <data sources>        # Design and build a dashboard
/docs <feature area>             # Discover a feature surface and write/update docs
/investigate <incident details>  # Root-cause an incident and produce a fix report
```

Details:
- These extend the existing remote session system (previously only `/autofix-pr` existed)
- Requires the `allow_remote_sessions` organizational policy to be enabled
- Before spawning, the CLI checks for unpushed local commits and warns: "you have unpushed local commits. The remote session clones from GitHub, so they would not be included."
- If the current branch has no upstream, you'll be prompted to `git push -u origin HEAD` first

Evidence: Remote workflow definitions (search for `"Spawn a remote session that reproduces"` and `"Spawn a remote Claude Code session that runs the autopilot"`)


### Plugin Favorites

What: You can now favorite/unfavorite plugins in the plugin list for quicker access.

Usage:
- Press `f` in the plugin list to toggle a plugin as a favorite
- Favorites are persisted and appear with priority in the list
- The option also appears in the plugin options dialog: "Add to favorites" / "Remove from favorites"

Evidence: Plugin favorites UI (search for `"Add to favorites"` and `"plugin:favorite"`)


### Transcript Undo

What: New undo capability in the conversation UI that lets you revert certain actions, such as compaction, memory saves, and feedback surveys.

Details:
- An `handleUndo` callback is now available in post-compact surveys, memory surveys, and feedback components
- Adds a new `'pending'` state to the transcript state machine for undo transitions
- Also available in the autocomplete/suggestions component

Evidence: Undo handler wiring (search for `"handleUndo"`)


### Session Rename

What: Sessions can now be renamed programmatically via the SDK, and remote sessions automatically get renamed based on their git branch.

Details:
- New `rename_session` control action with description: "Sets the user-facing title for the current session."
- Title validation requires non-empty strings
- Remote sessions now include `onRenameSession` callbacks and `parseGitRemote` for automatic naming based on the repo branch

Evidence: Session rename handler (search for `"rename_session"` and `"title must be non-empty"`)


### Auto-Scroll Setting

What: New user-configurable setting to control automatic scrolling behavior in fullscreen mode.

Details:
- Available in Settings panel as "Auto-scroll"
- Description: "Auto-scroll conversation to bottom (fullscreen mode only)"
- Enabled by default
- Toggle via `/config` or the settings panel

Evidence: Auto-scroll setting definition (search for `"Auto-scroll"` and `"autoScrollEnabled"`)


### External Editor Context Setting

What: New setting that includes Claude's last response as commented context when opening the external editor.

Details:
- Available in Settings panel as "Show last response in external editor"
- Disabled by default
- When enabled, the external editor will prepend Claude's last response as `#`-prefixed comment lines above a separator: `# ─── Write your reply below this line ──────────────────────────`
- Claude's response is labeled: `# ─── Claude's last response (for reference; removed on save) ───`

Evidence: External editor context setting (search for `"Show last response in external editor"` and `"externalEditorContext"`)


### Daemon Version Management

What: A new background daemon system with a lock file (`daemon.lock`) that manages version consistency and auto-restart.

Details:
- The daemon lock file contains a PID and version, enabling version-mismatch detection
- If a running daemon's version differs from the current CLI, it signals a restart: "Signaled claude daemon to restart"
- Lock file validation ensures the process is still alive before taking action

Evidence: Daemon lock system (search for `"daemon.lock"` and `"Signaled claude daemon to restart"`)


### `/recap` and Away Summary Enabled by Default

The `tengu_sedge_lantern` feature flag, which controls both the `/recap` command and the away-from-session summary, has been changed from defaulting to `false` to defaulting to `true`. This means:
- The `/recap` command (generates a one-line session recap) is now available to all users without needing a feature flag rollout
- The away summary that detects when you've returned to a long session is now on by default

Evidence: Flag default change from `b8("tengu_sedge_lantern", !1)` to `I8("tengu_sedge_lantern", !0)` (search for `"tengu_sedge_lantern"`)


### Idle-Return Dialog Removed

The "You've been away" idle-return dialog (controlled by `tengu_willow_mode`) has been completely removed from the conversation UI. Previously, when you returned to a session after an idle period, a dialog would appear suggesting you clear context. This is now gone — the away summary feature (above) replaces it with a less intrusive approach.

Evidence: Removal of the `willow_mode`/`idle-return` render branch (search for the removed `"idle-return"` in changes diff)


### `/ultrareview` PR Review Mode

The `/ultrareview` command now supports a PR review mode that shows different messaging depending on whether you're reviewing a specific PR or the current branch:
- PR mode: "Reviewing PR #123 fetched from GitHub."
- Branch mode: "Reviewing current branch against main."
- New tip: "Tip: run /ultrareview (no number) to review your current branch instead." / "Tip: run /ultrareview <PR number> to fetch and review a specific GitHub PR instead."
- PR field queries now include `additions,deletions` for richer review context

Evidence: PR review mode strings (search for `"Reviewing PR #"`)


### MCP Server Conflict Detection

When the same MCP server name is defined in multiple configuration scopes (project, user, etc.) with different endpoints, a warning is now shown with specific remediation guidance.

Details:
- Warning: `Server "X" is defined in multiple scopes with different endpoints`
- Suggestion: `Keep the correct endpoint and remove the others: \`claude mcp remove X -s SCOPE\``
- Shows the `[Conflicting scopes]` label in `/doctor` diagnostics

Evidence: MCP conflict detection (search for `"is defined in multiple scopes with different endpoints"`)


### MCP Server Not-Found Error Improvements

When an MCP server is not found, the error message now lists all configured servers, helping you identify typos or misconfigurations.

Evidence: Improved error message (search for `". Configured servers:"`)


### Improved Untrusted Device Error Messages

Authentication errors now distinguish between two device-trust failure scenarios:
- `untrusted_device`: "run /login to enroll this device"
- `session_stale_relogin`: "session expired for trusted-device check — run /login to re-authenticate"

Evidence: Trust error messaging (search for `"session expired for trusted-device check"`)


### Cloud Workspace Environment Detection

Claude Code now detects additional cloud development environments: Coder, DevPod, and Daytona workspaces, alongside existing cloud detection.

Evidence: Workspace detection (search for `"CODER"` and `"DevPod"` and `"Daytona"`)


### Expanded Terminal Emulator Support

The terminal detection system now recognizes Tabby alongside the previously supported set. The ARM64 architecture detection has also been improved for Linux platform identification.

Evidence: Terminal emulator detection (search for `"Tabby"`)


### Edit Tool Backward Compatibility

The Edit tool now accepts the older `old_str`/`new_str` parameter names, automatically migrating them to `old_string`/`new_string`. This improves compatibility with older model outputs or cached tool schemas.

Evidence: Parameter migration (search for `"old_str"`)


### Plugin Dependency Auto-Installation

MCP plugins that declare dependencies in `plugin.json` are now automatically installed if they're from a compatible marketplace. Cross-marketplace dependencies are validated and blocked with an informative message.

Details:
- Validates marketplace compatibility before auto-installing
- Shows truncated dependency lists: "dep1, dep2, dep3, dep4, dep5 (+ N dependencies)"
- Plugins from different marketplaces show: "not auto-installing — install it manually"
- Plugins not found in any marketplace are flagged: "not auto-installing"
- Deprecation notes (`depNote`) are now surfaced in plugin installation feedback

Evidence: Plugin dependency system (search for `"plugin.json declares dependency"`)


### Remote Session Environment Change

Remote sessions now use Bun's `--smol` option for reduced memory usage instead of the previous `ulimit -Sd` memory limit approach. This is more appropriate for the Bun runtime and avoids shell-level resource limits.

Evidence: Remote environment setup (search for `"BUN_OPTIONS"` and the removal of `"ulimit -Sd"`)


### Hook Security Enhancement

When a hook rewrites the user's input, permissions are now re-validated against the modified input. This prevents hooks from bypassing permission checks by rewriting a denied command into something different.

Evidence: Permission re-validation (search for `"ask rule on hook-rewritten input"`)


### Worktree Lock on Creation

Git worktrees created by Claude Code agents are now locked with `git worktree lock --reason` to prevent accidental pruning by other Git operations.

Evidence: Worktree locking (search for `"worktree"` and `"lock"` and `"--reason"`)


### Settings Panel Expansion

The settings panel now includes four configurable options:
1. Auto-scroll (fullscreen mode)
2. Show last response in external editor
3. Show turn duration
4. Notification preferences

Evidence: Settings panel items (search for `"autoScrollEnabled"` and `"externalEditorContext"`)


### Improved Error Diagnostics

Error messages from `/doctor` and plugin validation have been upgraded from simple counts to detailed per-error diagnostics, showing file, path, message, and suggestion for each issue.

Evidence: Diagnostic improvements (search for `"Suggestion:"`)


### Vim Mode Multi-Character Command Support

Vim mode's text-change handling has been refactored to support multi-character commands and improved state passing between operations.

Evidence: Vim mode refactor (search for the modified `D55` in the diff annotations)


### bypassPermissions Mode Scoping

The `bypassPermissions` mode is now explicitly session-scoped and will not be persisted as the default mode: "setMode:'bypassPermissions' is session-scoped; not persisting as defaultMode."

Evidence: Session scoping guard (search for `"setMode:'bypassPermissions' is session-scoped"`)


## Bug Fixes

- Fixed keybinding code parsing to use the `code` property from the source event instead of the derived string, improving reliability for key detection (search for `"q.code && q.code[0]"`)

- Fixed tmux integration by passing the current working directory (`cwd`) to tmux subprocess calls, resolving issues when the tmux binary isn't on the default path (search for `"cwd: R8()"` near `"tmux"`)

- Fixed subprocess spawn calls across the codebase to consistently pass `cwd: R8()`, preventing commands from running in wrong directories

- Fixed sleep command regex to accept trailing decimal points without fractional digits (e.g., `sleep 1.` now works), matching both Unix `sleep` and Windows `Start-Sleep` commands (search for `"\\d+(?:\\.\\d*)?"`)

- Added exponential growth protection to version range combining, preventing Cartesian product explosion in constraint resolution: "intersectConstraints: Cartesian product exceeded" (search for `"intersectConstraints"`)

- Fixed image rendering to show images even when they have been token-compressed, removing the overly restrictive `tokenCompressed` check

- Fixed terminal raw mode handling with reference counting to prevent mode conflicts between components


## In Development

Features with infrastructure added but not yet enabled. These are shipped "dark" and may become available in future versions.


### PushNotification Tool [In Development]

What: A tool that allows Claude to send notifications to the user's terminal and, when Remote Control is connected, push to their mobile device. Claude decides when to notify based on whether the user appears to be away and whether the event is actionable.

Status: Feature-flagged via `tengu_kairos_push_notifications` (default: `false`) and `tengu_kairos_input_needed_push` (default: `false`)

Details:
- Full implementation including tool definition, status rendering, mobile push via Remote Control API, and notification preference sync to `/api/claude_code/notification/preferences`
- The tool includes sophisticated logic: it only sends when the user appears away, considers terminal focus state, and respects user configuration
- User-facing status messages like "Terminal notification sent. Mobile push requested." and "Not sent because you're active in this terminal."
- Configuration options: "Push when Claude decides" and "Push when actions required" appear in `/config`
- Links to `https://claude.com/download#mobile` for mobile app setup
- The tool prompt coaches the model: "err toward NOT sending. Not every event is worth a push; the ones that change what they'd do next are."

Evidence: PushNotification tool (gated by `tengu_kairos_push_notifications`, search for `"PushNotification"` and `"Send a notification to the user via their terminal"`)


### Context Hint / Time-Based Microcompact [In Development]

What: An intelligent context window management system that automatically removes older tool results to stay within context limits, triggered by server-side hints.

Status: Feature-flagged via `tengu_hazel_osprey` (default: `false`), with beta header `context-hint-2026-04-09`

Details:
- When the context window approaches limits, old tool result content is replaced with `"[Old tool result content cleared]"`
- Handles HTTP 422/424 status codes as context-hint rejection signals
- Tracks telemetry for `tengu_time_based_microcompact` with token savings metrics
- Clears cached thinking tokens on context-hint triggers

Evidence: Microcompact system (gated by `tengu_hazel_osprey`, search for `"[Old tool result content cleared]"` and `"tengu_time_based_microcompact"`)


### Slate Ribbon [In Development]

What: A UI ribbon component controlled by a new feature flag.

Status: Feature-flagged via `tengu_slate_ribbon` (default: `false`)

Details:
- Infrastructure for a new UI element has been added but is not yet enabled
- Exact functionality unclear from code analysis

Evidence: Flag definition (search for `"tengu_slate_ribbon"`)


## Notes

- The Insights HTML report generator (2200+ lines of HTML/CSS/JS) has been refactored — it was removed and re-added in the same version, suggesting a significant rewrite of the report generation system
- The Yoga layout engine wrapper class and related constants have been removed, replaced by a more direct layout approach. This is an internal rendering change with no user-facing impact
- The update/relaunch mechanism (`FdY`) that displayed "Switching from X.X.X to latest…" has been removed, suggesting version transitions are now handled by the new daemon system
- The kill ring (Emacs-style clipboard) implementation has been refactored from a factory function to a dispatch-based approach, maintaining the same yank/kill functionality
- The `CLAUDE_CODE_ENABLE_BACKGROUND_PLUGIN_REFRESH` environment variable enables background refreshing of MCP plugin state — set it to opt in to async plugin reloading
