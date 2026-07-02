# Changelog for version 2.1.193

## Summary

Version 2.1.193 is a security and reliability-focused release. Key highlights include a new `disableSideloadFlags` enterprise setting that closes CLI-flag bypasses of marketplace restrictions, write-path symlink verification that prevents TOCTOU race conditions on file writes, a new `&`-operator safety prompt for background shell commands, and automatic recovery when the working directory is deleted. The release also adds plugin renaming support in marketplace manifests and a new `model_refusal_no_fallback` SDK event for better refusal handling.


## New Features


### `disableSideloadFlags` Enterprise Setting

What: A new managed setting that blocks `--plugin-dir`, `--plugin-url`, `--agents`, and non-SDK `--mcp-config` CLI flags at startup, closing the CLI-flag bypass of `strictKnownMarketplaces`.

Details:
- Only honored when set in **managed settings** (policy-controlled). Ignored in user, project, or local settings.
- When a blocked flag is used, Claude Code exits with: "X is disabled by your organization's managed settings (disableSideloadFlags). Plugins, custom agents, and MCP servers can only be loaded from sources your administrator has approved."
- Pair with `allowedMcpServers` for per-server MCP control; this setting does **not** gate other MCP entry points such as `claude mcp add`, SDK `setMcpServers`, or `.mcp.json`.
- Does not block MCP servers configured through approved marketplace sources.

Evidence: New setting description (search for `"disableSideloadFlags"` or `"rejects the --plugin-dir, --plugin-url, --agents"`)


### Plugin Renaming in Marketplace Manifests

What: Marketplace authors can now declare plugin renames in their manifest using a `renames` field. When a plugin is not found under its old name, Claude Code follows the rename chain and migrates the user's settings to the new name automatically.

Details:
- The `renames` field is an append-only map of old plugin name → current name (or `null` to indicate the plugin was removed).
- On plugin-not-found, the loader resolves the chain and updates `enabledPlugins` and `pluginConfigs` in all writable settings files.
- A new `tengu_plugin_renamed` telemetry event tracks rename outcomes (`resolved`, `removed`, `unresolved`).
- Unresolvable renames (cycles, missing targets, chains deeper than the limit) are logged with the reason.

Evidence: New `renames` schema field (search for `"Append-only map of old plugin name"`) and rename migration logic (search for `"migrateRenamedPluginsInSettings"`)


### `model_refusal_no_fallback` SDK Event

What: A new system event is now emitted when the model ends a turn with stop reason `"refusal"` and no fallback model is configured, allowing SDK consumers to handle refusals programmatically.

Details:
- Event fields: `type: "system"`, `subtype: "model_refusal_no_fallback"`, `original_model`, `request_id`, `api_refusal_category`, `api_refusal_explanation`, `content`, `uuid`, `session_id`.
- A new `refused_user_message_uuid` field (added to both `model_refusal_fallback` and `model_refusal_no_fallback`) contains the UUID of the human turn that triggered the refusal — the rewind target and composer prefill for edit-and-retry.
- `refused_user_message_uuid` is `null` when the refused turn was not human-authored (e.g., a background task notification or auto-continuation).
- Not emitted when a fallback model existed but was declined or gate-failed (that case uses the existing `model_refusal_fallback` event).

Evidence: New event schema (search for `"model_refusal_no_fallback"` or `"UUID of the user message the refused request was for"`)


## Improvements


### Write-Path Symlink Verification

What: When writing a file, Claude Code now verifies that the parent-directory symlink resolution has not changed between when permission was checked and when the write actually happens.

Details:
- If symlinks shift between the permission check and the write, the write is blocked with: "Refusing to write X: its parent-directory symlink resolution changed after permission was checked."
- The approved directory list is stashed at check-time (keyed by tool use ID) and compared at write-time, preventing TOCTOU races where a symlink is replaced after approval.

Evidence: New guard logic (search for `"its parent-directory symlink resolution changed after permission was checked"`)


