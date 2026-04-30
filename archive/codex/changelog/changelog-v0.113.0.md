# Changelog for version 0.113.0

## Highlights

This release is unusually structural. Codex now ships an **in-process app-server** that the TUI and `codex exec` both speak to over typed channels instead of stdio JSON-RPC, plus a brand-new **interactive `command/exec` family** with PTY support, stdin streaming, resize, and termination. A **named permissions profile system** replaces the legacy single `[permissions.network]` block and splits sandboxing into explicit filesystem and network policies, while a new **Guardian** subsystem can auto-review on-request approvals so users are not asked to confirm every shell command. The **web search tool**, **plugin marketplace**, and **MCP elicitation** schemas all gain richer typed configuration.


### In-process app-server runtime and shared client crate

**What:** A new `codex-app-server-client` crate lets `codex-tui` and `codex-exec` embed the entire app-server inside the same process and talk to it over bounded `mpsc` channels — no stdio JSON-RPC and no socket boundary.

**Details:**
- The new crate (`codex-rs/app-server-client/src/lib.rs`) exposes `InProcessAppServerClient::start`, which wires up a worker around `codex_app_server::in_process::start` (`codex-rs/app-server/src/in_process.rs`) and runs the JSON-RPC `Initialize` / `Initialized` handshake automatically before returning.
- Typed dispatch: `request()` / `request_typed()` / `notify()` / `resolve_server_request()` / `reject_server_request()` / `next_event()` / `shutdown()`. `TypedRequestError` distinguishes Transport vs. Server vs. Deserialize failures so callers can react appropriately.
- Backpressure surfaces through `InProcessServerEvent::Lagged { skipped }` rather than unbounded growth. `event_requires_delivery()` (`app-server/src/in_process.rs`) keeps terminal events such as `TurnCompleted`, `task_complete`, `turn_aborted`, and `shutdown_complete` from being dropped even when intermediate events are. Saturated server-request queues fail explicitly with `OVERLOADED_ERROR_CODE` so approval flows do not hang.
- Caller-supplied `SessionSource` and `client_name` flow into thread metadata via `InProcessClientStartArgs::initialize_params()` so the TUI and `exec` originator survives `thread/list` and `thread/read`.
- Tracing parity: new `typed_request_span()` in `codex-rs/app-server/src/app_server_tracing.rs` stamps `rpc.transport = "in-process"` so spans line up with the stdio and websocket transports.
- `codex-rs/app-server/src/message_processor.rs::MessageProcessorArgs` now carries `session_source` and `enable_codex_api_key_env` (previously hard-coded to `SessionSource::VSCode` and `false`).

**Why it matters:** The in-process path removes one layer of serialization and process startup from every TUI and exec session. It also unlocks the fully rewritten `exec/src/lib.rs` (see Improvements below), which now drives turns, approvals, and elicitations purely through `ClientRequest` / `ServerRequest` instead of touching `ThreadManager` directly.

**Code references:** `InProcessAppServerClient::start` in `codex-rs/app-server-client/src/lib.rs`, `start()` and `InProcessServerEvent` in `codex-rs/app-server/src/in_process.rs`, `typed_request_span()` in `codex-rs/app-server/src/app_server_tracing.rs`.


### Interactive `command/exec` API with streaming, PTY, resize, and termination

**What:** `command/exec` is now a process-lifecycle API instead of one-shot. Clients can run a command in a real PTY, stream stdout/stderr as base64 deltas, write stdin (including pasting and EOF), resize the terminal, and explicitly terminate.

**Details (new v2 RPC entries under `app-server-protocol/schema/{json,typescript}/v2/`):**
- `command/exec/write` — `CommandExecWriteParams { processId, deltaBase64?, closeStdin? }` writes stdin and/or sends EOF.
- `command/exec/resize` — `CommandExecResizeParams { processId, size: CommandExecTerminalSize }` resizes a PTY in cells.
- `command/exec/terminate` — `CommandExecTerminateParams { processId }` kills a running session.
- `command/exec/outputDelta` — server notification carrying `{ processId, stream: "stdout" | "stderr", deltaBase64, capReached }`.
- `CommandExecParams` gained `processId`, `tty`, `streamStdin`, `streamStdoutStderr`, `outputBytesCap`, `disableOutputCap`, `disableTimeout`, `env`, `size`. When streaming was used, `stdout` / `stderr` on `CommandExecResponse` are empty (the deltas already carried the bytes).

