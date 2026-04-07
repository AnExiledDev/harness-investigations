# Changelog for version 2.1.76


## Summary

This release adds the `/effort` slash command for controlling model effort level, replaces the interactive hooks editor with a read-only viewer, introduces automatic background memory extraction (feature-flagged), adds a PostCompact hook event, and makes the `--plugin-dir` flag repeatable for loading multiple session-only plugin directories.


### `/effort` Slash Command

What: A new built-in slash command to view and set the model effort level directly from the REPL, without navigating into `/config`.

Usage:
```bash
/effort              # Show current effort level
/effort medium       # Set to medium
/effort max          # Maximum reasoning depth (Opus 4.6 only)
/effort auto         # Reset to automatic (default)
```

Details:
- Effort levels: `low`, `medium`, `high`, `max`, `auto`
- Named levels are persisted to user settings (`effortLevel` in settings.json)
- `auto` clears the setting, returning to the model default
- Each level has a descriptive summary (e.g. "Balanced approach with standard implementation and testing")

Evidence: `/effort` command registration (search for `name: "effort"`, `description: "Set effort level for model usage"`)


### PostCompact Hook Event

What: A new hook event that fires after conversation compaction completes, letting you run shell commands or prompts in response to compaction.

Details:
- Hook event name: `PostCompact`
- Input includes compaction details and the summary text
- Allows post-processing after compaction (e.g., logging, notification, or custom follow-up actions)
- Hook output: exit code 0 shows stdout to user; other exit codes show stderr only

Evidence: PostCompact hook event definition (search for `hook_event_name: C.literal("PostCompact")`, `"Running PostCompact hooks…"`)


### Built-in Hooks

What: A new category of hooks that are registered internally by Claude Code, distinct from user-configured and plugin hooks.

Details:
- Shown separately in the hooks viewer as "Built-in Hooks" / "Built-in hooks (registered internally by Claude Code)"
- Cannot be modified by users—they are part of the Claude Code runtime
- Visible in the `/hooks` UI for transparency

Evidence: Built-in hooks category (search for `"Built-in hooks (registered internally by Claude Code)"`)


### Bundled Skill Reference Files

What: Built-in skills can now declare reference files that are extracted to a temporary directory at runtime, making them available for the skill prompt to reference.

Details:
- Skills define a `files` property in their registration, mapping relative paths to file content
- Files are extracted to a per-skill directory inside the Claude Code data directory
- Path traversal is blocked (`bundled skill file path escapes skill dir:` error)
- Files are written with `O_NOFOLLOW` to prevent symlink attacks
- The skill prompt is prefixed with `Base directory for this skill: <path>`

Evidence: Bundled skill file extraction (search for `"Bundled skill reference files are allowed for reading"`, `"Failed to extract bundled skill '"`)


### Hooks UI Redesigned as Read-Only Viewer

The `/hooks` command has been redesigned from a full hook management interface (add, edit, delete) to a read-only viewer. Users can browse hook events, matchers, and see hook details, but can no longer modify hooks through the UI.

What changed:
- Removed: "Add new hook", "Delete hook?", "Delete matcher?", "Save hook configuration", "Where should this hook be saved?" dialogs
- Added: "Hook details" detail view showing event, matcher, type, source, command/prompt, and status message
- Added: "This menu is read-only. To add or modify hooks, edit settings.json directly or ask Claude."
- Added: "To re-enable hooks, remove `disableAllHooks` from settings.json or ask Claude."
- Navigation: "Esc to go back" / "Esc to close" guides
- Description changed from "Manage hook configurations" to "View hook configurations"

Evidence: Read-only hooks viewer (search for `"View hook configurations"`, `"This menu is read-only"`, `"Hook details"`)


### `--plugin-dir` Flag Now Repeatable

The `--plugin-dir` flag has been updated from accepting a single paths argument to being individually repeatable.

What changed:
- Old: `--plugin-dir <paths...>` (space-separated paths in one argument)
- New: `--plugin-dir <path>` (repeat the flag: `--plugin-dir A --plugin-dir B`)
- Session-only plugins are now labeled as "Session-only plugins (--plugin-dir):" in the UI
- The reserved marketplace name `"inline"` is used internally for `--plugin-dir` session plugins

