# Changelog for version 2.1.71


## Summary

This is a major release introducing **Auto Mode**, a new AI-powered permission system that automatically approves or blocks tool actions for unattended workflows; **Team Memory**, enabling shared persistent context synced across all team members via the cloud; and **/loop**, a built-in scheduler for running prompts on recurring intervals. Additionally, `find` and `grep` are now shadowed with faster embedded alternatives (bfs and ugrep), voice mode has been updated with configurable push-to-talk, and a new heap dump diagnostic tool has been added for debugging memory issues.

### Auto Mode (`--permission-mode auto`)

What: A new permission mode that uses an AI-powered "dangerous action classifier" to automatically approve safe tool actions and block dangerous ones, enabling fully autonomous long-running workflows without manual permission prompts.

Usage:
```bash
claude --permission-mode auto
claude --enable-auto-mode
```

Details:
- When enabled, each tool action is evaluated by a multi-stage security classifier before execution
- Safe actions (read-only tools, tools on an allowlist, or actions that would be allowed in `acceptEdits` mode) are fast-pathed without classifier overhead
- The classifier evaluates against a comprehensive threat model including prompt injection, scope creep, accidental damage, data exfiltration, and credential leakage
- Users see an opt-in dialog on first use with options: "Yes, enable auto mode", "Yes, and make it my default mode", or "No, go back"
- If the classifier repeatedly blocks actions (3 consecutive or 20 total), auto mode pauses and falls back to standard permission prompts
- In headless/SDK mode, too many denials or classifier unavailability causes the agent to abort
- Can be disabled per-settings via `permissions.disableAutoMode: "disable"`
- The classifier can be circuit-breaked server-side via `tengu_auto_mode_config`

Evidence: Auto mode permission handler (search for `"Auto mode classifier blocked action"`) — `tM` at line ~534821. Classifier prompt at `g4q` (search for `"You are a security monitor for autonomous AI coding agents"`)


### /loop Command (Scheduled Recurring Prompts)

What: A new `/loop` slash command that schedules prompts to run on a recurring interval, enabling automated monitoring, polling, and periodic tasks within a Claude Code session.

Usage:
```
/loop 5m /babysit-prs
/loop 30m check the deploy
/loop 1h /standup 1
/loop check the deploy          (defaults to 10m interval)
```

Details:
- Supports intervals in seconds, minutes, hours, or days (e.g., `5m`, `30m`, `2h`, `1d`). Minimum granularity is 1 minute
- Also supports standard 5-field cron expressions for precise scheduling (e.g., `"*/5 * * * *"` for every 5 minutes, `"30 14 * * 1-5"` for weekdays at 2:30pm)
- Jobs are session-only by default (die when Claude exits), but can be persisted to `.claude/scheduled_tasks.json` to survive restarts
- Recurring tasks auto-expire after 3 days
- A small deterministic jitter is added to fire times to avoid thundering-herd effects
- Only fires while the REPL is idle (not mid-query)
- Uses file-based locking so only one Claude session runs the scheduler at a time
- Three new internal tools: `CronCreate`, `CronDelete`, `CronList`

Evidence: Cron expression parser (search for `"Standard 5-field cron expression"`) — `_a6` at line ~449603. Loop command (search for `"/loop"`)


### Team Memory (Shared Persistent Knowledge)

What: A new shared memory system that syncs learned context across all team members who work in the same project, enabling Claude to build up organizational knowledge over time.

Usage: Claude automatically manages team memory. Users can say:
- "Remember this for the team" — saves to team memory
- "Remember this" — saves to private user memory
- Team memories are stored in `.claude/team/` and synced via the cloud

Details:
- Two-tier memory system: **private** (per-user, persists across conversations) and **team** (shared, synced across the organization)
- Team memory is synced at session start via an API endpoint and pushed after local changes
- Memories use a frontmatter format with `name:` and `description:` fields, stored as individual `.md` files with a `MEMORY.md` index
- Secret detection prevents accidentally syncing credentials, API keys, or tokens to team memory
- Path traversal protection (`PathTraversalError`) prevents malicious file paths from escaping the memory directory
- Requires OAuth authentication; team memory sync uses ETag-based caching to minimize bandwidth
- Conflict resolution with retries when multiple team members push simultaneously
- The UI shows real-time status indicators like "Recalled 2 team memories" or "Writing 1 team memory"

