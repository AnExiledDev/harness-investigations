# Changelog for version 2.1.79


## Summary

This release adds a new "Memory consolidation" background task (DreamTask) that automatically reviews recent sessions and updates project memory, introduces a `/web-setup` command for connecting Claude Code to Claude on the web via GitHub, and adds in-transcript text search with `/` in the transcript viewer. It also includes subprocess environment scrubbing for secrets, improved stdin timeout handling, slow hook performance logging, and numerous UI refinements.

### Memory Consolidation (DreamTask)

What: A new background task type called "DreamTask" that automatically consolidates memory by reviewing past sessions. It runs in the background, reviews recent sessions since the last consolidation, and updates memory files with new learnings.

Details:
- Fires automatically based on configurable thresholds (default: 24 hours since last consolidation, minimum 5 sessions)
- Shows a "Memory consolidation" UI panel with real-time status: sessions reviewing, files touched, and running/completed state
- Can be stopped with `x` during execution, which rolls back the lock
- Tracks the `tengu_auto_dream_fired` and `tengu_auto_dream_failed` analytics events
- Restricted to read-only Bash commands (ls, find, grep, cat, stat, wc, head, tail) during execution

Evidence: DreamTask background task system (search for `"DreamTask"` and `"Memory consolidation"`)


### Transcript Search

What: You can now search within the detailed transcript view using `/` to enter search mode, with `n`/`N` to navigate between matches.

Details:
- Press `/` while in transcript view to activate search mode
- Type to filter, results are highlighted with inverse+underline styling
- Press `n` for next match, `N` for previous match
- Press `Esc` to clear the search
- Shows a match counter badge (e.g., "3/12") in the transcript footer

Evidence: Search highlight system with navigation (search for `"n/N to navigate"` and `"searchHighlightQuery"`)


### Web Setup Command

What: A new `/web-setup` command that connects Claude Code to Claude on the web by importing your GitHub credentials, enabling cloud-based sessions.

Details:
- Checks your Claude login status and GitHub CLI authentication
- Prompts for confirmation before uploading your GitHub token
- Creates a default cloud environment provider automatically
- Gated behind the `tengu_cobalt_lantern` feature flag (gradual rollout)
- Shows appropriate error messages for various failure cases: not signed in, GitHub token rejected, server errors, network issues

Evidence: Web setup flow (search for `"Connect Claude on the web to GitHub?"` and `"web-setup"`)


### Subprocess Environment Scrubbing

What: A new `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` environment variable that, when enabled, strips sensitive credentials from the environment passed to subprocesses (like Bash tool invocations).

Usage:
```bash
CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1 claude
```

Details:
- Removes API keys, OAuth tokens, and other secrets from subprocess environments
- Scrubbed variables include: `ANTHROPIC_API_KEY`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `GOOGLE_APPLICATION_CREDENTIALS`, `AZURE_CLIENT_SECRET`, GitHub Actions tokens, and more
- Also scrubs `INPUT_` prefixed variants of all listed variables

Evidence: Environment scrubbing for subprocess execution (search for `"CLAUDE_CODE_SUBPROCESS_ENV_SCRUB"`)


### Memory Verification Instructions

What: New system prompt instructions that teach the model to verify memories against current code before recommending from them. Memories about file paths, functions, or flags may be stale—the model now greps or checks files before acting on recalled information.

Details:
- Added a "Before recommending from memory" section to the memory system prompt
- Instructs the model: "If the memory names a file path: check the file exists", "If the memory names a function or flag: grep for it"
- Emphasizes that '"The memory says X exists" is not the same as "X exists now."'

Evidence: Memory verification guardrails (search for `"Before recommending from memory"` and `"The memory says X exists"`)


### Stdin Timeout Warning

What: When piping input to Claude Code from a slow command, a warning is now shown after 3 seconds if no stdin data has been received, helping users diagnose piping issues.

Details:
- Warns: "Warning: no stdin data received in 3s, proceeding without it. If piping from a slow command, redirect stdin explicitly: < /dev/null to skip, or wait longer."
- Uses a configurable timeout to detect stalled stdin

Evidence: Stdin timeout detection (search for `"no stdin data received in 3s"`)


### Mobile App Summary Labels

What: After tool use, the model is now prompted to generate a short summary label (git-commit-subject style, ~30 characters) suitable for display as a single-line row in a mobile app.

Details:
- Replaces the previous generic "Provide a brief summary of what was accomplished" prompt
- New labels are past-tense, concise, and drop articles/connectors (e.g., "Searched in auth/", "Fixed NPE in UserService", "Created signup endpoint")

Evidence: Mobile-optimized summary labels (search for `"Write a short summary label"`)

### Slow Hook and Permission Logging

Added performance logging that warns when PreToolUse hooks, PostToolUse hooks, or permission decisions take an unusually long time. This helps diagnose slow hook configurations that degrade responsiveness.

Evidence: Performance diagnostics for hooks (search for `"Slow PreToolUse hooks:"`, `"Slow PostToolUse hooks:"`, and `"Slow permission decision:"`)


### Tool Input Coercion for Numeric Parameters

Bash tool's `timeout` parameter and Grep tool's numeric parameters (`-A`, `-B`, `-C`, `context`, `head_limit`, `offset`) now accept string representations of numbers and coerce them to numeric types. This prevents errors when the model passes "5000" instead of 5000.

Evidence: Numeric string coercion wrapper (search for `"oR("` in the Grep and Bash tool schema definitions)


### PDF Reading Error Message Improvement

The error message for unsupported full-PDF reading has been updated from "only supported with the Anthropic API" to "not supported with this model. Use a newer model (Sonnet 3.5 v2 or later)". This gives users clearer guidance on which models support the feature.

