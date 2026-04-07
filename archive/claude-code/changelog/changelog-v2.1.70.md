# Changelog for version 2.1.70


## Summary

This release adds incremental MCP server instruction delivery (delta-based), a token-saving output compression system for Bash tool results, and improved CA certificate handling from Claude Code config. It also introduces a "fork" agent mode (feature-flagged), softens "kill" terminology to "stop" across the UI, fixes clipboard error messages on Windows/WSL, and includes numerous rendering and stability improvements.

### Token Saver for Bash Output

What: Bash tool results can now send a compressed version of output to the model while the UI still displays the full uncompressed stdout, reducing token usage on large command outputs.

Details:
- A new `tokenSaverOutput` field is added to the Bash tool result schema
- When token-saver is active, the model receives a compressed representation while users see full output
- Helps conserve context window on commands with verbose output

Evidence: New schema field with description `"Compressed output sent to model when token-saver is active (UI still uses stdout)"` (search for `"tokenSaverOutput"`)


### CA Certificate Configuration from Settings

What: Claude Code now reads `NODE_EXTRA_CA_CERTS` from your config and user settings files, applying them automatically at startup — no need to set environment variables manually.

Details:
- On startup, if `NODE_EXTRA_CA_CERTS` is not already set in the environment, Claude Code checks `globalConfig.env` and `userSettings.env` for the path
- Supports `--use-system-ca` flag to load system CA certificates via the Node.js `tls.getCACertificates` API
- Custom CA certificates are now also applied to WebSocket connections (both Bun and Node.js)
- Cache clearing added for CA certificates, mTLS configuration, and proxy agents

Evidence: CA certificate loader (search for `"CA certs: Applied NODE_EXTRA_CA_CERTS from config to process.env"`)


### Effort Level Indicator

What: A visual indicator in the input box border now shows the current reasoning effort level (low, medium, high, or max) using colored block characters.

Details:
- Displays 1–3 filled `▪` blocks based on effort level (1 for low, 2 for medium, 3 for high/max)
- Shows alongside model name and `/fast` mode indicator when present
- Controlled by existing effort level settings

Evidence: Effort-to-dots mapping function (search for `"▪"`) and effort indicator builder `$Qq`/`Cgz` at line ~258963


### Session Color Reset

What: The `/color` command now accepts `default` as a valid argument to reset session color.

Details:
- Argument hint changed from `<color>` to `<color|default>`
- Resetting displays "Session color reset to default"
- Color values `"default"`, `"reset"`, `"none"`, `"gray"`, and `"grey"` are treated as reset values

Evidence: Updated argument hint (search for `"<color|default>"`) and reset color list (search for `"Session color reset to default"`)


### Bridge Pointer for Worktree-Aware Reconnection

What: Remote session reconnection now supports git worktrees by writing and discovering `bridge-pointer.json` files across worktree directories.

Details:
- A `bridge-pointer.json` file stores `sessionId`, `environmentId`, and `source` for reconnection
- When reconnecting, Claude Code searches across git worktrees to find an active session pointer
- Pointers older than 4 hours are automatically cleared
- Fanout search is capped to prevent performance issues with many worktrees

Evidence: Bridge pointer system (search for `"bridge-pointer.json"`) and worktree fanout (search for `"[bridge:pointer] fanout found pointer in worktree"`)


### Session Metadata Files

What: Session transcripts now have companion `.meta.json` files that store additional metadata about each session.

Details:
- Metadata files are stored alongside session `.jsonl` transcripts
- Written and read via dedicated helpers
- Errors on inaccessible files are handled gracefully (ENOENT, EACCES, EPERM)

Evidence: Metadata file handler (search for `".meta.json"`)


### CCR v2 Worker Registration

What: A new CCR v2 worker registration flow enables Claude Code to register workers with session servers via a `/worker/register` endpoint.

Details:
- Workers register and receive a `worker_epoch` from the server
- Epoch mismatch (409) handling is now callback-based instead of hard `process.exit(1)`
- Enables reconnection flows and transport handoff in CCR v2 sessions
- Worker registration is also available for standalone session creation (not just environment-based)

Evidence: Worker registration function (search for `"/worker/register"`) and epoch handling (search for `"epoch superseded"`)

### "Kill" Terminology Changed to "Stop"

