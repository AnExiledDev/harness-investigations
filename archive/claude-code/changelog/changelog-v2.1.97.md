# Changelog for version 2.1.97

## Summary

This release removes the Buddy/Companion feature entirely, adds a new `/dream` slash command for manual and scheduled memory consolidation, introduces a "brief transcript" view mode and several new configuration options, improves CJK language support for mentions and slash commands, adds Cedar policy language syntax highlighting, and strengthens Bash tool security against network redirections and unsafe environment variables.


## New Features


### `/dream` Slash Command [Gradual Rollout]

What: A new user-invocable slash command for reflective memory consolidation — reviewing recent activity, synthesizing learnings into typed memory files, and pruning stale entries.

Usage:
```bash
# Manual consolidation
/dream

# Schedule nightly consolidation
/dream nightly
```

Details:
- Aliases: `/learn`
- Manual mode (`/dream` or `/dream consolidate`) runs an immediate memory consolidation pass
- Schedule mode (`/dream nightly`) sets up a recurring cron job that runs consolidation overnight
- The schedule persists across sessions (written to `.claude/scheduled_tasks.json`) and auto-expires after a configurable period
- Cancel scheduled consolidation at any time
- Gated behind the `tengu_kairos_dream` feature flag — availability may vary
- Previously, only the background auto-dream mechanism existed (silently consolidating between sessions); this command gives users direct control

Evidence: Skill registration with `name: "dream"`, `aliases: ["learn"]` (search for `"Reflective memory consolidation"`) — `WKA` at line ~636587


### Brief Transcript View Mode

What: A new condensed transcript display that collapses sequential tool-use messages into compact summaries showing tool counts and line-change statistics.

Details:
- When enabled, back-to-back tool calls between user prompts are collapsed into a single summary line (e.g., "5 reads, 2 edits, +40/-12 lines")
- Individual tool categories tracked: read, search, bash, edit, git, MCP, hooks, and more
- Togglable at runtime via the transcript UI
- New `briefTranscript` state property controls the display mode

Evidence: Message collapsing function `bd4` produces `collapsed_read_search` and `grouped_tool_use` objects (search for `"collapsed_read_search"`)


### `viewMode` Configuration Setting

What: A new setting to control the default transcript view mode on startup.

Usage:
```json
{
  "viewMode": "default"
}
```

Details:
- Options: `"default"`, `"verbose"`, `"focus"`
- Set in your configuration file to control how the conversation transcript is displayed each time you launch Claude Code

Evidence: Schema definition `viewMode: y.enum(["default", "verbose", "focus"])` (search for `"Default transcript view mode on startup"`)


### `refreshInterval` for Status Line

What: A new configuration option to re-run status line commands at a regular interval, in addition to event-driven updates.

Usage:
```json
{
  "statusLine": {
    "refreshInterval": 30
  }
}
```

Details:
- Value is in seconds (minimum: 1)
- Useful for status line commands that show time-varying data (e.g., build status, clock)

Evidence: Schema definition `refreshInterval: y.number().min(1).optional()` (search for `"Re-run the status line command every N seconds"`)


### Cedar Policy Language Syntax Highlighting

What: Code blocks written in the Cedar policy language are now syntax-highlighted in Claude Code output.

Details:
- Recognizes `cedar` and `cedarpolicy` as language identifiers in fenced code blocks
- Highlights keywords (`permit`, `forbid`, `when`, `unless`, `if`, `then`, `else`), built-in types (`principal`, `action`, `resource`, `context`), and standard Cedar constructs
- Cedar is Amazon's authorization policy language — useful when working with AWS Verified Permissions or custom Cedar policies

Evidence: Language definition with `name: "Cedar"`, `aliases: ["cedarpolicy"]` (search for `"permit forbid when unless if then else in has like is"`)


### `--session-mirror` Flag (SDK Internal)

What: A new CLI flag that enables transcript mirroring on stdout for SDK consumers.

Details:
- Emits `transcript_mirror` frames on the stdout JSON stream after each successful local transcript write
- Designed for use by `ProcessTransport` when a `sessionStore` is configured — allows the parent process to capture and batch transcript entries
- New `transcript_mirror` event type added to the SDK schema
- Not intended for direct user invocation; primarily benefits SDK/API integrations

Evidence: CLI flag `"--session-mirror"` with description `"Emit transcript_mirror frames on stdout"` (search for `"transcript_mirror"`)


