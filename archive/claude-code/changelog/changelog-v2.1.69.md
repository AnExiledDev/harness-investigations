# Changelog for version 2.1.69


## Summary
This release is a major update that introduces Remote Control Server mode for persistent multi-session hosting, an Ultraplan feature for remote session planning, a completely overhauled memory system with typed categories, live plugin reloading via `/reload-plugins`, the `--prefill` CLI flag, native mouse-based text selection and copying, scrollable UI views, auto theme detection, MCPB bundle tooling, and significant improvements to ToolSearch, command safety, and the hooks system.


### Remote Control Server Mode
What: A new `server` subcommand for `claude remote-control` that runs as a persistent server accepting multiple concurrent sessions from claude.ai/code.

Usage:
```bash
# Start a server where all sessions share the current directory
claude remote-control server

# Each session gets an isolated git worktree (max N sessions)
claude remote-control server --spawn-worktree-sessions [<N>]

# All sessions share the current directory (default behavior, max N sessions)
claude remote-control server --spawn-same-dir-sessions [<N>]

# Additional server options
claude remote-control server --idle-timeout <ms>    # Timeout for detached sessions
claude remote-control server --max-sessions <n>     # Max concurrent sessions
claude remote-control server --workspace <dir>      # Default working directory
claude remote-control server --auth-token <token>   # Bearer token for auth
claude remote-control server --host <string>        # Bind address
claude remote-control server --port <number>        # Listen port
```

Details:
- Runs as a persistent daemon that accepts connections without pre-creating an initial session
- Supports `cc+unix://` protocol for Unix domain socket connections
- Session management with `server-sessions.json` persistence and `server.lock` for single-instance enforcement
- Configurable spawn modes: shared directory (default) or isolated git worktrees
- Sessions can be created, attached, detached, and destroyed independently
- Policy-controllable via `allow_remote_control` organization policy

Evidence: Remote Control server mode (search for `"Start a Claude Code session server"`, `"--spawn-worktree-sessions"`, `"server-sessions.json"`)


### Ultraplan
What: A new remote-session-based planning mode that generates comprehensive implementation plans using a dedicated remote session.

Details:
- Triggered when planning complex implementations
- Runs a remote session that produces a structured `<ultraplan>` block
- Displays "Ultraplanning…" progress indicator during generation
- The generated plan is written to a plan file for user review
- After review, the user can approve and proceed to implementation

Evidence: Ultraplan feature (search for `"Ultraplanning…"`, `"Ultraplan complete"`, `"ultraplan"`)


### `--prefill` CLI Flag
What: Pre-fill the prompt input with text without automatically submitting it, allowing the user to review and edit before sending.

Usage:
```bash
claude --prefill "implement a function that"
```

Details:
- Text appears in the input field ready for editing
- Unlike `--print`, does not auto-submit — the user can modify the prompt before pressing Enter
- Useful for templates, repetitive prompts, or workflow scripting

Evidence: Prefill flag (search for `"--prefill"`, `"Pre-fill the prompt input with text without submitting it"`)


### `/reload-plugins` Command
What: Reload and activate plugin changes in the current session without needing to restart Claude Code.

Usage:
```
/reload-plugins
```

Details:
- Activates pending plugin installations, removals, and configuration changes
- Replaces the previous behavior of requiring a full restart after plugin changes
- Messages like "Run /reload-plugins to activate" now appear after plugin changes instead of "Restart Claude Code"

Evidence: Plugin reload (search for `"/reload-plugins"`, `"Activate pending plugin changes in the current session"`)


### Mouse-Based Text Selection and Copy
What: Native mouse text selection with drag-to-select and clipboard copy support in the terminal UI.

Details:
- Click and drag to select text in the terminal output
- Selected text can be copied to the system clipboard via OSC 52 escape sequence
- `noSelect` regions prevent selection of UI chrome (status bars, borders) while allowing content selection
- Selection state tracks anchor/focus positions with full drag handling
- `from-left-edge` option extends no-select regions from the left edge of the terminal

Evidence: Text selection system (search for `"isDragging"`, `"copySelection"`, `"noSelect"`)


### Scrollable UI Views
What: Terminal UI components can now use `overflowY: "scroll"` to create scrollable content areas with sticky-scroll behavior.

Details:
- New `scroll` overflow mode alongside existing `hidden` and `visible`
- `stickyScroll` attribute auto-scrolls to bottom as new content arrives
- Tracks `scrollHeight`, `scrollViewportHeight`, and `scrollTop` for programmatic scroll control
- Content outside the visible viewport is culled for rendering performance

Evidence: Scroll support (search for `"stickyScroll"`, `"scrollViewportHeight"`, `overflowY`)


### Auto Theme Detection
What: Claude Code can now automatically detect the system light/dark theme setting and follow it.

Details:
- New "Auto (follow system)" theme option
- On macOS, reads `AppleInterfaceStyle` from system defaults to detect Dark Mode
- Falls back to "dark" on non-macOS platforms
- Theme updates when toggling between light and dark mode

Evidence: Auto theme (search for `"Auto (follow system)"`, `"AppleInterfaceStyle"`)


