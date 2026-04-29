# Changelog for version 2.1.119

## Summary

This is a major release that introduces the **Claude Daemon** — a persistent background service with installable system service support (launchd/systemd), interactive management via the new `claude agents` fleet view, and a complete suite of CLI commands (`claude attach`, `claude kill`, `claude logs`, `claude rm`). It adds three new scheduled routines (morning check-in, catch-up, pre-meeting check-in) alongside the enhanced dream/memory consolidation system. Significant new settings, MCP tool name validation, session pinning, and many new SDK options round out the release.


### Fleet View (`claude agents`)

What: A full-screen interactive TUI dashboard for managing all background agent sessions from a single place.

Usage:
```bash
claude agents
```

Details:
- Displays all background sessions with live status: working, blocked, done, idle
- Jobs can be grouped by **directory** or **state** (toggle with `Ctrl+S`)
- Sessions can be **pinned** to the top of the list (`Ctrl+T`) for quick access; pins persist across sessions in `.pins.json`
- Sessions can be **renamed** inline (`Ctrl+R`)
- Sessions can be **deleted** (`Ctrl+X` to arm, press again to confirm; also stops running sessions)
- Sessions can be **reordered** within a group (`Shift+Up/Down`)
- A **peek panel** (`Space`) shows a split-view with reply input and session details
- An **input field** at the bottom lets you describe a new task to dispatch a new agent session — supports `@template` autocomplete and `/skill` slash commands
- PR status integration: for jobs monitoring PRs, shows CI pass/fail, review status, additions/deletions
- Quick-open numbered sessions with `Cmd+1-9`
- Help panel via `?` shows all keybindings
- Empty state shows helpful suggestions: "paste a link, or 'review PR #123 for bugs' · 'fix the failing test' · 'babysit my PR until CI passes'"

Evidence: Fleet view system (search for `"claude agents"`, `".fleetview-heartbeat"`, `"Agents here keep running"`)


### CLI Commands for Background Session Management

What: A suite of new top-level CLI commands for managing background sessions without entering the interactive fleet view.

Usage:
```bash
claude attach <id>    # Attach to a running background session
claude kill <id>      # Stop a background session
claude logs <id>      # Show recent output from a session
claude rm <id>        # Remove worktree and job state for a stopped session
claude respawn <id>   # Respawn an exited session
```

Details:
- After backgrounding a session, these commands are displayed as a quick reference
- `claude kill` retains the worktree (if used); prints `"worktree retained at <path>"` with a hint to use `claude rm <id>` for full cleanup
- `claude rm` removes both the worktree and job state files
- `claude respawn --all` respawns all exited sessions at once

Evidence: Session management commands (search for `"claude attach <id>"`, `"claude kill <id>"`, `"claude rm <id>"`, `"claude logs <id>"`)


### Daemon Service Management (`claude daemon install/uninstall`)

What: Install the Claude daemon as a persistent system service (launchd on macOS, systemd on Linux) so it runs automatically on boot and survives terminal closures.

Usage:
```bash
claude daemon install     # Install as a system service
claude daemon uninstall   # Remove the system service
claude daemon start       # Start the daemon
claude daemon stop        # Stop the daemon
claude daemon restart     # Restart the daemon
claude daemon status      # Show daemon status and PID
claude daemon log         # View daemon logs
```

Details:
- On macOS, installs as a launchd agent (`com.anthropic.claude-daemon`)
- On Linux, installs as a systemd user unit with `Restart=always` and rate limiting (10 bursts per 60s)
- The daemon manages all background workers: scheduled tasks, remote control servers, assistants, and heartbeat workers
- Hot-reloads `daemon.json` configuration automatically (chokidar watcher with debounce)
- Centralized OAuth token management — proactively refreshes tokens, broadcasts to workers via IPC
- If headless auth fails, writes `daemon-auth-status.json` and sends a desktop notification prompting `claude auth login`
- Logs to `~/.claude/daemon.log`
- Idle exit: daemon shuts down after a configurable period with no clients (unless installed as a service)

Evidence: Daemon service management (search for `"Install service"`, `"Uninstall service"`, `"com.anthropic.claude-daemon"`, `"daemon.status.json"`)


### Daemon Configuration (`daemon.json`)

What: A new JSON configuration file at `~/.claude/daemon.json` that defines persistent background workers.

