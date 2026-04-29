# Changelog for version 2.1.105

## Summary

This release significantly overhauls the worktree experience (enter existing worktrees), adds a `/doctor` diagnostics screen with auto-fix, introduces plugin monitors for background event streaming, and rewrites the `/btw` panel with a "fork to session" action. Think Back / Year in Review has been removed. Internally, session memory compaction and time-based microcompaction are replaced by a new reactive compaction system (currently feature-flagged), and a session recap feature is shipping dark.


## New Features


### Enter Existing Worktrees

What: The `EnterWorktree` tool now accepts a `path` parameter to switch into an existing linked worktree instead of always creating a new one.

Usage:
```
/worktree          # create a new worktree (existing behavior)
# or, via the model:
EnterWorktree(path: "/path/to/existing-worktree")
```

Details:
- The `path` must be a registered worktree of the current repo (shown by `git worktree list`)
- Mutually exclusive with the `name` parameter — specify one or the other
- A safety check prevents removing worktrees that were entered (not created) by `EnterWorktree`
- The exit flow returns you to the original working directory
- New UI messages: "Entering worktree", "Cleaning up worktree (no pending changes)…", "This session entered an existing worktree"

Evidence: Worktree `path` parameter (search for `"Path to an existing worktree"`) and enter-existing safety check (search for `"enteredExisting"`)


### /doctor Diagnostics with Auto-Fix

What: The `/doctor` command has been rewritten as a comprehensive diagnostic dashboard with a new keybinding to auto-fix detected issues.

Usage:
```
/doctor            # open diagnostics screen
f                  # press f to ask Claude to fix the reported issues
```

Details:
- Displays installation info, ripgrep status, update channel, auto-update permissions
- Aggregates warnings from multiple sources: CLAUDE.md context usage, agent parse errors, plugin errors, keybinding issues, MCP server health, unreachable permission rules, invalid settings, version locks
- New tree-view UI with severity-colored messages and suggested fixes
- "f to fix with Claude" sends the diagnostics output to a prompt: "Help me fix the issues reported by /doctor below"
- Read-only checks run without confirmation; destructive fixes require explicit user approval

Evidence: Doctor command context (search for `"doctor:fix"`) and fix prompt (search for `"Help me fix the issues"`)


### Plugin Monitors (Background Watch Scripts)

What: Plugins can now define persistent background monitors that stream events into the conversation as `<task_notification>` events.

Details:
- Define monitors in a `monitors/monitors.json` file at the plugin root, or inline via the `monitors` field in `plugin.json`
- Each monitor has: `id` (unique within plugin), `description`, `command` (shell command), and an `armTrigger`
- Arm triggers control when monitors start:
  - `"always"` — arms at session start and on plugin reload
  - `"on-skill-invoke:<skill>"` — arms the first time a specific skill is dispatched
- Each stdout line from the monitor command becomes a notification; stderr goes to an output file
- Monitor IDs are deduped to prevent duplicate spawns on reload
- Session-scoped: monitors stop when the session ends

Evidence: Monitor schema (search for `"monitors.json"`) and arm triggers (search for `"on-skill-invoke"`)


### /btw Fork to Full Session

What: After receiving a `/btw` side-question response, press `f` to fork it into a full independent conversation session.

Usage:
```
/btw what's the syntax for Python decorators?
# ... response appears ...
# Press f to fork into a new session with this context
# Press Esc to dismiss as before
```

Details:
- New keybinding: `f to fork` shown in the `/btw` footer when a response is available
- Forks the /btw context into a new session via `branchAndResume`
- Shows "Forking into a new session…" status while the fork is in progress
- Previous /btw questions in the session are now shown as a collapsed history: "(+N earlier /btw)"

Evidence: Fork keybinding (search for `"f to fork"`) and fork status (search for `"Forking into a new session"`)


### Text Selection Keybindings

What: Six new keybinding actions for extending text selections in the input editor.

Details:
- `selection:extendUp` — shift+up
- `selection:extendDown` — shift+down
- `selection:extendLeft` — shift+left
- `selection:extendRight` — shift+right
- `selection:extendLineStart` — shift+home
- `selection:extendLineEnd` — shift+end
- These are customizable via `~/.claude/keybindings.json`

Evidence: Selection keybindings (search for `"selection:extendDown"`)


### Multi-Repository Checkout Support

What: Two new environment variables let you configure Claude Code for multi-repo development workflows.