### Memory System Overhaul
What: Complete restructuring of the persistent memory system with typed categories, frontmatter format, and two-step save process.

Details:
- Four memory types: `user` (preferences/role), `feedback` (corrections/guidance), `project` (ongoing work context), and `reference` (external system pointers)
- Memories use markdown files with YAML frontmatter (`name`, `description`, `type` fields)
- Two-step save: write the memory file, then add a pointer in the memory index
- Clear guidance on what NOT to save (code patterns, git history, ephemeral details)
- When users correct information stated from memory, the stored entry must be updated
- `CLAUDE_COWORK_MEMORY_PATH_OVERRIDE` environment variable to customize the memory directory

Evidence: Memory system (search for `"## Types of memory"`, `"## What NOT to save in memory"`, `"CLAUDE_COWORK_MEMORY_PATH_OVERRIDE"`)


### MCPB Bundle Tooling
What: Infrastructure for creating, validating, packing, and unpacking MCP Bundle (MCPB) files — a packaging format for MCP server plugins.

Usage:
```bash
mcpb pack       # Create a .mcpb bundle from a directory
mcpb validate   # Validate a manifest.json
```

Details:
- Interactive manifest.json creation wizard with prompts for name, version, tools, prompts, screenshots, and more
- `.mcpbignore` support to exclude files from bundles
- Schema validation for manifest files
- Bundle unpacking and verification
- Supports Node.js and Python version constraints
- Platform compatibility settings (macOS, Linux, Windows)

Evidence: MCPB support (search for `"A MCPB bundle"`, `"mcpb pack"`, `".mcpbignore"`)


### git-subdir Plugin Source
What: Plugins can now be sourced from a subdirectory within a larger repository (monorepo support).

Details:
- Uses sparse checkout (`--filter=tree:0`) to minimize bandwidth for monorepo plugins
- Only the specified subdirectory is materialized; the rest of the repo is not downloaded
- Requires git version 2.25 or later for cone mode support
- Falls back to unshallow fetch if sparse-checkout fails

Evidence: git-subdir support (search for `"git-subdir"`, `"Subdirectory within the repo containing the plugin"`)


### Binary Content Handling
What: Improved detection and handling of binary file content, with disk-based storage for large binary results.

Details:
- Sophisticated binary detection using byte analysis (null bytes, control characters)
- Extensive list of known binary file extensions (images, audio, video, archives, executables, etc.)
- Binary content from tool results can be saved to disk and referenced by path
- Support for Office documents, archives, and other binary MIME types

Evidence: Binary content (search for `"Binary content ("`, `"Binary content could not be saved to disk"`)


### New Hook Events
What: Three new hook event types for more granular automation control.

Details:
- `InstructionsLoaded`: Fires when an instruction file (CLAUDE.md or rule) is loaded
- `TaskCompleted`: Can prevent continuation after task completion (`"TaskCompleted hook prevented continuation"`)
- `TeammateIdle`: Can prevent continuation when a teammate goes idle (`"TeammateIdle hook prevented continuation"`)
- Hooks support `agent_type` and `agent_id` context fields for subagent-aware automation
- Background hooks with `async` mode that wake the model on exit code 2

Evidence: New hooks (search for `"InstructionsLoaded"`, `"TaskCompleted hook prevented continuation"`, `"TeammateIdle hook prevented continuation"`)


### Settings Visibility and Debug
What: New settings API that returns effective merged settings plus raw per-source settings in merge order.

Details:
- Shows settings from all sources (User, Project, Local, Managed) with merge ordering
- Labeled "Ordered low-to-high priority — later entries override earlier ones"
- Makes it clear where each setting value comes from

Evidence: Settings debug (search for `"Effective merged settings plus raw per-source settings in merge order"`)


### ToolSearch Multi-Select and Search Hints
ToolSearch now supports loading multiple deferred tools at once with comma-separated `select:` syntax (e.g., `"select:Read,Edit,Grep"`). Tools can also display search hints alongside their names for better discoverability. A new `partial select` mode handles cases where some tools in a multi-select query are found while others are missing.

Evidence: ToolSearch improvements (search for `"select:Read,Edit,Grep"`, `"searchHint"`, `"partial select"`)


### Deferred Tools Announced via System Reminders
Deferred tools are now announced through system-reminder messages in the conversation rather than a static list, controlled by the `tengu_glacier_2xr` feature flag. This makes tool availability more dynamic and context-aware.

Evidence: Deferred tools announcement (search for `"Deferred tools are announced via system-reminder messages"`)


### Improved Command Shell Safety Checks
New obfuscation detection for potentially dangerous shell commands:
- Quoted newlines followed by `#`-prefixed lines that could hide arguments
- Consecutive quote characters at word start (potential obfuscation)
- Empty quote pairs adjacent to quoted dashes (flag obfuscation)
- Quoted brace characters inside brace contexts (brace expansion obfuscation)
- Excess closing braces after quote stripping

Evidence: Safety checks (search for `"Command contains a quoted newline followed by a #-prefixed line"`)