Usage:
```json
{
  "scheduled": [{
    "tasks": [{
      "id": "my-task",
      "cron": "*/30 * * * *",
      "prompt": "Check for new issues",
      "directory": "/path/to/project",
      "permissionMode": "dontAsk"
    }],
    "maxConcurrent": 1
  }],
  "remoteControl": [{
    "dir": "/path/to/project",
    "spawnMode": "worktree",
    "capacity": 32
  }]
}
```

Details:
- Worker kinds: `scheduled` (cron tasks), `remoteControl` (bridge to claude.ai), `heartbeat` (health monitoring)
- Configuration changes are hot-reloaded — the daemon diffs old vs new config and starts/stops/restarts only changed workers
- Unknown config keys are reported but don't block startup
- Interactive management via the `/daemon` slash command with tabbed UI for Scheduled Tasks, Remote Control, and Assistants
- Each tab supports add, edit, remove, enable/disable operations with inline forms

Evidence: Daemon configuration system (search for `"daemon.json"`, `"config validation failed"`, `"config reload failed"`)


### Interactive Daemon Hub (`/daemon`)

What: A new slash command providing a tabbed interactive UI for managing daemon services.

Usage:
```
/daemon
```

Details:
- **Scheduled** tab: lists all scheduled tasks with cron expression, directory, prompt, enabled/disabled status, permission mode, model, and timeout. Supports enable/disable, edit, and remove actions
- **Remote Control** tab: lists remote-control servers with directory, spawn mode, and running status
- **Assistants** tab: shows assistant entries with options to restart, clear conversation history, and uninstall
- **New Scheduled Task** form: accepts prompt, schedule (intervals like `5m`, `2h`, `1d` or cron expressions with live human-readable preview), directory, auto-generated ID, permission mode, and model selection
- **New Remote Control Server** form: accepts directory (with trust check), name, and spawn mode (same-dir or worktree)
- **New Assistant** form: accepts directory, name, permission mode, and model
- Service management buttons: Install, Uninstall, Start, Stop, Restart

Evidence: Daemon hub UI (search for `"Claude Daemon"`, `"New Scheduled Task"`, `"New Remote Control Server"`)


### Morning Check-In Routine

What: An automated morning briefing that fires before the workday begins, pulling calendar events, overnight messages, and priority items.

Details:
- Fires at a random time between 7:00-8:59am daily (randomized to avoid thundering herd)
- Installed as a permanent scheduled task when an assistant is set up
- Reviews today's calendar events, identifies prep needs, and schedules dynamic pre-meeting check-ins
- Scans overnight inbox for unread email and chat mentions from important contacts
- Identifies the single most important priority for the day
- Outputs a concise brief: calendar summary, items needing attention, and top priority
- Time guard: skips if fired more than 2 hours after configured work start time
- Registered as the skill `/morning-checkin` at `.claude/skills/morning-checkin/SKILL.md`

Evidence: Morning check-in routine (search for `"morning-checkin"`, `"/morning-checkin"`)


### Catch-Up Routine

What: A periodic ambient awareness system that checks on tracked priorities every 2 hours during work hours.

Details:
- Fires every 2 hours via cron (`0 */2 * * *`)
- Respects configurable quiet hours (default: 9am-5pm Mon-Fri) — silently exits outside that window
- Maintains a persistent priority list in `.claude/catch-up-state.json` tracking: `priorities`, `lastSnapshot`, `lastRunAt`, and `noiseFloor`
- On first run, bootstraps 2-3 priorities from `CLAUDE.md` and connected tools
- For each priority: checks if state has changed since last snapshot across source control, chat, email, calendar, docs, and issue tracking
- Triages findings into: assistant-can-act, user-should-act, FYI, or suppress
- When calendar events are found, dynamically schedules one-shot `/pre-meeting-checkin` tasks 2-15 minutes before each event
- If nothing is actionable, outputs `"Nothing actionable."` and the main agent won't relay it
- Learns over time: promotes new items, prunes resolved ones, demotes unchanged items

Evidence: Catch-up routine (search for `"catch-up-state.json"`, `"/catch-up"`)


### Pre-Meeting Check-In Routine

What: A dynamically-scheduled notification that fires 2-15 minutes before calendar events with meeting context and prep materials.

Details:
- Not on a fixed schedule — created as one-shot cron tasks by the morning check-in and catch-up routines
- Assembles: meeting document outline (if linked), recent chat/email context related to attendees, open questions from priorities, and notes from previous occurrences of recurring meetings
- Sends a notification directly to the user (runs in `main` context, not `fork`)
- Output format: meeting title, time to start, attendees, doc link, relevant context, and open items
- Offers to draft talking points or agenda but doesn't do so unasked