### Background Operator `&` Safety Warning

What: Shell commands that include the `&` background operator now always trigger an approval prompt, regardless of existing allow rules.

Details:
- The `&` operator defers execution past approval-time safety checks, so it cannot be pre-approved reliably.
- The prompt message explains: "This command uses the `&` background operator, which defers execution past approval-time safety checks. Approve only if you trust it."
- This does not apply to `&&` (and-then) or `&>` (output redirect); only actual backgrounding operators.

Evidence: New safety check (search for `"background operator, which defers execution past approval-time safety checks"`)


### REPL Context Poisoning Protection

What: When REPL sandbox code renders a global non-configurable (making it impossible to restore to a clean state), Claude Code now detects this, resets the VM context automatically, and shows a clear recovery message.

Details:
- A new `VMContextPoisonedError` class is thrown when this condition is detected.
- The REPL context is reset and the user sees: "REPL context poisoned by non-configurable global; context reset" with a note that "global state (variables, registered tools) starts fresh."
- Uses a WeakSet to identify boundary cap errors — the set is identity-based and not inspectable by attacker code, so a Proxy cannot fake a cap error to escape the walker.

Evidence: New error class (search for `"REPL sandbox code made the global"` or `"VMContextPoisonedError"`)


### Workflow VM Boundary Security

What: Values crossing the workflow VM boundary now pass through a security-hardened sanitizer that runs inside the VM context itself, protecting against Proxy-based escape attacks.

Details:
- The sanitizer uses a `WeakSet` for cap-error identity (cannot be faked by an attacker-controlled Proxy whose get-trap returns `true` for any key).
- Arrays are length-capped at a maximum count; exceeding it throws with "array length N exceeds the maximum of N supported across the workflow VM boundary."
- Functions on crossed values are stripped to `undefined`.
- Workflow results cannot be functions; attempting this now throws "workflow result cannot be a function."

Evidence: New in-VM sanitizer (search for `"workflow VM boundary"` or `"workflow result cannot be a function"`)


### `su` and `runuser` Added to Privilege Escalation List

What: The `su` and `runuser` commands are now added to the set of privilege escalation commands that always require manual approval, alongside the existing `sudo`, `doas`, and `pkexec`.

Evidence: Updated privilege escalation set (search for `"runuser"` in the permissions module)


### Autocompact Thrashing Detection

What: The autocompact circuit breaker now uses a fixed threshold of 3 consecutive rapid refills (rather than a configurable parameter embedded in the message), and the error message is now more actionable.

Details:
- New message: "Autocompact is thrashing: the context refilled to the limit within 3 turns of the previous compact, 3 times in a row. A file being read or a tool output is likely too large for the context window. Try reading in smaller chunks, or use /clear to start fresh."
- Previous message was split across multiple string fragments; it's now a single constant.

Evidence: New constant (search for `"Autocompact is thrashing: the context refilled to the limit within 3 turns"`)


### Working Directory Resilience

What: If the current working directory is deleted while Claude Code is running, it now recovers by changing to the nearest existing ancestor directory instead of crashing.

Details:
- Logs a warning: "Original directory X no longer exists — returned to Y instead."
- Walks up the directory tree until it finds an existing path.

Evidence: New recovery logic (search for `"no longer exists — returned to"` or `"Original directory"`)


### GitHub Enterprise Host Detection

What: GitHub Enterprise Server instances (self-hosted GitHub) are now properly detected throughout the codebase, replacing hardcoded `github.com` comparisons with host-aware utility functions.

Details:
- New `Em()` function recognizes a hostname as GitHub.com (with or without `www.` prefix).
- New `ewr()` and `fgs()` functions return the correct REST API and GraphQL endpoint URLs for both GitHub.com and GitHub Enterprise.
- `GH_HOST` environment variable comparisons now use normalized host matching (`ocn()`) instead of exact string equality.
- Marketplace git source fetches now use the constant `github.com` instead of a hardcoded literal string.

