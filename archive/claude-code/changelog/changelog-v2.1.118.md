# Changelog for version 2.1.118

## Summary

This release introduces the `/autofix-pr` command for automated PR monitoring and fixing, adds the `/plugin tag` command for plugin release management, replaces the standalone Config tool with integrated settings UI, and brings significant infrastructure improvements including a new `PostToolBatch` hook event, WSL managed settings inheritance, custom theme creation, MCP tool hooks, and a new SSE-based sessions transport (`SessionsV2Client`). The `/cost` and `/stats` commands are now aliases for an expanded `/usage` command.


### /autofix-pr Command

What: A new slash command that monitors a PR for CI failures and review comments, then automatically investigates and pushes fixes.

Usage:
```
/autofix-pr
/autofix-pr stop
```

Details:
- Can spawn either a background in-process agent or a remote autofix session (CCR)
- Monitors the current PR continuously for CI failures or review comments
- Automatically investigates issues and pushes fixes to the PR branch
- Tracks monitoring state, preventing duplicate monitors with "Already monitoring" detection
- Use `/autofix-pr stop` to stop monitoring
- The remote variant shows `"Spawning remote autofix session…"` instead of the previous generic `"Spawning remote Claude Code session…"`

Evidence: Slash command definition (search for `"autofix-pr"`) with description `"Monitor and autofix any issues with the current PR"`. Background agent spawned via `lG1` at line ~473108.


### /plugin tag Command

What: A new slash command and CLI subcommand to create versioned git tags for plugin releases, with validation against plugin.json and marketplace entries.

Usage:
```bash
/plugin tag [path] [--push] [--dry-run] [-f|--force]
claude plugin tag [path] [--push] [--dry-run] [-f|--force] [-m <msg>] [--remote <name>]
```

Details:
- Validates plugin.json and any enclosing marketplace manifest agree on name and version
- Checks for uncommitted changes, existing tags, valid semver, and valid git ref names
- Creates annotated git tags in the format `{name}--v{version}`
- `--push` pushes the tag to the remote after creation
- `--dry-run` previews what would be tagged without creating it
- `--force` skips dirty-working-tree and tag-already-exists checks
- CLI variant adds `--message <msg>` for custom tag annotation and `--remote <name>` for push target
- Detailed error messages for version mismatches, missing manifests, and invalid configs

Evidence: Slash command help text (search for `"Create a {name}--v{version} git tag"`) and CLI subcommand `.command("tag [path]")` at line ~652882.


### PostToolBatch Hook Event

What: A new hook event type that fires once after every tool call in a batch has resolved, before the next model request.

Details:
- Unlike `PostToolUse` which fires per-tool and may run concurrently for parallel tool calls, `PostToolBatch` fires exactly once with the full batch
- Hook input includes `tool_calls` array with `{tool_name, tool_input, tool_use_id, tool_response}` for each call
- Supports `additionalContext` return to inject content into the next model request
- Can return `"stopAgent": true` to halt execution, showing `"Execution stopped by PostToolBatch hook"`
- Available in hooks configuration under the event name `"PostToolBatch"`

Evidence: Schema definition (search for `"PostToolBatch"`) at line ~263664. Hook input schema describes `"Fired once after every tool call in a batch has resolved, before the next model request"`.


### MCP Tool Hooks (mcp_tool)

What: A new hook type that invokes an MCP server tool as the hook action, as an alternative to bash/command hooks.

Details:
- Configure with `type: "mcp_tool"` in hook definitions
- Specify `server` (name of an already-configured MCP server) and `tool` (tool name on that server)
- Supports `arguments` object with `${path}` interpolation from hook input JSON
- Optional `timeout` field for per-call timeout in seconds
- Reads `X-Mcp-Error-Code` header from 401 responses for better error diagnostics
- Not available for all hook events — logs `"mcp_tool hooks are not available for the '<event>' hook event"` when unsupported

Evidence: Hook type definition (search for `"mcp_tool"`) and MCP tool schema fields (search for `"Name of an already-configured MCP server to invoke"`).