### `enableWeakerNetworkIsolation` Sandbox Setting
New sandbox option for macOS that allows access to `com.apple.trustd.agent` within the sandbox. This is needed for Go-based CLI tools (gh, gcloud, terraform, etc.) to verify TLS certificates when using `httpProxyPort` with a MITM proxy and custom CA.

Evidence: Network isolation setting (search for `"enableWeakerNetworkIsolation"`, `"Reduces security"`)


### Thinking Summaries in Transcript View
New `showThinkingSummaries` setting to display thinking summaries when viewing the transcript (ctrl+o). Default: false.

Evidence: Thinking summaries (search for `"Show thinking summaries in the transcript view"`)


### `pluginTrustMessage` for Enterprise
Enterprise administrators can now configure a custom message appended to the plugin trust warning shown before installation, via `pluginTrustMessage` in managed settings or MDM policy. Useful for adding organization-specific guidance.

Evidence: Plugin trust message (search for `"pluginTrustMessage"`, `"Custom message to append to the plugin trust warning"`)


### `includeCoworkInstructions` Setting
New setting to control whether built-in commit and PR workflow instructions are included in Claude's system prompt. Default: true.

Evidence: Cowork instructions setting (search for `"Include built-in commit and PR workflow instructions"`)


### `pathPattern` for Marketplace Restrictions
Marketplace sources of type `strictKnownMarketplaces` can now use `pathPattern` — a regex matched against `.path` of file and directory sources — to allow filesystem-based marketplaces alongside network source restrictions.

Evidence: Path pattern restrictions (search for `"pathPattern"`, `"Regex pattern matched against the .path field"`)


### Improved Subagent System Prompt
Subagent prompts have been refined:
- Clearer instruction formatting with separate lines for avoiding emojis and colons before tool calls
- Different response expectations based on agent role: detailed writeup for some, concise reports for others
- Agents now use absolute paths in their final responses
- Verification agent type added for post-task validation
- Teammates explicitly cannot spawn other teammates (flat team roster)

Evidence: Subagent improvements (search for `"Teammates cannot spawn other teammates"`, `"NOTE: You just closed out 3+ tasks"`)


### Improved Summary/Compaction System
The conversation summary system has been significantly revised:
- New `<<ANALYSIS_INSTRUCTION>>` placeholder system for injecting analysis instructions
- Support for partial compaction of only recent messages when earlier context is retained
- Lean compaction mode (`tengu_lean_cast`) with shorter analysis prompts focused on coverage over detail
- Better handling of large conversation files via optimized `compact_boundary` detection for files over 64MB

Evidence: Summary improvements (search for `"<<ANALYSIS_INSTRUCTION>>"`, `"tengu_lean_cast"`)


### Fast Mode Availability Messaging
Fast mode status messages now distinguish between general unavailability and network-specific issues:
- "Fast mode is currently unavailable" for general outages
- "Fast mode unavailable due to network connectivity issues" for network errors
- Default status changed from "disabled" to more descriptive states

Evidence: Fast mode messaging (search for `"Fast mode is currently unavailable"`, `"Fast mode unavailable due to network connectivity issues"`)


### Inquirer.js Prompt Library
A full Inquirer.js-style prompt library has been embedded for interactive CLI prompts, with proper error handling (`AbortPromptError`, `CancelPromptError`, `ExitPromptError`), pagination, arrow-key navigation, and multi-select support. This replaces ad-hoc prompt implementations.

Evidence: Inquirer integration (search for `"AbortPromptError"`, `"[Inquirer] Hook functions can only be called from within a prompt"`)


### Managed Plugin Trust Messaging
Plugins managed by organization policy now display "Managed by your organization — contact your admin" instead of generic status messages.

Evidence: Managed plugins (search for `"Managed by your organization"`)

## Bug Fixes

- Fixed sandbox cleanup: `cleanupAfterCommand` is now exposed on the sandbox API for proper resource cleanup after command execution (search for `"cleanupAfterCommand"`)

- Fixed lock file handling: Force-removal of stale lock files now logs the action and handles failures gracefully (search for `"Force-removed lock file at"`, `"Failed to force-remove lock file"`)

- Fixed symlink resolution in path operations: New `Fsq` function properly resolves symlinks by walking up the directory tree and handling broken symlinks gracefully (search for `"realpathSync"` in added functions)

- Removed `microcompact` feature: The `Context microcompacted` flow has been removed, simplifying the compaction pipeline (search for `"microcompact"` — present in old, absent in new context references)

- Removed `coral_reef_opus2` client data check and `crystal_beam` budget token feature — these were internal feature gates that have been cleaned up

## Notes

The Remote Control `server` subcommand is a significant architectural addition. Previous versions only supported basic remote-control connections — the new server mode enables persistent multi-session hosting with session lifecycle management, making it suitable for team environments and CI/CD integrations. Both `--spawn-same-dir-sessions` (default) and `--spawn-worktree-sessions` require the `server` subcommand; attempting to use them with the base `remote-control` command will produce an error.

The memory system overhaul changes the recommended format for memory files. While existing plain-text memories will likely continue to work, adopting the new frontmatter format (`name`, `description`, `type` fields) is recommended for better relevance matching in future conversations.