Evidence: Team memory sync infrastructure (search for `"team-memory-sync: fetched successfully"`) — `gi8` at line ~460253. Memory instructions (search for `"team: memories that are shared"`)

Status: Gated by `tengu_herring_clock` feature flag — may be gradually rolling out.


### Embedded Search Tools (bfs/ugrep)

What: When enabled, Claude Code shadows the system `find` and `grep` commands with faster embedded alternatives — `bfs` (breadth-first search) and `ugrep` — providing significantly improved search performance in the shell.

Details:
- `find` is shadowed with `bfs` (breadth-first file search), configured with `-regextype findutils-default` for compatibility
- `grep` is shadowed with `ugrep`, configured with `--ignore-files`, `--hidden`, `-I` (skip binary), and automatic exclusion of `.git`, `.svn`, `.hg`, `.bzr` directories
- Controlled by the `EMBEDDED_SEARCH_TOOLS` environment variable
- Only active when not running via SDK entrypoints (sdk-ts, sdk-py, sdk-cli)
- Shell aliases for `find` and `grep` are unaliased first to avoid conflicts
- A tip in the system prompt mentions: "When using `find -regex` with alternation, put the longest alternative first"

Evidence: Shell shadowing setup (search for `"unalias find 2>/dev/null"`) — `e6Y` at line ~245057. Feature gate (search for `"EMBEDDED_SEARCH_TOOLS"`)


### Heap Dump and Memory Diagnostics

What: A new diagnostic tool for dumping the JS heap and analyzing memory usage, useful for debugging memory leaks in long-running Claude Code sessions.

Details:
- Writes `.heapsnapshot` files to `~/Desktop` for analysis
- Generates a `-diagnostics.json` file with memory state information
- Reports heap used, RSS, external memory, and total process memory
- Detects potential leak indicators: high memory growth rate, active handles (timer/socket leaks), open file descriptors (file/socket leaks), detached contexts (iframe/context leaks)
- Distinguishes between native memory leaks vs heap leaks
- Available through a diagnostic command

Evidence: Heap dump output (search for `"[HeapDump] Heap dump written to"`)


### `--workload` CLI Flag

What: A new `--workload <tag>` flag for billing-header attribution, allowing organizations to tag Claude Code usage by workload category.

Usage:
```bash
claude --workload my-project-tag
```

Details:
- Sets the `cc_workload` header on API requests for cost attribution
- Process-scoped; primarily used by SDK daemon callers that spawn subprocesses for cron work
- Only works with `--print` mode

Evidence: Workload tag (search for `"cc_workload="`) — `M31` at line ~64100


### Handoff Classifier (Sub-Agent Safety Review)

What: A new safety classifier that reviews sub-agent output when control is handed back to the main agent, checking for potentially dangerous actions performed by sub-agents.

Details:
- When a sub-agent completes, its actions are reviewed against security rules before the main agent acts on the output
- If the classifier flags an issue, the main agent sees: "SECURITY WARNING: This sub-agent performed actions that may violate security policy"
- If the classifier is unavailable, a warning note is shown instead of blocking
- Works in conjunction with the auto mode classifier

Evidence: Handoff classifier (search for `"Handoff classifier flagged sub-agent output"`)


### Voice Mode: Configurable Push-to-Talk

The voice input mode has been updated from a fixed "Hold Space to record" trigger to a configurable push-to-talk system. The voice mode setting is now `voice:pushToTalk` and supports space or modifier key combinations like `meta+k`. The prompt text changed from "Hold Space to record" to a generic "hold [key] to record" that reflects the configured key.

Evidence: Voice mode config (search for `"voice:pushToTalk"`)


### Plugin Management: Per-User Disable with `--scope local`

Users can now disable a project-scoped plugin just for themselves using the `--scope local` flag, without affecting other team members. When a plugin is enabled at project scope (`.claude/settings.json`), the CLI now suggests: "To disable just for you: `claude plugin disable <plugin> --scope local`". This writes the override to `.claude/settings.local.json`.

Evidence: Plugin disable scope (search for `"is enabled at project scope"`)


### Duplicate MCP Server Suppression