### WSL Managed Settings Inheritance

What: WSL (Windows Subsystem for Linux) instances can now inherit managed settings from the Windows host's policy chain.

Details:
- A new `wslInheritsWindowsSettings` boolean setting controls this behavior
- When set to `true` in a Windows admin-only source (HKLM registry or `C:/Program Files/ClaudeCode/managed-settings.json`), WSL reads managed settings from the full Windows policy chain
- Windows sources take priority over Linux-native `/etc/claude-code` settings
- Double opt-in required: admin enables the chain via HKLM/HKCU, user confirms via their own HKCU entry
- Uses `reg.exe` queries via `/mnt/c/Windows/System32/reg.exe` for cross-environment access
- Drop-in settings from `C:/Program Files/ClaudeCode/managed-settings.d/` are also supported

Evidence: Schema description (search for `"wslInheritsWindowsSettings"`) and WSL detection function `pnH()` at line ~50906.


### Custom Theme Creation and Management

What: Users can now create, edit, and manage custom color themes with fine-grained color token overrides.

Details:
- Custom themes are stored as JSON files in the user's themes directory (`~/.claude/themes/`)
- Each theme specifies a `name`, `base` theme (`dark` or `light`), and color `overrides`
- Color overrides accept `rgb(r,g,b)`, `#rrggbb`, `ansi256(n)`, or `ansi:name` formats
- Custom themes appear in the `/theme` picker with a `(custom)` label
- A `"New custom theme…"` option is available in the theme selector to create themes interactively
- File watcher auto-reloads themes when JSON files are added, changed, or removed
- Themes from plugins are also supported via a `themes` field in plugin.json or a `themes/` directory
- Plugin settings schema adds `themesDirectories` for specifying additional theme paths

Evidence: Theme creation flow (search for `"__new_custom_theme__"`) and color validation (search for `"Accepts rgb(r,g,b)"` and `"rgb(r,g,b) · #rrggbb · ansi:red"`).


### --managed-settings CLI Flag

What: A new CLI flag that accepts a JSON object of policy-tier settings from a spawning parent process (SDK use only).

Usage:
```bash
claude --managed-settings '{"key": "value"}'
```

Details:
- Only honored when spawned by an SDK parent process
- Ignored with a warning when passed outside SDK context: `"--managed-settings ignored: only honored when spawned by an SDK parent"`
- Invalid JSON produces: `"--managed-settings ignored: invalid JSON object"`
- Parsed settings are applied as `"Enterprise managed settings (parent process)"`

Evidence: CLI flag definition (search for `"--managed-settings"`) and validation messages (search for `"--managed-settings ignored"`).


### --plan-mode-instructions CLI Flag

What: A new CLI flag that lets users customize the plan-mode workflow instructions.

Usage:
```bash
claude --print --plan-mode-instructions "Custom workflow instructions here"
```

Details:
- Replaces the default code-implementation phases in the plan-mode system reminder
- The read-only enforcement preamble and ExitPlanMode protocol footer are always kept
- Can only be used with `--print` mode; using it otherwise produces: `"Error: --plan-mode-instructions can only be used with --print mode."`
- Also exposed as an agent frontmatter field `planModeInstructions` for programmatic configuration

Evidence: CLI option definition (search for `"--plan-mode-instructions"`) and enforcement (search for `"can only be used with --print mode"`).


### Auto Mode Classifier $defaults Inheritance

What: Agent definitions can now use the literal string `"$defaults"` in auto mode classifier sections to inherit built-in rules at a specific position.

Details:
- Works in `allow`, `deny` (soft_deny), and `environment` sections of the auto mode classifier
- When `$defaults` is present, the built-in rules are inserted at that position in the list
- Custom rules can appear before or after `$defaults`, enabling augmentation rather than replacement
- The UI now distinguishes between modes: `"Defaults also in effect:"` (custom rules added alongside) vs `"Defaults being replaced:"` (custom rules replacing defaults)

