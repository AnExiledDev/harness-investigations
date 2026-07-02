# Changelog for version 2.1.198

## Summary

This release raises the Node.js minimum from 18 to 22, removes the speculation engine and the `/agents` TUI wizard, and ships `/plan share` for publishing plans as shareable artifacts. MCP server configs gain a `request_timeout_ms` option, SSH connections now support the model catalog, and atomic file writes get tamper-resistant staging dirs.

## New Features


### `/plan share` command

What: Publish the current plan as a shareable artifact that can be opened in a browser or sent to a reviewer.

Usage:
```
/plan share
```

Details:
- Produces a standalone HTML artifact from the active plan
- Artifact URL is printed to the terminal; share it like any other artifact link
- Errors surface with actionable retry guidance: "Couldn't publish plan — run /plan share to retry"
- Not available in all session types; cloud sessions with an older runtime report: "The plan lives in the cloud workspace, so /plan share can't publish it from this machine yet"

Evidence: New command entry (search for `"plan share: publish returned"` and `"/plan share"`)


### MCP server `request_timeout_ms` config option

What: Per-server HTTP request timeout, overriding the default watchdog for fetch first-byte and tool-call duration.

Usage:
```json
{
  "mcpServers": {
    "my-server": {
      "command": "...",
      "request_timeout_ms": 30000
    }
  }
}
```

Details:
- Applies to both `stdio` and SSE server types
- Capped at 5 minutes regardless of the value you pass
- Set by the host on the `mcp_set_servers` control event; user-set values in config are also respected
- Takes precedence over the legacy `timeout` field when both are present

Evidence: New Zod schema field (search for `"Per-server HTTP request timeout in milliseconds"`)

## Improvements


### Node.js 22 now required

The minimum supported Node.js version has been raised from 18 to 22. Claude Code will refuse to start on older runtimes with:

> Error: Claude Code requires Node.js version 22 or higher.

Check your version with `node --version` and upgrade before updating Claude Code.


### SSH connections can now change models

The model catalog capability (`modelCatalog`) is now enabled for SSH connection types. Previously it was off, which meant `/model` commands in SSH-attached sessions couldn't load the server's available model list.

Evidence: `cSs` connection capability map now sets `ssh.modelCatalog: true` (search for `"modelCatalog"` near SSH entries)


### StopTask accepts teammate names and agent IDs

The task-stop tool description now explicitly documents that you can pass an agent ID (`name@team`) or a bare teammate name to stop an agent-team member — not just numeric background task IDs.

Evidence: Updated tool description (search for `"To stop an agent-team teammate, pass its agent ID"`)


### Atomic file writes: tamper-resistant staging dirs

The sandbox now creates and validates `.cc-writes` staging directories before each atomic write. Identity checks (device + inode) guard against TOCTOU races; a `StagingDirTamperedError` is thrown on mismatch. The `.cc-writes` directory is automatically added to the project `.gitignore`.

Evidence: New staging-dir constant (search for `".cc-writes"`) and tamper error (search for `"Staging dir"` and `"refusing atomic write"`)


### Expired CA certificates filtered at startup

The TLS certificate store now drops expired X.509 certs before they reach the HTTP layer, logging the count:

> CA certs: Dropped N expired certificate(s) from system store

Evidence: `kqu()` function (search for `"expired certificate(s) from system store"`)


### Windows sandbox per-exec filesystem deny

Per-exec `filesystem.denyRead` and `filesystem.denyWrite` entries are now propagated to the Windows sandbox command builder. The previous version threw an error rejecting any per-exec filesystem deny config on Windows; this version threads the paths through to the sandbox layer. `filesystem.allowRead` and `filesystem.allowWrite` still cannot be used per-exec on Windows and continue to throw with a clear message.

Evidence: `Kup()` function; error message (search for `"Per-exec filesystem.allowRead (re-allow within denyRead) is not supported on Windows"`)


### `safeSpawn` blocks commands in the current directory

A new safety guard rejects attempts to spawn executables resolved from `.` (the current directory). This closes a class of path-confusion attacks where a tool-written binary could shadow a system command.

Evidence: Error string (search for `"safeSpawn: command not found or is in an unsafe location (current directory)"`)


### MCP expand tip now service-specific

The tip that suggests adding an MCP server when a user pastes data manually now explicitly states it must name the specific service being bridged rather than citing the user's existing unrelated servers as justification. Prevents the tip from firing in unhelpful contexts.

Evidence: Updated tip `situation` field (search for `"The configured servers are an eligibility signal only"`)


### Proxy environment isolated from unverified connections

Proxy-related environment variables (`HTTPS_PROXY`, `HTTP_PROXY`, `NO_PROXY`, `CLAUDE_CODE_PROXY_RESOLVES_HOSTS`, and others) are now stripped from the environment when a connection has not been verified. Only verified sessions retain proxy config inheritance. This tightens the security boundary for multi-hop or thin-client setups.

Evidence: `IWu()` env-filter and `CRs()` verification check (search for `"CLAUDE_CODE_PROXY_RESOLVES_HOSTS"` and `"CLAUDE_CODE_ENABLE_PROXY_AUTH_HELPER"`)


### New environment variables

Several new `CLAUDE_CODE_*` variables are recognized:

