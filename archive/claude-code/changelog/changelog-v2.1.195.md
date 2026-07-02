# Changelog for version 2.1.195

## Summary

This release ships the enterprise cloud gateway — a self-hosted proxy that organizations run on-prem to enforce SSO login, spend limits, model allowlists, and audit logging. It also adds WebSocket support to the Monitor tool, updates the default `sonnet` alias to Sonnet 4.6, and brings organization-level effort restrictions that cap which effort levels (including `ultracode`) users can request.

## New Features


### Enterprise cloud gateway (`claude gateway`)

What: Organizations can now run `claude gateway` to self-host an authentication, policy, and telemetry proxy. All Claude Code users in the org connect through it, getting centralized SSO login, spend enforcement, model allowlists, and audit trails — without their tokens ever reaching Anthropic directly.

Usage:
```bash
# Operators: run the gateway (native binary required)
claude gateway --config /path/to/gateway.yaml

# Users: connect to your org's gateway
/login                    # opens browser OAuth flow to IdP
claude mcp login <name>   # also authenticates MCP servers through the gateway
```

Details:
- The gateway is Postgres-backed (`store.postgres_url` in the config). Redis/dev modes were removed in this release.
- SSO login uses OAuth2 device-code flow. When your managed settings include `forceLoginGatewayUrl`, `/login` connects there automatically.
- TLS certificate pinning: the first time you connect to a gateway host, Claude Code shows the SHA-256 fingerprint and asks you to trust it. Subsequent connections verify the pinned fingerprint; a changed certificate triggers a warning before proceeding.
- Gateway hosts must resolve to private IP space only (RFC 1918, loopback, link-local). Public addresses are blocked with an SSRF guard.
- HTTP proxies in the connection path are also checked: the proxy host must be on a private network or the connection is refused.
- Spend limits can be set per user, RBAC group, or organization, with daily/weekly/monthly periods. An admin API lets operators upsert, list, and delete limits.
- Models are checked against the gateway's policy allowlist before requests are forwarded. Requests for models not in the allowlist are rejected.
- OIDC/IdP integration supports Google Workspace (with groups via Admin SDK), Azure AD, and any standards-compliant provider. Email domain and group allowlists can gate access.
- OpenTelemetry telemetry forwarding is configurable; the gateway can relay OTLP data to your observability stack.
- The `claude gateway` command requires the native binary (installed via `https://claude.ai/install.sh`). The npm package alone is not sufficient.

Evidence: Gateway banner (search for `"│ Claude Code Gateway │"`) and startup string (search for `"Run the enterprise auth/telemetry gateway"`). Previous builds showed `"Gateway login is configured in managed settings, but this Claude Code build does not include Cloud gateway support."` — that stub is gone in this release.


### Monitor tool WebSocket support

What: The Monitor tool now accepts a `ws` parameter that opens a persistent WebSocket connection and streams incoming frames as live notifications, replacing the previous approach of using a shell command like `websocat wss://...`.

Usage:
```javascript
Monitor({
  ws: { url: 'wss://events.example.com/stream', protocols: ['v1'] },
  description: 'deploy events',
})
```

Details:
- Each text frame from the socket becomes one notification event. Multiline frames arrive as a single event.
- Binary frames are reported as `[binary frame, N bytes]` rather than passed through.
- Socket close ends the watch; the close code is surfaced. Errors are surfaced before close.
- `ws` and `command` are mutually exclusive. Use `ws` when the server pushes events; use `command` when you need shell tools to filter or transform output.
- Rate limiting and suppression apply the same way as bash monitors. A high-volume firehose will be throttled and eventually stopped — subscribe to a filtered feed where one exists.
- WebSocket egress is subject to `sandbox.network` allow/deny rules and is blocked entirely if `allow_web_fetch` is disabled by org policy.
- Connections to private IP ranges (RFC 1918, link-local, cloud metadata) are blocked with an SSRF guard.
- The Monitor tool description now reads: "watch, monitor, or keep an eye on a process/log/command or WebSocket — stream each stdout line as a live notification."

Evidence: Monitor tool description update (search for `"or WebSocket"`) and WebSocket handler (search for `"Monitor will open a WebSocket to"`). The new `MonitorWsPreconditionError` error class gates failed preconditions cleanly.


### MCP CLI authentication with `--no-browser`

What: `claude mcp login <name>` can now complete authentication without opening a browser, useful when Claude Code is running over SSH.

Usage:
```bash
claude mcp login <name> --no-browser
```

Details:
- Without `--no-browser`, the command opens a browser tab to complete the OAuth flow.
- With `--no-browser`, it prints the callback URL so you can paste it manually from a different machine or terminal.
- This addresses the common case of running Claude Code on a remote server where there is no local browser.

