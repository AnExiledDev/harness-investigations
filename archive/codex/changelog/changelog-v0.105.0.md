# Changelog for version 0.105.0

## Highlights

This release introduces **Realtime voice mode** (experimental, mic-driven conversation via `/realtime`), a **syntax highlighting theme picker** (`/theme` plus user-installable `.tmTheme` files in `$CODEX_HOME/themes/`), and a **Claude → Codex migration tool** that detects existing `~/.claude/` configs/skills/`CLAUDE.md` and imports them into Codex. The plumbing underneath gets a major overhaul: skills move into a dedicated `codex-skills` crate (with on-disk system-skill installation), the v2 protocol grows persistent-network-policy approvals, skill approval prompts, Windows Sandbox setup notifications, a "thread"-shaped replacement for the v1 conversation API, and a new `Reject` approval mode that auto-declines selected prompt categories.

### `/realtime` voice mode (experimental)

**What:** A new TUI slash command that toggles a live, audio-only voice conversation with Codex over a websocket connection. While active, the composer becomes audio-only and the footer shows `/realtime stop live voice`.

**Details:**
- Voice capture uses `cpal` for the microphone and a streaming `RealtimeAudioPlayer` for output. The realtime UI tracks four phases: `Inactive`, `Starting`, `Active`, and `Stopping`.
- Two new experimental config keys gate the connection:
  - `experimental_realtime_ws_base_url` — websocket endpoint to dial.
  - `experimental_realtime_ws_backend_prompt` — backend prompt template.
- New `Op` variants `RealtimeConversationStart(ConversationStartParams)` and `RealtimeConversationClose` drive the session.
- New protocol events `RealtimeConversationStartedEvent`, `RealtimeConversationRealtimeEvent { payload }`, `RealtimeConversationClosedEvent { reason }`. The `RealtimeEvent` payload covers `SessionCreated`, `SessionUpdated`, `AudioOut`, `ConversationItemAdded`, and `Error`.
- The codex-api ships a new `realtime_websocket` endpoint with end-to-end tests.
- The TUI realtime path is gated off on Linux (`#[cfg(not(target_os = "linux"))]`) — voice capture/playback fields are absent there. Other platforms get the full experience.

**Usage:**
```
/realtime          # start voice mode
/realtime          # toggle off (or "/realtime stop")
```

**Code references:** `realtime_websocket` endpoint in `codex-api/src/endpoint/realtime_websocket/methods.rs`; `core/src/realtime_conversation.rs` (≈473 new lines); `tui/src/voice.rs` (≈834 lines, `VoiceCapture`, `RealtimeAudioPlayer`); `RealtimeConversationUiState` in `tui/src/chatwidget/realtime.rs`; slash entry in `tui/src/slash_command.rs`.


### Syntax highlighting theme picker (`/theme`)

**What:** A new TUI slash command that lets you preview and pick a syntax highlighting theme. Themes are pulled from a bundled set plus any user-installed `.tmTheme` files under `$CODEX_HOME/themes/`. The choice is persisted to `[tui] theme = "..."` in `config.toml`.

**Details:**
- The picker shows side-by-side diff previews when the terminal is wide enough; otherwise a stacked 4-line preview.
- Selection is live: the runtime swaps in the highlighted theme as you scroll, and Cancel restores the snapshot.
- A new `theme` config key on the TUI config overrides automatic light/dark detection ("Syntax highlighting theme name (kebab-case). When set, overrides automatic light/dark theme detection. Use `/theme` in the TUI or see `$CODEX_HOME/themes` for custom themes.").
- Highlighting itself was rewritten on top of `syntect` (the workspace replaced `tree-sitter-highlight = "0.25.10"` with `syntect = "5"`), which is what enables `.tmTheme` compatibility.
- A clear, user-facing warning is shown when a configured theme name doesn't match any bundled theme or `.tmTheme` file.

**Usage:**
```
/theme                                      # open the picker
mkdir -p ~/.codex/themes
cp ~/Downloads/MyTheme.tmTheme ~/.codex/themes/my-theme.tmTheme
# /theme will now list "my-theme"
```

**Code references:** `tui/src/theme_picker.rs` (621 lines); `tui/src/render/highlight.rs`; `Cargo.toml` swap of `tree-sitter-highlight` for `syntect`.


