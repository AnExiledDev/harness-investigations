# Changelog for version 2.1.81


## Summary

This release introduces a new `RemoteTrigger` tool for managing scheduled remote agents, an `auto-mode critique` CLI subcommand for AI-powered review of custom auto mode rules, MCP channel permissions infrastructure, and configurable shell support for hooks (bash/powershell). It also adds time-based micro-compaction for idle sessions, a user-configurable `autoDreamEnabled` setting, `defaultShell` configuration, worktree state persistence, and new plan-approval UX options including "clear context."

### Auto Mode Rule Critique CLI

What: New `claude auto-mode critique` subcommand that sends your custom auto mode rules to an AI reviewer that evaluates them for clarity, completeness, conflicts, and actionability.

Usage:
```bash
claude auto-mode critique
claude auto-mode critique --model opus
claude auto-mode defaults   # view the default rules for reference
```

Details:
- Reads your custom rules from `autoMode.{allow, soft_deny, environment}` in settings
- Shows the full classifier system prompt alongside your custom rules for context
- AI reviewer comments only on rules that could be improved
- If no custom rules are found, prompts you to add them and use `claude auto-mode defaults` to see defaults

Evidence: Auto mode rule critique command (search for `"Analyzing your auto mode rules"` and `"auto_mode_critique"`)


### Auto-Dream User Setting

What: New user-configurable `autoDreamEnabled` setting that controls background memory consolidation (auto-dream), overriding the server-side default.

Usage: Set `autoDreamEnabled` in your Claude Code settings to `true` or `false`.

Details:
- Description: "Enable background memory consolidation (auto-dream). When set, overrides the server-side default."
- When not set, falls back to the server-controlled `tengu_onyx_plover` feature flag
- Related UI: `· /dream to run` hint shown in interface

Evidence: Auto-dream user setting (search for `"Enable background memory consolidation"` and `"autoDreamEnabled"`)


### Default Shell Setting

What: New `defaultShell` setting to configure the default shell interpreter for input-box `!` commands.

Details:
- Description: "Default shell for input-box ! commands. Defaults to 'bash' on all platforms (no Windows auto-flip)."
- Currently defaults to `"bash"`

Evidence: Default shell config (search for `"defaultShell"` and `"Default shell for input-box"`)


### Shell Type for Hooks

What: Hook frontmatter now accepts a `shell` field to specify the shell interpreter, supporting `'bash'` or `'powershell'`.

Details:
- Description: "Shell interpreter. 'bash' uses your $SHELL (bash/zsh/sh); 'powershell' uses pwsh. Defaults to bash."
- Invalid shell values log a warning and fall back to bash
- PowerShell hooks are not available in all builds of Claude Code — if unavailable, a warning is logged

Evidence: Shell hook support (search for `"shell must be 'bash' or 'powershell'"` and `"Shell interpreter."`)


### Plan Approval Clear Context Option

What: The plan approval dialog now offers a "clear context" option, letting you combine plan approval with context reset.

Details:
- New setting `showClearContext`: "When true, the plan-approval dialog offers a 'clear context' option. Defaults to false."
- When context usage is available, shows percentage: "Yes, clear context (X% used) and use auto mode"
- Also offers "Yes, and use auto mode" without clearing context
- "No, keep planning" option includes inline text input for feedback

Evidence: Plan clear context (search for `"Yes, clear context"` and `"showClearContext"`)


### Worktree Name Validation

What: Worktree names are now validated with strict rules for allowed characters and length.

Details:
- Names must contain only letters, digits, dots, underscores, and dashes
- Maximum length of 64 characters
- Cannot be empty, `"."`, or `".."`
- Parameter description updated: "Optional name for the worktree (letters, digits, dots, underscores, dashes only; max 64 chars)."

Evidence: Worktree name validation (search for `"Invalid worktree name"` and `"must contain only letters, digits"`)


### SessionStart Hook `initialUserMessage` Field

What: The `SessionStart` hook event input now includes an optional `initialUserMessage` field containing the first user message.

