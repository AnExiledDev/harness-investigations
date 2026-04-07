# Changelog for version 2.1.77


## Summary

This release renames `/fork` to `/branch`, adds `/copy N` for accessing earlier responses, introduces a comprehensive remote bridge v2 transport layer for Claude Desktop connectivity, adds local model capabilities caching, and includes a significantly expanded multi-phase `/init` command (behind an environment variable). Under the hood, Axios is upgraded from 1.8.4 to 1.13.4 and many lodash internals have been replaced with lighter native implementations.


### `/branch` Command (renamed from `/fork`)

What: The `/fork` command has been renamed to `/branch` for creating a branched copy of the current conversation. The old `/fork` name is preserved as an alias for backward compatibility.

Usage:
```
/branch
```

Details:
- Creates a branch of the current conversation at the current point
- All user-facing text updated: "Forked conversation" → "Branched conversation", "No conversation to fork" → "No conversation to branch"
- `/fork` still works as an alias — no migration needed
- Error messages updated accordingly: "Failed to branch conversation", "No messages to branch"

Evidence: Slash command definition (search for `"Create a branch of the current conversation"`) — aliases include `"fork"` for backward compat


### Remote Bridge v2 Transport

What: A complete WebSocket-based remote bridge implementation for connecting Claude Code CLI sessions to Claude Desktop, replacing the older SSE-based transport.

Details:
- New WebSocket transport with JWT-based authentication (`worker_jwt`)
- Automatic JWT refresh on 401 errors with transparent transport rebuilding
- Connection status tracking: "Disconnected", "Reconnecting…" states shown in the UI
- Keep-alive heartbeat for session persistence
- Message batching and history flushing on reconnection
- Session creation via `/v1/code/sessions` endpoint
- Session archival support
- Gated by `tengu_bridge_repl_v2` feature flag

Evidence: Remote bridge session manager (search for `"[remote-bridge]"`) — 38+ log messages added; feature flag `tengu_bridge_repl_v2`


### Model Capabilities Caching

What: Model capability definitions are now cached locally in a `model-capabilities.json` file, reducing redundant fetches.

Details:
- Capabilities are written to disk and reused across sessions
- Cache-change detection skips unnecessary writes: `"[modelCapabilities] cache unchanged, skipping write"`
- Graceful fallback on fetch failure: `"[modelCapabilities] fetch failed:"`

Evidence: Cache file handling (search for `"model-capabilities.json"`)


### Sandbox `allowRead` Setting

What: New `allowRead` setting lets administrators re-allow specific read paths within broad `denyRead` regions, and a new `allowManagedReadPathsOnly` flag restricts reads to only policy-approved paths.

Details:
- `allowRead`: array of paths that take precedence over `denyRead`, enabling fine-grained "deny broad, allow narrow" patterns
- `allowManagedReadPathsOnly`: boolean in `policySettings.sandbox.filesystem` — when true, only managed `allowRead` paths are permitted
- Glob expansion supported for `allowRead` patterns
- Logging for re-allowed paths within denied regions

Evidence: Settings schema (search for `"Paths to re-allow reading within denied regions"`) and policy check (search for `"allowManagedReadPathsOnly"`)


### Plugin/Skill Manifest Validation

What: New validation system for skill, agent, and command frontmatter, plus hooks.json schema checking, with clear error and warning messages.

Details:
- Validates YAML frontmatter in `.claude/skills/`, `.claude/agents/`, `.claude/commands/` markdown files
- Checks `description`, `name`, and `allowed-tools` field types
- Warns on missing frontmatter or missing description
- Validates `hooks.json` against the Zod schema
- Enhanced kebab-case enforcement: warns that Claude.ai marketplace sync requires kebab-case names
- Prints validation results with clear indicators for errors and warnings

Evidence: Frontmatter validator (search for `"No frontmatter block found. Add YAML frontmatter"`) and allowed-tools check (search for `"allowed-tools must be a string or array of strings"`)


### `update-config` Skill

What: New built-in skill for configuring Claude Code settings via `settings.json`, with embedded documentation for hooks, permissions, and environment variables.

Details:
- Provides guidance for editing `.claude/settings.json` and `.claude/settings.local.json`
- Includes complete hooks configuration reference with event/matcher tables
- Documents hook construction and verification workflow (7-step process)
- References Full Settings JSON Schema for discoverability

Evidence: Skill definition (search for `"update-config"`) with hooks documentation (search for `"Constructing a Hook"`)


### Full Settings JSON Schema

What: Claude can now output the complete JSON schema for all Claude Code settings, making settings discovery easier.

Evidence: Schema header (search for `"## Full Settings JSON Schema"`)


### `/copy N` — Copy Earlier Responses

The `/copy` command now accepts an optional numeric argument to copy earlier assistant responses, not just the most recent one.

Usage:
```
/copy       # copies latest response (same as before)
/copy 2     # copies second-most-recent response
/copy 3     # copies third-most-recent response
```

Details:
- Description updated: "Copy Claude's last response to clipboard (or /copy N for the Nth-latest)"
- Validates the argument: shows usage hint for invalid input
- Reports when there aren't enough messages: "Only N assistant messages available to copy"

Evidence: Updated command description (search for `"or /copy N for the Nth-latest"`)


### Axios Upgraded to 1.13.4

