# Changelog for version 2.1.122

## Summary

This release adds Cmd+K clear screen support, MCP long-running task tracking, a new "bash_command" event type for remote sessions, and "investigate first" system prompt injection gated behind `tengu_slate_harrier`. It also introduces the `ANTHROPIC_BEDROCK_SERVICE_TIER` environment variable for Bedrock users, improves MCP server duplicate detection with user-facing guidance, adds `--bg` safety guards, and reduces the Opus 4.7 image resolution limit from 2576px to 2000px.


### Cmd+K Clear Screen

What: Adds a `Cmd+K` keyboard shortcut (macOS) mapped to a new `chat:clearScreen` action, providing a way to visually clear the terminal display without losing conversation context.

Usage: Press `Cmd+K` in the chat input to clear the screen. This is separate from `Ctrl+L` (clear input), which only empties the input field.

Details:
- Bound as `"cmd+k": "chat:clearScreen"` in the default keybindings
- On iTerm and Apple Terminal, the feature also probes for external clears (e.g. via Cmd+K in the terminal itself) and automatically redraws the UI when an outside wipe is detected
- The clear screen action triggers `/clear` internally
- A brief "clear" hint is shown before the action takes effect

Evidence: New keybinding action (search for `"chat:clearScreen"`) and external wipe detection (search for `"probeExternalClear"`)


### MCP Long-Running Task Tracking

What: Adds infrastructure to track, poll, persist, and resume MCP tasks that run asynchronously on MCP servers using the experimental tasks API.

Details:
- When a tool call spawns an MCP task, Claude Code now registers it in a task registry and polls the server for status updates
- Task metadata is persisted to disk at `<session-dir>/mcp-tasks/mcp-task-<id>.meta.json` so tasks survive session restarts
- On resume, previously-running MCP tasks are reconnected to their servers and polling resumes
- Task status updates (completed, failed, cancelled) are injected back into the conversation as task-notification messages
- The status bar shows `1 MCP task` (or similar) during active polling
- Supports kill/cancel from the client side

Evidence: Full task lifecycle management (search for `"mcp_task"`, `"restoreMcpTasks"`, `"removeMcpTaskMetadata"`, `"Task was cancelled by the server."`)


### Remote Session Bash Command Event

What: Adds a new `bash_command` event type that allows remote clients (e.g. Claude Code Remote) to dispatch shell commands directly to a session without going through the model.

Details:
- The event schema includes a `command` string and optional `cwd` for the working directory
- Executed via a one-shot `/bin/sh -c` (or `pwsh` on Windows) subprocess, bypassing the model entirely
- Output includes stdout, stderr, and exit code wrapped in XML tags
- This allows CCR clients that surface a dedicated terminal UI to run shell commands natively

Evidence: New Zod schema with `type: "bash_command"` (search for `"bash_command"`) and handler function `sendBashCommand` (search for `"[RemoteSessionManager] Sending bash_command to session"`)


### Bedrock Service Tier Support

What: Adds support for the `ANTHROPIC_BEDROCK_SERVICE_TIER` environment variable, which lets Bedrock users specify a service tier via a custom request header.

Usage:
```bash
export ANTHROPIC_BEDROCK_SERVICE_TIER="on-demand"
claude
```

Details:
- When set, the value is passed as the `X-Amzn-Bedrock-Service-Tier` header on all Bedrock API requests
- Displayed in the connection info (e.g. `/config` or status display) as "Bedrock service tier"

Evidence: New env var handling (search for `"ANTHROPIC_BEDROCK_SERVICE_TIER"`) and display label (search for `"Bedrock service tier"`)


### Background Job Safety Guards

What: Adds upfront validation for `--bg` jobs that require specific permission modes, preventing silent failures when prerequisites are not met.

Details:
- Running `--bg` with `--permission-mode auto` now requires having opted in interactively first. If not, the error message reads: `--bg with auto mode requires opting in first. Run 'claude --permission-mode auto' once interactively.`
- Running `--bg` with `--dangerously-skip-permissions` now requires having accepted the disclaimer interactively first. The error message reads: `--bg with bypassPermissions requires accepting the disclaimer first. Run 'claude --dangerously-skip-permissions' once interactively.`

Evidence: New validation function (search for `"--bg with auto mode requires"` and `"--bg with bypassPermissions requires"`)


### MCP Server Duplicate Detection UI