Evidence: Repeatable plugin-dir flag (search for `"Load plugins from a directory for this session only (repeatable: --plugin-dir A --plugin-dir B)"`)


### Language Setting Now Includes Voice Dictation

The preferred language setting description has been expanded to explicitly include voice dictation.

What changed:
- Old: `Preferred language for Claude responses (e.g., "japanese", "spanish")`
- New: `Preferred language for Claude responses and voice dictation (e.g., "japanese", "spanish")`
- New dictation language display: shows current dictation language with unsupported-language warning

Evidence: Language setting update (search for `"Preferred language for Claude responses and voice dictation"`, `"Dictation language:"`)


### Disabled Organization Error Handling

New error messages provide better guidance when an `ANTHROPIC_API_KEY` belongs to a disabled organization.

Details:
- Subscription users: "Your ANTHROPIC_API_KEY belongs to a disabled organization · Unset the environment variable to use your subscription instead"
- Other users: "Your ANTHROPIC_API_KEY belongs to a disabled organization · Update or unset the environment variable"
- Organization verification errors now include actionable guidance about token scope and managed settings

Evidence: Disabled org handling (search for `"organization has been disabled"`, `"Your ANTHROPIC_API_KEY belongs to a disabled organization"`)


### Session Transcript Retention Semantics Changed

The `transcriptRetentionDays` setting now has stricter behavior when set to 0.

What changed:
- Old: "Number of days to retain chat transcripts (0 to disable cleanup)" — 0 meant keep forever
- New: "Number of days to retain chat transcripts (default: 30). Setting to 0 disables session persistence entirely: no transcripts are written and existing transcripts are deleted at startup."
- This is a behavioral change: setting 0 previously preserved transcripts forever; now it deletes them

Evidence: Transcript retention change (search for `"disables session persistence entirely"`)


### Stale Agent Worktree Cleanup

Agent worktrees that are no longer active are now automatically cleaned up.

Details:
- Worktrees with no uncommitted changes and no unpushed commits are removed
- The current session's worktree is never cleaned up
- Cleanup runs `git worktree prune` after removal
- Logged as: `cleanupStaleAgentWorktrees: removed N stale worktree(s)`

Evidence: Worktree cleanup (search for `"cleanupStaleAgentWorktrees"`)


### Compaction Now Preserves Message Segments

Conversation compaction can now preserve a segment of recent messages instead of summarizing everything.

Details:
- Compacted boundaries include a `preservedSegment` with `headUuid`, `anchorUuid`, and `tailUuid`
- Loaders splice the preserved segment at the anchor point so resumed sessions include actual message content
- Metadata is serialized as `preserved_segment` in transcript files

Evidence: Preserved segment in compaction (search for `"preservedSegment"`, `"Relink info for messagesToKeep"`)


### Read Tool Guidance Updated

The Read tool system prompt now encourages partial file reads when the needed section is known.

What changed:
- Added: "When you already know which part of the file you need, only read that part. This can be important for larger files."
- This supplements the existing guidance about offset/limit parameters

Evidence: Read tool guidance (search for `"When you already know which part of the file you need"`)


### PDF Reading Now Requires Anthropic API

Full PDF reading (without specifying page ranges) now requires the Anthropic API and poppler-utils.

What changed:
- Old: "PDF reading is not supported. Install poppler-utils..."
- New: "Reading full PDFs is only supported with the Anthropic API. Use the pages parameter to read specific page ranges (e.g., pages: \"1-5\", maximum N pages per request). This requires poppler-utils: install with `brew install poppler` on macOS or `apt-get install poppler-utils` on Debian/Ubuntu."

Evidence: PDF reading message (search for `"Reading full PDFs is only supported with the Anthropic API"`)


### Plugin Dependency Resolution Enhanced

Plugin dependencies can now be specified as bare names (without `@marketplace`) and are resolved against the declaring plugin's own marketplace.

Details:
- `Dependency must be a plugin name, optionally qualified with @marketplace`
- Bare names resolve against the parent plugin's marketplace source
- The `"inline"` marketplace name is reserved for `--plugin-dir` session plugins