Usage:
```bash
export CLAUDE_CODE_REPO_CHECKOUTS='{"frontend": "/home/user/frontend", "backend": "/home/user/backend"}'
export CLAUDE_CODE_BASE_REFS='{"frontend": "origin/main", "backend": "origin/develop"}'
claude
```

Details:
- `CLAUDE_CODE_REPO_CHECKOUTS` — JSON map of name-to-path entries for repository checkouts. Claude Code tracks branches across all configured repos.
- `CLAUDE_CODE_BASE_REFS` — JSON map specifying the base git ref for each checkout (used for diff comparisons and bundle generation).
- Both values are cached per session with singleton initialization.

Evidence: Repo checkouts env var (search for `"CLAUDE_CODE_REPO_CHECKOUTS"`) and base refs (search for `"CLAUDE_CODE_BASE_REFS"`)


### Skill Listing Configuration

What: New settings to control how skills are presented to Claude in the system prompt, giving users fine-grained control over context usage.

Details:
- `skillListingMaxDescChars` (default: 1536) — Per-skill description character cap. Descriptions longer than this are truncated.
- `skillListingBudgetFraction` (default: 0.01 = 1%) — Fraction of the context window reserved for the skill listing. When the listing exceeds this, descriptions are shortened to fit.
- `skillOverrides` — Per-skill visibility override keyed by skill name. Values:
  - `"on"` — full listing (default)
  - `"name-only"` — listed without description
  - `"user-invocable-only"` — hidden from the model but still available via `/name`
  - `"off"` — hidden from both model and user
- These settings can be configured at policy, flag, project, user, and local settings levels.

Evidence: Skill listing settings (search for `"skillListingMaxDescChars"`) and overrides (search for `"skillOverrides"`)


### Custom Subagent Status Lines

What: Plugins can now define a custom status line command that generates per-subagent status displayed in the agent panel.

Details:
- Configure via the `subagentStatusLine` field in plugin settings (allowlisted alongside `agent`)
- The command receives task metadata as JSON on stdin and should emit JSON lines on stdout
- Displays custom status per-teammate in the agent panel UI

Evidence: Subagent status line (search for `"subagentStatusLine"`)


### Plugin Dependency Installation

What: Plugins can now declare dependencies on other marketplace plugins that are automatically installed.

Details:
- Controlled via `allowedDependencyMarketplaces` in marketplace configuration
- Only the root marketplace's allowlist applies — no transitive trust
- Shows installation progress: "Installing plugin dependencies: [name]"
- Reports success, failure, or warnings per dependency
- Skips yarn/pnpm lockfiles (not supported; only bun and npm)

Evidence: Dependency installation (search for `"Installing plugin dependencies"`)


## Improvements


### /proactive Alias for /loop

The `/loop` command now has `/proactive` as an alias, making the autonomous loop feature more discoverable.

Evidence: Alias definition (search for `"proactive"` near `aliases`)


### Git Credential Redaction

Git remote URLs containing credentials are now automatically redacted in logs and debug output, preventing accidental exposure of authentication tokens.

Evidence: Credential redaction (search for `"redactGitRemoteCredentials"`)


### Plugin Path Traversal Protection

Plugins can no longer use `..` path segments to reference files outside their plugin directory. This is enforced for:
- Plugin file resolution (plugin.json paths)
- Marketplace name validation
- Package references

Evidence: Path traversal checks (search for `"path-traversal"`)


### PreCompact Hook Support

Conversation compaction now respects a `PreCompact` hook. If the hook blocks, compaction is skipped with the message "Compaction blocked by PreCompact hook." This gives users control over when context compression occurs.

Evidence: Hook integration (search for `"Compaction blocked by PreCompact hook"`)


### Improved Tool Call Error Handling

When the model's tool call cannot be parsed, a clearer error message is now returned: "The model's tool call could not be parsed (retry also failed). Your tool call was malformed and could not be parsed. Please retry."

Evidence: Error message (search for `"model's tool call could not be parsed"`)


### Ultrareview Billing Overhaul

Ultrareview billing now uses a server-driven preflight check that returns `proceed`, `blocked`, or `confirm` states, replacing the old client-side quota check. The blocked state shows an actionable message; the confirm state shows a dialog with billing details (e.g., "This review bills as usage (~$10)").

Evidence: Preflight endpoint (search for `"/v1/ultrareview/preflight"`)


### Worktree UI Polish