**Implementation:** New module `codex-rs/app-server/src/command_exec.rs` (~1000 lines) introduces `CommandExecManager` keyed by `(connection_id, processId)`.
- `start()` chooses `spawn_pty_process()` (when `tty`), `spawn_pipe_process()` (when `streamStdin`), or `spawn_pipe_process_no_stdin()`. It rejects streaming or PTY without a client `processId`, and rejects streaming and custom `outputBytesCap` under `SandboxType::WindowsRestrictedToken` (falls back to legacy buffered exec there).
- `connection_closed()` automatically terminates every process owned by a JSON-RPC connection when the connection drops, so a client crash cannot leak processes.
- `run_command()` drives the session loop with `tokio::select!` over control messages, expiration (`ExecExpiration::{Timeout, DefaultTimeout, Cancellation}`), and process exit. On timeout it returns `EXEC_TIMEOUT_EXIT_CODE = 124`. After exit it waits up to `IO_DRAIN_TIMEOUT_MS` to drain remaining output before sending the deferred `CommandExecResponse`.
- `spawn_process_output()` per-stream task either emits `ServerNotification::CommandExecOutputDelta` or buffers into the final response, applying `outputBytesCap` truncation and emitting `capReached: true` on the truncating chunk.

**PTY crate reshaped** (`codex-rs/utils/pty`):
- `spawn_pty_process()` in `codex-rs/utils/pty/src/pty.rs` now requires a `size: TerminalSize` argument (replacing a hard-coded 24×80) and returns `SpawnedProcess { session, stdout_rx, stderr_rx, exit_rx }` with split mpsc receivers.
- `ProcessHandle` (`codex-rs/utils/pty/src/process.rs`) gained `resize(TerminalSize)` (calls `MasterPty::resize`), `close_stdin()` (drops the writer to send EOF), and `request_terminate()` (kills the child but leaves reader/writer tasks alive so callers can still drain output).
- New helper `combine_output_receivers()` and a default cap constant `DEFAULT_OUTPUT_BYTES_CAP = 1 MiB`.
- Bug fix on Windows: `WinChild::do_kill()` and `WinChildKiller::kill()` had inverted `TerminateProcess` return-code checks — only `0` is now treated as failure.

**Code references:** `CommandExecManager::start()` and `run_command()` in `codex-rs/app-server/src/command_exec.rs`; `spawn_pty_process()` in `codex-rs/utils/pty/src/pty.rs`; tests in `codex-rs/app-server/tests/suite/v2/command_exec.rs` and `codex-rs/utils/pty/src/tests.rs`.


### Named permissions profiles and split filesystem / network sandbox policies

**What:** A complete redesign of the permissions config. Multiple named profiles can coexist; the active one is selected by a new top-level `default_permissions` key. Sandboxing now exposes filesystem and network policies as independent typed structures rather than one fused `SandboxPolicy`.

**TOML shape** (`codex-rs/core/src/config/permissions.rs`):

```toml
default_permissions = "workspace"

[permissions.workspace]
filesystem = { ":root" = "read", ":project_roots" = "write", ":tmpdir" = "write" }
network    = { default_permissions = "workspace", allowed_domains = ["*.example.com"] }

[permissions.locked_down]
filesystem = ":minimal"
network    = "off"
```

**Details:**
- `PermissionsToml` is now a `BTreeMap<String, PermissionProfileToml>`. When `[permissions]` profiles exist, `default_permissions` is required; missing it fails config load.
- Each profile holds a `filesystem: FilesystemPermissionsToml` and a `network: NetworkToml`. Filesystem entries accept absolute paths, `~/...`, or special tokens `:root`, `:minimal`, `:project_roots`, `:tmpdir`, `:slash_tmp`, `:cwd` (parsed by `parse_special_path()` / `compile_filesystem_permission()`).
- New protocol module `codex-rs/protocol/src/permissions.rs` defines `FileSystemSandboxPolicy` (`Restricted` / `Unrestricted` / `ExternalSandbox`), `FileSystemSandboxEntry`, `FileSystemPath` (`Path` or `Special`), `FileSystemSpecialPath`, `FileSystemAccessMode` (`None` / `Read` / `Write`), and `NetworkSandboxPolicy` (`Restricted` / `Enabled`). `to_legacy_sandbox_policy()` projects these back onto the legacy `SandboxPolicy` so the runtime keeps working during migration.
- `Permissions` (in `codex-rs/protocol/src/approvals.rs`) now carries `file_system_sandbox_policy` and `network_sandbox_policy` next to the legacy `sandbox_policy`.
- Sandbox build paths follow suit: `create_linux_sandbox_command_args_for_policies()` in `codex-rs/core/src/landlock.rs` passes `--file-system-sandbox-policy` and `--network-sandbox-policy` JSON args, and `linux-sandbox/src/linux_run_main.rs::resolve_sandbox_policies()` reconciles the legacy and split policies for the helper.
- `core/src/sandboxing/mod.rs` adds `merge_permission_profiles()`, `intersect_permission_profiles()`, `merge_file_system_policy_with_additional_permissions()`, and `should_require_platform_sandbox()`. `SandboxManager::select_initial()` now takes the split policies.