| Variable | Purpose |
|---|---|
| `CLAUDE_CODE_ENABLE_PROXY_AUTH_HELPER` | Enable the proxy auth helper |
| `CLAUDE_CODE_PROXY_AUTH_HELPER_TTL_MS` | TTL for proxy auth helper tokens |
| `CLAUDE_CODE_PROXY_RESOLVES_HOSTS` | Control whether the proxy resolves hosts |
| `CLAUDE_CODE_CUSTOM_OAUTH_URL` | Custom OAuth endpoint URL |
| `CLAUDE_CODE_HOST_CREDS_FILE` | Path to a host-managed credentials file |
| `CLAUDE_CODE_REMOTE_SETTINGS_PATH` | Path to remote settings override file |
| `CLAUDE_CODE_MOCK_REMOTE_SETTINGS` | Use mock remote settings (development) |
| `CLAUDE_CODE_SKIP_PROMPT_HISTORY` | Skip writing prompt history |
| `CLAUDE_CODE_CLIENT_KEY_PASSPHRASE` | Passphrase for a TLS client key |
| `CLAUDE_LOCAL_OAUTH_API_BASE` | Local OAuth API base URL |
| `CLAUDE_SDK_CAN_USE_TOOL_SHADOWED` | Allow SDK to call tool-shadowed tools |

Evidence: `CWu` environment variable set (search for `"CLAUDE_CODE_ENABLE_PROXY_AUTH_HELPER"`)


### `/loop` noop guidance in agent instructions

When the scheduler builds `/loop` instructions, it now includes an explanation of the `noop` field: marking a tick `noop: true` when nothing changed folds consecutive quiet wakeups into a single context entry instead of accumulating one entry per turn.

Evidence: `$da()` function (search for `"noop: true if nothing changed"`)

## Bug Fixes

- `control_cancel_request` messages are now properly validated in the session stream parser rather than silently dropped. Previously only `control_request` was handled; cancel messages fell through to the "unknown type" branch. (search for `"control_cancel_request"`)

- OAuth profile responses are now validated against an expected schema before being used. A malformed response body now logs an explicit error instead of propagating bad data. (search for `"OAuth profile: response body failed shape validation"`)

- Process start time is now read from `/proc/stat` on Linux for better reliability, rather than spawning `ps`. The `ps` path remains as the macOS fallback. (search for `"/proc/stat"`)

- Tool denial reason is now always recorded as `"user-rejected"` when a tool call is denied interactively. Previously the value was conditionally omitted based on an internal flag, causing inconsistent telemetry. (search for `"user-rejected"`)

## Removed


### Speculation engine

The pre-emptive text generation system ("speculation") has been removed entirely. This feature speculatively computed responses during permission prompts and pipelined suggestions; it had been gated behind an internal feature flag and was not widely visible. All `[Speculation]` log entries and the associated code paths are gone.

Evidence: Removed strings (search for `"Speculation paused"`, `"Speculation failed"` — absent in 2.1.198)


### `/agents` TUI wizard

The interactive terminal wizard for creating and managing agent configurations is removed. Attempting to use it now shows:

> The /agents wizard has been removed. Ask Claude to create or update subagents for you (e.g. "create a code-reviewer subagent that ..."), or edit the files directly: `.claude/agents/` (this project) or `~/.claude/agents/` (your user agents)

The agent config files themselves, the `subagents` link in the help, and all programmatic agent management remain fully functional — only the TUI wizard is gone.

Evidence: Removed UI component strings (`"Create new agent"`, `"Edit agent"`, `"Generate with Claude (recommended)"`) and the replacement message (search for `"The /agents wizard has been removed"`)

## In Development

Features with infrastructure added but not yet enabled for all users.


### Precomputed compact persistence [Feature-Flagged]

What: Compact summaries are serialized to `.precompact.json` alongside the session transcript and rehydrated on the next session start, eliminating the startup compact latency for long conversations.

Status: Gated by `tengu_amber_packet`. Off by default.

Details:
- Compact result is written to `<session-id>.precompact.json` after each compaction
- On session start, the file is read and validated (version, model, message boundary, token growth checks)
- If valid and fresh, the summary is used immediately instead of recomputing
- Stale or mismatched files are deleted silently
- Size cap: 8 MB

Evidence: `.precompact.json` suffix constant and `tengu_amber_packet` gate (search for `".precompact.json"` and `"tengu_amber_packet"`)


### Fold boundary for scheduled tasks [Feature-Flagged]

What: A new `fold_boundary` subtype for scheduled task events that marks a context fold point, collapsing repeating loop content in the conversation history.

Status: Gated by `tengu_fold_tool`. Off by default.

Details:
- When enabled, the scheduler emits `fold_boundary` events between loop ticks
- The event renderer treats them the same as `scheduled_task_fire` for display purposes
- Turn metadata gains a `foldedCount` field tracking how many turns were folded

Evidence: `tengu_fold_tool` gate in `vhp()` (search for `"tengu_fold_tool"`) and `"fold_boundary"` subtype


### Highlight.js language grammars as a configurable layer

The file-watcher config model gains an `hljsLanguages` key (enabled in regular mode, disabled in minimal mode). This is the infrastructure needed to load syntax-highlighting language grammars from a separate source rather than bundling them all into the main binary. A large number of built-in grammars (ActionScript, Arduino, C++, ArcGIS Arcade, ABNF, and many others) were removed from the core bundle in this release.

Status: Infrastructure present. No user-facing controls yet.

Evidence: `hljsLanguages` key in file-watcher config (search for `"hljsLanguages"`)

## Notes

Node.js 22 is required as of this version. If you run Claude Code via a system Node.js installation, update before upgrading the package (`node --version` should show v22 or higher). The installer-based distribution bundles its own runtime and is unaffected.

---

Generated with:
- tool: `harness-investigations@0c752ef-dirty`
- provider: `claude`
- model: `claude-sonnet-4-6`
- primary diff: `archive/claude-code/changes/changes-v2.1.198.md` (filtered astdiff)
- string diff: `archive/claude-code/changes/string-diff-v2.1.198.txt`