### `excludeDynamicSections` SDK Option

What: A new SDK configuration option that omits per-user dynamic sections from the cached system prompt.

Details:
- When `true`, working directory, auto-memory path, and other user-specific content are excluded from the system prompt and re-injected as the first user message instead
- Lets cross-user prompt caching hit on a shared static prefix, significantly improving cache efficiency in multi-tenant deployments
- New `redirectedContextTokens` field in the token usage response tracks how many tokens were redirected

Evidence: Schema property with full description (search for `"omit per-user dynamic sections"`)


## Improvements


### Buddy/Companion Feature Removed

The entire Buddy/Companion system has been removed from Claude Code. This includes:
- The `/buddy` command and companion creature generation
- ASCII art companion display with species, hats, eyes, and rarity tiers
- The companion reaction system that watched conversations and commented in speech bubbles
- The companion mute/unmute toggle in the footer
- The `companion_intro` dynamic section in system prompts
- The buddy teaser notification ("Hatch a coding buddy") that prompted users to try `/buddy`
- The LLM-powered companion personality generation using Claude API
- The "Voice mode is now available" static footer notice (replaced by a tip — see below)

Evidence: Removed functions include `hn8` (buddy_react API), `eE_` (creature generation), `w34` (companion_intro), `tcK` (conversation watcher) — search for `"buddy_react"` in v2.1.96 only


### CJK Punctuation Support for Mentions and Slash Commands

`@mentions` and `/commands` now recognize Chinese, Japanese, and Korean sentence-ending punctuation (`。`, `、`, `？`, `！`) as valid word boundaries. Previously, typing `@filename` or `/command` immediately after CJK punctuation would not be recognized.

Evidence: Regex patterns updated from `/(^|\s)/` to `/(^|[\s。、？！])/` in mention and slash command parsers (search for `"。、？！"`)


### Zellij Terminal Multiplexer Detection

Claude Code now detects the Zellij terminal multiplexer environment and reports it alongside TMUX and TERM_PROGRAM in diagnostic output. Some terminal features are gated to avoid conflicts with Zellij's own input handling.

Evidence: New check `process.env.ZELLIJ` (search for `"ZELLIJ"`) — `qk_` at line ~199074


### Warp Terminal Support Expanded

Warp Terminal (`WarpTerminal`) has been added to an additional terminal capability detection list, extending its integration beyond the existing bundle ID mapping and display name.

Evidence: `"WarpTerminal"` appears in a new terminal identifier array in v2.1.97 (search for `"WarpTerminal"`)


### Voice Notice Replaced with Contextual Tip

The persistent "Voice mode is now available · /voice to enable" footer notice has been replaced with a contextual tip (`"Use /voice to enable push-to-talk dictation"`) that respects cooldown sessions and relevance checks. This reduces visual noise for users who don't use voice mode.

Evidence: New tip with `id: "voice-mode"`, `cooldownSessions: 10` (search for `"Use /voice to enable push-to-talk dictation"`)


### Bash Tool Security: `/dev/tcp` and `/dev/udp` Blocking

Redirections targeting `/dev/tcp` or `/dev/udp` are now explicitly blocked as network connections. These Bash pseudo-device paths open network sockets and were previously not flagged by the safety checker.

Evidence: New safety message `"Redirect involving /dev/tcp or /dev/udp opens a network connection"` (search for `"/dev/tcp"`)


### Bash Tool: Environment Variable Validation

The Bash tool now validates environment variable names in command prefixes using a regex pattern (`/^([A-Za-z_][A-Za-z0-9_]*)/`) and checks them against a safe-list. Commands that set non-safe-listed environment variables require explicit approval.

Evidence: New function `fhz` with env var validation regex and `Ly6` safe-list checker (search for `"A-Za-z_][A-Za-z0-9_]*"`)


### Bash Tool: Expanded Argument Parsing

The Bash argument parser now handles additional flags for `cut`, `paste`, `column`, and `awk` commands, properly stripping their flag arguments to extract positional file paths for safety analysis.

Evidence: New `lF1` flag-stripping function factory with `--delimiter`, `--output-delimiter`, `--field-separator` support (search for `"--delimiter"`)


### Conversation Branching Size Limit