Details:
- Allows hooks to access the initial prompt text at session start
- Useful for hooks that need to adjust behavior based on what the user asked

Evidence: SessionStart hook field (search for `"initialUserMessage"`)


### Deep Link CLI Arguments

What: New `--deep-link-last-fetch` and `--deep-link-repo` CLI flags for deep linking from external sources.

Details:
- `--deep-link-last-fetch <ms>`: FETCH_HEAD mtime in epoch ms, precomputed by the deep link trampoline
- `--deep-link-repo <slug>`: Repo slug the deep link `?repo=` parameter resolved to the current cwd

Evidence: Deep link CLI args (search for `"--deep-link-last-fetch"` and `"--deep-link-repo"`)

### Renamed "Bash Command" → "Shell Command" Terminology

Hook-related log messages and internal naming have been updated from "Bash command" (`LocalBashTask`) to "Shell command" (`LocalShellTask`), reflecting the new multi-shell support. Messages like "Bash command failed for pattern" are now "Shell command failed for pattern."

Evidence: Terminology rename (search for `"LocalShellTask"` and `"Shell command failed for pattern"`)


### Auto Mode Context Window Fallback

When the auto mode classifier transcript exceeds the model's context window, Claude Code now falls back to manual approval instead of aborting. In headless mode, the session is still aborted with a descriptive error.

Evidence: Context window handling (search for `"Auto mode classifier transcript exceeded context window"` and `"Classifier transcript exceeded context window"`)


### Permission Denial Message Updates

Permission denial messages have been clarified: "Permission for this action has been denied. Reason:" replaces the previous "Permission for this action was declined." A separate "Denied via channel" path now supports MCP-channel-based denials.

Evidence: Permission messages (search for `"Permission for this action has been denied"` and `"Denied via channel"`)


### Memory Access Instructions Broadened

Memory retrieval instructions have been updated to trigger more broadly: "When memories (personal or team) seem relevant, or the user references prior work with them or others in their organization" replaces the narrower "When specific known memories seem relevant to the task at hand."

Evidence: Memory instructions (search for `"When memories (personal or team) seem relevant"`)


### Worktree State Persistence

Worktree session state (cwd, branch, commit, session ID) is now persisted to the session file as a `"worktree-state"` message, enabling session recovery.

Evidence: Worktree persistence (search for `"worktree-state"` and `"saveWorktreeState"`)


### PR Attribution Changed to Summary

PR attribution data processing changed from returning "enhanced" analysis to returning a "summary" format.

Evidence: PR attribution change (search for `"PR Attribution: returning summary"`)


### Credentials File Change Detection

A new file watcher monitors `.credentials.json` for mtime changes and automatically invalidates the credential cache when the file is modified externally.

Evidence: Credentials watcher — `kA9()` at line ~179473 (search for `".credentials.json"`)


### Plugin Skill Discovery Policy Enforcement

Dynamic skill discovery now respects `projectSettings` and `strictPluginOnlyCustomization` policies. When plugin-only customization is enforced, non-plugin skill sources are blocked.

Evidence: Skill discovery policy (search for `"Dynamic skill discovery skipped: projectSettings disabled or plugin-only policy"`)

## In Development

Features with infrastructure added but not yet enabled. These are shipped "dark" and may become available in future versions.


### RemoteTrigger Tool [Gradual Rollout]

What: A new tool for managing scheduled remote Claude Code agents (triggers) through the claude.ai CCR API — list, create, update, and run triggers without exposing OAuth tokens.

Status: Feature-flagged by `tengu_surreal_dali` (default false), also requires `allow_remote_sessions` policy.

Details:
- Actions: `list`, `get`, `create`, `update`, `run` — maps to `/v1/code/triggers` API
- Auth is handled in-process with OAuth tokens injected automatically
- Tool is deferrable (`shouldDefer: true`) to reduce initial tool schema load
- Read-only actions (`list`, `get`) are flagged as concurrency-safe
- Requires claude.ai login and organization UUID

