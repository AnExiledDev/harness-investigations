# Changelog for version 2.1.92


## Summary

This release introduces a major interactive AWS Bedrock setup wizard (`/setup-bedrock`), a new `/teleport` command for resuming sessions from claude.ai, and a `/stop` command for quick session-only stopping conditions. The `/advisor` command has been redesigned with a rich UI dialog, the release notes viewer is now interactive with a version picker, and several internal optimizations include tool result deduplication and a new seccomp multicall binary approach for Linux sandboxing. The `/tag` and `/vim` commands have been removed.

### Interactive AWS Bedrock Setup Wizard

What: A comprehensive multi-step wizard that walks you through configuring AWS Bedrock authentication, region selection, credential verification, and model pinning — all from within the CLI.

Usage:
```bash
/setup-bedrock
```

Details:
- Supports four authentication methods: AWS SSO profile, Bedrock API key (bearer token), access key + secret, or existing environment credentials
- Auto-discovers AWS profiles from `~/.aws/config` and `~/.aws/credentials`
- Verifies credentials by calling STS `GetCallerIdentity` and listing Bedrock inference profiles
- Model pinning step tests each candidate (Sonnet, Opus, Haiku) with a one-token request to verify availability
- Saves configuration to `~/.claude/settings.json` under `env:`
- Handles SSO session expiry, invalid credentials, and missing permissions with specific guidance
- Only visible when `CLAUDE_CODE_USE_BEDROCK=1` is already set

Evidence: Bedrock wizard UI components (search for `"Set up AWS Bedrock"`, `"Bedrock configuration saved to ~/.claude/settings.json"`, `"How do you authenticate to AWS?"`)


### /teleport Command

What: Resume a Claude Code session that was started on claude.ai/code directly in your local CLI.

Usage:
```bash
/teleport
# or use the alias:
/tp
```

Details:
- Loads a remote session's conversation history into your local Claude Code instance
- Requires remote sessions to be enabled (`allow_remote_sessions` policy)
- Only available when authenticated
- Shows "Session resumed successfully" on completion or "Teleport cancelled" on abort

Evidence: Teleport command registration (search for `"Resume a Claude Code session from claude.ai"`, `"Teleport cancelled"`)


### /stop Command — Quick Session Stop Hook

What: Set a session-only prompt-based Stop hook with a quick one-liner, allowing you to define a stopping condition that Claude evaluates after each turn.

Usage:
```bash
/stop Has Claude completed all requested tasks?
```

Details:
- Creates a prompt-type hook on the "Stop" event for the current session only
- If a Stop hook already exists, shows the current condition and lets you edit, update, or delete it
- Submitting an empty prompt clears the hook
- Tab switches focus between the input and a "Delete this hook" option when editing an existing hook
- The hook condition is evaluated by Claude after each turn — if met, Claude stops

Evidence: Stop hook command and UI (search for `"Set a session-only Stop hook with a quick prompt"`, `"Stop hook set"`, `"Stop hook cleared"`, `"tengu_stop_hook_command"`)


### Redesigned /advisor Command

What: The `/advisor` command is now a full interactive dialog with rich descriptions, replacing the previous text-based interface.

Usage:
```bash
/advisor           # Opens the advisor selection dialog
/advisor opus      # Set advisor directly
/advisor off       # Disable advisor
```

Details:
- New dialog title "Advisor Tool" with explanatory text about how the advisor works
- Explains: "When Claude needs stronger judgment — a complex decision, an ambiguous failure, a problem it's circling without progress — it escalates to the advisor model for guidance, then resumes"
- Highlights the Sonnet + Opus pairing: "near-Opus performance with reduced token usage"
- Shows a warning if the current main model doesn't support the advisor
- Valid advisor options are "opus" and "sonnet"
- Description changed from "Configure the advisor model" to "Configure the Advisor Tool to consult a stronger model for guidance at key moments during a task"
- Advisor enablement is no longer gated by `canUserConfigure` from `tengu_sage_compass`; now uses a simpler `nb()` check

Evidence: Advisor dialog redesign (search for `"Configure the Advisor Tool to consult a stronger model for guidance at key moments during a task"`, `"Advisor Tool"`, `"When Claude needs stronger judgment"`)


### Interactive Release Notes Viewer

What: The `/release-notes` command now shows an interactive version picker instead of dumping all notes at once.

Usage:
```bash
/release-notes
```

