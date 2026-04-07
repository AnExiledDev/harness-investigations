# Changelog for version 2.1.90


## Summary

This release introduces the `/powerup` interactive tutorial system for learning Claude Code features, adds first-class support for Claude Platform on AWS as a new provider, adds the `/toggle-memory` command for disabling automemory per-session, significantly expands parent proxy support for enterprise network environments, and improves security hardening across Docker, PowerShell, and Linux sandbox subsystems.

### /powerup — Interactive Feature Tutorials

What: A new `/powerup` command that launches a set of 10 interactive lessons teaching Claude Code features that "most people miss." Each power-up includes animated terminal demos, explanatory text, and can be marked as completed.

Usage:
```
/powerup
```

Details:
- 10 lessons covering: @ file mentions, permission modes (shift+tab), undo/rewind, background tasks, CLAUDE.md memory, MCP tool integration, skills & hooks, subagents, remote control/teleport, and model/effort switching
- Progress is persisted — unlocked power-ups carry across sessions (stored via `powerupsUnlocked` in local settings)
- A celebration animation plays when all 10 are completed ("All powered up")
- Suggested to new users on the welcome screen when the terminal is tall enough (≥44 rows): "New here? Run `/powerup` to learn the features most people miss."
- Telemetry events: `tengu_powerup_lesson_opened`, `tengu_powerup_lesson_completed`

Evidence: Power-up command and lesson system (search for `"Discover Claude Code features through quick interactive lessons"`)


### Claude Platform on AWS Provider

What: Claude Code now supports "Claude Platform on AWS" as a first-class API provider, alongside Bedrock, Vertex, and Foundry.

Usage:
```bash
CLAUDE_CODE_USE_ANTHROPIC_AWS=1 claude
```

Details:
- Set `CLAUDE_CODE_USE_ANTHROPIC_AWS=1` to enable the provider
- Requires `ANTHROPIC_AWS_WORKSPACE_ID` (or `workspaceId` in constructor)
- Optionally set `ANTHROPIC_AWS_BASE_URL` or let it derive from `AWS_REGION` / `AWS_DEFAULT_REGION` (pattern: `https://aws-external-anthropic.{region}.api.aws`)
- Supports AWS SigV4 request signing via `@aws-sdk/credential-providers`
- Supports explicit credentials via `awsAccessKey` + `awsSecretAccessKey`, AWS profile, or a custom `providerChainResolver`
- Set `CLAUDE_CODE_SKIP_ANTHROPIC_AWS_AUTH=1` to skip authentication (for development/testing)
- Fast mode is not available on this provider (same as Bedrock, Vertex, and Foundry)

Evidence: AnthropicAws client class (search for `"Claude Platform on AWS"` and `"ANTHROPIC_AWS_WORKSPACE_ID"`)


### /toggle-memory — Session Automemory Toggle

What: A new `/toggle-memory` slash command that disables or re-enables automemory for the current session.

Usage:
```
/toggle-memory
```

Details:
- When toggled off: "this conversation will not write or read new memories, and previously-loaded memory content should not be referenced"
- When toggled back on: "memory content may be referenced and new memories can be saved"
- Memory read/write operations are blocked while toggled off, returning guidance to run `/toggle-memory` to re-enable
- Fires `tengu_memory_toggled` telemetry with `toggled_off` boolean
- The command is `isHidden: false` so it appears in command listings, but `isEnabled: () => false` (the toggle itself is always available; the `isEnabled` likely gates something else)

Evidence: Toggle-memory command definition (search for `"Toggle automemory off/on for this session"`)


### Parent Proxy Configuration

What: The sandbox proxy can now route outbound traffic through an upstream (parent) HTTP proxy, enabling use in corporate environments with mandatory egress proxies.

Details:
- Configured via the `network.parentProxy` setting, with sub-keys for `http`, `https`, and `noProxy`
- Falls back to standard `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` environment variables when the setting is not explicitly configured
- `NO_PROXY` supports hostname suffixes, wildcard `*`, and CIDR ranges (both IPv4 and IPv6)
- Localhost and loopback addresses always bypass the parent proxy
- CONNECT tunneling through the parent proxy for HTTPS traffic, with proper authentication (Basic auth from proxy URL credentials)
- Hop-by-hop headers are stripped when forwarding through the proxy
- Logs configured proxy URLs at startup: `Parent proxy configured: http=... https=...`

Evidence: Parent proxy routing logic (search for `"Upstream HTTP proxy for outbound connections"` and `"Parent proxy configured"`)

### Memory System Refinements

