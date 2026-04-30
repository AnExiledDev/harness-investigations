# Changelog for version 2.1.124

## Summary
This release adds a new `claude project purge` CLI command for cleaning up per-project state, ships a scoped history-search picker (session/project/everywhere) bound to Ctrl+S, and renames the internal "upstreamproxy" relay to "egress-gateway" with a new `/v1/code/egress/gateway` endpoint. It also adds gateway-model discovery for `ANTHROPIC_BASE_URL` deployments, oversized-image auto-removal-and-retry, an `isolatePeerMachines` Remote Control safety setting, a new `oauth_org_not_allowed` error class, and the `doneMeansMerged` "keep going until PR is merged" mode (currently `@internal`).


### `claude project purge` command
What: A new CLI subcommand that deletes every piece of Claude Code state belonging to a project — transcripts, task lists, debug logs, file edit history, the project entry in `~/.claude.json`, and the matching prompt-history lines.

Usage:
```bash
# Purge state for the current directory (interactive picker if no path given)
claude project purge

# Purge for a specific project path
claude project purge /path/to/repo

# Show what would be deleted without deleting
claude project purge --dry-run

# Skip the confirmation prompt
claude project purge --yes

# Step through each item with delete/skip/all/abort prompts
claude project purge -i
claude project purge --interactive

# Purge state for ALL projects on this machine
claude project purge --all
```