When a plugin provides an MCP server that duplicates one already configured manually, the duplicate is now automatically suppressed with a log message rather than causing conflicts. This prevents issues when plugins and manual MCP configurations overlap.

Evidence: Duplicate suppression (search for `"mcp-server-suppressed-duplicate"`)


### Improved Explore/Plan Agent Search Instructions

The Explore and Plan sub-agents now dynamically adapt their search instructions based on whether embedded search tools (bfs/ugrep) are available. When embedded tools are active, agents are instructed to use `find` and `grep` via Bash; otherwise they use the dedicated Glob and Grep tools. The Explore agent system prompt was also updated to say "search broadly when you don't know where something lives" instead of the previous more specific tool-referencing language.

Evidence: Dynamic search instructions in sub-agent prompts (search for `"Use \`find\` via"`)


### Debug Skill Improvements

The `/debug` skill now explicitly supports enabling debug logging mid-session. When debug logging was off, invoking `/debug` turns it on and shows a message that nothing prior was captured. Users are instructed to reproduce the issue, then re-read the log.

Evidence: Debug logging toggle (search for `"## Debug Logging Just Enabled"`)


### Enhanced Shell Safety Checks

New safety checks for shell commands:
- Detection of carriage returns (`\r`) in commands, which `shell-quote` and `bash` tokenize differently — a potential injection vector
- Detection of unquoted redirect operators in `git commit` remainder arguments
- Improved metacharacter detection for glob, backtick, dollar-sign, and other shell expansion characters in tool inputs

Evidence: Carriage return detection (search for `"Command contains carriage return"`)


### Secret Detection Patterns

New regex patterns for detecting secrets that should not be committed or synced:
- GitHub personal access tokens (`github_pat_\w{82}`)
- PyPI API tokens (`pypi-AgEIcHlwaS5vcmc`)
- Slack xapp tokens (`xapp-\d-[A-Z0-9]+-\d+-[a-z0-9]+`)

Evidence: Token patterns (search for `"github_pat_"`)


### Auto Mode Plan Mode Behavior

When in auto mode, the `EnterPlanMode` tool prompt is significantly reduced — it instructs the agent to skip planning in almost all cases and start implementing immediately, since auto mode users chose continuous execution. Plan mode is reserved only for explicit user requests or exceptional architectural ambiguity.

Evidence: Auto mode plan override (search for `"Auto mode prioritizes continuous execution"`)


## Bug Fixes

- Fixed a typo in the Claude guide agent prompt: "relevate" → "relevant" (search for `"subagent to understand the relevant Claude Code features"`)
- Removed stale native module fallback attempts for `image-processor.node` (refactored to lazy singleton pattern) and `color-diff.node` (removed entirely)
- Fixed stdin resume edge case: added logging for `resumeStdin` being called with no stored listeners and `wasRawMode=false`, flagging a possible desync (search for `"resumeStdin: called with no stored listeners"`)


### Client Data Fetching System [Gradual Rollout]

What: A new `clientData` fetching system that pulls configuration and feature data from the server at session start, with caching, retry logic, and 401 token refresh.

Status: Feature-flagged — appears to require OAuth subscriber status with specific profile scopes.

Details:
- Fetches client data on session start with exponential backoff retries
- Caches responses to disk; skips writes if unchanged
- Handles 401 by refreshing OAuth tokens and retrying
- Skipped when "nonessential traffic" is disabled or when user lacks the required OAuth scopes

Evidence: Client data infrastructure (search for `"[clientData] fetch ok"`)


## Notes

**Removed in this version:**

- The `tengu_quartz_falcon` feature flag (and associated `Gs()` / `Hb6()` helpers) has been removed. This flag previously gated an unknown feature with a default label capability.
- The Opus 4.6 welcome notice system (`hasShownOpus46Notice`) has been removed — the one-time notice about model availability no longer appears. The string "Welcome to Opus 4.6" and the per-model notice tip (`opus-4.6-available`) were also removed.
- The native Rust `color-diff.node` module has been removed. Syntax-highlighted diffs now use a different rendering path.
- The native `ripgrep.node` module has been removed, replaced by the embedded bfs/ugrep search tooling.
- The `Auto-approving in` / `Auto-selecting in` / `Press any key to intervene` countdown UI text was removed, suggesting changes to how auto-approval timers work.
