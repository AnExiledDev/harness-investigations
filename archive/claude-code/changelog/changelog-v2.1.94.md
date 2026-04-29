# Changelog for version 2.1.94

## Summary

This release adds Amazon Bedrock (Mantle) as a new backend provider, introduces the `--thinking-display` CLI flag for controlling how thinking content appears, and substantially enhances the autofix-pr feature with full PR monitoring UI. Memory system improvements include a new "Dream" mode for background memory pruning/consolidation, tiny memory mode, and LLM-based memory synthesis. A new `/team-onboarding` command (feature-flagged) generates team ramp-up guides, and several quality-of-life improvements land around tmux/screen terminal detection, macOS Keychain diagnostics, and settings validation error reporting.


## New Features


### --thinking-display CLI Flag

What: New CLI option to control how model thinking content is rendered in output.

Usage:
```bash
claude --thinking-display summarized
claude --thinking-display omitted
```

Details:
- Choices: `summarized` or `omitted`
- Complements the existing `--thinking` flag (which controls `enabled`, `adaptive`, `disabled`)
- Allows users to get thinking benefits without verbose output

Evidence: CLI option definition (search for `"--thinking-display"`)


### Amazon Bedrock (Mantle) Provider

What: New backend provider option enabling Claude Code to connect through Amazon Bedrock's managed Mantle service.

Usage:
```bash
export CLAUDE_CODE_USE_MANTLE=1
claude
```

Details:
- Set `CLAUDE_CODE_USE_MANTLE` to enable the Mantle provider
- Additional env vars: `ANTHROPIC_BEDROCK_MANTLE_BASE_URL`, `ANTHROPIC_BEDROCK_MANTLE_API_KEY`, `CLAUDE_CODE_SKIP_MANTLE_AUTH`
- Uses `bedrock-mantle` as the service name with SigV4 authentication
- Supports explicit AWS credentials or the standard AWS credential provider chain
- Base URL pattern: `https://bedrock-mantle.{region}.api.aws/anthropic`
- Mantle endpoints added to all model deployment configurations
- Provider detection centralised into a single function that handles Mantle alongside existing providers (Bedrock, Vertex, Foundry)
- The `ANTHROPIC_BEDROCK_MANTLE_API_KEY` is treated as sensitive and masked in logs

Evidence: Provider configuration (search for `"Amazon Bedrock (Mantle)"`, `"CLAUDE_CODE_USE_MANTLE"`, `"bedrock-mantle"`)


### Autofix PR — Full Implementation

What: The `autofix-pr` command has been upgraded from a registered task name to a fully implemented feature with a React-based UI, PR validation, and remote session management.

Usage:
```
/autofix-pr
```

Details:
- Spawns a remote Claude Code session that monitors the current PR for CI failures and review comments, then pushes fixes directly
- Validates PR eligibility: checks the current branch is not the default branch, verifies a remote is set, and detects an open PR via `gh pr view`
- Warns if there are unpushed local commits: "WARNING: You have unpushed local commits, run git push so the remote session sees them"
- Communicates with the bridge API at `/v1/code/github/subscribe-pr` and `/v1/code/github/unsubscribe-pr`
- Tracks telemetry events: `tengu_autofix_pr_started`, `tengu_autofix_pr_result` (success/failed/cancelled)
- Requires `allow_remote_sessions` policy to be enabled
- Shows progress UI: "Detecting open PR for current branch…", "Spawning remote Claude Code session…", "Spawned remote autofix PR session on {host} (PR #{number})"

Evidence: Autofix PR component (search for `"Autofix PR"`, `"Detecting open PR for current branch"`, `"subscribe-pr"`)


### Memory Dream Mode (Background Pruning & Consolidation)

What: New "Dream" system that automatically prunes and consolidates memory files in the background between sessions.

Details:
- Two dream modes:
  - Pruning: "delete stale or invalidated memories, and collapse duplicates"
  - Consolidation: "synthesize what you've learned recently into durable, well-organized memories"