### Claude → Codex migration: `externalAgentConfig/detect` & `import`

**What:** Two new v2 RPCs that detect existing Anthropic Claude Code configuration on disk and migrate it into Codex's locations. The intent is to bootstrap new Codex users who already had a Claude setup.

**Details:**
- `externalAgentConfig/detect` walks `~/.claude/` (when `includeHome: true`) and any provided `cwds` looking for migration candidates. It returns a list of `ExternalAgentConfigMigrationItem` whose `type` is one of:
  - `AGENTS_MD` — `CLAUDE.md` files.
  - `CONFIG` — `~/.claude/settings.json` and equivalents.
  - `SKILLS` — entries under `~/.claude/skills/`.
  - `MCP_SERVER_CONFIG` — MCP server entries from settings.
- `externalAgentConfig/import` accepts the items and writes them out: TOML is **merged**, never clobbered (existing `config.toml` keys are preserved); skills land under `~/.agents/skills/`; CLAUDE.md content turns into `AGENTS.md`; items already present are skipped.
- Both home- and repo-scoped configs are handled.

**Code references:** `core/src/external_agent_config.rs` (≈920 lines); v2 protocol additions in `app-server-protocol/src/protocol/v2.rs`; types `ExternalAgentConfigMigrationItem`, `ExternalAgentConfigMigrationItemType`.


### `Reject` approval mode

**What:** A new `AskForApproval` variant that auto-declines specific categories of prompts instead of asking the user.

**Details:**
- The new variant is `Reject { sandbox_approval: bool, rules: bool, mcp_elicitations: bool }`. Per the JSON schema:
  - `sandbox_approval` — reject prompts triggered by sandbox escalation.
  - `rules` — reject prompts triggered by execpolicy `prompt` rules.
  - `mcp_elicitations` — reject MCP elicitation prompts.
- Useful for non-interactive runs where you want unattended-deny semantics on chosen prompt classes (e.g., reject all sandbox escalations but still ask about MCP elicitations).

**Code references:** `AskForApproval::Reject(RejectConfig)` in `app-server-protocol/src/protocol/v2.rs`; schema mirror in `RejectConfig.ts`.


### Skill approval requests (`skill/requestApproval`)

**What:** A new server→client request that prompts the user before a skill runs.

**Details:**
- Params: `SkillRequestApprovalParams { item_id, skill_name }`.
- Response: `SkillRequestApprovalResponse { decision: "approve" | "decline" }`.
- When the user declines, the skill receives the explanatory string `"This script is part of the skill and the user declined the skill usage"` so the model can reason about the refusal.
- The TUI gains skill-toggle and skill-popup views (`bottom_pane/skill_popup.rs`, `bottom_pane/skills_toggle_view.rs`) to drive the approval UI.

**Code references:** v2.rs `SkillRequestApprovalParams`/`SkillApprovalDecision`; constant in `core/src/skills/invocation_utils.rs`; `mcp-server/src/codex_tool_runner.rs` handles the new event type.


### Windows Sandbox setup notifications

**What:** A new RPC pair that lets clients drive Windows Sandbox preflight setup and observe its result.

**Details:**
- Request: `windowsSandbox/setupStart` with `WindowsSandboxSetupStartParams { mode: Elevated | Unelevated }` → returns `{ started: bool }`.
- Notification: `windowsSandbox/setupCompleted` with `{ mode, success, error }`.
- Implementation dispatches between an elevated path and a legacy preflight setup, persists the chosen mode to config, and emits success/failure metrics.

**Code references:** `core/src/windows_sandbox.rs` (`WindowsSandboxSetupMode`, `run_windows_sandbox_setup()`); v2.rs notification + request types.


### Persistent network-policy amendments

**What:** When approving a command that wants outbound network, the user can now persist an `allow` or `deny` rule for the host so future requests don't re-prompt.

**Details:**
- New types: `NetworkPolicyAmendment { host, action }` and `NetworkPolicyRuleAction = "allow" | "deny"`.
- `CommandExecutionRequestApprovalParams` gains `network_approval_context: NetworkApprovalContext` (host + protocol — `http`, `https`, `socks5Tcp`, `socks5Udp`) plus `proposed_network_policy_amendments: Vec<NetworkPolicyAmendment>`.
- New decision variant `CommandExecutionApprovalDecision::ApplyNetworkPolicyAmendment { network_policy_amendment }` causes the rule to be saved.
- Internally, amendments are translated into execpolicy rule entries (e.g., `Allow http`, `Deny https_connect`, `Allow socks5_tcp`) with auto-generated, human-readable justifications.
- The TUI ships a new approval-overlay snapshot for `network_exec_prompt`.

