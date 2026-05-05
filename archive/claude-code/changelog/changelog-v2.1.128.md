# Changelog for version 2.1.128

## Summary
Claude Code 2.1.128 adds a feature-flagged way to turn team onboarding guides into share links, adds a managed setting for organizations to disable Remote Control, and improves several background-session recovery paths. It also tightens provider-specific messaging for Channels/Fast Mode, expands session-only plugin handling, and makes large/media tool results fail more clearly instead of surfacing confusing output.

### Team Onboarding Guide Sharing [Gradual Rollout]
What: The built-in team onboarding flow can now upload `ONBOARDING.md` and return a Claude Code share link for teammates.

Usage:
```bash
/team-onboarding
```

Details:
- The existing onboarding guide flow now has a `ShareOnboardingGuide` tool that uploads `ONBOARDING.md`.
- The tool supports three modes: `check`, `update`, and `create`.
- If a guide already exists for the org, Claude asks whether to update the existing link or create a new one.
- The guide must be in the current directory and under 64 KB.
- This is gated by `tengu_flint_harbor_share`, so not every user will see it yet.

Evidence: Team onboarding share tool and rollout gate (search for `"ShareOnboardingGuide"` and `"tengu_flint_harbor_share"`)


### Managed Remote Control Disable Setting
What: Organizations can now disable Remote Control centrally through managed settings.

Usage:
```json
{
  "disableRemoteControl": true
}
```

Details:
- The new setting disables `claude.ai/code`, `claude remote-control`, `--remote-control`, `--rc`, auto-start, and the in-session Remote Control toggle.
- When policy blocks the feature, users now see a specific managed-setting error instead of a generic Remote Control denial.

Evidence: Managed setting schema and policy error (search for `"disableRemoteControl"` and `"Remote Control is disabled by your organization's policy (managed setting `disableRemoteControl`)."`)

### Background Session Recovery and Cleanup
Claude Code is better at recovering background sessions that stall, crash, or lose their supervisor connection.

Usage:
```bash
claude attach <id>
claude respawn <id>
claude respawn --all
claude rm <id>
```

Details:
- `attach` now attempts to wake sessions that report `ENOJOB`, reconnects through a transient service when possible, and gives clearer messages when a session moved, exited, or cannot be reattached.
- Startup stalls can now trigger an automatic worker restart before giving up.
- `respawn` and `rm` now have explicit `--help` output.
- `rm` keeps changed worktrees instead of blindly removing them when uncommitted changes are present.

Evidence: Background recovery messages (search for `"Session not responding — restarting it…"`, `"Usage: claude respawn <id>|--all"`, and `"Worktree has uncommitted changes — kept at"`)


### Session-Only Plugin Zip Loading
`--plugin-dir` now explicitly supports `.zip` files and reports when an inline plugin zip is extracted.

Usage:
```bash
claude --plugin-dir ./my-plugin.zip
```

Details:
- Help text now documents repeatable directory or zip loading.
- Zip extraction emits debug output, making plugin load failures easier to diagnose.
- Existing managed-setting checks still apply to session-only plugins.

Evidence: Plugin flag help and zip extraction path (search for `"Load a plugin from a directory or .zip"` and `"Extracted inline plugin zip to"`)


### MCP Tool Search Handles Late-Connecting Servers Better [Gradual Rollout]
Tool search can now refresh MCP clients and retry selection/search when matching tools may still be arriving from connecting servers.

Details:
- When enabled, direct `select:<tool_name>` can retry after an MCP refresh.
- Keyword searches can also refresh before declaring that no tools match.
- Claude receives clearer guidance that connecting MCP servers may expose tools shortly.
- This behavior is gated by `tengu_ashen_kelp`.

Evidence: Deferred tool refresh behavior (search for `"ToolSearchTool: partial select after MCP refresh"` and `"tengu_ashen_kelp"`)


### Clearer Provider Restrictions for Channels and Fast Mode
Provider-specific features now explain why they are unavailable instead of showing generic auth or availability errors.

Details:
- Channels now say they are unavailable on Bedrock, Vertex, or Foundry.
- Fast Mode now says it is only available when using the Anthropic API directly.
- Bedrock setup text consistently says “Amazon Bedrock.”

Evidence: Provider-specific messages (search for `"Channels are not available on Bedrock, Vertex, or Foundry"` and `"Fast mode is only available when using the Anthropic API directly"`)


### Effort Selection Defaults Back to Auto
Clearing effort now reports and applies `auto` instead of saying it set effort to `max`.

Usage:
```bash
/effort auto
```

Details:
- The cache-warning dialog now uses “Change effort level?” when only effort changes.
- Remote sessions get clearer messaging when an effort setting cannot reach the remote process.

Evidence: Effort reset and cache warning text (search for `"Effort level set to auto"` and `"Change effort level?"`)


### Better Large Input and Media Result Messages
Claude Code now explains size and media limits more directly.

Details:
- Piped stdin that exceeds the size cap tells users to pass large content as a file path.
- Oversized remote requests tell users to shorten the prompt or send it in parts.
- Media rejected by the API is replaced with an explicit placeholder instead of failing opaquely.
- PDF content returned by inner `Read` calls can be surfaced as document content blocks.

Evidence: User-facing limit messages (search for `"piped stdin input exceeds"`, `"request exceeds"`, `"(media removed — rejected by API)"`, and `"PDFs returned by inner Read calls"`)


### Background Fleet Labels Are More Action-Oriented
Blocked background work is now labeled as “Needs input,” making it clearer that user action is required.

Evidence: Fleet status label rename (search for `"Needs input"`)

## Bug Fixes

- Auto mode fallback now suggests `/compact` when classifier context is too large, and stage-2 classifier errors say retrying often succeeds. Evidence: Auto mode fallback messages (search for `"Auto mode classifier transcript exceeded context window — falling back to manual approval (try /compact to reduce conversation size)"` and `"Stage 2 classifier error - blocking based on stage 1 assessment (usually transient — retrying often succeeds)"`)

- Voice input now pauses after repeated early failures instead of repeatedly starting failing sessions. Evidence: Voice circuit breaker (search for `"Voice input is failing repeatedly and has been paused"`)

- Remote egress gateway environments now propagate Google Cloud auth and CA certificate variables, improving GCP tooling inside proxied remote sessions. Evidence: GCP proxy environment propagation (search for `"CLOUDSDK_AUTH_ACCESS_TOKEN"` and `"CLOUDSDK_CORE_CUSTOM_CA_CERTS_FILE"`)

- MCP configuration now rejects reserved internal server names with clearer guidance. Evidence: Reserved MCP name validation (search for `"is a reserved MCP name"` and `"Rename this server in your MCP config"`)

- GitHub PR status fetching drops `mergeStateStatus` from the GraphQL fragment and adds REST status-list fallback strings, reducing reliance on a fragile PR field. Evidence: PR status query change (search for `"fragment pr on PullRequest"` and `"[ghPrStatus] REST list"`)