Details:
- Presents a scrollable list of versions (up to 10 visible at once)
- "Show all" option to display all versions' notes combined
- Select a specific version to view only its notes
- Versions are sorted by semver (newest first)

Evidence: Release notes interactive picker (search for `"Select a version to view its notes."`)


### Context Window Size Notification

What: A new notification appears when your context window grows large, showing approximate uncached token count and suggesting `/clear`.

Details:
- Triggers when uncached tokens exceed ~50,000
- Only shows if more than a certain time has passed since session start
- Format: `~Nk uncached · /clear to start fresh`
- Helps users understand when conversation context is getting expensive

Evidence: Context notification function (search for `"k uncached"`, `"/clear to start fresh"`)

### Write Tool Prompt Update
The Write tool now advises: "For appending to an existing file, prefer shell redirection via Bash (e.g. `echo "..." >> file`) over rewriting the whole file." The old `mode:'append'` parameter has been removed from the Write tool schema.

Evidence: Write tool description change (search for `"For appending to an existing file, prefer shell redirection"`)


### Keybinding Display System Overhaul
A new `formatChord` system renders keyboard shortcuts with platform-aware formatting. Supports three display styles: `default` (e.g., `ctrl+A`), `compact` (e.g., `^a`), and `symbol` (e.g., `⌃A`). Mac-specific glyphs (⌘, ⌥) are used when the platform is macOS. Chord sequences and arrow key groups are formatted intelligently.

Evidence: Keyboard shortcut formatting (search for `"Enter"`, `"Esc"`, `"⏎"`, `"⌃"` in the new key map definition at ~line 316314)


### OAuth `offline_access` Scope
The OAuth flow now automatically appends `offline_access` to the authorization scope when the server supports it, enabling longer-lived refresh tokens.

Evidence: OAuth scope handling (search for `"Appended offline_access to authorization scope"`)


### Managed Settings Enforcement
Organizations can now require that remote managed settings are freshly fetched before the CLI starts. If the fetch fails, the CLI exits with a clear message instead of proceeding with stale settings.

Evidence: Managed settings enforcement (search for `"Your organization requires remote managed settings to load"`, `"When set in managed settings, the CLI blocks startup"`)


### Cron Minimum Tick Interval Validation
Scheduled tasks in proactive mode now validate that the cron expression doesn't fire more frequently than the configured `minTickIntervalMinutes`, preventing overly aggressive scheduling.

Evidence: Cron validation (search for `"Cron period too short"`)


### Auto-Compact Experiment Notification
When the auto-compact threshold is set by a server experiment (not user config), a notification now shows the threshold and how to override it: `compacted at N · override with CLAUDE_CODE_AUTO_COMPACT_WINDOW=1000000`.

Evidence: Auto-compact notification (search for `"override with CLAUDE_CODE_AUTO_COMPACT_WINDOW"`)


### Memory System Path Unification
The memory index now handles both private and team memories under a single path structure. Private memories use `file.md` paths and team memories use `team/file.md`. The old separate "shared team memory" context tag has been removed.

Evidence: Memory path description (search for `"indexes both private and team memories"`)


### macOS Sandbox: Mach Service Lookup Allow-List
A new sandbox setting lets users specify additional XPC/Mach service names to allow, supporting tools like 1Password CLI, Playwright, or other system services. Supports trailing-wildcard matching (e.g., `"2BUA8C4S2C.com.1password.*"`).

Evidence: Mach service setting (search for `"macOS only: Additional XPC/Mach service names"`)


### `CLAUDE_CODE_MAX_RETRIES` Validation
The `CLAUDE_CODE_MAX_RETRIES` environment variable is now validated to ensure it parses to a finite integer ≥ 0, preventing invalid values from causing unexpected behavior.

Evidence: Retry validation (search for `"Number.isFinite"` near the `CLAUDE_CODE_MAX_RETRIES` handler)


### Improved Worktree Change Detection
Worktree cleanup now writes a `CLAUDE_BASE` marker to track the baseline commit, enabling accurate detection of commits ahead and uncommitted changes when deciding whether to auto-clean a worktree.

Evidence: Worktree baseline tracking (search for `"CLAUDE_BASE"`, `"commitsAhead="`)


### Remote Control Session Name Prefix
The `--remote-control-session-name-prefix` flag now defaults to the hostname and is documented as configurable.

