# Changelog for version 2.1.85


## Summary

This release introduces a billing and quota system for ultrareviews, adds an upstream proxy for remote sessions, significantly hardens the Bash tool's security validation (especially on Windows/PowerShell), and replaces native Rust/WASM modules with pure JavaScript implementations for file indexing and syntax highlighting. Hooks gain a new `if` field for conditional filtering, and enterprise administrators can now block plugins by organization policy.

### Ultrareview Billing and Quota Management

What: Ultrareviews now operate on a freemium model — users get a limited number of free reviews, after which reviews bill as Extra Usage.

Details:
- A new `/v1/ultrareview/quota` API endpoint tracks remaining free reviews
- Each free ultrareview displays its count: "This is free ultrareview X of Y"
- Once free reviews are exhausted, users are prompted with a billing dialog titled "Ultrareview billing"
- Users can choose "Proceed with Extra Usage billing" to continue
- A minimum balance of $10 is required: "Balance too low to launch ultrareview ($X.XX available, $10 minimum)"
- Users without Extra Usage enabled see: "Free ultrareviews used. Enable Extra Usage at https://claude.ai/settings/billing to continue."
- Review time estimates updated from ~5–15 min to ~10–20 min

Evidence: Ultrareview billing dialog (search for `"Ultrareview billing"`) and quota API (search for `"/v1/ultrareview/quota"`)


### Enhanced Ultrareview Workflow

What: Ultrareviews now offer web-based review options, progress tracking, and better validation before launch.

Details:
- New option: "Review in Claude Code on the web" for launching reviews in the browser
- New option: "Review the plan in Claude Code on the web" for plan reviews
- Progress tracking link displayed after launch: "Track progress: {URL}"
- "Answer in browser" display for browser-based responses
- Pre-launch validation: "No changes against the {branch} fork point. Make some commits or stage files first."
- Improved large repo handling: "Repo is too large. Push a PR and use `/review <PR#>` instead."
- Better error for missing merge-base: "Could not find merge-base with {branch}"

Evidence: Web review option (search for `"Review in Claude Code on the web"`), progress tracking (search for `"Track progress"`)


### Hook Conditional Filtering via `if` Field

What: Hooks now support an `if` field that uses permission rule syntax to filter when the hook runs, avoiding unnecessary hook execution for non-matching commands.

Usage:
```json
{
  "hooks": {
    "PreToolUse": [{
      "if": "Bash(git *)",
      "command": "my-git-hook.sh"
    }]
  }
}
```

Details:
- The `if` field accepts permission rule syntax (e.g., `"Bash(git *)"`)
- Hooks only fire when the tool call matches the pattern
- Non-matching tool calls skip the hook entirely: "Skipping hook due to if condition not matching"
- If the `if` condition cannot be evaluated for non-tool events, a diagnostic is logged
- When a hook's condition is satisfied, interaction results are tracked (including deny rule overrides and ask rule prompts)

Evidence: Hook schema description (search for `"Permission rule syntax to filter when this hook runs"`)


### Enterprise Plugin Policy Enforcement

What: Organization administrators can now block specific plugins via enterprise policy, preventing installation and enablement.

Details:
- Plugins can be blocked directly: "Plugin {name} is blocked by your organization's policy and cannot be installed"
- Plugin dependencies can be blocked: "Cannot install {name}: dependency {dep} is blocked by your organization's policy"
- Enabled plugins can be blocked: "Plugin {name} is blocked by your organization's policy and cannot be enabled"
- MCP server blocking now shows explicit warnings: "Warning: MCP server(s) blocked by enterprise policy: {names}"
- Claude.ai MCP servers also show warnings when blocked: "Warning: claude.ai MCP server(s) blocked by enterprise policy: {names}"
- Terminology standardized from "managed policy" to "enterprise policy"

Evidence: Plugin blocking messages (search for `"blocked by your organization's policy"`)


### Upstream Proxy for Remote Sessions

What: Remote Claude Code sessions can now route traffic through an upstream WebSocket proxy with automatic CA certificate management.

Details:
- Activated when `CCR_UPSTREAM_PROXY_ENABLED` and `CLAUDE_CODE_REMOTE` environment variables are set
- Reads session tokens from `/run/ccr/session_token`
- Connects to the proxy via `/v1/code/upstreamproxy/ws` WebSocket endpoint
- Fetches CA certificates from `/v1/code/upstreamproxy/ca-cert`
- Includes `Proxy-Authorization` header support
- Relay listener starts on `127.0.0.1` for local proxying
- Comprehensive error handling and logging with `[upstreamproxy]` prefix

Evidence: Upstream proxy initialization (search for `"[upstreamproxy] enabled on 127.0.0.1"`)

### Bash Tool Security Hardening

Several new security checks have been added to the Bash tool's command validation, particularly for Windows/PowerShell:

- **WMI process spawning detection**: Commands that "can spawn arbitrary processes via WMI/CIM (Win32_Process Create)" are now flagged for manual approval
- **Glob pattern symlink validation**: "Glob patterns in paths cannot be statically validated — symlinks inside the glob expansion are not examined"
- **Archive + git exploit prevention**: "Compound command extracts an archive and runs git. Archive contents may plant bare-repository indicators (HEAD, hooks/, refs/) that git then treats as the repository root"
- **Filesystem link creation blocking**: "Compound command creates a filesystem link (New-Item -ItemType SymbolicLink/Junction/HardLink) — cannot auto-allow because path validation cannot follow just-created links"
- **New-PSDrive directory change detection**: Added to the compound command directory-change check alongside Set-Location, Push-Location, and Pop-Location
- **Command length validation**: Input length limits now measured in bytes with explicit error message
- **Windows archive tools**: `bsdtar.exe` and `gunzip.exe` added to the allowed archive tool list