Conversation branching now validates the transcript file size before attempting to create a branch. If the transcript exceeds the size limit, a clear error message is shown: "Conversation transcript is too large to branch."

Evidence: Size check in `QFK` (search for `"Conversation transcript is too large to branch"`)


### Improved Compaction Error Messages

Compaction failure messages are now more specific:
- "Compaction failed · attached media exceeds size limits" — when media attachments are too large
- "Compaction failed · conversation could not be reduced below the context limit" — when the conversation itself is too long

Evidence: New error strings (search for `"Compaction failed · attached media exceeds size limits"`)


### "Max Effort" Description Updated

The "max" effort level description has been simplified from "Maximum capability with deepest reasoning (Opus 4.6 only)" to just "Maximum capability with deepest reasoning", reflecting that max effort is no longer restricted to Opus 4.6.

Evidence: String change in `$p_` (search for `"Maximum capability with deepest reasoning"`)


### Session Origin Tracking in Memory Files

Memory files written via CLAUDE.md now include an `originSessionId` field in their YAML frontmatter, alongside the existing `created` timestamp. This helps trace which session originally created each memory entry.

Evidence: New frontmatter injection `"originSessionId: "` in function `jE8` (search for `"originSessionId"`)


### Keybinding Components Replace Hardcoded Text

Several UI elements that previously displayed hardcoded text like "Enter to apply", "Esc to go back", and "Ctrl+d to show debug info" now use structured keybinding components that respect custom key mappings. This means users who have remapped keys will see the correct bindings in the UI.

Evidence: Hardcoded `"Enter to apply"` replaced with `J1` component; `"Esc to go back"` replaced with structured `W1` component (search for `"show debug info"` and `"hide debug info"`)


### Improved Hook Evaluator: Transcript Truncation and Model Awareness

Hook evaluators now truncate conversation transcripts to fit within the evaluator's context window and pass the correct model identifier. When truncation occurs, a marker is inserted: "[Earlier conversation truncated to fit the hook evaluator's context window — N earlier messages omitted...]"

Evidence: Function `zQY` with truncation logic (search for `"Earlier conversation truncated to fit the hook evaluator's context window"`)


### "Routines" Configuration Section

A new `"routines"` category has been added to the configuration/help system alongside existing sections like commands and workflows.

Evidence: `"routines"` added to configuration sections list (search for `"routines"`)


### Remote Skills Discovery Tracking

The agent now tracks remotely-discovered skills (e.g., from MCP servers) via a `discoveredRemoteSkills` map, enabling better state management when skills become available or unavailable during a session.

Evidence: New `discoveredRemoteSkills: new Map()` field in agent state (search for `"discoveredRemoteSkills"`)


### Managed Agents API Documentation

Comprehensive documentation for the Managed Agents API has been embedded for the `claude-developer-platform` skill, covering Python, TypeScript, and cURL/HTTP usage with examples for environments, agents, sessions, SSE streaming, custom tool results, and interrupts.

Evidence: Documentation strings including `"anthropic-beta: managed-agents-2026-04-01"` (search for `"Managed Agents"`)


### Agent Inter-Tool Narration Suppression

Sub-agents (e.g., Task agents) now receive an explicit instruction: "Do not emit text between tool calls. Inter-tool narration is never shown to the user — go straight to the next tool call." This reduces wasted tokens on text the user never sees.

Evidence: Instruction string `A9Y` (search for `"Do not emit text between tool calls"`)


### Worktree Branch Creation: `--no-track`

When creating worktree branches, the `--no-track` flag is now passed to prevent automatic upstream tracking, avoiding potential conflicts with remote branches.

Evidence: New `"--no-track"` argument in worktree creation (search for `"--no-track"`)


### Workflow Script File Write Permissions

Files in the `workflows/scripts` directory for the current session are now automatically allowed for writing, removing the need for manual permission approval when Claude generates workflow scripts.

Evidence: Permission reason `"Workflow script files for current session are allowed for writing"` (search for `"Workflow script files"`)


### Upgrade Flow: Conditional "Switch to Team Plan" Label

The upgrade prompt now shows "Switch to Team plan" instead of "Upgrade to Team plan" when the user is already on a plan, providing more contextually accurate wording.

Evidence: Conditional label `X ? "Switch to Team plan" : "Upgrade to Team plan"` (search for `"Switch to Team plan"`)


### Duplicate Key Detection in Virtual Message List

