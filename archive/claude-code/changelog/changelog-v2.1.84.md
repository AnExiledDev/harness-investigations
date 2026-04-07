# Changelog for version 2.1.84


## Summary

This is a major release that introduces an in-process Computer Use MCP server for macOS (with tiered application permissions and guided teach mode), a full PowerShell tool for Windows, a new `--task-budget` CLI flag for controlling API output tokens, and a "You've been away" idle re-engagement prompt. The release also renames "remote sessions" to "cloud sessions" throughout the UI, adds the `TaskCreated` hook event, and includes numerous improvements to permission dialogs, MCP connector deduplication, and theme detection.


### Computer Use MCP Server (macOS)

What: A comprehensive, in-process MCP server that allows Claude to control macOS desktop applications — clicking, typing, scrolling, dragging, and taking screenshots — with a tiered permission system.

Usage:
```bash
claude --computer-use-mcp
```

Details:
- Applications must be explicitly approved by the user via `request_access` before any interaction
- Three permission tiers: **read** (screenshots only, no interaction), **click** (visible + plain left-click), and **full** (typing, key presses, modifier-clicks, drag-drop)
- Browsers and trading apps default to "read" tier; terminals/IDEs default to "click" tier; other apps get "full"
- Tool set includes: `screenshot`, `left_click`, `right_click`, `middle_click`, `double_click`, `triple_click`, `type`, `key`, `hold_key`, `scroll`, `mouse_move`, `left_mouse_down`, `left_mouse_up`, `left_click_drag`, `mouse_position`, `computer_batch`, `activate_app`, `switch_display`, `read_clipboard`, `write_clipboard`, `zoom`, `wait`, `list_granted_applications`
- `computer_batch` executes a sequence of actions in ONE tool call, avoiding round-trip latency between steps
- Multi-monitor support with `switch_display` to capture different monitors
- Clipboard read/write requires separate grant flags (`clipboardRead`, `clipboardWrite`)
- System-level key combos (e.g. Cmd+Q, Ctrl+Alt+Delete) require the `systemKeyCombos` grant
- Pixel comparison validation detects when screen content changed since last screenshot
- Includes a comprehensive deny-list for sensitive apps (financial, crypto wallets, etc.) that cannot be controlled
- macOS Accessibility and Screen Recording permissions required
- Esc hotkey registered for user to abort computer control at any time

Evidence: In-process Computer Use MCP server (search for `"In-process Computer Use MCP server started"`, `"--computer-use-mcp"`, `"request_access"`)


### Computer Use Teach Mode

What: A guided-tour teaching system built on top of Computer Use that allows Claude to walk users through UI workflows step-by-step with interactive tooltips.

Details:
- `request_teach_access` initializes teach mode with app permissions and a stated reason (shown in approval dialog)
- `teach_step` shows a tooltip with explanation text, optional anchor coordinates (pointing arrow), and actions to execute when user clicks "Next"
- `teach_batch` batches multiple steps into one round-trip for predictable sequences on the same page
- User can click "Exit" at any point to end the tour
- Text emitted outside teach_step calls is NOT visible until teach mode ends
- During teach mode, `request_access` cannot add new permissions (would hide the tooltip UI)
- Returns screenshots after each step so Claude can anchor the next step's coordinates

Evidence: Teach mode tools (search for `"teach_step"`, `"teach_batch"`, `"request_teach_access"`)


### PowerShell Tool (Windows)

What: A dedicated PowerShell command execution tool for Windows users, providing native PowerShell syntax support with comprehensive security analysis.

Details:
- Enabled via the `CLAUDE_CODE_USE_POWERSHELL_TOOL` environment variable on Windows
- Uses `pwsh` (PowerShell 7+) for command parsing and execution
- Full AST-based security analysis of PowerShell commands before execution
- Validates PowerShell-specific patterns: cmdlet names, parameter types, pipeline chains, `.NET` type usage, script blocks
- Recognizes dangerous patterns: `Invoke-Expression`, encoded commands, COM object creation, module loading, splatting, UNC paths
- Read-only cmdlets (e.g. `Get-ChildItem`, `Get-Content`, `Select-String`, `Get-Process`) are auto-allowed
- Handles PowerShell-specific security concerns: `-FilePath` execution, `-Command` re-invocation, `Start-Process` nesting
- Provides PowerShell syntax guidance in tool description (variable syntax, pipe objects, here-strings, cmdlet naming)
- Falls back gracefully if PowerShell is not installed
- Enterprise policy enforcement: sandboxing policy blocks shell execution on native Windows when sandbox is unavailable

Evidence: PowerShell tool implementation (search for `"PowerShell command"`, `"CLAUDE_CODE_USE_POWERSHELL_TOOL"`, `"Run PowerShell command"`)


### `--task-budget` CLI Flag

What: A new hidden CLI flag that sets an API-side task budget in output tokens via `output_config.task_budget`.

Usage:
```bash
claude --task-budget 50000
```