Evidence: Host detection utilities (search for `"https://api.github.com"` in `ewr()`, or `"github.com"` constant `LA`)


### Org Policy Error Message Consolidation

What: The per-feature "disabled by policy" messages (previously separate for voice mode, remote control, cloud sessions, and web search) are now generated by a shared utility function that also handles the case where the policy cannot be fetched.

Details:
- When policy cannot be fetched (network unreachable), now shows: "Couldn't verify your organization's policy for X. Check your network connection and try again." — instead of silently blocking.
- When policy is fetched and feature is blocked: "X is disabled by your organization's policy. Contact your organization admin to enable it/them."
- Old separate static strings removed.

Evidence: New shared utility `gG()` (search for `"Couldn't verify your organization's policy for"`)


### Trust Dialog Enforcement for Settings Permissions

What: Permission allow-rules and additional directory grants from `.claude/settings.json` and `.claude/settings.local.json` are now silently ignored when the workspace has not yet been trusted via the interactive trust dialog.

Details:
- Logs to stderr: "Ignoring N permissions.allow entries from .claude/settings.json: this workspace has not been trusted. Run Claude Code interactively here once and accept the trust dialog, or set `projects[\"...\"].hasTrustDialogAccepted: true` in `~/.claude/settings.json`."
- Only applies before the trust dialog has been accepted for this workspace; once trusted, all settings are applied normally.
- Managed (policy-level) settings are still honored regardless of trust state.

Evidence: New enforcement logic (search for `"this workspace has not been trusted. Run Claude Code interactively here once"`)


### `OTEL_LOG_ASSISTANT_RESPONSES` Environment Variable

What: A new environment variable that enables OTEL telemetry logging of assistant response content (previously only `OTEL_LOG_USER_PROMPTS` existed).

Usage:
```bash
OTEL_LOG_ASSISTANT_RESPONSES=1 claude
```

Details:
- When either `OTEL_LOG_ASSISTANT_RESPONSES` or `OTEL_LOG_USER_PROMPTS` is set, assistant response text is included in OTEL spans.
- Without this flag, response content is logged as `<REDACTED>`.

Evidence: New env var check (search for `"OTEL_LOG_ASSISTANT_RESPONSES"`)


### Worktree Symlink Safety Checks

What: Worktree setup now checks that entries in `.worktreeinclude` and `settings.local.json` copies do not resolve to destinations outside the worktree via committed symlinks, and skips them if they do.

Details:
- Logs: "Skipping .worktreeinclude entry: destination escapes worktree via committed symlink: X"
- Logs: "Skipping settings.local.json copy: destination escapes worktree via committed symlink"
- Prevents a worktree setup from being used to read or write files outside the isolated checkout.

Evidence: New safety messages (search for `"destination escapes worktree via committed symlink"`)


### Screen Reader Mode: Cursor Visibility

What: When accessibility mode or screen reader detection is enabled, the cursor is no longer hidden when leaving alternate screen mode.

Details:
- Previously, the `\x1B[?25l` (hide cursor) escape was always sent. Now it is skipped when `accessibilityMode` or `isScreenReaderEnabled` is true.
- Screen-reader-driven tools often rely on the cursor being visible for navigation.

Evidence: Conditional cursor-hide escape (search for `"accessibilityMode || this.isScreenReaderEnabled"`)


### Destructive Command Scope Detection

What: A new analysis pass for Bash and PowerShell commands classifies the scope of destructive operations (e.g., `rm -rf`, `Remove-Item -Recurse`) as `cwd`, `outside_cwd`, `tmp`, or `unknown`, enabling more targeted permission prompts.

Details:
- Analyzes both bash-style (`rm -rf path`) and PowerShell cmdlet (`Remove-Item -Path target -Recurse -Force`) syntax.
- Recognizes temp-directory patterns on macOS (`/tmp`, `/var/tmp`, `/private/tmp`), Linux, and Windows (`%TEMP%`, `AppData\Local\Temp`).
- Shell expansions (`$VAR`, backticks, wildcards) cause the scope to be classified as `unknown` rather than guessing.

