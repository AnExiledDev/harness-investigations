# Changelog for version 2.1.83


## Summary

This release introduces the Advisor Tool — a server-side reviewer model you can configure with `/advisor` — along with `claude-cli://` deep link support for opening Claude Code from external URLs, two new hook types (`CwdChanged` and `FileChanged`) for filesystem-aware automation, and the rebranded Ultrareview cloud code review. Enterprise users gain XAA IdP authentication for MCP servers and a `managed-settings.d` drop-in directory. Internally, Segment.io analytics has been completely removed.

### Advisor Tool

What: A server-side tool backed by a stronger reviewer model that automatically sees your entire conversation history. When invoked, the advisor reviews your work and provides feedback before you commit to an approach.

Usage:
```bash
# Enable the advisor with a model
/advisor opus

# Check current advisor status
/advisor

# Disable the advisor
/advisor unset

# Via CLI flag
claude --advisor opus
```

Details:
- The advisor tool takes no parameters — it automatically receives the full conversation context
- Designed to be called before substantive work (writing code, committing to an interpretation), when stuck, or when you believe a task is complete
- Can be disabled via the `CLAUDE_CODE_DISABLE_ADVISOR_TOOL` environment variable
- Only available when the server enables this capability; the `/advisor` command appears when user configuration is permitted
- Supports Opus 4.6 and Sonnet 4.6 class models as advisor models

Evidence: Advisor tool feature (search for `"advisor-tool-2026-03-01"`, `"tengu_sage_compass"`, `"/advisor"`)


### Deep Link Protocol Handler

What: Claude Code now registers as a `claude-cli://` URI scheme handler, allowing external applications and web pages to open Claude Code with a specific working directory and pre-filled prompt.

Details:
- Auto-registers the protocol handler on macOS (via an `.app` bundle), Linux (via `.desktop` file and `xdg-mime`), and Windows (via registry entries)
- Deep links can specify `cwd` (working directory), `repo` (GitHub-style `owner/repo`), and `query` (pre-filled prompt) parameters
- Input is validated: paths must be absolute, control characters are rejected, and length limits are enforced
- Users see a notification that the session was opened by a deep link and are prompted to review any pre-filled prompt before submitting
- Can be disabled via the `disableDeepLinkRegistration` setting
- Controlled by the `tengu_lodestone_enabled` feature flag

Evidence: Deep link handler (search for `"claude-cli://"`, `"Claude Code URL Handler"`, `"tengu_lodestone_enabled"`)


### CwdChanged and FileChanged Hooks

What: Two new hook event types that trigger automation when the working directory changes or when specific files are modified.

Usage in `.claude/hooks.json`:
```json
{
  "hooks": {
    "CwdChanged": [{
      "command": "my-script.sh",
      "timeout": 10000
    }],
    "FileChanged": [{
      "command": "on-file-change.sh",
      "matcher": "src/**/*.ts",
      "timeout": 10000
    }]
  }
}
```

Details:
- **CwdChanged**: Fires after the working directory changes. Input JSON includes `old_cwd` and `new_cwd`. Hook output can include `watchPaths` to dynamically register additional file watchers via `hookSpecificOutput`
- **FileChanged**: Fires when a watched file changes, is added, or is removed. Input JSON includes `file_path` and `event` (one of `change`, `add`, `unlink`). The `matcher` field specifies file glob patterns to watch
- Both hook types set `CLAUDE_ENV_FILE` — write bash exports there to inject environment variables into subsequent BashTool commands
- File watching uses chokidar under the hood for cross-platform filesystem monitoring

Evidence: New hook types (search for `"CwdChanged"`, `"FileChanged"`, `"cwdchanged-hook-"`, `"filechanged-hook-"`)


### Ultrareview (Cloud Code Review)

What: A rebranded and enhanced cloud-based code review feature. A cloud agent analyzes your branch for ~5–15 minutes, finding and verifying bugs, then delivers findings as a task notification.

Details:
- Launched in the background — users can continue working while the review runs
- Review output arrives as a task notification when complete; press shift+↓ to view results
- Requires a git repository with a GitHub remote and OAuth login
- Replaces the previous "Remote review" terminology

Evidence: Cloud review feature (search for `"ultrareview"`, `"~5–15 min"`, `"Cloud agent finds and verifies bugs"`)


### XAA IdP Authentication for MCP Servers

What: Enterprise-grade OIDC authentication for MCP servers using the SEP-990 standard. Configure once and all XAA-enabled MCP servers authenticate silently using cached identity tokens.

Usage:
```bash
# One-time setup: configure IdP connection
claude mcp xaa setup

# Login (opens browser for OIDC flow)
claude mcp xaa login

# Check current connection
claude mcp xaa status

# Clear configuration
claude mcp xaa clear
```