What: When a connector-type MCP server would duplicate an already-configured server, Claude Code now shows it as "hidden" with actionable guidance on how to switch to the alternative.

Details:
- Hidden servers display as `<name> · ○ hidden — same URL as your server '<duplicateOf>'`
- Depending on where the duplicate is configured, users see specific instructions:
  - Plugin servers: "To use this connector instead, disable the plugin server in /plugins"
  - Local/user/project config: "To use this connector instead: `claude mcp remove <name>`"
  - Dynamic (via `--mcp-config`): "To use this connector instead, drop it from your --mcp-config flag"
  - Enterprise/managed: "An admin-managed server takes precedence here"
- Tracks `duplicateOf` and `duplicateOfScope` for each suppressed server

Evidence: Duplicate hint rendering (search for `"hidden \u2014 same URL as your server"`) and scope-based guidance (search for `"claude mcp remove"`, `"An admin-managed server takes precedence here"`)


### Web Search Isolation Exemption for MCP Servers

What: Adds a new `webSearchIsolationExemptMcpServers` init config field that lets specific MCP servers bypass the web search / connector isolation latch.

Details:
- Accepts an array of MCP server names
- These servers are unioned with the built-in infrastructure server list, so they remain accessible even when the isolation latch is engaged
- Marked as `@internal` — intended for SDK/API integrators, not end-user configuration

Evidence: New schema field (search for `"webSearchIsolationExemptMcpServers"`)


### "workspace" Reserved as MCP Server Name

What: The name `"workspace"` is now reserved and cannot be used when adding a custom MCP server.

Details:
- Attempting to add an MCP server named "workspace" will throw: `Cannot add MCP server "workspace": this name is reserved.`

Evidence: New reserved name check (search for `xeH = "workspace"` at line ~55807)


### AI-Generated Session Titles

The "aiTitle" system, which generates session titles automatically, has been significantly expanded in this release. Sessions now track both a user-set `customTitle` and an auto-generated `aiTitle` separately. The AI title is persisted in the session journal, displayed in the resume picker, and used as the terminal title when no user-set title exists. The `/resume` list now shows sessions with AI-generated titles even if the user never set a custom title.

Evidence: New `currentSessionAiTitle` field and `"type":"ai-title"` journal entries (search for `"ai-title"`, `"aiTitle"`)


### Fast Mode Tag in Input Box Border

The input box border now displays a mode indicator tag (e.g. the model name and `/fast` toggle state) inline in the top-right corner of the border, replacing the previous approach. This is rendered by the new `OZ5` component.

Evidence: New border tag component (search for `fastModeTag` in the `OZ5` function at line ~629655)


### Reduced Opus 4.7 Image Resolution Limit

The maximum image dimension for `claude-opus-4-7` has been reduced from 2576×2576 to 2000×2000 pixels, which may reduce token usage for image-heavy conversations.

Evidence: Changed constant (search for `maxWidth: 2000, maxHeight: 2000`)


### Improved MCP OAuth Error Recovery

When an OAuth `invalid_grant` error is encountered, Claude Code now proactively clears the stale refresh token from both the file-based and config-based credential stores, rather than leaving it to fail on every subsequent request. This should reduce repeated auth failures after token expiration.

Evidence: New `invalid_grant` detection and token clearing (search for `"invalid_grant"`, `"tengu_oauth_refresh_token_cleared_invalid_grant"`, `"tengu_wif_user_oauth_refresh_token_cleared"`)


### Improved MCP Authentication Error Messages

MCP server authentication error messages have been rewritten to be more specific and actionable:
- Old: "Authentication successful, but server still requires authentication. You may need to manually restart Claude Code."
- New: "Tried reconnecting, but <name> is still unauthorized. Make sure the browser sign-in completed, then try again from /mcp."
- Old: "Authentication successful, but server reconnection failed."
- New: "Tried reconnecting to <name>, but the connection failed. Restart Claude Code to retry."

Evidence: Improved error messages (search for `"Tried reconnecting, but"`, `"Tried reconnecting to"`)


### Background Worker Crash Visibility

When a background worker crashes and is respawning, a visible message is now written to the worker's output stream: `[worker crashed (<reason>) — respawning…]`. Previously, crashes were silent from the user's perspective.

Evidence: New crash notification (search for `"[worker crashed ("`)


### Background Worker Respawn with Session Continuity

Background workers now track a `resumeSessionId` separately from `sessionId`, allowing a respawned worker to resume the correct session even if internal state has been updated. The respawn flag list is also persisted and restored on crash recovery, ensuring workers re-launch with the correct CLI flags.

