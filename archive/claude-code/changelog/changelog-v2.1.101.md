# Changelog for version 2.1.101

## Summary

This release introduces a significantly overhauled `/loop` command with a new dynamic self-pacing mode and autonomous loop instructions, adds MCP OAuth completion tooling, enables keybinding customization by default, and includes a new `CLAUDE_CODE_CERT_STORE` environment variable for configuring SSL certificate sources. Session resume now supports fuzzy matching by title, and a new vim-style kill ring improves terminal text editing.

## New Features


### MCP OAuth Completion Tool

What: A new `complete_authentication` tool for MCP servers that enables completing OAuth authorization flows directly within Claude Code, particularly useful in remote/SSH sessions where browser redirects don't work.

Usage:
When an MCP server requires OAuth authentication, Claude can now call the `authenticate` tool to start the flow, then use `complete_authentication` with the callback URL the user pastes from their browser's address bar.

Details:
- Handles the full OAuth callback flow: validates the URL contains an authorization code, resolves the pending auth promise, and reports success or failure
- Provides clear error messages when no OAuth flow is in progress, the callback URL is malformed, or authentication fails
- Specifically designed for remote sessions where `http://localhost:<port>/callback` pages fail to load but the URL in the address bar is still valid

Evidence: MCP OAuth completion handler (search for `"Complete an in-progress OAuth flow for the"`)


### CLAUDE_CODE_CERT_STORE Environment Variable

What: A new environment variable that gives users explicit control over which SSL/TLS certificate stores Claude Code uses, replacing the less flexible `--use-system-ca` flag approach.

Usage:
```bash
# Use both bundled and system certificates (default)
export CLAUDE_CODE_CERT_STORE=bundled,system

# Use only system certificates
export CLAUDE_CODE_CERT_STORE=system

# Use only bundled certificates
export CLAUDE_CODE_CERT_STORE=bundled
```

Details:
- Accepts comma-separated values: `bundled` and/or `system`
- Defaults to `["bundled", "system"]` when not set
- Falls back to the `--use-system-ca` / `--use-openssl-ca` flags if the env var is not present
- Unrecognized sources are logged as warnings and ignored
- The old `--use-system-ca` flag still works as a fallback

Evidence: Certificate store configuration (search for `"CLAUDE_CODE_CERT_STORE"`)


### Resume Sessions by Title

What: The `--resume` flag now accepts session titles in addition to UUIDs, with fuzzy matching support.

Usage:
```bash
# Resume by UUID (existing behavior)
claude --resume 550e8400-e29b-41d4-a716-446655440000

# Resume by session title (new)
claude --resume "my refactoring session"

# Also works with --print mode
claude -p --resume "my session title"
```

Details:
- When the provided value is not a valid UUID, Claude Code now searches for matching session titles
- If multiple sessions match, the user is prompted to disambiguate with a list of matching session IDs
- Error messages have been updated: `"Error: --resume requires a valid session ID or session title when used with --print"`

Evidence: Session title matching (search for `"is not a UUID and does not match any session title"`)


### Vim Kill Ring and Yank Support

What: Full vim-style kill ring (yank ring) implementation for the terminal text editor, supporting kill accumulation, yank, and yank-pop cycling.

Details:
- New `killRing` data structure with `push()`, `getLastKill()`, `yankPop()`, `recordYank()`, and `canYankPop()` operations
- Kill accumulation: consecutive kills are merged into a single ring entry
- Yank-pop (`Ctrl+Y` then `Alt+Y` in emacs-style) cycles through the kill ring history
- Ring size is bounded to prevent unbounded memory growth

Evidence: Kill ring implementation (search for `"getLastKill"` and `"yankPop"`)


### Hook Event Validation

What: Settings files now validate hook event names and produce clear warnings for unrecognized events, helping users catch typos in their configuration.

Details:
- Unknown hook events are removed from the parsed configuration and a warning is emitted
- Warning messages include the invalid event name, valid events list, and a link to documentation
- Applies to all settings sources: local, project, remote managed, and SDK inline settings
- Example warning: `Unknown hook event "PreTooluse" was ignored. Valid events: PreToolUse, PostToolUse, UserPromptSubmit, SessionStart, SessionEnd, Stop`