Evidence: New tip string (search for `"claude mcp login <name> --no-browser"`).


### Organization-level effort restrictions

What: Administrators can now cap the maximum effort level users are allowed to request per model. When a user requests an effort level above the org's limit, the request is silently capped or rejected with a clear message.

Details:
- The effort cap is set via gateway policy on a per-model or per-role basis.
- When a user requests a capped level, Claude Code uses the highest permitted level and logs: `Effort 'xhigh' exceeds your organization's limit for <model>; using '<capped-level>'.`
- `ultracode` mode (xhigh + dynamic workflows) is also subject to this cap. The error shown is: "Ultracode runs at xhigh effort, which is restricted by your organization for <model>."
- The `/effort` usage string is now dynamically generated and only shows the levels your org allows for the current model — levels above your cap are omitted from the list.
- A static message "Higher effort levels are restricted by your organization." appears in the effort picker UI when restrictions apply.

Evidence: Effort restriction message (search for `"Higher effort levels are restricted by your organization."`). Capping logic checks org's `maxEffortLevel` per model via the gateway policy.


### `/config` inline key=value setting

What: `/config key=value` now lets you set panel settings directly from the chat input without opening the settings panel.

Usage:
```
/config model=claude-sonnet-4-6
/config theme=dark
/config verbose=true
```

Details:
- Supported keys include model, theme, verbose, output style, editor, and other panel-level settings.
- This is a faster alternative to opening the `/config` panel and navigating menus.
- The tip shown to users reads: "/config key=value sets panel settings (model, theme, verbose, output style, …) inline — no need to open the panel."

Evidence: New tip string (search for `"/config key=value sets panel settings"`).

## Improvements


### Sonnet 4.6 is now the default `sonnet` alias

The `sonnet` family alias now resolves to `claude-sonnet-4-6` (was `claude-sonnet-4-5`). The model catalog aliases were updated to:

```
sonnet  → claude-sonnet-4-6  (was claude-sonnet-4-5)
opus    → claude-opus-4-8    (unchanged)
haiku   → claude-haiku-4-5   (unchanged)
fable   → claude-fable-5     (unchanged)
```

Sonnet 4.6 has a knowledge cutoff of August 2025 and supports effort levels, max effort, adaptive thinking, and context management.

Evidence: Model catalog (search for `"sonnet": { "default": "claude-sonnet-4-6" }`).


### Structured model catalog with formal schema

The model registry is now a versioned, schema-validated catalog (`model-catalog.json`) instead of scattered inline definitions. Each model entry includes: family, display name, knowledge cutoff, provider IDs for all backends (first_party, Bedrock, Vertex, Foundry, Mantle, gateway), context window size, capability flags, default effort level, image size limits, and model picker metadata.

The catalog is used to look up capabilities for any model by ID, replacing ad-hoc hardcoded checks. The `JB()` helper queries capability flags like `effort`, `max_effort`, `xhigh_effort`, `adaptive_thinking`, `fast_mode`, `lean_prompt`, `mid_conv_system`, `rejects_disabled_thinking`, `context_management`.

Evidence: Model catalog (search for `"Generated by \`bun run generate:model-catalog\`"`).


### MCP tool input schema normalization

MCP tools with top-level `anyOf`, `oneOf`, or `allOf` schemas can now be normalized for Claude. When a tool's input schema uses these combinators at the root level, the CLI flattens the properties into a standard `{ type: "object", properties: {...} }` shape and adds a human-readable `Input constraint:` note explaining which parameter groups apply.

This is gated by the `tengu_mcp_normalize_root_combinators` feature flag. Set this flag to `["*"]` to normalize all MCP servers, or to a list of hostnames to normalize only specific servers.

Without normalization, tools with top-level combinators are still available but the model may have trouble filling out the input correctly. The previous behavior was to log a warning and drop the tool.

Evidence: Normalization functions (search for `"Input constraint: all listed parameters apply together"`) and feature flag (search for `"tengu_mcp_normalize_root_combinators"`).


### Permission rule tooltip teaches Tool(param:value) matching

The permission rules UI now shows a tip explaining that deny and ask rules can match on specific tool input parameters, not just tool names:

> Deny and ask rules can match a tool input parameter — e.g., deny Agent(model:opus) or ask Bash(run_in_background:true) — so that specific pattern is auto-handled without prompting each time.

This makes it clearer that you can write rules like `deny Agent(model:opus)` to auto-deny whenever Claude requests an Agent call with that specific model, without blocking all Agent calls.

Evidence: New user tip string (search for `"deny Agent(model:opus) or ask Bash(run_in_background:true)"`).


### Code review skill: per-location verification

The `/code-review` workflow description was updated to clarify that verification now runs per unique (file, line) location across all finders, rather than per individual candidate.

