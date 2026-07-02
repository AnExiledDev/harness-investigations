# Changelog for version 2.1.187

## Summary

This release renames the `/toggle-memory` command to `/pause-memory`, introduces a `--bg`/`--background` CLI flag for launching background agent sessions, and adds `sandbox.credentials` support for protecting credential files and environment variables inside the sandbox. MCP tool idle timeout detection is now configurable via a new env var, skill token footprints appear in `/usage`, and the keyboard input parser gains robust UTF-8 multi-byte handling.

## New Features


### `/pause-memory` replaces `/toggle-memory`

What: The command that pauses automemory for a session has been renamed from `/toggle-memory` to `/pause-memory`. The old name is kept as an alias so existing shortcuts and muscle memory still work.

Usage:
```
/pause-memory          # pause automemory for this session
/pause-memory          # run again to resume
```

Details:
- The status indicator in the sidebar now shows "Paused for this session · /pause-memory to resume"
- Error messages shown when memory operations are blocked have been updated to reference the new command name
- `memory-pause` and `toggle-memory` are registered as aliases — the old command name continues to work

Evidence: Command renamed (search for `"Pause automemory for this session"` or `"pause-memory"` in command list); old alias retained (search for `"toggle-memory"`)


### `sandbox.credentials` — Credential protection in sandbox

What: A new `credentials` section in sandbox configuration lets you declare specific files and environment variables that must be protected when Claude runs sandboxed commands.

Usage:
```json
{
  "sandbox": {
    "credentials": {
      "files": [
        { "path": "~/.aws/credentials", "mode": "deny" },
        { "path": ".env", "mode": "deny" }
      ],
      "envVars": [
        { "name": "AWS_SECRET_ACCESS_KEY", "mode": "deny" },
        { "name": "GITHUB_TOKEN", "mode": "deny" }
      ]
    }
  }
}
```

Details:
- `mode: "deny"` on a file entry blocks reads inside the sandbox
- `mode: "deny"` on an envVar entry unsets the variable for sandboxed commands
- Only explicitly declared files and variables are restricted; everything else is unrestricted by default
- Paths support the same resolution as other sandbox paths: absolute, `~`-expanded, or relative to the settings file root
- `mode: "mask"` is not yet supported — the sandbox will drop the credentials block and warn if an unsupported mode is specified
- Works alongside existing `filesystem.denyRead` rules

Evidence: New schema and logic (search for `"sandbox.credentials"` or `"Credential handling configuration"`)


### `--bg` / `--background` — Launch as background agent

What: A new CLI flag that starts the session as a background agent and returns immediately, rather than waiting for the conversation to complete.

Usage:
```bash
claude --bg "implement the feature described in TASK.md"
# or
claude --background "run the test suite and summarize failures"
```

Details:
- The session runs detached; you can track and manage it with `claude agents`
- Useful for fire-and-forget tasks or parallel workstreams

Evidence: New flag definition (search for `"--bg, --background"` or `"Start the session as a background agent"`)


### MCP tool idle timeout detection

What: MCP tools that stop sending progress or responses are now detected and aborted after a configurable timeout. A new env var controls the timeout duration.

Usage:
```bash
# Set timeout in milliseconds (default is built-in; 0 disables timeout)
export CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT=120000   # 2 minutes
export CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT=0        # disable
```

Details:
- When an MCP tool produces no output for the configured duration, Claude aborts the call and reports the timeout
- Error message includes the tool name and duration: "MCP server `X` tool `Y` sent no response or progress for Ns; aborting"
- A new `McpResponseSchemaError` is thrown and surfaced when an MCP server returns a result that fails schema validation, with a description of what was wrong

Evidence: New timeout guard (search for `"CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT"` or `"MCP tool idle timeout"`)


### `preset:default` in `allowed-tools`

What: Skill frontmatter can now use the token `preset:default` in its `allowed-tools` list to include the full default tool set alongside any custom additions.

Usage:
```yaml
---
allowed-tools: preset:default, Bash(make test)
---
```

Details:
- When `preset:default` is present, Claude expands it to the full list of default tools and then appends any additional entries in the list
- This makes it easy to write skills that extend — rather than replace — the default tool set

Evidence: New expansion logic (search for `"preset:default"`)


