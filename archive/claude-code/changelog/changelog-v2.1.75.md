# Changelog for version 2.1.75


## Summary

This release introduces Opus 1M context as the default for first-party Opus users, adds a memory staleness system that warns when recalled memories may be outdated, redesigns the SendMessage tool for more intuitive agent-to-agent communication, and introduces plugin configurable options. Several quality-of-life improvements include concurrent session detection, an auto mode circuit breaker, and a new SSH `startDirectory` setting.

### Opus 1M Context Window Default

What: First-party Opus users now default to a 1M token context window (5x larger), with automatic migration from the standard Opus setting.

Details:
- Controlled by the `tengu_cobalt_compass` feature flag (gradual rollout)
- Users who had "opus" selected are automatically migrated to "opus[1m]"
- A merge notice is shown up to 6 times: "Opus now defaults to 1M context · 5x more room, same pricing"
- When Opus 1M is active, Opus no longer triggers "Billed as extra usage" — same pricing as before
- The model picker now offers an explicit "Opus (1M context)" entry labeled `[NEW]`

Evidence: Opus 1M migration and display (search for `"tengu_cobalt_compass"`, `"Opus now defaults to 1M context"`, `"tengu_opus_to_opus1m_migration"`)


### Plugin Configurable Options

What: Plugins can now declare user-configurable options in their manifest via a `userConfig` schema, with typed fields, defaults, and secure storage for sensitive values.

Details:
- Plugin manifests can include a `userConfig` block with named options of type `string`, `number`, `boolean`, `directory`, or `file`
- Each option supports `title`, `description`, `required`, `default`, `sensitive`, `min`/`max`, and `multiple` fields
- Option keys must be valid identifiers — they become `CLAUDE_PLUGIN_OPTION_<KEY>` environment variables in hooks
- Sensitive values are stored in secure storage (macOS keychain or `.credentials.json`), non-sensitive values in `settings.json`
- Available as `${user_config.KEY}` in MCP/LSP server config, hook commands, and (non-sensitive only) skill/agent content

Evidence: Plugin options schema and env var injection (search for `"CLAUDE_PLUGIN_OPTION_"`, `"User-configurable values this plugin needs"`)


### SSH Start Directory Setting

What: SSH remote configurations now support a `startDirectory` field to set the default working directory on the remote host.

Usage:
```json
{
  "sshRemotes": {
    "my-server": {
      "host": "example.com",
      "startDirectory": "~/projects"
    }
  }
}
```

Details:
- Supports tilde expansion (e.g., `~/projects`)
- If not specified, defaults to the remote user's home directory
- Can be overridden by the `[dir]` positional argument in `claude ssh <config> [dir]`

Evidence: SSH start directory setting (search for `"startDirectory"`, `"Default working directory on the remote host"`)


### Memory Staleness Warnings

What: Memories recalled from CLAUDE.md and project memory files are now annotated with their age, warning Claude when recalled information may be outdated.

Details:
- Memories older than 1 day display their age (e.g., "Memory (saved yesterday)" or "Memory (saved 5 days ago)")
- Memories older than 1 day include a system reminder: "Memories are point-in-time observations, not live state — claims about code behavior or file:line citations may be outdated. Verify against current code before asserting as fact."
- This helps prevent Claude from asserting stale file:line references or code behavior as current fact

Evidence: Memory age formatting and staleness warnings (search for `"Memories are point-in-time observations"`, `"claims about code behavior"`)


### Agent Message Queuing to Running Agents

What: When resuming a running agent via `Agent({resume: id})`, the prompt is now queued for delivery instead of throwing an error. Coordinators can also send messages to running agents via `SendMessage`.

Details:
- If an agent is already running, calling `Agent({resume: id})` queues the prompt and returns a `queued_to_running` status
- The agent receives the queued message at its next tool-round boundary
- `SendMessage({to: "<name>", message: "..."})` can also queue messages to running local agents
- A coordinator message is rendered with: "The coordinator sent a message while you were working: [...] Address this before completing your current task."

Evidence: Agent message queue system (search for `"queued_to_running"`, `"Message queued for delivery"`, `"pendingMessages"`)


### Concurrent Session Detection

What: Claude Code now detects when multiple sessions are running simultaneously and offers a relevant tip.

Details:
- Sessions register PID files in the Claude Code data directory
- When 2+ sessions are detected, a tip suggests: "Running multiple Claude sessions? Use /color and /rename to tell them apart at a glance."
- Session count is also reported via telemetry (`tengu_concurrent_sessions`)

Evidence: Concurrent session tracking (search for `"concurrentSessions"`, `"color-when-multi-clauding"`)

### SendMessage Tool Redesigned

The `SendMessage` tool schema has been simplified from a discriminated union with `type`/`recipient`/`content` fields to a more intuitive `to`/`message`/`summary` format. Agents now use `to: "<name>"` for direct messages and `to: "*"` for broadcasts. Structured protocol messages (shutdown requests, plan approvals) are sent as objects in the `message` field. A backward-compatibility shim (`backfillObservableInput`) translates old-format calls.

Evidence: Simplified SendMessage schema (search for `"Recipient: teammate name"`, `'to must be a bare teammate name or "*"'`)


### Auto Mode Circuit Breaker

Auto mode can now be remotely disabled via a server-side gate. When the circuit breaker is active, auto mode requests silently fall back to the default permission mode with a warning logged. The `claude auto-mode` subcommand is also hidden when auto mode is disabled.