Evidence: Pre-meeting check-in routine (search for `"pre-meeting-checkin"`, `"/pre-meeting-checkin"`)


### Background Session Lifecycle UI

What: New interactive UI flows for backgrounding, detaching, and managing the lifecycle of sessions.

Details:
- **Background confirmation dialog**: when backgrounding a session, shows "Background this session?" with options to keep running or detach
- `Backgrounding…` progress indicator while the session is being forked to the background daemon
- After backgrounding: shows helper commands (`claude agents`, `claude attach`, `claude kill`, `claude logs`)
- **Detach prompt**: "Detach (keep running)" option to leave a session while it continues in the background
- **Warning for running tasks**: "Background anyway (tasks will be abandoned)" when background tasks are active
- **Nothing to background**: shows "Nothing to background yet — send a message first" if no conversation exists
- **Cannot background**: shows "Cannot background — session persistence is disabled" when persistence is off
- Session status labels: `"idle — waiting for trigger"`, `"idle — attach to send a prompt"`, `"actively progressing on the task"`, `"stopped from session"`
- Exit command description updated: "Exit the CLI (in a background session: detach or stop)"

Evidence: Background session UI (search for `"Background this session?"`, `"Backgrounding"`, `"Nothing to background yet"`, `"Leave background session"`)


### Daemon Assistant Scaffolding

What: When setting up a daemon assistant, Claude Code scaffolds a complete directory structure with skill files, scheduled tasks, memory system, and personality templates.

Details:
- Creates `.claude/agents/assistant.md` — a voice-and-values template defining Claude's personality ("Warm, not performative / Smart, not showy / Direct, not blunt / Collaborative, not obedient")
- Creates `CLAUDE.md` at the project root — a user profile template with fields for name, timezone, work schedule, communication preferences, and catch-up hours
- Sets up skill directories for all four routines: `dream`, `catch-up`, `morning-checkin`, `pre-meeting-checkin`
- Pre-populates `.claude/scheduled_tasks.json` with three permanent tasks
- Initializes `.claude/catch-up-state.json` with empty state
- Memory directory established at `~/.claude/projects/<hash>/memory/`

Evidence: Assistant scaffolding (search for `"assistant.md"`, `"voice and values"`, `"About The User"`)


### Session Pinning in Fleet View

What: Pin important sessions to the top of the fleet view for quick access.

Usage:
In the `claude agents` view, press `Ctrl+T` on any session to pin/unpin it.

Details:
- Pinned sessions appear in a "Pinned" group at the top of the list
- Pins persist across sessions via `.pins.json` in the global config directory
- Auto-expands the pinned group when pinning a new session
- Available via `Ctrl+T` keybinding in the fleet view

Evidence: Session pinning (search for `".pins.json"`, `"pin to top"`, `"ctrl+t to pin"`)


### Remote Control Server Configuration

What: Configure Remote Control bridge servers as persistent daemon workers, making sessions accessible from claude.ai.

Details:
- Configured via `daemon.json` under the `remoteControl` key
- Each server maps a local directory to a Remote Control endpoint
- **Spawn mode**: `same-dir` (default) shares the directory, `worktree` gives each session its own git worktree
- Configurable capacity (default 32 concurrent sessions), permission mode, sandbox mode, and session timeout
- Sessions can be created on daemon start with `createSessionOnStart: true`
- Manages the Remote Control bridge headlessly with automatic OAuth token management

Evidence: Remote control server configuration (search for `"remote-control server"`, `"New Remote Control Server"`, `"spawnMode"`)


### New Settings

What: Several new user-configurable settings have been added.

Details:
- `prUrlTemplate` — URL template for PR links in the footer badge and inline messages. Supports placeholders: `{host}`, `{owner}`, `{repo}`, `{number}`, `{url}`. Example: `"https://reviews.example.com/{owner}/{repo}/pull/{number}"` (search for `"URL template for PR links"`)
- `theme` — now documented with `.describe("Color theme for the UI")` (search for `"Color theme for the UI"`)
- `fileCheckpointingEnabled` — now documented with `.describe("Snapshot files before edits so /rewind can restore them")` (search for `"Snapshot files before edits"`)
- `timestampMessages` — stamps each assistant message with its arrival time, described as `'Show "Cooked for Nm Ns" after each assistant turn'` (search for `"Cooked for"`)
- `todoTrackingEnabled` — enables the todo/task tracking panel, described as `"Enable the todo / task tracking panel"` (search for `"Enable the todo"`)
- `notificationChannel` — preferred OS notification channel (search for `"Preferred OS notification channel"`)
- `showFullToolOutput` — shows full tool output instead of truncated summaries (search for `"Show full tool output"`)
- `keybindingMode` — key binding mode for the prompt input (search for `"Key binding mode"`)
- `remoteControlAtStartup` — start Remote Control bridge automatically each session (already existed, now with description)
- `autoUploadSessions` — mirror local sessions to claude.ai as view-only (already existed, now with description)

