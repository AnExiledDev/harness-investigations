# Changelog for version 2.1.108

## Summary

This release introduces a JavaScript REPL tool for executing code with persistent state and programmatic tool access, a new usage analysis dashboard (Birch Compass) for understanding what drives your rate limits, and a model-switch confirmation dialog that warns about cache invalidation. It also brings fuzzy "Did you mean?" suggestions for mistyped commands and skills, changes the permission rule wildcard syntax from `:*` to ` *`, adds MCP server auto-reconnection with exponential backoff, and includes a broad UI refresh replacing text-based status icons with a unified component system.


### JavaScript REPL Tool

What: A new built-in tool that lets Claude execute JavaScript code in a persistent VM context with programmatic access to Claude Code tools (Read, Write, Edit, Glob, Grep, Bash).

Usage: Claude can now run JavaScript directly to perform file operations, chain tool calls, and compute results. Variables persist across multiple REPL invocations within the same conversation.

Details:
- Supports top-level `await` for async operations
- State persists across calls — variables defined in one REPL call remain accessible in subsequent calls
- Provides `registerTool()`, `unregisterTool()`, `listTools()`, and `getTool()` for dynamic tool management
- Includes a `haiku(prompt, schema?)` function for lightweight model sampling
- Includes `shQuote(s)` for safe shell string quoting
- `import`/`require` are not available (VM context is sealed); use the built-in tool functions for file and shell operations
- REPL VM state is cleared on `/compact` — a notification informs you: "Your REPL VM state has been cleared as part of this compaction"
- Includes a replay mechanism for validating REPL execution determinism across compaction boundaries

Evidence: REPL tool registration with "Execute JavaScript code with access to Claude Code tools" description (search for `"Execute JavaScript"`)


### REPL Replay and Drift Detection

What: Infrastructure for replaying REPL code blocks after compaction to validate that execution produces consistent results.

Details:
- Extracts code blocks and tool calls from conversation history for replay
- Caches tool call results to replay against
- Detects nondeterminism: "likely nondeterminism (Date.now, Math.random) took a different branch"
- Throws `ReplayCacheExhausted` when replayed code makes more tool calls than the original
- Reports replay status: "N blocks replayed cleanly"

Evidence: Replay infrastructure (search for `"REPL replay"` and `"ReplayCacheExhausted"`)


### Usage Analysis Dashboard (Birch Compass) [Gradual Rollout]

What: A new settings panel that analyzes your local sessions and shows what's contributing to your rate limit usage, with actionable recommendations.

Details:
- Available to Pro and Max subscribers
- Shows approximate usage breakdown based on local sessions (does not include other devices or claude.ai)
- Tracks five cost behavior categories:
  - **Cache misses**: "X% of your usage hit a >100k-token cache miss" — recommendation: `/compact` before stepping away
  - **Long context**: "X% of your usage was at >150k context" — recommendation: `/compact` mid-task, `/clear` when switching
  - **Subagent-heavy sessions**: "X% of your usage came from subagent-heavy sessions" — recommendation: configure cheaper models for simpler subagents
  - **High parallelism**: "X% of your usage was while 4+ sessions ran in parallel" — recommendation: queue sessions for more even usage
  - **Long-running sessions**: "X% of your usage came from sessions active for 8+ hours" — recommendation: ensure continuous usage is intentional
- Toggle between 24-hour and 7-day views with `d` and `w` keyboard shortcuts
- Notes: "these are independent characteristics of your usage, not a breakdown"
- Warns about oversized session files (>200MB) that would skew analysis

Evidence: Feature gated by `tengu_birch_compass` flag (search for `"tengu_birch_compass"` and `"What's contributing to your limits usage"`)


### Model Switch Confirmation Dialog

What: A new confirmation dialog warns you when switching models mid-conversation that the cache will be invalidated.

Details:
- Dialog title: "Switch model?"
- Message: "This conversation is cached for the current model. Switching to [model] means the full history gets re-read on your next message."
- Subtitle: "Your next response will be slower and use more tokens"
- Options: "Yes, switch to [model]" or "No, go back"
- Only shown when the conversation has cached content for the current model

Evidence: Model switch confirmation (search for `"Switch model?"` and `"This conversation is cached"`)


### Fuzzy "Did You Mean?" Suggestions

What: When you mistype a slash command or skill name, Claude Code now suggests the closest match.

Details:
- For slash commands: `Unknown command: /stauts. Did you mean /status?`
- For skills: `Unknown skill: comit. Did you mean commit?`
- Uses fuzzy string matching to find the best candidate from available commands and skills
- Tracks suggestion availability for analytics

Evidence: Fuzzy matcher for commands and skills (search for `"Did you mean /"` and `"Did you mean "`)


### Command vs Skill Disambiguation

What: When the model tries to invoke a built-in CLI command as a skill, it now receives a clear error explaining the distinction.

Details:
- Error message: "[name] is a [type] command, not a skill. Ask the user to run /[name] themselves — it cannot be invoked via the [tool] tool."
- Prevents confusion between built-in slash commands and skill invocations

