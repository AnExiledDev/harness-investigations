# Changelog for version 2.1.199

## Summary

This release adds a new session grouping UI, plugin/skill/connector discovery tools for claude.ai sessions, stacked slash command execution, partial output recovery when agents are cut off by API errors, and significant improvements to the sandbox credential masking system. The Windows sandbox is also rearchitected around a dedicated user SID rather than a Windows group, eliminating the logout requirement.

## New Features


### Session grouping in the TUI

Sessions in the session list can now be tagged with a group label. Groups then appear as a collapsible "group view" alongside the regular session list ("folder view") and the existing "status view".

Usage:

- Press `ctrl+e` on a session to set or change its group label.
- Press `ctrl+x` again on a grouped session to ungroup it.
- When no groups exist yet, the list shows: "No groups yet — press ctrl+e on a session to tag it."

Only local sessions can be grouped; remote bridge sessions are excluded.

Evidence: UI strings added for group management (search for `"ctrl+e to set group"`, `"group view"`, `"folder view"`, `"status view"`)


### Connector, plugin, and skill discovery tools

Claude Code sessions connected to claude.ai now have access to a set of discovery tools for the user's org:

- `ListConnectors` — list MCP connectors installed for the org, optionally filtered by keyword. Shows whether each connector is authenticated and whether its tools are loaded in the current chat.
- `ListPlugins` — list enabled claude.ai plugins for the user.
- `ListSkills` — list enabled claude.ai skills for the user.
- `SearchPlugins` — search the plugin catalog by keyword.
- `SearchSkills` — search the skill catalog by keyword.
- `SearchMcpRegistry` — search the MCP connector registry by keyword.
- `SuggestConnectors` — render a suggestion card for connectors the user doesn't have yet.
- `SuggestPluginInstall` — render an inline plugin install card after a `SearchPlugins` result.
- `SuggestSkills` — render a card of skills the user can add.

These tools only activate in authenticated claude.ai sessions and are used by Claude to help users discover and install new capabilities.

Evidence: New tool definitions (search for `"ListConnectors"`, `"SearchMcpRegistry"`, `"SuggestSkills"`)


### Stacked slash commands

Slash commands whose expansions begin with another slash command are now executed as a chain rather than as nested invocations. When you invoke `/foo` and its expansion starts with `/bar ...`, the stacked execution runs them in sequence, passing trailing arguments through.

A skill or command definition must not declare `argsMayContainSlashCommands: true` for this to work; that flag opts out of stacking (the args are treated as literal text). Stacking depth is capped; when the cap is reached the remaining input is passed as trailing arguments. A `UserPromptExpansion` hook can also block individual items in the stack.

Evidence: New stacker function and logging strings (search for `"Stacked skill /"`, `"Stacked command limit ("`)


### Partial output recovery for API-interrupted agents

When a subagent is cut off partway through its work by a transient API error (rate limit, server overload, or other server error), its partial output is now preserved and returned to the orchestrator with a clear note:

> "Everything below is PARTIAL output recovered from the agent before it was cut off. The agent did NOT finish its task — treat these results as incomplete."

Previously, an interrupted agent's work was discarded entirely. Now the orchestrator receives whatever the agent managed to produce, clearly labeled as incomplete.

The new `AgentApiErrorTerminationError` error class carries an `errorKind` that identifies whether the interruption was a rate limit, overload, or generic server error.

Evidence: New error class and recovery note (search for `"AgentApiErrorTerminationError"`, `"PARTIAL output recovered from the agent"`)


### Credential mask: extract patterns

The sandbox `credentials.files` masking system now supports extracting specific values from a credential file rather than substituting the entire file. The new `extract` field accepts a regex whose capture group 1 is the credential value to protect.

New fields on a `credentials.files` entry:

- `extract` — regex pattern; only the captured value is replaced with a sentinel, not the whole file.
- `maskDuplicates` — when true, any additional occurrences of the extracted value elsewhere in the file are also masked.
- `onExtractNoMatch` — controls what happens when the pattern matches nothing: `"warn"` (default, file is left unprotected with a warning), `"deny"` (degrades to full-file deny mode), or `"error"` (throws).
- `allowPlaintextInject` — allows sentinel-to-real substitution on the plain-HTTP proxy path; intended only for trusted-network test fixtures.

Evidence: New masking engine with extract support (search for `"onExtractNoMatch"`, `"extract pattern /"`, `"sandbox.credentials.allowPlaintextInject"`)


### CLAUDE_CODE_SKIP_PLUGIN_MCP_SERVERS_EXCEPT

When `CLAUDE_CODE_SKIP_PLUGIN_MCP_SERVERS` is set to skip all plugin MCP servers, you can now exempt specific servers using the new `CLAUDE_CODE_SKIP_PLUGIN_MCP_SERVERS_EXCEPT` environment variable. Pass a comma-separated list of server names or `@owner/repo` references; those servers will load even when the skip flag is active.

Evidence: New env var handling (search for `"despite CLAUDE_CODE_SKIP_PLUGIN_MCP_SERVERS (exempted via CLAUDE_CODE_SKIP_PLUGIN_MCP_SERVERS_EXCEPT)"`)