Evidence: Hook validation (search for `"Unknown hook event"` and `"Not a recognized hook event"`)


### File Attribution Tracking

What: Claude Code now tracks per-file edit contributions by computing the magnitude of changes, enabling better understanding of how much Claude contributed to each file.

Details:
- Computes `claudeContribution` based on the diff between old and new content for each edit
- Tracks both regular edits and file deletions
- Logs attribution events: `"Attribution: Tracked N chars for path/to/file"`
- Uses content hashing to detect unchanged files
- Supports bulk edit tracking for batch operations

Evidence: File attribution system (search for `"Attribution: Tracked"`)


### Worktree-Aware Session Resume

What: When resuming a session that was running in a git worktree, the resume instructions now automatically include the `--worktree` flag.

Details:
- The "Resume this session with:" message now dynamically includes `--worktree <name>` when the session was created in a worktree
- Preserves worktree context across session restarts

Evidence: Worktree resume instructions (search for `"Resume this session with: claude"`)


### Worktree Orphan Self-Healing

What: Automatic detection and cleanup of orphaned worktree directories that can accumulate when sessions crash or are interrupted.

Details:
- Detects orphaned worktree directories (directories that exist but have no corresponding git worktree entry)
- Checks that the worktree has no unpushed commits before self-healing to prevent data loss
- Falls back to recursive directory cleanup if `git worktree remove` fails
- Logs cleanup actions: `"[worktree] removed orphaned worktree directory at ..."`

Evidence: Orphan worktree cleanup (search for `"Cannot self-heal orphaned worktree"`)


### SDK Protocol: request_user_dialog

What: A new SDK protocol message type `request_user_dialog` that enables tool-driven blocking dialogs, replacing the previous Ink JSX-based approach.

Details:
- New message types: `request_user_dialog` (request) and `user_dialog_response` (response)
- Uses `dialog_kind` as an open string union to identify which dialog to render (known kinds: `"it2_setup"`, `"computer_use_approval"`)
- Enables SDK consumers to render custom dialogs and return structured results
- Description: "Requests the SDK consumer to render a tool-driven blocking dialog and return the user choice"

Evidence: Dialog protocol (search for `"request_user_dialog"`)

## Improvements


### Keybinding Customization Now Enabled by Default

The keybinding customization feature, which was previously gated behind a feature flag defaulting to false, now defaults to enabled. Users can customize their keyboard shortcuts via `~/.claude/keybindings.json` without needing to wait for a server-side flag rollout. The error message has been updated from "This feature is currently in preview" to "Keybinding customization is disabled in this environment" for cases where it is explicitly disabled.

Evidence: Keybinding flag default change (search for `"tengu_keybinding_customization_release"` — default changed from `!1` to `!0`)


### Improved Refusal Error Messages

API refusal responses now include the model's explanation when available, providing more context about why a request was declined. The explanation text is truncated to 400 characters and appended to the standard policy violation message.

Evidence: Refusal message enhancement (search for `"has_explanation"`)


### Enhanced Rate Limit Display

Rate limit errors now display human-readable descriptions (e.g., "session limit", "weekly limit", "extra usage limit") instead of internal identifiers, and show countdown timers to when limits reset.

Evidence: Rate limit descriptions (search for `"session limit"` and `"weekly limit"`)


### Improved Ultraplan Cloud Dialog

The ultraplan launch dialog now shows context-aware messaging based on whether the git remote can be cloned:
- If cloning is viable: "This will try to clone your git remote and fall back to uploading this repository."
- Otherwise: "This will upload your repository to Claude Code on the web."

Evidence: Ultraplan dialog text (search for `"This will try to clone your git remote"`)


### Plugin Dependency Version Checking

Plugin dependency validation now includes version constraint checking. When a plugin requires a specific version of a dependency, Claude Code validates the installed version matches the constraint and provides a clear error message when it doesn't.

Evidence: Dependency version validation (search for `"dependency-version-unsatisfied"`)


### Improved Error Coloring in CLI Output

Error messages printed to the console now use red color formatting for improved visibility.

Evidence: Red error output (search for `"red"` near `console.error`)