Evidence: New settings (search for the `.describe(` strings listed above)


### Auto-Compact Interactive Configuration (`/autocompact`)

What: A new slash command with both interactive slider UI and text-mode for configuring the auto-compact window size.

Usage:
```
/autocompact           # Opens interactive slider dialog
/autocompact 500k      # Sets window to 500,000 tokens
/autocompact auto      # Resets to automatic (recommended)
```

Details:
- Interactive mode: slider with up/down arrows, wrapping to "Auto" at boundaries
- Accepts token values in various formats: `500k`, `200000`, `200` (shorthand for 200,000), range 100k-1M
- Reset with: `auto`, `reset`, `unset`, or `default`
- Displays current window size, source (env var, settings, or auto), and whether it's capped by the model limit
- Shows warnings when: auto-compact is disabled, env var `CLAUDE_CODE_AUTO_COMPACT_WINDOW` takes precedence, or when overriding auto
- Strongly recommends the auto setting: "The auto setting picks a window tuned for your model and is strongly recommended for the best cost and performance."

Evidence: Auto-compact configuration (search for `"Auto-compact Window"`, `"Configure the auto-compact window size"`, `"CLAUDE_CODE_AUTO_COMPACT_WINDOW"`)


### MCP Tool Name Validation

What: Claude Code now validates MCP tool names against the emerging MCP naming standard and warns about non-conforming names.

Details:
- **Hard failures** (tool rejected): empty names, names exceeding 128 characters, names with characters outside `[A-Za-z0-9._-]`
- **Soft warnings** (tool registered but warning logged): names with spaces, commas, leading/trailing dashes or dots
- Warning output references the MCP specification proposal: [SEP: Specify Format for Tool Names](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/986)
- Registration proceeds for soft warnings: "Tool registration will proceed, but this may cause compatibility issues."

Evidence: Tool name validation (search for `"Tool name validation warning"`, `"Tool name contains invalid characters"`, `"Allowed characters are"`)


### Spawn Mode for Worktree Isolation

What: Background sessions and remote control servers can now be configured to use git worktree isolation, giving each session its own isolated copy of the repository.

Details:
- Configured via `--spawn-mode worktree` or in daemon.json `spawnMode: "worktree"`
- System prompt injected for worktree sessions: "This is a git worktree — an isolated copy of the repository"
- Agents in worktree mode are instructed to call `EnterWorktree` as their first action
- Session records now carry `worktreePath`, `worktreeBranch`, and `worktreeHookBased` fields
- After killing a worktree session, the worktree is retained with a hint to use `claude rm` for cleanup

Evidence: Worktree spawn mode (search for `"--spawn-mode"`, `"spawnMode"`, `"worktree retained at"`)


### `--json-path` Flag for Daemon

What: New CLI flag to override the default daemon configuration file path.

Usage:
```bash
claude daemon --json-path=/path/to/custom-daemon.json run
```

Details:
- Default path remains `~/.claude/daemon.json`
- Useful for running multiple daemon instances with different configurations
- Also exposed in service installation (ExecStart includes `--json-path`)

Evidence: JSON path flag (search for `"--json-path"`)


### `--setting-sources` Flag

What: New CLI flag to control which settings sources are loaded.

Usage:
```bash
claude --setting-sources=user,project,local
```

Details:
- Comma-separated list of setting sources: `user`, `project`, `local`
- Allows restricting which settings layers are applied for a session

Evidence: Setting sources flag (search for `"--setting-sources"`, `"Comma-separated list of setting sources"`)


### MCP Completion Support (`McpCompletable`)

What: Added support for MCP completion/autocomplete of prompts and resource templates.

Details:
- New `McpCompletable` type registered as `Symbol.for("mcp.completable")`
- Validates completion request types: prompts must use `ref/prompt`, resource templates must use `ref/resource`
- Provides structured error messages: "Expected CompleteRequestPrompt, but got ..." / "Expected CompleteRequestResourceTemplate, but got ..."