Evidence: New scope detection (search for `"destructive-target-scope parse failed"`)


## Bug Fixes

- OAuth profile: now requires **both** `account` and `organization` fields before applying a fetched profile; previously any non-null result was accepted, potentially leaving org context empty. (search for `"l?.account && l.organization"`)

- Bash parse error recovery: when the tree-sitter parser returns an `ERROR` node wrapping a `program` node at the root level, the inner `program` node is now unwrapped before redirect analysis, preventing false-positive dangerous-redirect detections. (search for `"n.type === \"ERROR\" && n.children[0]?.type === \"program\""`)

- PowerShell quoting: shell-quoting checks on Windows now use the full Windows quoting rules (backslash at end of string requiring special treatment), not just dollar-sign detection. (search for `"SCo(c)"` in Windows quoting path)

- Background bash shell memory pressure reaping: Claude Code now registers a `memoryPressure` event listener on background shell processes when not running as a subagent, allowing the OS to signal when memory is tight. Idle, unnoticed shells are then reaped. (search for `"task_local_shell_pressure_reap"`)

- MCP needs-auth count is now surfaced in the app state (`mcpNeedsAuthCount`), enabling the UI to reflect pending MCP authentication requirements. (search for `"mcpNeedsAuthCount"`)

- Model picker now correctly filters and replaces deprecated model aliases with their first-party equivalents when the model is confirmed available. (search for `"Ia(r.aliasModel)"` in model picker)

- `--mcp-debug` flag removed; functionality is covered by `--debug`. (search for removed `"--mcp-debug"` in string diff)

- Background agent spawn: when resuming a previous session with `--resume`, the transcript path is now correctly passed through to the background agent launch parameters. (search for `"resumeTranscriptPath"`)

- HTML content extraction: the web fetch tool now also extracts `<meta name="description">` content and `<h1>` headings for better URL titles when the `<title>` tag is missing or generic. (search for `"<meta[^>]+name="` in HTML parser)

- Error telemetry: errors from background spawn failures and console method failures now include a `telemetryMessage` field (via `gh()`) so they're correctly categorized in error tracking rather than grouped under generic labels. (search for `"background spawn failed"` or `"console.${s} failed"`)


## In Development


### `tengu_cobalt_plinth_putguard` [In Development]

What: A dormant security flag that, when enabled, detects proxy interception of GCS artifact uploads by checking for a header that only real GCS responses include.

Status: Feature-flagged (off by default)

Details:
- Export name `isFrameSignedPutHeaderCheckEnabled` reveals the intent.
- After a successful (2xx) HTTP PUT to Google Cloud Storage, the guard checks for the `x-goog-generation` response header — present on every authentic GCS response, absent on proxied ones.
- If the header is missing on a 2xx, the upload is rejected with: `"upload intercepted: 2xx without x-goog-generation — a proxy answered in place of GCS"` (status 403, `intercepted: true`).
- Scoped to GCS PUT responses only. Anthropic API traffic (`api.anthropic.com`), telemetry, OAuth, and MCP are unaffected — this does not block proxying of model requests or conversation content.
- When enabled, would break transparent proxies that cannot forward GCS headers intact: Burp Suite, mitmproxy, corporate SSL inspection, LLM gateways (LiteLLM, Portkey, etc.).

Evidence: Flag check `mrl()` in `vKp()` GCS upload handler; export `isFrameSignedPutHeaderCheckEnabled` (search for `"x-goog-generation"`)

---

Generated with:
- tool: `harness-investigations@66416d2-dirty`
- provider: `claude`
- model: `claude-sonnet-4-6`
- primary diff: `archive\claude-code\changes\changes-v2.1.193.md` (filtered astdiff)
- string diff: `archive\claude-code\changes\string-diff-v2.1.193.txt`