Details:
- The interactive picker lists every project that has state on disk (current cwd plus anything found under `~/.claude/projects/`) so you can pick one to purge.
- A "purge plan" is printed before any deletion runs, e.g. `dir: <path>  project transcripts (.jsonl) and memory/`, `config: projects["<path>"]  project entry in ~/.claude.json (trust, history, MCP servers)`, `filter: <path>/history.jsonl  N prompt(s) typed in this project`.
- `--all` is mutually exclusive with both a path argument and `--interactive`; the CLI errors with `Cannot specify both a path and --all.` / `Cannot use -i/--interactive with --all.` if you mix them.
- Warnings are printed (not deleted): `shell-snapshots/ are not project-scoped and will not be touched`, and `backups/ may still contain this project entry in old .claude.json snapshots (...); at most 5 are kept and they rotate out automatically`.
- A safety check refuses to overwrite the config if an in-process re-read is missing auth that the cache has — preventing accidental credential loss (GH #3117).

Evidence: Project purge command (search for `"Manage Claude Code project state"` and `"Delete all Claude Code state for a project (transcripts, tasks, file history, config entry)"`).


### Scoped history search (Ctrl+S to cycle)
What: The `↑` / history picker now shows a dedicated "Search prompts" view that can be scoped to the current session, the current project, or everywhere. Press Ctrl+S to cycle between scopes.

Usage:
- Open the history picker, type to filter, press `Ctrl+S` to switch between `session` → `project` → `everywhere`.
- Filter input shows `Filter history…` placeholder; the title displays the active scope (e.g. `Search prompts · project`).
- Empty states are now `Loading…`, `No matching prompts`, or `No history yet` depending on the picker state.

Details:
- The picker uses fuzzy-subsequence matching as a fallback when the literal substring isn't found.
- Layouts adapt to terminal width: ≥ 100 columns shows a side-by-side preview; narrower terminals stack the preview below.
- A new keybinding action `historySearch:cycleScope` is registered globally and emits the `tengu_history_picker_scope` telemetry event when used.
- In remote sessions, history search is unavailable and the user sees: `History search isn't available in remote sessions yet`.

Evidence: History search picker (search for `"Search prompts"`, `"Filter history…"`, and the new keybinding `"historySearch:cycleScope"`); scope list `Sc$ = ["session", "project", "everywhere"]`.


### Oversized-image auto-removal with retry
What: When a request to the model fails because an image's dimensions exceed the per-request many-image pixel limit, Claude Code now identifies the offending image, replaces it with a placeholder, and retries automatically.

Details:
- A new pure-JS image dimension reader recognizes PNG, GIF, JPEG, and WebP (VP8/VP8L/VP8X) headers — no shelling out.
- On a 400 from the API matching `dimensions exceed max allowed size … N pixels`, the offending content block is rewritten to text: `[Image removed: dimensions exceeded the 2000px limit for requests with many images]` and the request retries with a log line `(exceeded 2000px many-image limit); retrying.`
- Retry is gated by the existing image-pre-resize logic so requests that wouldn't fit even after rescaling fail fast.

Evidence: Image dimension parser and retry path (search for `"[Image removed: dimensions exceeded the 2000px limit for requests with many images]"` and `"retry:image-dimension:"`).


### Gateway model discovery for `ANTHROPIC_BASE_URL`
What: When `ANTHROPIC_BASE_URL` is set against a first-party gateway, Claude Code now discovers the gateway's available Claude/Anthropic models on startup and lists them in the model picker labelled `From gateway`.

Details:
- On startup it issues `GET <baseUrl>/v1/models?limit=1000` (using whichever of `ANTHROPIC_AUTH_TOKEN` / API key is configured plus any `ANTHROPIC_CUSTOM_HEADERS`), filters to entries whose `id` starts with `claude` or `anthropic`, and caches them in `<config-dir>/cache/gateway-models.json` keyed by base URL.
- Empty / non-OK responses are dropped with debug logs: `[gatewayDiscovery] non-OK status …`, `[gatewayDiscovery] response body failed validation`, `[gatewayDiscovery] 0 usable models after filter`, `[gatewayDiscovery] cached N models`.
- Discovery is skipped when the host manages the provider (`CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST`) or when not in first-party mode.
- The `/model` picker merges these into the available list so Bedrock/Vertex-only models get inline labels and descriptions instead of being hidden.

Evidence: Gateway discovery (search for `"gateway-models.json"`, `"/v1/models?limit=1000"`, and `"From gateway"`).


### `isolatePeerMachines` setting (Remote Control safety)
What: A new boolean setting that requires explicit user approval before `SendMessage` can reach a peer Claude Code session running on a different machine via Remote Control.

Usage (in settings.json):
```json
{
  "isolatePeerMachines": true
}
```

Details:
- When the latch is engaged for a session it is persisted to the JSONL session log as `isolation-latch` events (sticky type) so resumed sessions inherit the side they were locked to.
- Setting description: `Require explicit approval before SendMessage can reach a peer session on another machine via Remote Control`.

Evidence: Setting schema and runtime check (search for `"isolatePeerMachines"` and `"isolation-latch"`).


### `doneMeansMerged` mode (`@internal`, gradual rollout)
What: A new internal setting that changes Claude's stop condition: instead of stopping when its response is "done", Claude keeps working until the PR is ready to merge, a cron/Monitor is armed to resume later, or it hands you a concrete next step.

Usage (in settings.json, internal builds only):
```json
{
  "doneMeansMerged": true
}
```

Details:
- Schema description: `@internal When true, Claude keeps working until the PR is ready for you to merge, a cron/Monitor is armed to resume later, or it hands you a self-contained next step.`
- A companion meta-system message is injected when the setting is on: `The user has asked you to work without stopping for clarifying questions. When you'd normally pause to check, make the reasonable call and continue; they'll redirect if needed.` Internal text describing how the harness signals itself: `You ended the turn without calling SendUserMessage.`
- A new "session PR resolved" tracker (`sessionPrResolved`) and the kairos brief stop-hook text are wired into this mode; a flag-controlled hint (`tengu_kairos_brief_stop_hook_text`) lets the server adjust the in-prompt language without a release.

Evidence: Schema setting and behavioral hint (search for `"doneMeansMerged"` and `"You ended the turn without calling SendUserMessage."`).


### Better OAuth-disabled-by-org error
What: When OAuth login is disallowed at the organization level, Claude now produces a dedicated error (`oauth_org_not_allowed`) and a clearer user-facing message instead of treating it as a generic auth failure.

Details:
- Long form (login screens, Web UI): `Your organization has disabled Claude subscription access for Claude Code · Use an Anthropic API key instead, or ask your admin to enable access`.
- Short form (status indicators / logs): `org disabled OAuth — use API key or ask admin`.
- The error is plumbed through both the autonomous-progress state machine and the `terminate_reason` enum.

Evidence: New error code (search for `"oauth_org_not_allowed"` and `"Your organization has disabled Claude subscription access for Claude Code"`).


### Trusted-Device gate for Remote Control
What: Organizations that mandate Trusted Devices now block Remote Control startup with an actionable message until the device is enrolled.

Details:
- New gate function returns: `Your organization requires Trusted Devices for Remote Control, but this device is not enrolled. Please run \`/login\` in Claude Code to enroll this device.`
- Both `RA6` (Remote Control eligibility) and the `claude bridge` startup check honor the new gate.

Evidence: Trusted-device check (search for `"Your organization requires Trusted Devices for Remote Control"`).


### `DISABLE_GROWTHBOOK` environment variable
What: A new environment variable that disables GrowthBook-driven server-side feature flagging.

Usage:
```bash
DISABLE_GROWTHBOOK=1 claude
```

Details:
- Listed alongside the other `DISABLE_*` opt-outs (`DISABLE_TELEMETRY`, `DISABLE_INSTALLATION_CHECKS`, `DISABLE_COST_WARNINGS`, etc.) and is automatically forwarded to subprocesses.

Evidence: Environment passthrough lists (search for `"DISABLE_GROWTHBOOK"`).


### `claude install` deprecation banner
What: The "switch from npm to native installer" notification has been refreshed and is now a registered startup notification with priority `high`.

Details:
- Message: `Claude Code has switched from npm to native installer. Run \`claude install\` or see https://docs.anthropic.com/en/docs/claude-code/getting-started for more options.`
- Suppressed in development builds and when `DISABLE_INSTALLATION_CHECKS` is set.

Evidence: Startup notification (search for `"npm-deprecation-warning"` and `"Claude Code has switched from npm to native installer"`).


### Bash-tool / printf safety hardening
The Bash command analyzer now rejects `printf` invocations that could execute arbitrary code via format-string substitution: `printf` arguments containing `$`, `\u/\U` escapes, format specifiers paired with non-numeric runtime values, or any flag other than the literal `--` are no longer auto-allowed.

For double-bracket arithmetic, the diagnostic now points out that `bash` may run `$(cmd)` while reusing `[[`'s semantics: `' contains array subscript or runtime-determined value — bash evaluates $(cmd) in subscripts` and `...' operand is non-numeric — \`[[\` arithmetically evaluates identifiers/subscripts (may run $(cmd))`.

A new escape-line-continuation rule replaces the older one to handle even-vs-odd backslashes correctly when deciding whether a backslash-newline pair is a real line continuation.

Evidence: Bash analyzer (search for `"contains array subscript or runtime-determined value"` and `"Delimiters-only string node contains unparsed command substitution"`).


### Egress gateway rename (was "upstream proxy")
The internal MCP-proxy infrastructure was renamed end-to-end:
- New endpoints: `/v1/code/egress/gateway` (was `/v1/code/upstreamproxy/...`) and `/v2/session_ingress/mcp/ws/`.
- All log lines moved from `[upstreamproxy] ...` to `[egress-gateway] ...` (e.g. `[egress-gateway] enabled on 127.0.0.1:`, `[egress-gateway] relay listening on 127.0.0.1:`, `[egress-gateway] aws config write failed: ...`, `[egress-gateway] prctl unavailable: ...`, `[egress-gateway] no session token; proxy disabled`, `[egress-gateway] ws error: ...`).
- The internal `initEgressGateway` / `getEgressGatewayEnv` / `registerEgressGatewayEnvFn` exports replace the `*UpstreamProxy*` names.
- Init failures now log `[init] egress gateway init failed: ...; continuing without proxy`.

If you scrape Claude Code logs for the old `upstreamproxy` prefix, update your queries.

Evidence: Renamed prefixes (search for `"[egress-gateway]"` and `"/v1/code/egress/gateway"`).


### Windows clipboard copy via stdin pipe
Pasting large content into the clipboard on Windows no longer base64-encodes the payload onto the PowerShell command line. Instead, Claude pipes UTF-8 bytes to a fixed PowerShell snippet (`[Console]::InputEncoding = [Text.Encoding]::UTF8; Set-Clipboard -Value ([Console]::In.ReadToEnd())`), removing the previous payload-length cap.

Evidence: New clipboard copy command (search for `"Set-Clipboard -Value ([Console]::In.ReadToEnd())"`).


### PowerShell shell description on Windows
When git-bash is the active shell but PowerShell is also detected on Windows, the system prompt now reads: `Shell: PowerShell (use PowerShell syntax — e.g., $null not /dev/null, $env:VAR not $VAR, backtick for line continuation). Bash is also available via the Bash tool for POSIX scripts.`

Previously the wording was bash-first with a "PowerShell is also available via the PowerShell tool" suffix; the new copy emphasizes PowerShell as primary and points at Bash as a fallback.

Evidence: Windows shell description (search for `"Bash is also available via the Bash tool for POSIX scripts"`).


### Cursor-IDE detection accommodates VSCode 1.92–1.105
Detection of Cursor as the host editor now also fires when `TERM_PROGRAM === "vscode"` and the reported VSCode version falls in the `1.92.0`–`1.105.0` range, since a Cursor-bundled VSCode in that window mis-reports as plain VSCode. A small parser (`major.minor.patch` → `M*1e6 + m*1e3 + p`) makes the comparison explicit.

Evidence: Cursor host detection (search for `"VSCODE_GIT_ASKPASS_MAIN"` and `"TERM_PROGRAM_VERSION"`).


### Background-job working-directory error is now actionable
When a background worker can't spawn because its `cwd` no longer exists, the job is marked permanently `crashed` instead of looping respawn attempts:

```
working directory no longer exists: <cwd>
[<reason> — this job cannot be respawned]
```

The same path also fires the new `tengu_bg_spawn_cwd_gone` telemetry event.

Evidence: Background spawn cwd-gone (search for `"working directory no longer exists:"` and `"this job cannot be respawned"`).


### Stream watchdog re-arms after suspend
The byte-stream watchdog in remote sessions now distinguishes "the network really went idle" from "your laptop went to sleep". When the wall-clock idle exceeds the expected interval by enough to look like a system suspend, it logs `Stream watchdog fired after suspend (actual idle <ms> ms (sleep/suspend), re-arming` and re-arms instead of declaring the stream dead. Late watchdog suppressions are also logged as `[byte-watchdog] suppressed: late=`.

Evidence: Watchdog re-arm (search for `"Stream watchdog fired after suspend"` and `"[byte-watchdog] suppressed:"`).


### Memory-feedback prompt copy
The optional-feedback prompt after a memory recall is now phrased `Did this memory help? (optional)` (was `Did this help? (optional)`), making it clearer what the user is rating.

Evidence: Memory feedback prompt (search for `"Did this memory help? (optional)"`).


### File edit history snippet budgeting
When several files are edited in a single turn and their accumulated diff snippets would blow past the per-turn budget (`16384` chars), later files are now omitted from the in-prompt diff. The model sees:

> Note: `<filename>` was modified, either by the user or by a linter. ... The diff was omitted because other modified files in this turn already exceeded the snippet budget; use the Read tool if you need the current content.

This trades extra `Read` calls for predictable context usage.

Evidence: Snippet budget (search for `"The diff was omitted because other modified files in this turn already exceeded the snippet budget"`).


### Auto-mode classifier timeout cleanup
The two-stage auto-mode tool classifier now runs each call inside a single `Dj6(timeout, ...)` wrapper that tears down the abort signal and timer in `finally`, replacing the previous ad-hoc `signal:` plumbing. The user impact is shorter hangs when an auto-classifier call stalls.

Evidence: Auto-mode wrapper (search for `"classifierStage"` near the new helper).


### `token-efficient-tools` beta header
A new beta header is added to the centralized header registry: `token_efficient_tools` → `token-efficient-tools-2026-03-28`. The whole registry was reorganized to use `Object.freeze({ name, header })` records, making it easier to enable/disable individual betas server-side via `stickyBetas`.

Evidence: Beta header registry (search for `"token-efficient-tools-2026-03-28"`).


### Bedrock auth header normalization
The Bedrock client now always sets `Authorization: null` in `defaultHeaders` and re-injects the bearer or service-tier headers explicitly. This stops a leaked Authorization header from a parent fetch leaking into Bedrock requests.

Evidence: Bedrock client builder (search for `Authorization: null`).


### MCP `file_suggestions` SDK request
The SDK control protocol gains a new `file_suggestions` request kind: callers can ask Claude Code's index for matching file paths and receive a list of `{ path }` entries. This enables external tools (e.g. `claude-code-vscode`) to power the `@` mention autocomplete from the host process.

Evidence: New SDK request branch (search for `"file_suggestions"` and `"generateFileSuggestions"`).


### `ccshare_url` in feedback responses (internal builds)
Submit-feedback responses now include an optional `ccshare_url` field on success. Schema: `Internal share URL for the conversation. Only set in internal builds when the upload succeeded; absent otherwise.`

Evidence: Feedback response schema (search for `"ccshare_url"` and `"Internal share URL for the conversation"`).


### Pickers reset on filter change
The reusable list-picker now exposes a `resetKey` prop; when it changes, focus resets to the top and any input is cleared. The history picker uses this when you cycle scopes so you don't end up with a stale focused row from the previous scope.

Evidence: Picker `resetKey` (search for `resetKey:` in the picker call site).


### "Settings errors" prompt has a "Fix with Claude" path
When startup detects malformed `settings.json` (or similar), the error dialog now offers `Fix with Claude` instead of just exiting. Choosing it boots Claude with an auto-generated prompt asking it to repair the file and any in-flight prompt is appended after the fix prompt.

Evidence: Settings repair flow (search for `"Fix with Claude"`).


### `update-config` skill prompt rewritten
The bundled `update-config` skill (the one Claude uses to edit `settings.json`) was rewritten with explicit guidance on:
- When hooks are required vs preferences (`PreToolUse`, `PostToolUse`, `PreCompact`, `PostCompact`, `Stop`, `Notification`, `SessionStart`).
- "CRITICAL: Read Before Write" — always read the existing settings file before editing.
- Using `AskUserQuestion` to disambiguate user/project/local scope.
- Right-vs-wrong array merging examples for `permissions.allow` and hook arrays.
- Troubleshooting hook execution (debug flags, matcher checking, etc.).

Evidence: Skill prompt (search for `"# Update Config Skill"` and `"## CRITICAL: Read Before Write"`).


### Remote Control entrypoint detection tightened
The set of entrypoints that count as "remote" (and therefore skip terminal-only features) is now more conservative — only known entrypoints, and never when `BUGHUNTER_FLEET_SIZE` is set.

Evidence: Remote-mode classification (search for the entrypoint set check that gates `H.add("ccr")`).


### Plugins cache cleared on plugin refresh
`refreshActivePlugins` now also calls a new `clearedInstalledPluginsCache` log — `Cleared installed plugins cache` — alongside the existing per-component clears, ensuring stale plugin metadata never bleeds across switches.

Evidence: Plugin refresh (search for `"Cleared installed plugins cache"`).


### Effort command no longer error-spams
`/effort` no longer surfaces a "Failed to set effort level: …" toast when the underlying user-settings write returns an error; the value is still applied via the in-memory app state.

Evidence: Effort command simplification (search for the removed `"Failed to set effort level:"` string).


### Read tool description simplified
The `Read` tool's `offset` and `limit` parameter descriptions reverted to the original short form. The longer "harness truncates oversized files automatically" copy gated by `tengu_slate_reef` was removed.

Evidence: Read tool schema (search for `"The line number to start reading from. Only provide if the file is too large to read at once"` — single description now).


### Session resume tracks isolation latch
Session JSONL files now include `isolation-latch` records (sticky), and resuming a session restores the previous `currentSessionIsolationLatch`. This complements the new `isolatePeerMachines` setting so Remote-Control approvals don't reset on resume.

Evidence: JSONL session log type (search for `"isolation-latch"` and `currentSessionIsolationLatch`).


### `@`-mention attribution metadata
Tagged-input attributions now serialize `from` and `from-name` attributes (with quote-stripping on the display name) into the system-reminder block, so multi-user sessions can show who supplied each piece of context.

Evidence: Attribution serialization (search for `"from-name=\""`).


## Bug Fixes

- Fix a race in OAuth token refresh that could write a stale token after a parallel refresh succeeded; the lock now compares `accessToken` against the value held at lock acquisition time.
- Token-refresh HTTP timeout raised from 15s to 30s — long-tail refreshes no longer fail when the IDP is slow.
- The `enter` chord is no longer suggested in the task-picker hint row for `mcp_task` items, where viewing isn't supported.
- Fixed a sort instability in the prompt-completion suggester — scores are now bucketed by tenths before falling back to recent-usage tiebreak, removing a flicker on every keystroke.
- Background spare-claim failures now propagate the inner error to the caller (previously only the outer "Background service unreachable" message survived).
- The history-picker's last-match search now case-folds the query before scanning entries.
- The `prompt-caching-scope-2026-01-05` plus other betas dropped only the `tengu_slate_reef` gating; no functional change.
- Web search results no longer enable prompt caching (caching was forced off for that path), avoiding wasted cache reads on per-call ephemeral tool schemas.

(Search for `"tengu_oauth_token_refresh_race_resolved"`, `"tengu_oauth_token_refresh_starting"`, `"\"mcp_task\""`, and `"enablePromptCaching: !1"` to verify each.)


### `doneMeansMerged` "keep working" mode [In Development]
Covered above under New Features; the schema, hint, telemetry, and PR-resolved tracker all ship in this version, but the field is annotated `@internal` and only exposed in internal builds. External users can't toggle it yet.

Status: `@internal` schema field; runtime support is wired up.

Orphaned tip: ⚠️ None visible to users.

Evidence: Schema description (search for `"@internal When true, Claude keeps working until the PR is ready for you to merge"`).


### `purge-by-glob` and `wheelFlood` keybinding [In Development]
A new `wheelFlood` keybinding action is registered alongside `historySearch:cycleScope` but no UI binding currently routes a keystroke to it; it appears only in telemetry/debug logs (`· wheelFlood`).

Status: Action declared but not bound to a key; no user-facing effect yet.

Evidence: Keybinding action registry (search for `"· wheelFlood"`).


### `oauth_org_not_allowed` plumbing for the autonomous-progress state [In Development]
The new error code is fully wired through the request/response and terminate-reason enums, but at present it surfaces only on initial-request failures. Mid-session token rotations that hit the org-disabled response still get classified as a generic `authentication_failed`. Expect mid-session detection to follow.

Evidence: Enum expansion only (search for `"oauth_org_not_allowed"` in the enum but not in the in-flight refresh paths).


## Notes

- If you have any tooling or log-analysis scripts that match `[upstreamproxy]` log lines or `/v1/code/upstreamproxy/...` URLs, update them to `[egress-gateway]` / `/v1/code/egress/gateway`.
- The `isolatePeerMachines` setting is opt-in and defaults to off, so existing Remote Control workflows are unchanged unless you set it.
- Per-project state purges via `claude project purge` are irreversible (`This cannot be undone.`); always preview with `--dry-run` first.