### Mouse Wheel Event Support

Terminal mouse wheel events now properly dispatch as `wheel` DOM events with `deltaY`, `deltaX`, and modifier key tracking (`ctrl`, `shift`, `meta`), enabling scroll-based interactions in the UI.

Evidence: Wheel event class (search for `"wheelup"` and `"wheeldown"`)


### Improved Plugin Status Messages

A new `all-plugins-project-installed` status message informs users when all available plugins are already installed for their project, providing clearer feedback during plugin management.

Evidence: Plugin status (search for `"All available plugins are installed for this project"`)


### OAuth 401 Recovery via SDK Callback

OAuth token refresh now attempts an SDK callback-based recovery when no local refresh token is available. This provides a fallback path for SDK consumers that manage their own token lifecycle.

Evidence: SDK OAuth recovery (search for `"SDK getOAuthToken callback"`)


### Settings Validation Warnings with Suggestions

Settings validation errors now include suggestion text when available, helping users understand how to fix configuration issues.

Evidence: Settings suggestions (search for `".suggestion"`)


### Improved Signal Listener Error Handling

The internal event emitter now catches errors from individual listeners and aggregates them using `AggregateError`, preventing a single failing listener from blocking other listeners.

Evidence: Signal error handling (search for `"Signal listener(s) threw"`)


### Context Window Cache Token Tracking

The context window visualization now tracks cache token usage (both creation and read tokens) alongside standard input/output tokens, giving users better visibility into prompt caching behavior.

Evidence: Cache token tracking (search for `"cache_creation_input_tokens"`)


### MCP Registry Pagination

The MCP server registry fetch now supports pagination, fetching up to 100 servers per page and following cursor-based pagination. It also supports a new BFF (Backend for Frontend) registry endpoint alongside the legacy one.

Evidence: MCP registry pagination (search for `"api/directory/servers"`)


### Version Check in Essential-Traffic-Only Mode

When running in essential-traffic-only mode (e.g., `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`), the version display now shows a specific message instead of a generic failure: "Version check skipped (essential-traffic-only mode)".

Evidence: Version check message (search for `"essential-traffic-only mode"`)

## Bug Fixes

- Fixed worktree removal to include fallback directory cleanup when `git worktree remove` fails, preventing orphaned directories from accumulating (search for `"git worktree remove failed"`)
- Fixed settings mutation bug where remote managed settings could be modified in-place; now uses `structuredClone` before validation (search for `"structuredClone"`)
- Fixed null safety issue in file path handling that could cause crashes when `filePath` is undefined (search for `"filePath: q = ''"`)
- Fixed OAuth callback abort handling to use proper `AbortController`-based cleanup, preventing resource leaks (search for `"AbortController"`)
- Fixed retention cleanup to skip when userSettings source is disabled via `--setting-sources`, preventing unintended data deletion (search for `"Skipping retention cleanup"`)
- Fixed terminal output sanitization to filter ANSI escape sequences more aggressively, preventing garbled output (search for `"charCodeAt(0) === 27"`)

## In Development

Features with infrastructure added but not yet enabled. These are shipped "dark" and may become available in future versions.


### /loop Dynamic Self-Pacing Mode [In Development]

What: A major enhancement to the `/loop` command that allows the model to dynamically choose its own iteration timing instead of requiring a fixed interval.

Status: Feature-flagged via `tengu_kairos_loop_dynamic` (defaults to false) and `tengu_kairos_loop_prompt` (defaults to false)

Details:
- When enabled, `/loop` can be invoked without an interval, and the model decides how long to wait between iterations based on the task context
- Uses a new `ScheduleWakeup` tool for the model to request its next wake-up with a specific delay (clamped to 60–3600 seconds)
- Includes sophisticated cache-aware delay selection: delays under 270s keep the prompt cache warm, delays over 300s incur a cache miss
- Supports `loop.md` task files in `.claude/loop.md` or `~/loop.md` that define recurring task instructions
- Introduces sentinel values `<<autonomous-loop-dynamic>>` and `<<loop.md-dynamic>>` for the dynamic pacing variants
- Includes a detailed autonomous loop system prompt that instructs the model on how to behave during timer-based autonomous operation, including PR maintenance, CI monitoring, and scope management
- The system prompt emphasizes maintaining user trust: "Acting on what the conversation already established is safe and valuable. Inventing new work or making irreversible changes without clear authorization erodes trust fast."
- Loops have a maximum age limit, after which they automatically age out

