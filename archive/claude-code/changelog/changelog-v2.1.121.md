# Changelog for version 2.1.121

## Summary

This release introduces in-app extra usage management (buy credits, set spend limits, configure auto-reload without leaving the CLI), a new `claude plugin prune` command for cleaning up orphaned plugins, searchable skills dialog, iTerm2 clipboard integration, per-request cost attribution by agent/skill/plugin, and a new `updatedToolOutput` hook property for modifying tool output before it reaches the model. The daemon also gains significant improvements including pre-warmed spare workers, yield/takeover protocol, and a `--keep-workers` stop flag.


### In-App Extra Usage Management

What: Users can now enable extra usage, buy credits, set monthly spend limits, and configure auto-reload directly from within the CLI — no need to visit claude.ai.

Usage:
```
# When you hit a usage limit, the CLI now offers interactive options:
# - "Continue with extra usage"
# - "Buy extra usage"
# - "Adjust monthly limit"
# - "Set to unlimited"
# - "Auto-reload" (on/off)
# - "Manage on claude.ai"
```

Details:
- Full payment flow integrated in-terminal, including 3DS verification support
- Set monthly spend limits with real-time enforcement
- Auto-reload automatically buys more credits when balance falls below a configurable threshold
- Shows balance and auto-reload status inline
- Tax calculation and discount display supported
- Links to Anthropic Help Center for extra usage terms
- Not available in essential-traffic-only mode

Evidence: Extra usage billing flow (search for `"Buy extra usage"`, `"auto-reload"`, `"/setup_overage_billing"`)


### Plugin Prune Command

What: New `claude plugin prune` subcommand removes auto-installed plugin dependencies that are no longer needed by any active plugin.

Usage:
```bash
# List orphaned plugins without removing them
claude plugin prune --dry-run

# Remove orphans at user scope
claude plugin prune

# Remove at project scope
claude plugin prune --scope project

# Skip confirmation prompt (for CI)
claude plugin prune -y

# Also prune during uninstall
claude plugin uninstall my-plugin --prune
```

Details:
- Detects auto-installed dependencies that no longer have a parent plugin requiring them
- Supports scopes: user, project, or local
- Dry-run mode shows what would be removed without acting
- Non-TTY environments require `-y` flag
- Reports which plugins were removed and their count
- Integrates with `plugin uninstall --prune` for cleanup during uninstall
- Telemetry event `tengu_plugin_prune_cli` tracks usage

Evidence: Plugin prune handler (search for `"plugin prune"`, `"Nothing to prune"`, `"no longer needed"`)


### Skills Search Dialog

What: The `/skills` dialog now includes a real-time search/filter input, making it easy to find skills by name in large skill sets.

Usage:
```
/skills
# Then press / to start searching
# Type to filter skills by name
# ↓/Enter to select, Esc to clear search
```

Details:
- Press `/` to activate search mode within the skills picker
- Shows filtered count (e.g., "3/12 skills") when search is active
- Keyboard hints update contextually: "type to filter · ↓/enter to select · esc to clear"
- Reports "No skills match \"{query}\"" when filter returns empty

Evidence: Skills search UI (search for `"Search skills"`, `"No skills match"`, `"type to filter"`)


### iTerm2 Clipboard Integration

What: Claude Code now automatically enables the "Applications in terminal may access clipboard" setting in iTerm2, making the `/copy` command work without manual configuration.

Usage:
```bash
# Run /terminal-setup in iTerm2 — it now specifically enables clipboard access
/terminal-setup

# Or just use /copy — Claude will prompt to enable clipboard access if needed
```

Details:
- Detects iTerm2 terminal via `TERM_PROGRAM` or `LC_TERMINAL` environment variables
- Writes `AllowClipboardAccess` preference via `defaults write` on macOS
- Reports success and reminds user to restart iTerm2
- When connected from iTerm2 via SSH, shows guidance about reaching local clipboard
- Shift+Enter is noted as natively supported in iTerm2 (no configuration needed)
- `/terminal-setup` description dynamically changes to "Enable iTerm2 clipboard access for /copy" in iTerm2

Evidence: iTerm2 clipboard enablement (search for `"AllowClipboardAccess"`, `"iTerm2 clipboard access already enabled"`)