Evidence: Disambiguation error message (search for `"command, not a skill"`)


### MCP Server Auto-Reconnection with Backoff

What: Failed remote MCP servers now automatically reconnect using exponential backoff instead of staying disconnected.

Details:
- Logs: `[MCP] Retry: N failed remote server(s) after Xms backoff`
- Stops retrying when all servers reconnect: `[MCP] Retry: all remote servers connected, stopping`
- Reports persistent failures: `remote server(s) still failed after all retries:`

Evidence: MCP reconnection logic (search for `"[MCP] Retry"` and `"failed remote server"`)


### Permission Rule Wildcard Syntax Changed from `:*` to ` *`

The wildcard syntax for permission rules has changed from colon-asterisk to space-asterisk. For example:

- Old: `Bash(git:*)`, `Bash(npm run:*)`
- New: `Bash(git *)`, `Bash(npm run *)`

This affects settings files, autocomplete suggestions, onboarding examples, and documentation. The old `:*` syntax continues to be recognized alongside the new ` *` syntax for backward compatibility.

Evidence: Permission rule syntax change (search for `"Bash(git *)"` and `"Bash(npm *)"`)


### `/clear` Command Description Updated

The `/clear` command description has been updated from "Clear conversation history and free up context" to "Start fresh: discard the current conversation and context" for clearer communication.

Evidence: Clear command description (search for `"Start fresh: discard the current conversation and context"`)


### `/rewind` Gains `undo` Alias

The `/rewind` command (also aliased as `/checkpoint`) now also responds to `/undo`, making it more discoverable.

Evidence: Undo alias addition (search for `"undo"` near `"checkpoint"`)


### Improved Language Orthographic Correctness

When Claude responds in non-English languages, it now receives explicit instructions to maintain full orthographic correctness, including all required diacritical marks, accents, and special characters. For example, it will no longer substitute "nao" for "não" or "fur" for "für".

Evidence: Orthographic instruction (search for `"orthographic"` and `"diacritical marks"`)


### Enhanced Rate Limit and Server Error Messages

Rate limit and server error messages now include dynamic status information and direct users to the updated status page at `status.claude.com` (changed from `status.anthropic.com`).

Details:
- 429 errors now show: "Request rejected (429)" with "Server is temporarily limiting requests (not your usage limit)"
- Status URL changed to `status.claude.com`
- Error guidance suggests: "this may be a temporary capacity issue — check status.claude.com"

Evidence: Status URL change (search for `"status.claude.com"`)


### Improved Sleep/Blocking Guidance

The guidance for sleep commands and blocking behavior has been substantially rewritten to emphasize Monitor as the preferred alternative.

Details:
- Old: `sleep N` as first command with N ≥ 2 is blocked with brief explanation
- New: "Long leading `sleep` commands are blocked. To poll until a condition is met, use Monitor with an until-loop (e.g. `until <check>; do sleep 2; done`)"
- Additional guidance: "Do not chain shorter sleeps to work around the block"
- General sleep advice simplified from "keep the duration short (1-5 seconds)" to "keep the duration short"

Evidence: Blocking guidance improvements (search for `"Long leading"` and `"until-loop"`)


### Paste Line Break Normalization

Multiline paste operations now normalize Windows (CRLF) and classic Mac (CR) line endings to Unix (LF) format, preventing issues with mixed line endings in pasted content.

Evidence: Paste normalization (search for `"\\r\\n|\\r"` in paste handler)


### Enhanced BOM Handling in File Reads

File reading now properly handles UTF-8 Byte Order Marks with improved byte count accounting and comprehensive line ending normalization after BOM removal.

Evidence: BOM detection (search for `"65279"`)


### Unified Status Icon Component

Success checkmarks (✓), warning icons, and error indicators throughout the CLI have been replaced with a consistent component-based icon system (`N4` component), improving visual consistency across status messages, plugin marketplace results, GitHub Actions workflow confirmations, and iTerm2 setup output.

Evidence: 45+ instances of the new component replacing text-based icons (search for `status: "success"` near `N4`)


### Plugin Version Resolution Tracking

Plugin installations now track a `resolvedVersion` field that records the tag-derived semver version resolved during installation. This improves version verification and deduplication, especially when upstream plugins forget to bump their `plugin.json` version.

Details:
- Description: "Tag-derived semver this install resolved to (when fetched via a version constraint). Used by verifyAndDemote in preference to manifest.version"
- Plugin cache is invalidated when resolved version changes

Evidence: Plugin version tracking (search for `"resolvedVersion"`)


### ExitWorktree and EnterWorktree Subagent Validation

Both `ExitWorktree` and `EnterWorktree` now validate that they are not being called from a subagent with a cwd override (e.g., `isolation: "worktree"` or explicit cwd). This prevents subagents from mutating the parent session's working directory.

