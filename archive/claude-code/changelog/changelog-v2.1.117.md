# Changelog for version 2.1.117

## Summary

This release introduces the `/fork` command for spawning background agents that inherit the full conversation context, a team artifacts discovery system that notifies you about new skills and commands from teammates, and one-time scheduled remote agent execution (`run_once_at`). It also includes significant security hardening (path traversal detection, version string validation, stricter git reflog safety, `cd` multi-argument validation), a terminology rename from "triggers" to "routines" for scheduled agents, removal of the `/mode` and `/autocompact` interactive commands, and updated model deprecation tracking with remapping for Opus 4, Opus 4.1, and Sonnet 4.


### /fork Command

What: Spawn a background agent fork that inherits the full conversation context and executes a specific directive independently.

Usage:
```
/fork <directive>
```

Details:
- The fork receives the parent conversation's full history as read-only reference context
- Each fork executes ONE directive, then stops — it is not a continuation of the parent
- Fork prompts should be specific directives about what to do, not descriptions of the situation
- The fork agent name is auto-generated from the first few words of the directive
- Requires at least one conversation turn before forking (you'll see "Cannot fork before the first conversation turn" if attempted too early)
- Controlled by the `tengu_copper_fox` feature flag or `CLAUDE_CODE_FORK_SUBAGENT` environment variable

Evidence: Fork command handler (search for `"Usage: /fork"`) — `mp1` at line ~548474; fork spawner `_n7` at line ~548333


### Team Artifacts Discovery

What: Automatically detects new skills and commands added by teammates to the project's `.claude/skills/` and `.claude/commands/` directories within the last 7 days and surfaces them as notifications.

Details:
- Queries git history (`git log --since=7.days --diff-filter=A`) to find recently added team artifacts
- Filters out artifacts authored by the current user (using git email)
- Displays notification like "New from your team: /my-skill (Alice), /deploy-cmd (Bob)"
- Tracks seen artifacts in user config to avoid repeated notifications
- Shows author attribution for each discovered artifact

Evidence: Team artifacts discovery system (search for `"New from your team:"`) — `sr$` at line ~389663, `x97` at line ~389651


### One-Time Scheduled Remote Agent Execution

What: The `/schedule` command (previously `/trigger`) now supports one-time execution at a specific time in addition to recurring cron schedules.

Usage:
```
/schedule  (then specify run_once_at instead of cron_expression)
```

Details:
- Use `"run_once_at": "YYYY-MM-DDTHH:MM:SSZ"` (RFC 3339 UTC) instead of a cron expression
- The timestamp must be in the future
- When the user specifies a local time, the agent converts it to UTC and confirms

Evidence: Schedule system prompt changes (search for `"run_once_at"`) and description update: `"or once at a specific time."` — `$J7` at line ~428477


### Deeper Reasoning Display for Effort Parameter

What: When deeper reasoning is requested for a turn (effort level `xhigh`, Opus 4.7 only), a visible notification now appears in the conversation.

Details:
- Displays "Deeper reasoning requested for this turn" when the effort parameter triggers enhanced reasoning
- This is part of the effort parameter support that allows users to control adaptive reasoning depth

Evidence: Effort notification display (search for `"Deeper reasoning requested for this turn"`) at line ~596751


### Model Deprecation Remapping System

What: Expanded model deprecation tracking with retirement dates and automatic remapping guidance for deprecated models.

Details:
- New entries for Claude Opus 4 (retiring June 15, 2026 on first-party), Claude Opus 4.1, and Claude Sonnet 4 (retiring June 15, 2026 on first-party)
- Models with `remappedTo` field tell users what replacement to use (e.g., Opus 4 and 4.1 remap to "the latest Opus")
- Replaces the older deprecation table that only covered Claude 3 Opus, Claude 3.7 Sonnet, and Claude 3.5 Haiku
- The system displays warnings via `addNotification` when a model is approaching retirement

Evidence: Model deprecation table with `remappedTo` field (search for `"remappedTo"`) — `Vq8` at line ~544460


### Model Source Indicator in Status

What: The status line now shows where your active model setting originates when it comes from project settings or managed (enterprise) settings.

Details:
- Displays "(from managed settings)" when the model is pinned by enterprise policy
- Displays "(from [project settings path])" when set in project-level configuration
- Omitted when using the default model or when overridden via `ANTHROPIC_MODEL` env var
- Also shows "· /model to change" hint alongside the model name

Evidence: Model source label generator (search for `"(from managed settings)"`) — `aN8` at line ~108402


### Remote File Suggestions via RPC

What: In remote sessions, file suggestions are now fetched from the remote host via an RPC call instead of being computed locally.

Details:
- Sends a `file_suggestions` control request to the remote session manager
- Falls back gracefully if the RPC fails, returning an empty suggestion list
- Only activates when `u6()` returns true (remote workspace mode)

Evidence: Remote file suggestions RPC (search for `"file_suggestions"`) — `JW1` at line ~474645


### Remote Context Usage Display

What: The `/context` command now works in remote sessions by fetching context usage data from the remote host via RPC.

Details:
- In remote mode, sends a `get_context_usage` control request to the remote agent
- Displays the response using the same UI component as local mode (with `isRemote: true` flag)
- Falls back to a user-friendly error message if the remote fetch fails

Evidence: Remote context handler (search for `"get_context_usage"`) — `q01` at line ~485532


### Terminology Change: "Triggers" Renamed to "Routines"

The scheduled remote agents feature has been renamed from "triggers" to "routines" throughout the CLI. All user-facing text, help descriptions, and command references now use the "routines" terminology. For example:
- "manage scheduled remote agent triggers" → "manage scheduled remote agent routines"
- "Connected connectors (available for triggers)" → "Connected connectors (available for routines)"
- "Create, update, list, or run scheduled remote agents (triggers)" → "Create, update, list, or run scheduled remote agents (routines) on a cron schedule or once at a specific time"

Evidence: Description string change (search for `"manage scheduled remote agent routines"`)


### Enhanced Git Command Safety Validation

The git reflog command now has stricter safety validation:
- Explicitly whitelists only "show" and "list" as safe subcommands
- Blocks "expire", "delete", "exists", "drop", and "write" as dangerous (previously only blocked "expire", "delete", "exists")
- Any unrecognized first argument that isn't a flag is treated as potentially dangerous

Evidence: Git reflog safety callback (search for `"expire", "delete", "exists", "drop", "write"`) in the git command validator


### Path Traversal Detection for Shell Commands

A new security check prevents path traversal attacks in shell write/create operations. Paths containing `..` after a directory segment (which may follow a symlink outside the working directory) are now rejected.

Evidence: Path traversal validator (search for `"Path contains '..' traversal"`) — `U19` at line ~212741


### Version String Validation

Version strings are now validated against path-unsafe characters and traversal patterns. Strings that don't match `^[a-zA-Z0-9._+-]+$` or contain `..` are rejected with clear error messages.

Evidence: Version string validation (search for `"Invalid version string"`) — `sq6` at line ~351290


### `cd` with Multiple Directory Arguments Requires Approval

Zsh's `cd OLD NEW` form (which substitutes OLD→NEW in `$PWD`) now requires manual approval because the target path cannot be statically validated. This prevents potentially unexpected directory changes.

Evidence: cd safety check (search for `"cd with two or more directory arguments"`) at line ~303589


### `file` Command Removed from Shell Allowlist

The `file` system command (with its various flags like `--brief`, `--mime`, `--dereference`, etc.) has been removed from the automatic shell command allowlist. This means `file` invocations will now go through the normal permission flow.

Evidence: Removed `file` command and its `safeFlags` from allowlist (removed strings include `"--dereference"`, `"--extension"`, `"--mime-encoding"`, `"--mime-type"`)


### Advisor Tool Marked as Experimental

The Advisor Tool configuration dialog title has been updated from "Advisor Tool" to "Advisor Tool (Experimental)" to better communicate its maturity status. A link to the blog post about the advisor strategy is now included.

Evidence: Updated title (search for `"Advisor Tool (Experimental)"`) at line ~543011; blog link `"https://claude.com/blog/the-advisor-strategy"` at line ~543061


### Plugin Installation Duplicate Detection

Plugin installation now checks if a plugin is already installed before attempting reinstallation. If a plugin with the same name and scope already exists, a clear message is shown: `Plugin '<name>' is already installed (scope: <scope>)`.

Evidence: Plugin duplicate check (search for `"is already installed"`) — `CLK` at line ~229155


### Enterprise Policy Enforcement for Marketplace Sources

Marketplace sources blocked by enterprise policy are now explicitly skipped during bulk refresh and plugin operations, with warning messages like "Skipping policy-blocked marketplace '<name>'".

Evidence: Policy enforcement check (search for `"Skipping policy-blocked marketplace"`)


### Improved Plugin Dependency Error Messages

When a plugin dependency can't be resolved, the error message now includes a specific install command and marketplace information: `not installed — run "claude plugin install <name>"` instead of the previous generic "not found in any configured marketplace".

Evidence: Enhanced error message (search for `"not installed — run"`)


### Auto-Compact Window Message Improvement

The auto-compact notification now shows "compacted at the auto window" with a clearer reference to the `autoCompactWindow` setting in `settings.json`, replacing the previous more verbose messaging.

Evidence: Updated compact message (search for `"compacted at the auto window"`)


### Managed Settings Model Pin Visibility

When a model is pinned by managed (enterprise) settings or project settings, the `/model` command now shows where the pin comes from and how to override it locally. Messages like "Managed settings pin [model] — that applies on restart" and "Also saved to [local settings] to override the pin" help users understand the configuration hierarchy.

Evidence: Model pin messaging (search for `"Managed settings pin"`) — `Fx1` at line ~542813


### Bridge Authentication Debug Info

A new `respawn` CLI command integrates bridge authentication debugging, providing detailed auth state information for troubleshooting remote session connections. The debug output includes OAuth token status, API key presence, scopes, and third-party provider configuration.

Evidence: Auth debug info (search for `"[debug] Remote Control auth state:"`) — `hI9` at line ~548456


### Agent Frontmatter Type Support

Agent-scoped configuration is now recognized as a distinct source type, showing "Agent config (from agent frontmatter)" in configuration source displays. This supports agent-scoped MCP servers and other per-agent customization.

Evidence: Agent config source label (search for `"Agent config (from agent frontmatter)"`)


### Standardized Error and Empty State Components

Error displays across the CLI have been systematically refactored to use a dedicated `A7` error component and `L4` empty-state component, replacing ad-hoc inline styling. This provides more consistent visual treatment of errors and empty states throughout the UI.

Evidence: New `A7` error component (search for `"color: \"error\""` in component definition) at line ~198548


### Confirmation Dialog Simplification

Multiple confirmation dialogs (folder trust, API key, agent deletion, exit) have been refactored from dropdown-style selectors to simpler yes/no confirmation dialogs with explicit confirm/cancel labels.

Evidence: New confirmation dialog component `m_` at line ~302036


## Bug Fixes

- Fixed git sha parameter injection by adding input validation that rejects sha values starting with "-" (search for `"Invalid sha"`)
- Fixed git clone argument injection by adding `--` separator to prevent URL and ref arguments from being interpreted as flags (search for `"A.push('--', H, $)"`)
- Fixed git remote HEAD reference validation to verify that detected references actually exist before using them (search for `"refs/heads/"` in remote HEAD check)
- Fixed cache directory path sanitization to prevent `.` and `..` from being used as path components (search for `"z === \".\" || z === \"..\""`)
- Fixed cursor state display logic to properly update cursor state instead of only handling specific opposite-pair transitions (cursor state handling)
- Fixed damage rectangle merging to properly expand bounds in all directions when new damage extends beyond existing bounds
- Added `--` argument separator in `sed` safety validation to prevent sed expression injection attacks (search for `"aI9"` — new sed expression extractor at line ~303347)
- Fixed handling of broken symlinks during directory copy operations, now skips them with a warning (search for `"copyDir: skipping broken symlink"`)
- Fixed symlink escape detection during directory copy to prevent following symlinks outside the source tree (search for `"copyDir: skipping symlink escaping source tree"`)


### /mode Command

The `/mode` command for interactively changing permission modes has been removed. Users should use the local TUI (shift+tab) to change permission modes instead.

Evidence: Removed command registration (search for `name: "mode"` in old version at line ~544018)


### /autocompact Interactive Dialog

The `/autocompact` interactive dialog (with up/down arrow selection of compact window sizes and the "Long context that holds up" marketing copy) has been removed. Auto-compact window configuration is now done exclusively through `settings.json` (`autoCompactWindow` key) or the `CLAUDE_CODE_AUTO_COMPACT_WINDOW` environment variable.

Evidence: Removed dialog component `vP1` and command registration `aT7` from old version


### /files Command

The `/files` command that listed all files currently in context has been removed.

Evidence: Removed command (search for `"List all files currently in context"` in old version at line ~534335)


### Stop Hook Command

The interactive `/stop` hook command for setting session-only stopping conditions has been removed. The underlying stop hook system still functions (hooks configured via other means continue to work), but the interactive prompt-based UI for creating them is gone.

Evidence: Removed `kF7` stop hook editor component and `zR1` command handler from old version


### Runtime Verification Embedded Skill

The embedded `runtime-verification` skill documentation (~700 lines of verification guides with CLI and server examples) has been removed from the CLI bundle. This skill may still be available through other distribution channels.

Evidence: Removed `o54` runtime verification content and associated example files `jA4`, `XA4` from old version


### Team Artifacts Hint System [Gradual Rollout]

What: A hint/warmup feature that proactively notifies users about new team artifacts (skills and commands) discovered in the project.

Status: Feature-flagged behind `tengu_tussock_oriole` (defaults to `!1` / false).

Details:
- The team artifacts discovery system (described above) is fully implemented
- The proactive hint/tip that would surface discoveries during session warmup is gated
- When enabled, it would show team artifact notifications during the hint cycle

Evidence: Feature gate check `h$("tengu_tussock_oriole", !1)` at line ~607799 (search for `"tengu_tussock_oriole"`)


### Session Resume Notification [Gradual Rollout]

What: A notification system that would alert users when resuming a session after a period of inactivity.

Status: Feature-flagged behind `tengu_gleaming_fair` (defaults to `!1` / false).

Details:
- Evaluates elapsed time since last activity to determine if a resume notification should appear
- Also checks the `CLAUDE_CODE_RESUME_SESSION` environment variable
- Infrastructure exists but the flag gates activation

Evidence: Feature gate (search for `"tengu_gleaming_fair"`) — `$s7` resume notification evaluator


### Fork Subagent Feature Gate [Gradual Rollout]

What: The `/fork` command's availability is additionally controlled by a server-side feature flag.

Status: Gated by `tengu_copper_fox` flag (defaults to `!1`), but can be overridden with `CLAUDE_CODE_FORK_SUBAGENT` environment variable.

Details:
- When the flag is disabled and the env var is not set, the fork tool is not loaded
- Setting `CLAUDE_CODE_FORK_SUBAGENT=1` provides a local override

Evidence: Fork feature gate (search for `"tengu_copper_fox"`) — `MG` at line ~381717


## Notes

- The rename from "triggers" to "routines" affects help text, command descriptions, and scheduled task references. If you have scripts or documentation referencing "triggers", update them to use "routines".
- The removal of `/mode`, `/autocompact`, and `/files` commands simplifies the slash command surface. Auto-compact configuration moves to settings files; permission mode changes move to the TUI (shift+tab).
- The `file` system command removal from the allowlist means any `file` invocations in automated workflows may now prompt for approval.