Evidence: MCP completions (search for `"McpCompletable"`, `"mcp.completable"`, `"Expected CompleteRequestPrompt"`)


### Enhanced Dream/Memory Consolidation

The dream routine has been upgraded from simple hardcoded prompts to a structured 4-phase SKILL.md with explicit protocol:
- **Phase 1 (Preparation)**: Reviews `logs/YYYY/MM/YYYY-MM-DD.md` entries and session transcripts
- **Phase 2 (Topics)**: Extracts events, lessons, and decisions into topic files (`<topic-slug>.md`)
- **Phase 3 (Rules & Learnings)**: Records painful/inefficient experiences and user frustrations in `learnings/<learning-slug>.md`
- **Phase 4 (Prioritization & Pruning)**: Keeps `MEMORY.md` under 200 lines, removes stale entries, adds newly important ones
- Now scheduled as a permanent task at a random time between 1:00-4:59am

Evidence: Dream SKILL.md (search for `"Nightly reflection and consolidation"`, `"Prioritization and Pruning"`)


### Revised Usage Limit Messaging

Usage limit messages have been updated to use "usage allocation" terminology for certain seat types:
- "Your usage allocation has been disabled by your admin" (new)
- "Now using your usage allocation" / "You're now using your usage allocation" (new)
- "Your seat type doesn't include usage" / "Your seat type doesn't include extra usage" (new)
- "Your org is out of usage · add funds to continue" / "· contact your admin" (new)
- "Your group's usage limit is set to $0" (new)
- Removed: "Request extra usage", "Switch to extra usage"

Evidence: Updated usage strings (search for `"usage allocation"`, `"Your seat type doesn't include"`)


### Improved EPIPE/EIO Error Handling

The stdout/stderr error handler now handles `EIO` in addition to `EPIPE`, and properly triggers a graceful exit callback when stdout encounters these errors.

Evidence: Stream error handling (search for `"EIO"` in `hJ8` function near line ~8728)


### Skill Tool Description Update

The Skill tool description has been updated to clarify `skill` parameter usage:
- Removed: "Set `skill` to the exact name of an available skill (no leading slash)"
- Added: "Only invoke a skill that appears in that list, or one the user explicitly typed as `/<name>` in their message. Never guess or invent a skill name from training data"
- Added the concept of `plugin:skill` fully qualified names for plugin-namespaced skills

Evidence: Skill tool description (search for `"Never guess or invent a skill name"`)


### Slash Command Aliases

Slash commands now support explicit alias definitions with the description: "Alternate names that resolve to this command (e.g., /cost and /stats both resolve to /usage)".

Evidence: Command aliases (search for `"Alternate names that resolve to this command"`)


### Stale File Notification

When a file has been modified on disk after Claude last read it, users now see a warning: "is now stale relative to disk — Read it again if you need current contents."

Evidence: Stale file warning (search for `"is now stale relative to disk"`)


### Fast Mode Switching in Remote Sessions

Remote sessions now give a more specific error when trying to switch models: "Model picker shows local options in remote sessions — use /model <name> instead" and "Fast mode switching in remote sessions is coming soon — set at session creation for now".

Evidence: Remote model switching (search for `"remote-model-picker-unavailable"`, `"Fast mode switching in remote sessions"`)


### Pro Trial Lifecycle

The Pro trial flow now includes:
- Trial start screen: "Your Pro plan includes N days of Claude Code"
- Interactive confirmation: "Press Enter to start your trial"
- Progress indicator: "Starting your trial..."
- Error handling: "Couldn't start your trial. Press Enter to continue."
- Trial duration display: "Trial: N day(s) left" in the status area
- Trial expiration route at `/pro-trial-expired`

Evidence: Pro trial lifecycle (search for `"Pro trial started"`, `"Your Pro plan includes"`, `"Starting your trial"`)


### SDK Enhancements

Several new options are available for the Agent SDK:
- `askUserQuestion.previewFormat` exposed via `CLAUDE_CODE_QUESTION_PREVIEW_FORMAT` env var
- `canUseTool` callback for dynamic tool permission decisions (mutually exclusive with `permissionPromptToolName`)
- `getOAuthToken` callback for custom OAuth token provision
- Input/output validation with structured error messages: "Input validation error: Invalid arguments for tool" / "Output validation error: Invalid structured content for tool"
- Tool annotations support via Zod schemas
- `taskSupport` for tools: `"required"` (needs task augmentation) vs `"forbidden"` (must use `registerTool()` instead)

