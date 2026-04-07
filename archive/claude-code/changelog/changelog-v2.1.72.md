# Changelog for version 2.1.72


## Summary

This is a substantial release that introduces the **SendUserMessage** tool for structured agent-to-user communication, an **ExitWorktree** tool for mid-session worktree management, and a new **Brief mode** compact chat view. The remote control system receives a major overhaul with unified `--spawn` flags, auto mode gets an opt-in dialog and a settings-level disable option, and the bash security analyzer is rewritten to use tree-sitter AST analysis for more accurate shell command validation. GCP/Vertex users gain automatic credential refresh, and effort level now supports a session-scoped "max" setting.


### SendUserMessage Tool

What: A new tool that lets Claude post structured checkpoint messages to the user, designed for async workflows where the user may only be reading a compact view of the conversation.

Usage: Claude calls SendUserMessage with a message, optional file attachments, and a status (`proactive` for push notifications, `normal` for replies).

Details:
- Messages are concise, outcome-focused checkpoints — like commit messages, not recaps
- Supports markdown formatting and file attachments (screenshots, diffs, logs)
- `proactive` status is for reaching the user's phone when they're away (task done, blockers, questions)
- `normal` status is for replies to active conversations
- Tied to a new `defaultView` setting: `"chat"` shows only SendUserMessage checkpoints, `"transcript"` shows the full output

Evidence: New tool constant and prompt definition (search for `"SendUserMessage"`)


### ExitWorktree Tool

What: A new tool that allows exiting a worktree session mid-conversation without ending the session, returning to the original working directory.

Details:
- Accepts `action: "keep"` to preserve the worktree and branch on disk, or `action: "remove"` to delete both
- When removing a worktree with uncommitted changes, requires explicit `discard_changes: true` confirmation
- Checks for uncommitted files and unmerged commits before removal
- Only operates on worktrees created by EnterWorktree in the current session
- The EnterWorktree tool message now references ExitWorktree: "Use ExitWorktree to leave mid-session, or exit the session to be prompted"

Evidence: New tool definition (search for `"ExitWorktree"`)


### Brief Mode (Compact Chat View)

What: A new compact view mode that shows only checkpoint messages (from SendUserMessage) instead of the full tool-call transcript, with dedicated visual styling.

Details:
- Controlled by the `CLAUDE_CODE_BRIEF` environment variable or the `tengu_kairos_brief` feature flag
- Adds a `Brief` tool and `BRIEF_TOOL_NAME` / `LEGACY_BRIEF_TOOL_NAME` constants
- User messages display with a "You" label in blue; Claude's responses use a distinct orange label
- When brief-only mode is active, the token usage bar is hidden and the spinner uses a simplified dots animation
- Toggle via a new "Toggle brief-only mode" action

Evidence: Brief mode infrastructure (search for `"CLAUDE_CODE_BRIEF"`, `"tengu_kairos_brief"`, `"isBriefOnly"`)


### Auto Mode Opt-In Dialog

What: When launching Claude with `--mode auto`, users who haven't previously opted in now see a consent dialog explaining what auto mode does.

Details:
- Dialog text: "Auto mode lets Claude run commands without prompting — each action is first checked for safety. Claude can still make mistakes; use in isolated environments."
- Declining the dialog exits the application
- Once accepted, the opt-in is remembered
- New "Yes, and use auto mode" and "Yes, clear context" options in the context-clearing prompt

Evidence: New dialog component (search for `"AutoModeOptInDialog"`)


### Remote Control Spawn Mode Overhaul

What: The remote control `--spawn-worktree-sessions` and `--spawn-same-dir-sessions` flags are replaced with a unified `--spawn <mode>` flag and a new `--capacity` flag.

Usage:
```bash
claude remote-control --spawn=worktree --capacity=4
claude remote-control --spawn=same-dir
claude remote-control --spawn=session
```

Details:
- `--spawn` accepts `same-dir` (default), `worktree`, or `session`
- `--capacity` sets the max concurrent sessions (not valid with `--spawn=session`, which has fixed capacity 1)
- New `--create-session-in-dir` / `--no-create-session-in-dir` flag controls whether a session is pre-created in the current directory
- Interactive spawn mode picker (`w to toggle spawn mode`) when starting remote control
- Spawn mode preference is saved per-project
- Falls back to `same-dir` if saved mode is `worktree` but the directory isn't a git repo
- Error message updated: "Error: Multi-session Remote Control is not enabled for your account yet."

Evidence: New spawn mode infrastructure (search for `"spawn mode"`, `"--spawn"`, `"--capacity"`)


### GCP Auth Refresh

What: A new `gcpAuthRefresh` setting that automatically refreshes GCP/Vertex AI credentials when they expire, similar to the existing `awsAuthRefresh` for AWS.

