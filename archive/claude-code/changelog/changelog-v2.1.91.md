# Changelog for version 2.1.91


## Summary

This release activates the Ultraplan cloud planning feature (previously dark-launched), introduces several feature-flagged agent behavior optimizations (reduced file re-reads, Write append mode, smarter subagent output), removes the deprecated `/output-style` and `/pr-comments` commands along with Magic Docs, and fixes keyboard shortcut conflicts across the entire UI where single-key bindings could interfere with system shortcuts like Ctrl+X or Ctrl+F.

### Disable Shell Execution in Skills (Policy Setting)

What: A new `disableSkillShellExecution` policy/config setting that prevents inline shell execution in skills and custom slash commands from user, project, or plugin sources.

Usage: Set in your settings or policy configuration:
```json
{
  "disableSkillShellExecution": true
}
```

Details:
- When enabled, shell command blocks (`` ```! `` fenced blocks and `` !`...` `` inline syntax) in skills are replaced with `[shell command execution disabled by policy]`
- Applies to commands from user, project, or plugin sources — not policy settings
- Useful for organizations that want to allow skills but prevent arbitrary shell execution

Evidence: Policy gate and replacement logic (search for `"disableSkillShellExecution"` and `"[shell command execution disabled by policy]"`)


### `/feedback` Command Provider-Aware Disabling

What: The `/feedback` command now displays informative messages explaining why it's unavailable on non-first-party providers and when disabled by policy, instead of silently failing or showing a generic error.

Details:
- Shows specific messages for Amazon Bedrock, Vertex AI, and Microsoft Foundry users, directing them to GitHub issues
- Respects `DISABLE_FEEDBACK_COMMAND`, `DISABLE_BUG_COMMAND`, and `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` environment variables
- Respects organization policy `allow_product_feedback`
- All messages now direct users to `https://github.com/anthropics/claude-code/issues`

Evidence: Provider-specific feedback disabling (search for `"/feedback has been disabled"` and `"/feedback is not available when using"`)


### Peer Session Messaging

What: When another Claude Code session sends a message while you're working, it now appears with contextual framing that helps Claude understand the message source.

Details:
- Messages from peer sessions are labeled: "A peer session sent a message while you were working"
- Claude is instructed: "This is from another Claude session, not your user. After completing your current task, decide whether/how to respond."

Evidence: Peer session notification framing (search for `"A peer session sent a message"`)


### Sandbox Unavailable Error in Stream-JSON Mode

What: When running in headless mode (`--output-format stream-json`) and the sandbox is required but unavailable, Claude Code now emits a proper JSON error result instead of only writing to stderr.

Details:
- Error message includes: `"Sandbox required but unavailable: {reason}. Set sandbox.failIfUnavailable=false to allow unsandboxed execution."`
- The JSON result includes all standard fields (session_id, uuid, duration, etc.) for proper parsing by automation tools

Evidence: Headless sandbox error handling (search for `"Sandbox required but unavailable:"`)


### Untrusted Device Detection for Bridge Sessions

What: Bridge/remote session connections now detect "untrusted device" errors and return a terminal failure instead of silently retrying.

Details:
- When the bridge endpoint returns a 403 with `untrusted_device` resource, the connection is marked as terminal
- Users see a message to `"run /login to enroll this device"`

Evidence: Untrusted device handling in bridge connection (search for `"untrusted_device"` and `"run /login to enroll this device"`)

### Keyboard Shortcut Conflict Prevention

Multiple keyboard handlers across the UI now properly check that Ctrl and Meta (Cmd) modifiers are not pressed before responding to single-key shortcuts. Previously, pressing Ctrl+X, Ctrl+F, Ctrl+S, Ctrl+K, Ctrl+T, Ctrl+W, or Ctrl+Q could trigger unrelated in-app actions.

Affected areas:
- Shell/task panel: `x` (kill), `f` (focus), `t` (terminate), `k` (kill)
- Submit confirmation: `s` (submit)
- Session picker: `q` (quit)
- Worktree picker: `w` (select worktree)

Evidence: Guards added as `!t.ctrl && !t.meta` before key checks across ~10 components (search for `!t.ctrl && !t.meta` in the diff)


### Permission Mode: `auto` Classifier

The permission mode setting now includes `auto` as an option, which uses a model classifier to approve or deny permission prompts automatically.

Evidence: Auto mode in permission enum (search for `"Use a model classifier to approve/deny permission prompts"`)


### Terminal Reason Tracking

Query results now include a `terminal_reason` field that records why the query loop terminated. Possible values include: `blocking_limit`, `rapid_refill_breaker`, `prompt_too_long`, `image_error`, `model_error`, `aborted_streaming`, `aborted_tools`, `stop_hook_prevented`, `hook_stopped`, `tool_deferred`, `max_turns`, `completed`.

Evidence: Terminal reason enum and field (search for `"Why the query loop terminated"`)


### Rate Limit Reduction Suggestions [Gradual Rollout]

When hitting a 7-day rate limit on Pro plans, Claude Code now suggests concrete ways to reduce usage:
- If using an Opus model: suggests `"try /model sonnet · ~2× runway"`
- If using high/max effort: suggests `"try /effort medium"`

Evidence: Rate limit suggestions (gated by `tengu_garnet_plover`, search for `"try /model sonnet"`)


### Opus Usage Cost Warning [Gradual Rollout]

The model selector now shows `" · ~2× usage vs Sonnet"` when selecting Opus on Pro plans, helping users understand the relative cost.

Evidence: Opus cost indicator (gated by `tengu_gypsum_kite`, search for `"~2× usage vs Sonnet"`)


### High Effort Warning [Gradual Rollout]

When effort is set to "high" on the Max plan, the effort display now appends `"burns fastest — medium handles most tasks"` as a gentle nudge.

Evidence: High effort cost warning (gated by `tengu_slate_finch`, search for `"burns fastest"`)


### Unified Upgrade Paths from Server

Rate limit dialogs now use server-provided upgrade path data (via the `anthropic-ratelimit-unified-upgrade-paths` response header) to determine which options to show (overage, plan upgrade), rather than computing them client-side.

Evidence: Server-driven upgrade paths (search for `"anthropic-ratelimit-unified-upgrade-paths"`)


### Memory Selector Conversation Caching

The memory selection system now caches its state per-directory across queries within a session, reusing the conversation context for follow-up memory relevance queries instead of rebuilding it each time. The memory selection prompt has also been revised to support multi-turn usage ("Do not re-select memories you already returned for an earlier query").

Evidence: Memory selector state management (search for `"memdir_relevance"`)


### PermissionDenied Hook Retry Message

The message shown after a PermissionDenied hook allows a retry has been simplified from "this command is now approved. You may retry it if you would like" to "you may retry this tool call" — more accurate since the hook may approve a non-command tool call.

Evidence: Revised retry message (search for `"you may retry this tool call"`)


### Tool Telemetry Enrichment

Tool usage telemetry now tracks additional dimensions: file path length, bash command length, and whether Read calls use `limit`/`offset` parameters.

Evidence: Telemetry fields (search for `readHasLimit` and `bashCommandLen` in the diff)


### NotebookEdit Path Handling

The NotebookEdit tool now properly resolves relative paths (consistent with other file tools) and uses `randomUUID` instead of `Math.random()` for generating cell IDs.

Evidence: Path resolution in notebook edit (search for `"notebook_path"` and `backfillObservableInput` in the diff)


### File Upload Filename Sanitization

File upload form data now properly escapes special characters (newlines, backslashes, quotes) in filenames, preventing malformed multipart requests.

Evidence: Filename escaping function `hMK()` (search for `"Content-Disposition: form-data"` in the string changes)


### Ultraplan Improvements

The Ultraplan feature received several enhancements:
- Better error handling: "Ultraplan hit an unexpected error during launch" message now sent to the model for graceful recovery
- Auto-polling timeout: sessions that remain unresolved are automatically cleaned up
- Telemetry: new `tengu_ultraplan_stopped` event when killing ultraplan tasks
- Terms tracking with `hasSeenUltraplanTerms` state

Evidence: Ultraplan error and state management (search for `"Ultraplan hit an unexpected error"`)


### Removed: `/output-style` Command

The deprecated `/output-style` command has been fully removed. It was already showing a deprecation notice directing users to `/config`.

Evidence: Removal of output-style command handler (search for `"output-style"` in removed section)


### Removed: `/pr-comments` Command

The built-in `/pr-comments` slash command for fetching GitHub pull request comments has been removed. The same functionality is available via `gh api` commands directly.

Evidence: Removal of pr-comments command definition (search for `"Get comments from a GitHub pull request"` in removed section)


### Removed: Magic Docs

The Magic Docs feature — which automatically updated `# MAGIC DOC:` files based on conversation context — has been completely removed. This includes the update prompt, the template system, and the background agent that processed magic doc files.

Evidence: Removal of magic doc infrastructure (search for `"MAGIC DOC"` in removed section)

## Bug Fixes

- Fixed `findLogicalLineStart` crashing or scanning unnecessarily when offset is 0 — now returns 0 immediately (search for `"findLogicalLineStart"`)
- Fixed `CLAUDE_FORCE_DISPLAY_SURVEY` environment variable not being properly checked as a boolean, which could cause the feedback survey to show unexpectedly (search for `"CLAUDE_FORCE_DISPLAY_SURVEY"`)
- Fixed plugin name extraction using proper string-before-delimiter logic instead of naive `.split("@")[0]`, which could fail for scoped package names (search for `FB6` in the diff)
- Added proper timeout cleanup in conversation effects, preventing potential memory leaks from dangling setTimeout references
- Fixed Chrome extension installation check to properly catch and log errors instead of letting them propagate silently (search for `"Failed to check extension installation"`)
- Fixed Windows binary detection for MCP servers by adding a fallback file-size comparison when the standard executable path resolution fails
- Fixed theme change detection by adding support for the `themeNotify` terminal response, enabling automatic theme updates when the terminal theme changes

## In Development

Features with infrastructure added but not yet enabled for all users. These are shipped behind feature flags and may become available in future versions.


### Relative File Paths in Tool Descriptions [Gradual Rollout]

What: When enabled, tool descriptions instruct Claude to use relative (cwd-based) file paths instead of absolute paths, and the Bash tool description notes that `cd` does not persist between calls.

Status: Feature-flagged via `tengu_relpath_gh7k` (default: false)

Details:
- Read tool description changes from "must be an absolute path" to "can be relative to cwd (preferred for brevity) or absolute"
- Bash tool adds: "Avoid `cd` unless the User explicitly requests it. The shell already starts in cwd"
- Read tool adds `ONLY include with offset to read a specific slice. OMIT to read the whole file`

Evidence: Relative path tool descriptions (gated by `tengu_relpath_gh7k`, search for `"The file_path parameter can be relative to cwd"`)


### Redundant File Re-Read Prevention [Gradual Rollout]

What: When Claude re-reads a file that hasn't changed since its last Read, the tool result returns a warning instead of the file content, saving tokens.

Status: Feature-flagged via `tengu_noreread_q7m_velvet` (default: false)

Details:
- Returns: "Wasted call — file unchanged since your last Read. Refer to that earlier tool_result instead."
- Edit/Write results now append: "(file state is current in your context — no need to Read it back)"
- Tool descriptions add: "Do NOT re-read a file you just edited to verify"

Evidence: Re-read prevention (gated by `tengu_noreread_q7m_velvet`, search for `"Wasted call"`)


### Write Tool Append Mode [Gradual Rollout]

What: The Write tool gains a `mode` parameter with `'overwrite'` (default) and `'append'` options, allowing content to be added to the end of a file without rewriting it.

Status: Feature-flagged via `tengu_maple_forge_w8k` (default: false)

Details:
- New `mode` parameter on the Write tool schema
- Description: "Use 'append' to add content to the end of an existing file instead of rewriting the full content — e.g. for logs, accumulating output, or adding entries"
- Instruction: "Do NOT re-send the existing file contents" when appending

Evidence: Write append mode (gated by `tengu_maple_forge_w8k`, search for `"mode:'append'"`)


### Edit After Write Without Read [Gradual Rollout]

What: Files written during the current session can be edited without a prior Read call — the Edit tool recognizes that the session already knows the file's contents.

Status: Feature-flagged via `tengu_editafterwrite_qpl` (default: false)

Details:
- Edit tool description appends: "Files you Wrote this session can be Edited without a prior Read."
- Reduces unnecessary round-trips when writing then immediately editing a file

Evidence: Edit after write (gated by `tengu_editafterwrite_qpl`, search for `"Files you Wrote this session"`)


### Subagent Report File Prevention [Gradual Rollout]

What: Subagents are instructed to return findings as text in their final message instead of creating report/summary `.md` files.

Status: Feature-flagged via `tengu_sub_nomdrep_q7k` (default: false)

Details:
- Adds instruction: "Do NOT write report/summary/findings/analysis .md files. Return findings directly as your final assistant message — the parent agent reads your text output, not files you create."

Evidence: Subagent no-report instruction (gated by `tengu_sub_nomdrep_q7k`, search for `"report/summary/findings/analysis .md files"`)


### Ultraplan Cloud Planning UI [Gradual Rollout]

What: The Ultraplan feature — which launches a planning session in Claude Code on the web — now has a fully functional interactive UI in the CLI.

Status: Feature-flagged via `tengu_ultraplan_config` (must have `enabled: true`)

Details:
- Typing "ultraplan" in a prompt triggers keyword detection and launches the `/ultraplan` flow
- "Run ultraplan in the cloud?" dialog with time estimates and option to disable Remote Control
- Plan approval UI with three choices: "Implement here" (inject into current conversation), "Start new session" (clear and start fresh with the plan), or "Cancel" (save plan to file)
- Scrollable plan preview with `ctrl+u/ctrl+d` to scroll
- If Remote Control is active, launching ultraplan disables it with a warning
- Rejected plans are saved to `{session}-ultraplan.md`

Evidence: Ultraplan config and UI (gated by `tengu_ultraplan_config`, search for `"Run ultraplan in the cloud?"` and `"Ultraplan approved"`)
