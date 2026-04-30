# Changelog for version 0.102.0

## Highlights

This release introduces a wide-ranging hardening pass on Codex's permission model, plus several new user-facing capabilities. Native sleep prevention keeps your Mac awake during long turns, a brand-new live "fuzzy file search session" API streams matches incrementally, and skill manifests can now declare granular network / filesystem / macOS automation permissions that drive a per-skill seatbelt sandbox. The experimental sub-agents feature has been renamed from `collab` to `multi_agent`, the deprecated `request_rule` feature flag has been folded into the always-on `on-request` policy, and `on-failure` is now formally deprecated in favor of `on-request` / `never`. Numerous protocol additions land in this version: `model/rerouted` notifications, explicit `status` fields on `exec_command_end` / `patch_apply_end`, a `[memories]` config section, user-defined agent roles, and `persistExtendedHistory` for non-lossy thread replay.

### Prevent Idle Sleep While a Turn Is Running (macOS)

**What:** A new experimental feature, `prevent_idle_sleep`, keeps your machine awake while Codex is actively running a turn. Unlike previous `caffeinate`-based approaches, this uses native IOKit power assertions (`IOPMAssertionCreateWithName` / `IOPMAssertionRelease`), so the assertion lifecycle is bound to a Rust object's lifetime — the assertion is automatically released when the turn ends or the process exits.

**Details:**
- Assertion type: `PreventUserIdleSystemSleep`.
- Available on macOS only (the feature shows as `Experimental` on macOS and `UnderDevelopment` elsewhere).
- Enable from `/experimental` in the TUI or via `[features] prevent_idle_sleep = true` in `config.toml`.
- A new `codex-utils-sleep-inhibitor` workspace crate exposes `SleepInhibitor::new(enabled).set_turn_running(true|false)` and is wired into the TUI's chat widget.
- Idempotent: repeated `set_turn_running(true)` calls do not stack assertions, and disabling at runtime releases the assertion immediately.

**Code references:** `SleepInhibitor` in `utils/sleep-inhibitor/src/lib.rs`, `MacOsSleepInhibitor` in `utils/sleep-inhibitor/src/macos_inhibitor.rs`, feature spec in `core/src/features.rs`.


### Live Fuzzy File Search Sessions (Experimental Protocol API)

**What:** A new streaming API lets app-server clients open a long-lived fuzzy-file-search session and receive incremental matches as the user types — replacing the old "search everything once per query" model.

**Details:**
- Three new client requests: `fuzzyFileSearch/sessionStart`, `fuzzyFileSearch/sessionUpdate`, `fuzzyFileSearch/sessionStop`.
- Two new server notifications: `fuzzyFileSearch/sessionUpdated` (`{ sessionId, query, files }`) and `fuzzyFileSearch/sessionCompleted` (`{ sessionId }`).
- The session walks the configured `roots`, streams snapshots that match the latest query, and is automatically canceled when the session struct is dropped.
- TUI's file_search has been migrated to the streaming session API.

**Code references:** `FuzzyFileSearchSession::start_fuzzy_file_search_session()` in `app-server/src/fuzzy_file_search.rs`, schema in `app-server-protocol/src/protocol/common.rs`.


### Skill Manifest Permissions (network / filesystem / macOS)

**What:** Skills can now declare a granular `[permissions]` block that compiles directly into a per-invocation sandbox profile.

**Details:**
- `permissions.network` (boolean) — gate network access for the skill.
- `permissions.file_system.read` / `permissions.file_system.write` — lists of paths (absolute, `~`, or relative-to-skill-dir) that promote the sandbox to `WorkspaceWrite` with restricted readable roots.
- `permissions.macos.preferences` — `"read-only"` (default), `"read-write"`, or `false` to disable; emits matching seatbelt clauses for `cfprefsd` and `user-preference-*`.
- `permissions.macos.automations` — `true`, `false`, or an array of bundle IDs; emits scoped or unscoped `appleevent-send` allowlists.
- `permissions.macos.accessibility` and `permissions.macos.calendar` — boolean toggles that allow the corresponding mach services.
- Path normalization expands `~`, resolves relative paths against the skill directory, and canonicalizes via `dunce::canonicalize`.

**Code references:** `compile_permission_profile()` in `core/src/skills/permissions.rs`, `build_seatbelt_extensions()` in `core/src/seatbelt_permissions.rs`.


