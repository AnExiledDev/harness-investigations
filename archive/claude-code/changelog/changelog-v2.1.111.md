# Changelog for version 2.1.111

## Summary

This is a major release introducing full support for **Claude Opus 4.7**, a new **"xhigh" effort level**, an **interactive effort selector UI**, **automatic terminal theme detection**, and a new **proxy authentication helper** for enterprise environments. Opus 4.7 becomes the default model for first-party users, with automatic remapping from Opus 4.6. The `/effort` command now supports five levels instead of four, and the Skills dialog gains a token-count sorting option. Windows users also gain session environment support, previously restricted to macOS and Linux.


### Claude Opus 4.7 Model Support

What: Full support for the new Claude Opus 4.7 model across all provider platforms, with automatic remapping from Opus 4.6.

Usage:
```bash
# Opus 4.7 is now the default for first-party users
claude

# Explicitly select Opus 4.7
claude --model claude-opus-4-7

# Opus 4.7 with 1M context window
claude --model opus[1m]

# Opt out of automatic model remapping
CLAUDE_CODE_DISABLE_LEGACY_MODEL_REMAP=1 claude
```

Details:
- Opus 4.7 is automatically selected as the default model for first-party users, replacing Opus 4.6
- Users on Opus 4.6 will see "Model updated to Opus 4.7" with an option to opt out via `CLAUDE_CODE_DISABLE_LEGACY_MODEL_REMAP=1`
- The 1M context window variant is available as "Opus 4.7 (1M context)" in the model picker
- Vertex AI region support added via `VERTEX_REGION_CLAUDE_4_7_OPUS` environment variable
- First-time users see an onboarding banner: "Opus 4.7 is here" / "Welcome to Opus 4.7 xhigh!"
- Model descriptions updated throughout: "Opus 4.7 · Most capable for complex work"
- Adaptive thinking support extended to Opus 4.7
- The model family reference in system prompts now reads "Claude 4.X" instead of "Claude 4.6 and 4.5"

Evidence: Opus 4.7 model strings (search for `"claude-opus-4-7"`) — 0 occurrences in v2.1.110, 144 in v2.1.111. Onboarding via `qUY()` at line ~546062 (search for `"Opus 4.7 is here"`)


### New "xhigh" Effort Level

What: A new effort level called "xhigh" is added between "high" and "max", providing deeper reasoning capability exclusive to Opus 4.7.

Usage:
```bash
# Set effort via CLI flag
claude --effort xhigh

# Set effort in-session
/effort xhigh
```

Details:
- The effort scale now has five levels: `low`, `medium`, `high`, `xhigh`, `max`
- "xhigh" is described as "Deeper reasoning than high, just below maximum (Opus 4.7 only)"
- "xhigh" is the automatic default effort level when using Opus 4.7
- If "xhigh" is requested on a model that doesn't support it, it falls back to "high"
- The `effortLevel` setting now accepts: `low`, `medium`, `high`, `xhigh`, `max`
- The `/effort` command help text is updated accordingly

Evidence: "xhigh" effort level (search for `"xhigh"`) — 0 occurrences in v2.1.110, 40 in v2.1.111. Default logic in `bF1()` at line ~237923 (search for `"opus-4-7"` returning `"xhigh"`)


### Interactive Effort Level Selector

What: A new visual, interactive effort level picker that lets you slide between effort levels using arrow keys.

Usage:
```
/effort
```
Then use `←`/`→` arrow keys to move between levels and `Enter` to confirm.

Details:
- When invoked without arguments, `/effort` opens an interactive dialog
- A visual slider displays a scale from "Speed" to "Intelligence"
- The current selection is highlighted with a `▲` indicator on the track
- Each level renders with a distinct color and animation style (e.g., "autoAccept-shimmer" for certain levels)
- Press `Escape` or `Ctrl+C` to cancel without changing

Evidence: Effort selector UI in `boY()` at line ~575448 (search for `"←/→ to change effort"`)