- "Entering worktree" and "Cleaning up worktree (no pending changes)…" replace the old "Creating worktree…" and "Exiting worktree…" messages
- Background tasks are now shown in the worktree exit dialog
- "Switched to worktree" message is now context-aware (no longer appends "on branch" unconditionally)

Evidence: Worktree messages (search for `"Entering worktree"` and `"Cleaning up worktree"`)


### Tmux Focus-Events Diagnostic

The `/doctor` output now detects when tmux `focus-events` is off and shows a suggestion: "add 'set -g focus-events on' to ~/.tmux.conf and reattach for focus tracking."

Evidence: Tmux diagnostic (search for `"tmux focus-events off"`)


### Model Deprecation Warnings

A new warning system notifies users when their configured model is approaching or past its retirement date, including the deprecation date and a suggestion to switch.

Evidence: Deprecation warning generator (search for `"was retired on"`)


### Improved MCP Large Output Handling

The MCP tool result processor now provides format-specific guidance for large outputs. For JSON files, it suggests using `jq` for targeted queries. For text files, it suggests `grep`. For analysis tasks, it recommends using the Task tool to process the file in an isolated subagent context.

Evidence: Format-specific guidance (search for `"first probe the structure"`)


### Hyperlink Detection Improvements

Terminal hyperlink support detection is improved with broader terminal emulator recognition, including checks for `TERM_PROGRAM`, `LC_TERMINAL`, and Kitty terminal detection.

Evidence: Hyperlink detection (search for `"supportsHyperlink"`)


### Event Loop Stall Detection

A new internal diagnostic detects event loop stalls (blocked main thread) and logs them with memory statistics. This helps diagnose performance issues and detect sleep/wake transitions.

Evidence: Stall detector (search for `"event-loop-stall"`)


### Managed Agents Documentation

Comprehensive documentation has been embedded for the Managed Agents API, covering:
- cURL/HTTP endpoint reference
- Python and TypeScript SDK examples
- Core concepts (agent lifecycle, sessions, environments)
- Event streaming and session steering
- Tools and skills configuration
- Interactive onboarding script

Evidence: Managed Agents docs (search for `"Managed Agents"`)


### Skills Dialog Rewrite

The skills dialog has been completely rewritten with:
- Toggle states per skill: on / name-only / user-invocable-only / off
- Source and override indicator (policy, flag, author)
- Improved keyboard navigation with scroll windowing

Evidence: Skills dialog toggle states (search for `"user-invocable-only"`)


## Bug Fixes

- Fixed worktree safety: prevents removing worktrees that were entered (not created) via `EnterWorktree`, avoiding accidental deletion of shared worktrees (search for `"enteredExisting"`)
- Fixed stream handling for socket writes by deferring `stream.end()` until the write buffer is fully drained, preventing truncated output (search for `"endAfterDrain"`)
- Added defensive null check for `prePlanMode` property to prevent crashes when the property is undefined (search for `"prePlanMode"`)
- Fixed array last-element access using `.at(-1)` instead of manual indexing, preventing potential off-by-one errors
- Added type safety check for non-Array inputs to token counting function, returning 0 instead of throwing (search for `"Array.isArray"`)
- Fixed async cleanup race condition in caffeinate (sleep prevention) by capturing the reference before try-finally blocks
- Added optional chaining for `querier.onResponse()` to prevent null reference crashes
- Fixed UNC path permission checks to allow certain whitelisted UNC paths that pass security validation


## Removals


### Think Back / Year in Review

The Think Back feature ("Your 2025 Claude Code Year in Review" ASCII animation) has been completely removed — all plugin detection, animation generation, player scripts, and associated slash commands are gone.

Evidence: Removed strings (search for `"thinkback"` returns 0 results in new version)


### Proactive Auto-Enable Setting

The `proactive.autoEnable` setting (which controlled whether autonomous background operation was auto-activated at launch) has been removed. The `/proactive` alias for `/loop` replaces the previous configuration approach.

Evidence: Setting removed (search for `"autoEnable"` near proactive in old file only)


### Time-Based Microcompaction

The time-based microcompaction system (`tengu_time_based_microcompact`, `tengu_slate_heron`) — which cleared old tool results when a time gap was detected — has been completely removed.

Evidence: Removed telemetry event and feature flag (search for `"TIME-BASED MC"` or `"tengu_slate_heron"`)


### Session Memory Compaction