A new diagnostic warning detects duplicate sibling keys in the virtual message list renderer, which could previously cause DOM node leaks via `mapRemainingChildren` overwrite.

Evidence: Warning message `"VirtualMessageList: duplicate sibling keys"` (search for `"VirtualMessageList: duplicate sibling keys"`)


### Read Tool: Absolute Paths Always Required

The Read tool documentation now unconditionally requires absolute file paths. The previous conditional behavior (which sometimes allowed relative paths) has been removed for consistency.

Evidence: Read tool description change — removed conditional `qk6()` check, hard-codes `"must be an absolute path"` (search for `"must be an absolute path"`)


## Bug Fixes

- Fixed unguarded promise chains in Chrome onboarding and session reconnection that could cause unhandled rejections (search for `.catch(w6)` in `K4A` and `ABY`)

- Fixed text input handling: replaced regex-based `.replace(/\r/g, ...)` with `.replaceAll("\r", ...)` and added proper handling for `meta+backspace`, `super+backspace`, `ctrl+backspace`, `meta+delete`, and `super+delete` key combinations (search for `".replaceAll"` in `aQ8`)

- Fixed CRLF line-ending normalization: content is now normalized with `.replace(/\r\n?/g, "\n")` before splitting, preventing blank lines or split errors on Windows-originated text (search for `"\\r\\n?"`)

- Fixed variable reference in text processing: corrected `f6.slice(1)` to `J6.slice(1)`, fixing incorrect text extraction (search for `J6.slice(1)` in `kn4`)

- Added explicit error type checking for `TC6` errors in the error handling cascade, preventing these errors from being swallowed by generic catch blocks (search for `"instanceof TC6"`)

- Fixed permission stripping logic to preserve existing rules and add deduplication when stripping dangerous permissions, preventing accidental rule loss (search for `"strippedD"` in `ex`)

- Stale marketplace backup directories (`.bak`) are now cleaned up alongside the main directory during marketplace refresh (search for `".bak"`)


## In Development

Features with infrastructure added but not yet enabled. These are shipped "dark" and may become available in future versions.


### Subagent Model Downgrade: Opus to Sonnet [In Development]

What: When enabled, this feature automatically downgrades Opus model usage for sub-agents to Sonnet, potentially reducing costs for agentic workflows.

Status: Feature-flagged (disabled by default)

Details:
- Gated behind `tengu_garnet_loom` flag with default `!1` (false)
- When active and the current model includes "opus", it substitutes a Sonnet model
- Likely intended to balance cost vs. capability for Task sub-agents

Evidence: Flag check `R8("tengu_garnet_loom", !1)` that downgrades opus to sonnet (search for `"tengu_garnet_loom"`)


### Bash Allowlist Strip-All Mode [In Development]

What: A mode that strips all bash command allowlist entries from the permission context, effectively requiring re-approval for all bash commands.

Status: Feature-flagged (disabled by default)

Details:
- Gated behind `tengu_bash_allowlist_strip_all` flag with default `!1` (false)
- When enabled, the `stripAllBashFlag` property activates in the permission decision flow
- May be intended as a security hardening measure for sensitive environments

Evidence: Flag `R8("tengu_bash_allowlist_strip_all", !1)` assigned to `stripAllBashFlag` (search for `"tengu_bash_allowlist_strip_all"`)


### Effort Level Clamping [In Development]

What: Infrastructure to cap the maximum effort level based on a model's capability tier, preventing users from setting effort higher than what a model supports.

Status: Feature-flagged (disabled by default)

Details:
- Gated behind `tengu_pyrite_wren` flag with default `!1` (false)
- Compares the requested effort against the model's position in the effort ranking

Evidence: Function `Uz4` gated by `R8("tengu_pyrite_wren", !1)` (search for `"tengu_pyrite_wren"`)


## Notes

The removal of the Buddy/Companion feature is a clean removal with no migration needed — the feature was experimental and self-contained. Any companion state stored in your configuration will simply be ignored.

The new `/dream` command is gated behind a feature flag (`tengu_kairos_dream`) and may not be available to all users immediately. The existing background auto-dream mechanism continues to work independently.

The `claude-sonnet-4-6` model was already present in v2.1.96; this release adds no new model families but refines model capability detection (the `max_effort` resolver now properly handles version-based capability checks for Opus/Sonnet >= 4.6).
