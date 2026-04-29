# Changelog for version 2.1.98

## Summary

This release introduces the **Monitor tool** for streaming background events, a comprehensive **Vertex AI setup wizard** with credential validation and model pinning, and **Perforce workspace support**. It also adds subprocess environment scrubbing for enhanced security, sleep command blocking in agent mode, model-aware image processing limits, and a new `--exclude-dynamic-system-prompt-sections` CLI flag for improved prompt cache reuse. The Vertex AI model management system gains automatic upgrade detection and fallback capabilities.


## New Features


### Monitor Tool

What: A new built-in tool that streams events from background scripts as live notifications in the conversation.

Usage:
```bash
# Inside a Claude Code session, Claude can use the Monitor tool to:
# - Tail logs for errors
# - Watch for file changes
# - Poll GitHub for new PR comments
# - Stream events from WebSocket listeners
```

Details:
- Each stdout line from the script becomes a notification in the conversation
- Events arriving within 200ms are batched into a single notification
- Supports `persistent: true` mode for session-length watches (PR monitoring, log tails)
- Supports `timeout_ms` for time-limited monitoring
- Monitors that produce too many events are automatically stopped with guidance to restart using tighter filters
- Use `TaskStop` to cancel a running monitor
- Distinct from `Bash` with `run_in_background` — Monitor is for the streaming case ("tell me every time X happens"), while background Bash is for one-shot "wait until done"

Evidence: MonitorTool definition (search for `"stream events from a background script as live notifications"`)


### Vertex AI Setup Wizard

What: An interactive, multi-step wizard for configuring Google Vertex AI as your model backend, with credential validation and model pinning.

Details:
- Step-by-step flow: authentication method → service account key (if applicable) → GCP project → region → credential verification → model pinning → confirmation
- Three authentication methods: Application Default Credentials (gcloud auth), service account key file, or existing environment credentials
- Reads existing gcloud configurations to auto-discover project IDs
- Validates credentials by making a test API call to Vertex AI
- Probes each model tier (Sonnet, Opus, Haiku) with a one-token request to check availability
- Provides specific error messages for common issues: expired credentials, missing permissions, wrong region, missing API enablement
- Model pinning option: pin specific model versions that are confirmed working, or use Claude Code defaults (auto-updates)
- Saves configuration to `~/.claude/settings.json` under the `env` key
- For ADC users, reminds that `gcloud auth application-default login` refreshes credentials automatically

Evidence: Vertex setup wizard (search for `"How do you authenticate to Google Cloud?"` and `"Pin model versions"`)


### Vertex AI Model Upgrade and Fallback System

What: Automatic detection of stale Vertex model pins and probing for accessible fallback models when defaults are unavailable.

Details:
- On startup (for first-party Vertex users), Claude Code checks whether pinned model versions are outdated compared to built-in defaults
- For each stale tier, it probes Vertex AI to verify the upgrade candidate is accessible (one-token request, 20s timeout)
- If upgrades are found, presents a dialog to update model pins
- Separately, detects unpinned tiers where the default model may not be accessible and finds compatible fallbacks
- Displays warnings when fallback models are used instead of defaults
- Logs telemetry: `tengu_vertex_upgrade_check` and `tengu_vertex_fallback_check`
- Auto-restarts Claude Code when model configuration changes

Evidence: Vertex upgrade/fallback system (search for `"[vertex-upgrade] tiersWithPin="` and `"[vertex-fallback] unpinnedTiers="`)


### Perforce Workspace Support

What: First-class support for Perforce version control workspaces, including read-only file detection and checkout guidance.

Usage:
```bash
export CLAUDE_CODE_PERFORCE_MODE=1
```

Details:
- When enabled, Claude Code detects files that haven't been opened for edit in Perforce
- Write tool returns a specific error message guiding users to run `p4 edit <file>` before modifying
- Prevents `chmod` workarounds that would bypass Perforce tracking
- System prompt includes Perforce-specific guidance for the model

Evidence: Perforce mode (search for `"CLAUDE_CODE_PERFORCE_MODE"` and `"File is read-only — it has not been opened for edit in Perforce"`)


### `--exclude-dynamic-system-prompt-sections` CLI Flag

What: Moves per-machine sections (cwd, environment info, memory paths, git status) from the system prompt into the first user message to improve prompt cache reuse across users.

Usage:
```bash
claude --exclude-dynamic-system-prompt-sections
```

Details:
- Only applies when using the default system prompt (ignored with `--system-prompt`)
- Particularly useful for teams or CI environments where multiple users/machines share cached prompts
- Defaults to `false` (disabled)