Evidence: Variable definition `do$ = "$defaults"` and schema descriptions (search for `"Include the literal string \"$defaults\" to inherit the built-in rules at that position"`).


### Session Color Tags on Bridge Sessions

What: The `/color` command now syncs color choices to the bridge session via API tags, enabling consistent color display across clients.

Details:
- When a bridge session ID is available, `/color` calls `updateBridgeSessionColorTag` to set a `color:` tag on the server-side session
- Resetting to default removes all color tags
- Uses the new `QD6` function to manage `color:` prefixed tags via the sessions API

Evidence: Color tag update function `QZ1` at line ~476042 (search for `"color:"`) and tag prefix constant `UD6 = "color:"`.


### Unified /usage Command (replaces /cost)

The standalone `/cost` command has been removed and consolidated into `/usage`. The `/usage` command now has `"cost"` and `"stats"` as aliases, so typing `/cost` or `/stats` still works. The description changed from `"Show plan usage limits"` to `"Show session cost, plan usage, and activity stats"`. For thin-client (remote) sessions, `/usage` now fetches the remote container's cost via a `get_session_cost` control request instead of displaying `$0.00`.

Evidence: Command definition with aliases (search for `"Show session cost, plan usage, and activity stats"`) and remote cost fetching (search for `"Loading remote cost"`).


### Config Tool Removed in Favor of Settings UI

The standalone `Config` tool (which allowed the model to get/set settings via tool use) has been completely removed. All its functionality — theme, model, permissions, voice, memory, and other settings — is now managed through the `/config` slash command and settings UI. This simplifies the tool surface and prevents the model from changing settings without explicit user intent.

Evidence: Removal of `var Fw7 = "Config"` tool definition and all associated functions (`sw7`, `tw7`, `ms$`, `ew7`, `$j7`, `Kj7`, `_j7`, `Aj7`, `Wj7`, `Gj7`, `Zj7`) from v2.1.117.


### Broadcast Messaging Deprecated

The `to: "*"` broadcast mode for `SendMessage` in agent teams has been deprecated. The new behavior produces: `"broadcast (to: \"*\") is no longer supported — send a message per recipient"`. The team system prompt no longer mentions broadcast capability, directing agents to send individual messages instead.

Evidence: Deprecation message (search for `"broadcast (to: \"*\") is no longer supported"`).


### Improved Recap Messages

The recap command now provides more specific error messages based on the failure reason:
- No turns yet: `"Nothing to recap yet — send a message first."` (previously: generic "No recap available")
- Generation failed: `"Couldn't generate a recap. Run with --debug for details."`
- Cancelled: `"Recap cancelled."`

Evidence: New recap messages (search for `"Nothing to recap yet"` and `"Couldn't generate a recap"`).


### MCP Server Authentication Improvements

When an MCP server returns 401, the error message now offers an `"Authenticate"` option for OAuth-capable servers: `"requires authentication. Use 'Authenticate' if the upstream server uses OAuth, or check the headersHelper script and use 'Reconnect'."` The previous version only suggested checking the headersHelper script.

Evidence: Updated authentication message (search for `"Use 'Authenticate' if the upstream server uses OAuth"`).


### Speculation Generalized from Bash to Shell

The speculative execution boundary detection has been generalized from `"Speculation paused: bash boundary"` to `"Speculation paused: shell boundary"`, reflecting broader shell support including PowerShell.

Evidence: New string `"Speculation paused: shell boundary"` replaces `"Speculation paused: bash boundary"`.


### PowerShell Remove-Item Support in Memory Mode

The memory agent's restricted shell commands now understand PowerShell `Remove-Item` (and aliases `ri`, `del`, `erase`, `rd`, `rm`, `rmdir`) for `.md` file deletion, not just Unix `rm`. This aligns with the cross-platform shell support.

Evidence: PowerShell command parser `Z31` at line ~433184 (search for `"Remove-Item"` / `"PowerShell Remove-Item"`).