The bundled Axios HTTP client was upgraded from 1.8.4 to 1.13.4. The AxiosError class has been rewritten from a prototype-based pattern to a native ES class, and the CanceledError similarly uses class inheritance.

Evidence: Version constant (search for `"1.13.4"` in the new version vs `"1.8.4"` in the old)


### Lodash Internals Replaced

Many lodash utility functions (ListCache, Stack, MapCache, Hash, deep clone helpers, typed array checks, key enumeration, etc.) have been removed and replaced with lighter native JavaScript implementations. This reduces bundle size without changing external behavior.

Evidence: Structural diff shows ~150+ removed lodash functions (ListCache, MapCache, Hash, Stack prototypes, `baseClone`, `baseAssign`, `baseKeys`, etc.)


### Agent Resume via `SendMessage`

The agent resume mechanism has been updated. Instead of passing a `resume` parameter with an agent ID, agents are now continued by sending a `SendMessage` with the agent's ID or name as the `to` field. The agent resumes with its full context preserved.

Evidence: New text (search for `"with the agent's ID or name as the \`to\` field"`) replacing old `resume` parameter documentation


### Enhanced `/init` Command [Gradual Rollout]

The `/init` command has a significantly expanded multi-phase workflow (gated behind the `CLAUDE_CODE_NEW_INIT` environment variable):

- Phase 1: Choose between project CLAUDE.md, personal CLAUDE.local.md, or both
- Phase 2: Codebase exploration (build/test commands, frameworks, project structure)
- Phase 3: Gap-fill interview with the user, synthesize proposals for hooks/skills/notes
- Phase 4: Write minimal, high-signal CLAUDE.md
- Phase 5: Write personal CLAUDE.local.md (added to `.gitignore`)
- Phase 6: Suggest and create skills in `.claude/skills/`
- Phase 7: Suggest optimizations (GitHub CLI, linting, format-on-edit hooks)
- Phase 8: Summary with plugin recommendations (skill-creator, frontend-design, playwright)

Evidence: Multi-phase flow (search for `"Phase 1: Ask what to set up"`) and env var gate (search for `"CLAUDE_CODE_NEW_INIT"`)


### Installation Deduplication

When multiple install requests are triggered concurrently, subsequent calls now join the in-flight installation rather than starting parallel ones.

Evidence: Dedup logic (search for `"installLatest: joining in-flight call"`)


### Improved Remote Session Status UI

The status line now shows connection state for remote sessions ("Disconnected", "Reconnecting…") and displays a count of active background tasks ("N in background").

Evidence: Status component (search for `"Reconnecting"` near status rendering) and background count (search for `"in background"`)


### Improved Image Error Messages

Empty image files now produce a clearer error: "Image file is empty (0 bytes)" instead of the generic empty-file error.

Evidence: Error message (search for `"Image file is empty (0 bytes)"`)


### Background Command Output Limits

Background commands that exceed output file size limits are now explicitly killed with a descriptive message.

Evidence: New message (search for `"Background command killed: output file exceeded"`)


### Remote Control Error Messages Refined

Remote control error messages have been simplified and made more concise:
- "Remote Control disabled after repeated failures this session. Restart to retry." → "disabled after repeated failures · restart to retry"
- New: "disabled by your organization's policy" for policy-blocked remote control
- "Connection to server lost" → lowercase "connection to server lost"

Evidence: Updated strings in the string diff (search for `"disabled after repeated failures · restart to retry"`)


### Conversation Summary Improvements

The conversation compaction system now has a separate prompt for summarizing only recent messages when earlier context is retained, avoiding redundant re-summarization of already-kept content.

Evidence: New partial summary prompt (search for `"Your task is to create a detailed summary of the RECENT portion"`)


## Bug Fixes

- Fixed potential prototype pollution: Properties starting with `_PROTO_` are now stripped from objects before processing (search for `"_PROTO_"` in the `wE6` function)
- Fixed `apiKeyHelper` error handling: Clearer error messages when API key helper fails or takes too long (search for `"apiKeyHelper failed:"` and `"apiKeyHelper is taking a while"`)
- Data URL byte-size estimation now correctly handles percent-encoded base64 padding characters in data URIs (search for `Lc1` function at line ~37105)


### Enhanced `/init` Multi-Phase Flow [In Development]

Status: Gated behind `CLAUDE_CODE_NEW_INIT` environment variable

What: The expanded 8-phase `/init` flow described above is fully implemented but requires setting `CLAUDE_CODE_NEW_INIT=1` to activate. When unset, the original single-phase `/init` behavior is used.

Details:
- Complete implementation exists including skills setup, hooks creation, and plugin recommendations
- Includes worktree-aware CLAUDE.local.md placement logic
- Skill-creator plugin and frontend-design plugin recommendations baked in
- When enabled, the description changes to: "Initialize new CLAUDE.md file(s) and optional skills/hooks with codebase documentation"

Evidence: Env var check (search for `"CLAUDE_CODE_NEW_INIT"`) — when set, activates the `QBY` prompt template with full Phase 1–8 flow


### Remote Bridge v2 [Gradual Rollout]

Status: Feature-flagged under `tengu_bridge_repl_v2`

What: The WebSocket-based remote bridge described in New Features is gated by a server-controlled feature flag and will roll out gradually.

Evidence: Feature flag checks (search for `"tengu_bridge_repl_v2"`)