Evidence: Auto mode circuit breaker (search for `"auto mode circuit breaker active (cached)"`, `"Cannot transition to auto mode"`)


### File Read Size Controlled by Feature Flag

File read limits (`maxSizeBytes` and `maxTokens`) are now configurable via the `tengu_amber_wren` feature flag, allowing server-side tuning of read limits without client updates. A new `CLAUDE_CODE_AUTO_COMPACT_WINDOW` environment variable also allows users to override the auto-compaction window size.

Evidence: Feature-flag-controlled read limits (search for `"tengu_amber_wren"`, `"CLAUDE_CODE_AUTO_COMPACT_WINDOW"`)


### Background Task Monitor Distinction

The status bar now distinguishes between regular background tasks and monitors, showing counts like "2 background tasks, 1 monitor" instead of a single combined count.

Evidence: Monitor/task distinction in status line (search for `"Monitor details"`, `kind === "monitor"`)


### Shift+Arrow Navigation for Teammates

The keyboard shortcut to expand teammate views has changed from `↓` to `shift + ↓`. A new `shift + ↑` shortcut navigates upward through the teammate list.

Evidence: Updated keybindings (search for `"shift + ↓"`)


### Leader Idle State Display

When the team leader is idle but teammates are still working, the spinner now shows a distinct "Idle · teammates running" state instead of the generic working indicator.

Evidence: Leader idle state in spinner (search for `"· teammates running"`, `leaderIsIdle`)


### Session Metadata Enrichment

Session metadata returned by `listSessions` and `getSessionInfo` now includes `tag` (user-set session tag) and `createdAt` (creation timestamp). The `fileSize` field is now optional and only populated for local JSONL storage.

Evidence: Expanded session metadata schema (search for `"User-set session tag"`, `"Creation time in milliseconds since epoch"`)


### Marketplace Name Security Validation

Marketplace names now reject path traversal patterns — names containing `/`, `\`, `..` sequences, or consisting of just `.` are rejected with a clear error message.

Evidence: Path traversal validation (search for `'Marketplace name cannot contain path separators'`)


### Credential Redaction in Git Clone Logs

URLs containing embedded usernames or passwords are now redacted when logged during git clone operations, preventing accidental credential exposure in logs.

Evidence: URL credential redaction function `A96()` (search for `q.username = "***"`)


### Permission Mode Change Events

Permission mode changes (default, acceptEdits, bypassPermissions, auto, etc.) are now emitted as system status events on the outbound stream, enabling external integrations to track permission state.

Evidence: Permission mode event emission (search for `"permissionMode"`, `Tkq`)


### Skill/Prompt Aliases

Skills and prompts now support an `aliases` field, enabling multiple names for the same slash command.

Evidence: Aliases support in prompt definitions (search for `aliases: A.aliases`)


### Hook Source Tracking

Hooks now carry `hookSource` metadata indicating their origin (e.g., `plugin:name`, `skill:name`, or `settings`), improving debuggability.

Evidence: Hook source annotation (search for `"hookSource"`)


### Error Details on Prompt Too Long

When an API request fails with "prompt is too long", the error response now includes `errorDetails` with the full exception message, providing more diagnostic context.

Evidence: Error details propagation (search for `"errorDetails"`)

## Bug Fixes

- Fixed `readFileState` being recomputed from messages on every turn — the main session class now caches and reuses it, improving performance (search for `"readFileState"`)
- Removed redundant `existsSync` checks before `readFileSync` and `unlinkSync` calls, fixing potential race conditions (search for `unlinkSync`)
- Fixed the tag-clearing behavior: setting an empty tag now correctly clears it (`tag || void 0`) instead of keeping the empty string (search for `"currentSessionTag"`)
- Voice-enabled checks now additionally gate on `$I()`, preventing voice features from activating when conditions aren't fully met (search for `voiceEnabled`)
- The `user:file_upload` OAuth scope is now requested for first-party authenticated sessions (search for `"user:file_upload"`)
- Fixed async hook response rendering: previously only showed for PreToolUse/PostToolUse when tool hooks were enabled; now also shows for SessionStart and other hook types when session hooks are enabled (search for `"async_hook_response"`)

## Removed

- **Nested session restriction removed**: The check that prevented launching Claude Code inside another Claude Code session (via the `CLAUDECODE=1` environment variable) has been removed. Users can now nest sessions freely. (search for `"Nested sessions share runtime resources"` — present in v2.1.74, absent in v2.1.75)

- **Windows ProgramData deprecation warning removed**: The notification warning about migrating `C:\ProgramData\ClaudeCode\managed-settings.json` to `C:\Program Files\ClaudeCode\` has been removed, along with the associated detection logic. (search for `"programdata-deprecation-warning"` — present in v2.1.74, absent in v2.1.75)

## In Development

Features with infrastructure added but not yet enabled or partially gated.


### Opus 1M Context [Gradual Rollout]

What: The Opus 1M context window default is controlled by the `tengu_cobalt_compass` feature flag with a default of `false`.

Status: Feature-flagged, rolling out gradually.

Details:
- The function `UH()` checks `tengu_cobalt_compass` — returns `false` by default
- Only applies to first-party users (not API key users or third-party)
- Excluded when `je()` (demo mode) or `ZC()` (certain restricted contexts) is active
- Once enabled server-side, migration is automatic

Evidence: Feature gate check (search for `"tengu_cobalt_compass"`) — `UH()` at line ~532570