### GitHub App post-install — GitHub Actions setup

What: After installing the Claude GitHub App via `/install-github-app`, a new step offers to set up GitHub Actions workflows so Claude automatically responds to `@claude` mentions in issues and PRs.

Details:
- A selection UI appears after successful App installation: "Set up GitHub Actions workflows" or "Skip for now"
- The header reads "Set up GitHub Actions" with the message "The Claude GitHub App is now installed. You can optionally set up GitHub Actions workflows…"
- Skipping shows "Run /install-github-app again anytime to set up GitHub Actions workflows"
- If workflows are set up, the previous success message "GitHub Actions setup complete!" is displayed

Evidence: New post-install flow (search for `"Set up GitHub Actions workflows"` or `"GitHub App installed!"`)


### Subagent nesting depth limit — explicit error

What: When a subagent tries to spawn another agent beyond the nesting depth cap, it now receives a clear error message explaining what happened and instructing it to complete the task directly.

Details:
- Error: "Subagent nesting limit reached (depth N of M). Complete this task directly using your tools instead of spawning another agent."
- Previously this situation could fail silently or produce a confusing error

Evidence: New depth-cap error (search for `"Subagent nesting limit reached"`)


## Improvements


### Skill token footprint in `/usage`

Plugin pages in `/usage` now show how much of the system prompt context budget each plugin's skills consume, broken down per skill.

Details:
- Shown under "Skill-listing footprint" — the cached input cost after the first turn, before agents and MCP tools are counted
- Lists each skill with its approximate token cost per turn, sorted by size
- Footer note: "For per-skill invocation counts and cost attribution, see /usage"
- When no model-invocable skills are loaded for a plugin, shows "No model-invocable skills loaded for this plugin"

Evidence: New skill footprint UI (search for `"Skill-listing footprint"` or `"What this plugin's skill descriptions add to the system prompt"`)


### Artifact design skill — comprehensive design guidance

The `artifact-design` skill has been expanded with detailed design principles covering typography, layout, color, copy writing, UI design, and an editorial workflow for higher-stakes creative pages.

Details:
- Guidance covers: honoring existing design systems, typeface pairing (with `@font-face` data URIs since CDNs are blocked), layout with flex/grid, CSS cascade specificity, writing copy, structural vs. decorative elements, and avoiding AI-generated design clichés
- Adds an explicit process: sketch a compact token system (color, type, layout) before writing code
- Adds an "editorial" mode for landing pages, games, and apps — with instructions to make opinionated calls and take one real aesthetic risk
- Description updated from "Design guidance for Artifact pages" to "Design guidance and fundamentals for Artifacts"

Evidence: Skill content replaced (search for `"Approach this as the design lead at a small studio"`)


### DesignSync — improved messages in non-interactive sessions

`/design-sync` error messages now give context-appropriate guidance depending on whether the session is interactive or headless.

Details:
- In non-interactive sessions (e.g. claude.ai/code), authorization errors now explain that `/design-login` is not available and suggest alternatives such as "Send to Claude Code Web" or providing project files directly
- Design token refresh failures in headless environments now direct users to re-authorize from an interactive terminal
- The "wrong_provider" and "essential_traffic_only" error cases are unchanged

Evidence: Context-aware error messages (search for `"DesignSync needs design-system authorization, but /design-login requires an interactive terminal"`)


### Usage credits messages — cleaner wording

Several Fable 5 usage-credits status messages have been rewritten for clarity.

Details:
- "Fable 5 uses usage credits and you're out · run /usage-credits..." → "You're out of usage credits. Run /usage-credits to keep using Fable 5 or /model to switch models."
- Monthly limit messages now say "You've hit your monthly spend limit" (admin-path: ask admin; user-path: run /usage-credits)
- "Now using usage credits for `<model>`" notification appears when the model switches to credit-based billing
- Fable 5 onboarding banners (the "Fable 5 is here!" and "Fable 5 now runs on usage credits" intro screens) have been removed now that the launch period is over

Evidence: Updated messaging (search for `"You're out of usage credits"` or `"You've hit your monthly spend limit"`)


### Plan mode — clearer model restriction messages

