# Changelog for version 2.1.126

## Summary
This is a small release that removes the model-specific malware-analysis system reminder previously injected into file reads, persists `/effort` selections to user settings so the choice survives across sessions, and extracts the streaming idle-timeout calculation into a small helper. Most of the diff is version-string churn (2.1.124 → 2.1.126); the user-visible changes are limited to those three areas.


### `/effort` selections are now persisted to user settings
What: Choosing an effort level with the `/effort` slash command now writes the value to your user settings file, so it persists across sessions and across Claude Code restarts. Previously, an `/effort` change only mutated in-memory session state — when you started a fresh session the selection reverted.

Usage:
```
/effort high     # persisted to userSettings.effortLevel = "high"
/effort medium   # persisted
/effort auto     # clears the persisted effortLevel (writes undefined)
```

Details:
- The command now invokes the settings writer (`I6("userSettings", { effortLevel: $ })`) in addition to the existing in-session update.
- If the write fails (read-only filesystem, permissions, etc.), the command returns a new error message: `Failed to set effort level: <reason>`.
- The session-scoped guard for non-allowed values is unchanged: only `low`, `medium`, `high`, and `xhigh` propagate to remote sessions; other values still produce the existing "session-scoped and won't reach the remote process" warning.
- `/effort auto` likewise clears the persisted `effortLevel` (writes `undefined`), so resetting works symmetrically.

Evidence: `/effort` command handler now persists to settings (search for the new error string `"Failed to set effort level: "` and the call `I6("userSettings", { effortLevel"`). The prior version's handler had no `I6("userSettings", ...)` call at all.


### Read-tool no longer injects a model-specific malware-analysis system reminder
What: When the Read tool returned the contents of a file, prior versions appended a `<system-reminder>` instructing the assistant to treat any file content as potentially malware and to refuse to "improve or augment" the code while still allowing analysis. That reminder has been removed entirely, along with the per-file model tracking that decided when to inject it.

User impact:
- File reads now produce cleaner output without an extra trailing system reminder block.
- Models that previously received the reminder (Claude 3 Opus/Sonnet/Haiku, 3.5 Sonnet/Haiku, 3.7 Sonnet, Sonnet 4.0/4.5, Opus 4.0/4.1/4.5, Haiku 4.5) will no longer be auto-instructed to refuse to "improve or augment" code in the file. In practice this means Claude Code can edit code in files it has read without that hardcoded refusal cue in its context.
- The model-tracking `WeakMap` that recorded which model read which file (`qB7`) is gone, as is the hardcoded model allowlist (`oB_`) used to gate the reminder.

For users who relied on Claude pushing back on suspicious-looking code in read files, you may notice it doing so less aggressively; behavior now derives only from the model's own training and your project instructions, not from a hardcoded reminder.

Evidence:
- The system-reminder string `"Whenever you read a file, you should consider whether it would be considered malware..."` was removed (search for it in v2.1.124 — present; v2.1.126 — absent).
- The model allowlist `Set(["claude-3-opus", "claude-3-sonnet", ..., "claude-haiku-4-5"])` was removed.
- File-read formatter simplified from `q = sB_(H) + iB_(H.file) + (aB_(K) ? rB_ : "")` (with conditional reminder) to `q = rB_(H) + iB_(H.file)` (no reminder).
- The line `qB7.set(Z, M.options.mainLoopModel)` that recorded the reading model per text block was removed.


### Streaming idle-timeout calculation extracted into a helper
What: The logic that decides how long the SSE/streaming HTTP layer waits before declaring an idle stream dead has been pulled into its own function. Behavior is effectively unchanged — both before and after, the timeout is the maximum of the user's `CLAUDE_STREAM_IDLE_TIMEOUT_MS` env var and a 300000 ms (5 minute) floor.

Details:
- Previous inline expression: `Math.max(parseInt(process.env.CLAUDE_STREAM_IDLE_TIMEOUT_MS || "", 10) || 90000, 300000)`.
- New helper: `Math.max(Number(process.env.CLAUDE_STREAM_IDLE_TIMEOUT_MS) || 0, 300000)`.
- The 90000 fallback in the old version was always dominated by the 300000 floor, so the 5-minute minimum is preserved.
- The env var continues to behave the same: setting `CLAUDE_STREAM_IDLE_TIMEOUT_MS` above 300000 raises the timeout; values at or below 300000 are clamped to the 5-minute floor.

This is mostly an internal cleanup, but documented here because `CLAUDE_STREAM_IDLE_TIMEOUT_MS` is a user-configurable env var — its semantics are unchanged in this release.

Evidence: New function returning the timeout (search for `"CLAUDE_STREAM_IDLE_TIMEOUT_MS"`); call site previously had the inline `Math.max(...)` expression and now invokes the helper.


### Re-running an initialization step on a code path
A second invocation of an internal initialization function was added to a top-level setup block (effectively `OF(); OF();` instead of a single call). This pattern usually indicates a "the second call ensures X is reset/applied after some intervening side effect" fix. There is no user-facing string change associated with it, but it is included here for completeness because it is one of only a handful of non-version-bump structural diffs in this release.

Evidence: structural diff in the `Wh6` initializer adds a duplicate `OF()` call after the existing `OF()` call.


## Notes
- The release notes / onboarding-version comparators were rewritten as new functions (`OK5`, `N55`, `MI5`) replacing the old (`wK5`, `h55`, `jI5`). This is a pure version-string churn artifact: each function compares the user's last-seen version to the constant `2.1.126` instead of `2.1.124`. No behavior change.
- This release does **not** bump any models, change any commands or flags, add any settings, or alter permission rules. If you only care about user-facing surface area, the two notable changes are persistent `/effort` and the removal of the Read-tool malware reminder.