Details:
- Performs full OIDC discovery from the IdP issuer URL
- Browser-based authorization with a local callback server on loopback
- Caches `id_token` with automatic expiration; use `--force` to re-login
- Supports `--client-id`, `--issuer`, `--callback-port`, and `--id-token` flags
- Client secret can be read from the `MCP_XAA_IDP_CLIENT_SECRET` environment variable
- Settings stored include `issuer`, `clientId`, `callbackPort`, and optionally `clientSecret` (in secure storage)

Evidence: XAA authentication system (search for `"XAA IdP"`, `"claude mcp xaa"`, `"SEP-990"`)


### Enterprise Managed Settings Drop-in Directory

What: Enterprise administrators can now distribute policy settings via a `managed-settings.d/` directory alongside the existing `managed-settings.json` file.

Details:
- JSON files placed in the `managed-settings.d/` directory are merged into the enterprise policy configuration
- Files are sorted alphabetically and merged in order, allowing layered configuration
- Only `.json` files are loaded; hidden files (starting with `.`) are ignored
- The health check display now distinguishes between "Enterprise managed settings (file + drop-ins)" when both sources exist

Evidence: Drop-in settings directory (search for `"managed-settings.d"`, `"Enterprise managed settings (drop-ins)"`)


### Companion

What: A small animated ASCII character that sits beside the user's input box and occasionally comments in a speech bubble. Each user gets a unique procedurally-generated companion based on their account.

Details:
- Companions are generated from a seeded random number generator keyed to the user's account UUID
- Each companion has a species (from a pool of 18 creatures), rarity tier (common through legendary), eye style, optional hat, stats, and a chance to be shiny
- Activated by server-side configuration (requires the `companion` config to be set)
- Can be muted via `companionMuted` state

Evidence: Companion system (search for `"companion_intro"`, `"friend-2026-401"`, `"companionMuted"`)


### `/version` Command

What: A new slash command that prints the version of the currently running session, as distinct from what the auto-updater may have downloaded.

Usage:
```
/version
```

Evidence: Version command (search for `"Print the version this session is running (not what autoupdate downloaded)"`)

### Ultraplan Enhanced with Web-Based Refinement

Ultraplan now supports an interactive refinement workflow where plans can be generated and refined in Claude Code on the web (claude.ai/code), then brought back to the local CLI for execution. Users see a "No, refine with Ultraplan on Claude Code on the web" option during plan approval, and approved plans are automatically applied locally.

Evidence: Enhanced ultraplan flow (search for `"Ultraplan approved in browser"`, `"Refine local plan"`, `"No, refine with Ultraplan on Claude Code on the web"`)


### MCP Registry for Official Server Validation

Claude Code now fetches the official Anthropic MCP server registry at startup to validate MCP server URLs. This allows trusted servers to receive enhanced metadata forwarding (server name and tool name in API requests), improving the quality of tool-use responses.

Evidence: MCP registry validation (search for `"mcp-registry"`, `"https://api.anthropic.com/mcp-registry/v0/servers"`)


### Plugin Marketplace GCS Distribution

Official marketplace plugins are now distributed via Google Cloud Storage (`downloads.claude.ai`) with ZIP-based atomic updates and SHA-based cache validation, providing faster and more reliable plugin installation compared to the previous git-only approach. Falls back to git if GCS is unavailable.

Evidence: GCS plugin distribution (search for `"downloads.claude.ai"`, `"Official marketplace GCS"`)


### `useAutoModeDuringPlan` Setting

A new boolean setting controls whether plan mode uses auto mode semantics (automatically accepting edits) when auto mode is available. Defaults to `true`. Can be configured at the user, local, flag, or policy level.

Evidence: Plan mode setting (search for `"useAutoModeDuringPlan"`, `"Whether plan mode uses auto mode semantics"`)


### Default Teammate Model Setting

A new `teammateDefaultModel` setting allows users to configure the default model used when spawning teammate agents. Accessible through the `/config` settings UI under "Default teammate model".

Evidence: Teammate model config (search for `"TeammateModel"`, `"Default teammate model"`, `"teammateDefaultModel"`)


### `ctrl+x ctrl+k` Keybinding for Killing Background Agents

A new chord keybinding `ctrl+x ctrl+k` kills all running background agents. This supplements the existing `ctrl+f` toggle (press twice to stop agents).

Evidence: Kill agents keybinding (search for `"ctrl+x ctrl+k"`, `"chat:killAgents"`)


### `sandbox.failIfUnavailable` Setting

A new boolean setting that causes Claude Code to exit with an error at startup if `sandbox.enabled` is true but the sandbox cannot start (missing dependencies, unsupported platform, or platform not in `enabledPlatforms`). When false (the default), a warning is logged but execution continues.

