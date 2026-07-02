# Changelog for version 2.1.191

## Summary

This release introduces an AI-powered contextual tips system that surfaces relevant feature suggestions mid-session based on what you are doing, a team discovery feature that surfaces teammates' shared MCP servers and skills, and MCP tool-level permission policies. It also hardens several security boundaries (Linux automount `/net` paths, Windows drive-relative paths, HIPAA/data-residency Files API restrictions) and fixes a critical config corruption issue affecting users who hit parse errors during writes (GH #3117).


## New Features


### Contextual Tips System [Gradual Rollout]

What: Claude now occasionally surfaces a short, context-aware tip after a response based on an AI analysis of the current conversation — suggesting a relevant command, shortcut, or workflow that fits what you are doing.

How it works:

- After eligible responses, a lightweight sidecar classifier (using the fast model) reads the last ~30 turns of the transcript alongside your session metadata (turn count, MCP servers, team skills) and decides whether a tip is relevant.
- Declining to tip is the expected default — tips only fire when a known situation in the catalog matches. Examples from the catalog include correction spirals, previous-session references, large context windows, and long-running commands.
- Tips include a short 1-2 sentence message, the relevant feature ID, and an optional suggested action (e.g., `/clear`, `claude --resume`).
- You can give feedback on a tip by acting on it; reception is tracked.

Details:
- Gated by the `allow_context_tips` feature flag and the `tengu_context_tip_classifier_outcome` telemetry gate — not all users see tips yet.
- Team discovery metadata (teammate MCP servers and skills) is included in session context to make tips more relevant when working in a shared project.
- Tips are not shown in non-interactive or transcript-mode sessions.

Evidence: Context tip classifier system (search for `"[context-tips] classifier eligible, firing sideQuery"` or `"emit_context_tip"`)


### Team Discovery [Gradual Rollout]

What: Claude Code now silently fetches your organization's shared MCP servers and skills used by teammates and incorporates that information into session context for the tips classifier — so tips can mention tools your team already relies on.

Details:
- Fetches from `/api/claude_code/discovery/team_usage` (gated by `tengu_team_discovery` and `allow_team_discovery`).
- Cached locally to `team-discovery.json` in the Claude cache directory, refreshed at most once per hour.
- Data surfaced in session metadata for the classifier: `teamMcpServers (used by teammates, count is users)` and `teamSkills (used by teammates, count is users)`.
- No data is shown to users directly — it feeds only the contextual tips classifier.

Evidence: Team discovery fetch function (search for `"/api/claude_code/discovery/team_usage"`)


### MCP Tool-Level Permission Policies

What: Individual MCP tools can now declare a `permission_policy` in the MCP server config, allowing fine-grained pre-authorization without manual approval prompts.

Usage:

Set `permission_policy` on any tool entry in your MCP server configuration:

```json
{
  "mcpServers": {
    "myserver": {
      "type": "http",
      "url": "http://localhost:3000",
      "tools": [
        { "name": "read_db",  "permission_policy": "always_allow" },
        { "name": "write_db", "permission_policy": "always_ask"  },
        { "name": "drop_db",  "permission_policy": "always_deny" }
      ]
    }
  }
}
```

Details:
- Accepted values: `always_allow`, `always_ask`, `always_deny`.
- Policies are translated to `mcpServerPolicy` entries in the effective allow/ask/deny rule sets.
- Only applies to `http` and `sse` transport types; stdio tools are unaffected.
- Overrides the default prompt-based approval flow for that specific tool.

Evidence: MCP permission policy resolver (search for `"permission_policy"` alongside `"always_allow"`)


### Linux File Manager Integration (D-Bus)

What: On Linux with a desktop environment, Claude Code can now open files in the native file manager using D-Bus (`org.freedesktop.FileManager1.ShowItems`), mirroring the "Reveal in Finder" behavior on macOS.

Details:
- Uses `dbus-send` to invoke the `ShowItems` method on the `org.freedesktop.FileManager1` interface.
- Falls back silently if D-Bus or a file manager is not available.
- Applies to paths that Claude surfaces in the terminal where an "open in folder" action makes sense.

Evidence: D-Bus ShowItems integration (search for `"org.freedesktop.FileManager1.ShowItems"`)


## Improvements


### Config Corruption Auto-Repair (GH #3117)

What changed: When `~/.claude.json` is found corrupted during a locked save operation, Claude Code now automatically repairs it from the in-memory cached config rather than leaving the file in a corrupted state.

Previously, hitting a parse error on the re-read inside `saveConfigWithLock` would block the write and leave the file unchanged. Now:
1. If a parse error is detected during the locked re-read, the cached in-memory config is used as the recovery source.
2. The repair is logged and reported to telemetry (`tengu_config_auto_repaired`).
3. A timestamped `.corrupted.` backup is still saved so the original can be inspected.
4. The error message changed from `"Config file corrupted, resetting to defaults"` to `"Config file corrupted"` and separately `"Could not back up corrupted config"` for backup failures — more accurate since defaults are no longer the only fallback.