### Auto Theme Detection (Match Terminal)

What: Claude Code can now automatically detect your terminal's light or dark theme and match it, using the "Auto (match terminal)" theme option.

Details:
- A new system theme watcher uses OSC 11 terminal escape sequences to query the terminal's background color
- The detected luminance determines whether the terminal is "light" or "dark"
- Supports multiplexers (tmux, screen) with DCS passthrough and fallback detection
- Theme changes are detected dynamically — if you switch your terminal's theme, Claude Code follows
- The "Auto (match terminal)" option is now available in the theme picker

Evidence: System theme detection via OSC 11 in `Wh_()` at line ~185609 (search for `"systemTheme: OSC 11"`) — 0 occurrences in v2.1.110, 2 in v2.1.111


### Proxy Authentication Helper

What: Enterprise users behind authenticated proxies can now configure a shell command that provides proxy authentication headers, avoiding manual credential management.

Usage:
```bash
# Enable the proxy auth helper
export CLAUDE_CODE_ENABLE_PROXY_AUTH_HELPER=1

# Optionally configure the cache TTL (in milliseconds)
export CLAUDE_CODE_PROXY_AUTH_HELPER_TTL_MS=60000
```

Configure `proxyAuthHelper` in your project or local settings to specify the shell command that outputs a `Proxy-Authorization` header value.

Details:
- When enabled, Claude Code runs the configured helper command to obtain proxy auth credentials
- Credentials are cached with a configurable TTL (via `CLAUDE_CODE_PROXY_AUTH_HELPER_TTL_MS`)
- If the helper is configured in project/local settings, workspace trust must be accepted before it runs
- HTTP 407 (Proxy Authentication Required) responses now trigger automatic re-authentication
- The `Proxy-Authenticate` header from 407 responses is passed to the helper as `CLAUDE_CODE_PROXY_AUTHENTICATE`
- Helper failures are logged with details and fall back to previously cached credentials
- The feature is marked "EAP" (Early Access Program) in the settings description

Evidence: Proxy auth helper in `f08()` at line ~100631 (search for `"proxyAuthHelper"`) — 0 occurrences in v2.1.110, 7 in v2.1.111


### SDK: Subagent System Prompt Injection

What: SDK users can now append custom system prompt content to all Task-tool subagents via a new `appendSubagentSystemPrompt` option.

Usage:
```typescript
// In SDK session options
{
  appendSubagentSystemPrompt: "Your custom instructions here"
}
```

Details:
- The `appendSubagentSystemPrompt` field is propagated to nested subagents automatically
- Gated by the `CLAUDE_CODE_ENABLE_APPEND_SUBAGENT_PROMPT` environment variable
- Allows SDK consumers to inject additional instructions into every subagent without modifying the main system prompt

Evidence: SDK subagent prompt support (search for `"appendSubagentSystemPrompt"`) — 0 occurrences in v2.1.110, 13 in v2.1.111


### SDK: 1-Hour Cache TTL and Query Depth Configuration

What: New SDK schema fields for controlling cache behavior and query depth.

Details:
- `is1hCacheTTL`: Boolean flag (default `false`) to enable 1-hour cache TTL instead of the default 5-minute TTL
- `queryDepth`: Numeric field for configuring query depth in SDK sessions
- These are passed as query parameters in API requests

Evidence: Cache TTL config (search for `"is1hCacheTTL"`) — 0 occurrences in v2.1.110, 6 in v2.1.111


### Skills Dialog: Sort by Token Count

The Skills management dialog (`/skills`) now supports sorting skills by their token count. Press `t` to toggle between alphabetical sorting and token-count sorting. When sorted by tokens, the subtitle displays "· sorted by tokens". This helps identify which skills consume the most context.

Evidence: Token sorting in `UlK()` at line ~554320 (search for `"settings:sortByTokens"`) — 0 occurrences in v2.1.110, 4 in v2.1.111


### Windows Session Environment Support