- The two-step memory save process (write file, then update MEMORY.md index) has been simplified — the MEMORY.md index step has been removed, and memory is saved directly to individual files. The number of `MEMORY.md` references decreased from 10 to 6 between versions.
- Memory retrieval now prefixes content with "Retrieved for possible relevance — use only if it actually applies to what the user asked" to reduce false positive influence.
- Memory selection is now more conservative with user-profile and project-overview memories: the system explicitly avoids matching on surface keyword overlap (e.g., a profile mentioning "DB performance" won't be selected just because a question contains the word "performance").
- Memory extraction now skips runs where no user prose has been added since the last extraction, reducing unnecessary extraction cycles (search for `"[extractMemories] skipping — no user prose since last extraction"`).
- The extraction prompt now includes "If nothing is worth saving, output only 'Nothing to save.' Do not explain why." for cleaner no-op results.

Evidence: Memory selection system prompt (search for `"Be especially conservative with user-profile"`) and extraction guard (search for `"no user prose since last extraction"`)


### PostToolUse Hook File State Sync

When a PostToolUse hook modifies a file that Claude just edited (e.g., a formatter running after a write), Claude Code now automatically detects the change and re-syncs its internal read-file state. This prevents stale-file errors on the next Edit tool call for that file.

Evidence: Hook file sync handler (search for `"PostToolUse hook modified"` and `"re-synced readFileState"`)


### Docker Command Security Hardening

Docker commands now reject `--host`, `--context`, `--config`, and `--tls` flags, as well as short flags `-H` and `-c`, which could be used to redirect Docker operations to a remote daemon and escape the sandbox.

Evidence: Docker flag validation (search for `startsWith("--host")` near the docker command validator)


### PowerShell Security Improvements

- Background job operator (`&`) detection: PowerShell commands using the `&` operator now trigger a security prompt with the message "Command uses the background job operator (`&`) which spawns a child PowerShell process" (search for `"background job operator"`).
- `Remove-Item -Recurse` safety: Deleting the working directory (including `.git` and `.claude`) via `Remove-Item -Recurse` now requires manual approval (search for `"Remove-Item -Recurse targeting"`).
- Action parameter validation: PowerShell common parameters like `-ErrorAction`, `-WarningAction` (and their aliases `-ea`, `-wa`, etc.) are now validated to ensure they use expected values (`SilentlyContinue`, `Stop`, `Continue`, `Ignore`), preventing abuse of these parameters.

Evidence: PowerShell AST parser (search for `"hasBackgroundJob"` and `"background job operator"`)


### Linux Sandbox Improvements

- Mount point cleanup is now deferred when multiple sandboxes are still active, using a reference counter to avoid premature cleanup (search for `"Deferring mount point cleanup"`).
- Added `--unshare-user` flag in certain sandbox configurations for tighter process isolation.
- Write paths that get wiped by a `denyRead` tmpfs mount are now automatically re-bound (search for `"Re-bound write path wiped by denyRead tmpfs"`).
- Deny path deduplication prevents redundant sandbox mount operations.

Evidence: Sandbox refcount (search for `"sandbox(es) still active"`) and re-bind logic (search for `"Re-bound write path wiped by denyRead tmpfs"`)


### Proxy Error Handling

The sandbox proxy now provides more specific error messages for connection failures:
- `"CONNECT handshake timed out"` — timeout during proxy CONNECT
- `"Proxy closed during CONNECT handshake"` — premature close
- `"Proxy refused CONNECT: ..."` — non-2xx response from proxy
- `"CONNECT response header too large"` — headers exceeding 16KB
- `"Denying malformed host: ..."` / `"Rejecting malformed SOCKS host: ..."` — input validation
- `"Invalid destination host for CONNECT"` / `"Invalid destination port"` — bad target validation
- `"Invalid parent proxy URL, ignoring: ..."` — misconfigured parent proxy URL
- `"unsupported scheme or empty host"` — bad proxy URL scheme

Evidence: CONNECT tunnel error handling (search for `"CONNECT handshake timed out"` and `"Proxy refused CONNECT"`)


### Upgrade Path Messaging

Users who cannot upgrade their plan now see a clearer message: "Upgrade not currently available. For additional usage, run /extra-usage." instead of a generic error.

Evidence: Upgrade handler (search for `"Upgrade not currently available"`)


### Auto-Mode Opt-in Logging

Debug logging now records auto-mode permission opt-in status, including checks across user, local, flag, and policy settings scopes, making it easier to diagnose permission configuration issues.

Evidence: Auto-mode logging (search for `"[auto-mode] hasAutoModeOptIn"`)

## Bug Fixes

- Fixed network allowlist hostname matching to correctly reject IP addresses for wildcard domain patterns (e.g., `*.github.com` no longer incorrectly matches bare IP addresses) (search for `"qI_"` in the `NC1` function)
- Removed the FetchHttpHandler polyfill and several duplicate URI encoding/query string builder modules that were dead code from the AWS SDK bundling (removed `bc7`, `rn7`, `D9q`, `f9q`, `N9q`, `y9q`, `B9q` functions)

### "Buddy" Feature [In Development]

What: A companion feature referenced as "buddy" that appears to be gated by configuration.

Status: Dark-launched / configuration-gated

Details:
- The only visible artifact is the message: "buddy is unavailable on this configuration"
- Appears to be checked via `Fd8()` and returns null when unavailable
- No further implementation details are visible in this version

Evidence: Buddy availability check (search for `"buddy is unavailable on this configuration"`)


### Transcript Persistence Sync [Gradual Rollout]

What: Infrastructure for synchronizing conversation transcripts to a server for session continuity across devices.

Status: Feature-flagged / server-controlled

Details:
- Uploads main conversation events and subagent entries to a persistence backend
- Tracks events since last compaction, skips oversized entries
- Integrated with the bridge:repl system for session forwarding
- Log prefix `[persistence-sync]` for debugging
- CCR v2 internal event writer registered for transcript persistence

Evidence: Persistence sync system (search for `"[persistence-sync] Uploaded"` and `"CCR v2 internal event writer"`)

## Notes

- The full HTML generation for "Claude Code Insights" reports was removed from the CLI bundle. If you used `/insights` to generate local HTML reports, this functionality may have moved to the web interface.
- The `/resume` command now filters out loop sessions and entrypoint-based sessions from the resume picker (search for `"filtered from /resume"`).
