# Changelog for version 2.1.78


## Summary

This release adds automatic memory consolidation ("auto-dream") as a feature-flagged background capability, introduces persistent data directories for plugins with a new `--keep-data` uninstall flag, adds a `StopFailure` hook event for reacting to API errors, and improves sandbox diagnostics with proactive warnings when sandboxing is unavailable. Voice mode on Linux/WSL also receives better hardware detection and clearer error messaging.


### StopFailure Hook Event

What: A new hook event type that fires when a turn ends due to an API error (rate limit, auth failure, billing error, etc.), distinct from the normal `Stop` event.

Usage:
```json
{
  "hooks": {
    "StopFailure": [
      {
        "type": "command",
        "command": "echo 'API error: $CLAUDE_HOOK_ERROR'"
      }
    ]
  }
}
```

Details:
- Fires instead of `Stop` when an API error ended the turn
- Fire-and-forget — hook output and exit codes are ignored
- Supports matching on error type: `rate_limit`, `authentication_failed`, `billing_error`, `invalid_request`, `server_error`, `max_output_tokens`, `unknown`

Evidence: Hook event definition (search for `"StopFailure"`) — added to the hook event schema with `matcherMetadata` on `"error"` field


### Plugin Persistent Data Directories

What: Plugins now get a dedicated persistent data directory at `~/.claude/plugins/data/{id}/`, accessible via the `CLAUDE_PLUGIN_DATA` environment variable and the `${CLAUDE_PLUGIN_DATA}` template in plugin configs.

Details:
- Each plugin receives its own data directory, created automatically
- The directory persists across plugin updates and sessions
- On plugin uninstall, users are prompted: "Delete it along with the plugin?" with the data directory path shown
- Use `--keep-data` flag with uninstall to preserve the data directory

Evidence: Plugin data path helper (search for `"CLAUDE_PLUGIN_DATA"`) — new env var injected into plugin processes; `--keep-data` CLI option (search for `"--keep-data"`)


### Sandbox Unavailability Warnings

What: Claude Code now proactively detects when sandboxing is configured but cannot actually run, and displays a clear warning at startup instead of silently falling back.

Details:
- Checks for missing dependencies (bubblewrap, socat on Linux; ripgrep), unsupported platforms, and WSL1 incompatibility
- Displays a warning: `⚠ Sandbox disabled: {reason}` followed by `Commands will run WITHOUT sandboxing. Network and filesystem restrictions will NOT be enforced.`
- The `/sandbox` diagnostic UI now also shows ripgrep status and uses "seatbelt: built-in (macOS)" labeling on macOS

Evidence: Sandbox check function (search for `"getSandboxUnavailableReason"`) and startup warning (search for `"Commands will run WITHOUT sandboxing"`)


### Custom Model Picker via Environment Variables

What: Administrators can inject a custom model option into the model picker via environment variables, useful for enterprise deployments with custom-routed models.

Usage:
```bash
export ANTHROPIC_CUSTOM_MODEL_OPTION="my-custom-model-id"
export ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="My Custom Model"
export ANTHROPIC_CUSTOM_MODEL_OPTION_DESCRIPTION="Custom routed model for our org"
```

Details:
- The custom model appears as an additional option in the model selection UI
- If no name is provided, the model ID is used as the label
- If no description is provided, defaults to `Custom model ({id})`

Evidence: Model picker injection (search for `"ANTHROPIC_CUSTOM_MODEL_OPTION"`)


### Monitor MCP Background Task Type

What: A new background task type `monitor_mcp` for MCP-based monitors that can run alongside the main conversation.

Details:
- Appears in the background tasks panel with status indicators ("done", "unread" for completed but unviewed)
- Displayed as "1 monitor" / "N monitors" in task counts

Evidence: Task type definition (search for `"monitor_mcp"`)


### Improved Voice Mode on Linux/WSL

Voice mode now probes the `arecord` audio device before attempting to record on Linux, providing clearer error messages when audio hardware is unavailable. On WSL specifically, the error message now explains WSL2 with WSLg (Windows 11) requirements:

> Voice mode could not access an audio device in WSL. WSL2 with WSLg (Windows 11) provides audio via PulseAudio — if you are on Windows 10 or WSL1, run Claude Code in native Windows instead.

Evidence: Audio probe function (search for `"arecord probe failed"`) and improved WSL message (search for `"WSLg"`)


### Auto Mode Classifier: `deny` Renamed to `soft_deny`

The auto mode classifier setting field `deny` has been renamed to `soft_deny` in the settings schema. This is a semantic clarification — existing `deny` rules in your config should be updated to `soft_deny`.