**Network proxy follow-on:** Network settings now live under `[permissions.<profile>.network]` (with a per-profile `default_permissions = "workspace"`) instead of a top-level `[network]` block. The README in `codex-rs/network-proxy/README.md` was rewritten to match.

**Code references:** `PermissionsToml` and `parse_special_path()` in `codex-rs/core/src/config/permissions.rs`; `FileSystemSandboxPolicy` in `codex-rs/protocol/src/permissions.rs`; `create_linux_sandbox_command_args_for_policies()` in `codex-rs/core/src/landlock.rs`; `merge_permission_profiles()` in `codex-rs/core/src/sandboxing/mod.rs`.


### `request_permissions` tool and approval flow

**What:** The agent can now request additional filesystem (and future) permissions mid-turn. Granted permissions stay valid for the rest of the turn.

**Details:**
- New event variant `EventMsg::RequestPermissions(RequestPermissionsEvent { call_id, turn_id, reason, permissions })` and new `Op::RequestPermissionsResponse { id, response }` (`codex-rs/protocol/src/protocol.rs`, `codex-rs/protocol/src/request_permissions.rs`).
- Two feature flags work together: pre-existing `Feature::RequestPermissions` (the underlying capability) and new `Feature::RequestPermissionsTool` (key `request_permissions_tool`, `Stage::UnderDevelopment`) which exposes the built-in tool.
- New v2 server request `item/permissions/requestApproval` with typed schemas `PermissionsRequestApprovalParams.ts` and `PermissionsRequestApprovalResponse.ts`. Response carries the granted subset in `result.permissions`. Granted permissions are tracked via `GrantedPermissionProfile` and `GrantedMacOsPermissions`.
- TUI integration: `bottom_pane/approval_overlay.rs` adds `ApprovalRequest::Permissions`, `permissions_options()`, `handle_permissions_decision()`, and `format_additional_permissions_rule()`. The overlay shows the reason and the requested rule (e.g. "network; read `/tmp/x`; write `/tmp/y`"). Wired through `chatwidget.rs::on_request_permissions()` and `app.rs` (which renders the "P E R M I S S I O N S" header).

**Test:** `request_permissions_round_trip` in `codex-rs/app-server/tests/suite/v2/request_permissions.rs`.

**Code references:** `RequestPermissionsEvent` in `codex-rs/protocol/src/request_permissions.rs`; `permissions_options()` in `codex-rs/tui/src/bottom_pane/approval_overlay.rs`.


### Guardian: automatic approval review subagent

**What:** A new automated approval-review subsystem. When the new `Feature::GuardianApproval` is enabled and the approval policy is `OnRequest`, escalations that would normally prompt the user are routed to a "guardian" subagent that fails closed.

**Details (new files: `codex-rs/core/src/guardian.rs`, `guardian_prompt.md`, `guardian_tests.rs`, `codex_tests_guardian.rs`):**
- `routes_approval_to_guardian()` gates routing on `Feature::GuardianApproval` plus `AskForApproval::OnRequest`.
- `review_approval_request()` / `run_guardian_review()` are the public entry points; they emit a `WarningEvent` with verdict and timing.
- `GuardianApprovalRequest` covers `Shell`, `ExecCommand`, `Execve` (Unix), `ApplyPatch`, `NetworkAccess`, and `McpToolCall` — every on-request escalation surface.
- `run_guardian_subagent()` spawns a one-shot subagent via `run_codex_thread_interactive()` with `SubAgentSource::Other("guardian")`, prefers model `gpt-5.4` (`GUARDIAN_PREFERRED_MODEL`), reasoning effort `Low`, with a 90s timeout (`GUARDIAN_REVIEW_TIMEOUT`).
- `build_guardian_subagent_config()` locks the subagent down to read-only sandbox, `AskForApproval::Never`, disables `Collab`/`WebSearchRequest`/`WebSearchCached`, refreshes managed-network proxy/allowlist from live runtime, and copies session-scoped network approvals.
- `GuardianAssessment` (`risk_level`, `risk_score`, `rationale`, `evidence[]`) is enforced with a JSON schema; the guardian approves only if `risk_score < 80` (`GUARDIAN_APPROVAL_RISK_THRESHOLD`).
- Transcript construction (`collect_guardian_transcript_entries()`) keeps every user message plus up to 40 recent non-user entries, budgeted to 10,000 tokens for messages and 10,000 separate tokens for tool evidence. `guardian_truncate_text()` produces `<guardian_truncated omitted_approx_tokens=".." />` markers.
- On rejection the agent receives `GUARDIAN_REJECTION_MESSAGE` telling it not to retry by workaround.