### Admin-Controlled Update Blocking

Administrators can now disable auto-updates via managed settings. When disabled, users see: `"Updates are disabled by your administrator. Contact your IT team to get the latest version."` This supports enterprise environments with controlled rollout.

Evidence: Admin update blocking message (search for `"Updates are disabled by your administrator"`).


### Plugin Autoupdate "Blocked by Pinner" Notifications

When a plugin can't auto-update because another plugin pins it to a specific version, users now receive a clear notification explaining the hold: `"Autoupdate held"`. The notification identifies which plugin is blocking the update and whether those pinning plugins are disabled.

Evidence: Autoupdate blocked notification type (search for `"autoupdate-blocked-by-pinner"` and `"Autoupdate held"`).


### Push Notification Tips

New tips encourage users to enable push notifications:
- `"Get pinged on your phone when long tasks finish · enable push notifications in /config"`
- After session completion: `"get pinged when Claude finishes · enable push notifications in"`

Evidence: Tip definition (search for `"push-notif"` or `"Get pinged on your phone"`).


### Frontmatter Schema Validation Telemetry

New telemetry tracks when plugin/skill frontmatter contains unknown keys or type mismatches against the expected schema. This helps identify misconfigured plugins without breaking them.

Evidence: Validation function `pwH` at line ~205424 (search for `"tengu_frontmatter_shadow_unknown_key"`).


### Anthropic Client Platform Header

API requests now include an `anthropic-client-platform` header that identifies the entrypoint context (VSCode, remote, SDK, MCP, GitHub Action, local agent, Slack, or CLI). This enables better server-side analytics.

Evidence: Header function `YDH()` at line ~147245 (search for `"anthropic-client-platform"`).


### Fork Context Reference Tracking

When forking sessions, the system now tracks a `fork-context-ref` linking the child to the parent context. This improves session lineage tracking for forked conversations.

Evidence: Fork context reference (search for `"fork-context-ref"` and `"Failed to record fork-context-ref"`).


### Stall Detection and Diagnostics

A comprehensive stall detection system has been added that logs timing information for:
- Stream idle partials: `[Stall] stream_idle_partial lastChunkAgeMs=...`
- Classifier requests: start, progress, and finish with timing and outcome
- Tool dispatch: start, end, and post-error with tool name and permission decision timing
- Agent completion events

This helps diagnose performance bottlenecks and stuck sessions.

Evidence: Stall detection logs (search for `"[Stall]"`), with fields like `promptTokensEst=` and `permissionDecisionMs=`.


### Improved Edit Tool Unicode Handling

The Edit tool now attempts to match `\uXXXX` escape sequences and their literal Unicode character equivalents. If neither form matches, it provides a more helpful error message: `"Edit also tried swapping \uXXXX escapes and their characters; neither form matched, so the mismatch is likely elsewhere in old_string."`.

Evidence: Unicode swap functions `$e8` and `qe8` at line ~260927, and error hint (search for `"swapping \\uXXXX escapes"`).


### Fullscreen Renderer Memory Optimization

The fullscreen renderer's pool reset logic has been optimized. Instead of resetting all pools every 5 minutes unconditionally, it now only resets the hyperlink pool when its size exceeds a threshold. The character pool is no longer reset, reducing memory churn.

Evidence: Structural change in class `VH$` — conditional `this.hyperlinkPool.size > i4K` check before pool reset.


### Byte Watchdog with Stall Detection Tiers

The streaming byte watchdog now includes tiered stall detection with escalating timeouts (15s, 30s, 60s, 120s) before the final hard watchdog fires. Each tier logs `[Stall] stream_idle_partial` with byte count and timing, providing earlier visibility into stalled streams.

Evidence: Stall tier array `f = [15000, 30000, 60000, 120000]` in function `Md_` at line ~145358.


### User OAuth and Ant Auth Profile Support