Evidence: CLI flag (search for `"--exclude-dynamic-system-prompt-sections"`)


### `CLAUDE_CODE_MAX_CONTEXT_TOKENS` Environment Variable

What: Allows manual control of the maximum context token limit when automatic compaction is disabled.

Usage:
```bash
export DISABLE_COMPACT=1
export CLAUDE_CODE_MAX_CONTEXT_TOKENS=500000
```

Details:
- Only takes effect when `DISABLE_COMPACT` is set to a truthy value
- Parses the value as an integer; ignores invalid or non-positive values
- When compaction is disabled without this variable, the context limit message now shows "Compaction is disabled." instead of the previous autocompact instructions

Evidence: Context limit override (search for `"CLAUDE_CODE_MAX_CONTEXT_TOKENS"` and `"Compaction is disabled."`)


### `CLAUDE_CODE_SCRIPT_CAPS` Environment Variable

What: Enforces per-script call limits in subprocess-scrubbed environments to prevent data exfiltration via repeated write operations.

Usage:
```bash
export CLAUDE_CODE_SCRIPT_CAPS='{"curl": 10, "wget": 5}'
```

Details:
- JSON object mapping script/command name substrings to maximum call counts
- Tracks cumulative usage across the session
- Throws an error when a cap is exceeded: "Script call limit exceeded: X has been called N times (cap: M)"
- Only active when `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` is enabled
- Designed for untrusted-input workflows where exfiltration prevention is critical

Evidence: Script caps (search for `"CLAUDE_CODE_SCRIPT_CAPS"` and `"Script call limit exceeded"`)


### MCP Resource Templates Support

What: Adds support for MCP resource templates, enabling template-based resource discovery with completion and icon support.

Details:
- Fetches `resourceTemplates` alongside existing resources during MCP server initialization
- New `mcp-template` tool type detection for template-based resource access
- Template resources get their own icon in the UI (distinct from regular `mcp-resource` icon)
- Supports completions for template arguments via the MCP protocol's `complete` method
- Template resource IDs use `mcp-template::` and `mcp-template-value::` prefixes

Evidence: MCP templates (search for `"mcp-template"` and `"Failed to fetch resource templates"`)


## Improvements


### Subprocess Environment Scrubbing Enhancements

The `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` feature (introduced previously) receives significant hardening in this release:
- Requires `bubblewrap` (bwrap) on Linux for filesystem sandboxing; provides clear installation instructions if missing
- Creates stub files for common dotfiles (.gitconfig, .bashrc, .npmrc, etc.) to prevent errors in sandboxed environments
- Defines comprehensive filesystem access rules: deny-read for container sockets, deny-write for shell configs, git hooks, CI environment files, and package manager configs
- Adds `.git/info/exclude` entries for scrub-mode stubs to keep git status clean
- Forces permission mode to default when env scrubbing is active
- New `allowUnsandboxedCommands` sandbox setting for fine-grained control

Evidence: Env scrub hardening (search for `"bubblewrap is required for subprocess env scrubbing"` and `"claude-code scrub-mode stubs"`)


### Sleep Command Blocking in Agent Mode

Long-running foreground `sleep` commands (≥2 seconds) are now blocked when running in agent mode (`tengu_amber_sentinel` flag). This prevents agents from wasting time on unnecessary delays.
- Detects `sleep N` as the first command when N ≥ 2
- Distinguishes between standalone sleeps and sleep-then-continue patterns
- Agents must use `run_in_background: true` for commands that need delays

Evidence: Sleep blocking (search for `"standalone sleep"` and `` "`sleep N` as the first command with N ≥ 2 is blocked" ``)


### Dynamic Keyboard Hint Components

All hardcoded keyboard instruction text throughout the UI has been replaced with a reusable `A8` keyboard chord component. This affects dozens of locations:
- "Esc to cancel" → rendered via `A8` chord component
- "Enter to confirm" → rendered via `A8` chord component
- Navigation hints ("↑↓ to scroll", "← → to adjust") → rendered via `A8` chord components
- Selection hints ("Enter to select", "Tab to switch") → rendered via `A8` chord components

This infrastructure enables future support for custom keybindings — the hint text will dynamically reflect any user-configured key remappings.

Evidence: Keyboard hint refactoring (search for `chord:` and `action:` in component definitions)


### Worktree Filtering in Session Browser

The session/project browser UI now supports filtering by worktree:
- "only show current worktree" / "show all worktrees" toggle options
- Tracks active worktrees and filters the session list accordingly

Evidence: Worktree filtering (search for `"only show current worktree"` and `"show all worktrees"`)


### Model-Aware Image Processing Limits