Evidence: New `resumeSessionId` field (search for `"resumeSessionId"`) and flag persistence (search for `"respawnFlags"`)


### Piped Stdin Size Warning

When piping content into Claude Code, if the input exceeds the internal limit (1 MB), the excess is now silently truncated and a warning is printed to stderr: `warning: piped stdin exceeds <limit> bytes, truncated`. Previously, very large piped inputs could cause issues.

Evidence: New stdin truncation handler (search for `"piped stdin exceeds"`)


### Improved Docker Command Safety Checks

Docker `logs` and `inspect` commands now check for dangerous global flags like `--host`, `--context`, `--tlscacert`, `--tlscert`, and `--tlskey` that could redirect the Docker daemon connection. These flags will now trigger permission prompts.

Evidence: New Docker global flag checking (search for `"--tlscacert"`)


### Improved `find` Command Safety Checks

The `find` command's safe-flag list has been expanded to include `-D`, `-f`, `-flags`, `-Bnewer`, `-Btime`, `-Bmin`, `-files0-from`, and `-xattrname`. Additionally, the `test`/`[`/`[[` builtins now flag `-t` operands with non-numeric values as potentially dangerous, since bash/zsh can arithmetically evaluate identifiers that may trigger command execution.

Evidence: Expanded find flags (search for `"-files0-from"`, `"-xattrname"`) and test safety (search for `"operand is non-numeric"`)


### Text Cursor Navigation Handles Placeholders

The text input cursor now correctly navigates around multi-character placeholder tokens like `[Pasted text #1]`, `[Image #1]`, and `[...Truncated text #1]` as atomic units. Word-movement commands (w, b, e in vim mode and Ctrl+arrows) skip over these placeholders rather than stepping through them character-by-character.

Evidence: New placeholder-aware cursor movement (search for `"placeholderEndingAt"`, `"placeholderStartingAt"`, `"snapOutOfPlaceholder"`)


### Certificate Validation: basicConstraints Check

TLS certificate validation now explicitly checks for the `basicConstraints` extension. Certificates missing this extension are rejected with: "Certificate is missing basicConstraints extension and cannot be used as a CA."

Evidence: New validation check (search for `"Certificate is missing basicConstraints extension"`)


### Plan Mode Prompt Consolidation

The three separate plan mode phase-4 prompt variants (controlled by `tengu_pewter_ledger` returning "trim", "cut", or "cap") have been removed. The feature flag `tengu_pewter_ledger` is no longer read. Plan mode now uses a single consolidated prompt.

Evidence: Removed `A98()` function and `pU1`/`BU1`/`FU1` prompt variants (previously searched for `"tengu_pewter_ledger"` — now absent from v2.1.122)


### Removed `loopAutoEnabled` Setting

The `loopAutoEnabled` user setting has been removed from the persisted settings list.

Evidence: Removed from settings list (search for `"loopAutoEnabled"` — absent from v2.1.122)


### Worker Init PUT Retry Logic

The daemon worker initialization PUT request now retries up to 3 times with exponential backoff (500ms base, max 30s) before giving up. Previously, a single failure would immediately throw. A telemetry event `tengu_bg_pty_unavailable` is logged if all retries are exhausted.

Evidence: New retry logic in worker init (search for `"cli_worker_init_put_retries_exhausted"`)


### Background Process SIGTERM Escalation

When killing a background shell process with SIGTERM, if the process doesn't exit within 5 seconds, it's now automatically escalated to SIGKILL. This prevents zombie processes from lingering indefinitely.

Evidence: New SIGKILL escalation timeout in the pty manager (visible in the `yM8` structural change adding a 5000ms timeout for SIGTERM→SIGKILL escalation)


### API Request Detail Logging

When verbose logging is enabled, Claude Code now logs detailed API request metadata including model, thinking config, output config, temperature, and beta flags as `[API REQUEST DETAIL]`.

Evidence: New verbose logging (search for `"[API REQUEST DETAIL]"`)


### MCP Server Input Request Shows Task ID

When an MCP server requests user input, the dialog title now includes a truncated task ID (e.g. `MCP server "foo" requests your input (task abc12345)`) to help distinguish between multiple concurrent requests.

Evidence: Task ID in MCP input dialog (visible in `ZP5` structural change appending task ID to title)


### Improved URL Pattern Matching for Permissions

