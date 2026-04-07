# Changelog for version 2.1.73


## Summary

This release adds the `--remote-control` CLI flag for launching Remote Control sessions directly from the command line, introduces native clipboard image reading on macOS for faster paste workflows, and deprecates the `/output-style` command in favor of `/config`. Under the hood, it adds a new `modelOverrides` enterprise setting, improves plugin dependency resolution, strengthens Bash command safety analysis, and adds SSH session management infrastructure for remote connections.

### `--remote-control` CLI Flag

What: Start Claude Code with Remote Control enabled directly from the command line, optionally naming the session.

Usage:
```bash
claude --remote-control
claude --remote-control my-project
claude --rc my-project          # shorthand alias
```

Details:
- Launches Claude in "spawn mode," which lets you create new sessions in the current project from Claude Code on Web or the Mobile app
- Supports `--spawn=same-dir` (default) or `--spawn=worktree` for git worktree isolation
- Includes a circuit breaker: if Remote Control encounters repeated failures, it disables itself for the session with a message to restart
- Checks account eligibility and shows `"Remote Control is not enabled for your account; --rc flag ignored."` if unavailable

Evidence: Remote Control spawn mode (search for `"--remote-control"`, `"Alias for --remote-control"`, `"Remote Control disabled after repeated failures"`)


### Model ID Override Mapping (Enterprise)

What: Enterprise administrators can now map Anthropic model IDs to provider-specific model IDs (e.g., Bedrock inference profile ARNs) via managed settings.

Details:
- New `modelOverrides` setting in the configuration schema
- Maps standard Anthropic model names (e.g., `"claude-opus-4-6"`) to provider-specific identifiers
- Reverse mapping is applied when resolving model families, so features that depend on knowing the model class (opus/sonnet/haiku) continue to work correctly
- Typically set by enterprise administrators in managed settings files, not by end users

Evidence: Model override resolver — `Wfq()` and `Dk1()` at ~line 529379 (search for `"Override mapping from Anthropic model ID"`)


### Auto Mode Configuration Inspector

What: New subcommands for inspecting how auto mode is configured, useful for debugging why auto mode approves or denies certain actions.

Usage:
```bash
claude auto-mode                # overview of classifier configuration
claude auto-mode defaults       # print default environment, allow, and deny rules as JSON
claude auto-mode config         # print effective config (your settings merged with defaults)
```

Details:
- `defaults` prints the built-in auto mode rules as JSON
- `config` shows the merged view: your custom settings where they exist, defaults otherwise
- Helps diagnose unexpected auto mode approval or denial behavior

Evidence: Auto mode inspection commands (search for `"Print the default auto mode environment"`, `"Print the effective auto mode config"`, `"Inspect auto mode classifier configuration"`)


### New Keyboard Shortcuts

What: Three new global application keybindings are now available.

Details:
- `app:globalSearch` — trigger global search
- `app:quickOpen` — quick-open file picker
- `app:toggleBrief` — toggle brief output mode (bound to `Ctrl+Shift+B`)

Evidence: New keybinding action identifiers (search for `"app:globalSearch"`, `"app:quickOpen"`, `"app:toggleBrief"`)

### Native Clipboard Image Reading on macOS

Clipboard image detection and reading on macOS now uses a native module when available (gated by the `tengu_collage_kaleidoscope` flag), bypassing the slower `osascript` approach. When a clipboard image is detected, users see an `"Image in clipboard · [key] to paste"` notification. The native path reads PNG data directly, handles resizing, and falls back to the original osascript method if the native module is unavailable.

Evidence: Native clipboard reader (search for `"native clipboard reader unavailable"`, `"Image in clipboard"`, `"tengu_collage_kaleidoscope"`)


### Plugin Dependency Resolution

Plugin installation now resolves transitive dependencies. When installing a plugin that declares dependencies, Claude Code validates the entire dependency closure and reports issues clearly:
- Dependency cycles are detected and reported: `"Dependency cycle: A → B → A"`
- Cross-marketplace dependencies are blocked with an explanation
- Missing dependencies report which marketplace they expected to be in
- Installation messages now show the dependency count: `"✓ Installed my-plugin (+ 2 dependencies)"`
- Disabled dependencies are flagged: `"disabled — enable it or remove the dependency"`

Evidence: Plugin dependency resolver (search for `"Dependency cycle"`, `"cross-marketplace"`, `"not found in any configured marketplace"`)


### Improved Bash Command Safety Analysis

The Bash command safety checker now correctly parses command wrappers that prepend the real command, preventing false safety denials when using common Unix utilities:
- `timeout` — parses `--foreground`, `--kill-after`, `--preserve-status`, `--signal`, and duration arguments
- `stdbuf` — parses `-i`, `-o`, `-e` buffer-mode flags
- `env` — parses environment variable assignments and `-i`, `-0`, `-u`, `-v` flags
- `time`, `nohup`, `nice` — unwrapped to find the actual command being run
- These wrappers are recursively stripped before analyzing the inner command for safety

Evidence: Command wrapper parsing (search for `"--foreground"`, `"--kill-after"`, `"--preserve-status"`, `"stdbuf"`)


### `/output-style` Deprecated in Favor of `/config`

The `/output-style` command has been deprecated. It now shows a message directing users to `/config` or the settings file. The command is hidden from help output but still works for backwards compatibility.