Evidence: Remote control prefix (search for `"Prefix for auto-generated Remote Control session names"`)

## Bug Fixes

- Fixed compact streaming error messages to include `hasStartedStreaming` state for better debugging (search for `"Compact streaming failed. hasStartedStreaming="`)
- Hook condition evaluation prompt now includes structured response format guidance, requiring JSON with `ok` and `reason` fields (search for `"You are evaluating a hook condition in Claude Code"`)
- Worktree removal hooks now report specific failure messages distinguishing between agent worktrees and regular worktrees (search for `"WorktreeRemove hook did not remove"`)
- Team memory sync now gracefully handles inaccessible team directories instead of failing (search for `"team-memory-sync: team dir inaccessible"`)
- Voice recording cancellation now explicitly discards without submitting (search for `"cancelRecording: discarding without submit"`)

### Tool Result Deduplication [In Development]

What: When identical tool results appear multiple times in a conversation, subsequent occurrences are replaced with a short reference to the original, saving context window space.

Status: Feature-flagged behind `tengu_onyx_basin_m1k` (default: false)

Details:
- Hashes tool result content and tracks seen results with short IDs (`r1`, `r2`, etc.)
- Duplicate results are replaced with: `<identical to result [rN] from your {tool} call earlier — refer to that output>`
- Only applies to results longer than 256 characters and shorter than a configurable max
- Tracks telemetry via `tengu_tool_result_dedup`

Evidence: Tool result deduplication (gated by `tengu_onyx_basin_m1k`, search for `"result-id:"`, `"identical to result"`)


### Rerun Command Aliases [In Development]

What: Tool results will include `[rerun: bN]` footers, and future Bash calls can use `{rerun: 'bN'}` to exactly replay a prior command without retyping it.

Status: Feature-flagged behind `tengu_velvet_anchor` (default: false)

Details:
- Each Bash command gets assigned a short alias (`b1`, `b2`, etc.)
- The `rerun` field and `command` field are mutually exclusive
- Error message for invalid alias: `Unknown rerun alias 'bN'. Valid aliases this session: ...`

Evidence: Rerun alias system (gated by `tengu_velvet_anchor`, search for `"Unknown rerun alias"`, `"rerun"`)


### Voice Handsfree Mode [In Development]

What: A hands-free voice interaction mode with hold-to-talk and tap-to-toggle modes.

Status: Feature-gated behind `VOICE_HANDSFREE`; internal-only annotation states "Hidden from public SDK types until external launch."

Details:
- Three modes: `hold` (hold to talk, default), `tap` (tap to start/stop+submit), and `off`
- Setting for "Submit the prompt when hold-to-talk is released (hold mode only)"
- Described as "Voice handsfree settings; behavior gated at read sites by feature(VOICE_HANDSFREE)"

Evidence: Voice handsfree settings (search for `"VOICE_HANDSFREE"`, `"'hold' (default): hold to talk"`)


### Autonomous Proactive Auto-Activation [In Development]

What: A setting to automatically activate autonomous background operation at launch for entitled users.

Status: New setting infrastructure added; activation depends on entitlement.

Details:
- When `true`, proactive mode activates automatically at launch (if entitled)
- When `false` or `null`, the user must opt in via `/proactive` or `--proactive`
- Described as "Autonomous background operation configuration"

Evidence: Proactive auto-activate setting (search for `"Autonomous background operation configuration"`, `"When true, autonomous background operation is activated automatically at launch"`)

### /tag Command
The `/tag` command for toggling searchable tags on sessions has been entirely removed. All related UI (tag confirmation dialog, tag display in resume, tag-based search prioritization) has been removed.


### /vim Command
The `/vim` command for toggling between Vim and Normal editing modes has been removed.


### Sleep Tool
The `Sleep` tool (for waiting/resting) has been removed from the tool set.


### Pre-generated Seccomp BPF Filters
The old approach of shipping pre-generated BPF filter files (`unix-block.bpf`) for seccomp sandboxing has been replaced with a multicall binary approach using `/proc/self/exe` and `ARGV0` dispatch. The `vendor/seccomp/` directory and architecture-specific filter lookup code have been removed.


### Skill Improvement Feature
The infrastructure for auto-improving skill definition files based on user preferences has been removed (the "You are editing a skill definition file" prompt and related code).


### `--session-timeout` Flag
The `--session-timeout` CLI flag has been removed.
