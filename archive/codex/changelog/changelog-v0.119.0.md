# Changelog for version 0.119.0

## Highlights

Codex 0.119.0 is a sweeping release. The biggest user-visible additions are a **WebRTC voice transport** for realtime conversations (with a configurable voice palette), a new **Remote Control** outbound transport that lets ChatGPT drive a local Codex app-server over a persistent WebSocket, and a substantially overhauled **Guardian** auto-approval reviewer that now returns an explicit allow/deny verdict plus a four-tier risk model. Under the hood, configuration moves into a dedicated `codex-config` crate (introducing a structured `[permissions]` profile system, a `[realtime]` block, and JSON-schema-validated `[features]`), MCP code is extracted into a new `codex-mcp` crate (with a new `mcp resources/read` JSON-RPC method), and the TUI gains an OSC-52-aware clipboard pipeline backed by a new `Ctrl+O` hotkey.

### WebRTC realtime voice transport

**What:** Codex now supports running its realtime voice conversations over WebRTC in addition to WebSocket. WebRTC offers significantly lower-latency audio because the peer connection handles audio I/O locally instead of streaming PCM frames over a WebSocket.

**Details:**

- A new workspace crate `codex-realtime-webrtc` wraps `libwebrtc`. `RealtimeWebrtcSession::start()` in `realtime-webrtc/src/lib.rs` returns a `StartedRealtimeWebrtcSession { offer_sdp, handle, events }`. The peer connection is configured for SendRecv audio (`offer_to_receive_audio: true`) using a `realtime-mic` track.
- WebRTC transport is **macOS-only at runtime**: on Linux/Windows the session immediately returns `RealtimeWebrtcError::UnsupportedPlatform` (`realtime-webrtc/src/native.rs`).
- Local audio peak metering is implemented via `start_local_audio_level_task()` polling `peer_connection.get_stats()` every 200 ms, surfaced through `RealtimeWebrtcEvent::LocalAudioLevel(u16)`.
- A new HTTP endpoint client `RealtimeCallClient::create()` / `create_with_session()` in `codex-api/src/endpoint/realtime_call.rs` posts the SDP offer to `realtime/calls` either as `application/sdp` or as a `multipart/form-data` bundle including a JSON `session` blob; `decode_call_id_from_location()` parses the resulting `rtc_…` call id.
- The companion sideband is established via `connect_webrtc_sideband()` in `codex-api/src/endpoint/realtime_websocket/methods.rs`, which appends `?call_id=rtc_…` to the WebSocket URL.

**Configuration:**

A new `[realtime]` table in `config.toml`:

```toml
[realtime]
version = "v2"
transport = "webrtc"   # or "websocket"
voice = "cedar"
```

`RealtimeTransport` (in `codex-config/src/config_toml.rs`) defaults to `WebRtc` and accepts `"webrtc"` or `"websocket"`.

**Code references:**

- `RealtimeWebrtcSession::start()` in `realtime-webrtc/src/lib.rs`
- `RealtimeCallClient::create_with_session()` in `codex-api/src/endpoint/realtime_call.rs`
- `RealtimeConversationManager::start()` in `core/src/realtime_conversation.rs`
- TUI integration in `tui/src/chatwidget/realtime.rs` (`RealtimeConversationUiTransport::Webrtc`, `start_realtime_webrtc_offer_task()`, `on_realtime_conversation_sdp()`)


### Configurable realtime voices

**What:** A first-class voice palette for realtime conversations, replacing the previously hard-coded `Marin` / `Fathom` defaults.

**Details:**

- New `RealtimeVoice` enum with 19 voices: `alloy, arbor, ash, ballad, breeze, cedar, coral, cove, echo, ember, juniper, maple, marin, sage, shimmer, sol, spruce, vale, verse`.
- Voice list is split per-version: `RealtimeVoicesList::builtin()` provides a v1 palette (Juniper/Maple/Spruce/Ember/Vale/Breeze/Arbor/Sol/Cove, default `Cove`) and a v2 palette (Alloy/Ash/Ballad/Coral/Echo/Sage/Shimmer/Verse/Marin/Cedar, default `Marin`).
- A new JSON-RPC method `thread/realtime/listVoices` returns `ThreadRealtimeListVoicesResponse { voices }` so client UIs can populate a voice picker dynamically.
- The session config validator `validate_realtime_voice()` in `core/src/realtime_conversation.rs` rejects voices that aren't in the chosen version's palette.

**Code references:**

- `RealtimeVoicesList::builtin()` in `app-server-protocol/src/protocol/v2.rs` (also exported as `RealtimeVoice.ts` / `RealtimeVoicesList.ts`)
- `default_realtime_voice()` and `validate_realtime_voice()` in `core/src/realtime_conversation.rs`
- `session_update_session()` now takes a `voice: RealtimeVoice` argument in `codex-api/src/endpoint/realtime_websocket/methods_v2.rs` and `methods_v1.rs`


### Remote Control transport (outbound app-server)

**What:** A new transport for `codex app-server` that **dials out** to ChatGPT and stays connected as a "remote control server," letting ChatGPT (web/mobile) drive an agent running on the user's machine without exposing a local port. Rather than `--listen` waiting for incoming connections, the local server enrolls itself with `chatgpt.com`/`chatgpt-staging.com` and proxies JSON-RPC traffic between cloud-side clients and local handlers.

**Details:**