**Code references:** `core/src/network_policy_decision.rs`; `NetworkPolicyAmendment` / `NetworkPolicyRuleAction` in v2.rs and TS schema.


### Managed-MITM HTTPS proxy mode

**What:** The `network-proxy` crate gains a managed certificate authority and an opt-in MITM mode so HTTPS traffic can be inspected against the same allow/deny rules as plain HTTP.

**Details:**
- New config keys (network-proxy/README.md):
  - `mitm = false` — when `true`, HTTPS `CONNECT` requests are terminated locally so limited-mode method policy applies to the inner traffic.
  - `dangerously_allow_all_unix_sockets = false` (macOS) — bypasses the unix-socket allowlist.
- A local CA is auto-generated under `$CODEX_HOME/proxy/ca.pem` + `ca.key` via `rcgen`. New file `network-proxy/src/certs.rs` handles generation and persistence.
- `NetworkRequirements` adds `dangerouslyAllowAllUnixSockets: bool | null` so the requirement can be surfaced in the UI.

**Code references:** `network-proxy/src/certs.rs`; README at `network-proxy/README.md`; `NetworkRequirements.ts`.


### Additional permission profiles in approval prompts

**What:** When a command needs new permissions (network, filesystem read/write, macOS preferences/automation/accessibility/calendar), the approval prompt can now include the requested deltas so the user knows what they're elevating.

**Details:**
- New top-level types: `PermissionProfile { network, file_system, macos }`, `FileSystemPermissions` (read/write path lists), `MacOsPermissions { preferences, automations, accessibility, calendar }`, `MacOsPreferencesValue`, `MacOsAutomationValue`.
- v2 adds `AdditionalPermissionProfile`, `AdditionalFileSystemPermissions`, `AdditionalMacOsPermissions` that are attached to `CommandExecutionRequestApprovalParams.additional_permissions`.
- The TUI ships a new `additional_permissions_prompt` approval-overlay snapshot.

**Code references:** types in `app-server-protocol/schema/typescript/`; v2.rs additions to `CommandExecutionRequestApprovalParams`.


### Bundled "system" skills installed under `$CODEX_HOME/skills/.system/`

**What:** A new `codex-skills` workspace crate that ships embedded reference skills (e.g., `skill-creator`, `skill-installer`) and writes them to disk on startup.

**Details:**
- `install_system_skills(codex_home)` is the entry point. It writes embedded skills into `$CODEX_HOME/skills/.system/`.
- A marker file `.codex-system-skills.marker` plus a content fingerprint hash makes reinstall a no-op when the on-disk copy already matches.
- Skill metadata gains `permission_profile: Option<PermissionProfile>` so a `SKILL.md` can declare the extra permissions it needs, which feeds into the new approval prompts.

**Code references:** `codex-rs/skills/src/lib.rs`; `install_system_skills()`; `core/src/skills/invocation_utils.rs`.


### Thread status notifications and richer thread metadata

**What:** The v2 thread API can now stream live thread status, supports searching by title, and tracks human-friendly nicknames/roles for sub-agents.

**Details:**
- New `ThreadStatus` enum: `notLoaded`, `idle`, `systemError`, or `{ type: "active", activeFlags: ["waitingOnApproval" | "waitingOnUserInput"] }`.
- New notification `thread/status/changed` with `ThreadStatusChangedNotification { threadId, status }`.
- `Thread` gains `status`, `agentNickname` (random nickname for `AgentControl`-spawned sub-agents), `agentRole`, and `name` (user-facing thread title).
- `ThreadListParams.searchTerm` filters threads by title substring.
- `ThreadStartParams.serviceName: string | null` lets the client tag the originating service.
- `ThreadItem::AgentMessage` gains `phase: MessagePhase | null` where `MessagePhase = "commentary" | "final_answer"`, distinguishing in-turn narration from the final answer.

**Code references:** `app-server-protocol/src/protocol/v2.rs`; `Thread.ts`, `ThreadStatus.ts`, `ThreadActiveFlag.ts`; `TurnCompletedNotification.json` for `MessagePhase`.