Background agent management now uses softer language throughout the UI:
- "Press ctrl+f again to kill background agents" → "Press ctrl+f again to stop background agents"
- "Background agents were killed by the user" → "Background agents were stopped by the user"
- Agent status label changed from "Killed" to "Stopped"
- Command keywords: `kill agents` → `stop agents`, `kill all agents` → `stop all agents`

Evidence: Terminology change (search for `"stop agents"`) replacing old (search for `"kill agents"`)


### Improved Clipboard Error Messages on Windows/WSL

Clipboard copy failure messages now suggest both PowerShell and clip as alternatives:
- Windows: "Make sure `powershell` or `clip` is available on your system"
- WSL: "Make sure `powershell.exe` or `clip.exe` is available in your WSL environment"

Evidence: Updated error messages (search for `"powershell.exe"`)


### Task Tool: Simplified Background Agent Notifications

The Task tool's `run_in_background` description was simplified from "The tool result will include an output_file path — use Read tool or Bash tail to check on output" to "You will be notified when it completes."

Evidence: Updated background description (search for `"You will be notified when it completes"`)


### Task Tool: Agent Resume Support Documented

The Task tool's system prompt now documents that agents can be resumed using the `resume` parameter, that agent outputs should generally be trusted, and includes guidance on distinguishing research vs. code-writing tasks.

Evidence: New prompt text (search for `"Agents can be resumed using the \`resume\` parameter"`)


### Better Voice Recording No-Audio Detection

Voice recording now distinguishes between "no audio detected from microphone" (hardware/permission issue) and "no speech detected" (audio received but no speech recognized), providing more actionable error messages.

Evidence: Improved error message (search for `"No audio detected from microphone"`)


### MCP Instructions Now Delivered as Deltas

MCP server instructions are now delivered incrementally as a new `mcp_instructions_delta` attachment type, sending only added/removed server instructions instead of the full set each turn. Falls back to the previous full-set approach when the `tengu_basalt_3kr` feature flag is disabled.

Evidence: Delta attachment handler (search for `"mcp_instructions_delta"`)


### MIME Type Database Removed (Bundle Size Reduction)

The full IANA MIME type database (~4000+ entries) has been replaced with stubs that throw descriptive errors, significantly reducing bundle size. The stubs warn against relying on axios auto-multipart serialization.

Evidence: Stub implementation (search for `"mime-types."` and `"is stubbed in this build"`)


### mkdir Race Condition Fix

Both async and sync `mkdir` with `recursive: true` now catch `EEXIST` errors, fixing race conditions where parallel operations could fail when two processes try to create the same directory simultaneously.

Evidence: EEXIST handling in mkdir (search for `"EEXIST"` in the filesystem module at line ~3495)


### Remote Mode: Restricted defaultMode Settings

When running in `CLAUDE_CODE_REMOTE`, only `acceptEdits`, `plan`, and `default` are allowed as `defaultMode` values. Other modes are silently ignored with a warning logged.

Evidence: Remote mode restriction (search for `"is not supported in CLAUDE_CODE_REMOTE"`)


### ToolSearch Disabled for Non-First-Party Hosts

Optimistic ToolSearch is now properly disabled when `ANTHROPIC_BASE_URL` points to a non-first-party Anthropic host, preventing unnecessary tool search requests that would fail.

Evidence: Host check (search for `"[ToolSearch:optimistic] disabled: ANTHROPIC_BASE_URL="`)


### Plugin Auto-Refresh After Background Install

After marketplace plugins are installed in the background, Claude Code now auto-refreshes the plugin list immediately instead of just setting a `needsRefresh` flag, reducing the need for manual refresh.

Evidence: Auto-refresh logic (search for `"Auto-refreshing plugins after"`)


### Effort Level: New Environment Variables

- `CLAUDE_CODE_ALWAYS_ENABLE_EFFORT`: Force-enables the effort/reasoning level selector for all models
- `CLAUDE_CODE_EFFORT_LEVEL`: Override the effort level (set to `"unset"` to disable)
- Third-party models no longer unconditionally get effort level support; it's now checked against first-party host detection

Evidence: New env vars (search for `"CLAUDE_CODE_ALWAYS_ENABLE_EFFORT"` and `"CLAUDE_CODE_EFFORT_LEVEL"`)


### Rendering: Frame Contamination Tracking