Evidence: Deprecation handler (search for `"/output-style has been deprecated"`, `"Deprecated: use /config to change output style"`)


### Simplified Effort Level Setting

The `effortLevel` setting description was simplified from `"Persisted effort level for supported models. \"max\" is session-scoped and not persisted."` to just `"Persisted effort level for supported models."` — the session-scoped restriction on "max" has been lifted.

Evidence: Effort level schema change (search for `"Persisted effort level for supported models"`)


### Rewritten SendUserMessage Prompt

The system prompt for the `SendUserMessage` tool has been significantly condensed. The old version was a detailed multi-paragraph guide with examples. The new version is a concise description: `"Send a message the user will read. Text outside this tool is visible in the detail view, but most won't open it — the answer lives here."` The companion "Talking to the user" guide has similarly been streamlined to focus on the key pattern: replies go through `SendUserMessage`; text outside it should be assumed unread.

Evidence: Rewritten prompt (search for `"Send a message the user will read"`, `"## Talking to the user"`)


### Improved Team Memory Sync (Delta Pushes)

Team memory synchronization now supports hash-based conflict resolution with `entryChecksums`. Instead of pulling and re-pushing the entire memory file on conflict, the system probes the server for per-entry hashes (`?view=hashes`), enabling delta-based pushes. This reduces bandwidth and merge conflicts for organizations with large shared memory files.

Evidence: Hash-based sync (search for `"entryChecksums"`, `"Conflict resolution hashes probe"`, `"team-memory-sync: server response missing entryChecksums"`)


### Terminal Identification via XTVERSION

Claude Code now queries the terminal emulator for its identity using the XTVERSION escape sequence. This can be used to tailor behavior to specific terminals. If the terminal ignores the query, it logs `"XTVERSION: no reply"`.

Evidence: Terminal identification (search for `"XTVERSION"`)


### Plan Mode Verbosity Control

Plan mode now supports multiple verbosity levels for Phase 4 (Final Plan) output, controlled by the `tengu_pewter_ledger` feature flag. Options include `"trim"` (concise), `"cut"` (minimal, no context section), and `"cap"` (hard 40-line limit, no prose). The default behavior is unchanged.

Evidence: Plan mode variants (search for `"tengu_pewter_ledger"`, `"Hard limit: 40 lines"`)


### Output Token Tracking Per Turn

A new metadata display now shows output token usage per turn and per session: `"Output tokens — turn: X · session: Y"`. This gives users better visibility into how many tokens each response consumes.

Evidence: Token tracking (search for `"Output tokens — turn"`)

## Bug Fixes

- Orphaned bash tasks from exiting agents are now killed automatically, preventing zombie processes from accumulating (search for `"killBashTasksForAgent: killing orphaned bash task"`)
- Voice mode now handles early pre-transcript errors gracefully by retrying once, and ignores stale `onError` callbacks from previous sessions (search for `"early voice_stream error (pre-transcript), retrying once"`, `"ignoring onError from stale session"`)
- OAuth token expiration during bridge/REPL sessions now shows a clear message directing users to run `/login` (search for `"OAuth token expired and could not be refreshed. Run /login to re-authenticate."`)
- Bridge REPL initialization now tracks consecutive failures and stops retrying after a threshold, preventing infinite retry loops (search for `"consecutive init failures, not retrying this session"`)
- Hook success content changed from `"Success"` / `"Condition met"` to empty string, reducing noise in hook output
- SSL certificate errors now provide actionable guidance: set `NODE_EXTRA_CA_CERTS` or ask IT to allowlist `*.anthropic.com` (search for `"SSL certificate error"`)
- Cron job deletion errors now provide clear messages: `"Cannot delete cron job '...'"` (search for `"Cannot delete cron job"`)
- Orphaned cron jobs (for agents that no longer exist) are now automatically cleaned up (search for `"gone, removing orphaned cron"`)
- Durable cron jobs are now explicitly blocked for teammate sessions with a clear error message (search for `"durable crons are not supported for teammates"`)
- Environment variables related to `ANTHROPIC_UNIX_SOCKET` connections are now stripped when applying config-level env overrides, preventing socket connection leaks across configurations (search for `"ANTHROPIC_UNIX_SOCKET"` in `Rr6()`)
- Text selection in the terminal now uses word-boundary-aware double-click selection with proper anchor span tracking (search for `"anchorSpan"` with `kind: "word"`)

### SSH Remote Sessions

What: Infrastructure for managing SSH-based remote sessions, enabling Claude Code to connect to and manage remote machines.

Status: Feature-flagged / Infrastructure

Details:
- Full SSH session lifecycle management with connect, disconnect, reconnect, and cleanup hooks
- Automatic reconnection on SSH connection drops with configurable retry attempts
- Permission request handling for SSH sessions
- Remote stderr capture and exit code reporting
- Log messages: `"[useSSHSession] connected"`, `"[useSSHSession] ssh dropped, reconnecting"`, `"[useSSHSession] ssh process exited (giving up)"`
- Related: `"Remote session ended."`, `"Remote stderr (exit ...)"`, `"SSH session failed before connecting."`

Evidence: SSH session manager (search for `"[useSSHSession]"`, `"SSH connection dropped"`, `"SSH session failed before connecting"`)