When a plan-mode upgrade model is blocked by org settings, the error message now mentions both `availableModels allowlist` and `model_access entitlement` instead of just the allowlist.

Evidence: Updated messages (search for `"availableModels allowlist or model_access entitlement"`)


### Advisor — warning when model is not in capability table

When Claude Code's advisor feature is activated with a custom model that isn't in its capability table, it now emits a visible warning with guidance.

Details:
- Warning: "Warning: Advisor disabled — base model `<name>` isn't in the advisor capability table. Switch to a public model alias (opus, sonnet, fable) or set CLAUDE_CODE_ENABLE_EXPERIMENTAL_ADVISOR_TOOL=1."
- This replaces a silent failure

Evidence: New warning (search for `"Warning: Advisor disabled"`)


### Subagent prompt — file-writing note clarified

The instruction telling subagents not to write report/summary/analysis files has been clarified to note that writing files as input to another tool is acceptable.

Details:
- Old: "Do NOT write report/summary/findings/analysis .md files. Return findings directly..."
- New: "...Return findings directly... (Files written as input to another tool are fine; this note is about report files.)"

Evidence: Prompt text change (search for `"Files written as input to another tool are fine"`)


### Artifact tool — improved file-not-found error

When the `Artifact` tool is called with a path that does not exist, the error message now mentions the shell as an alternative to the Write tool.

Details:
- Old: "Use the Write tool to create the file first, then call Artifact with the same absolute path."
- New: "Create the file first (Write tool, or via shell if Write is unavailable), then retry with the same path."

Evidence: Updated error message (search for `"or via shell if Write is unavailable"`)


### Safety messages — updated wording

Several model safeguard/flagged-message strings have been updated for consistency.

Details:
- "This model has safety measures that flagged something in this session." → "This model's safeguards flagged this message."
- Cybersecurity/biology topic messages now use the `'s safeguards flagged` phrasing consistently
- The broader note now reads "The safeguards are intentionally broad right now and may flag safe and routine coding, cybersecurity, or biology work. These measures let us bring you Mythos-level capabilities sooner..."

Evidence: String changes (search for `"safeguards flagged this message"`)


### WorktreeRemove hook — fallback now logged

When no `WorktreeRemove` hook is configured and Claude falls back to running `git worktree remove` directly, this is now logged explicitly.

Details:
- Log message: "No WorktreeRemove hook configured; falling back to git worktree remove for: `<path>`"

Evidence: New fallback log (search for `"No WorktreeRemove hook configured"`)


### Git config lockfiles excluded from file watching

`.git/config.lock` and `.git/config.worktree.lock` are now included in the list of paths excluded from the file watcher.

Details:
- Prevents spurious change events triggered by git operations that momentarily hold a config lock

Evidence: New exclusion entries (search for `".git/config.lock"`)


### OAuth error details now tracked

When OAuth token operations fail, the specific error type is now captured and classified (expired token, invalid token, no organization, no account associated).

Evidence: New OAuth error classification (search for `"Refresh token expired"` or `"No organization associated with this token"`)


## Bug Fixes

- **UTF-8 multi-byte characters in keyboard input**: The key parser now correctly reassembles multi-byte UTF-8 sequences delivered as individual escape sequences. Previously, non-ASCII characters entered via the terminal (particularly on some Linux/remote terminals) could be dropped or misinterpreted. A `pendingByteEvents` buffer accumulates bytes and flushes the complete character once all bytes have arrived. (search for `"pendingByteEvents"`)

- **AbortSignal memory leak in event listeners**: Abort-signal subscriptions created during agent turns now use a `FinalizationRegistry` to automatically remove the listener when the child object is garbage-collected. Previously, long-running sessions with many tool calls could accumulate a growing number of stale abort listeners. (search for `"FinalizationRegistry"`)

- **FileIndex: skip path normalization when unchanged**: Path normalization is now skipped when the raw git paths have not changed, avoiding unnecessary work and a potential re-index cycle. (search for `"[FileIndex] skipped path normalization"`)

- **FileIndex: discard mid-refresh results when cache was reset**: If the file index cache is reset while a refresh is in progress, the results of that refresh are now discarded rather than written over the fresh cache. (search for `"[FileIndex] discarding refresh results"`)