### Network Approval for Sandboxed Commands

**What:** When a sandboxed shell or unified-exec command tries to reach a host that is denied or not on the allowlist, the request can now be surfaced to the user as an approval prompt with rich context (host + protocol).

**Details:**
- New `NetworkApprovalContext { host, protocol }` is attached to `ExecApprovalRequest` events; protocol enum is `http`, `https`, `socks5_tcp`, or `socks5_udp`.
- A new `NetworkApprovalService` registers per-attempt state (turn id, call id, command, cwd) and exposes a `BlockedRequestObserver` + `NetworkPolicyDecider` so the running proxy decides whether to ask, deny, or auto-allow.
- Two approval modes: `Immediate` (block the command and prompt) and `Deferred` (let the command continue while the prompt is pending).
- Denied-by-policy paths produce a human-readable explanation (`"Network access to \"x\" was blocked: domain is not on the allowlist for the current sandbox mode."`) instead of a generic sandbox-denied error.
- `SandboxErr::Denied` now carries an optional `network_policy_decision` payload describing the proxy decision.

**Code references:** `network_approval_context_from_payload()` and `denied_network_policy_message()` in `core/src/network_policy_decision.rs`, `NetworkApprovalService` in `core/src/tools/network_approval.rs`.


### `model/rerouted` Notification & ModelRerouteEvent

**What:** When the backend silently reroutes a request to a safer model (currently for high-risk cyber-activity safety checks), the TUI/clients now learn about it instead of just seeing a different `from_model`/`to_model` pair.

**Details:**
- New `EventMsg::ModelReroute { from_model, to_model, reason }` event.
- New `ModelReroutedNotification` (v2 app-server notification) carrying `threadId`, `turnId`, `fromModel`, `toModel`, and `reason`.
- `ModelRerouteReason` is currently `"high_risk_cyber_activity"` (snake_case in the v1 wire form, `"highRiskCyberActivity"` in v2 camelCase).

**Code references:** `ModelRerouteEvent` in `protocol/src/protocol.rs`, dispatch in `app-server/src/bespoke_event_handling.rs`.


### `[memories]` Config Section

**What:** Users can now tune the memories subsystem from `config.toml` instead of relying on hard-coded constants.

**Details:**
- `max_raw_memories_for_global` — number of recent raw memories retained for global consolidation.
- `max_rollout_age_days` — maximum age of threads considered for memory creation.
- `max_rollouts_per_startup` — max rollout candidates processed per startup.
- `min_rollout_idle_hours` — minimum idle time before a thread becomes eligible (>12h recommended).
- `phase_1_model` — model used for thread summarization.
- `phase_2_model` — model used for global consolidation.

Example:

```toml
[memories]
max_raw_memories_for_global = 512
max_rollout_age_days = 42
max_rollouts_per_startup = 9
min_rollout_idle_hours = 24
phase_1_model = "gpt-5-mini"
phase_2_model = "gpt-5"
```

**Code references:** `MemoriesToml` in `core/src/config/types.rs`, schema additions in `core/config.schema.json`.


### `[agents.<role>]` User-Defined Agent Roles

**What:** The hard-coded `AgentRole` enum has been replaced by a config-driven mechanism: any role declared under `[agents]` becomes a spawnable sub-agent type, layered on top of the parent config.

**Details:**
- New `AgentRoleToml` schema with `description` (shown in the spawn-tool guidance) and `config_file` (a TOML layer applied on top of the active config).
- Built-in roles include `default`, `worker`, and `explorer`; the `explorer` role embeds `agent/builtins/explorer.toml` (`model = "gpt-5.1-codex-mini"`, `model_reasoning_effort = "medium"`).
- `apply_role_to_config()` validates the role, deserializes its TOML, inserts it as a `SessionFlags` layer on the active `ConfigLayerStack`, and reloads the merged `Config`.
- The spawn-tool description is generated from user-defined roles first, then built-ins, with descriptions you provide rendered into the tool spec.

**Code references:** `apply_role_to_config()` and `spawn_tool_spec::build()` in `core/src/agent/role.rs`.


### `persistExtendedHistory` Flag for Lossless Thread Replay

**What:** `thread/start`, `thread/resume`, and `thread/fork` now accept `persistExtendedHistory: true`, which records additional event types into the rollout file so subsequent `thread/read`/`resume`/`fork` calls reconstruct a richer history.

