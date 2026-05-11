# Changelog for version 2.1.139

## Summary

Claude Code 2.1.139 adds several user-visible workflow and administration improvements: a new plugin details command, a built-in Proactive output style, interactive terminal scroll-speed tuning, and new Cloud gateway authentication plumbing for enterprise deployments. It also tightens `/goal`, hook/plugin execution, Remote Control diagnostics, MCP eligibility messages, shell safety checks, and several plugin and transport edge cases.

### Plugin Details Command

What: `claude plugin details <name>` shows what a plugin contributes and estimates how much context its components add.

Usage:
```bash
claude plugin details my-plugin
claude plugin details my-plugin --json
```

Details:
- Lists component inventory for skills, commands, agents, hooks, and MCP servers.
- Shows estimated always-on token cost added to each session.
- Breaks down per-component always-on and on-invoke costs when available.
- Supports JSON output for scripting.

Evidence: Plugin details subcommand and report output (search for `"Show a plugin's component inventory and projected token cost"`, `"Component inventory"`, `"Projected token cost"`)


### Proactive Output Style

What: A new built-in `Proactive` output style makes Claude act more autonomously: execute immediately, minimize interruptions, and prefer action over planning.

Usage:
```bash
claude
# Open /config and set Output style to Proactive
```

Details:
- Adds `Proactive` alongside existing built-in output styles.
- Uses a dedicated style prompt, not just a generic reminder.
- Adds a shorter per-turn reminder: `Execute autonomously, minimize interruptions, prefer action over planning.`
- This is a fully built-in style; no plugin is required.

Evidence: Built-in output style definition (search for `"Proactive Style Active"`, `"Claude executes immediately, minimizes interruptions, and prefers action over planning"`)


### Terminal Scroll Speed Setup

What: `/terminal-setup` now includes an interactive scroll-speed control for tuning mouse wheel behavior in the terminal.

Usage:
```bash
claude
# Run /terminal-setup, then use left/right to adjust scroll speed
```

Details:
- Shows current terminal/editor scroll behavior.
- Lets users adjust with left/right arrows, reset with `r`, save with Enter, or cancel with Esc.
- Saves the selected value to user settings as `CLAUDE_CODE_SCROLL_SPEED`.
- Detects terminal context such as VS Code, Cursor, Windows Terminal, xterm.js, and high-rate wheel events.

Evidence: Interactive scroll-speed UI (search for `"Scroll speed"`, `"Scroll to feel it · ←/→ adjust · r reset to auto · Enter save · Esc cancel"`, `"CLAUDE_CODE_SCROLL_SPEED"`)


### Cloud Gateway Authentication [Gradual Rollout]

What: Claude Code now has first-class plumbing for an enterprise Cloud gateway backend.

Usage:
```bash
claude auth login
# Select Cloud gateway when that option is available for your environment
```

Details:
- Adds Cloud gateway as a distinct API provider.
- Stores gateway URL/status in account and diagnostics views.
- Refreshes gateway JWTs through the gateway OAuth token endpoint.
- Pins and verifies TLS fingerprints on restore, warning users to re-login if trust changes.
- Loads managed settings through the gateway and surfaces actionable re-authentication messages when they fail.

Evidence: Cloud gateway provider and login flow (search for `"Cloud gateway"`, `"Gateway URL"`, `"Connected to Cloud gateway."`, `"[gateway-refresh] refreshed gateway JWT"`)

### `/goal` Status and Completion Behavior

`/goal` is not new in this release, but its UX is clearer. Active goals now show a richer panel with elapsed time, turns, token count, last check, and `/goal clear to stop early`. Completed goals show `Goal achieved` and the stop-hook instruction now says the goal auto-clears after success, instead of telling the user to clear it manually.

Evidence: Goal status panel and updated hook instruction (search for `"Goal active"`, `"/goal clear to stop early"`, `"It auto-clears once the condition is met"`)


### Hook and Plugin Commands Gain Safer Exec Form

Hook command definitions can now use an explicit `args` array for exec-style invocation. Claude Code validates the common mistake of putting both whitespace in `command` and also supplying `args`, and explains how to split executable and arguments correctly.

Usage:
```json
{
  "command": "node",
  "args": ["script.js"]
}
```

Details:
- `command` is resolved as an executable when `args` is present.
- Arguments avoid shell parsing for quotes, `$`, and backticks.
- Plugin and hook substitutions now include `${CLAUDE_PROJECT_DIR}` in more places, including monitor hooks and plugin command paths.

Evidence: Exec-form hook schema and validation (search for `"Argument list for exec form"`, `"Exec form treats \"command\" as a single executable name"`, `"${CLAUDE_PROJECT_DIR}"`)


### Remote Control Diagnostics Are More Specific

Remote Control now tells users why it is unavailable in more cases, especially when the session is using API-key auth or a non-first-party backend.