### Feedback uploads can include extra log files

**What:** `feedback/upload` now accepts an optional list of additional log file paths so users can attach more context when filing feedback.

**Details:** `FeedbackUploadParams` adds `extraLogFiles: Array<string> | null`. Clients can populate it in addition to the standard bundled logs.

**Code references:** `FeedbackUploadParams.ts`; `tui/src/bottom_pane/feedback_view.rs`.


### `/copy` and `/clear` slash commands

**What:** Two convenience commands in the TUI:
- `/copy` — copy the latest Codex output to your clipboard. Hidden on Android.
- `/clear` — clear the terminal and start a new chat.

**Code references:** `tui/src/slash_command.rs`.


### `codex exec --progress-cursor`

**What:** A new boolean flag on `codex exec` that forces cursor-based progress updates (useful in environments where the default heuristic guesses wrong).

**Details:** Alongside this, `--output-last-message` / `-o` was promoted to a global flag (`global = true`), so it now works after `exec resume` as well as before.

**Code references:** `exec/src/cli.rs`.


### Local-CA-generating dependency stack

**What:** New workspace dependencies enable several user-visible features above:
- `csv` — used by data import paths.
- `gethostname` — embedded in feedback/metadata helpers.
- `syntect` — drives the new theme picker and `.tmTheme` support.
- `bindgen`/`alsa` (transitive) — pulled in to support the realtime audio pipeline on Linux-like platforms.

### Multi-agent picker shows nicknames, roles, and live status

**What changed:** `CollabAgentSpawnEndEvent` and `CollabAgentInteractionEndEvent` now carry `new_agent_nickname` / `new_agent_role` and `receiver_agent_nickname` / `receiver_agent_role`. The TUI multi-agents picker formats entries as `"{nickname} [{role}]"` (with `Main [default]` for the root) and renders status dots — green for active, gray for closed.

**Code references:** `tui/src/multi_agents.rs`: `format_agent_picker_item_name`, `agent_picker_status_dot_spans`, `sort_agent_picker_threads`; new types `CollabAgentRef`, `CollabAgentStatusEntry`.


### Apps configuration model: per-tool overrides and defaults

**What changed:** The `[apps]` config surface was restructured for finer-grained control:
- `AppConfig` gains `destructive_enabled`, `open_world_enabled`, `default_tools_approval_mode`, `default_tools_enabled`, and a `tools` map for per-tool overrides.
- New `AppToolApproval = Auto | Prompt | Approve`.
- New `[apps._default]` section (`AppsDefaultConfig`) sets the baseline `enabled`, `destructive_enabled`, and `open_world_enabled` flags inherited by individual apps.

**Removed:** the `disabled_reason: AppDisabledReason` field (and the `AppDisabledReason` enum entirely) — apps are now described by enabled/disabled flags rather than a reason-tagged disable.

**Code references:** `app-server-protocol/src/protocol/v2.rs`; `AppToolApproval.ts`, `AppsDefaultConfig.ts`, `AppToolsConfig.ts`.


### `Arg0DispatchPaths` consolidates dispatch binaries

**What changed:** The CLI plumbing replaced the bare `Option<PathBuf>` for `codex_linux_sandbox_exe` with a struct `Arg0DispatchPaths { codex_linux_sandbox_exe, main_execve_wrapper_exe }`. Every subcommand entry point and `ConfigOverrides` was updated so the new `codex-execve-wrapper` binary path is propagated alongside the linux-sandbox path.

**Why it matters:** This is the wiring that makes the new shell-escalation crate (and the wrapper binary) reachable from every entry point — exec, MCP server, app server, TUI — without each one re-discovering it.

**Code references:** `cli/src/main.rs`; `mcp-server`'s `ConfigOverrides`.


### Pending approvals replay on thread resume

**What changed:** When a thread is resumed, any approvals that were pending at the moment of suspension are replayed so the user is asked again instead of silently losing the prompt.

**Code references:** `tui/src/app/pending_interactive_replay.rs`.


### Rate-limit and status surfaces

**What changed:** New status pieces in the TUI: `status/card.rs` and `status/rate_limits.rs` give the bottom-pane a structured place to surface rate-limit information (rather than ad-hoc strings).

