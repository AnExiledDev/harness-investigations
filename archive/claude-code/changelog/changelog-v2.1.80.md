# Changelog for version 2.1.80


## Summary

This release introduces **Channels**, a new system for MCP servers to push inbound notifications into Claude Code sessions, along with the **`/schedule` command** for creating and managing remote agents (triggers) that run on cron schedules in Anthropic's cloud. It also adds a comprehensive **Bash tool output compressor** that intelligently summarizes verbose command outputs, a **message actions navigation system** for browsing and copying transcript messages, and support for **inline marketplace definitions** in settings.json.


### Channels (MCP Inbound Push Notifications)

What: A new system that allows MCP servers to push notifications directly into your Claude Code session, enabling real-time event-driven workflows.

Usage:
```bash
claude --channels server1 server2
```

Details:
- MCP servers that declare the `claude/channel` capability can send `notifications/claude/channel` messages that appear in your session
- Use `--channels <servers...>` to specify which servers may push notifications
- Use `--dangerously-load-development-channels <servers...>` for local development of channel-enabled servers (shows a confirmation dialog at startup)
- Requires claude.ai authentication (`/login`)
- Org administrators can control availability via the `channelsEnabled` managed setting
- Plugin-based channels must be on an approved allowlist (controlled by the `tengu_harbor` feature flag and `tengu_harbor_ledger`)
- A warning is displayed: "Experimental · inbound messages will be pushed into this session, this carries prompt injection risks"
- Channel messages are rendered with a `←` prefix showing the source server name

Evidence: Channel notification system — `notifications/claude/channel` protocol (search for `"claude/channel"`)


### /schedule Command (Remote Agent Triggers)

What: Schedule, update, list, or run remote Claude Code agents that execute on cron schedules in Anthropic's cloud infrastructure.

Usage:
```bash
claude /schedule
claude /schedule "run tests every morning"
```

Details:
- Each trigger spawns a fully isolated remote session (CCR) with its own git checkout, tools, and optional MCP connections
- Supports four operations: create, update, list, and run triggers via the `/v1/code/triggers` API
- Can connect to GitHub repos (via the Claude GitHub App or token sync) and MCP connectors from claude.ai
- Automatically creates environments if none exist
- Includes git bundle uploading to seed remote sessions with your local code (including uncommitted changes)
- Requires claude.ai authentication (API-only accounts are not supported)
- Cron expressions are in UTC; the skill converts local times automatically
- Cannot delete triggers from CLI — directs users to https://claude.ai/code/scheduled

Evidence: Schedule remote agents skill (search for `"Schedule Remote Agents"` and `"/v1/code/triggers"`)


### Bash Tool Output Compressor

What: An intelligent output compression system that recognizes common CLI commands and summarizes their verbose output to save context window space.

Details:
- Automatically detects command types by parsing the shell command and applies type-specific compression:
  - **git status**: Strips hint lines, collapses clean repos to "clean"
  - **git diff/show**: Summarizes per-file with `+N -N` counts, truncates hunks
  - **git log**: Limits line length and total output
  - **git branch**: Groups local/remote, deduplicates
  - **git commit/push/pull**: Extracts only key status lines
  - **Test runners** (pytest, jest, vitest, cargo test, go test): Extracts pass/fail summary and failure details
  - **Linters/type checkers** (tsc, eslint, ruff, mypy, clippy): Keeps only error/warning lines
  - **Package managers** (npm/pip/brew install): Strips download progress noise
  - **grep/rg**: Restructures into `N matches in M files` with per-file groupings
  - **ls -l**: Strips metadata, shows `dir/` and `file size` format with extension summary
  - **cat/file reads**: Truncates long files, keeps definition-like lines
  - **JSON output** (gh api, etc.): Prunes boilerplate URL fields (`followers_url`, `repos_url`, etc.)
  - **Docker/kubectl logs**: Deduplicates repeated log lines
  - **Tables** (docker ps, kubectl get, psql): Limits row count
- Handles piped commands (e.g., `cmd | head -5`) and compound commands (`&&`, `;`, `||`)
- Only compresses when savings exceed a minimum threshold

Evidence: Command classifier and compressor system (search for `"git-status"`, `"git-diff"`, `"test"`, `"error-only"` as case labels in the switch statement)


### Message Actions Navigation

What: A new keyboard-driven system for navigating between messages in the transcript and performing actions like copying message content or tool arguments.

Details:
- Navigate messages: prev/next, prev-user/next-user, top/bottom
- Actions available per message type:
  - **`c`** — copy message content (all message types)
  - **`p`** — copy tool argument (e.g., file path for Read/Edit, command for Bash, pattern for Grep)
  - **`e`** — edit a user message
  - **Enter** — expand/collapse grouped tool uses, attachments, and system messages
- Messages in the active actions view get a subtle background highlight (`messageActionsBackground`)
- Escape collapses the expanded view, Ctrl+C exits message actions entirely
- Strips `<system-reminder>` tags when copying user message content

Evidence: Message actions keybinding system (search for `"messageActions:prev"` and `"messageActionsBackground"`)


### Inline Marketplace Definitions in Settings

What: Define plugin marketplaces directly in `settings.json` using a new `"settings"` source type, without needing an external repository.

Details:
- Add marketplace definitions inline via the `extraKnownMarketplaces` config with `source: "settings"`
- The reconciler writes a synthetic `marketplace.json` to the cache directory
- Plugins must use remote sources (github, git-subdir, npm, url, pip) — relative paths are not supported
- Reserved official marketplace names (anthropic, claude, etc.) cannot be used with settings sources
- Marketplace name must match the `extraKnownMarketplaces` key