**Why it matters:** This is the missing piece that lets `OnRequest` approval mode run unattended on a trusted-but-not-blanket-yes setup — the guardian sees the same evidence the user would but resolves quickly.

**Code references:** `routes_approval_to_guardian()`, `run_guardian_review()`, `build_guardian_subagent_config()`, and `GuardianAssessment` in `codex-rs/core/src/guardian.rs`.


### Plugin marketplace: list, install, uninstall

**What:** A first cut of a plugin marketplace surface. Codex can now discover plugins from per-cwd marketplace files plus a curated `openai/plugins` repo, install or uninstall them, and surface rich UI metadata.

**Details:**
- New v2 RPC methods: `plugin/list`, `plugin/install`, `plugin/uninstall`.
- `PluginListParams { cwds? }` -> `PluginListResponse { marketplaces: PluginMarketplaceEntry[] }`. Each marketplace exposes `name`, `path`, and a list of `PluginSummary { id, name, source, installed, enabled, interface }`. New TS types: `PluginInterface.ts`, `PluginMarketplaceEntry.ts`, `PluginSource.ts`, `PluginSummary.ts`, `AppSummary.ts`.
- `PluginInstallParams` was redesigned from `{ marketplaceName, pluginName, cwd }` to `{ marketplacePath: AbsolutePathBuf, pluginName }` — install now targets a specific marketplace file by absolute path. `PluginInstallResponse` now returns `appsNeedingAuth: AppSummary[]` so the UI can surface which apps still need OAuth after install.
- `PluginUninstallParams { pluginId }` plus the new `PluginsManager::uninstall_plugin()` and `PluginStore::uninstall()` (`codex-rs/core/src/plugins/{manager,store}.rs`). Uninstall removes cached files and strips the `plugins.<id>` config key.
- Curated repo auto-sync (`codex-rs/core/src/plugins/curated_repo.rs`): clones `https://github.com/openai/plugins.git` shallow into `<codex_home>/.tmp/plugins`, gated by an `ls-remote` SHA file, with 30s timeout and atomic rename + rollback. Honors `CODEX_DISABLE_CURATED_PLUGIN_SYNC` and is wired in via `PluginsManager::start_curated_repo_sync()` and `maybe_start_curated_repo_sync_for_config()`.
- Plugin manifest (`PluginManifest` in `manifest.rs`) gained a full `interface` block: `displayName`, `shortDescription`, `longDescription`, `developerName`, `category`, `capabilities[]`, `websiteUrl`, `privacyPolicyUrl`, `termsOfServiceUrl`, `defaultPrompt`, `brandColor`, `composerIcon`, `logo`, `screenshots[]`. Asset paths must use a `./` prefix and stay inside the plugin root (`resolve_manifest_path()`).
- TUI integration: `chat_composer.rs::set_plugin_mentions()` accepts `Vec<PluginCapabilitySummary>`. Plugins appear in the `$`-prefixed mention popup with capability labels ("Plugin · skills · 1 MCP server · 2 apps") and `plugin://name@marketplace` paths. `mention_codec.rs::parse_history_linked_mention()` decodes both `[$name](plugin://...)` and `[@name](plugin://...)` forms.

**Code references:** `PluginsManager::list_marketplaces_for_config()` and `uninstall_plugin()` in `codex-rs/core/src/plugins/manager.rs`; `marketplace::list_marketplaces()` in `codex-rs/core/src/plugins/marketplace.rs`; `start_curated_repo_sync()` in `codex-rs/core/src/plugins/curated_repo.rs`.


### MCP elicitation: typed schemas and rich form overlay

**What:** MCP elicitation requests are now strongly typed and rendered in a dedicated form overlay (with select/text/secret fields) rather than a free-text approval prompt.

