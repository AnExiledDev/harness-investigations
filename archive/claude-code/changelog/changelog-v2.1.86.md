# Changelog for version 2.1.86


## Summary

This release introduces trusted device enrollment for enhanced session security, a new file read caching optimization that avoids re-reading unchanged files, and a context window usage breakdown command. It also adds Slack channel autocomplete integration, expands git/PR operation tracking beyond just `git commit` and `gh pr create`, and includes new shell safety checks for zsh equals expansion and bash array subscript injection.

### Trusted Device Enrollment

What: Claude Code now automatically enrolls your device as a trusted device, sending a `X-Trusted-Device-Token` header with API requests for enhanced session security.

Details:
- Enrollment happens automatically in the background when you're logged in via OAuth
- Device is registered with the display name `Claude Code on <hostname> · <platform>`
- The token is persisted locally and reused across sessions
- You can override with the `CLAUDE_TRUSTED_DEVICE_TOKEN` environment variable
- Enrollment can be skipped in essential-traffic mode

Evidence: Trusted device enrollment flow (search for `"[trusted-device] Enrolled device_id="`) — gated by `tengu_sessions_elevated_auth_enforcement` flag

**[Gradual Rollout]** — gated by the `tengu_sessions_elevated_auth_enforcement` feature flag.


### File Read Caching ("Unchanged since last read")

What: When the Read tool is used on a file that hasn't changed since a previous read in the same conversation, Claude now returns a short notice instead of re-reading the entire file, saving context window space.

Details:
- Displays "Unchanged since last read" in the tool output
- The full message tells Claude to refer to the earlier Read tool result instead of re-reading
- Controlled by the `tengu_compact_line_prefix_killswitch` feature flag (enabled when killswitch is off)
- Helps conserve context window tokens in long conversations with repeated file reads

Evidence: Read caching message (search for `"File unchanged since last read"`) — `kf1()` at line ~163425


### Context Window Usage Breakdown

What: A new command that provides a breakdown of your current context window usage by category (system prompt, tools, messages, etc.).

Details:
- Shows how your context budget is being consumed across different categories
- Useful for understanding why you're running low on context or for optimizing long sessions

Evidence: Context window command (search for `"Breakdown of current context window usage by category"`)


### Slack Channel Autocomplete

What: When a connected Slack MCP server is detected, Claude Code now offers channel autocomplete with `#channel-name` syntax.

Details:
- Automatically discovers connected Slack MCP servers
- Searches for channels using the Slack MCP tool (supports public and private channels)
- Parses channel names from MCP tool responses and provides autocomplete suggestions
- Channel references use the `#channel-name` format in the input

Evidence: Slack channel integration (search for `"Failed to fetch Slack channels"`) — `AQK()` at line ~592144


### Expanded Git and PR Operation Tracking

What: Claude Code now tracks a broader set of git and GitHub PR operations, beyond just `git commit` and `gh pr create`.

Details:
- Newly tracked operations: `git push`, `gh pr edit`, `gh pr merge`, `gh pr comment`, `gh pr close`, `gh pr ready`
- Telemetry events emitted as `tengu_git_operation` with specific operation tags (e.g., `pr_edit`, `pr_merge`)
- Enables better understanding of Claude's git workflow patterns

Evidence: Expanded PR regex list (search for `"pr_edit"`) — `in6` at line ~308673


### Shell Safety: Zsh Equals Expansion and Bash Array Subscript Checks

What: New command safety checks that detect and flag potentially dangerous shell expansion patterns before execution.

Details:
- **Zsh equals expansion (`=cmd`)**: Detects commands containing zsh `=cmd` syntax, which could unexpectedly expand to command paths
- **Bash array subscript injection**: Flags commands where `$(cmd)` appears inside `[[ ... ]]` array subscripts, which bash arithmetically evaluates — a known injection vector

Evidence: Shell safety checks (search for `"Zsh equals expansion (=cmd)"` and `"bash arithmetically evaluates"`)


### Skill `anthropic/alwaysLoad` Metadata

What: Skills can now declare `anthropic/alwaysLoad` in their MCP metadata to be loaded automatically without requiring explicit invocation.

Details:
- Set via `_meta.["anthropic/alwaysLoad"]` on the skill server
- When true, the skill is loaded into the conversation automatically
- Useful for skills that provide always-relevant context or capabilities

Evidence: Always-load flag (search for `"anthropic/alwaysLoad"`)

### Overage Credit Grant and Extra Usage Display

The extra usage billing display has been significantly enhanced with an overage credit grant system. Users may now see their available extra usage credit amount (e.g., "$5 in extra usage") along with the message "On us. Works on third-party apps · /extra-usage". The system fetches grant info from a new `/overage_credit_grant` API endpoint and caches it per-organization.

Evidence: Overage credit display (search for `"On us. Works on third-party apps · /extra-usage"`) — `LE6()` at line ~424063


### Ultrareview Billing Now Org-Scoped

The ultrareview billing prompt now says "Your free ultrareviews for this organization are used" instead of the previous user-scoped message. This aligns with organization-level billing. The ultrareview billing dialog also now supports abort signals and shows a "Launching…" state.

