# Changelog for version 2.1.136

## Summary
Claude Code 2.1.136 adds admin-controlled managed settings helpers, a new `autoMode.hard_deny` rule category, and gradual-rollout routine notifications. It also improves MCP configuration compatibility, `--worktree` failure messages, WSL image paste support, and PowerShell safety checks.

### Enterprise Managed Settings Helper
What: Organizations can now configure an admin-controlled helper executable that computes managed settings at startup.

Usage:
```json
{
  "policyHelper": {
    "path": "/usr/local/bin/claude-policy-helper",
    "timeoutMs": 5000,
    "refreshIntervalMs": 60000
  }
}
```

Details:
- The helper is honored only from admin-controlled policy sources.
- It can return `managedSettings`, `claudeMd`, and `appendSystemPrompt`.
- Claude Code validates the helper path, rejects non-absolute paths, and can refresh the helper output periodically.
- If refresh fails, Claude Code retains the current policy instead of dropping managed settings.

Evidence: Managed settings helper schema and runtime execution (search for `"policyHelper"` and `"Executable that computes managed settings at startup. Honored only from admin-controlled policy sources."`)


### Auto Mode Hard-Deny Rules
What: Auto mode custom rules now distinguish soft blocks from hard security blocks.

Usage:
```json
{
  "autoMode": {
    "allow": ["$defaults"],
    "soft_deny": ["$defaults"],
    "hard_deny": [
      "$defaults",
      "Never send secrets to external endpoints"
    ],
    "environment": ["$defaults"]
  }
}
```

Details:
- `soft_deny` is now described as destructive or irreversible behavior that clear user intent can authorize.
- `hard_deny` is new and covers security-boundary actions that user intent does not clear.
- `claude auto-mode defaults`, `claude auto-mode config`, and `claude auto-mode critique` now understand all four categories: `allow`, `soft_deny`, `hard_deny`, and `environment`.

Evidence: Auto mode schema and CLI output now include `hard_deny` (search for `"Rules for the auto mode classifier HARD BLOCK section"` and `"autoMode.{allow, soft_deny, hard_deny, environment}"`)


### Routine Fired Notifications [Gradual Rollout]
What: Claude Code can now notify you when remote routines have run.

Usage:
```bash
claude
```

Details:
- When enabled, Claude Code checks Claude routine trigger state and shows a notification such as a routine name or “routines ran”.
- Notifications link back to `/code/routines`.
- This is gated by remote-session support and a feature flag, so not all users will see it immediately.
- Organizations can disable routine dispatch through policy.

Evidence: Routine trigger notification path (search for `"routine-fired"`, `"/code/routines"`, and `"Routines are disabled by your organization's policy."`)

### MCP Server Config Compatibility
Claude Code now accepts `streamable-http` as an MCP transport alias for HTTP and gives clearer errors for invalid MCP server types.

Usage:
```json
{
  "mcpServers": {
    "example": {
      "type": "streamable-http",
      "url": "https://example.com/mcp"
    }
  }
}
```

Evidence: MCP transport normalization and validation (search for `"streamable-http"` and `"Valid types are: stdio, sse, http (or streamable-http), ws, sdk"`)


### Safer MCP Client Secret Storage
When adding HTTP/SSE MCP servers with `--client-secret`, Claude Code now preserves the server config even if secure storage is unavailable, then tells you how to retry secret storage.

Usage:
```bash
claude mcp add --transport http my-server https://example.com/mcp --client-id abc --client-secret
```

Evidence: MCP add fallback warning (search for `"Server added, but the client secret could not be stored"`)


### Clearer Worktree Setup Failures
`--worktree` now gives more actionable errors when workspace trust has not been accepted, when a worktree branch is already checked out elsewhere, or when a stale worktree directory blocks reuse.

Usage:
```bash
claude --worktree feature-name
```

Evidence: Worktree diagnostics (search for `"Workspace trust not yet accepted. Run \`claude\` once in this directory and accept the trust dialog, then retry with --worktree."` and `"is already checked out in a worktree at"`)


### WSL Clipboard Image Paste
Claude Code can now fall back to Windows PowerShell from WSL when checking or saving image clipboard contents.

Evidence: WSL clipboard fallback to Windows PowerShell (search for `"powershell.exe)"` and `"Get-Clipboard -Format Image"`)


### Broader `/effort max` Documentation
The `/effort` help text now documents `max` as available for Opus 4.6/4.7 and Sonnet 4.6, instead of only Opus 4.6/4.7.

Usage:
```bash
/effort max
```

Evidence: Effort help text (search for `"Opus 4.6/4.7, Sonnet 4.6"`)

## Bug Fixes

- Fixed `--worktree` starting before workspace trust is accepted, replacing a later failure with a direct trust message. Evidence: trust gate added before worktree creation (search for `"Workspace trust not yet accepted"`)

- Improved PowerShell 5.1 command safety detection for cwd-first command shadowing. Evidence: new warning for commands that create a file which shadows a later command (search for `"Windows PowerShell 5.1 cwd-first resolution"`)

- Improved PowerShell validation around runtime-resolved Unicode codepoint escapes. Evidence: new classifier message (search for `"PowerShell \`u{HEX} codepoint escape is runtime-resolved and cannot be statically validated."`)

- Fixed bare Git repository detection to recognize `.git` files that contain `gitdir:` and avoid misclassifying linked worktrees or nested repositories. Evidence: updated Git structure detection (search for `"gitdir:"`)


Generated with:
- tool: `harness-investigations@cc606f8-dirty`
- provider: `codex`
- model: `gpt-5.5`
- reasoning effort: `medium`
- primary diff: `archive/claude-code/changes/changes-v2.1.136.md` (filtered astdiff)
- string diff: `archive/claude-code/changes/string-diff-v2.1.136.txt`