Usage: Add to settings or `~/.claude.json`:
```json
{
  "gcpAuthRefresh": "gcloud auth application-default login"
}
```

Details:
- Automatically detects expired GCP credentials ("Could not load the default credentials", "Could not refresh access token", `invalid_grant`)
- Runs the configured refresh command before making API calls
- Times out after 3 minutes with a warning
- Validates credentials before running refresh (skips if still valid)
- Works with Vertex AI authentication (checks `CLAUDE_CODE_USE_VERTEX`)
- Respects the new `CLAUDE_CODE_SKIP_VERTEX_AUTH` environment variable

Evidence: New settings schema field and credential checker (search for `"gcpAuthRefresh"`, `"Could not load the default credentials"`)


### Disable Auto Mode via Settings

What: A new `disableAutoMode` setting that allows organizations or users to disable auto mode entirely.

Usage: Add to settings:
```json
{
  "permissions": {
    "disableAutoMode": "disable"
  }
}
```

Details:
- When set, shows "auto mode disabled by settings" or "auto mode disabled: disableAutoMode in settings"
- Also respects model-level and org-level restrictions: "auto mode disabled: model does not support auto mode", "auto mode disabled: org not in DAC allowlist"
- New DAC (Documented Allowlisting Check) org allowlist system controls auto mode availability per organization
- Auto mode state is tracked with new attachment types (`auto_mode` and `auto_mode_exit`) for proper context management

Evidence: New settings field and gate messages (search for `"disableAutoMode"`, `"auto mode disabled"`)


### Tree-Sitter Bash Security Analyzer Rewrite

The shell command security analyzer has been significantly rewritten to use tree-sitter AST analysis instead of relying solely on string-based heuristics. When tree-sitter is available, it provides authoritative quote context analysis, compound structure detection, and dangerous pattern identification.

New security checks include:
- Arithmetic expansion with variable references
- Heredocs with unquoted delimiters (shell expansion risk)
- Brace expansion syntax detection
- IFS assignment (word-splitting changes)
- Tilde expansion in assignment values
- Unicode whitespace and control character detection
- Zsh `~[` dynamic directory syntax
- Shell keyword misuse detection

When tree-sitter is unavailable, falls back to the legacy shell-quote parser with a log message: "tree-sitter unavailable, using legacy shell-quote path".

Evidence: New analyzer functions (search for `"Tree-sitter quote context is authoritative"`, `"Brace expansion"`, `"IFS assignment"`)


### Effort Level "max" and Persistence

The effort level system now supports a `"max"` level (restricted to Opus 4.6 models) and persists the effort setting across sessions.

Details:
- New `effortLevel` setting in user config: accepts `"low"`, `"medium"`, or `"high"` (persisted)
- `"max"` is session-scoped and not persisted to disk
- If `"max"` is requested on a non-Opus 4.6 model, it silently falls back to `"high"`
- The status line now shows effort level with visual indicators: ○ low, ◐ medium, ● high, ◉ max
- Effort level display text appears in the status bar with a 20-second timeout

Evidence: New effort schema and display functions (search for `"Persisted effort level"`, `"opus-4-6"`)


### Remote Session Timeout Increase

Remote sessions now have a 60-minute timeout, doubled from the previous 30-minute limit.

Evidence: Timeout string change (search for `"remote session exceeded 60 minutes"`)


### Copy on Select

A new `copyOnSelect` user preference has been added to the persistent settings, allowing automatic clipboard copy when text is selected in the terminal.

Evidence: New preference key (search for `"copyOnSelect"`)


### Plan Command Enhancement

The `/plan` command now accepts a description argument to immediately start planning with context, instead of only supporting `open`.

Usage:
```
/plan add authentication to the API
```

Evidence: Argument hint change from `"[open]"` to `"[open|<description>]"`


### Hooks Format Updated

The hooks configuration tip has been updated to reflect the new matcher format. Matchers are now strings (tool names, pipe-separated lists, or empty to match all) instead of objects.

Before: `{"matcher": {"tools": ["BashTool"]}, "hooks": [...]}`
After: `{"matcher": "Edit|Write", "hooks": [...]}`

Evidence: Updated tip text (search for `"matcher + hooks array"`)


### Settings Keybinding Changes

The settings panel keybindings have been updated:
- `enter` now triggers `settings:close` (was `select:accept`)
- `space` remains `select:accept`
- New `scroll:pageDown` and `scroll:pageUp` keybindings added

Evidence: Keybinding map changes (search for `"settings:close"`, `"scroll:pageDown"`)


### Plugin Source Resolution Improvements