Evidence: Schema change (search for `"soft_deny"`)


### Transcript Viewer: Press `q` to Exit

You can now press `q` in addition to `Escape` or `Ctrl+C` to exit the transcript viewer.

Evidence: Keybinding addition (search for `"transcript:exit"`)


### Bridge Reconnection Resilience

The bridge reconnection logic now handles up to 2 consecutive failed `/bridge/reconnect` calls before falling through to a fresh session, improving reliability on flaky connections. Empty message arrays from resumed sessions are now also handled gracefully.

Evidence: Reconnect logic (search for `"Next 2 POST /bridge/reconnect"`) and empty-session guard (search for `"z.messages.length === 0"`)


### Terminal Mode Reassertion After Stdin Pause

The terminal renderer now re-asserts mouse tracking and raw mode settings when stdin resumes after a gap, preventing issues where terminal state was lost during long idle periods or after backgrounding the process.

Evidence: Terminal mode fix (search for `"reassertTerminalModes"`)


### Opus 4.6 Model Label Updated

The model picker label for Opus 4.6 no longer shows the `[NEW]` tag, reflecting that it's now the established default model.

Evidence: String change — old: `"Opus 4.6 with 1M context [NEW]"` → new: `"Opus 4.6 with 1M context"`


### Remote Session Credential Persistence

In remote/CCR environments, OAuth tokens and API keys are now persisted to well-known file paths (`/home/claude/.claude/remote/.oauth_token`, `/home/claude/.claude/remote/.api_key`) so that subprocesses can access credentials without inheriting file descriptors.

Evidence: Remote credential paths (search for `"/.oauth_token"`) and persistence function (search for `"Failed to persist"`)


### `CLAUDE_CODE_EXTRA_METADATA` Environment Variable

A new environment variable that lets you inject additional metadata (as a JSON object) into session telemetry. Useful for enterprise environments that need to tag sessions with org-specific identifiers.

Evidence: Metadata injection (search for `"CLAUDE_CODE_EXTRA_METADATA"`)


### Sandbox Dependency Check: Bare-Repo File Scrubbing

The sandbox initialization now detects and scrubs "planted" bare-repo files (directories like `HEAD`, `objects`, `refs`, etc.) that could be mistakenly treated as git repository internals.

Evidence: Scrubbing function (search for `"scrubbed planted bare-repo file"`)


### Syntax Highlighting Refactored to React Suspense

Code highlighting for diffs, code blocks, and tool use previews has been refactored to use React Suspense with lazy loading. The highlighter module is loaded asynchronously, showing an unhighlighted fallback until ready. This should improve perceived startup time.

Evidence: Suspense-based highlighting wrapper (search for `"Suspense"` near highlight components)


### Remote Control Command Availability

Commands that aren't usable in Remote Control mode now return a clear message: `/{command} isn't available over Remote Control.`

Evidence: Availability check (search for `"isn't available over Remote Control"`)


## Bug Fixes

- Fixed bridge session resumption failing silently when the resumed session has zero messages — now correctly falls through to a fresh session (search for `"z.messages.length === 0"`)
- Fixed `ANTHROPIC_BETAS` environment variable not being applied in all request contexts — the beta header filter was incorrectly gated on a condition that could prevent user-specified betas from being sent (search for `"ANTHROPIC_BETAS"`)
- Telemetry `additional_metadata` is now base64-encoded before transmission, fixing potential encoding issues with JSON payloads (search for `"base64"`)


### Auto-Dream: Automatic Memory Consolidation [In Development]

What: A background process that automatically reviews recent session transcripts and consolidates insights into your memory files, similar to running a manual memory consolidation pass but triggered automatically.

Status: Feature-flagged via `tengu_onyx_plover` — disabled by default (`enabled: !1`).

Details:
- When enabled, triggers after a configurable minimum hours (default: 24h) and minimum sessions (default: 5) since last consolidation
- Uses a `.consolidate-lock` file with PID-based locking to prevent concurrent consolidation
- Runs as a forked background query with `querySource: "auto_dream"` that reads session transcripts and updates memory files
- Includes throttling to prevent excessive scanning (minimum gap between scans)
- The dream prompt instructs the model to orient by reading existing memories, gather signal from recent sessions, consolidate into topic files, and prune the index
- Telemetry events: `tengu_auto_dream_fired`, `tengu_auto_dream_completed`, `tengu_auto_dream_failed`

Evidence: Dream infrastructure (search for `"autoDream"`) — gated by `tengu_onyx_plover` flag (search for `"tengu_onyx_plover"`)
