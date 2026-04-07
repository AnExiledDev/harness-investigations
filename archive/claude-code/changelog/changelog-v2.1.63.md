# Changelog for version 2.1.63


## Summary

This is a substantial release with several major additions: a new `/batch` command for parallelized large-scale codebase changes, fully functional HTTP hooks (previously disabled), MCP elicitation hook support, and the renaming of the `Task` tool to `Agent`. It also ships a new `/simplify` code review command, git sparse-checkout support for marketplace plugins, enhanced shell security checks for Zsh, and makes claude.ai MCP servers enabled by default.


### /batch Command

What: New slash command that researches and plans a large-scale change, then executes it in parallel across 5–30 isolated git worktree agents that each open a PR.

Usage:
```
/batch migrate from react to vue
/batch replace all uses of lodash with native equivalents
/batch add type annotations to all JavaScript files
```

Details:
- Requires a git repository (spawns agents in isolated worktrees)
- Each agent independently implements its portion and opens a PR
- User-invocable only (`disableModelInvocation: true`) — the model cannot invoke this on its own
- Operates in two phases: first plans in plan mode, then spawns parallel workers after approval

Evidence: Slash command registration (search for `name: "batch"`, `"Research and plan a large-scale change"`)


### /simplify Command

What: New slash command that reviews changed code for reuse, quality, and efficiency, then fixes any issues found.

Usage:
```
/simplify
```

Details:
- Runs a 3-agent parallel review process: Code Reuse Review, Quality Review, and Efficiency Review
- Examines all changed files (via `git diff`)
- User-invocable only

Evidence: Slash command registration (search for `name: "simplify"`, `"Review changed code for reuse, quality, and efficiency"`)


### HTTP Hooks (Now Functional)

What: HTTP hooks, previously stubbed with "HTTP hooks are not yet supported," are now fully implemented and operational.