Details:
- Value must be a positive integer (number of tokens)
- Controls the API's output token budget for the task
- Hidden from `--help` output (intended for programmatic/advanced use)

Evidence: Task budget flag (search for `"--task-budget"`, `"task-budgets-2026-03-13"`)


### "You've Been Away" Re-engagement Prompt

What: When returning to a conversation after being idle, Claude Code now shows an interactive prompt suggesting you may want to start fresh.

Details:
- Displays idle time (e.g., "You've been away 2h 15m") and conversation token count
- Three options: "Continue this conversation", "Send message as a new conversation" (clears context), or "Don't ask me again"
- Helps save usage on stale conversations where starting fresh would be more efficient

Evidence: Re-engagement UI component (search for `"You've been away"`, `"Continue this conversation"`, `"Send message as a new conversation"`)


### TaskCreated Hook Event

What: A new hook event type that fires when a task (e.g., from `/loop` or teammate creation) is being created.

Details:
- Hook receives JSON input with `task_id`, `task_subject`, `task_description`, `teammate_name`, and `team_name`
- Exit code 0: stdout/stderr not shown
- Exit code 2: show stderr to model and prevent task creation
- Other exit codes: show stderr to user but proceed
- Allows organizations to gate or customize task creation behavior

Evidence: TaskCreated hook (search for `"TaskCreated"`, `"When a task is being created"`)


### "Open in Claude Code on the Web" Action

What: Ultraplan and ultrareview sessions now offer an "Open in Claude Code on the web" action, allowing users to view and interact with cloud sessions directly in the browser.

Details:
- Available in the ultraplan and ultrareview status bar menus
- Links to the cloud session URL at `code.claude.com`

Evidence: Web open action (search for `"Open in Claude Code on the web"`)


### WorktreeCreate Hook Output

What: The `WorktreeCreate` hook event now supports hook-specific output providing the absolute path to the created worktree directory.

Details:
- JavaScript hooks return `{ hookEventName: "WorktreeCreate", worktreePath: "<path>" }`
- Command hooks print the path on stdout instead
- Enables custom worktree workflows via hooks

Evidence: WorktreeCreate hook output (search for `"Hook-specific output for the WorktreeCreate event"`)


### "Remote Sessions" Renamed to "Cloud Sessions"

The UI now uses "cloud session" / "cloud sessions" terminology instead of "remote session" / "remote sessions" throughout the ultraplan and session management interfaces.

Evidence: Terminology change (search for `"cloud session"`, `"cloud sessions"`)


### Improved Permission Denial Dialog

The permission prompt now offers a "Deny, and tell Claude what to do differently" option (with Esc shortcut), giving users a clear way to deny a tool call and redirect Claude's approach instead of just blocking.

Evidence: Deny option (search for `"Deny, and tell Claude what to do differently"`)


### Theme Detection: "Auto (match terminal)" Replaces "Auto (follow system)"

The automatic theme setting now reads the `COLORFGBG` environment variable (set by many terminals) to detect whether the terminal uses a light or dark background, rather than querying macOS system settings. The label changed from "Auto (follow system)" to "Auto (match terminal)" to reflect this behavior.

Evidence: Theme detection (search for `"Auto (match terminal)"`, `"COLORFGBG"`)


### MCP Connector Deduplication

When claude.ai provides built-in MCP connectors that duplicate manually-configured servers (matching by server URL), the built-in connector is automatically suppressed to avoid conflicts. A debug log message is emitted.

Evidence: Connector dedup (search for `"Suppressing claude.ai connector"`)


### Server Instructions Truncation

MCP server instructions that exceed the maximum allowed length are now truncated with a logged warning, rather than potentially causing errors.

Evidence: Truncation handling (search for `"Server instructions truncated"`)


### Skill Content Truncation During Compaction

During conversation compaction, large skill/prompt content is now truncated with a helpful message: "[... skill content truncated for compaction; use Read on the skill path if you need the full text]". This reduces token usage during compaction while preserving the ability to re-read full content.

Evidence: Skill truncation (search for `"skill content truncated for compaction"`)


### Dynamic Agent Type Notifications

When agent types change mid-conversation (e.g., from plugin/MCP server updates), Claude now receives explicit notifications: "New agent types are now available for the Agent tool" and "The following agent types are no longer available" — helping it stay aware of available capabilities.

Evidence: Agent notifications (search for `"New agent types are now available"`, `"The following agent types are no longer available"`)


### API Request ID Tracking (`x-client-request-id`)

All API requests to Anthropic's first-party service now include an `x-client-request-id` header. When API errors occur, the request ID is surfaced in the error message ("give this to the API team for server-log lookup"), making it easier to debug issues with Anthropic support.

Evidence: Request ID tracking (search for `"x-client-request-id"`, `"API error x-client-request-id="`)


### Consecutive Auth Failure Detection

The CCR (Claude Code Remote) client now tracks consecutive authentication failures. If multiple auth failures occur with a valid-looking token, the client exits cleanly instead of retrying indefinitely, preventing hung sessions.

Evidence: Auth failure handling (search for `"consecutive auth failures with a valid-looking token"`)