Evidence: Auto-repair path in saveConfigWithLock (search for `"saveConfigWithLock: re-read hit a parse error; auto-repairing from cached config under lock. See GH #3117."`)


### Linux Automount /net Path Protection

What changed: Claude Code now detects and requires manual approval for any read or glob request touching the Linux automount `-hosts` map (paths under `/net/…`). Previously only Windows UNC paths were blocked this way.

Details:
- Accessing `/net/<hostname>/...` silently triggers a DNS lookup and NFS mount to a remote host, which is a potential data-exfiltration and latency vector.
- The new check fires before any other access control decision.
- Message shown: `Claude requested permissions to read from <path>, which is under the /net automount map and could trigger a DNS lookup and NFS mount to a remote host.`
- Decision reason recorded: `"Automount -hosts path detected (defense-in-depth check)"`.
- Both file reads and glob patterns are covered.
- `/proc/net/tcp` and `/proc/net/tcp6` are also in scope (they reveal active network connections on Linux).

Evidence: Automount path detector (search for `"Automount -hosts path detected (defense-in-depth check)"`)


### Windows Drive-Relative Path Security

What changed: Paths of the form `C:filename` (drive-relative, without a backslash) are now flagged and require manual approval rather than being resolved silently.

Details:
- Drive-relative paths resolve against a per-drive current directory (a Windows quirk), which cannot be statically validated at permission-check time.
- Approval message: `Path '<path>' is drive-relative (resolves against the per-drive current directory, which cannot be statically validated) and requires manual approval`.

Evidence: Drive-relative path check (search for `"is drive-relative (resolves against the per-drive current directory"`)


### Files API Restrictions for HIPAA and Data-Residency Orgs

What changed: Attempts to use the Files API now raise an explicit error for two restricted organization types.

- HIPAA-regulated organizations: `"Files API is unavailable for HIPAA-regulated organizations"`
- Third-party provider / data-residency orgs: `"Files API is unavailable on third-party providers (data-residency)"`

Previously these would fail with less informative errors or unexpected behavior.

Evidence: Files API restriction checks (search for `"Files API is unavailable for HIPAA-regulated organizations"`)


### Compliance Taint Notifications

What changed: When your session has active compliance restrictions, a status notification now appears in the UI to make them visible rather than leaving you wondering why certain features aren't available.

Format: `<source> · some features are restricted · /status for details`

Run `/status` to see the full details of what is restricted and why.

Evidence: Compliance taint event push (search for `"some features are restricted · /status for details"`)


### History Picker: Previous Session Entry

What changed: The history picker now shows a dedicated entry at the top for the previous session, labeled `(previous session)`. Selecting it calls the `onResumePreviousSession` callback, which typically resumes the prior session via `claude --resume`.

Evidence: Previous session entry in history picker (search for `"(previous session)"`)


### Long Context Survey

What changed: Added a new `longContext` survey type to the in-session survey system. The survey fires when Claude Code detects conditions associated with a large or stale context window, and the question text is now customizable per-trigger rather than hardcoded.

Evidence: Long context survey type (search for `"long_context"` alongside `"surveyType"`)


### Stream Stall Detection and Recovery

What changed: New error messages and handling for two distinct streaming failure modes:

- `"Response stalled mid-stream. The response above may be incomplete."` — shown when the stream goes idle after some output has been produced.
- `"Response stalled while thinking, before producing a response. Try again."` — shown when the stream stalls during the thinking phase before any output.
- `"Stream idle timeout after thinking-only yield — retrying streaming"` — internal retry logic for the thinking-stall case.

These replace previous silent failures or generic timeout messages with specific, actionable descriptions.

Evidence: Stream stall messages (search for `"Response stalled mid-stream"` and `"Stream idle timeout after thinking-only yield"`)


### Error Tracking Per-Process Cap

What changed: The Datadog error-tracking integration now enforces a per-process limit on the number of error reports sent, preventing runaway error logging from a single long-running session.

Details:
- When the cap is hit, a sentinel error `ErrorTrackingCapReached` is recorded once, and all subsequent reports are dropped.
- Log message: `"dd-error-tracking: per-process report cap reached (<N>); dropping further reports"`.
- Prevents excessive API calls to the intake endpoint under pathological error conditions.

Evidence: Error tracking cap (search for `"dd-error-tracking: per-process report cap reached"`)


### Ghostty Terminal Detection

What changed: Claude Code can now detect when it is running inside the Ghostty terminal emulator, enabling any terminal-specific rendering or feature adjustments. Detection is based on the `TERM_PROGRAM` environment variable starting with `"ghostty"` (case-insensitive).