Image processing now respects per-model limits for dimensions and file size, rather than using global constants:
- `maxWidth`, `maxHeight`, `maxBase64Size`, and `targetRawSize` can now vary by model
- Default limits remain at 2000×2000 pixels, 5MB base64, and ~3.75MB target raw size
- The `imageLimits` parameter is threaded through clipboard paste, content processing, and tool result handling
- Image validation now also checks images inside `tool_result` content blocks (not just top-level user messages)

Evidence: Image limits (search for `"imageLimits"` and `"targetRawSize"`)


### egrep and fgrep Support in Bash Tool

The Bash tool's safe-command validation now recognizes `egrep` and `fgrep` as valid commands, applying the same safe flags as `grep`.

Evidence: egrep/fgrep support (search for `"egrep"` and `"fgrep"` in command safety checks)


### Write Tool Directory Validation

The Write tool now validates file modes before writing, preventing attempts to write to directories. Returns an appropriate error when the target path is a directory.

Evidence: Directory mode check (search for `"& 128"` bit flag validation)


### GitHub PR mergeStateStatus

PR queries now include the `mergeStateStatus` field, exposing whether a PR is in a clean, has_hooks, or unstable merge state.

Evidence: PR query enhancement (search for `"mergeStateStatus"`)


### Hook Error Display Improvements

Non-blocking hook errors now extract and render stderr/stdout output more clearly, making it easier to diagnose hook failures.

Evidence: Hook error display (search for `"hook_non_blocking_error"`)


### Context Limit Messaging

The context limit reached message has been simplified. When `DISABLE_COMPACT` is set, the message now says "Compaction is disabled." rather than suggesting `/compact`.

Evidence: Context limit message (search for `"Context limit reached"` and `"Compaction is disabled."`)


### Bedrock Configuration No Longer Requires Restart

The Bedrock setup wizard message previously said "Bedrock configuration saved to ~/.claude/settings.json. Restart Claude Code to apply." It now simply says "Bedrock configuration saved to ~/.claude/settings.json." — the restart is handled automatically.

Evidence: String diff shows removal of `"Restart Claude Code to apply"` from Bedrock setup


## Bug Fixes

- Fixed potential null reference when trimming text input in internal processing — added optional chaining (`text?.trim()`) to prevent crashes on undefined text values (search for `"text?.trim()"`)
- Fixed semantic version prerelease regex pattern by correcting the component order of numeric and non-numeric identifiers (search for `"PRERELEASEIDENTIFIER"`)
- Improved Bedrock model tier fallback logic by validating environment variable values before applying them as fallback models (search for `"[bedrock-fallback]"`)


## In Development


### Opus 4.6 Communication Style Tuning [Gradual Rollout]

What: Differentiated system prompt instructions for Opus 4.6 models that emphasize concise, anti-verbose communication and refined code quality guidance.

Status: Feature-flagged via `quiet_salted_ember` (server-controlled, only applies to Opus 4.6 models)

Details:
- When enabled, adds a "Communicating with the user" prompt section instructing the model to give brief updates at key moments rather than verbose explanations
- Includes refined code quality instructions: "Default to writing no comments. Only add one when the WHY is non-obvious"
- Adds anti-verbosity guidance as a separate prompt category
- Includes refined instructions about not adding features/refactoring beyond what was asked
- The `cM6()` gate function checks both the model family (must include "opus-4-6") and the `quiet_salted_ember` flag value

Evidence: Opus 4.6 prompt tuning (gated by `quiet_salted_ember`, search for `"Default to writing no comments"` and `"Communicating with the user"`)


### Sage Compass v2 [Gradual Rollout]

What: Updated version of the Sage Compass feature, migrated from `tengu_sage_compass` to `tengu_sage_compass2`.

Status: Feature-flagged via `tengu_sage_compass2`

Details:
- The feature flag has been renamed/versioned, suggesting an iteration on the existing Sage Compass feature
- Enabled state is checked via `h8("tengu_sage_compass2", {}).enabled ?? !1` (default disabled)

Evidence: Sage Compass v2 (search for `"tengu_sage_compass2"`)


### Agent Mode Command Validation [Gradual Rollout]

What: Validation layer that blocks certain long-running synchronous bash commands when running in agent mode.

Status: Feature-flagged via `tengu_amber_sentinel`

Details:
- When enabled, checks commands before execution in foreground mode
- Blocks standalone `sleep` commands with duration ≥ 2 seconds
- Designed to prevent agents from wasting time on unnecessary blocking operations
- Commands can bypass the check by using `run_in_background: true`

Evidence: Agent command validation (gated by `tengu_amber_sentinel`, search for `"standalone sleep"`)