Evidence: Dynamic loop system (gated by `tengu_kairos_loop_dynamic` and `tengu_kairos_loop_prompt`, search for `"Autonomous-loop instructions"`)


### /loops Management Command [In Development]

What: A dedicated command to list, create, and delete recurring loops and stop-hooks.

Status: Disabled (`isEnabled: () => !1`)

Details:
- Full React-based UI for managing loops with keyboard navigation
- Supports creating two types: cron-based recurring loops ("every N") and stop-hooks ("until condition")
- Shows existing loops with their schedule, prompt, and ID
- Keyboard shortcuts: `n` to create new, `d` to delete, `up`/`down` to navigate, `escape` to close
- Includes tab-switching between "every" (cron) and "until" (stop-hook) creation modes

Evidence: Loops management UI (search for `"List, create, and delete recurring loops and stop-hooks"`)


### /update Command [In Development]

What: An in-session command to switch to the latest Claude Code version while preserving the current conversation.

Status: Disabled (`isEnabled: () => !1`) and hidden (`isHidden: !0`)

Details:
- Description: "Switch to the latest version (conversation continues)"
- Does not support non-interactive mode
- When enabled, would allow users to upgrade without losing their session context

Evidence: Update command (search for `"Switch to the latest version (conversation continues)"`)


### Away Summary [In Development]

What: Automatically generates a brief task summary when the user steps away (window blur detected), so they can quickly re-orient when returning.

Status: Feature-flagged via `tengu_sedge_lantern` (defaults to false)

Details:
- Triggered by terminal focus/blur events tracked via the presence system
- Generates summaries under 40 words in 1-2 plain sentences, naming the task and next action
- Summary is added as a system message of subtype `away_summary`
- Uses cached parameters to avoid expensive re-computation
- Cannot use tools (text-only generation)

Evidence: Away summary generation (search for `"The user stepped away and is coming back"`)


### Cloud-Based Loop Scheduling Offer [In Development]

What: When a user sets up a long-interval loop (≥60 minutes or daily cadence), Claude would offer to run it as a cloud-based scheduled task instead of a local session loop.

Status: Feature-flagged via `tengu_surreal_dali` (defaults to false)

Details:
- Generates a conditional prompt offering cloud-based scheduling as an alternative to local loops
- Explains that daily-cadence loops won't fire before the session closes
- Provides guidance on using the `/schedule` command for cloud execution
- Includes differentiation text: "Runs until you close this session · For durable cloud-based loops, use /schedule"

Evidence: Cloud scheduling offer (gated by `tengu_surreal_dali`, search for `"Offer cloud first"`)


### MCP Directory BFF [In Development]

What: A new Backend-for-Frontend endpoint for the MCP server directory, with configurable visibility filters.

Status: Feature-flagged via `tengu_mcp_directory_bff` (defaults to false)

Details:
- New `https://api.anthropic.com/api/directory/servers` endpoint alongside the legacy `mcp-registry/v0/servers` endpoint
- Supports configurable visibility categories: `commercial`, `gsuite`, `enterprise`, `health`
- Uses cursor-based pagination with up to 500 results per page
- Controlled by `tengu_mcp_directory_visibility` flag for the visibility filter list

Evidence: MCP directory BFF (gated by `tengu_mcp_directory_bff`, search for `"api/directory/servers"`)

## Notes

The `/loop` command continues to work in its existing fixed-interval mode (e.g., `/loop 5m /babysit-prs`). The new dynamic self-pacing mode is behind feature flags and will be gradually rolled out. When enabled, running `/loop` without an interval will activate dynamic mode where the model picks its own delay between iterations.

The `CLAUDE_CODE_CERT_STORE` environment variable supersedes the `--use-system-ca` CLI flag for controlling certificate store behavior. Users on enterprise networks with custom CA certificates should consider switching to this env var for more explicit control.