**Details:**
- New `EventPersistenceMode` enum (`Limited` | `Extended`) controls which `EventMsg` variants are persisted in rollout files.
- Extended mode persists `WebSearchEnd`, `ExecCommandEnd`, `PatchApplyEnd`, `McpToolCallEnd`, `ViewImageToolCall`, and all collab agent end events on top of the limited set.
- Override is rejected mid-session: passing `persistExtendedHistory` to `sendUserTurn` while a session is already running emits a config warning.
- Note: this does not backfill history that was not persisted previously.

**Code references:** `EventPersistenceMode` in `core/src/rollout/policy.rs`, threading through `core/src/codex.rs`.


### `cwd` Filter on `thread/list`

**What:** `thread/list` now accepts an optional `cwd` parameter that returns only threads whose session cwd exactly matches the given path.

**Details:** Useful for project-scoped UIs that want to restrict the thread picker to the current workspace.

**Code references:** `ThreadListParams` in `app-server-protocol/schema/typescript/v2/ThreadListParams.ts`.


### `/sandbox-add-read-dir <absolute-path>` Slash Command (Windows)

**What:** A new TUI slash command that grants the Windows sandbox read access to an additional absolute directory without having to elevate the entire sandbox.

**Details:**
- Validates the path is absolute, exists, and is a directory.
- Uses `grant_read_root_non_elevated()` to refresh the Windows ACL setup with the canonical path added to the allowed read roots.
- Visible only on Windows (`SlashCommand::SandboxReadRoot::is_visible()` checks `cfg!(target_os = "windows")`).

**Code references:** `grant_read_root_non_elevated()` in `core/src/windows_sandbox_read_grants.rs`, slash command wiring in `tui/src/slash_command.rs`.


### `Op::ReloadUserConfig` and Hidden-Model Filtering

**What:** Two related pieces of plumbing for live config and model-list curation:
- `Op::ReloadUserConfig` reloads user-level config-layer overrides for the active session (notably enables/disables apps without restarting the thread). The TUI submits this op when the user toggles app config.
- `Model.hidden: bool` distinguishes models that should not appear in the default picker. `model/list` accepts a new `includeHidden: boolean` parameter (default `false`) to opt into showing them.

**Code references:** `reload_user_config_layer()` in `core/src/state/session.rs`, hidden-model filter in `app-server/src/models.rs`.


### `[Image #N]` Remote Image Rows in the Composer

**What:** The TUI composer now renders remote-image attachments (URLs rehydrated from app-server/backtrack history) as non-editable `[Image #N]` rows above the textarea, with keyboard-driven selection and deletion.

**Details:**
- `Up` at cursor 0 selects the last remote image; `Up`/`Down` walks rows; `Down` past the last row returns focus to text.
- `Delete`/`Backspace` removes the selected row.
- Numbering is unified: remote rows occupy `[Image #1]..[Image #M]`, and local image placeholders shift to `[Image #M+1]..[Image #N]`. Deleting a remote row relabels the locals to keep numbering contiguous.

**Code references:** `ChatComposer::remote_image_urls` in `tui/src/bottom_pane/chat_composer.rs`.

### Renames & Deprecations

- **`collab` → `multi_agent`.** The experimental sub-agent feature is now keyed as `multi_agent` in `[features]` and announced as "Multi-agents". `collab` is preserved as a legacy alias so existing configs keep working. `feature_for_key("collab")` and `feature_for_key("multi_agent")` both resolve to `Feature::Collab` (the internal name was kept to avoid churn). Source files moved: `core/src/tools/handlers/collab.rs` → `multi_agents.rs`, and `tui/src/collab.rs` → `tui/src/multi_agents.rs`.
- **`skills/remote/read` → `skills/remote/list`** and **`skills/remote/write` → `skills/remote/export`.** The export response no longer returns `name` (only `id` and `path`), and `SkillsRemoteList` requires `hazelnutScope` (`example` | `workspace-shared` | `all-shared` | `personal`), `productSurface` (`chatgpt` | `codex` | `api` | `atlas`), and `enabled`. The `isPreload` flag on the export request has been removed.
- **`on-failure` approval policy** is now formally marked **DEPRECATED** in both the CLI (`--ask-for-approval=on-failure`) and the protocol enum. Prefer `on-request` for interactive runs and `never` for non-interactive ones.
- **`request_rule` feature** has been moved to `Stage::Removed` and is no longer toggleable. The on-request approval prompt now always uses the rule-based template (`approval_policy/on_request_rule.md`); the old `on_request.md` template has been deleted, and `prefix_rule` is always part of `create_approval_parameters()`.
- **`web_search`** legacy notice now reads "deprecated because web search is enabled by default" and the help text mentions overriding only if needed.