### Ultraplan Stop Confirmation

Stopping an ultraplan session now shows a confirmation dialog ("Stop ultraplan?") with "Terminate session" and "Back" options, preventing accidental cancellation.

Evidence: Stop confirmation (search for `"Stop ultraplan?"`, `"Terminate session"`)


### Improved Remote Control Error Messages

Remote Control error messages are now more specific and actionable:
- Requires a claude.ai subscription (not just login)
- Explains that long-lived tokens from `setup-token` or `CLAUDE_CODE_OAUTH_TOKEN` are limited to inference-only
- Provides clear guidance to run `claude login`

Evidence: RC error messages (search for `"Remote Control requires a claude.ai subscription"`, `"Remote Control requires a full-scope login token"`)


### OAuth URL Migration

The claude.ai OAuth authorization endpoint has been updated from `claude.ai/oauth/authorize` to `claude.com/cai/oauth/authorize`.

Evidence: URL change (search for `"claude.com/cai/oauth/authorize"`)


### Configurable MCP Tool Output Token Limits

The maximum MCP tool output size is now configurable via both the `MAX_MCP_OUTPUT_TOKENS` environment variable and the `tengu_satin_quoll` feature flag, instead of being hardcoded at 25,000 tokens.

Evidence: Configurable limits (search for `"MAX_MCP_OUTPUT_TOKENS"`) — function `PV8` at line ~319854


### Plugin Source Tracking

Plugin entries now include a `source` field in `"name@marketplace"` format, with sentinels `"name@inline"` for `--plugin-dir` session plugins and `"name@builtin"` for built-in plugins. This enables better identification and management of plugin origins.

Evidence: Plugin source field (search for `'@internal Plugin source identifier in "name\\@marketplace" format'`)


### Channel Plugin Allowlists

A new `allowedChannelPlugins` managed setting allows Teams/Enterprise admins to restrict which channel plugins can be enabled. When set, it replaces the default Anthropic allowlist — admins decide which plugins their organization can use.

Evidence: Channel allowlist (search for `"allowedChannelPlugins"`, `"Teams/Enterprise allowlist of channel plugins"`)


### Custom Model Capability Overrides

Third-party API users can now declare model capabilities via environment variables: `ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES`, `ANTHROPIC_DEFAULT_SONNET_MODEL_SUPPORTED_CAPABILITIES`, and `ANTHROPIC_DEFAULT_HAIKU_MODEL_SUPPORTED_CAPABILITIES`. These are comma-separated capability strings that Claude Code checks when deciding which features to enable for custom models.

Evidence: Capability env vars (search for `"ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES"`)


### PowerShell Output Persistence

Long command outputs that exceed the inline display limit are now persisted to disk, with the tool result including the file path and total output size. This prevents loss of large command outputs.

Evidence: Output persistence (search for `"Path to persisted full output when too large for inline"`, `"Total output size in bytes when persisted"`)


### Ultraplan Status Bar Improvements

The ultraplan footer now shows a "ready · shift+↓ to view" hint and supports a `footer:down` keybinding to quickly scroll to the ultraplan status. Cloud session status is displayed inline with "ultraplan · cloud session · No need to wait — Claude will notify you when done."

Evidence: Status bar updates (search for `"ready · shift+↓ to view"`, `"footer:down"`)


### Slack Message Link Parsing

When a user's message contains a `message_link` field pointing to a Slack archive URL, Claude Code now parses the channel information from the link. This enables richer context when conversations originate from Slack integrations.

Evidence: Slack link parsing (search for `"message_link"`, regex `slack\.com\/archives`)


## Bug Fixes

- Fixed interactive prompt detection: commands that appear to be waiting for interactive input now get a more helpful error message suggesting piped input or non-interactive flags (search for `"appears to be waiting for interactive input"`)

- Fixed GitHub issue link rendering to use `owner/repo#123` format instead of just `#123`, producing proper cross-repository links (search for `"owner/repo#123"`)

- Fixed table cell rendering by tracking blank cells (`cellIsBlank` property), improving display of sparse tabular data

- Fixed auto-backgrounded task tracking: the tool result now includes a `was_auto_backgrounded` field when a command was auto-backgrounded by the assistant-mode blocking budget (search for `"auto-backgrounded by the assistant-mode blocking budget"`)


### Agent List in System Messages [Gradual Rollout]

What: Agent type descriptions can be injected directly into system-reminder messages instead of only in the Task tool description.

Status: Feature-flagged via `tengu_agent_list_attach` (default: false). Can be overridden with `CLAUDE_CODE_AGENT_LIST_IN_MESSAGES` environment variable.

Details:
- When enabled, available agent types are listed in `<system-reminder>` messages in the conversation
- Agent type descriptions use the format: `- agentType: whenToUse (Tools: toolList)`
- This helps models discover available agent types more reliably

Evidence: Agent list feature (gated by `tengu_agent_list_attach`, search for `"CLAUDE_CODE_AGENT_LIST_IN_MESSAGES"`)