**Details:**
- `McpServerElicitationRequestParams.requestedSchema` is now the typed `McpElicitationSchema` (object with primitive properties: `string` / `number` / `boolean` / enum). New TS types under `app-server-protocol/schema/typescript/v2/`: `McpElicitationSchema`, `McpElicitationStringSchema`, `McpElicitationStringFormat` (`email | uri | date | date-time`), `McpElicitationNumberSchema`, `McpElicitationBooleanSchema`, `McpElicitationEnumSchema` (single-select / multi-select / titled / untitled / legacy-titled variants), `McpElicitationConstOption`, `McpElicitationTitledEnumItems`, `McpElicitationUntitledEnumItems`.
- `ElicitationRequest::Form` and `Url` gained an `_meta: Option<JsonValue>` for client-side action handling, and `ElicitationRequestEvent` gained `turn_id` for correlation. `Op::ElicitationResponse` gained `meta: Option<Value>` for round-tripping client metadata.
- New feature flag `Feature::ToolCallMcpElicitation` (key `tool_call_mcp_elicitation`, `Stage::UnderDevelopment`) routes MCP tool-approval prompts through this elicitation path.
- TUI: new file `codex-rs/tui/src/bottom_pane/mcp_server_elicitation.rs` (~2000 lines) introduces `McpServerElicitationOverlay` and `McpServerElicitationFormRequest::from_event()`. Renders structured fields with persist options (once / session / always). When an `ElicitationRequest` has a parseable schema it is routed to this overlay; otherwise it falls back to the legacy approval overlay (`chatwidget.rs::on_mcp_elicitation`).

**Code references:** `McpElicitationSchema` in `codex-rs/app-server-protocol/schema/typescript/v2/McpElicitationSchema.ts`; `McpServerElicitationOverlay` in `codex-rs/tui/src/bottom_pane/mcp_server_elicitation.rs`.


### `Esc` to flush pending steers immediately

**What:** While a turn is running and you have queued follow-up messages, pressing `Esc` now interrupts the turn and submits all pending steers as a single immediate message.

**Details:**
- `chatwidget.rs` gained a `submit_pending_steers_after_interrupt: bool` flag. On `Esc` with queued steers it emits `Op::Interrupt` and merges the queue into one submission via the new `merge_user_messages()`.
- `pending_input_preview.rs` replaced the old `pending steer:` prefix with labeled section headers — "Messages to be submitted after next tool call (press Esc to interrupt and send immediately)" vs. "Queued follow-up messages".

**Code references:** `merge_user_messages()` and `submit_pending_steers_after_interrupt` in `codex-rs/tui/src/chatwidget.rs`.


### Login file logging

**What:** All four login flows now write a per-user `codex-login.log` (mode `0600` on Unix) with tracing for `codex_cli` / `codex_core` / `codex_login` so login failures can be diagnosed after the fact.

**Code references:** `init_login_file_logging()` in `codex-rs/cli/src/login.rs`.


### Status-line live preview

**What:** The status-line setup screen now previews real runtime values (model, fast-mode state, context-window usage) instead of static placeholders, and refreshes on `TurnStarted`.

**Details:**
- `codex-rs/tui/src/bottom_pane/status_line_setup.rs` introduces `StatusLinePreviewData` (a `BTreeMap` of runtime values) and a new `StatusLineItem::FastMode` ("Fast on/off"). `chatwidget.rs::open_status_line_setup()` feeds real runtime values; `app.rs::apply_turn_started_context_window()` triggers a refresh on every turn start.

**Code references:** `StatusLinePreviewData` in `codex-rs/tui/src/bottom_pane/status_line_setup.rs`.


### Web search tool config object

**What:** `[tools].web_search` is no longer a boolean; it is a configurable object that accepts allowed domains, context size, and a user location.

**Details:**
- `ToolsToml.web_search` changed from `Option<bool>` to `Option<WebSearchToolConfig>` (`codex-rs/core/src/config/mod.rs`).
- New types in `codex-rs/protocol/src/config_types.rs`: `WebSearchToolConfig { context_size, allowed_domains, location }`, `WebSearchContextSize` (`Low` / `Medium` / `High`), `WebSearchLocation { country, region, city, timezone }`, and supporting `WebSearchUserLocation` / `WebSearchFilters` / `WebSearchConfig` with `merge()` methods.
- `Config` gained `web_search_config: Option<WebSearchConfig>` resolved via `resolve_web_search_config()`.
- `ProfileV2` gained `tools: Option<ToolsV2>` so the V2 protocol can carry the typed config.

**Example:**

```toml
[tools.web_search]
context_size = "high"
allowed_domains = ["*.openai.com", "*.example.com"]

[tools.web_search.location]
country  = "US"
region   = "CA"
city     = "San Francisco"
timezone = "America/Los_Angeles"
```

**Code references:** `WebSearchToolConfig` in `codex-rs/protocol/src/config_types.rs`; `resolve_web_search_config()` in `codex-rs/core/src/config/mod.rs`.


### Memories: stale Phase-1 entries are pruned at startup

**What:** Stale Phase-1 memories that were never selected for Phase-2 are now garbage-collected at session startup so the local DB does not grow unbounded.