The URL pattern matching system used for web fetch permissions has been rewritten with more robust handling. It now uses a placeholder-based approach for wildcards, properly handles protocols, ports, and paths, and falls back to regex matching when the pattern isn't a valid URL.

Evidence: New `WY$` function with comprehensive URL matching (search for `"zzwildcard"`)


### "Caps Lock" Tooltip

A new informational string "Caps Lock is not delivered to terminal applications" has been added, likely shown as a tooltip or hint when relevant.

Evidence: New string (search for `"Caps Lock is not delivered"`)


## Bug Fixes

- Fixed an issue where `exit`/`quit` typed in bash reply mode would incorrectly trigger the session exit handler. The check now only applies when in prompt mode, not bash mode. (search for `"bash" && !v && f38.includes`)

- Fixed phantom parent UUID handling during transcript persistence — when a `sourceToolAssistantUUID` references a UUID not present in the current write set, it's now detected and logged via `tengu_phantom_parent_write` telemetry rather than silently creating a dangling reference. (search for `"tengu_phantom_parent_write"`)

- Fixed transcript walk to detect and gracefully handle phantom parent references that point to non-existent slots, logging `tengu_transcript_phantom_parent` telemetry and falling back to the full transcript instead of potentially producing an incomplete view. (search for `"tengu_transcript_phantom_parent"`)

- Fixed the `/branch` (fork) operation to respect the actual message ordering from the current session, ensuring forked sessions preserve the correct conversation flow. (search for `GQ7` which now takes messages as a parameter)

- Fixed RSA signature verification to enforce minimum PKCS#1 v1.5 padding length (8 bytes), preventing potential signature forgery attacks. Added `_skipPaddingChecks` option for backward compatibility. (search for `"_skipPaddingChecks"`)

- Fixed ed25519 signature verification to check scalar values are within the valid range, rejecting signatures with out-of-range S values. (search for `"Jg1"` in the ed25519 verification path)

- Fixed BigInteger `modInverse` to handle zero input correctly, returning `ZERO` instead of potentially entering an infinite loop. (search for `"this.signum() == 0"` in the `sp_` function)

- Fixed semver prerelease identifier parsing to check numeric identifiers before non-numeric, matching the correct semver specification order. (search for `"PRERELEASEIDENTIFIER"` in the structural change)


### "Investigate First" System Prompt [Gradual Rollout]

What: A new system prompt injection that instructs Claude to investigate before asking clarifying questions, gated behind the `tengu_slate_harrier` feature flag and configurable via `CLAUDE_CODE_INVESTIGATE_FIRST` environment variable.

Status: Feature-flagged via `tengu_slate_harrier` (defaults to `"off"`). Only applies when using `claude-opus-4-7`.

Details:
- Two modes: `"additive"` (adds investigation guidance to the existing "executing actions with care" prompt) and `"compact"` (uses a shorter version of the actions prompt plus investigation guidance)
- In both modes, adds: "Asking the user a clarifying question has a cost: it interrupts them... Before asking, spend up to a minute on read-only investigation (grep the codebase, check docs, search memory) so your question is specific."
- Can be overridden via `CLAUDE_CODE_INVESTIGATE_FIRST=additive|compact|off`

Evidence: Feature flag check (search for `"tengu_slate_harrier"`) and env var (search for `"CLAUDE_CODE_INVESTIGATE_FIRST"`)


### New Init Flow [Gradual Rollout]

What: A new initialization/onboarding flow, controlled by both the `CLAUDE_CODE_NEW_INIT` environment variable and the new `tengu_new_init` feature flag.

Status: Feature-flagged via `tengu_new_init` (defaults to `false`).

Details:
- The flag was previously only checkable via env var; now it can also be server-controlled via the `tengu_new_init` feature flag
- The actual new init experience is not yet visible in this diff

Evidence: Dual-check function (search for `"CLAUDE_CODE_NEW_INIT"` and `"tengu_new_init"`)


## Notes

- The `--autocompact` flag string now appears in the codebase, suggesting auto-compaction may be controllable as a CLI flag in the future. The implementation appears to be connected to existing compaction infrastructure with `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` and `CLAUDE_CODE_BLOCKING_LIMIT_OVERRIDE` environment variables.
- The `loopAutoEnabled` user setting has been removed. If you relied on this setting, it no longer has any effect.
- The Opus 4.7 image resolution limit change from 2576px to 2000px may affect workflows that rely on high-resolution image analysis.