Evidence: SDK enhancements (search for `"CLAUDE_CODE_QUESTION_PREVIEW_FORMAT"`, `"canUseTool callback"`, `"Output validation error"`)


### Improved Zod Schema Support

Added support for Zod Mini (`ZodMiniType`, `ZodMiniObject`) alongside existing Zod schemas, with automatic detection and mixed-version handling. The system now throws a clear error on mixed versions: "Mixed Zod versions detected in object shape."

Evidence: Zod Mini support (search for `"ZodMiniType"`, `"ZodMiniObject"`, `"Mixed Zod versions"`)


### Enhanced JSON Schema Generation

Significantly expanded `zodToJsonSchema` converter supporting:
- `jsonSchema2019-09` target with `unevaluatedProperties` support
- OpenAI-specific type handling (`OpenAiAnyType`) with reference strategies
- Date strategies: `format:date-time`, `format:date`, `string`, `integer` (unix-time)
- Email strategies: `format:email`, `format:idn-email`, `pattern:zod`
- Base64 strategy: `contentEncoding:base64`
- Warning messages for OpenAI compatibility: "Warning: OpenAI may not support records in schemas!" / "Warning: OpenAI may not support schemas with unions as roots!"

Evidence: JSON schema generation (search for `"jsonSchema2019-09"`, `"OpenAiAnyType"`, `"Warning: OpenAI may not support"`)


## Bug Fixes

- Fixed handling of `EPIPE` and `EIO` errors on stdout/stderr — now properly destroys the stream and triggers a graceful exit callback instead of silently failing (search for `"EIO"`)
- Improved handling of failed daemon connections: "Couldn't reach the daemon — it may be restarting. Press Enter to retry" instead of silent failure (search for `"Couldn't reach the daemon"`)
- Added protection against recursive Zod schema references: "Recursive reference detected at" (search for `"Recursive reference detected"`)
- Fixed regex pattern conversion failures with descriptive error: "Could not convert regex pattern at" (search for `"Could not convert regex pattern"`)
- Added validation for `--permission-mode` flag values: "must be one of" (search for `"--permission-mode must be one of"`)
- Added guard against duplicate task IDs: "task ids must be unique" (search for `"task ids must be unique"`)
- Fixed transcript mirroring with bounded retry (3 attempts with short backoff; timeouts are not retried) to prevent silent data loss (search for `"TranscriptMirrorBatcher"`)
- Added timeout handling for `SessionStore` operations: `append()`, `load()`, `listSessions()`, `listSubkeys()` all now have explicit timeout errors (search for `"SessionStore.append() timed out"`)
- Fixed speculation pausing for backgrounded shells: "Speculation paused: backgrounded shell" (search for `"Speculation paused: backgrounded shell"`)


### Claude Code Insights HTML Report

The full HTML-based "Claude Code Insights" report generator — which produced an interactive dashboard with charts, project areas, friction analysis, usage patterns, and suggestions — has been removed from the CLI. The removal includes all HTML templates, CSS styles, JavaScript interactivity (timezone selector, collapsible sections, copy buttons), and the data rendering pipeline.

Evidence: Removed Insights template (search for `"Claude Code Insights"` — reduced from 5 occurrences to 3 minor references)


### Autofix PR Inline Component

The `cG1` React component for `/autofix-pr` — which handled inline PR monitoring setup, Remote Control subscription, and session spawning — has been removed from the bundled source. (The broader autofix-pr infrastructure remains, suggesting this was refactored rather than removed entirely.)

Evidence: Removed autofix-pr component (the `cG1` function at old line ~472814 is gone; search for `"tengu_autofix_pr"` still returns hits in both versions)


### /init Command Prompt Refactoring

The large inline `/init` command prompt (which guided the multi-phase CLAUDE.md setup flow) has been removed from the bundled source. The `/init` command likely still exists but its prompt content has been restructured or externalized.

Evidence: Removed init prompt (the `cN1` string at old line ~492860 covering Phases 1-8 is gone)


## Notes

- The daemon installation (`claude daemon install`) creates a system service — users should run `claude daemon uninstall` before major upgrades if they experience issues with the service
- The `daemon.json` configuration format is new; there is no migration from previous daemon configurations since the daemon infrastructure was previously minimal
- Scheduled routines (morning-checkin, catch-up, pre-meeting-checkin) are installed when creating a daemon assistant via the `/daemon` command — they are not automatically enabled for existing setups
- The fleet view (`claude agents`) replaces the previous "List configured agents" description with "Manage background and configured agents", reflecting its expanded interactive capabilities