**Details:**
- New `prune()` in `codex-rs/core/src/memories/phase1.rs` calls `db.prune_stage1_outputs_for_retention(max_unused_days, PRUNE_BATCH_SIZE)` and logs the pruned row count.
- New constant `PRUNE_BATCH_SIZE = 200` in `codex-rs/core/src/memories/mod.rs`.
- New DB method `prune_stage1_outputs_for_retention()` in `codex-rs/state/src/runtime/memories.rs` deletes only rows where `selected_for_phase2 = 0` and `COALESCE(last_usage, source_updated_at)` is older than `max_unused_days`, ordered stalest-first and capped by `limit` — preserving the latest Phase-2 baseline and watermarks.
- Wired into `start_memories_startup_task` in `codex-rs/core/src/memories/start.rs`: `phase1::prune()` runs before `phase1::run()` and `phase2::run()`.

**Code references:** `prune()` in `codex-rs/core/src/memories/phase1.rs`; `prune_stage1_outputs_for_retention()` in `codex-rs/state/src/runtime/memories.rs`.


### `codex exec` rewritten on the in-process app-server

`exec/src/lib.rs` no longer touches `ThreadManager` or constructs `Op::*` directly. Instead it drives turns through `InProcessAppServerClient` and JSON-RPC requests (`ThreadStart`, `ThreadResume`, `TurnStart`, `ReviewStart`, `TurnInterrupt`, `ThreadUnsubscribe`). New helpers `RequestIdSequencer`, `handle_server_request()`, `decode_legacy_notification()`, `canceled_mcp_server_elicitation_response()`, and `local_external_chatgpt_tokens()` keep `exec` symmetric with the TUI. Approvals (exec / patch / permissions / user-input / dynamic tool calls) are auto-rejected with explicit unsupported messages, and MCP elicitations auto-cancel.

`event_processor_with_human_output.rs::ImageGenerationEnd` now prints the generated `result` inline if it is not a `data:` or `url` value, matching how the TUI renders results.


### Thread name updates broadcast over WebSocket

`thread/name/set` now emits `thread/name/updated` to every initialized opted-in client, including not-loaded threads. New tests in `codex-rs/app-server/tests/suite/v2/thread_name_websocket.rs` (`thread_name_updated_broadcasts_for_loaded_threads`, `thread_name_updated_broadcasts_for_not_loaded_threads`) and helper utilities `read_notification_for_method()` / `read_response_and_notification_for_method()` cover both shapes.


### Realtime conversations re-inject startup context on reconnect

`tests/suite/v2/realtime_conversation.rs` now asserts that the first WS frame contains a `session.update` carrying `STARTUP_CONTEXT_HEADER = "Startup context from Codex."`. A new `experimental_realtime_ws_startup_context` config knob controls this. The `app-server` Cargo dependencies pulled in `sse-stream` and `thiserror 2.0.18` for the new realtime plumbing.


### Skill-triggered approvals carry their script path

`ExecApprovalRequestEvent` and `CommandExecutionRequestApprovalParams` gained an optional `skill_metadata: { path_to_skills_md }` field (new `ExecApprovalRequestSkillMetadata` struct in `codex-rs/protocol/src/approvals.rs`) so the UI can label approvals coming from skill scripts.


### Image generation results report the saved path

`ImageGenerationItem` and `ImageGenerationEndEvent` gained `saved_path?: string`. `history_cell.rs::new_image_generation_call()` dropped its `status` parameter and gained an optional `saved_to` parameter (renders `Saved to: <dir>` line); the header changed from `Generated Image` to `Generated Image:`.


### `applyPatchApproval` decisions and unstable `grantRoot`

The apply-patch approval response now accepts `acceptForSession` and `cancel` decisions in addition to the existing accept/reject, and an unstable `grantRoot` field. `Permissions` (the approval struct) now carries the new split `file_system_sandbox_policy` and `network_sandbox_policy`.


### macOS sandbox: unreadable carveouts and bundle-ID intersection

- `core/src/seatbelt.rs::build_seatbelt_access_policy()` introduces `SeatbeltAccessRoot` and emits `(require-not (subpath ...))` exclusion clauses for both `file-read*` and `file-write*` rules. `create_seatbelt_command_args_for_policies_with_extensions()` is the new primary entry; `create_seatbelt_command_args_with_extensions()` becomes a wrapper.
- `dynamic_network_policy_for_network()` now fail-closes when proxy config or managed-network is requested but no usable endpoints exist.
- `core/src/sandboxing/macos_permissions.rs` adds `intersect_macos_seatbelt_profile_extensions()` and `intersect_macos_automation_permission()` (e.g. bundle-ID intersection).
- `MacOsAutomationPermission` now also accepts `{"bundle_ids": [...]}` object form, and `MacOsSeatbeltProfileExtensions` accepts old field aliases (`preferences` / `automations` / `accessibility` / `calendar`).