Old: "one independent verifier per candidate"
New: "one independent verifier per every distinct (file, line) location across the pooled candidates"

This means if two finder agents surface the same bug at the same location, only one verification pass runs for that location — eliminating redundant verification work.

Evidence: Skill description string (search for `"per distinct (file, line) location across the pooled candidates"`).


### Voice mode gives clearer error on servers without microphones

When voice mode fails to open an audio capture device, the error message now explicitly explains that this typically means the host has no microphone (e.g., a remote server) and tells you to run Claude Code on a machine with a microphone:

> Voice mode requires a microphone, but SoX could not open an audio capture device. This usually means the host has no microphone (for example, a remote server). Run Claude Code on a machine with a microphone.

Evidence: New error string (search for `"Voice mode requires a microphone, but SoX"`).


### Better error messages for cloud Projects

Error handling for `--project` flag now includes:
- Specific message when the project ID doesn't exist or isn't accessible: "Project not found: <id>. Check the id — a Project you don't have access to looks the same as one that doesn't exist."
- Warning when a public Project is requested with a non-Anthropic cloud environment: "is a public Project, and public Projects run on Anthropic-hosted infrastructure only. Pick an Anthropic-managed cloud environment, or use a private Project."
- Org-level gate message: "Projects are not available for your organization."
- Endpoint gating message: "--project requires the new session-create endpoint, which isn't enabled for your account yet — no session was created."
- Conflict with GitHub PR sessions: "--project cannot be used on a GitHub-PR-bound create; it has no Project input — no session was created."

Evidence: Error strings (search for `"Project not found:"` and `"Projects are not available for your organization."`).


### Interrupted response recovery

When a response is interrupted mid-generation, Claude Code now attempts to continue coherently from where it left off. The user sees: "Continuing an interrupted response. Text before the interruption:" followed by the partial output fenced as `<interrupted-output>`. The continuation prefill hint is handled internally as `[reply-on-resume] partial-hint`.

Evidence: Recovery strings (search for `"Continuing an interrupted response"` and `"[reply-on-resume] partial-hint"`).


### Vertex 1M context caveat documented

A note was added explaining that Sonnet 4.5 and Sonnet 4 do not support 1M context on Vertex (requests using the `[1m]` model suffix for these models will get a 400). The 1M lineup on Vertex is Opus 4.6 and newer Sonnet variants.

Evidence: New caveat string (search for `"Sonnet 4.5/Sonnet 4 do not support 1M context on Vertex"`).


### Sandbox network permission checks use domain matching

The network sandbox (`sandbox.network.allowedDomains` / `deniedDomains`) now also reads from `permissions.allow` / `permissions.deny` rules with `domain:` prefix, unifying two separate configuration paths. Domain matching supports wildcards (`*`). Both operator and managed-policy rules are evaluated.

Evidence: Domain check functions (search for `"is in sandbox.network.deniedDomains"` and `"sandbox.network.allowManagedDomainsOnly"`).

## Bug Fixes

- Adopt (`adopt.json` handoff) now retries on `EPERM`/`EBUSY`/`EACCES` with up to 3 retries and 50ms backoff before giving up, instead of failing immediately on a locked file (search for `"ebusy_retry"`).
- Skill override lookup now checks `localSettings` in addition to `projectSettings` and `userSettings`, and correctly handles the `user-invocable-only` lock state for author-locked skills (search for `"user-invocable-only"`).
- The `/clear` command now logs the original cwd it captured, helping debug cases where the working directory was wrong after clearing (search for `"/clear: originalCwd"`).
- Daemon log redaction now masks full `cc-daemon-<hex>` socket names in error messages and stack traces, preventing internal socket paths from leaking into user-visible output (search for `"cc-daemon-*"`).

## Notes

The `dev:` store type for the gateway was removed. Gateway configurations that used `dev:` must be updated to set `store.postgres_url` pointing at a PostgreSQL instance (locally: `docker run --rm -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres`). There is no in-process fallback store anymore.

Settings keys prefixed with `__` (double underscore) are no longer recognized. If you have any such keys in your `settings.json`, remove or rename them. See the string `__.*`. See CHANGELOG v2.1.195.` in the source for the gate that rejects them.

The `claude gateway` command requires the native binary distributed via `https://claude.ai/install.sh`. Installing only the npm package `@anthropic-ai/claude-code` is not sufficient — the binary check returns the message "claude gateway requires the native binary" and exits.

---

Generated with:
- tool: `harness-investigations@0c752ef-dirty`
- provider: `claude`
- model: `claude-sonnet-4-6`
- primary diff: `archive/claude-code/changes/changes-v2.1.195.md` (filtered astdiff)
- string diff: `archive/claude-code/changes/string-diff-v2.1.195.txt`