The restriction preventing session environment initialization on Windows has been removed. Previously, users saw "Session environment not yet supported on Windows" — this message no longer appears, and session environments now work on all platforms.

Evidence: Removed guard (search for `"Session environment not yet supported on Windows"`) — present in v2.1.110, absent in v2.1.111


### Ultrareview Enhancements

The `/ultrareview` command (which existed since v2.1.110) receives several improvements:
- Dynamic cost and duration estimates are now fetched from server configuration instead of being hardcoded (previously "~$10", now configurable like "$10-$20")
- Billing messaging now shows "This review bills as Extra Usage" with cost estimates and a link to billing documentation
- Diff stat scope information is displayed when reviewing a branch
- Bundle size checking warns if the repo is too large to bundle: "Repo is too large to bundle. Push a PR and use `/ultrareview <PR#>` instead."
- Improved error handling with `onBundleFail` callbacks and session tracking (`sessionId`, `sessionUrl`)
- Feature availability is gated by `Yu6()?.enabled === !0`, allowing server-side control

Evidence: Ultrareview enhancements (search for `"Ultrareview is currently unavailable."`) — new error message in v2.1.111. Cost config via `Au6()` at line ~552336 (search for `"$10-$20"`)


### LSP Diagnostics Management

The Language Server Protocol manager now tracks document versions with a `getDocumentVersion` method, ensuring proper version incrementing for `didOpen` and `didChange` notifications. Additionally, a new diagnostics purging system drops stale `publishDiagnostics` entries when files change, with logging: "LSP Diagnostics: Purged N pending entry(ies) referencing ..."

Evidence: Diagnostics purging in `kI8()` at line ~293692 (search for `"LSP Diagnostics: Purged"`)


### Sleep Inhibitor Naming

The sleep prevention system has been renamed from "caffeinate" to "sleep inhibitor" for cross-platform clarity. Status messages now read:
- "Stopped sleep inhibitor, allowing sleep" (was "Stopped caffeinate, allowing sleep")
- "Restarting sleep inhibitor to maintain prevention" (was "Restarting caffeinate to maintain sleep prevention")
- "sleep inhibitor spawn error:" (was "caffeinate spawn error:")

Evidence: Renamed messages (search for `"sleep inhibitor"`) — 0 occurrences in v2.1.110, 3 in v2.1.111


### /clear Command Description Clarified

The `/clear` command description now reads: "Start a new session with empty context; previous session stays on disk (resumable with /resume)" — replacing the previous "Start fresh: discard the current conversation and context". This clarifies that previous sessions are preserved and resumable.

Evidence: Updated description (search for `"resumable with /resume"`)


### Improved Version Constraint Error Messages

Plugin dependency version conflict messages are now more specific, with three distinct error types:
- "has conflicting version requirements (no version satisfies all of: ...)" for disjoint ranges
- "has version requirements too complex to intersect — simplify the ranges: ..." for overly complex constraints
- "has an invalid version requirement among: ..." for malformed version strings

Evidence: New error messages in `ZS8()` at line ~257651 (search for `"has conflicting version requirements (no version satisfies all of:"`)


### Improved Bash Command Safety Analysis

Shell command safety checks now categorize different types of risks with specific `bashMissKind` tags:
- `multi-cd` for commands with multiple directory changes
- `cd-compound-redirect` for compound cd commands with output redirection
- `shell-operators` for dangerous shell metacharacters
- Glob vs variable expansion now distinguished: "Command contains unquoted variable expansion" replaces the previous "Command contains unquoted glob or variable expansion"

Evidence: Bash safety categorization (search for `"bashMissKind"`)


### Faster Fuzzy Matching with Damerau-Levenshtein

The string distance algorithm used for fuzzy matching (e.g., command suggestions for typos) has been upgraded from standard Levenshtein distance to Damerau-Levenshtein distance, which also considers character transpositions. A configurable `maxEditDistance` parameter is now available.

Evidence: Damerau-Levenshtein algorithm in `EKY()` at line ~421613