Evidence: Settings source marketplace schema (search for `"source: \"settings\""` and `"Inline marketplace manifest defined directly in settings.json"`)


### Effort Level Display Enhancement

The effort status bar message now shows the currently computed effort level when effort is set to "auto". Instead of just `Effort level: auto`, you now see `Effort level: auto (currently high)` (or medium/low), giving better visibility into what the model is actually using. Additionally, a new recommendation dialog suggests medium effort for Opus to balance speed, intelligence, and rate limits.

Evidence: Updated effort display (search for `"Effort level: auto (currently"` and `"We recommend medium effort for Opus"`)


### Improved Agent Memory Scope Labels

The agent memory enablement prompt now uses clearer scope labels: "User scope (~/.claude/agent-memory/)" and "Project scope (.claude/agent-memory/)" instead of the previous generic "Enable" labels, making it easier to understand where memories will be stored.

Evidence: Updated scope labels (search for `"User scope (~/.claude/agent-memory/) (Recommended)"` and `"Project scope (.claude/agent-memory/) (Recommended)"`)


### Improved Memory Staleness Guidance

The system prompt guidance for handling memories has been updated to emphasize verifying memories against current state before acting on them, rather than simply trusting what was true when the memory was written.

Evidence: Updated memory instruction (search for `"Memory records can become stale over time"`)


### Search Highlighting from End

The terminal search highlighting system now supports searching from the end of the buffer, improving the search experience when looking for recent content.

Evidence: New `searchHighlightFromEnd` property (search for `"searchHighlightFromEnd"`)


### Rust File Index Skip Optimization

The file indexer now detects when tracked paths haven't changed and skips unnecessary Rust index rebuilds, improving startup and refresh performance for projects using the Rust-based file indexer.

Evidence: Index rebuild skip messages (search for `"[FileIndex] skipped Rust index rebuild"`)


### Git Index-Based File Cache Invalidation

The file index cache now checks the `.git/index` modification time to intelligently invalidate and refresh the file listing only when the git index actually changes, rather than on a fixed timer.

Evidence: Git index mtime check in file cache refresh (search for `".git", "index"` in the `RnY` function)


### History Search Navigation with Up Arrow

A new `historySearch:navUp` keybinding (bound to the Up arrow key) allows navigating upward through history search results, complementing the existing search controls.

Evidence: New keybinding (search for `"historySearch:navUp"`)


### Attachments Navigation to Messages

A new `attachments:toMessages` keybinding (bound to the Up arrow key) allows navigating from the attachments area directly into the message transcript, improving keyboard-driven navigation flow.

Evidence: New keybinding (search for `"attachments:toMessages"`)


### Open in Editor with Line Number Support

The open-in-editor feature now supports jumping to specific line numbers across different editors. GUI editors (like VS Code, Sublime) use their native line-jump flags, while terminal editors (like vim, nano) use `+N` syntax. The editor spawning handles both detached GUI processes and inline terminal editors with alternate screen management.

Evidence: Editor spawning with line support (search for `"editor spawn failed"`)


### Chunked Transcript Export

Transcript export now renders in chunks using a `renderRange` system, enabling streaming/progressive rendering of large transcripts instead of rendering everything at once.

Evidence: Chunked rendering via `renderRange` (search for `"renderRange"`)


### Improved Tab Focus Management

The focus management system has been refactored. Tab/Shift+Tab now properly cycles focus between interactive elements, and the focus manager is attached to the root node rather than being a standalone entity. The keyboard dispatch system now handles Tab key for focus cycling when not consumed by other handlers.

Evidence: Focus management changes (search for `"focusManager"` and `"focusNext"`)


### GitHub App Installation & Token Sync Checks

New infrastructure checks whether the Claude GitHub App is installed on a repository and whether the user's GitHub token is synced via web-setup. These checks support the `/schedule` command's ability to determine if remote agents can access specific repos.

Evidence: GitHub checks (search for `"checkGithubAppInstalled"` and `"checkGithubTokenSynced"`)


### Git Bundle Upload for Remote Sessions

A new git bundle creation and upload system captures the current repository state (including uncommitted work via `git stash create`) and uploads it as a seed bundle for remote CCR sessions. Supports automatic fallback from `--all` to `HEAD`-only bundles when the full bundle exceeds size limits.

Evidence: Bundle upload system (search for `"git bundle create"` and `"_source_seed.bundle"`)


### Fine-Grained Tool Streaming Guard

The `eager_input_streaming` feature for fine-grained tool streaming is now gated to only activate for first-party connections that support extended notifications, preventing incompatible configurations.

Evidence: Guard conditions added (search for `"tengu_fgts"` in the structural diff)


### Vercel Plugin Tip

A new tip suggests installing the Vercel plugin when working with Vercel projects: "Working with Vercel? Install the vercel plugin."

Evidence: Vercel tip (search for `"Working with Vercel? Install the vercel plugin"`)


## Bug Fixes

- Fixed mouse wheel event parsing for the legacy X10 mouse protocol (6-byte `\x1B[M` sequences), ensuring scroll events are correctly recognized in more terminal emulators (search for `"\x1B[M"` in the mouse parser)

- Fixed Kitty keyboard protocol detection to require digit after `[` prefix, preventing false matches on other escape sequences (search for `"/^\\[\\d/.test(K)"`)

- Fixed `async` declaration for project rules loading function (`dV1`/`FV1`), which was missing the `async` keyword (search for `"async function dV1"`)

- Config panel now wrapped in `Suspense` boundary, preventing crashes from lazy-loaded components (search for `"Suspense"` near config panel)