The credentials system now recognizes `user_oauth` authentication type alongside `oidc_federation`, enabling new identity provider flows. The status display distinguishes between profile types (explicit vs. implicit) and shows the authentication type. A new logout hint tells users: `"Run \`ant auth logout\`, or remove the active profile under ~/.config/anthropic/configs/."`.

Evidence: Authentication type detection in `$y8` at line ~101631 (search for `"user_oauth"`) and logout hint (search for `"ant auth logout"`).


### Cache Diagnosis Beta Header Handling

Improved handling of the cache diagnosis beta feature. If the server rejects the beta header, it's now detected and dropped gracefully: `"[cache-diagnosis] server rejected beta — dropping header latch"`. A retry mechanism (`"retry:cache-diagnosis-beta"`) handles transient failures.

Evidence: Cache diagnosis handling (search for `"cache-diagnosis"` and `"retry:cache-diagnosis-beta"`).


### Atomic File Writes

A new `rcq` function implements atomic file writes using temp-file-then-rename, with fallback to copy+unlink for cross-device scenarios (`EXDEV`, `EPERM`, `EEXIST`). This prevents data corruption from interrupted writes.

Evidence: Atomic write function at line ~145955 (search for `".tmp."` in the write context).


## Bug Fixes

- Fixed potential data loss when writing files across filesystem boundaries — atomic writes now handle `EXDEV` and `EPERM` errors gracefully (search for `"EXDEV"`)
- Fixed session reattachment cleanup — `CLAUDE_BRIDGE_REATTACH_SESSION` and `CLAUDE_BRIDGE_REATTACH_SEQ` environment variables are now properly cleared on TUI restart to prevent stale reattachment (search for `"CLAUDE_BRIDGE_REATTACH_SESSION"`)
- Improved credentials lock handling with proper retry logic and error reporting: `"Could not acquire credentials lock at ... after N retries"` (search for `"credentials lock"`)
- Fixed potential memory leak in fullscreen renderer where character pools were unnecessarily reset every 5 minutes


### Pro Trial Expired Options [In Development]

What: A new slash command `pro-trial-expired` for handling expired Pro plan Claude Code trials.

Status: Stubbed — `isEnabled` returns `!1` (false) and `isHidden` is `!0` (true).

Details:
- Described as `"Options shown when the Pro plan Claude Code trial has ended"`
- Includes a user-facing message `"Your Claude Code trial has ended."` and `"Upgrade to Max"` option
- The `"No, don't ask again"` dismiss option with value `"decline-dont-ask"` is also wired up
- Infrastructure is complete but the command is hidden and disabled

Evidence: Command definition (search for `"pro-trial-expired"`) with `isEnabled: () => { return !1; }` and `isHidden: !0`.


### Sessions V2 Client (SSE Transport) [In Development]

What: A complete replacement for the WebSocket-based `SessionsWebSocket` client, using Server-Sent Events (SSE) over HTTP.

Status: Infrastructure added. The new `SessionsV2Client` coexists with the old WebSocket client.

Details:
- Uses `/events/stream` SSE endpoint for receiving events (replacing WebSocket)
- Uses `POST /events` for sending events (replacing WebSocket send)
- Includes reconnection budget tracking with backoff
- Supports `from_sequence_num` for event replay on reconnect
- Liveness timeout detection with automatic reconnection
- Force reconnect capability
- Full control request/response protocol over HTTP

Evidence: New client class (search for `"SessionsV2Client"`) with log prefixes like `"[SessionsV2Client] Connecting to"`, `"[SessionsV2Client] Connected"`, etc.


## Notes

- The `/cost` command still works — it is now an alias for `/usage`, which provides expanded session cost, plan usage, and activity stats
- The Config tool removal means the model can no longer change settings autonomously; all settings changes now go through the interactive `/config` UI
- WSL managed settings inheritance requires explicit opt-in from both the Windows admin (via HKLM or Program Files config) and the user (via HKCU) — it is not enabled by default
- Custom themes require the user themes directory (`~/.claude/themes/`); themes are auto-detected and hot-reloaded on file changes