Details:
- Distinguishes `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `apiKeyHelper`, and `ANTHROPIC_UNIX_SOCKET` cases.
- Explains that Remote Control requires claude.ai subscription auth.
- Adds a specific message when the active backend is not `api.anthropic.com`.

Evidence: Remote Control auth diagnostics (search for `"Remote Control requires claude.ai subscription auth"`, `"ANTHROPIC_API_KEY is set"`, `"Remote Control is only available when using Claude via api.anthropic.com"`)


### Claude.ai MCP Connector Diagnostics

Claude.ai MCP connector setup now reports clearer disabled states for third-party providers, API-key precedence, and missing `user:mcp_servers` scope.

Details:
- Clarifies that claude.ai org connectors are disabled when the inference token lacks MCP scope.
- Explicitly says locally configured MCP servers in `managed-mcp.json`, `.claude.json`, and `.mcp.json` are not affected.
- Adds clearer provider-specific messages for third-party backends.

Evidence: MCP eligibility messages (search for `"[claudeai-mcp] Disabled on third-party provider"`, `"inference token lacks user:mcp_servers scope"`)


### Agent View Disable Setting Renamed

The managed setting/environment-variable wording changed from “background-agents fleet” to “agent view.”

Details:
- New setting field: `disableAgentView`.
- New environment variable: `CLAUDE_CODE_DISABLE_AGENT_VIEW`.
- Old wording referenced `CLAUDE_CODE_DISABLE_AGENTS_FLEET`; administrators should update managed settings and environment overrides.

Evidence: Setting rename (search for `"Disable agent view"`, `"CLAUDE_CODE_DISABLE_AGENT_VIEW"`, and compare old `"CLAUDE_CODE_DISABLE_AGENTS_FLEET"`)


### Configurable Max Turns Environment Variable

Claude Code now reads `CLAUDE_CODE_MAX_TURNS` as a default max-turn override when max turns are not otherwise supplied.

Usage:
```bash
CLAUDE_CODE_MAX_TURNS=50 claude
```

Details:
- The value must be a positive integer.
- Invalid values fail early with a clear error.

Evidence: Max-turn environment parsing (search for `"CLAUDE_CODE_MAX_TURNS must be a positive integer"`)


### Supervised Mode Exits on Fatal Runtime Errors

When `CLAUDE_CODE_SUPERVISED` is set, uncaught exceptions and unhandled rejections now cause the process to exit after logging. This is useful for service managers or wrapper processes that should restart a crashed CLI instead of letting it limp along.

Usage:
```bash
CLAUDE_CODE_SUPERVISED=1 claude
```

Evidence: Supervised fatal-error handling (search for `"Uncaught exception under CLAUDE_CODE_SUPERVISED — exiting"`, `"Unhandled rejection under CLAUDE_CODE_SUPERVISED — exiting"`)

## Bug Fixes

- Bash safety analysis now detects ambiguous heredoc terminators, including `<<-` tab-prefixed delimiters and heredoc body lines that can be mistaken for terminators with shell metacharacters. Evidence: heredoc safety checks (search for `"ambiguous heredoc terminator"`, `"Heredoc uses <<- with a tab-prefixed delimiter"`)

- Plugin ZIP loading now handles archives with a wrapper directory instead of failing or choosing the wrong root. Evidence: inline plugin ZIP handling (search for `"Inline plugin zip had wrapper directory; using"`)

- Missing plugin errors are more actionable and now suggest `claude plugin list` or `--plugin-dir <path>`. Evidence: plugin lookup error (search for `"not found. Run `claude plugin list` to see installed plugins"`)

- Marketplace plugin cache misses now explain that the plugin may have been removed and tell users to disable it via `/plugin`. Evidence: plugin source cache-miss message (search for `"the plugin may have been removed. Disable it via /plugin to clear this warning"`)

- Settings-file watching now tracks symlink targets so atomic-save edits to the target file are detected. Evidence: symlink target watcher (search for `"also watching"`, `"so atomic-save edits to the target are detected"`)

- Plugin directory copying now handles cyclic symlinks, non-regular symlink targets, and symlinks escaping the containment root more carefully. Evidence: symlink materialization safeguards (search for `"copyDir: skipping cyclic symlink target"`, `"copyDir: skipping symlink escaping containment root"`)

- HTTP/SSE transport now aborts streams that exceed the body limit without an SSE event boundary, preventing unbounded memory growth when a server returns non-protocol data. Evidence: SSE body overflow guard (search for `"without an SSE event boundary"`, `"HttpBodyOverflowError"`)

- Proxy and TLS connection setup now has explicit timeout/failure errors for gateway-style connections. Evidence: connection error strings (search for `"TLS connection timed out"`, `"proxy CONNECT failed"`, `"proxy CONNECT timed out"`)

## Notes

The main migration item is for administrators or wrapper authors: update `disableAgentView` / `CLAUDE_CODE_DISABLE_AGENT_VIEW` if you previously depended on the older background-agents fleet setting name. For normal interactive users, this release is backward-compatible.


Generated with:
- tool: `harness-investigations@1ed3002-dirty`
- provider: `codex`
- model: `gpt-5.5`
- reasoning effort: `medium`
- primary diff: `archive/claude-code/changes/changes-v2.1.139.md` (filtered astdiff)
- string diff: `archive/claude-code/changes/string-diff-v2.1.139.txt`