Evidence: WMI check (search for `"can spawn arbitrary processes via WMI/CIM"`), glob check (search for `"Glob patterns in paths cannot be statically validated"`)


### PowerShell Parser Timeout Handling

The PowerShell parser now has a dedicated `PwshTimeout` error class. When `pwsh` times out, the error message reports: "pwsh timed out after {N}ms (2 attempts)", indicating that retries are now built into the timeout logic.

Evidence: Timeout error (search for `"PwshTimeout"`)


### File Index Migrated to Pure JavaScript

The file indexing system has been completely rewritten from a synchronous native Rust module (`file-index.node`) to an asynchronous pure JavaScript implementation. The new `loadFromFileListAsync()` method returns `{ queryable: Promise, done: Promise }`, allowing the UI to remain responsive during index rebuilds. Log messages now reference generic "index" instead of "Rust index".

Evidence: Async file index (search for `"[FileIndex] rebuilt index with"`)


### Native Module and WASM Removal

Multiple native and WASM dependencies have been removed in favor of pure JavaScript implementations:
- `color-diff.node` native module removed — syntax highlighting diff now uses JS-based approach
- `resvg.wasm` SVG rendering module removed entirely
- `index_bg.wasm` removed
- `initWasm()` initialization infrastructure removed
- Monokai Extended theme added as a new syntax highlighting option

Evidence: WASM removal (search for `"resvg"` in v2.1.84 — absent from v2.1.85)


### Connection Resilience for Stale Connections

API request retries now detect stale connections (ECONNRESET/EPIPE) and automatically disable HTTP keep-alive for the retry attempt. This is controlled by the `tengu_disable_keepalive_on_econnreset` feature flag and prevents repeated failures on dead TCP connections.

Evidence: Stale connection handling (search for `"Stale connection (ECONNRESET/EPIPE)"`)


### Compaction Retry Mechanism

When conversation compaction fails (e.g., due to token limits), the system now retries with a truncated conversation prefixed with "[earlier conversation truncated for compaction retry]". This improves reliability of long conversations that need compaction.

Evidence: Compaction retry (search for `"compaction retry"`)


### Enhanced Link-Supplied Prompt Display

When a link supplies a long prompt that exceeds the viewport height, users now see a character count and explicit scroll instruction: "The prompt below ({N} chars) was supplied by the link — scroll to review the entire prompt before pressing Enter."

Evidence: Long prompt display (search for `"scroll to review the entire prompt"`)


### Worktree Support for Non-Git VCS

The `--worktree` flag now provides a clear error and migration path for non-git repositories: "Configure a WorktreeCreate hook in settings.json to use --worktree with other VCS systems."

Evidence: Worktree hook suggestion (search for `"Configure a WorktreeCreate hook"`)


### Background Agent Resume Error Handling

Background agent resumption now has dedicated error handling and user notifications. When an agent fails to resume, a notification is shown with the error details rather than silently failing.

Evidence: Resume error handling (search for `"resumeAgentBackground failed"`)


### Ultraplan Phase Status Display

The ultraplan status indicator now shows distinct states: "ultraplan ready", "ultraplan needs your input", and a generic "ultraplan" state, giving users better visibility into where their review plan stands.

Evidence: Ultraplan phases (search for `"ultraplan needs your input"`)


### Background Post-Turn Summaries

A new internal summarization mechanism emits a background summary after each assistant turn, with a `summarizes_uuid` field pointing to the message being summarized. This infrastructure supports future conversation intelligence features.

Evidence: Post-turn summary (search for `"Background post-turn summary"`)


### MCP Server Policy Documentation

The `allowedMcpServers` setting description has been enhanced to clarify that it "applies to all scopes including enterprise servers from managed-mcp.json" and that "denylist takes precedence — if a server is on both lists, it is denied."

Evidence: Enhanced description (search for `"Denylist takes precedence"`)

## Bug Fixes

- Fixed the `ConstrainedLanguage` allowlist check to cover both `New-Object` .NET type instantiation and direct command invocations in PowerShell (search for `"ConstrainedLanguage allowlist"`)
- Improved `ensureToolResultPairing` to refuse synthetic placeholder injection when repair would corrupt model context: "See inc-4977" (search for `"See inc-4977"`)
- Enhanced step-up authentication tracking with "Marked step-up pending" logging for better debugging of auth state transitions (search for `"Marked step-up pending"`)
- Removed the `tengu_grey_wool` feature flag and associated legacy model remapping logic controlled by `CLAUDE_CODE_DISABLE_LEGACY_MODEL_REMAP`

### Built-in MCP Server Toggle [Gradual Rollout]

What: A mechanism to toggle built-in MCP servers on/off.

Status: Feature-flagged behind `tengu_builtin_mcp_toggle`.

Details:
- Tracks the server name and whether it's being enabled or disabled
- Related to managing a `disabledMcpServers` list in application state
- When enabled, users will be able to selectively disable built-in MCP servers

Evidence: MCP toggle tracking (gated by `tengu_builtin_mcp_toggle`, search for `"disabledMcpServers"`)


### Scheduled Task Execution [Gradual Rollout]

What: Infrastructure for running scheduled tasks with timestamp logging.

Status: Present in code with "Running scheduled task" display.

Details:
- Displays "Running scheduled task ({timestamp})" when executing
- Suggests a future capability for timed/recurring agent operations

Evidence: Scheduled task display (search for `"Running scheduled task"`)