- User setting: `autoDreamEnabled` (boolean) — "Enable background memory consolidation (auto-dream). When set, overrides the server-side default."
- Default thresholds: minimum 24 hours and 5 sessions between dreams (configurable via server flag)
- Memory files are treated as immutable — combining means deleting old files and writing fresh single-fact replacements
- Tool constraints during dream: Bash restricted to read-only commands plus `rm` for `.md` files inside the memory directory
- Existing `autoDreamEnabled` setting existed in v2.1.92 but the Dream prompts and pruning/consolidation logic are new

Evidence: Dream instructions (search for `"Dream: Memory Pruning"`, `"autoDreamEnabled"`, `"tengu_onyx_plover"`)


### LLM-Based Memory Synthesis

What: New memory retrieval path that uses an LLM to synthesize relevant memories into a single paragraph, replacing the previous raw-file retrieval approach.

Details:
- When tiny memory mode (`tengu_billiard_aviary`) is active, uses LLM synthesis to produce contextually relevant memory summaries
- System prompt instructs: "synthesize information directly relevant to" the current query
- Output formatted as JSON with a one-paragraph synthesis
- Recalled memories shown to users with: "Recalled from your persistent memory system:"
- Synthesis memories are excluded from the standard memory context to avoid duplication

Evidence: Memory synthesis (search for `"Synthesize memory information relevant to"`, `"synthesizeRelevantMemories"`)


### Agentic Search — Session ID Extraction

What: Refactored agentic search now returns structured `session_ids` arrays instead of prose-based responses, making session search results more reliable.

Details:
- Search agent returns JSON: `{"session_ids": ["<uuid>", ...]}`
- Response parsed via regex: `/"session_ids"\s*:\s*(\[[^\]]*\])/g`
- Logs "Agentic search: no session_ids array in final response" when extraction fails
- Session metadata display now includes tag, git branch, and project path (formatted via new `uCY` helper)
- Search prompt refactored with separate system prompt constant for better maintainability

Evidence: Session ID extraction (search for `"session_ids"`, `"Agentic search: no session_ids array"`)


### chat:clearInput Keybinding

What: New keyboard shortcut to clear the current chat input field.

Usage: `Ctrl+L` (or `Cmd+L` on macOS)

Details:
- Event name: `chat:clearInput`
- Joins existing chat keybindings: `Escape` (cancel), `Ctrl+X Ctrl+K` (kill agents), `Meta+P` (model picker), `Meta+O` (fast mode), `Meta+T` (thinking toggle), `Enter` (submit)

Evidence: Keybinding definition (search for `"chat:clearInput"`)


### macOS Keychain Diagnostics

What: New keychain probe during `claude doctor` that tests whether the macOS Keychain is writable and provides actionable fix suggestions.

Details:
- Probes keychain write access during initialisation when `probeKeychain: true` is passed
- New error messages:
  - "macOS Keychain is not writable"
  - "Failed to save API key to macOS Keychain"
- Fix suggestion: "Run: security unlock-keychain ~/Library/Keychains/login.keychain-db"
- Keychain operations now have explicit 5-second timeout and stderr-based error detection
- Probe service name: `"Claude Code-doctor-probe"`

Evidence: Keychain probe (search for `"macOS Keychain is not writable"`, `"Claude Code-doctor-probe"`, `"probeKeychain"`)


### Settings Parse and Validation Error Reporting

What: Settings files that fail to parse or validate are now reported with structured error information instead of being silently skipped.

Details:
- New structured error fields: `path` (dot-notation to field), `message` (human-readable), `severity` (set to `"warning"`)
- Settings errors section: "Settings parse and validation errors. When non-empty, the listed files were skipped during the merge above — their settings are not reflected in `effective` or `sources`."
- Error types include invalid JSON, JSON comments, and schema mismatches
- File path of the failing settings file is included in error output

Evidence: Settings validation (search for `"Settings parse and validation errors"`, `"severity"`)


### Session Title Hook

What: Hooks can now set the session title programmatically, enabling automated title assignment based on conversation content.

Details:
- New hook handler applies session title updates with sanitization
- Titles sanitized: control characters removed, limited to 200 characters
- Emits event after title update so UI stays in sync
- Log message: "Hook sessionTitle applied"

Evidence: Session title hook (search for `"Hook sessionTitle applied"`, `"type\":\"custom-title\""`)


## Improvements


### Enhanced tmux Terminal Detection