- Git repository URLs no longer require a `.git` suffix
- Plugin source path resolution messages now explain that paths are relative to the marketplace root (the directory containing `.claude-plugin/`)
- Marketplace-only fields in `plugin.json` now produce informational warnings instead of errors
- "View on GitHub" link renamed to "View repository" (works with non-GitHub repos)
- Plugin already-installed message clarified to "already installed globally"

Evidence: Schema and message changes (search for `"marketplace root"`, `"marketplace-only fields"`)


### Clipboard Support in tmux over SSH

Clipboard operations now properly support tmux sessions over SSH by writing OSC 52 escape sequences directly to `SSH_TTY` when available, with a fallback to `tmux load-buffer`.

Evidence: New clipboard function (search for `"tmux load-buffer"` in added function `FD7`)


### Feedback Flow Update

When users give a thumbs-down rating, the follow-up prompt now directs them to `/issue` for reporting model behavior issues, rather than general feedback.

Evidence: Feedback text change (search for `"Use /issue to report model behavior issues"`)


### API Error Message Extraction

Better extraction of error messages from nested API error responses. When the top-level `message` field is missing, the system now digs into nested `error.error.message` and `error.message` fields before falling back to a generic status message.

Evidence: New error extraction functions (search for `"API error (status"`)


### Deferred Tools Announcement Simplification

The deferred tools announcement text has been simplified from lengthy explanations to concise notices: "Deferred tools appear by name in `<system-reminder>` messages" or "Deferred tools appear by name in `<available-deferred-tools>` messages."

Evidence: Updated deferred tools text (search for `"Deferred tools appear by name"`)


### SDK Enhancements

- New `agentProgressSummaries` SDK init option for enabling progress summary reporting from agents
- New `applied` field in settings response showing runtime-resolved model and effort values (as opposed to `effective` which only shows disk-merged values)
- Task progress summaries now include a `summary` field in the SDK schema
- `supportsAutoMode` field added to model information schema

Evidence: SDK schema additions (search for `"agentProgressSummaries"`, `"Runtime-resolved values"`)


## Bug Fixes

- Removed `python --version` and `python3 --version` from the auto-allowed command list, ensuring these commands go through normal permission checks (search for `"docker ps"` in the reduced allowlist)
- Fixed voice mode availability check to use a simple boolean state instead of calling an external function, preventing potential errors (search for `"voiceEnabled"`)
- Fixed carriage return handling in text input to not treat `\r` preceded by a backslash as a submit trigger (search for `"replace(/(?<=[^\\\r\n])\r$/"`)
- Improved mouse input handling to filter out raw mouse escape sequences that lack a key name, preventing spurious input events (search for `"^\[<\d+;\d+;\d+[Mm]"`)
- Fixed tmux clipboard detection — mouse reporting is now disabled in tmux sessions to prevent conflicts (search for `"process.env.TMUX"` in function `o_8`)
- Auto mode classifier now checks `requiresUserInteraction` on tools before sending to classifier, preventing interactive tools from being auto-approved (search for `"requiresUserInteraction"`)
- TaskOutput tool's `block` parameter now accepts string booleans (`"true"`/`"false"`) in addition to actual booleans, improving compatibility (search for `"preprocess"` near `"block"`)


### Background Workflows [In Development]

What: Infrastructure for a new "local_workflow" task type that tracks background workflow execution with dedicated status line display.

Status: Infrastructure added but the trigger mechanism is not yet exposed.

Details:
- New task type `local_workflow` alongside existing `local_agent` and `remote_agent`
- Status line shows "1 background workflow" or "N background workflows" count
- The spinner component displays `" · N in background"` when workflows are running

Evidence: Task label generation (search for `"background workflow"`)


### Nova 3 Voice Gate [In Development]

What: A feature flag `tengu_cobalt_frost` gates a "Nova 3" voice stream capability.

Status: Feature-flagged, not yet broadly enabled.

Details:
- Log message: "Nova 3 gate enabled (tengu_cobalt_frost)"
- Likely an upgrade to the voice transcription model

Evidence: Feature flag (search for `"tengu_cobalt_frost"`)


## Notes

**Migration: Remote Control flags** — If you use `--spawn-worktree-sessions` or `--spawn-same-dir-sessions`, these have been replaced by `--spawn=worktree` and `--spawn=same-dir` respectively. The old flags will produce an error directing you to the new syntax.

**Migration: Hooks format** — The hooks matcher format has changed from an object `{"tools": ["BashTool"]}` to a string `"Bash"` or pipe-separated list `"Edit|Write"`. Existing configurations should still work but the error tip now reflects the new format.

**Bundle size reduction** — The RxJS library (Observable, Subscriber, Subscription, and many related classes) has been removed from the bundle, reducing the overall package size. The tree-sitter WASM files and several other large dependencies (lodash templating, spawn-rx internals) have also been cleaned up.