- Off by default. Enabled via the new `remote_control` feature flag (`Feature::RemoteControl`, key `remote_control`, stage `UnderDevelopment`). It is dynamically toggleable — `RemoteControlHandle::set_enabled()` is invoked on config reload.
- Auth piggybacks on existing ChatGPT login: `load_remote_control_auth()` requires `auth.is_chatgpt_auth()` with an `account_id`. **API-key auth is explicitly rejected** with the message "remote control requires ChatGPT authentication; API key auth is not supported."
- Enrollment hits `<base>/wham/remote/control/server/enroll` with the user's bearer token, sending `{name, os, arch, app_server_version}`; the server returns `{server_id, environment_id}`.
- The persistent WebSocket connects to `<base>/wham/remote/control/server` carrying `x-codex-server-id`, base64-encoded `x-codex-name`, `x-codex-protocol-version: 2`, and an optional `x-codex-subscribe-cursor` for stream resume.
- URL targets are restricted by `normalize_remote_control_url()` to HTTPS on `chatgpt.com` / `chatgpt-staging.com` (and subdomains) or HTTP/HTTPS on localhost. Anything else is rejected.
- A simple framed protocol carries `ClientEvent::ClientMessage`, `Ack`, `Ping`, `ClientClosed` and `ServerEvent::ServerMessage`, `Ack`, `Pong{status}`. A `BoundedOutboundBuffer` retains unacked envelopes so reconnects can resume from a cursor. WebSocket pings fire every 10 s with a 60 s pong timeout.
- Idle clients are reaped after 10 minutes (`REMOTE_CONTROL_CLIENT_IDLE_TIMEOUT`).
- Persisted in a new SQL table by migration `0024_remote_control_enrollments.sql`, keyed by `(websocket_url, account_id, app_server_client_name)` so re-enrollment isn't required across restarts. Account-id mismatches invalidate cached enrollments.

**Code references:**

- `start_remote_control()`, `RemoteControlHandle::set_enabled()` in `app-server/src/transport/remote_control/mod.rs`
- `enroll_remote_control_server()` in `app-server/src/transport/remote_control/enroll.rs`
- `RemoteControlWebsocket::run()`, `load_remote_control_auth()`, `BoundedOutboundBuffer` in `app-server/src/transport/remote_control/websocket.rs`
- `normalize_remote_control_url()`, `ClientEnvelope`/`ServerEnvelope` in `app-server/src/transport/remote_control/protocol.rs`
- `state/migrations/0024_remote_control_enrollments.sql`, accessors in `state/src/runtime/remote_control.rs`


### `mcp resources/read` JSON-RPC method

**What:** Codex clients can now read MCP resources (text or binary) directly through the app-server protocol, rather than only invoking tools.

**Details:**

- New JSON-RPC method with params `{threadId, server, uri}` and response `{resources: ResourceContent[]}`. `ResourceContent` is either `Text { uri, mimeType, text, _meta }` or `Blob { uri, mimeType, blob, _meta }`.
- Lets a UI surface MCP-served documents (e.g. fetch a remote PDF or markdown resource) without first asking the agent to call a tool.
- The integration test `app-server/tests/suite/v2/mcp_resource.rs` exercises both text and binary resource reads against a Streamable HTTP MCP server.

**Code references:**

- `McpResourceReadParams` / `McpResourceReadResponse` in `app-server-protocol/src/protocol/v2.rs` (and TypeScript exports under `schema/typescript/v2/`)
- `app-server/tests/suite/v2/mcp_resource.rs`


### MCP server status filtering

**What:** Clients can now list MCP server status with a coarser detail level to avoid pulling the full tool catalog on every poll.

**Details:**

- `ListMcpServerStatusParams` gains a `detail` field with values `"full"` or `"toolsAndAuthOnly"`, exposed via the new `McpServerStatusDetail` enum.
- `app-server/tests/suite/v2/mcp_server_status.rs` validates pagination/detail filtering.

**Code references:**

- `McpServerStatusDetail` in `app-server-protocol/schema/typescript/v2/McpServerStatusDetail.ts`


### Apps SDK file-parameter bridging for MCP tools

**What:** When ChatGPT-hosted MCP "Apps" tools declare `_meta["openai/fileParams"]`, Codex now uploads the local file paths the agent passes and rewrites those arguments into the upload-aware payload the Apps SDK expects.

**Details:**