### Diff panel file list scrolling keybindings

Two new keybindings are available for navigating the file list in the diff panel:

- `app:diffFileListDown` — scroll the diff panel file list down
- `app:diffFileListUp` — scroll the diff panel file list up

Evidence: New action strings added (search for `"app:diffFileListDown"`, `"app:diffFileListUp"`)


### /rewind tip for recovering pre-/clear conversations

A new contextual tip is now shown when `/clear` is used during a session:

> "/rewind can take you back to before /clear — pick the previous-session entry to restore the pre-/clear conversation."

A companion tip describes how: "Press Esc twice or type /rewind, then pick the previous-session entry at the top."

The `rewind_pre_clear` snapshot mechanism has existed for several versions but this is the first time users are explicitly told about it.

Evidence: New tip strings (search for `"/rewind can take you back to before /clear"`)


### X-MCP-Server-ID header on tool calls

Claude Code now attaches an `X-MCP-Server-ID` header to identify which MCP server a tool call originates from. This helps MCP server operators distinguish requests from different registered servers in shared-transport setups.

Evidence: New header constant (search for `"X-MCP-Server-ID"`)


### anthropic/requiresUserInteraction tool metadata

Tools can now declare `anthropic/requiresUserInteraction: true` in their metadata to signal that their approval UI requires a human to open the session and respond. SDK hosts that embed Claude Code are expected to not offer one-tap Approve/Deny for such tools.

Evidence: New metadata field (search for `"anthropic/requiresUserInteraction"`, `"True when the tool's approval card IS the user-interaction surface"`)


### CLAUDE_CODE_BRIDGE_SESSION_ID

A new `CLAUDE_CODE_BRIDGE_SESSION_ID` environment variable is available for bridge-connected sessions.

Evidence: New env var string (search for `"CLAUDE_CODE_BRIDGE_SESSION_ID"`)

## Improvements


### Windows sandbox rearchitected around user SID (no logout required)

The Windows sandbox (`srt-win`) now uses a dedicated `srt-sandbox` user SID rather than a Windows discriminator group. Key changes:

- `--sandbox-user-sid` replaces `--group-sid` in srt-win commands.
- No logout is required after installation. The WFP egress filter is keyed on the sandbox user's SID, so the caller's network is unaffected.
- Installation instructions no longer mention group membership propagation at logon.
- `srt-win user status` replaces `srt-win group status` for readiness checks.
- Sandbox provisioning errors now report `Sandbox user is not provisioned (user=...)` rather than a group-based message.

The install instruction is now: `npx sandbox-runtime windows-install` (one UAC prompt). No logout needed.

Evidence: Removed `--group-sid` flag, added `--sandbox-user-sid` (search for `"--sandbox-user-sid"`, `"No logout is needed: the WFP filter keys on the dedicated \`srt-sandbox\` user's SID"`)


### Notification tool: clearer "not sent" explanation

The notification tool's description was updated to distinguish between different suppression reasons. When the user is actively at the terminal, the result now says:

> "Not sent — this terminal is active, so your output here already reaches the user; a separate notification would be redundant."

Previously the message distinguished between terminal focus and keystroke-based activity detection separately; now it's a single, plain explanation.

Evidence: Updated notification tool description (search for `"Not sent — this terminal is active, so your output here already reaches the user"`)


### Memory sync: concurrent write conflict recovery

When two sessions write to the same shared memory file at the same time, the losing write is now detected, the file is refreshed from the server's current version, and a message is shown:

> "Your recent write to the memory file 'X' was NOT saved to shared memory: another session updated the file first (concurrent-write conflict). The file on disk has been refreshed with the server's current version. Re-read it and re-apply your change if it is still wanted."

Evidence: New conflict recovery path (search for `"concurrent-write conflict"`)


### Memory sync: file size limit warning

Writes to a memory file that exceed the sync size limit now produce a specific warning rather than silently failing:

> "This memory file is X, over the Y sync limit — it was saved locally but will NOT be synced to shared/server memory. Split it into smaller files under the limit."

Evidence: New size check (search for `"over the"`, `"sync limit"`)


### Memory sync: foreign partition error

When a memory directory contains sync state from a different memory store, the write still saves locally but sync is disabled with a clear explanation:

> "Memory sync is disabled for this file's directory: it contains sync state from a different memory store (mount_dir_foreign_partition). This write was saved locally but is NOT being synced to shared/server memory."

Evidence: New partition check (search for `"mount_dir_foreign_partition"`)


### Plan artifact template updated to official CDS design tokens

The plan artifact HTML template (used when publishing implementation plans as shareable web pages) was updated to embed the official `@ant/cds` design token CSS rather than manually approximated values. The tokens are vendored verbatim from `@ant/cds`'s `tokens.vanilla.css` with a drift test to keep them canonical.

A new `{{TAB_TITLE}}` slot was added alongside the existing `{{TITLE}}` slot; the tab title can now differ from the document heading (useful when publishing a `.md` file whose filename differs from its heading).