### Explicit `status` Field on Exec / Patch End Events

- `ExecCommandEndEvent` and `PatchApplyEndEvent` now carry an explicit `status` field (`completed` | `failed` | `declined`) instead of inferring success from `exit_code == 0` or `success: bool`. The app server uses this to map directly into `CommandExecutionStatus` / `PatchApplyStatus`.


### Hooks API Refactor: `HookOutcome` → `HookResult` / `HookResponse`

- Hooks now return a richer outcome: `HookResult::Success`, `HookResult::FailedContinue(error)`, or `HookResult::FailedAbort(error)`, wrapped in a `HookResponse { name, result }`.
- `Hooks::dispatch()` returns `Vec<HookResponse>` instead of nothing, and the orchestrator decides how to react: continue on success, log on `FailedContinue`, abort the operation on `FailedAbort`.
- The legacy `notify_hook` is now named `"legacy_notify"`, and `command.spawn()` failures surface as `FailedContinue` instead of being silently dropped.

**Code references:** `HookResult` and `HookResponse` in `hooks/src/types.rs`, dispatch loop in `hooks/src/registry.rs`.


### Apps Improvements

- **`app://` mention scheme.** Prompt rendering for apps now uses `[$app-name](app://{connector_id})` instead of the previous `apps://...`. The TUI also filters out disabled apps when resolving mentions to user input.
- **`isEnabled` flag on `AppInfo`.** The `app/list` response and `app/list/updated` notification now report whether each app is enabled in `config.toml` (e.g. `[apps.bad_app] enabled = false`).
- **`apps_mcp_gateway` feature.** A new under-development feature flag (`apps_mcp_gateway`) routes apps MCP calls through the configured gateway.


### Search Tool BM25 Rewrite

- The `search_tool_bm25` tool description now lives in `core/templates/search_tool/tool_description.md` and is templated with `{{app_names}}`. It is re-framed around "Apps tool discovery" (vs. the previous generic MCP tool discovery), explicitly tells the model not to use it for filesystem/repo search, and notes that explicit `[$app-name](app://{connector_id})` mentions can be called directly without a search.
- The old `developer_instructions.md` template has been removed.


### `js_repl_tools_only` Experimental Mode

- New experimental flag `js_repl_tools_only` (requires `js_repl`) limits the model's tool surface to `js_repl` and `js_repl_reset`. All other tools (including dynamic ones) are filtered out of the model-visible spec, but remain callable indirectly via `codex.tool(name, args?)` from inside `js_repl`. The code automatically disables the flag (with a warning) if `js_repl` itself isn't enabled.

**Code references:** `filter_tools_for_model()` in `core/src/tools/spec.rs`, gating in `core/src/tools/router.rs`.


### Permissions Are First-Class on `Config`

- `Config` now exposes a `permissions: Permissions { approval_policy, sandbox_policy, network, shell_environment_policy, windows_sandbox_mode, macos_seatbelt_profile_extensions }` struct. Existing code that read `config.approval_policy` / `config.sandbox_policy` directly was updated to read `config.permissions.*`. This sets up the unified permission model used by skills, exec commands, and Windows/macOS sandboxes.


### Memory Pipeline Cleanup

- `phase1::run` now takes `&config` so model selection respects the new `[memories].phase_1_model`.
- `phase2::run` replaces the older `dispatch::run_global_memory_consolidation` entry point and reads `[memories].max_raw_memories_for_global` instead of a compile-time constant.
- Memory-consolidation turns are now tagged as a `SubAgentSource::MemoryConsolidation`, so analytics distinguishes them from review/compact/thread-spawn turns.
- New `state` migrations: `0009_stage1_outputs_rollout_slug.sql` adds a `rollout_slug` column for rollout-summary file naming, and `0010_logs_process_id.sql` adds `process_uuid` (with an index) to the logs table.


### Logs CLI