### Cost Attribution by Agent, Skill, and Plugin

What: The usage/cost display now breaks down spending by agent, skill, and plugin, showing what percentage of usage each component consumed.

Details:
- API responses now carry `attributionAgent`, `attributionSkill`, and `attributionPlugin` fields
- Costs are accumulated per-request into `byAgent`, `bySkill`, and `byPlugin` maps
- The cost view renders a "Skills, subagents, and plugins" section with percentage breakdown
- Actionable tips appear alongside high-cost items:
  - Skills: "Heavy skills can be scoped down or run with a cheaper model via skill frontmatter."
  - Plugins: "Review what this plugin contributes — its agents, skills, and MCP tools all count toward your limit."
- Shows "No attribution data yet · accumulates as you use Claude" when no data exists

Evidence: Attribution tracking (search for `"attributionAgent"`, `"attributionPlugin"`, `"Skills, subagents, and plugins"`)


### `updatedToolOutput` Hook Property

What: PostToolUse hooks can now replace tool output for ALL tools (not just MCP tools) via the new `updatedToolOutput` field.

Details:
- Previously, only `updatedMCPToolOutput` was available, which only worked for MCP tools
- The new `updatedToolOutput` field works for any tool (Bash, Read, Write, Edit, MCP, etc.)
- The old `updatedMCPToolOutput` is retained but its description now says "Prefer updatedToolOutput, which works for all tools"
- Validation error if hook output doesn't match expected tool output shape: "PostToolUse hook returned updatedToolOutput that does not match {tool}'s output shape"

Evidence: Hook output replacement (search for `"updatedToolOutput"`, `"Replaces the tool output before it is sent to the model"`)


### MCP Server `alwaysLoad` Option

What: New boolean configuration option for MCP servers that forces all tools from a server to always be included in the prompt, bypassing tool search deferral.

Details:
- Added to all MCP server config types: stdio, HTTP, and SSE
- When `true`, tools are never deferred behind tool search
- Equivalent to setting `defer_loading: false` on the API
- Default behavior: tools are deferred when tool search is enabled

Evidence: MCP alwaysLoad option (search for `"When true, all tools from this server are always included"`)


### Disable Background Agents Fleet Setting

What: New `disableAgentsFleet` setting and `CLAUDE_CODE_DISABLE_AGENTS_FLEET` environment variable to fully disable the background-agents fleet.

Details:
- Disables `claude agents`, `--bg`, `/background`, and the on-demand daemon
- Typically set in managed settings for enterprise environments
- Can be set via environment variable: `CLAUDE_CODE_DISABLE_AGENTS_FLEET=1`

Evidence: Fleet disable option (search for `"Disable the background-agents fleet"`, `"CLAUDE_CODE_DISABLE_AGENTS_FLEET"`)


### Shell CWD Recovery

What: When the shell's current working directory is deleted (e.g., by a branch switch or cleanup), Claude Code now recovers gracefully and informs the user.

Details:
- Detects when cwd is removed and recovers to a valid directory
- Shows message: "{path} was deleted; shell cwd recovered to {new path}"
- Advises re-issuing the command from the recovered directory

Evidence: CWD recovery handler (search for `"was deleted; shell cwd recovered"`)


### File Read `encoding` Parameter

What: The Read tool now accepts an `encoding` parameter, allowing base64 encoding for binary file reads (e.g., images).

Details:
- Description: "How to encode the bytes in `contents`. Defaults to utf-8 (lossy for binary); pass 'base64' to read images."
- Response includes `encoding` field: "Set when the request asked for base64. Absent means utf-8 — including when an older CLI ignored the request's encoding field."

Evidence: Read encoding support (search for `"How to encode the bytes"`)


### Daemon Pre-Warmed Spare Workers

Background agents now use a pre-warmed "spare" worker mechanism (`--bg-spare`) for faster session startup. When a new background session is requested, the daemon can claim a pre-spawned spare worker instead of cold-starting a new process.

Evidence: Spare worker system (search for `"bg claimed-spare"`, `"[bg-spare] missing claim sock path"`)


### Daemon Yield/Takeover Protocol