### Skill Tool Description Improvements

The Skill tool's description and parameter guidance have been refined:
- Skill name parameter now reads: "The name of a skill from the available-skills list. Do not guess names."
- The tool now instructs: "Only invoke a skill that appears in that list, or one the user explicitly typed as `/<name>` in their message. Never guess or invent a skill name from training data"
- Simplified invocation guidance with explicit instructions for plugin-namespaced skills

Evidence: Updated skill tool description (search for `"Do not guess names"`)


### MCP Tool Permission Policies

MCP server tool permissions now support a `permission_policy` field carried on `mcp_set_servers` for remote servers, allowing administrators to pre-configure allowed/denied tool lists for MCP tools.

Evidence: Permission policies (search for `"permission_policy"`) — 2 occurrences in v2.1.110, 5 in v2.1.111


### PowerShell Tool Now Feature-Flagged on Windows

The PowerShell tool on Windows is now controlled by the `tengu_cobalt_ridge` feature flag instead of being always enabled. Non-Windows platforms continue to respect the `CLAUDE_CODE_USE_POWERSHELL_TOOL` environment variable. This allows server-side rollout control of the PowerShell tool experience.

Evidence: Feature flag in `ly6()` at line ~250722 (search for `"tengu_cobalt_ridge"`)


### Accept-Encoding Header Added to Requests

HTTP requests now include an `Accept-Encoding: identity` header across transport types, which may improve compatibility with certain proxy configurations.

Evidence: New header (search for `"Accept-Encoding"`) — 8 occurrences in v2.1.110, 14 in v2.1.111


### System Prompt Streamlining

Several large embedded documentation blocks have been removed from the system prompt and likely externalized:
- Claude API cURL/HTTP documentation (~220 lines)
- Claude API Python documentation (~420 lines)
- Streaming TypeScript documentation (~178 lines)
- Prompt Caching documentation (~171 lines)
- Tool Use Concepts documentation (~287 lines)
- TypeScript API documentation (~333 lines)

This reduces the token footprint of the system prompt. The documentation content is now served from external skill files or live documentation sources.

Evidence: Removed documentation blocks (search for `"# Claude API — cURL"`, `"# Claude API — Python"`)


## Bug Fixes

- Fixed case-insensitive path comparison on Windows to correctly handle path matching logic (search for `"platform detection and case normalization"`)

- Fixed delete-word-before behavior in REPL editor: when the line is empty, the action is now a no-op instead of potentially causing unexpected behavior (search for `"delete-word-before"`)

- Fixed retry error display to detect SSL errors and show configurable max retries (search for `"SSL error detection"`)

- Fixed git index refresh to add an early-return guard when the index is null and a prior refresh has already occurred, preventing unnecessary refreshes (search for `"lastRefreshMs"`)

- Fixed Windows path glob pattern handling to preserve leading slashes instead of stripping them (search for `"relativePattern"`)

- Fixed Node component rendering to display the `name` property instead of the entire object (search for `"q.name property"`)

- Fixed path validation to add null safety check before path derivation, preventing potential crashes when the path is unavailable (search for `"if (!K) return !1"`)

- Removed stale file tracking length check that could cause early returns, allowing file operations to proceed even with an empty cached file list (search for `"cachedTrackedFiles"`)


## Notes

Opus 4.6 users will be automatically remapped to Opus 4.7 on upgrade. To opt out of this remapping, set the environment variable `CLAUDE_CODE_DISABLE_LEGACY_MODEL_REMAP=1`. The Opus 4.6 model remains available via the model picker as "Opus 4.6" and "Opus 4.6 (1M context)".

The default effort level for Opus 4.7 is "xhigh". If you previously had your effort level pinned to a specific value, it will be preserved. The new `unpinOpus47LaunchEffort` configuration flag allows the system to auto-adjust effort on first use of the `/effort` command.

The commit message template has been updated from "Claude Opus 4.6" to "Claude Opus 4.7".