Usage:
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write",
      "hooks": [{
        "type": "http",
        "url": "https://hooks.example.com/on-write",
        "headers": { "Authorization": "Bearer $MY_TOKEN" },
        "allowedEnvVars": ["MY_TOKEN"]
      }]
    }]
  }
}
```

Details:
- Sends POST requests with hook input as JSON body
- Supports environment variable interpolation in headers via `$VAR_NAME` or `${VAR_NAME}` syntax
- SSRF protection: private/link-local addresses are blocked; loopback (127.0.0.1, ::1) is allowed for local development
- New managed setting `allowedHttpHookUrls` for organization-level URL allowlisting with wildcard support (e.g., `"https://hooks.example.com/*"`)
- New managed setting `httpHookAllowedEnvVars` restricts which environment variables hooks can interpolate, intersecting with per-hook `allowedEnvVars`
- Responses must be valid JSON

Evidence: HTTP hook execution code (search for `"Hooks: HTTP hook POST to"`, `"ERR_HTTP_HOOK_BLOCKED_ADDRESS"`, `"allowedHttpHookUrls"`)


### MCP Elicitation Hooks

What: Two new hook events that let hooks intercept MCP server elicitation requests (when an MCP server asks the user for input).

Details:
- `Elicitation` hook fires when an MCP server requests user input. Hook can accept, decline, cancel, or provide content to auto-respond.
- `ElicitationResult` hook fires after the user responds to an elicitation. Hook can override the response action or content.
- Supports both form-based and URL-based elicitation modes
- If a hook declines, the elicitation is blocked with "Elicitation denied by hook"

Evidence: Hook event definitions (search for `"Elicitation"` and `"ElicitationResult"` near `hook_event_name`)


### Task Tool Renamed to Agent

What: The `Task` tool has been renamed to `Agent` to better reflect its purpose. `Task` is kept as a backward-compatible alias.

Details:
- Tool name changed from `"Task"` to `"Agent"`
- Description changed from `"Launch a new task"` to `"Launch a new agent"`
- `"Task"` remains as an alias — existing CLAUDE.md files and permissions referencing "Task" will continue to work
- Hook event descriptions updated from "Task tool call" to "Agent tool call"

Evidence: Tool definition (search for `var tq = "Agent"`, `aliases:` containing `"Task"`)


### Git Sparse-Checkout for Marketplace Plugins

What: New `--sparse` CLI option and `sparsePaths` config field for marketplace plugin installation, enabling cone-mode sparse-checkout for monorepo plugin sources.

Usage:
```bash
claude plugin marketplace add my-marketplace --sparse .claude-plugin plugins
```

Details:
- Uses git sparse-checkout in cone mode to clone only specified directories
- Useful for monorepos where the marketplace lives in a subdirectory
- Combines `--filter=blob:none` for blobless clones with sparse-checkout for minimal disk usage
- If `sparsePaths` is removed from config but the repo is already sparse, triggers a re-clone for full checkout

Evidence: CLI option definition (search for `"--sparse <paths...>"`, `"sparse-checkout"`, `"sparsePaths"`)


### Copy Full Response Setting

What: New `copyFullResponse` boolean config option that makes `/copy` always copy the full response, skipping the block-picker dialog.

Usage:
- Enable via `/config` → "Always copy full response (skip /copy picker)"
- Or toggle from the `/copy` picker itself: "Skip this picker in the future (revert via /config)"

Details:
- Default: `false` (existing block-picker behavior preserved)
- When enabled, `/copy` immediately copies the entire last response
- Reversible via `/config` at any time

Evidence: Config definition (search for `"copyFullResponse"`, `"Always copy full response"`)


### --permission-mode CLI Flag

What: New top-level CLI flag for controlling permission handling in sessions.

Usage:
```bash
claude --permission-mode acceptEdits
claude remote-control --permission-mode bypassPermissions
```

Details:
- Applies both as a general CLI option and specifically in `claude remote-control`
- Available modes correspond to existing permission modes (e.g., `acceptEdits`, `bypassPermissions`)
- Used when spawning sub-sessions and for remote control configuration

Evidence: CLI argument definition (search for `"--permission-mode"`)


### Marketplace Seed Directory Support

What: New `CLAUDE_CODE_PLUGIN_SEED_DIR` environment variable for pre-populating marketplace plugins in managed/enterprise environments.

Details:
- Reads `known_marketplaces.json` from the seed directory
- Syncs seed marketplaces into the user's configuration with `autoUpdate: false`
- Supports seed-managed plugin caches and external plugin caching
- Seed-managed marketplaces are marked read-only and cannot be overwritten by user operations

Evidence: Seed directory function (search for `"CLAUDE_CODE_PLUGIN_SEED_DIR"`, `"marketplace(s) from seed dir"`)


### claude.ai MCP Servers Enabled by Default

The claude.ai MCP server integration has changed from opt-in to enabled by default (still GrowthBook-gated for rollout). Users who previously had to set `ENABLE_CLAUDEAI_MCP_SERVERS=true` no longer need to. To opt out, set `ENABLE_CLAUDEAI_MCP_SERVERS=false`.

Evidence: Changed message from `"require ENABLE_CLAUDEAI_MCP_SERVERS=true"` (v2.1.62) to `"enabled by default (GrowthBook-gated). To opt out, set ENABLE_CLAUDEAI_MCP_SERVERS=false"` (v2.1.63)


### /model Command Shows Current Model

The `/model` command description is now dynamic, displaying the currently active model: `"Set the AI model for Claude Code (currently Claude Sonnet 4.6)"` instead of the previous static `"Set the AI model for Claude Code"`.

Evidence: Changed from static `description:` to `get description()` getter (search for `"Set the AI model for Claude Code (currently"`)


### Improved Escape Key UX

The Escape key behavior has been refined with clearer feedback:
- Status line now shows `"ctrl+c to interrupt · Esc again to clear"` during response generation
- A "keep holding…" animation appears when holding Escape
- Replaces the previous simpler `"Esc to clear again"` text

Evidence: New UI strings (search for `"ctrl+c to interrupt · Esc again to clear"`, `"keep holding"`)


### Stricter SSH Host Key Checking

Git clone operations for marketplace plugins now use `StrictHostKeyChecking=yes` instead of the previous `StrictHostKeyChecking=accept-new`. This means new host keys are no longer automatically trusted — the user must explicitly add them first. Improved error messages now provide specific remediation steps:
- For changed host keys: shows `ssh-keygen -R <host>` command
- For unknown hosts: shows `ssh -T git@<host>` command
- Detects `REMOTE HOST IDENTIFICATION HAS CHANGED` and `Host key verification failed` scenarios

Evidence: SSH config change (search for `"StrictHostKeyChecking=yes"`, `"SSH host key has changed"`)


### Enhanced Shell Security Checks

New Zsh-specific and general shell security checks for the Bash tool:
- **Zsh process substitution** `=()` — detected and flagged
- **Zsh glob qualifiers** with command execution `(+` — detected and flagged
- **Zsh `try/always` constructs** `} always {` — detected and flagged
- **Dangerous Zsh builtins** (`zmodload`, `zpty`, `ztcp`, `zsocket`, `zf_rm`, etc.) — blocked
- **`fc -e`** command detection — prevents arbitrary command execution via editor
- **Backslash-escaped operators** — detects `\;`, `\|`, `\&`, `\<`, `\>` outside quotes that can hide command structure
- **Comment quote desync** — detects quote characters inside `#` comments that can confuse quote tracking
- **Tilde expansion variants** (`~user`, `~+`, `~-`) — require manual approval
- **Compound `cd` + `git`** commands — flagged to prevent bare repository attacks

Evidence: Security check functions (search for `"Zsh process substitution"`, `"backslash-escaped operators"`, `"comment quote desync"`, `"fc -e"`)


### Config File Write Protection

A new safety mechanism prevents concurrent config writes from wiping authentication data in `~/.claude.json`. Before writing, the system re-reads the file and refuses to proceed if the disk version is missing `oauthAccount` or `hasCompletedOnboarding` data that exists in the in-memory cache. This addresses a race condition reported in GitHub issue #3117.

Evidence: Config lock function (search for `"saveConfigWithLock"`, `"re-read config is missing auth that cache has"`)


### Transcript Sharing Prompts

New session transcript sharing feature that occasionally prompts users: "Can Anthropic look at your session transcript to help us improve Claude Code?" with three options: Yes, No, and "Don't ask again." A frustration-triggered variant also exists. Selecting "Don't ask again" permanently suppresses the prompt via a `transcriptShareDismissed` config flag.

Evidence: Transcript sharing dialog (search for `"Can Anthropic look at your session transcript"`, `"Don't ask again"`)


### WSL Voice Mode Guard

Voice mode now detects WSL (Windows Subsystem for Linux) and provides a clear error message explaining that audio devices are unavailable, suggesting users run Claude Code in native Windows instead.

Evidence: WSL detection guard (search for `"Voice mode is not supported in WSL"`)


### Fast Mode Cooldown State

Fast mode now has a three-state model: `"on"`, `"off"`, and `"cooldown"` (after a rate limit). Network errors show a temporary unavailability message rather than fully disabling fast mode. The `fast_mode_state` field is now included in API response schemas.

Evidence: Fast mode state function (search for `"Fast mode is temporarily unavailable due to a network error"`)


### SubagentStart / SubagentStop Hook Event Descriptions

The `SubagentStart` and `SubagentStop` hook event descriptions have been updated from "Task tool call" to "Agent tool call" to match the Task→Agent rename. The events themselves are unchanged.

Evidence: Hook event descriptions (search for `"subagent (Agent tool call)"`)


### Opus 4.6 Launch Promo Removed

The Opus 4.6 launch promotional banner, extra usage promo text (`"$50 free extra usage"`, `"/extra-usage to enable"`), and associated feed display logic have been cleaned up. The `tengu_copper_lantern` and `tengu_silver_lantern` feature flag checks and related UI components are removed.

Evidence: Removed functions (search for removed strings `"Opus 4.6 is here"`, `"$50 free extra usage"`)


## Bug Fixes

- Fixed race condition where concurrent config writes could wipe authentication data from `~/.claude.json` (search for `"See GH #3117"`)
- Improved OAuth callback handling with better error message when the redirect URL is missing the authorization code (search for `"Invalid callback URL: missing authorization code"`)
- Fixed `"Prompt cancelled by user"` error propagation when prompts are cancelled during hook flows (search for `"Prompt cancelled by user"`)
- Improved orphaned version cleanup with better error handling for `stat` failures (search for `"Failed to stat orphaned marker"`)
- MCP server `.mcp.json` writes now use atomic `datasync` + `rename` pattern with proper file permission preservation, replacing the previous simpler write approach

### Tool Result Summarization [Gradual Rollout]

What: A feature that instructs the model to preserve important information from tool results in its response text, since original tool results may be cleared later (for context window management).

Status: Feature-flagged via `tengu_summarize_tool_results` (default `false`)

Details:
- When enabled, appends a system instruction: "When working with tool results, write down any important information you might need later in your response, as the original tool result may be cleared later."
- Prepares for a future where tool results are more aggressively pruned from context

Evidence: Gated by `tengu_summarize_tool_results` flag (search for `"tengu_summarize_tool_results"`)


### Asciicast Terminal Recording [Internal]

What: Infrastructure for recording terminal sessions in asciicast v2 format (`.cast` files).

Status: Internal infrastructure — no user-facing command to enable or control recording.

Details:
- Monkey-patches `process.stdout.write` to capture all terminal output with timestamps
- Recordings stored under `~/.claude/projects/<project>/` as `.cast` files
- Supports flushing and renaming recordings for session management
- File permissions set to owner read/write only (mode 384)

Evidence: Recording infrastructure (search for `"[asciicast] Recording to"`, `"[asciicast] Renamed recording"`)


### Custom Subagent Definitions [In Development]

What: Schema support for defining custom subagent types that can be invoked via the Agent tool.

Status: Schema definitions exist but no user-facing documentation or invocation path found.

Details:
- New schema field: `"Definition for a custom subagent that can be invoked via the Agent tool"`
- Includes fields for agent type identifier, description, model alias, and tool availability
- Suggests future ability to define custom agent types in configuration

Evidence: Schema descriptions (search for `"Definition for a custom subagent"`, `"Agent type identifier"`)


## Notes

- **Task → Agent migration**: If you have CLAUDE.md files, hooks, or permissions referencing the `Task` tool by name, they will continue to work — `Task` is retained as an alias. However, new documentation and tool output will use `Agent`.
- **HTTP hook security**: Organizations deploying HTTP hooks should review the new `allowedHttpHookUrls` and `httpHookAllowedEnvVars` managed settings to restrict which URLs hooks can call and which environment variables can be interpolated.
- **SSH host key change**: The switch to `StrictHostKeyChecking=yes` means marketplace plugin installations via SSH may fail if the host key isn't already in `known_hosts`. Run `ssh -T git@<host>` once manually to add it, or use HTTPS URLs for public repos.
- **`/todos` removed**: The `/todos` slash command has been removed. The `TodoWrite` tool for in-session task tracking remains available.