Evidence: RemoteTrigger tool definition (gated by `tengu_surreal_dali`, search for `"RemoteTrigger"` and `"manage scheduled remote agent triggers"`)


### MCP Channel Permissions [Gradual Rollout]

What: Enables MCP servers with the `claude/channel` capability to push permission decisions and requests via notifications, allowing server-side permission management.

Status: Feature-flagged by `tengu_harbor_permissions` (default false). Additionally requires Teams/Enterprise opt-in.

Details:
- Uses `notifications/claude/channel/permission` and `notifications/claude/channel/permission_request` notification paths
- MCP servers must declare both `claude/channel` and `claude/channel/permission` in capabilities
- Teams/Enterprise opt-in: "Teams/Enterprise opt-in for channel notifications... Default off. Set true to allow; users then select servers via --channels."
- Includes an FNV-1a hash-based identifier system with profanity filtering for generated codes

Evidence: Channel permissions infrastructure (gated by `tengu_harbor_permissions`, search for `"notifications/claude/channel/permission"`)


### Remote Review [In Development]

What: Offloads `/review` PR reviews to a remote Claude Code session, running the review in the background and delivering results as a task notification.

Status: Gated by `REVIEW_REMOTE` environment variable.

Details:
- When triggered, launches a remote session with the PR diff
- Polls remote session for events every 1 second, with 30-minute timeout
- Delivers review findings via task-notification when complete
- Includes session cleanup (delete/archive) after completion
- Falls back to local review if remote launch fails
- Produces notification: "Remote review session launched. Review output will arrive as a task-notification when complete."

Evidence: Remote review launcher (gated by `REVIEW_REMOTE`, search for `"Remote review session launched"` and `"launchRemoteReview"`)


### Time-Based Micro-Compaction [Gradual Rollout]

What: Automatically clears old tool result content when the user returns after an idle gap, reducing context size without a full compaction.

Status: Feature-flagged by `tengu_slate_heron`.

Details:
- Detects idle gaps between the last assistant message and the current time
- When the gap exceeds a configurable threshold, replaces old tool results with "[Old tool result content cleared]"
- Keeps the N most recent tool results intact (`keepRecent` config)
- Logs token savings: "[TIME-BASED MC] gap Xmin > Ymin, cleared Z tool results (~N tokens), kept last M"
- Triggers automatic compaction marker after clearing

Evidence: Time-based micro-compaction (gated by `tengu_slate_heron`, search for `"[TIME-BASED MC]"` and `"[Old tool result content cleared]"`)


### MCP Tool Read/Search Allowlist [In Development]

What: A comprehensive allowlist classifying hundreds of known MCP tool names as "search" or "read" operations, likely for auto-approving read-only MCP operations.

Status: Infrastructure added, not yet visibly wired to auto-approval logic.

Details:
- Search tools: ~90 tools from Slack, GitHub, Datadog, Sentry, Google, Atlassian, Stripe, PubMed, Brave, and more
- Read tools: ~270 tools covering Slack reads, GitHub detail views, Grafana dashboards, PagerDuty, Jira/Confluence, Asana, MongoDB, Elasticsearch, Figma, Puppeteer screenshots, and more
- Classification uses snake_case normalization of tool names

Evidence: MCP tool classification allowlist — `PT4()` at line ~327832 (search for `"slack_search_public"`)


### strictPluginOnlyCustomization Policy [In Development]

What: New managed settings policy that blocks non-plugin customization sources for specified surfaces (skills, hooks, etc.).

Status: Available in managed settings but not broadly documented.

Details:
- Can be set to `true` (locks all surfaces) or an array of specific surface names (e.g., `["skills", "hooks"]`)
- `false` is an explicit no-lock override
- Plugin, policySettings, built-in, builtin, and bundled sources are always allowed
- Invalid values are logged as warnings

Evidence: Plugin-only customization policy (search for `"strictPluginOnlyCustomization"`)