- New file `core/src/mcp_openai_file.rs` (~470 lines) implements `rewrite_mcp_tool_arguments_for_openai_files`. At execution time it scans declared file param paths, calls `codex_api::upload_local_file`, and substitutes `{download_url, file_id, mime_type, file_name, uri, file_size_bytes}` for the raw path string.
- Requires ChatGPT auth (the upload uses the user's session).

**Code references:**

- `rewrite_mcp_tool_arguments_for_openai_files()` in `core/src/mcp_openai_file.rs`


### Tool exposure thresholding for large MCP catalogs

**What:** When a session has 100+ MCP tools available and the search tool is on, Codex automatically defers most tools (loaded on demand via `tool_search`) and only exposes "directly enabled" connectors up front. This cuts model context use when many MCP servers are connected.

**Details:**

- New module `core/src/mcp_tool_exposure.rs` introduces `DIRECT_MCP_TOOL_EXPOSURE_THRESHOLD = 100` and `build_mcp_tool_exposure(...)` returning `McpToolExposure { direct_tools, deferred_tools }`.
- `filter_codex_apps_mcp_tools()` restricts Codex Apps tools to allowed connector ids, with the per-originator denylist managed in the new `utils/plugins/src/mcp_connector.rs`.

**Code references:**

- `build_mcp_tool_exposure()` in `core/src/mcp_tool_exposure.rs`
- `is_connector_id_allowed()` / `is_connector_id_allowed_for_originator()` in `utils/plugins/src/mcp_connector.rs`


### Centralized tool registry plan

**What:** Tool selection and handler registration are now driven by a single declarative `ToolRegistryPlan`, replacing scattered ad-hoc registration logic across the core crate.

**Details:**

- The plan combines `specs: Vec<ConfiguredToolSpec>` (the tools the model sees) with `handlers: Vec<ToolHandlerSpec>` keyed by a 32-variant `ToolHandlerKind` enum (Shell, ApplyPatch, Plan, JsRepl, ToolSearch, ToolSuggest, FollowupTaskV2, McpResource, ViewImage, …).
- A single function `build_tool_registry_plan()` (~560 lines) consumes a `ToolsConfig` plus `ToolRegistryPlanParams` and produces the full plan, including a code-mode-nested variant via `config.for_code_mode_nested_tools()` and `augment_tool_spec_for_code_mode()`.
- The `tools` crate is now the canonical home for tool specs, configuration, and search/suggest helpers; `core/src/tools/handlers/*` become thin invocation wrappers.

**Code references:**

- `build_tool_registry_plan()` in `tools/src/tool_registry_plan.rs`
- `ToolRegistryPlan`, `ToolHandlerSpec`, `ToolHandlerKind` in `tools/src/tool_registry_plan_types.rs`
- `tools/src/tool_config.rs` (new): `ToolsConfig`, `ToolsConfigParams`, `ShellCommandBackendConfig`, `UnifiedExecShellMode::ZshFork(ZshForkConfig)`


### Code-mode `setTimeout` / `clearTimeout`

**What:** The JavaScript runtime backing `code-mode` now exposes `setTimeout(callback, delayMs)` and `clearTimeout(id)`, so generated scripts can sleep, debounce, or stagger work between tool calls.

**Details:**

- `setTimeout` schedules a thread-spawned timer that posts `RuntimeCommand::TimeoutFired { id }` after `delayMs`; the v8 callback is invoked under try/catch.
- `setInterval` is **not** provided.
- The exec tool description now documents both globals and notes "Pending timeouts do not keep `exec` alive by themselves; await an explicit promise if you need to wait for one."

**Code references:**

- `code-mode/src/runtime/timers.rs` (new) — `schedule_timeout()`, `cancel_timeout()`, `invoke_timeout_callback()`
- Globals exposed in `code-mode/src/runtime/globals.rs`
- Description text in `code-mode/src/description.rs`


### Tool namespace headings in code-mode descriptions

**What:** When code-mode lists nested tools, related tools are grouped under a namespace heading with a one-line description, instead of a flat list.

**Details:**

- `build_exec_tool_description()` in `code-mode/src/description.rs` now takes a `BTreeMap<String, ToolNamespaceDescription>` and inserts `## <namespace>` headings (with the namespace's description) before the `### tool_name` blocks belonging to it. Empty descriptions degrade gracefully.

**Code references:**

- `build_exec_tool_description()` and `ToolNamespaceDescription` in `code-mode/src/description.rs`


### `Ctrl+O` to copy the last agent response

**What:** A new keyboard shortcut to copy the most recent agent message as raw markdown.

**Details:**

- `Ctrl+O` in the chatwidget calls `copy_last_agent_markdown()`. The same backend powers `/copy`, whose description is updated to "copy last response as markdown".
- The clipboard backend automatically picks the right path: OSC 52 over SSH, `arboard` natively, `wsl_clipboard_copy()` (PowerShell `Set-Clipboard`) on WSL. On Linux/X11 a `ClipboardLease` is held by the TUI so the content stays pasteable.
- `last_agent_markdown` records the markdown of the **first** item-level source per turn (agent message, plan commit, review), so the final-turn summary cannot overwrite a more specific item.
- A new info cell shows `"No agent response to copy"` when the buffer is empty.
- A new tooltip line surfaces the shortcut: "Use /copy or press Ctrl+O to copy the latest agent response as Markdown."

**Code references:**

- `copy_to_clipboard()` in `tui/src/clipboard_copy.rs` (new)
- `ChatWidget::copy_last_agent_markdown()` and `record_agent_markdown()` in `tui/src/chatwidget.rs`
- `tui/src/slash_command.rs` (`SlashCommand::Copy` description rewrite)


### `/resume` available during an active task

**What:** The `/resume` slash command is now allowed mid-task instead of being blocked while the agent is running.

**Code references:**

- `available_during_task()` in `tui/src/slash_command.rs`


### Async, non-blocking `/status`

**What:** `/status` no longer blocks while it gathers expensive data (rate limits, agents summary). It renders immediately and patches the panel in as data arrives.

**Details:**

- New `StatusHistoryHandle` (`tui/src/status/card.rs`) with `finish_agents_summary_discovery()` and `finish_rate_limit_refresh()` patches the displayed status cell when async tasks complete.
- New rate-limit copy distinguishes three states: `not available for this account` (no data), `refresh requested; run /status again shortly.` (refresh in flight), and `limits may be stale - run /status again shortly.` when stale and refreshing simultaneously.
- New `StatusRateLimitData::Unavailable` variant in `tui/src/status/rate_limits.rs`.
- New `discover_agents_summary()` in `tui/src/status/helpers.rs` now also looks at `config.user_instructions_path` (global `AGENTS.md`) ahead of project docs.
- New entry point `new_status_output_with_rate_limits_handle()` ties the UI to the async refresh.

**Code references:**

- `StatusHistoryHandle::finish_rate_limit_refresh()` in `tui/src/status/card.rs`
- `StatusRateLimitData::Unavailable` in `tui/src/status/rate_limits.rs`


### Status line: unified `context-usage` meter

**What:** A single status-line entry replaces the old context-remaining/context-used pair and renders a five-cell unicode block-meter instead of a raw percentage.

**Details:**

- `StatusLineItem::ContextRemaining` and `StatusLineItem::ContextUsed` collapsed into `StatusLineItem::ContextUsage` ("Visual meter of context window usage") in `tui/src/bottom_pane/status_line_setup.rs`. The legacy ids `context-remaining`/`context-used` still parse via `strum` aliases for back-compat.
- The selectable list also adds `WeeklyLimit`.
- Default status-line items dropped from `["model-with-reasoning", "context-remaining", "current-dir"]` to `["model-with-reasoning", "current-dir"]`.
- Renderer `format_context_used_meter()` in `tui/src/chatwidget/status_surfaces.rs` produces output like `Context [██▌  ]`.


### Hidden `codex exec-server` subcommand

**What:** The standalone exec-server can now be launched as a subcommand of `codex` for diagnostic/automation use.

**Details:**

- `Subcommand::ExecServer(ExecServerCommand)` in `cli/src/main.rs` (hidden in help) takes `--listen` (default `ws://127.0.0.1:0`) and dispatches to `run_exec_server_command()` which calls `codex_exec_server::run_main_with_listen_url()`.

**Code references:**

- `run_exec_server_command()` in `cli/src/main.rs`


### `codex debug prompt-input` subcommand

**What:** A new debug subcommand that prints the model-visible prompt input list as JSON, so you can see exactly what tokens Codex would send for a given prompt + image set.

**Details:**

- `DebugSubcommand::PromptInput(DebugPromptInputCommand)` accepts a positional `prompt` and `--image/-i` (comma-separated). It calls `codex_core::build_prompt_input(...)` and prints the result.

**Code references:**

- `run_debug_prompt_input_command()` in `cli/src/main.rs`


### `app-server --listen=off` literal

**What:** `codex app-server --listen` now accepts the literal `off` (in addition to `stdio://` / `ws://...`), useful when running with only the new remote-control transport.

**Code references:**

- Test `app_server_listen_off_parses` in `cli/tests/`


### Network-policy decision payload

**What:** A new structured payload describing why a network access was allowed, denied, or asked, ready to drive richer UI prompts.

**Details:**

- `protocol/src/network_policy.rs` (new) introduces `NetworkPolicyDecisionPayload { decision, source, protocol, host, reason, port }` and `is_ask_from_decider()`.


### Bwrap user-namespace startup probe

**What:** On Linux, Codex now actively probes whether `bwrap` can create user namespaces and warns the user when it can't, instead of failing silently inside the sandbox.

**Details:**

- `system_bwrap_warning(sandbox_policy)` short-circuits for `DangerFullAccess` / `ExternalSandbox` and otherwise calls the new helper `system_bwrap_has_user_namespace_access()` which actually invokes `bwrap --unshare-user --unshare-net --ro-bind / / /bin/true` and pattern-matches stderr against `USER_NAMESPACE_FAILURES` (`loopback: Failed RTM_NEWADDR/NEWLINK`, `setting up uid map: Permission denied`, `No permissions to create a new namespace`).
- New constants `MISSING_BWRAP_WARNING` and `USER_NAMESPACE_WARNING` deliver the user-facing copy. `linux-sandbox/README.md` documents the new check.
- New `CODEX_SKIP_VENDORED_BWRAP` env var (`linux-sandbox/build.rs`) skips building the vendored bwrap during builds that supply their own.

**Code references:**

- `system_bwrap_warning()` and `system_bwrap_has_user_namespace_access()` in `sandboxing/src/bwrap.rs`


### Seatbelt: PyTorch / OpenMP shared memory allowance

**What:** macOS sandboxed shells can now run programs that use libomp/OpenMP (notably PyTorch) without sandbox denials.

**Details:**

- New rule in `sandboxing/src/seatbelt_base_policy.sbpl` allows `ipc-posix-shm-read-data`/`ipc-posix-shm-write-create`/`ipc-posix-shm-write-unlink` for paths matching `^/__KMP_REGISTERED_LIB_[0-9]+$`.


### `[permissions]` profile system

**What:** A first-class TOML `[permissions]` table for declaring named permission profiles, selectable per-project or per-invocation via the new top-level `default_permissions` key.

**Details:**

- New file `codex-config/src/permissions_toml.rs` (~240 lines) introduces `PermissionsToml` with two main sections per profile:
  - `[permissions.<name>.filesystem]` — flatten map of path → `FileSystemAccessMode`, with optional sub-path scoping.
  - `[permissions.<name>.network]` — `NetworkToml` with `enabled`, `proxy_url`, `enable_socks5`, `socks_url`, `enable_socks5_udp`, `allow_upstream_proxy`, `dangerously_allow_non_loopback_proxy`, `dangerously_allow_all_unix_sockets`, `mode` (`limited`/`full`), `domains` (allow/deny map), `unix_sockets` (allow/none map), `allow_local_binding`.
- Profiles in `codex-config/src/profile_toml.rs` gain matching toggles `include_permissions_instructions`, `include_apps_instructions`, `include_environment_context`.

**Code references:**

- `PermissionsToml`, `NetworkToml` in `codex-config/src/permissions_toml.rs`


### Schema-validated `[features]` and structured feature configs

**What:** The `[features]` block in `config.toml` is now validated against a JSON schema and individual features can carry rich, typed configuration instead of just a boolean.

**Details:**

- `config/src/schema.rs` (new) provides `config_schema()`/`features_schema()` and rejects unknown keys via Draft-07 `deny_unknown_fields`.
- A new `FeatureToml<T>` enum and `FeatureConfig` trait (`features/src/feature_configs.rs`) let a single feature accept either `feature_x = true` or a structured table. Example: the new `multi_agent_v2` feature accepts `{ enabled, usage_hint_enabled, usage_hint_text, hide_spawn_agent_metadata }` (booleans still work).
- New feature flags:
  - `general_analytics` (UnderDevelopment, default off) — thread lifecycle analytics.
  - `remote_control` (UnderDevelopment, default off) — see Remote Control transport above.
  - `image_detail_original` graduated UnderDevelopment → Experimental.

**Code references:**

- `MultiAgentV2ConfigToml` in `features/src/feature_configs.rs`
- `Feature::RemoteControl`, `Feature::GeneralAnalytics` in `features/src/lib.rs`


### Multi-agent v2: `followup_task` replaces `assign_task`

**What:** Multi-agent v2 sessions now expose a single `followup_task` tool with simpler semantics: deliver a string message to a target agent, optionally interrupting the in-flight turn.

**Details:**

- `core/src/tools/handlers/multi_agents_v2/followup_task.rs` (new) deserializes `FollowupTaskArgs { target, message, interrupt }` and routes to `handle_message_string_tool(MessageDeliveryMode::TriggerTurn, ...)`.
- `message_tool.rs` was rewritten — old vector-of-`UserInput` inputs replaced with plain-string `message`, and both `SendMessageArgs`/`FollowupTaskArgs` use `#[serde(deny_unknown_fields)]`.

**Code references:**

- `core/src/tools/handlers/multi_agents_v2/followup_task.rs`
- `core/src/tools/handlers/multi_agents_v2/message_tool.rs`


### Curated-plugin export-archive fallback

**What:** When the curated plugin sync can't reach git or HTTP, Codex now falls back to downloading a backup zip archive from `chatgpt.com/backend-api/plugins/export/curated`, so plugins still install on networks where the primary fetch path is blocked.

**Details:**

- `core/src/plugins/startup_sync.rs` adds the `export_archive` transport: it fetches `CuratedPluginsBackupArchiveResponse { download_url }`, unzips the archive, and recovers the embedded git SHA from `HEAD` / `refs/` / `packed-refs` via `read_extracted_backup_archive_git_sha()` and `read_git_ref_sha()`. If no SHA can be recovered, it records the version as `"export-backup"`.
- A new OTel metric value `transport=export_archive` reports use of this path. The prerequisite-fetch timeout was raised from 5 s to 10 s.

**Code references:**

- `read_extracted_backup_archive_git_sha()`, `validate_backup_archive_git_ref()` in `core/src/plugins/startup_sync.rs`


### Non-curated plugin cache refresh worker

**What:** Non-curated plugins (those installed from arbitrary sources) now have their caches refreshed in the background so they stay in sync with manifest version updates.

**Details:**

- New `NonCuratedCacheRefreshState`, `maybe_start_non_curated_plugin_cache_refresh_for_roots()`, and `run_non_curated_plugin_cache_refresh_loop()` (`core/src/plugins/manager.rs`) spawn a deduped background worker `plugins-non-curated-cache-refresh`.
- The worker calls a new `refresh_non_curated_plugin_cache()`. Sync-time warnings batch missing-on-remote plugins into a single message via `missing_remote_plugin_examples()`.

**Code references:**

- `run_non_curated_plugin_cache_refresh_loop()` in `core/src/plugins/manager.rs`


### Plugin manifest versioning

**What:** Plugin manifests can now declare a `version`, which is captured by the install pipeline and surfaced in cache lookup keys.

**Details:**

- `RawPluginManifest` and `PluginManifest` (`core/src/plugins/manifest.rs`) gain an optional trimmed `version` field. `core/src/plugins/store.rs` adds `plugin_version_for_source()` and `validate_plugin_version_segment()` (ASCII alphanumeric plus `.`, `+`, `_`, `-`). `install` now uses the manifest version automatically.

**Code references:**

- `plugin_version_for_source()` in `core/src/plugins/store.rs`

### Guardian: explicit allow/deny verdicts and four-tier risk

The Guardian auto-approval reviewer (already present in earlier versions) gets a substantial schema overhaul:

- Outcome model rewritten. The reviewer no longer returns `risk_score: 0–100` matched against a `GUARDIAN_APPROVAL_RISK_THRESHOLD = 80`. Instead it returns four typed fields: `risk_level` (`low|medium|high|critical` — `critical` is new), `user_authorization` (`unknown|low|medium|high` — entirely new field), `outcome` (`allow|deny` — model decides directly), and `rationale` (one sentence). The `evidence` array was dropped.
- Policy was split into `policy_template.md` (reusable scaffold with sections for Evidence Handling, User Authorization Scoring, Base Risk Taxonomy, Investigation Guidelines, Outcome Policy, plus a `{tenant_policy_config}` placeholder) and the existing `policy.md` (now the tenant-policy fragment with structured sections like Environment Profile, Data Exfiltration, Credential Probing, Persistent Security Weakening, Destructive Actions, Low-Risk Actions). `guardian_policy_prompt_with_config()` does the substitution.
- Approval requests now carry a typed `source: GuardianCommandSource` (`Shell` | `UnifiedExec`) instead of a `tool_name: String`. Action serialization moved from ad-hoc `serde_json::json!` to a typed `GuardianAssessmentAction` enum (Command, Execve, ApplyPatch, NetworkAccess, McpToolCall). `ApplyPatch` dropped its `change_count` field; `McpToolCall` now carries `connector_id`/`connector_name`/`tool_title`.
- Denial messages now carry rationale. `GUARDIAN_REJECTION_MESSAGE` (a static `&str`) was replaced with async `guardian_rejection_message(session, assessment_id)`. Denials are stored in `session.services.guardian_rejection_rationales` keyed by assessment id and injected into the model-visible message: `"This action was rejected due to unacceptable risk.\nReason: {rationale}\n{instructions}"`.
- `GUARDIAN_MAX_ACTION_STRING_TOKENS` was raised from 1,000 to 16,000.
- The TUI's status warning now reads `Automatic approval review {verdict} (risk: {level}, authorization: {auth}): {rationale}`, including the new authorization tier.
- The new `ItemGuardianApprovalReviewStartedNotification` / `ItemGuardianApprovalReviewCompletedNotification` payloads now carry a typed `action: GuardianApprovalReviewAction` (was `JsonValue | null`).

**Code references:**

- `guardian_output_schema()` and `guardian_policy_prompt_with_config()` in `core/src/guardian/prompt.rs`
- `run_guardian_review()` and `guardian_rejection_message()` in `core/src/guardian/review.rs`
- `GuardianAssessmentAction` in `core/src/guardian/approval_request.rs`
- New protocol enums `GuardianCommandSource`, `GuardianUserAuthorization`; `GuardianRiskLevel` adds `Critical`.


### Onboarding device-code login moves to the app-server

The headless ChatGPT login flow no longer drives `request_device_code` / `complete_device_code_login` from the TUI:

- `tui/src/onboarding/auth/headless_chatgpt_login.rs` now sends `ClientRequest::LoginAccount { params: LoginAccountParams::ChatgptDeviceCode }` to the app-server and renders `LoginAccountResponse::ChatgptDeviceCode { login_id, verification_url, user_code }`. The browser-fallback path was removed (handled server-side); errors reset to `PickMode`.
- `ContinueWithDeviceCodeState` now stores `request_id`, optional `login_id`, `verification_url`, `user_code`, with `pending(request_id)` / `ready(...)` constructors and `is_showing_copyable_auth()`. Cancellation goes through a shared `cancel_login_attempt` helper that sends `ClientRequest::CancelLoginAccount`.
- `AuthModeWidget` lost `codex_home`, `cli_auth_credentials_store_mode`, and `forced_chatgpt_workspace_id` (now app-server-owned).

**Code references:**

- `onboarding/auth/headless_chatgpt_login.rs`
- `cancel_login_attempt()` in `onboarding/auth.rs`


### Onboarding animations freeze when copyable URLs are visible

To avoid breaking terminal text selection, the onboarding ASCII animation now pauses while a copyable verification URL or user code is showing.

**Details:**

- New `animations_suppressed: Cell<bool>` and `should_suppress_animations()` in `tui/src/onboarding/welcome.rs`; `tui/src/onboarding/onboarding_screen.rs` propagates the freeze to all current steps.
- `run_onboarding_app` now takes `Option<&mut AppServerSession>` instead of owning the session, so onboarding no longer shuts the session down on exit.


### Status line: weekly-limit and announcement targeting

- `WeeklyLimit` is added to the `SELECTABLE_STATUS_LINE_ITEMS` slice (was previously gated behind enum iteration).
- Server-side announcement tips (`tui/src/tooltips.rs`, `parse_announcement_tip_toml()`) now support `target_plan_types` and `target_oses` filters, so promotions can be plan- or OS-targeted.
- The expired "2x rate limits until April 2nd" promo strings (`PAID_TOOLTIP*`) were removed and replaced with a single neutral `APP_TOOLTIP`. On non-mac/non-windows the paid app tooltip is suppressed entirely.


### MCP server elicitation: persist-mode for non-tool requests

Persist-mode prompts are no longer restricted to tool-approval requests:

- `tool_approval_supports_persist_mode` was renamed `approval_supports_persist_mode` in `tui/src/bottom_pane/mcp_server_elicitation.rs` and now applies to message-only forms generally. Copy adapts: `"Allow this request and continue."` (vs the older `"Run the tool and continue."`). New snapshot `mcp_server_elicitation_message_only_form_with_persist_options.snap`.
- The new `rmcp-client/src/elicitation_client_service.rs` (~213 lines) is a dedicated `Service<RoleClient>` wrapping `LoggingClientHandler`, restoring `_meta` from request context (stripping `progressToken`) and serializing `CreateElicitationResultWithMeta` with `_meta` passthrough — RMCP's typed result lacked this support.


### MCP code carved out into a `codex-mcp` crate

A large reorganization extracts MCP code from `codex-core` into a new dedicated `codex-mcp` crate (`Cargo.toml`, `src/lib.rs`, `src/mcp/auth.rs`, `src/mcp/skill_dependencies.rs`, `src/mcp_connection_manager.rs`, `src/mcp_tool_names.rs`). `core/src/mcp.rs` is now a thin 41-line wrapper providing `McpManager` that delegates. The connection-manager cache schema was bumped to v2; `ToolInfo` now has serde aliases `callable_name`/`callable_namespace` (with backward-compat `tool_name`/`tool_namespace`); `MAX_TOOL_NAME_LENGTH` was removed.


### Login / auth refactor

Auth code moves from `codex-core` into `codex-login` and `codex-protocol`:

- `protocol/src/auth.rs` (new) hosts `PlanType`, `KnownPlan` (with `is_workspace_account()`, `display_name()`, `raw_value()`), `RefreshTokenFailedError`, `RefreshTokenFailedReason`.
- `login/src/api_bridge.rs` (new): `auth_provider_from_auth(Option<CodexAuth>, &ModelProviderInfo) -> Result<CoreAuthProvider>` with precedence `provider api_key > experimental_bearer_token > CodexAuth.get_token()`.
- `ExternalBearerAuth` was renamed `BearerTokenRefresher` and now implements a unified `ExternalAuth` async trait. `AuthManager` now stores `Option<Arc<dyn ExternalAuth>>` and exposes `set_external_auth`, `clear_external_auth`, `has_external_auth`, `has_external_api_key_auth`, `external_auth_mode`, `resolve_external_api_key_auth`. New `AuthManagerConfig` trait + `AuthManager::shared_from_config(...)` constructor.
- `ModelProviderAuthInfo.refresh_interval_ms` changed from `NonZeroU64` to `u64`; `refresh_interval()` now returns `Option<Duration>` so `0` disables proactive refresh and the provider command is only re-run after a 401.


### Resume picker UX polish

- Column headers shortened: `Created at` → `Created`, `Updated at` → `Updated`.
- Relative-time labels (`X minutes ago`) now use a snapshot reference time set in `start_initial_load()` so timestamps don't drift while the picker is open.
- New empty-state distinction: `Loading sessions…` while initial load is pending vs `No sessions yet` after.
- When `--cd` was passed in remote mode, the picker now filters threads server-side via `cwd_filter`.
- `update_thread_names()` now prefers locally cached names from `session_index.jsonl` over backend titles.


### Notifications: Warp terminal support

OSC 9 desktop notifications are now also enabled on Warp (`TERM_PROGRAM=WarpTerminal`) alongside WezTerm and Ghostty (`supports_osc9()` in `tui/src/notifications/mod.rs`).


### Update notifier ignores source builds

`is_source_build_version()` (`tui/src/updates.rs`) now short-circuits the "new version available" check when the build version is `0.0.0` (a from-source build).


### Markdown: percent-decode local link targets

`parse_local_link_target()` in `tui/src/markdown_render.rs` now percent-decodes bare local link paths so `Example%20Folder/R%C3%A9sum%C3%A9/...` renders as `Example Folder/Résumé/...`.


### Bottom-pane composer: Zellij styling

`ChatComposer.is_zellij` (`bottom_pane/chat_composer.rs`) detects Zellij and renders the textarea with explicit `Color::Reset`, cyan/dark-gray prompt chevron, and italic white placeholder, to avoid Zellij pane chrome bleeding into cell styles. New snapshot `zellij_empty_composer`.


### Bottom-pane: paste tears down stacked modals

`BottomPane::handle_paste()` now dismisses stacked modal views when a paste completes, so the composer regains focus correctly.


### Skill popup ranking

`bottom_pane/skill_popup.rs`: when a query is typed, fuzzy-match against the display name now beats `sort_rank`, so display-name matches win over plugin-rank bias. Two new tests pin the ordering: `display_name_match_sorting_beats_worse_secondary_search_term_matches`, `query_match_score_sorts_before_plugin_rank_bias`. Empty-filter ordering still falls back to `sort_rank`.


### Feedback view → app-server upload

The feedback flow no longer uploads from the TUI directly: `BottomPane::feedback_view::submit()` now emits `AppEvent::SubmitFeedback` and the upload is handled by the app server. The renderer factored a reusable `feedback_success_cell()`.


### `codex exec` usage

`codex-rs/exec/src/cli.rs` adds `override_usage = "codex exec [OPTIONS] [PROMPT]\n       codex exec [OPTIONS] <COMMAND> [ARGS]"`. The `--full-auto` help text dropped the misleading `-a on-request` reference.


### `codex login --api-key` guidance

The deprecated `--api-key` flag now uses `num_args = 0..=1, default_missing_value = ""` so a bare `--api-key` produces a guided exit message pointing at `--with-api-key`. `format_exit_messages` no longer early-returns on zero token usage, allowing the resume-command line to be emitted alone.


### `codex exec` resume tests reorganized

The inline `tests` module in `exec/src/cli.rs` was extracted to `exec/src/cli_tests.rs` (and equivalent splits for `event_processor_with_human_output`, `event_processor_with_jsonl_output`, `lib`, `main`).


### Exec environment hardening

- New helper `create_env_from_vars()` (`core/src/exec_env.rs`) injects `PATHEXT=.COM;.EXE;.BAT;.CMD` on Windows when missing (works around Bazel CI failures).
- The `Core` inherit set is split into `COMMON_CORE_VARS = [PATH, SHELL, TMPDIR, TEMP, TMP]` plus platform-specific `PLATFORM_CORE_VARS` (`HOME, LANG, LC_ALL, LC_CTYPE, LOGNAME, USER` on unix; `PATHEXT, USERNAME, USERPROFILE` on Windows). `LANG`/`LC_*` are now inherited core vars on unix.
- `get_shell_path` (`core/src/shell.rs`) takes `&[&str]` instead of `Vec<&str>`. New named fallback constants: `ZSH_FALLBACK_PATHS`, `BASH_FALLBACK_PATHS`, `SH_FALLBACK_PATHS`, plus platform-conditional `PWSH_FALLBACK_PATHS` / `POWERSHELL_FALLBACK_PATHS`. On Windows, pwsh now falls back to `C:\Program Files\PowerShell\7\pwsh.exe` and powershell to `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`.


### Unified-exec remote awareness

`core/src/unified_exec/mod.rs`: `ctx.turn.environment` is now `Option<Arc<Environment>>` (absence yields `ToolError::Rejected("exec_command is unavailable in this session")`). The runtime now uses a typed `environment.is_remote()` predicate; in remote environments `maybe_wrap_shell_lc_with_snapshot()` is bypassed (the base command is forwarded verbatim) and `zsh-fork` is rejected with `unified_exec zsh-fork is not supported when exec_server_url is configured`.


### Tool search: pre-built BM25 engine

`core/src/tools/handlers/tool_search.rs` now pre-builds the BM25 `SearchEngine` at construction time (was rebuilt per call). Search text now includes `plugin_display_names` and `tool.name`. Constants `TOOL_SEARCH_TOOL_NAME` / `TOOL_SEARCH_DEFAULT_LIMIT` moved to `codex_tools`. Result formatting moved to `codex_tools::collect_tool_search_output_tools` consuming `ToolSearchResultSource`.


### Plugin / config crate split (refactor with user-visible re-exports)

`McpServerConfig`, `PluginConfig`, `AuthManager`, `CodexAuth`, `build_reqwest_client`, `AuthCredentialsStoreMode`, etc. moved out of `codex-core` into `codex-config`, `codex-login`, and `codex-mcp`. End-user API surface is preserved via re-exports. `core/src/auth_env_telemetry.rs` is now in `codex-login` (and made `pub`); `core/src/provider_auth.rs` likewise.


### State DB migration: log table dropped

Migration `0023_drop_logs.sql` drops the now-unused logs table. `LOGS_DB_VERSION` was bumped 1 → 2; `STATE_DB_VERSION` advanced to 5.


### Analytics rewritten internally

The `codex-analytics` crate's single `analytics_client.rs` was split into four files: `client.rs` (`AnalyticsEventsClient`), `events.rs` (`AppServerRpcTransport`, RPC payload types), `facts.rs` (typed analytics fact inputs), `reducer.rs` (state reduction logic ~320 lines). Public API is preserved via the new `lib.rs` re-exports.


### `commit_attribution` config key

A new top-level `commit_attribution` string key in `config.toml` lets the user customize (or disable, via empty string) the co-author trailer applied to git commits Codex produces.


### `default_permissions` config key

A new top-level `default_permissions` string key selects a profile from the new `[permissions]` table to be applied when no explicit override is set.


### Realtime backend prompt template

A new template at `core/templates/realtime/backend_prompt.md` provides the default backend prompt for realtime conversations ("You are **Codex**, an **OpenAI Coding Agent**…"), with `{{ user_first_name }}` substituted from `whoami::realname()` / `username()`. `prepare_realtime_backend_prompt()` (`core/src/realtime_prompt.rs`) resolves the prompt in priority order: `experimental_realtime_ws_backend_prompt` config key, per-request prompt, or this template. The TUI no longer hardcodes its own realtime prompt; it now passes `prompt: None` so core uses the template.

### `format_exit_messages` no longer suppressed when token usage is zero

Previously `cli/src/main.rs::format_exit_messages` early-returned on zero token usage, hiding the resume-command line for short sessions. The early-return was removed.


### Account mismatch invalidates remote-control enrollments

In the new remote-control transport, mismatched account IDs between the persisted enrollment and the active ChatGPT session would silently cause failures. The enrollment is now invalidated and re-fetched on account change (see `app-server/src/transport/remote_control/websocket.rs`).


### Resume-picker timestamps no longer drift

The resume picker's relative-time labels would shift while the picker was open. They now use a snapshot reference time captured at load.


### `/copy` final-turn override

The previous implementation could overwrite a more specific copy source (plan commit, review) with the final turn's summary message. The new `record_agent_markdown` records the first item-level source per turn and uses `last_agent_message` only as a fallback.


### `app-server --listen` requires explicit transport choice

When the `remote_control` feature is off and no `--listen` value was given, the app-server now emits a clear error: "no transport configured; use --listen or enable remote control" (`app-server/src/lib.rs`).