Details:
- Error: "ExitWorktree cannot be called from a subagent with a cwd override — it would mutate the parent session's process-wide working directory."
- Directs subagents to use Bash with `cd` for directory changes

Evidence: Worktree validation (search for `"ExitWorktree cannot be called from a subagent"`)


### Ultrareview Cloud Launch Flow

Ultrareview has been updated with a clearer cloud launch confirmation flow.

Details:
- Now prompts: "Run ultrareview in the cloud?" with estimated time "~10–20 min"
- Requires Claude.ai authentication: "Ultrareview requires a Claude.ai account. Run /login to authenticate."
- Unavailable during essential-traffic-only mode
- Description updated: "Finds and verifies bugs in your branch using a multi-agent review fleet"
- REPL tool execution is blocked during ultrareview with access validation

Evidence: Ultrareview flow (search for `"Run ultrareview in the cloud?"` and `"ultrareview-launch"`)


### Settings Schema Refactored to Feature Gates

The monolithic settings schema has been refactored into a modular feature gate system. Features like `autoMode`, `deepLink`, `voice`, `assistant`, and `briefView` are now individually defined with their own `buildGate()`, `shape()`, and `permissionsShape()` methods, making the settings system more maintainable and enabling conditional feature compilation.

Evidence: Feature gate definitions (search for `"autoMode"` near `"buildGate"`)


### Headless Plugin Installation Progress Callbacks

Plugin installations via the SDK now support progress callbacks, enabling SDK consumers to track installation stages (started, completed, per-marketplace installed/failed).

Evidence: Progress callback (search for `"Headless plugin installation progress"`)


### REPL Blocked by PreToolUse Hook

REPL tool execution now respects PreToolUse hooks, showing a clear "Blocked by PreToolUse hook" message when execution is blocked by a hook.

Evidence: Hook blocking message (search for `"Blocked by PreToolUse hook"`)


## Bug Fixes

- Fixed paste handling to normalize CRLF and CR line endings to LF in multiline mode, preventing mixed line endings from confusing editors (search for `"\\r\\n|\\r/g"`)
- Fixed attribution snapshot handling to clear the map before storing new snapshots, preventing stale data accumulation (search for `"D.clear()"`)
- Fixed dependency version resolution to check both `resolvedVersion` and manifest version for more accurate plugin deduplication (search for `"resolvedVersion"`)
- Fixed ANSI escape sequence parsing to correctly handle CSI sequences, OSC sequences, and other terminal control codes (search for `"Tq4"`)
- Fixed a variable reference bug in a slice operation where the wrong variable was being used (search for `"O6.slice(1)"`)
- Improved validation of at-mentions to require content presence alongside title checks, preventing empty mentions from being processed (search for `"contentLength"`)
- Fixed React component state management by correcting dependency arrays and initial state values (search for `"lzA"`)
- Improved skill source filtering logic to correctly include builtin sources instead of excluding them (search for `"q.source !== 'builtin'"`)


### Birch Compass Session Dashboard [Gradual Rollout]

What: While the dashboard infrastructure is fully built, it is gated behind the `tengu_birch_compass` feature flag with a default of `false`, meaning it is not yet available to all users.

Status: Feature-flagged with `tengu_birch_compass` (default: disabled)

Details:
- Full UI, cost analysis engine, and 5 behavior categories are implemented
- Requires Pro or Max subscription even when enabled
- Keyboard shortcuts (`d`/`w`) for period switching are wired up
- Session scanning and file size validation are complete

Evidence: Feature gated with default false (search for `tengu_birch_compass` — `b8("tengu_birch_compass", !1)`)


### Coach Mode [In Development]

What: A new `coachMode` configuration option has been added to the settings schema and tracked configuration attributes, but its behavioral implementation is not yet visible.

Status: Infrastructure only — configuration plumbing exists but no observable behavioral changes

Details:
- Added to tracked configuration attributes alongside existing settings
- No user-facing documentation or tips found for this feature yet

Evidence: Configuration property (search for `"coachMode"`)


### Assistant Feature Gate [In Development]

What: The feature gate system includes an `assistant` feature with `buildGate: () => !1` (always false), indicating planned but disabled functionality.

Status: Disabled — build gate returns false, shape returns empty object

Details:
- Included in the feature gate list alongside `autoMode`, `deepLink`, `voice`, and `briefView`
- Shape returns `Md5` (an empty object), indicating the settings schema is not yet defined

Evidence: Assistant gate disabled (search for `assistant` near `buildGate` — returns `!1`)


## Notes

The permission rule wildcard syntax change from `:*` to ` *` is the most impactful change for existing users. If you have custom permission rules in your settings files using the old syntax (e.g., `Bash(git:*)`), the old format continues to work but new autocomplete suggestions and documentation now use the space-asterisk format (e.g., `Bash(git *)`). Consider updating your rules to the new syntax for consistency.

The removal of the bundled Chalk template library and HTML5 tokenizer (parse5) from the CLI reduces the package size. These were replaced by lighter-weight alternatives or removed where unused.