Evidence: Plugin dependency resolution (search for `"Dependency must be a plugin name, optionally qualified with @marketplace"`)


### LSP Server Manager Reinitialization

A new `reinitializeLspServerManager()` function allows the LSP server manager to be restarted without restarting the entire session, useful when plugin configurations change.

Evidence: LSP reinit (search for `"[LSP MANAGER] reinitializeLspServerManager() called"`)


### MCP Tool Call Error Type

A dedicated `McpToolCallError` error type has been added for MCP (Model Context Protocol) tool call failures, providing better error categorization.

Evidence: Error type (search for `"McpToolCallError"`)


### ExitPlanMode Tool Description Clarified

The ExitPlanMode tool description now explicitly states it's only for plan mode: "present plan for approval and start coding (plan mode only)". An error message was also added: "You are not in plan mode. This tool is only for exiting plan mode after writing a plan."

Evidence: ExitPlanMode update (search for `"present plan for approval and start coding (plan mode only)"`)


## Bug Fixes

- Fixed autocompact circuit breaker to stop retrying after repeated failures: `"autocompact: circuit breaker tripped after N consecutive failures — skipping future attempts this session"` (search for `"circuit breaker tripped"`)
- Prompt/memory count now only counts messages after the last compaction boundary, fixing inflated counts in long sessions (search for `"compact_boundary"` in `UFY`)
- Tool schema discovery warning now explains why typed parameters fail and how to fix it: `"This tool's schema was not sent to the API — it was not in the discovered-tool set"` (search for `"This tool's schema was not sent to the API"`)


### Automatic Memory Extraction [In Development]

What: A background agent that automatically extracts and saves memories from conversations, running alongside the main conversation without user intervention.

Status: Feature-flagged behind `tengu_passport_quail` (default: `false`)

Details:
- After each turn, a background agent analyzes recent messages and saves relevant information to memory files
- Uses the `tengu_bramble_lintel` flag to control how many turns to accumulate before running (default: 1)
- Supports both private (user-only) and team (shared) memory scopes
- Team memory format controlled by `tengu_swinburne_dune` flag (alternative two-step format)
- Tracks which files the conversation has already written to, skipping extraction if the user manually saved memories
- Coalesces rapid extractions: if one is already running, subsequent requests are stashed for a trailing run
- Sends notification: "Saved N memor(y|ies)" when memories are written
- Memory extraction agent is restricted to only Write, Read, and Edit tools within the memory directory
- System prompt: "A background agent automatically extracts and saves memories from this conversation. If the user asks you to remember or forget something, acknowledge it — the save happens automatically."

Evidence: Memory extraction system (search for `"tengu_passport_quail"`, `"[extractMemories]"`, `"extract_memories"`)


### Session Quality Survey [In Development]

What: An in-session quality survey that can appear when a session is eligible.

Status: Feature-flagged — controlled by a probability setting (suggested starting point: 0.05)

Details:
- Configuration: "Probability (0–1) that the session quality survey appears when eligible. 0.05 is a reasonable starting point."
- No evidence of the survey UI itself in the diff, suggesting infrastructure only

Evidence: Survey config (search for `"session quality survey"`)


### Cancel Async Message [In Development]

What: Ability to cancel a pending async user message from the command queue by UUID.

Status: Infrastructure added

Details:
- Operation: `cancel_async_message` drops a pending message that hasn't been dequeued yet
- Result includes `cancelled` boolean: false means the message was already dequeued or never enqueued
- Related to Remote Control bridge functionality

Evidence: Async message cancellation (search for `"cancel_async_message"`, `"Drops a pending async user message"`)


### Bridge Debug Commands (Internal)

What: A `/bridge-kick` debug command for injecting failure states into the Remote Control bridge for manual recovery testing.

Status: Registered but explicitly disabled (`isEnabled: () => !1`)

Details:
- Subcommands: `close`, `poll`, `register`, `reconnect-session`, `heartbeat`, `reconnect`, `status`
- Only available when Remote Control is connected (USER_TYPE=ant)
- Intended for internal Anthropic debugging, not user-facing

Evidence: Bridge debug command (search for `"bridge-kick"`, `"Inject bridge failure states"`)