Terminal detection in tmux sessions now queries the actual terminal type via `#{client_termtype}` instead of relying solely on the `TERM` environment variable. This enables better color support and escape sequence handling when running inside tmux.

Evidence: tmux display-message query (search for `"#{client_termtype}"`)


### Screen (STY) Escape Sequence Fix

Escape sequences for the GNU Screen terminal multiplexer now correctly wrap content using DCS passthrough (`\x1BP...\x1B\\`) with proper double-escaping of embedded escape characters. Previously this wrapping could produce malformed sequences.

Evidence: STY escape handler (search for `process.env.STY`)


### Improved API Error Classification

HTTP error codes are now mapped to user-friendly status messages in the retry UI:
- 429 → "Rate limited"
- 529 → "API overloaded" (new)
- 401/403 → "Authentication error"

The retry display shows the error reason, retry countdown timer, and attempt number in a structured warning frame.

Evidence: Error mapping function (search for `"API overloaded"`, `"Rate limited"`)


### /feedback Command Authentication Check

The `/feedback` command now checks for valid Anthropic credentials before attempting to submit. If no OAuth token or API key is found, it returns: "/feedback requires Anthropic credentials (OAuth or API key)."

Evidence: Feedback auth check (search for `"/feedback requires"`)


### Team Memory Sync — Forbidden Error Handling

Team memory sync now explicitly detects HTTP 403 responses and returns "Forbidden by server policy" with `skipRetry: true` and `errorType: "forbidden"`, preventing futile retry loops when server policy blocks access.

Evidence: Forbidden handling (search for `"Forbidden by server policy"`)


### Feedback Payload Size Validation

Feedback submissions now validate payload size before sending (8 MB limit). If the payload exceeds the limit or the server returns 413, the error is surfaced as `payloadTooLarge` rather than a generic failure.

Evidence: Payload validation (search for `"payloadTooLarge"`)


### WebSocket Decompression Bomb Protection

WebSocket message handling now tracks cumulative decompressed size and enforces a `maxDecompressedMessageSize` limit (default 4 MB). Messages exceeding this limit are rejected with `"Max decompressed message size exceeded"`.

Evidence: Decompression protection (search for `"maxDecompressedMessageSize"`)


### UTF-8 Encoding for stream-json Input

The `stream-json` input mode now explicitly sets UTF-8 encoding on `process.stdin`, preventing encoding issues that could corrupt multi-byte characters.

Evidence: Encoding fix (search for `"stream-json"` near `"utf-8"`)


### Terminal Hyperlink Detection Enhancement

Hyperlink support detection now uses the `supports-hyperlinks` library with `FORCE_HYPERLINK` environment variable support, replacing the previous raw stdout capability check.

Evidence: Hyperlink detection (search for `"supportsHyperlink"`, `"FORCE_HYPERLINK"`)


### Plugin Bin Path Security

Plugin bin directories are now validated against shell metacharacters before being added to PATH. Paths containing dangerous characters are dropped with a warning: "Dropping plugin bin path with shell metacharacters."

Evidence: Bin path security (search for `"Dropping plugin bin path with shell metacharacters"`)


### Memory System — Immutability Enforcement

Memory files are now explicitly treated as immutable across the system. Edit and Write tools are blocked for memory paths with the message: "is not permitted — memories are immutable, so delete-and-recreate replaces in-place edits." In tiny memory mode, the restriction is phrased as: "is not permitted in tiny memory mode — memories are immutable, so delete via Bash rm and rewrite."

Evidence: Memory immutability enforcement (search for `"memories are immutable"`)


### Improved Memory Save Instructions

Memory save guidance has been significantly expanded with:
- Each memory file should contain one paragraph about a single fact
- Frontmatter format with type, scope, and created date
- Instructions to check for duplicates before writing
- Separate scope guidance for private vs team memories
- Delete-and-recreate workflow instead of in-place edits

Evidence: Memory documentation (search for `"Each memory file should contain one paragraph"`)


### Model Restart Notification

When changing models, Claude Code now shows "Restarting Claude Code to apply the new model…" and automatically relaunches, rather than requiring a manual restart.

Evidence: Restart message (search for `"Restarting Claude Code to apply the new model"`)