Transient daemons can now be gracefully displaced by foreground or persistent service daemons. The new daemon asks the existing transient daemon to yield, and background workers are re-adopted without interruption. Messages include "yielding to a foreground/service daemon — bg workers will be re-adopted".

Evidence: Daemon yield protocol (search for `"yielding to a foreground/service daemon"`)


### Daemon `--keep-workers` Flag

`claude daemon stop` now accepts `--keep-workers` to leave detached background sessions running when stopping the daemon supervisor. Useful for cleanly upgrading the daemon without interrupting active background work.

Evidence: Keep-workers flag (search for `"--keep-workers"`)


### Daemon Install Prompt Default Changed

The daemon install prompt changed from `[Y/n/never, or 'once' for this login session]` to `[y/N/never, or 'once' just for now]`. The default answer is now **no** (lowercase `y` vs uppercase `Y`), making it less aggressive about installing as a persistent service.

Evidence: Install prompt comparison (search for `"Install as a service now?"`)


### Daemon Peer UID Security

The daemon now validates the UID of connecting peers on the control socket. Connections from different users are rejected with "[daemon] rejecting control connection: peer uid {uid}".

Evidence: Peer UID validation (search for `"[daemon] rejecting control connection: peer uid"`)


### Daemon Log Rotation

The daemon log now supports rotation (creating `daemon.log.1` when the primary log reaches a size limit) to prevent unbounded log growth.

Evidence: Log rotation (search for `"daemon.log.1"`)


### `claude stop` Replaces `claude kill`

The command to stop background sessions has been renamed from `claude kill` to `claude stop` for clarity. The old `claude kill` syntax now shows a deprecation message suggesting `claude daemon` instead.

Evidence: Command rename (search for `"claude stop"`, `"' is no longer supported — use: claude daemon"`)


### `claude daemon assistant add` Subcommand

The daemon assistant management command changed from `claude daemon assistant -a` (flag-based) to `claude daemon assistant add <name-or-dir>` (subcommand-based). Similarly, `claude daemon assistant remove` and `claude daemon remote-control remove` use explicit subcommands.

Evidence: Subcommand style (search for `"claude daemon assistant add"`, `"usage: claude daemon assistant remove"`)


### Focus View Requires Fullscreen Renderer

The `/focus` command now requires the fullscreen renderer (TUI mode) and provides clear guidance on how to enable it. If `viewMode` is set to `"focus"` in settings.json, the command warns that it must be removed there before toggling. The `viewMode` setting now validates against an enum: `["default", "verbose", "focus"]`.

Evidence: Focus view requirements (search for `"Focus view needs the fullscreen renderer"`)


### Autocompact Status Display

The autocompact feature now shows its configuration state more clearly in the token counter with the format `{tokens} tokens) · /autocompact to configure` and logs "Compacting at auto window ({N} tokens)" when triggering.

Evidence: Autocompact display (search for `"/autocompact to configure"`, `"Compacting at auto window"`)


### Improved `-p` (Print) Flag Description

The `-p` flag description now correctly explains non-interactive mode: "The workspace trust dialog is skipped when Claude is run in non-interactive mode (via -p, or when stdout is not a TTY, e.g. piped or redirected output)" — previously it only mentioned "directories you trust".

Evidence: Print mode description (search for `"non-interactive mode (via -p, or when stdout is not a TTY"`)


### Remote Session Permission Mode Message

Remote sessions now explicitly show "No other permission modes are available in this remote session" when users attempt to change permission modes, making the limitation clear.

Evidence: Permission restriction (search for `"No other permission modes are available"`)


### Model Picker Guidance in Remote Sessions

The model picker message in remote sessions improved from "use /model <name> instead" to "pass a model name, e.g. /model sonnet" — providing a concrete example.

Evidence: Model picker message (search for `"Model picker shows local options in remote sessions"`)


### MCP OAuth Flow Improvements

The MCP authentication flow now supports custom `redirectUri` parameters and provides better error messages for invalid callback URLs: "Invalid callback URL — no authorization code. The flow is still open; retry with the full redirect URL."

Evidence: OAuth improvements (search for `"Invalid callback URL"`, `"No OAuth flow in progress"`)