- `logs_client` gained `--search <substring>` for message-text filtering and `--compact` for time/level/message-only output.


### Status Card / Status Indicator

- The status indicator widget no longer schedules animation frames when animations are disabled, eliminating wasted wakeups in headless or test contexts.
- Status cards read `config.permissions.{approval_policy,sandbox_policy}` instead of the now-removed top-level fields.


### `/statusline` Tooltip

- Tooltips list now mentions `/statusline` ("Use /statusline to configure which items appear in the status line.") and the paid/other tooltips link to `https://chatgpt.com/codex?app-landing-page=true`.


### Compaction Robustness

- `extract_trailing_model_switch_update_for_compaction_request()` strips a trailing model-switch developer message before sending the compaction request and re-attaches it after the new history is built. This keeps compaction prompts in-distribution while preserving the model-switch instructions for the next real sampling request.
- Turn-metadata header retrieval moved to `TurnContext::turn_metadata_state.current_header_value()` so it is recomputed per attempt, and `ModelClientSession::ensure_responses_websocket_session` no longer accepts an explicit `turn_metadata_header` parameter.


### Exec Wrapper Compatibility

- `exec-server` now sets both `EXEC_WRAPPER` (the new generic env var) and `BASH_EXEC_WRAPPER` (compatibility alias for older patched bash builds). The escalate client filters both names when rebuilding the child env.


### Feedback Categories

- Added a "safety_check" classification to `feedback/src/lib.rs`, rendered as "Safety check" in the picker and emitted at `Level::Error` in the log snapshot.

### Usage-Limit Header Parsing

- The `UsageLimitReachedError` no longer carries a separate `limit_name` field; it now lives on `RateLimitSnapshot` exclusively. The fallback that previously copied `limit_id` (from the `x-codex-limit-name` / active-limit header) into `limit_name` has been removed — `limit_name` is only populated when the dedicated `x-codex-{slug}-limit-name` header is present. This prevents misreporting the user-facing name when only the internal id is known.

**Code references:** `map_api_error()` in `core/src/api_bridge.rs` and the new test `map_api_error_does_not_fallback_limit_name_to_limit_id`.


### Patch / Exec Approval Receiver Errors

- `on_patch_approval_response()` now distinguishes a transport `Err(_)` from a client-returned `Err(JSONRPCErrorError)`. On a client error it submits an explicit `Op::PatchApproval { decision: Denied }` so the agent stops waiting forever for an approval that will never come.
- `on_exec_approval_response()` similarly handles `ClientRequestResult::Err` without leaving the call hung.


### Status Indicator Animation Loop

- Fixed the status indicator widget always rescheduling a 32 ms frame regardless of whether animations were enabled.


### MCP Tool Filter Helpers

- `filter_codex_apps_mcp_tools_only`, `filter_non_codex_apps_mcp_tools_only`, and `filter_mcp_tools_by_name` now operate on `&HashMap<String, ToolInfo>` and return a fresh map instead of mutating the input. This avoids subtle shared-state bugs when the same tool list is reused by multiple call sites.


### Apps Mention Scheme

- The connector mention link in the apps prompt section was incorrectly rendered as `apps://...` when the rest of the system used `app://...`. The render now matches the canonical scheme.


### File-Search API Surface

- `file_search::create_session` now takes `Vec<PathBuf>` roots, options, reporter, and an optional cancel flag in a single public signature; the previously private `create_session_inner` has been removed and existing callers were migrated. Tests updated to pass the new signature.


### Approval-Policy Prompt Always Includes Escalation Guidance

- Removed the dead `request_rule_enabled` parameter from `DeveloperInstructions::from`/`from_policy`/`from_workspace_write`. The on-request prompt always emits the "How to request escalation" section, including the approved-prefix-rule list when the exec policy has any.

## Internal / Developer Notes

- A new sanity test `default_enabled_features_are_stable` asserts that any feature with `default_enabled = true` is also `Stage::Stable`, preventing accidental shipping of unstable defaults.
- The TUI's `feature_for_key` lookup now exercises both the new `multi_agent` key and the legacy `collab` alias.
- New compact/compact_remote snapshot tests under `core/tests/suite/snapshots/` lock in the rollout shapes for manual compact, mid-turn compaction, pre-turn compaction (context-window-exceeded and including-incoming variants), pre-sampling model-switch compaction, and the remote-compact failure path.