Evidence: Model-specific PDF error (search for `"Reading full PDFs is not supported with this model"`)


### User Message Hover Styling

All themes now include a `userMessageBackgroundHover` color, providing visual feedback when hovering over user messages in the transcript.

Evidence: Theme hover colors (search for `"userMessageBackgroundHover"`)


### Dimmed Nested Output Indicators

The `⎿` prefix indicators in tool output and stderr rendering are now displayed with dimmed color (`dimColor: true`), improving visual hierarchy and reducing clutter in dense output.

Evidence: Dimmed output prefix styling (search for `"dimColor"` near `"⎿"`)


### Bash Command Formatting Prefix

Bash commands displayed in the transcript now include a `$ ` prefix, making them visually distinguishable as shell commands.

Evidence: Shell command display prefix (search for `"$ " +` in function `Jn9`)


### SIGINT Handling in Print Mode

SIGINT (Ctrl+C) signals are now ignored when running in `--print` (`-p`) mode, preventing accidental termination during non-interactive pipeline usage.

Evidence: Print mode signal handling (search for `'process.argv.includes("-p")'`)


### Cross-Marketplace Plugin Dependencies

The plugin system now supports `allowCrossMarketplaceDependenciesOn` in marketplace configuration, enabling plugins from one marketplace to declare dependencies on plugins from specified other marketplaces.

Evidence: Cross-marketplace dependency allowlist (search for `"allowCrossMarketplaceDependenciesOn"`)


### Plugin Dependency Resolution Improvements

Plugin dependency specifications now support both string and object formats, with version constraint stripping (`@^version` suffixes are now parsed and removed). Plugin resolution no longer requires a feature flag gate.

Evidence: Enhanced dependency schema (search for `"@\\^[^@]*$"`)


### Event Batch Size Limiting

The event uploader now respects a `maxBatchBytes` limit (10 MB) in addition to `maxBatchSize`, preventing oversized event batches that could fail server-side.

Evidence: Byte-level batch limiting (search for `"maxBatchBytes"`)


### Statusline Trust Check

Status line commands now check workspace trust before executing. If trust hasn't been accepted, a notification is shown: "statusline skipped · restart to fix".

Evidence: Statusline workspace trust validation (search for `"Status line command skipped: workspace trust not accepted"`)


### `git push` Telemetry

Git push operations are now tracked via the `tengu_git_operation` telemetry event (alongside the existing commit, amend, and PR create tracking).

Evidence: Push operation tracking (search for `"git_operation"` near `"push"`)


### Rate Limit Retry Improvements

429 rate limit errors are now retried more aggressively, and the `anthropic-ratelimit-unified-reset` header is parsed to calculate precise backoff delays (capped at 6 hours).

Evidence: Unified rate limit reset parsing (search for `"anthropic-ratelimit-unified-reset"`)


### Conversation Compaction Prompt Updates

The conversation compaction (summary) system now uses a two-prompt approach: one for full conversation summaries and a separate prompt for summarizing only the recent portion of a conversation when earlier context is retained. Both prompts include detailed section structure (Primary Request, Key Technical Concepts, Files, Errors, Problem Solving, User Messages, Pending Tasks, Current Work, Next Step).

Evidence: Dual compaction prompts (search for `"Your task is to create a detailed summary of the RECENT portion"`)


### Removed `process.title` Override

Claude Code no longer sets `process.title = "claude"`, avoiding interference with terminal title management in some environments.

Evidence: Process title removal (search for `process.title` — removed from main entry)


### Prototype Pollution Fix in Axios Config Merge

The Axios config merge utility now rejects `__proto__`, `constructor`, and `prototype` keys, closing a potential prototype pollution vector.

Evidence: Proto key rejection (search for `"__proto__"` near `"constructor"` near `"prototype"`)

## Bug Fixes

- Fixed duplicate entries in plugin hook results by deduplicating the returned array (search for `"new Set(q)"` in function `KuY`)
- Fixed clipboard copy not working on SSH sessions by adding tmux passthrough escape sequence wrapping (search for `"Ptmux"`)
- Fixed a potential issue where non-finite timeout values could cause errors in tool timeout calculation (search for `"Number.isFinite(q)"` in function `Uq4`)
- Fixed resume session message being printed multiple times by adding a guard flag (search for `"iL4"` in function `IC1`)
- Fixed auth error message format to show login instruction before the error details (search for `"Please run /login · "`)
- Fixed nested memory attachments being incorrectly inserted into the middle of message groups instead of being prepended (search for `"nested_memory"`)
- Removed `bridge_metadata` system message type from the message schema, simplifying the bridge protocol

### `--claudeai` CLI Flag [In Development]

What: A new `--claudeai` flag appears alongside a billing selection flow that lets users choose between "Use Anthropic Console (API usage billing)" and "Use Claude subscription (default)".

Status: Feature-flagged — the web-setup flow it ties into is gated behind `tengu_cobalt_lantern` (defaults to false).

Details:
- Error message added: "Error: --console and --claudeai cannot be used together"
- Suggests this is infrastructure for a Claude web/subscription billing path alternative to API key billing

Evidence: Billing mode selection (search for `"--claudeai"` and `"Use Anthropic Console"`)

## Notes

- The JWT library bundled within Claude Code has been replaced: the old multi-file `jwa`/`jws`/`Buffer`-based implementation was removed in favor of a leaner inline version with improved error handling for missing HMAC secrets.
- The `claude-developer-platform` skill content has been significantly updated with new model references (Opus 4.6, Sonnet 4.6), adaptive thinking guidance, compaction documentation, and multi-language SDK support information including Go, Ruby, C#, and PHP.