Evidence: Ghostty detection check (search for `"ghostty"` near `"toLowerCase"`)


### Headless Environment Detection Improvement

What changed: The check for whether to skip browser-open operations (e.g., after auth) now handles more cases correctly:

- Respects `BROWSER=""` (browser explicitly set to empty string) vs `BROWSER=true` (legacy signal meaning "use default").
- Treats `SSH_CONNECTION` presence as a headless signal.
- On Linux, treats absence of both `DISPLAY` and `WAYLAND_DISPLAY` as headless.

This reduces spurious browser-open attempts in remote/SSH environments.

Evidence: Headless check function (search for `"SSH_CONNECTION"` alongside `"WAYLAND_DISPLAY"`)


### Cloud Session History Prefetch

What changed: Background conversation-history prefetching is now active for CCR (cloud session relay) sessions. Claude Code proactively loads recent events for background sessions so that attaching to them feels instant.

Details:
- Prefetch is keyed by CCR session ID, validated against the session ID format before proceeding.
- Results are cached on disk under a `cc-history-prefetch-` key.
- Gracefully degrades: gate failures, HTTP errors, and parse failures are all logged but do not block session attach.

Evidence: History prefetch system (search for `"[historyPrefetch]"`)


### Worktree Lock Check Improvement

What changed: The worktree entry check now parses the git lock reason string rather than calling a generic lock-owner function, so it correctly identifies lock entries written by Claude Code agents specifically. A locked worktree from a different tool no longer prevents entry.

Details:
- Pattern matched: `claude agent <name> (pid <N>[ start <time>])`
- Only if the matching PID is running and confirmed to be a Claude Code process is the `Cannot enter worktree` error raised.

Evidence: Worktree lock parsing (search for `"claude agent .+ \\(pid"`)


## Bug Fixes

- Atomic write error handling improved: if the temp-file close fails after a write error, the original write error is preserved and re-thrown with the close failure attached as context, rather than losing the original error. (search for `"atomic write failed first:"`)

- Config file read no longer reports `"resetting to defaults"` when the file is corrupted — it now auto-repairs from cache or reports backup location accurately. (search for `"Config file corrupted:"`)

- Cloud session registration no longer silently swallows HTTP 503 errors; 503 is now treated as a retryable server error rather than a client error, matching the intended error-handling strategy. (search for `"registerWorker failed"`)

- Memory byte-cap stripping now correctly accounts for byte sizes when deciding which media to remove, and reports removed byte counts to telemetry (`tengu_media_byte_cap_stripped`). Previously only item counts were tracked, which could leave the cap under-enforced for large images.

- `/design-login` credential rejection now includes a more specific message for HTTP 403 responses: `"token may be missing a scope this server needs — run /design-login"`, distinguishing scope issues from full re-auth requirements. (search for `"token may be missing a scope this server needs"`)


## In Development

Features with infrastructure added but not yet enabled. Shipped dark and may become available in future versions.


### Prompt Draft Auto-Save [In Development]

What: Infrastructure for saving the current input box contents as a draft (`.prompt-draft`) has been added, which would allow the prompt to persist if the session exits unexpectedly.

Status: Fully implemented — write and read paths are both present. Not yet confirmed as user-visible in all configurations.

Details:
- Draft is written to `CLAUDE_JOB_DIR/.prompt-draft`, capped at 256 KiB (content is sliced at 262144 bytes before write)
- On session restore, the draft file is read back (up to 1 MiB), then immediately deleted — one-shot recovery, not a persistent store
- If the session is not in auto mode, the draft is restored to the composer input box directly (`V$t`)
- If the session has no prior prompt set, the draft is restored to in-memory context (`Myt`)
- The earlier changelog note that "no write/read paths appear to be wired" is outdated — both paths exist in this version

Evidence: Draft write/read functions (search for `".prompt-draft"` or the 262144 byte cap constant)


## Notes

The file-based memory system (synthesis from separate `.md` memory files with `<synthesis:>` parsing, "Recalled from memory" display, memory pruning "dreams") has been removed from the codebase in this version. The `/memory` command, CLAUDE.md-based memory, and `# shortcut or /memory saves facts and preferences to CLAUDE.md` tip remain in place — memory continues to work via CLAUDE.md files. If you relied on the older per-file memory directory with separate `user/`, `feedback/`, and `project/` typed memory files, those files are no longer read by Claude Code as of this version.

---

Generated with:
- tool: `harness-investigations@66416d2-dirty`
- provider: `claude`
- model: `claude-sonnet-4-6`
- primary diff: `archive\claude-code\changes\changes-v2.1.191.md` (filtered astdiff)
- string diff: `archive\claude-code\changes\string-diff-v2.1.191.txt`