Evidence: Strict sandbox setting (search for `"failIfUnavailable"`, `"sandbox required but unavailable"`)


### `shift+tab` Plan Approval Feedback

In plan mode, `shift+tab` now allows approving a plan while simultaneously providing feedback text. The input placeholder shows "shift+tab to approve with this feedback", streamlining the plan refinement workflow.

Evidence: Plan feedback approval (search for `"shift+tab to approve with this feedback"`)


### Worktree Name Validation Supports Path Segments

Worktree names now support `/`-separated path segments (e.g., `feature/my-branch`). Each segment is independently validated for allowed characters (letters, digits, dots, underscores, dashes). The 64-character maximum length still applies to the full name.

Evidence: Path segment validation (search for `"each \"/\"-separated segment must be non-empty"`)


### Improved Windows Terminal Detection

Claude Code now detects and supports a broader range of terminal emulators on all platforms for launching new terminal sessions (used by deep links and remote sessions). On Windows, it prioritizes Windows Terminal, then PowerShell 7+, PowerShell 5, and Command Prompt. On macOS and Linux, it detects Ghostty, iTerm2, Alacritty, Kitty, WezTerm, and various others with proper `--working-directory` flag support.

Evidence: Terminal detection (search for `"Windows Terminal"`, `"com.mitchellh.ghostty"`, `"com.googlecode.iterm2"`)


### MCP Tool Search Hints via `anthropic/searchHint`

MCP servers can now provide search hints through the `anthropic/searchHint` metadata field on tool definitions. These hints help Claude find and select the right tools more effectively by providing natural-language descriptions of when to use each tool.

Evidence: MCP search hints (search for `"anthropic/searchHint"`)


### `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` Environment Variable

A new environment variable for SDK hosts (desktop apps, IDE extensions) to signal that the API provider is managed by the host application, preventing users from accidentally overriding the provider configuration.

Evidence: Host-managed provider (search for `"CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST"`)


### Memory System Prompt Refinements

The memory guidance system prompt has been significantly rewritten for clarity:
- MEMORY.md entries are now recommended to be under ~200 characters (up from ~150) with detail moved to topic files
- Byte-size truncation added alongside line-count truncation for oversized MEMORY.md files
- New instruction: "If the user says to *ignore* or *not use* memory: proceed as if MEMORY.md were empty"
- HTML comment stripping added when processing MEMORY.md content

Evidence: Memory prompt updates (search for `"Keep index entries to one line under ~200 chars"`)


### Plugin Sensitive Options with Secure Storage

Plugin configuration now distinguishes between non-sensitive values (saved to `settings.json`) and sensitive values (saved to macOS keychain or `.credentials.json`). Sensitive fields are scrubbed from `settings.json` after migration to secure storage.

Evidence: Plugin secrets handling (search for `"sensitive)"`, `"to secure storage"`, `"saveMcpServerUserConfig: scrubbed"`)

## Bug Fixes

- Fixed atomic file write cleanup: the temp file is now cleaned up even if it doesn't exist at the expected path (search for `"Cleaning up temp file"`)
- Improved plugin hooks reload: now tracks plugin-affecting settings changes rather than just `enabledPlugins` to avoid unnecessary reloads (search for `"plugin-affecting settings change"`)
- Fixed deep link input validation to reject control characters and enforce length limits, preventing potential injection issues (search for `"Deep link cwd contains disallowed control characters"`)
- Fixed MCP lazy dedup to properly suppress duplicate servers from plugins that overlap with claude.ai connectors (search for `"[MCP] Lazy dedup: suppressing"`)

## Internal Changes

- **Segment.io analytics completely removed**: The `@segment/analytics-node` library and all associated code (event factory, priority queue, emitter, stats tracking, UUID generation) have been removed. Telemetry is now handled through a lighter-weight internal system (search for `"Segment.io"` in old version)
- **Bootstrap API replaces clientData**: The `/api/oauth/claude_cli/client_data` endpoint has been replaced by `/api/claude_cli/bootstrap`, which also returns additional model options alongside client data (search for `"/api/claude_cli/bootstrap"`)
- **Improved debug repainting**: New `CLAUDE_CODE_DEBUG_REPAINTS` environment variable enables detailed React component owner chain tracking for diagnosing UI repaint issues (search for `"CLAUDE_CODE_DEBUG_REPAINTS"`)

## Notes

- The Advisor Tool, Deep Link Protocol, and Companion features are controlled by server-side configuration and feature flags. They may not be immediately available to all users.
- The `managed-settings.d` directory enables enterprise administrators to manage settings across multiple JSON files. Existing `managed-settings.json` files continue to work unchanged.
- Ultrareview replaces the "Remote review" terminology from previous versions. The functionality is enhanced with cloud agent-based bug detection.