**Code references:** `tui/src/status/card.rs`, `tui/src/status/rate_limits.rs`.


### Schema codegen now panics on naming collisions

**What changed:** `app-server-protocol/src/export.rs` was tightened to **panic** on numbered-definition or variant title collisions during JSON-schema codegen, instead of silently appending `2`/`3`/... suffixes. Authors of new protocol types now get a hard compile-time error if names collide. Combined with a new v1 allow-list (`V1_CLIENT_REQUEST_METHODS`), the schema codegen only emits `InitializeParams`/`InitializeResponse` for v1 — effectively marking the v1 conversation API as legacy and steering schema-generated clients toward the v2 thread API.

**Code references:** `app-server-protocol/src/export.rs`.


### Skill metadata: `path` → `path_to_skills_md`

**What changed:** `SkillMetadata.path` was renamed to `path_to_skills_md` everywhere it's referenced (injection, chatwidget, MCP runner) so the field clearly describes what it points to rather than being ambiguous about which file in the skill bundle.

**Code references:** `core/src/skills/injection.rs`; `tui/src/chatwidget/skills.rs`; `core/src/skills/invocation_utils.rs`.


### Skill invocation analytics

**What changed:** Skill invocations are now tagged with `analytics_client::InvocationType::Explicit` vs `Implicit` so the source (slash command vs auto-injected) is distinguishable in telemetry.

**Code references:** `core/src/skills/invocation_utils.rs` and `core/src/skills/injection.rs`.

### `--output-last-message` works after `exec resume`

**What was broken:** The `--output-last-message` / `-o` flag could only be passed before the subcommand, so `codex exec resume … -o file` would fail.

**Fix:** The flag is now declared `global = true`, and a regression test was added at `exec/src/cli.rs` line ~112258.


### Lazy `import yaml` in skill-creator helper

**What was broken:** `skill-creator/scripts/generate_openai_yaml.py` imported PyYAML at module load, so users without it installed couldn't even invoke the tool to see the helpful error.

**Fix:** The import now lazy-loads inside the function so users see a clear failure path.

**Code references:** `skill-creator/scripts/generate_openai_yaml.py`.

### `codex-exec-mcp-server` binary and `codex-exec-server` crate removed

**What:** The `codex-exec-mcp-server` MCP tool that exposed a `shell` capability with fine-grained per-`execve()` privilege escalation has been deleted, along with the entire `codex-exec-server` crate and its tests.

**Impact:** If you launched `codex-exec-mcp-server` directly, that binary no longer exists. The execve-wrapper portion of the functionality moved into the new `codex-shell-escalation` crate (decisions are `Run`, `Escalate`, `Deny` via the new `EscalationPolicy` async trait). The `codex-execve-wrapper` binary is the supported replacement and is now plumbed through every entry point via `Arg0DispatchPaths`.

**Code references:** deletion of `codex-rs/exec-server/`; new `codex-rs/shell-escalation/` crate (README, `escalation_policy.rs`, `bin/main_execve_wrapper.rs`).


### `utils/sanitizer` workspace member removed

**What:** The dedicated sanitizer crate was removed from the workspace; sanitizer logic is inlined into its callers.


### `askama`, `indoc`, and `tree-sitter-highlight` removed from workspace deps

**What:** `askama` (templating) and `indoc` (string dedenting) were dropped. `tree-sitter-highlight` was replaced by `syntect` to support `.tmTheme` files in the new theme picker.


### v1 conversation API treated as legacy

**What:** JSON schema codegen now emits only `InitializeParams`/`InitializeResponse` for v1. All other v1 conversation methods (`newConversation`, `getConversationSummary`, `listConversations`, `resumeConversation`, `forkConversation`, `archiveConversation`, `sendUserMessage`, `sendUserTurn`, `interruptConversation`, `addConversationListener`, `removeConversationListener`, `gitDiffToRemote`, `loginApiKey`, `loginChatGpt`, `cancelLoginChatGpt`, `logoutChatGpt`, `getAuthStatus`, `getUserSavedConfig`, `setDefaultModel`, `getUserAgent`, `userInfo`, `execOneOffCommand`) still work at runtime, but no schemas are generated for them — clients are expected to migrate to the v2 thread API.

**Code references:** `V1_CLIENT_REQUEST_METHODS` allow-list in `app-server-protocol/src/export.rs`.