### Linux sandbox: explicit deny carveouts and reordered mounts

`linux-sandbox/src/bwrap.rs` adds `BwrapArgs { args, preserved_files }`. `create_filesystem_args()` now applies `unreadable_roots` carveouts: directories get `--perms 000 --tmpfs <path> --remount-ro <path>` masking; files get `--ro-bind-data <fd-of-/dev/null>` (the `preserved_files` list keeps the fd open across `exec`). Mount order changed: writable binds before `/dev` re-mount; deny carveouts last.


### Windows sandbox helper-binary materialization

`windows-sandbox-rs/src/helper_materialization.rs::resolve_current_exe_for_launch()` (re-exported from `lib.rs`) copies the current Codex binary into the helper-bin directory for sandbox launch, falling back to the original path on copy failure. `WindowsSandboxSetupStartParams.cwd` schema is now nullable `AbsolutePathBuf` instead of a raw nullable string.


### Cloud requirements: 401-aware retry

`codex-rs/cloud-requirements/src/lib.rs` adds `FetchCloudRequirementsError::Unauthorized` which triggers `auth_manager.unauthorized_recovery()` and re-fetches with the refreshed token. Failures surface a user-visible "sign in again" message instead of a raw HTTP 401.


### Managed config: `managed_allowed_domains_only` and expansion controls

- `config/src/config_requirements.rs` and `core/src/config/network_proxy_spec.rs`: `NetworkRequirementsToml` and `NetworkConstraints` add a new `managed_allowed_domains_only: Option<bool>`. When `true`, user `allowed_domains` are ignored and `NetworkProxySpec` enforces this via the new `hard_deny_allowlist_misses` flag plus `merge_domain_lists()` and `allowlist_expansion_enabled()`.
- `network-proxy/src/state.rs::NetworkProxyConstraints` adds two new options: `allowlist_expansion_enabled: Option<bool>` and `denylist_expansion_enabled: Option<bool>`. `Some(true)` lets the user add hosts beyond the managed baseline (must still contain it); `Some(false)` requires exact match; `None` keeps prior subset-of-pattern behavior.


### OTel: `OtelManager` renamed to `SessionTelemetry`; PII split between logs and traces

- All public surface renamed: `OtelManager` → `SessionTelemetry`, `OtelEventMetadata` → `SessionTelemetryMetadata`. `events/session_telemetry.rs` (moved from `traces/otel_manager.rs`) defines them; the `traces/` directory was removed. All metric and event helpers (`counter`, `histogram`, `record_duration`, `start_timer`, `shutdown_metrics`, `snapshot_metrics`, `runtime_metrics_summary`, `with_metrics*`, `with_provider_metrics`, `new`) moved onto `SessionTelemetry` with unchanged signatures. `SessionTelemetry::new()` gains an `originator: String` parameter.
- New tracing-target routing splits logs vs traces. `targets.rs` introduces `OTEL_LOG_ONLY_TARGET = "codex_otel.log_only"` and `OTEL_TRACE_SAFE_TARGET = "codex_otel.trace_safe"` plus `is_log_export_target()` / `is_trace_safe_target()`. New macros `log_event!`, `trace_event!`, `log_and_trace_event!` route to those targets. PII fields (full prompt text, command arguments, output, `user.email`, `user.account_id`, `mcp_server`) go only to logs; traces receive sanitized counts/lengths (`prompt_length`, `text_input_count`, `image_input_count`, `arguments_length`, `output_length`, `output_line_count`, `tool_origin`).
- Resource attributes differ by signal kind: `resource_attributes()` accepts a `ResourceKind` (`Logs` or `Traces`); `host.name` is now attached only to log exports, not traces.
- New turn-level metric names in `metrics/names.rs`: `codex.turn.e2e_duration_ms`, `codex.turn.ttft.duration_ms`, `codex.turn.ttfm.duration_ms`, plus `TURN_TOOL_CALL_METRIC`, `TURN_TOKEN_USAGE_METRIC`, `THREAD_STARTED_METRIC`. `RuntimeMetricsSummary` gained `turn_ttft_ms` and `turn_ttfm_ms` fields with corresponding handling in `from_snapshot()` / `merge()` / `is_empty()`.
- New `metrics/tags.rs` centralizes `SessionMetricTagValues` and the `APP_VERSION_TAG` / `AUTH_MODE_TAG` / `MODEL_TAG` / `ORIGINATOR_TAG` / `SERVICE_NAME_TAG` / `SESSION_SOURCE_TAG` constants.


### Resume picker default sort