### Hook Validation — Environment Variable Checks

Hook commands now validate that environment variable references (`${...}`) match the correct variables available for that hook type. Invalid references produce warnings during validation.

Evidence: Hook env var validation (search for `"Hook command references ${"`)


### Skill Name Sanitization

Skill names from plugins are now sanitized by removing invalid characters and replacing them with hyphens (`[^a-zA-Z0-9_-]` → `-`), preventing registration failures from names with special characters.

Evidence: Skill name sanitization (search for `"[^a-zA-Z0-9_-]"`)


### Updated Task/Agent Tool Documentation

The Task tool's system prompt has been condensed and reorganised. The "When NOT to use" section is now streamlined, examples are updated, and the `isolation: "worktree"` option and agent resumption via `to` field are better documented.

Evidence: Task tool help (search for `"Launch a new agent to handle complex, multi-step tasks"`)


## Bug Fixes

- Fixed UTF-8 encoding for `stream-json` input mode to prevent multi-byte character corruption (search for `"stream-json"` near `"utf-8"`)
- Fixed escape sequence handling in GNU Screen (STY) terminal multiplexer — properly wraps DCS passthrough sequences with double-escaped embedded escapes (search for `process.env.STY` in `tD` function)
- Fixed PATH extraction on Windows to use shell-aware subprocess for correct environment resolution (search for `h1Y`)
- Added defensive guard in team memory watcher to check identifier existence before processing, preventing potential crashes (search for `"team-memory-watcher: suppressing retry"`)
- Session title updates now emit events to keep the UI synchronized (search for `"rA7.emit()"`)


## In Development

Features with infrastructure added but not yet enabled. These are shipped "dark" and may become available in future versions.


### /team-onboarding Command [Gradual Rollout]

What: Generates team onboarding guides by analysing your Claude Code usage patterns across sessions, then produces a shareable guide for teammates.

Status: Feature-flagged via `tengu_flint_harbor` (default: false). Can also be enabled with `CLAUDE_CODE_TEAM_ONBOARDING=1`.

Details:
- Scans session transcripts for usage metrics: slash commands, MCP servers, project patterns
- Generates markdown onboarding guide with team-specific recommendations
- Uses allowed tools: `Edit(ONBOARDING.md)` and `Bash(ls:*)`
- Shows progress: "scanning usage data"
- Discovery variant controlled by `tengu_cedar_inlet` flag
- Custom prompt/template configurable via `tengu_flint_harbor_prompt`
- Onboarding banner visible to users: "On a team? Ask a teammate to run /team-onboarding and share the guide."

Evidence: Command definition (search for `"team-onboarding"`, `"tengu_flint_harbor"`)


### Tiny Memory Mode [Gradual Rollout]

What: Alternative memory storage mode that uses a separate `tiny_memory` directory with reduced footprint and LLM-based synthesis for retrieval.

Status: Feature-flagged via `tengu_billiard_aviary` (default: false).

Details:
- When enabled, memory directory switches from `memory` to `tiny_memory`
- Memory files get YAML frontmatter timestamps (`created:`, `last_read:`)
- Read-only shell commands and `rm` for `.md` files only are permitted during memory operations
- Memory retrieval uses LLM synthesis instead of raw file contents
- Team memory paths are excluded from tiny memory mode
- Timestamp stamping: `tinyMemoryStamps` tracks file modification

Evidence: Feature flag and directory selection (search for `"tengu_billiard_aviary"`, `"tiny_memory"`)


## Notes

The XML/DOM parsing library has been replaced. The previous `xmldom`-based parser (with error messages like "end tag name: X is not complete", "unclosed xml attribute", etc.) has been swapped for a new implementation with W3C-compliant DOM exceptions (DOMException types like `HierarchyRequestError`, `InvalidCharacterError`, `NamespaceError`, etc.) and stricter validation. This is an internal change but may surface different error messages if XML parsing is used by MCP servers or plugins.

Several Smithy/AWS SDK utility modules (`FetchHttpHandler`, `buildQueryString`, `escapeUri`, `fromBase64`, `toBase64`, etc.) have been removed as standalone CommonJS modules and replaced by native implementations, reducing bundle size.