- **Windows: UNC watch paths dropped gracefully**: When the file watcher encounters remote UNC paths on Windows, they are now silently dropped with a debug log rather than crashing the watcher. (search for `"FileChanged: dropped remote UNC watch path(s)"`)

- **MCP schema validation error surfaced as named error**: MCP tool results that fail schema validation now throw a `McpResponseSchemaError` with the validation message attached, rather than an untyped error. (search for `"McpResponseSchemaError"` or `"MCP server returned a malformed result"`)


## In Development

Features with infrastructure added but not yet enabled for general availability.


### Startup announcements [In Development]

What: A server-controlled system for showing one-time startup messages to users — for example, announcing a new feature or a policy change.

Status: Feature-flagged (gated by `tengu_startup_announcements`)

Details:
- Announcements are fetched from the server as the value of the `tengu_startup_announcements` feature flag — the flag carries the announcement payload, not just an on/off gate
- Each announcement has `id`, optional `title`, `text`, `priority`, and `maxImpressions` fields
- Claude Code tracks how many times each announcement has been shown (`announcementImpressions` in config) and stops showing it once `maxImpressions` is reached; multiple announcements can be queued and the highest-priority un-maxed one is selected
- Rendered as a named UI component (`startup-announcement`) that appears before the session prompt, not inline during a session
- Slash-command references in the text are syntax-highlighted
- Model requirements can be attached to an announcement, restricting which sessions see it

Evidence: New announcement component (gated on `tengu_startup_announcements` flag, search for `"startup-announcement"`)


### Team memory partition manifest (`.memory-sync`) [In Development]

What: Team memory sync will gain a manifest file (`.memory-sync`) inside each mount directory to detect and handle cross-partition conflicts — preventing one team's memory store from silently being misused by another team that happens to share the same directory path.

Status: Feature-flagged (gated by `tengu_silk_almanac`)

Details:
- Each team's memory is scoped to a unique `partitionId` (the backend's partition identifier, likely an org or team UUID)
- Each mount directory gets a `.memory-sync` manifest (JSON: `{ v: 1, partitionId: "..." }`) written at sync time
- On pull, the manifest's `partitionId` is compared against the expected backend partition; a mismatch invalidates the basis and forces a full re-sync
- If a different partition's manifest is detected during a non-user-scoped mid-session sync, sync is suppressed entirely with a warning: "mount dir holds a different partition's `.memory-sync` — suppressing sync (remove the dir to re-mount)"
- Without this flag enabled, two teams sharing the same directory path could silently read and overwrite each other's memory

Evidence: New manifest functions (gated on `it("tengu_silk_almanac", !1)`, search for `".memory-sync"` or `"partition mismatch"`)


### Per-context bootstrap data cache [In Development]

What: Bootstrap data (client configuration, model options, costs) will be cached on a per-context key (entrypoint + model + org UUID + CC version) rather than a single global cache slot, allowing different sessions or entrypoints to carry their own cached data without overwriting each other.

Status: Active — `tengu_client_data_cache_key` is a telemetry-only gate, not a feature gate. The per-context caching is written and read regardless; the gate only controls whether cache hit/miss/stale/changed stats are reported to telemetry.

Details:
- Cache key is composed of: entrypoint + model + org UUID + CC version — so CLI and IDE extension sessions never clobber each other's cached model/org config
- New `clientDataCacheSlots` config key stores keyed entries; legacy `clientDataCache` (global single slot) is still read as a fallback when no matching slot exists (`legacy_fallback: true` in telemetry)
- Telemetry tracks four outcomes per fetch: `slot_hit`, `slot_changed` (remote data differs from cached), `legacy_fallback`, and `slot_stale` (cache older than the stale threshold)
- If cache hit and data is unchanged and not stale, the bootstrap write is skipped entirely

Evidence: New slot-keyed cache (search for `"clientDataCacheSlots"` or `"tengu_client_data_cache_key"`)

---

Generated with:
- tool: `harness-investigations@66416d2-dirty`
- provider: `claude`
- model: `claude-sonnet-4-6`
- primary diff: `archive\claude-code\changes\changes-v2.1.187.md` (filtered astdiff)
- string diff: `archive\claude-code\changes\string-diff-v2.1.187.txt`