The `tengu_sm_compact` session memory compaction system, which automatically truncated conversation history using a token-counting approach, has been removed. It is replaced by the new reactive compaction system (see In Development section).

Evidence: Removed orchestrator (search for `"tengu_sm_compact"` returns 0 results in new version)


### Plugin Enable CLI Command

The `claude plugin enable` CLI command has been removed. Plugin management is now handled through the `/plugin` slash command.

Evidence: Removed function `G$A` (search for `"Enabling plugin"` returns 0 results in new version)


### Plugin Validate and Update Marketplace CLI Commands

The `claude plugin validate` and `claude plugin update-marketplace` CLI commands have been removed.

Evidence: Removed functions `H$A` and `W$A` (search for `"Installing marketplace"` returns 0 results in new version)


### MCP Tool Classification Lists

The large static classification lists (500+ MCP tool names categorized as "search" or "read") have been removed. The classification likely uses a different approach now.

Evidence: Removed sets `fVz` and `TVz` (search for `"slack_search_public"` returns 0 results in new version)


## In Development

Features with infrastructure added but not yet enabled. These are shipped "dark" and may become available in future versions.


### Reactive Compaction [Gradual Rollout]

What: A new conversation compaction system that automatically summarizes older messages when the prompt exceeds context limits, using binary search to find the optimal compaction boundary.

Status: Feature-flagged behind `tengu_cobalt_raccoon` (default: false). Disabled in non-interactive mode.

Details:
- Replaces the removed `tengu_sm_compact` system with a more sophisticated approach
- Uses binary search to determine how many message groups to preserve vs. summarize
- Sends older messages to a model fork for summarization
- Includes retry logic (strips media on size errors), empty-response detection, and PreCompact hook support
- Extensive telemetry: trigger, success, duration, pre/post token counts, group counts
- When enabled, triggers automatically during conversation turns when token limits are approached

Evidence: Feature gate (search for `"tengu_cobalt_raccoon"`) returns `!1` (false) as default


### Session Recap (Away Summary) [Gradual Rollout]

What: When you return to a session after being away for 5+ minutes, Claude generates a brief recap of where things left off.

Status: Feature-flagged behind `tengu_sedge_lantern` (default: false). Can be force-enabled with `CLAUDE_CODE_ENABLE_AWAY_SUMMARY=1`.

Details:
- Tracks focus/blur events to detect when the user steps away
- On return, generates a recap: "under 40 words, 1-2 plain sentences, no markdown. Lead with the overall goal and current task, then the one next action."
- Toggleable in `/config` via `awaySummaryEnabled` setting (when the flag is on)
- Recap can be cancelled, and shows "No recap available" if generation fails
- A `/recap` command is also available to manually trigger a recap
- SDK event: `memory_recall` emitted when memories are surfaced

Orphaned Tip: ⚠️ Users who get the flag enabled may see "(disable recaps in /config)" — but the feature doesn't work unless the flag is active.

Evidence: Feature gate (search for `"tengu_sedge_lantern"`) and env override (search for `"CLAUDE_CODE_ENABLE_AWAY_SUMMARY"`)


### Memory Rating Survey [In Development]

What: A "Did this help? (optional)" prompt allowing users to rate recalled memories as good or bad.

Status: Stubbed — the gate function `H_5()` always returns `!1` (false). The UI components (rating buttons with thumbs up/down hover states) are fully built but unreachable.

Details:
- Rating buttons component exists with [Good]/[Bad] options
- Keyboard shortcuts (+ and - keys) are wired up for rating
- The infrastructure includes both memory-specific and general feedback survey paths
- General feedback survey is also gated behind `tengu_dunwich_bell` (default: false)

Evidence: Stubbed gate (search for `"Did this help?"`) and gate function returning `!1`


### Prompt Cache Break Detection [In Development]

What: Internal diagnostic that detects when the prompt cache is invalidated between API calls, identifying the cause (system prompt change, tool schema change, model change, TTL expiry).

Status: Active internally for telemetry only (`tengu_prompt_cache_break` event). Not user-visible.

Details:
- Snapshots system prompt, tools, and model between requests
- When a cache break is detected, classifies the cause: system prompt changed, tools changed, model changed, betas changed, possible 5min or 1h TTL expiry, or unknown
- Logs `[PROMPT CACHE BREAK]` with cause details
- Helps Anthropic optimize prompt caching behavior

Evidence: Cache break detection (search for `"PROMPT CACHE BREAK"` and `"tengu_prompt_cache_break"`)