Terminal rendering now tracks whether the previous frame was "contaminated" (had selection overlays or image clears), preventing unnecessary full-screen redraws and reducing flickering in alt-screen mode.

Evidence: New `prevFrameContaminated` property (search for `"prevFrameContaminated"`)


### Text Input: Improved Carriage Return Handling

The text input editor now strips trailing `\r` from single-line inputs more precisely and handles multi-line paste with trailing carriage returns, which improves behavior when pasting from Windows clipboard sources.

Evidence: CR handling in input editor (structural change in function `Uy1` at line ~452368)


### Git Watcher Initialization Order Fix

The git file watcher now sets `this.initialized = true` after (instead of before) calling `gitDir()`, preventing a race where the watcher could report as initialized before knowing the git directory.

Evidence: Initialization reorder in `ZFA` class (search for `"this.initialized"` near `"this.gitDir"`)

## Bug Fixes

- Fixed clipboard copy on Windows/WSL to suggest PowerShell as an alternative when `clip`/`clip.exe` is unavailable (search for `"powershell"`)
- Fixed `AskUserQuestion` tool input schema being re-parsed on every render by wrapping in `useMemo` (search for `"inputSchema.safeParse"`)
- Fixed remote hook (`useRemoteMode`) return value not being memoized, causing unnecessary re-renders (search for `"useMemo"` in `vQq`)
- Fixed destructive command warning and sandboxing check not being memoized in permission prompts (search for `"destructiveWarning"`)
- Fixed permission animation timer starting before component is visible by using `null` initial delay when `K` is true (search for `"lc6"`)
- Fixed `CLAUDE_CODE_EXTRA_BODY` env var to shallow-copy parsed object, preventing mutations to the cached parse result (search for `"CLAUDE_CODE_EXTRA_BODY"`)
- Fixed WebFetch HTML-to-Markdown converter (`Turndown`) being loaded eagerly; it's now lazy-loaded via dynamic import (search for `"turndown"`)
- Fixed Bash command argument parser to use case-insensitive comparison for command names like `python`/`Python3` (search for `"python3"`)
- Fixed early return from `onSubmit` when bridge reconnection is active, preventing accidental message submission (search for `"[onSubmit] early return"`)
- Fixed deferred context attachments (tips, changed files) leaking empty arrays when no items are found by adding early-return checks (search for `"if (K.length === 0) return []"`)

### Fork Agent [Feature-Flagged]

What: A new "fork" agent type for the Task tool that creates a copy of the current conversation context to process a task in the background.

Status: Feature-flagged — only triggers when the fork experiment is active.

Details:
- When the fork experiment is active, omitting `subagent_type` from the Task tool creates a fork instead of using the general-purpose agent
- Forks inherit the full conversation context from the parent
- Fork workers cannot create nested forks ("Fork is not available inside a forked worker")
- Uses `permissionMode: "bubble"` to propagate permission requests to the parent
- System prompt indicates: "You are a forked worker process" with worktree context awareness
- Maximum 200 turns per fork

Evidence: Fork agent definition (search for `"You are a forked worker process"`) and fork config (search for `"Implicit fork"`)


### BTW Side Questions Gating [Feature-Flagged]

What: The BTW side-question feature, previously hardcoded as disabled (`w1(void 0)` which was always `false`), is now properly gated behind the `tengu_marble_whisper` feature flag.

Status: Feature-flagged via `tengu_marble_whisper` (default `false`)

Details:
- All three references to the BTW feature (tip display, input parser, spinner tip) now check `gz6()` which reads `tengu_marble_whisper`
- This means the feature can be enabled server-side without a client update

Evidence: Feature gate function (search for `"tengu_marble_whisper"`)

## Notes

- The `coral_reef_sonnet` client data flag was added, checked via `YgA()` — this may gate future model-related behavior (search for `"coral_reef_sonnet"`)
- A `kairosActive` flag was added to session telemetry, tracked as `is_assistant_mode` in analytics (search for `"kairosActive"`)
- The telemetry event `tengu_session_quality_classification` was replaced by `tengu_session_file_read` (search for `"tengu_session_file_read"`)
- The "server" subcommand infrastructure (including WebSocket server, session management, auth tokens, direct-connect protocol, and `cc+unix://` URL scheme) has been removed, suggesting the standalone server mode has been deprecated in favor of the CCR bridge architecture
