# Changelog for version 2.1.133

## Summary

Claude Code 2.1.133 adds more control over agent worktrees, improves plugin and managed-policy diagnostics, and exposes reasoning effort more consistently to hooks and Bash. It also includes Windows background-daemon reliability work and a fix for MCP session-expiry handling.

### Worktree Base Ref Setting

What: You can now choose whether new worktrees start from a clean remote default branch or from your current local HEAD.

Usage:
```json
{
  "worktree": {
    "baseRef": "head"
  }
}
```

Details:
- `fresh` remains the default and branches from `origin/<default-branch>`.
- `head` branches from the current local HEAD, so unpushed commits and feature-branch state are present.
- The setting applies to `--worktree`, `EnterWorktree`, and agent isolation.
- The setting is also exposed in the config UI as “Worktree base ref”.

Evidence: Worktree setting schema and UI were added (search for `"Which ref new worktrees branch from"` and `"Worktree base ref"`).


### Default Agents View [Gradual Rollout]

What: Users with the agents interface enabled can make Claude Code open the agents view by default.

Usage:
```json
{
  "defaultToAgentsView": true
}
```

Details:
- A new config UI toggle appears as “Open agents view by default”.
- When enabled, normal interactive startup can enter the agents view without requiring `claude agents`.
- This depends on the existing agents-view gate, so not every user will necessarily see it.

Evidence: Config option and startup behavior were added (search for `"Open agents view by default"` and `"defaultToAgentsView"`).

### Clearer Plugin Override Warnings

Claude Code now warns when a plugin disabled in `~/.claude/settings.json` is re-enabled by a higher-precedence source such as project, local, flag, or policy settings. The warning explains exactly where to disable it instead.

Usage:
```json
{
  "enabledPlugins": {
    "formatter@anthropic-tools": false
  }
}
```

Details:
- Project-enabled plugins should be disabled in `.claude/settings.local.json`.
- Plugins enabled through `--settings` must be removed from the `--settings` value.
- Plugins enabled by managed policy cannot be overridden locally.

Evidence: New warning UI and remediation text (search for `"Plugin settings overridden"` and `"These plugins are disabled in ~/.claude/settings.json, but a higher-precedence source re-enables them:"`).


### Better Documentation for Plugin Setting Precedence

The `enabledPlugins` setting description now documents the precedence order directly: user < project < local < flag < policy.

Details:
- This makes it clearer why disabling a plugin in user settings may not work when the project re-enables it.
- The schema description now points users to `.claude/settings.local.json` for project-specific opt-outs.

Evidence: Updated setting description (search for `"Settings precedence is user < project < local < flag < policy"`).


### Reasoning Effort Exposed to Hooks and Bash

Hook authors get structured reasoning-effort information for tool-use lifecycle hooks, and Bash receives the active value as `CLAUDE_EFFORT` when the model supports effort.

Usage:
```bash
echo "$CLAUDE_EFFORT"
```

Details:
- Hook input now includes an optional `effort.level` field.
- The value reflects the active effort level after any model-specific downgrade.
- The field is present for tool-use contexts such as `PreToolUse`, `PostToolUse`, `Stop`, and `SubagentStop`, but absent for session-lifecycle hooks and models without effort support.

Evidence: Hook schema and Bash environment wiring (search for `"Reasoning effort applied to the current turn"` and `"Active effort level for the current turn"`).


### Managed Settings Can Merge Parent Policy

Administrators can now control whether SDK-provided parent managed settings are dropped or merged under an admin tier.

Usage:
```json
{
  "parentSettingsBehavior": "merge"
}
```

Details:
- `first-wins` keeps the previous admin-first behavior.
- `merge` layers a restrictive-only slice from the parent settings under the admin winner.
- This matters for managed-policy deployments where an SDK parent wants to add restrictions without overriding the administrator’s policy.

Evidence: New managed-settings schema and merge path (search for `"parentSettingsBehavior"` and `"Controls whether the SDK parent tier"`).


### Admin-Controlled Sandbox Binary Paths

Managed settings can now provide absolute paths for Linux/WSL sandbox helper binaries.

Usage:
```json
{
  "sandbox": {
    "bwrapPath": "/usr/bin/bwrap",
    "socatPath": "/usr/bin/socat"
  }
}
```

Details:
- `sandbox.bwrapPath` overrides bubblewrap auto-detection.
- `sandbox.socatPath` controls the sandbox network proxy helper.
- These paths are only honored from admin-controlled managed settings.
- Error messages now distinguish “bubblewrap missing” from “configured bwrap path is not executable”.

Evidence: Managed sandbox path descriptions and validation errors (search for `"Linux/WSL only: Absolute path to the bwrap"` and `"sandbox.bwrapPath is set to"`).


### Windows Background Daemon Respawn Is More Durable

Claude Code now tries to spawn upgraded background daemons on Windows through WMI/CIM, falling back to direct spawn if WMI fails.

Details:
- The WMI path uses `Win32_Process.Create` with a hidden process startup configuration.
- If WMI fails or times out, Claude Code logs a fallback warning and starts directly.
- The fallback note says the daemon may not survive SSH or terminal close.

Evidence: Windows daemon spawn path (search for `"daemon: WMI spawn failed"` and `"Win32_Process.Create rc="`).


### Skill Tool Guidance Updated

The allowed-tools schema now explicitly deprecates passing `Skill` through the generic `tools` field and points authors to the dedicated `skills` field.

Details:
- This helps agent and skill authors avoid older tool-allowlist patterns.
- Existing allowed-tools inheritance behavior is unchanged.

Evidence: Updated schema description (search for `"Note: passing 'Skill' here is deprecated"`).

## Bug Fixes

- MCP session-expiry errors are now recognized when a 404 response includes `"mcp_session_terminated"`, allowing Claude Code to mark the server as needing auth instead of treating it as a generic failure. Evidence: MCP error classifier (search for `"mcp_session_terminated"`).

- Compact-cache fallback now preserves abort behavior instead of continuing through fallback paths after cancellation. Evidence: abort checks added around compact cache sharing (search for `"Compact cache sharing: no text in response, falling back"`).

- Windows command/path handling gained additional normalization and quoting safeguards for daemon spawning, including rejection of unsupported Unicode single-quote variants in generated PowerShell command lines. Evidence: PowerShell quoting guard (search for `"unsupported Unicode single-quote in command line"`).