### Background Session UI Improvements

- "Session can't redraw right now — Ctrl+B then d to detach" shown when a background session is busy
- "Session is starting — it will appear once ready. Ctrl+B then d to detach" for sessions that haven't initialized yet
- "Session keeps running. Use /stop to end it." replaces previous messaging
- `ctrl+x again to delete` confirmation before deletion
- Exit description dynamically changes: "Detach from this background session (it keeps running)" in background mode vs "Exit the CLI" normally

Evidence: Background session messages (search for `"Session can't redraw right now"`, `"ctrl+x again to delete"`)


### Symlink Safety Improvements

- Settings files that are symlinks are now detected and skipped: "Skipping symlinked settings.local.json"
- Worktree include files that are symlinks are warned: "Skipping symlink in .worktreeinclude"
- Speculation/overlay file copies check for parent directory symlink escapes: "[Speculation] Skipping {path}: parent dir escapes cwd via symlink"

Evidence: Symlink safety (search for `"Skipping symlinked settings.local.json"`, `"parent dir escapes cwd via symlink"`)


### Logind Kill Warning for SSH Users

On Linux systems with `KillUserProcesses=yes` in logind.conf, Claude now warns SSH users that disconnecting will kill the transient daemon and background jobs, suggesting `loginctl enable-linger` or `claude daemon install` as alternatives.

Evidence: Logind warning (search for `"logind KillUserProcesses=yes"`)


### Google Auth Library Upgrade

The bundled `gaxios` library upgraded from 6.7.1 to 7.1.4, and `google-auth-library` was updated with:
- New `CertificateSubjectTokenSupplier` for mTLS workload identity federation
- New `ExternalAccountAuthorizedUserClient` credential type
- Certificate-based identity pool credential source (alongside existing file/url types)
- `GOOGLE_API_CERTIFICATE_CONFIG` environment variable for certificate discovery
- Improved error messages for certificate parsing failures

Evidence: Gaxios upgrade (search for `"gaxios"`, version `"7.1.4"`, `"certificate_config.json"`)


### Container Restart Task Recovery

When a container restarts, Claude now injects a system reminder listing previously-running background tasks that were stopped, with "Re-create them if still needed" guidance.

Evidence: Container restart recovery (search for `"The container was restarted"`, `"Re-create them if still needed"`)


### Thinking Type Override Retry

When a model rejects a thinking type, Claude now logs the rejection and can retry with a different configuration: "[thinking] model rejected thinking.type={type}".

Evidence: Thinking type retry (search for `"retry:thinking-type"`, `"[thinking] model rejected thinking.type="`)


## Bug Fixes

- Fixed path traversal detection for file operations — now correctly handles symlink-based escapes: "{path}: parent dir escapes cwd via symlink" replaces the simpler "path traversal detected" (search for `"parent dir escapes cwd via symlink"`)
- Fixed daemon refusing to stop when a previous worker hadn't acknowledged: "Couldn't stop the previous worker — supervisor may be starting, retry in a moment" (search for `"Couldn't stop the previous worker"`)
- Fixed stale roster entries after daemon restart: "orphaned background task(s) after restart" cleanup (search for `"orphaned background task(s) after restart"`)
- Fixed MCP connection manager readiness check: "MCP connection manager not ready — try again in a moment" instead of crashing (search for `"MCP connection manager not ready"`)
- Fixed daemon version mismatch detection: "and CLI versions differ; restart claude" message for stale daemon connections (search for `"and CLI versions differ"`)
- Fixed `claude daemon` display-name collisions: "[claudeai-mcp] Display-name collision on distinct upstreams" now logged as a warning rather than failing silently (search for `"Display-name collision on distinct upstreams"`)


## Notes

- The `claude kill` command is deprecated. Use `claude stop` or `claude stop <id>` instead.
- The daemon install prompt now defaults to **no** — users must explicitly confirm with `y` to install as a persistent service.
- `claude daemon assistant -a` is no longer available; use `claude daemon assistant add` subcommand syntax.
- `updatedMCPToolOutput` in PostToolUse hooks is deprecated in favor of the new `updatedToolOutput` which works for all tool types.