`resume_picker.rs` default `sort_key` swapped from `CreatedAt` to `UpdatedAt` so the most recently active threads appear first.


### Windows: `TerminateProcess` return-code check inverted

`WinChild::do_kill()` and `WinChildKiller::kill()` in `codex-rs/utils/pty/src/win/mod.rs` had inverted checks against `TerminateProcess`'s return code — non-zero is success, but the prior code treated non-zero as failure. Fixed: only `0` is now treated as failure.


### App-server WebSocket initialize ordering

`MessageProcessor::process_client_request()` and `connection_initialized()` / `send_initialize_notifications_to_connection()` (`codex-rs/app-server/src/message_processor.rs`) were refactored to defer outbound-ready until per-connection notifications fire, fixing a subtle timing issue where a websocket client could miss initialize-time notifications.


### Network proxy: rejects `*` domain patterns

`compile_globset()` (`codex-rs/network-proxy/src/policy.rs`) now returns an error when any pattern expands to `*` (caught via the new `is_global_wildcard_domain_pattern()`), and `validate_policy_against_constraints()` runs `validate_domain_patterns()` against both `allowed_domains` and `denied_domains`. Previously a stray `"*"` (or `"[*]"`, `"**.[*]"`) would silently allow or deny everything. The `DomainPattern::Any` variant was removed.


### Network proxy: `allow_local_binding` default flipped to safe value

`NetworkProxySettings::default()` (`codex-rs/network-proxy/src/config.rs`) now sets `allow_local_binding = false`. Local and private-range targets are blocked unless explicitly allowlisted. Users who relied on the prior `true` default must opt in.


### Trust-screen logic simplified

`lib.rs::should_show_trust_screen()` no longer respects the (now-removed) `did_user_set_custom_approval_policy_or_sandbox_mode` field, and only checks `trust_level`. This avoids a class of cases where the trust screen reappeared unexpectedly after a user had configured custom approval settings.


## Removals and Breaking Changes

These break external integrations:

- **Network proxy admin HTTP API removed.** The whole admin server (defaulted at `127.0.0.1:8080`) is gone, including `/health`, `/config`, `/patterns`, `/blocked`, `POST /mode`, `POST /reload`. `codex-rs/network-proxy/src/admin.rs` was deleted. `NetworkProxyBuilder::admin_addr()`, `NetworkProxy::admin_addr()`, `RuntimeConfig::admin_addr`, `NetworkProxySettings::admin_url`, `dangerously_allow_non_loopback_admin`, and the matching constraint field are all removed. Operators relying on `curl http://127.0.0.1:8080/...` must migrate. `SessionNetworkProxyRuntime` lost `admin_addr` from its TS schema.
- **Network config moved.** Settings now live under `[permissions.<profile>.network]` with `default_permissions = "workspace"` instead of a top-level `[network]` block.
- **`Feature::Sqlite` is now `Removed`** (was `Stable`).
- **Legacy `[tools].web_search` boolean removed.** `LegacyFeatureToggles::tools_web_search` and the alias path in `core/src/features/legacy.rs` and `managed_features.rs` are gone — use the new `WebSearchToolConfig` object.
- **`Config.did_user_set_custom_approval_policy_or_sandbox_mode` field removed.**
- **`MacOsPermissions` / `MacOsPreferencesValue` / `MacOsAutomationValue` types removed** from `codex-rs/protocol/src/models.rs`.
- **`PluginInstallParams` reshape:** callers must pass `marketplacePath: AbsolutePathBuf` + `pluginName` instead of `marketplaceName` + `pluginName` + `cwd`. The `DuplicatePlugin` error is gone — duplicates now silently take the first entry.
- **`StateRuntime::init` and `get_state_db` lost their trailing `None` parameter.** External callers must drop that argument (see `cli/src/main.rs`, `cli/tests/debug_clear_memories.rs`, `core/tests/suite/memories.rs`).
- **`SandboxPermissions` helper rename:** `requires_additional_permissions()` -> `requests_sandbox_override()`, with a new `uses_additional_permissions()` (`codex-rs/protocol/src/models.rs`).
- **`OtelManager` -> `SessionTelemetry`** across all callers (constructor adds an `originator` argument).


## Workspace

- Workspace version bumped to `0.113.0` (`codex-rs/Cargo.toml`).
- New crates added to the workspace: `codex-app-server-client` (`codex-rs/app-server-client`).
- `codex-otel` removed as a dependency from `codex-rs/state/Cargo.toml`.
- New nextest test groups `app_server_protocol_codegen` and `app_server_integration` (single-threaded) added in `codex-rs/.config/nextest.toml` to keep schema-codegen and `app-server` integration tests deterministic.