Evidence: Updated plan template with vendored tokens (search for `"BEGIN vendored @ant/cds tokens"`, `"{{TAB_TITLE}}"`)


### Skill file name tracking in telemetry

When Claude Code runs a skill or command, telemetry now records a normalized `skill_file_name` and `skill_file_scope` (user or project). A fixed set of built-in skill names (`verify`, `pr`, `commit`, `code-review`, `simplify`, `go`) are tagged by their canonical name; custom skills are tagged as `custom`.

Evidence: New telemetry extraction function (search for `"skill_file_name"`, `"skill_file_scope"`)


### Extra CA cert paths for TLS termination trust bundles

The TLS termination trust bundle builder now accepts a list of additional CA cert paths (`extraCaCertPaths`). Each PEM file is read and validated individually; missing files or files with no `CERTIFICATE` block produce a warning and are skipped rather than aborting setup.

Evidence: Updated bundle builder (search for `"[mitm-ca] extraCaCertPaths:"`, `"has no PEM CERTIFICATE block; skipping"`)


### Hook output: additionalContext now shown to subagent

The `SubagentStart` hook behavior was clarified and changed:

- Exit code 0: the hook's JSON `additionalContext` is now injected into the subagent's context (previously: stdout was shown directly to the subagent, blocking errors were ignored).
- Exit code 2: stderr is shown to the user only.
- Other exit codes: stderr is shown to the user only.

Similarly for `SessionStart` and `PreToolUse`/`PostToolUse` hooks: the exit-code contract is now documented as JSON `additionalContext` on code 0.

Evidence: Updated hook exit-code descriptions (search for `"Exit code 0 - JSON additionalContext shown to subagent"`)


### Request body compression (feature-flagged)

A new feature flag `tengu_gzip_request_bodies` and corresponding env var `CLAUDE_CODE_GZIP_REQUEST_BODIES` enable gzip compression of API request bodies. Not enabled by default.

Evidence: New flag check (search for `"tengu_gzip_request_bodies"`, `"CLAUDE_CODE_GZIP_REQUEST_BODIES"`)


### /config command syntax shown in help

The `/config` command now shows its usage syntax when a bare invocation or help is requested:

> `/config <key>=<value> (run /config --help to list keys)`

Evidence: New usage string (search for `"/config <key>=<value> (run /config --help to list keys)"`)


### Settings write queue: async serial writes

The settings write path was refactored to use a serial queue (`_f`) that chains writes as promises rather than executing synchronously. This prevents race conditions when multiple settings mutations happen in quick succession. A `R$s` drain function waits for up to five rounds of queue settling before proceeding.

Evidence: New async write queue (search for `"mbn"` pattern with promise-chained map, also `"saveConfigWithLock"` log strings)


### Model alias migration: more cases covered

New migration functions handle Sonnet 4.5, legacy opus, and `sonnet[1m]` model settings:

- Failed to migrate Sonnet 4.5 model setting
- Failed to migrate legacy Opus model setting
- Failed to migrate opus model setting
- Failed to migrate sonnet[1m] model setting

Evidence: New migration error strings (search for `"Failed to migrate Sonnet 4.5 model setting"`)


### Cowork setup guide

A guided onboarding skill for Cowork is now bundled. It walks users through picking a role, installing a matching plugin, trying a skill, and connecting tools. Triggered by phrases like "set up cowork", "setup cowork", "get started with cowork", and similar.

Evidence: New skill definition (search for `"Guided Cowork setup"`, `"Setup Cowork Help"`)

## Bug Fixes

- Settings writes that fail to persist no longer bump the migration version counter, so the failed migration re-runs on the next startup instead of being silently skipped. (search for `"Skipping migrationVersion bump: a settings-writing migration failed to persist"`)

- The credential mask now correctly reports "mask mode" (not "whole-file mask mode") when skipping a binary file, consistent with the new extract-based masking approach. (search for `"binary credential files are not supported in mask mode"`)

## In Development


### tengu_paper_halyard [In Development]

A new feature flag `tengu_paper_halyard` is present that, when enabled, prevents Project and Local memory types from being synced or included in context. The flag defaults to `false` and is not exposed to users.

Status: Feature-flagged (defaults off)

Evidence: Flag check disabling memory sync (search for `"tengu_paper_halyard"`)


### X-CCR-Turn-Id request tracking [In Development]

Infrastructure was added to track a cross-session turn ID (`X-CCR-Turn-Id`) through relay-relayed human messages. The turn ID is extracted from relay-flagged messages, propagated through the request context via `AsyncLocalStorage`, and cleared when the turn context changes. Not yet exposed as a user-facing feature.

Status: Internal infrastructure, no user-visible behavior yet.

Evidence: New turn ID tracker (search for `"X-CCR-Turn-Id"`)

---

Generated with:
- tool: `harness-investigations@0c752ef-dirty`
- provider: `claude`
- model: `claude-sonnet-4-6`
- primary diff: `archive/claude-code/changes/changes-v2.1.199.md` (filtered astdiff)
- string diff: `archive/claude-code/changes/string-diff-v2.1.199.txt`