Evidence: Org-scoped billing text (search for `"Your free ultrareviews for this organization are used"`)


### Compact Line Number Prefix Format

The Read tool output format is being updated from `spaces + line number + arrow` to a more compact `line number + tab` format. The Edit tool description dynamically adapts to tell the model which format is in use, reducing confusion when matching indentation.

Evidence: Dynamic format description (search for `"line number + tab"`) — controlled by `tengu_compact_line_prefix_killswitch`

**[Gradual Rollout]** — gated by `tengu_compact_line_prefix_killswitch` feature flag.


### XAA (Cross-App Access) Protocol Expansion

The MCP OAuth cross-app access (XAA) system has received a major expansion with full PRM (Protected Resource Metadata) discovery, AS (Authorization Server) metadata discovery, and a two-stage token exchange flow (ID token → ID-JAG → access token). New `--xaa`, `--client-id`, and `--client-secret` flags are now available for MCP server configuration. A dedicated `XaaTokenExchangeError` class provides better error handling with per-stage failure tracking.

Evidence: XAA protocol flow (search for `"XAA: starting cross-app access flow"`) — `eB1()` at line ~327934


### Auto Mode Plan-Gating Message

The message when auto mode is unavailable has been updated from "Auto mode temporarily unavailable" to the more informative "Auto mode is unavailable for your plan", clarifying that the limitation is plan-based rather than temporary.

Evidence: Plan-gating message (search for `"Auto mode is unavailable for your plan"`)


### Agent System Prompt Refinements

Agent system prompts have been refined with more specific guidance:
- New "don't gold-plate" phrasing: "Complete the task fully—don't gold-plate, but don't cut corners"
- More emphatic `$TMPDIR` guidance: "TMPDIR is automatically set to the correct sandbox-writable directory" (removed fallback variable mention)
- New guidance on failure handling: "diagnose why before switching tactics—read the error, check your assumptions, try a focused fix"
- Fork workers now use a `"Your directive:"` prefix with a `"fork-boilerplate"` key instead of embedded boilerplate text
- Summary format now strictly requires `<analysis>` and `<summary>` blocks with tool-call prohibition: "CRITICAL: Respond with TEXT ONLY. Do NOT call any tools"

Evidence: Agent prompt changes (search for `"Your directive:"` and `"CRITICAL: Respond with TEXT ONLY"`)


### Ultrareview Suggests `/ultrareview <PR#>` for Large Repos

When a repository is too large for full-repo review, the suggestion now says "Push a PR and use `/ultrareview <PR#>` instead" (previously referenced `/review`).

Evidence: Large repo message (search for `"Repo is too large. Push a PR and use"`)


### Plugin Telemetry Overhaul

Plugin analytics have been comprehensively restructured with hashed plugin IDs, scope classification (official, org, user-local, default-bundle), and per-session tracking of enabled plugins. Load failures are now categorized (network, not-found, permission, validation, unknown) and reported with plugin-level metadata.

Evidence: Plugin telemetry (search for `"tengu_plugin_enabled_for_session"`) — `sC()` at line ~431412


### Stdout JSON Guard

A new stdout guard (`streamJsonStdoutGuard`) diverts non-JSON lines that accidentally leak to stdout, preventing them from corrupting structured JSON output in headless/piped modes.

Evidence: Stdout guard (search for `"streamJsonStdoutGuard diverted non-JSON stdout line:"`)


### File Diff Rendering with Streaming I/O

The Write and Edit tool result renderers now use a new streaming file-read approach (`ur6()` / `Pm1()`) that reads files through file handles with buffer-based needle search, rather than loading entire files into memory. This improves performance for large file edits by seeking directly to the relevant region.

Evidence: Streaming file read (search for `"Skipping raw transcript read: file too large"`) — `Pm1()` at line ~317956

## Bug Fixes

- Directory removal is now more robust — uses a single `rmdir` call and handles `ENOTDIR`/`ENOENT`/`ENOTEMPTY` errors gracefully instead of manually checking if a directory is empty first (search for `"Could not remove directory at"`)
- Lock acquisition failure logging simplified — always wraps errors with a `cause` chain instead of conditionally stringifying (search for `"NON-FATAL: Lock acquisition failed"`)
- Skill usage tracking now debounces writes with a minimum interval, preventing rapid config updates when a skill is invoked repeatedly (search for `"skillUsage"` in `bI8()`)
- SwarmPermissionPoller now validates and drops malformed permission update entries with a warning instead of crashing (search for `"[SwarmPermissionPoller] Dropping malformed permissionUpdate"`)
- Advisor feedback message wording corrected: "will apply the feedback" (was: "will now apply the feedback.") (search for `"Advisor has reviewed the conversation and will apply the feedback"`)

## Notes

- The `CLAUDE_CODE_ENABLE_XAA=1` environment variable is required to use XAA features. Without it, servers configured with `oauth.xaa` will error on startup.
- The `--xaa`, `--client-id`, and `--client-secret` flags are only supported for HTTP/SSE MCP transports and will be ignored for stdio.
- The compact line prefix format and trusted device enrollment are behind feature flags and may not be active for all users yet.
