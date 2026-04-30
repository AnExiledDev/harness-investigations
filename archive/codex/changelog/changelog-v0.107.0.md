# Changelog for version 0.107.0

## Highlights

This release introduces realtime audio device selection in the TUI (new `/settings` slash command and `[audio]` config section), a new `serverRequest/resolved` notification that lets app‑server clients track lifecycle of approval/input requests across turn transitions, and a `host_executable` directive in execpolicy that constrains basename rule fallback to known absolute paths. It also ships a `debug clear-memories` CLI command, an opt‑in `fork_context` parameter on `spawn_agent` so child agents can inherit the parent thread's history, and an OAuth `oauth_resource` (RFC 8707) field for MCP servers.

### `/settings` slash command and per‑device realtime audio configuration

**What:** A new TUI slash command (`/settings`) opens a popup that lets you pick the microphone and speaker devices used by realtime voice mode. Selections are persisted in `config.toml` under a new top‑level `[audio]` table, and apply only to realtime conversations (regular voice transcription continues to use the system default).

**Details:**

- The popup lists installed input/output devices via `cpal` and supports a "System default" entry plus an "Unavailable: …" placeholder when a previously‑configured device is no longer present.
- If a realtime conversation is already live when you change the device, Codex prompts "Restart now" / "Apply later". Restarting tears down and re‑creates the capture/playback streams without ending the conversation.
- The `[audio]` block accepts `microphone = "USB Mic"` and `speaker = "Desk Speakers"` (string device names matching what the OS reports).
- The command is hidden when the realtime feature is disabled or when the TUI is built without `voice-input`/on Linux.

**Code references:** `open_realtime_audio_popup()`, `open_realtime_audio_device_selection_with_names()`, `restart_realtime_audio_device()` in `tui/src/chatwidget.rs`; `RealtimeAudioToml`/`audio` parsing in `core/src/config/types.rs`; new module `tui/src/audio_device.rs`; `SlashCommand::Settings` in `tui/src/slash_command.rs`.


### `serverRequest/resolved` notification

**What:** A new `serverRequest/resolved` server notification (with `{ threadId, requestId }`) tells app‑server clients when a pending app‑server → client request has been answered, withdrawn by a turn transition, or otherwise cleared.

**Details:**

- Emitted after the client responds to `item/tool/requestUserInput`, `item/commandExecution/requestApproval`, and `item/fileChange/requestApproval`.
- Emitted for any pending request that the server cancels because a turn started, completed, or was aborted. In that case the request callback resolves with the JSON‑RPC error reason `"turnTransition"` so client wrappers know the resolution was a cleanup, not a real reply.
- Client request handlers in `bespoke_event_handling.rs` short‑circuit on the `turnTransition` reason to avoid double‑replying to core.

**Example payload:**

```json
{
  "method": "serverRequest/resolved",
  "params": { "threadId": "thr_…", "requestId": 42 }
}
```

**Code references:** New `tui/`‑adjacent module `app-server/src/server_request_error.rs` with `is_turn_transition_server_request_error()`; `ServerRequestResolvedNotification` in `app-server-protocol/src/protocol/v2.rs`; `resolve_pending_server_request()` and `ThreadListenerCommand::ResolveServerRequest` in `app-server/src/codex_message_processor.rs` and `app-server/src/thread_state.rs`; `abort_pending_server_requests()` in `app-server/src/outgoing_message.rs`.


### `host_executable` policy directive and `--resolve-host-executables` flag

**What:** The Starlark execpolicy DSL gains a new `host_executable(name=…, paths=[…])` builtin that pins which absolute executable paths are allowed to fall back through basename rules. The `codex execpolicy check` CLI exposes a new `--resolve-host-executables` flag that opts a check into that fallback path.

**Details:**

- Without `--resolve-host-executables`, only exact first‑token matches resolve a rule (e.g., `/usr/bin/git status` only matches a rule whose first token is `/usr/bin/git`).
- With the flag, if no exact rule matches, Codex tries the basename — but only when either no `host_executable()` entry exists for that basename, or the absolute path is one of the listed paths.
- `RuleMatch::PrefixRuleMatch` now carries a `resolvedProgram` field so callers can see which absolute program triggered a basename‑fallback match.
- Examples passed to `match` / `not_match` are now validated lazily after parsing finishes so rules referencing later‑declared `host_executable` entries can be verified correctly.

**Example:**

```starlark
host_executable(
    name = "git",
    paths = ["/opt/homebrew/bin/git", "/usr/bin/git"],
)
```

```bash
codex execpolicy check \
  --rules path/to/policy.rules \
  --resolve-host-executables \
  /usr/bin/git status
```

**Code references:** New `executable_name.rs`, `policy.rs::MatchOptions`, `policy.rs::match_host_executable_rules()`, `parser.rs::host_executable` builtin, all under `execpolicy/src/`; `--resolve-host-executables` flag in `execpolicy/src/execpolicycheck.rs`; updated `execpolicy/README.md`.


### `debug clear-memories` CLI command

**What:** A new (hidden) subcommand `codex debug clear-memories` resets the local memory pipeline for a fresh start.

**Details:**

- Drops all rows from `stage1_outputs`, deletes `memory_stage1` and `memory_consolidate_global` jobs, marks every existing thread's `memory_mode = "disabled"`, and removes the `~/.codex/memories` directory.
- Prints a one‑line summary of what was cleared (`"Cleared memory state from …. Removed …."`).
- Newly created threads after clearing default to `memory_mode = "disabled"`, controlled by the new `[memories].generate_memories` flag (see "Memory pipeline gating" below).

**Code references:** `run_debug_clear_memories_command()` in `cli/src/main.rs`; `reset_memory_data_for_fresh_start()` in `state/src/runtime/memories.rs`.


### `fork_context` parameter on `spawn_agent`

**What:** The `spawn_agent` tool exposes a new boolean argument, `fork_context`. When `true`, the new sub‑agent is initialized with a forked copy of the parent's rollout history and a synthetic `FunctionCallOutput` is appended for the parent's `spawn_agent` call so the parent transcript stays balanced.

**Details:**

- The synthetic output text is `"You are the newly spawned agent. The prior conversation history was forked from your parent agent. Treat the next user message as your new task, and use the forked history only as background context."` and is marked `success: true`.
- The parent's rollout is materialized and flushed before the snapshot is taken so the fork is guaranteed to include the latest in‑memory turns.
- This requires a `SubAgentSource::ThreadSpawn` session source; calling `spawn_agent_with_options` with `fork_parent_spawn_call_id` set without a thread‑spawn source returns a fatal error.

**Code references:** `SpawnAgentOptions { fork_parent_spawn_call_id }` and `spawn_agent_with_options()` in `core/src/agent/control.rs`; new `fork_context` JSON schema entry in `create_spawn_agent_tool()` in `core/src/tools/spec.rs`.


### MCP server `oauth_resource` config option (RFC 8707)

**What:** Streamable‑HTTP MCP servers can declare an `oauth_resource` URI in `config.toml`. During OAuth login, Codex appends it as a `resource` query parameter on the authorization URL, satisfying RFC 8707 ("Resource Indicators for OAuth 2.0").

**Details:**

- The field is forwarded through `codex mcp add`, `codex mcp login`, and the MCP edit codepaths; setting it on a stdio transport is rejected with `"oauth_resource is not supported for stdio"`.
- The query parameter is URL‑encoded and skipped when empty.
- Round‑trip serialization preserves the value.

**Example `config.toml`:**

```toml
[mcp_servers.docs]
url = "https://example.com/mcp"
oauth_resource = "https://api.example.com"
```

**Code references:** `oauth_resource` in `McpServerConfig` (`core/src/config/types.rs`); `append_query_param()` in `rmcp-client/src/perform_oauth_login.rs`; CLI threading in `cli/src/mcp_cmd.rs`.


### Model availability NUX (new‑user‑experience tooltip)

**What:** Each `ModelInfo` can now declare an `availability_nux: { message }` block. When such a model becomes available, the TUI shows a one‑line tooltip ("Tip: …") on the next startup session info card and persists a per‑model shown counter so the same NUX is not shown more than four times.

**Details:**

- The shown counts live in `[tui.model_availability_nux]` in `config.toml` (one entry per model slug).
- The NUX is suppressed on first‑run sessions, when `show_tooltips = false`, when the user resumes/forks an existing session, and after the per‑model count reaches `MODEL_AVAILABILITY_NUX_MAX_SHOW_COUNT` (4).
- The model list response (`v2/Model`) gains optional `availabilityNux` and `upgradeInfo` fields (the latter exposes structured `upgradeCopy`, `modelLink`, and `migrationMarkdown` previously only carried by the legacy `upgrade` slug).

**Code references:** `ModelAvailabilityNux` and `ModelAvailabilityNuxConfig` in `protocol/src/openai_models.rs` and `core/src/config/types.rs`; `select_model_availability_nux()` and `prepare_startup_tooltip_override()` in `tui/src/app.rs`; `Model::availability_nux`/`upgrade_info` in `app-server-protocol/src/protocol/v2.rs`.


### `audio_device` and watch helpers in `app-server-test-client`

**What:** A new `watch` subcommand opens an app‑server connection, performs `initialize`, and then prints every inbound JSON‑RPC message until the process is interrupted. This is intended for protocol debugging.

**Code references:** `CliCommand::Watch` and `watch()` in `app-server-test-client/src/lib.rs`; documented in `app-server-test-client/README.md`.


### Memory pipeline gating (`generate_memories` / `use_memories`)

**What:** Two new boolean keys under `[memories]` let users opt out of either side of the memory pipeline:

- `generate_memories = false` — newly created threads are persisted with `memory_mode = "disabled"` so stage 1 jobs skip them.
- `use_memories = false` — skips injecting memory usage instructions into developer prompts.

Stage 1 job claiming was updated to skip threads whose `memory_mode != 'enabled'`, and stage 1 SQL queries now also expose `git_branch` for global consolidation.

**Code references:** `MemoriesToml` / `MemoriesConfig` in `core/src/config/types.rs`; `memory_mode` filter in `state/src/runtime/memories.rs`; `upsert_thread_with_creation_memory_mode()` in `state/src/runtime/threads.rs`.


### `ephemeral` thread flag

**What:** `Thread` (v2) gains an `ephemeral: boolean` field that signals whether a session is intentionally in‑memory only. When `true`, `thread.path` is `null`. The flag is propagated through `thread/start`, `thread/resume`, `thread/fork`, `thread/list`, `thread/read`, `thread/rollback`, `thread/started`, and `thread/unarchive` responses.

**Code references:** `ephemeral` in `protocol/v2.rs::Thread`; documented in `app-server/README.md`.


### Local time + timezone in turn context

**What:** `TurnContext` and the persisted `TurnContextItem` now record `current_date` (`YYYY-MM-DD`) and `timezone` (IANA, e.g. `America/Los_Angeles`). When IANA detection fails the context falls back to `Etc/UTC` and the UTC date.

**Details:**

- A new `iana-time-zone` workspace dependency is added.
- These fields propagate through resume/fork rollout reconstruction so replayed sessions retain the original turn's date/timezone.

**Code references:** `local_time_context()` and updated `TurnContext` in `core/src/codex.rs`; `TurnContextItem` in `protocol/src/protocol.rs`.

### Strict absolute paths in approval payloads

`AdditionalFileSystemPermissions.read` / `write` now use `AbsolutePathBuf` instead of `PathBuf` in both Rust and the generated TypeScript/JSON schemas. Deserialization rejects relative paths with `"AbsolutePathBuf deserialized without a base path"`. This guarantees that every filesystem path in command/file‑change approvals is absolute on the wire, which removes a class of ambiguity for clients rendering approval prompts. (`AdditionalFileSystemPermissions` in `app-server-protocol/src/protocol/v2.rs`; new round‑trip test in `app-server-protocol/src/protocol/v2.rs::tests`.)


### `FunctionCallOutputPayload` for custom tool call output

`ResponseItem::CustomToolCallOutput.output` is now `FunctionCallOutputPayload` instead of `String`, matching `FunctionCallOutput`. This unifies how Codex truncates and image‑strips custom‑tool outputs (e.g., `js_repl`/`apply_patch`) — they now share the same `truncate_function_output_payload()` helper and `image_data_url_estimate_adjustment()` accounting. Generated TypeScript bindings (`ResponseItem.ts`) reflect the change. Existing wire payloads continue to work because `FunctionCallOutputPayload` is `untagged`.


### Optional `summary` in `TurnStart` / `SendUserTurn`

The `summary` field on the `Op::UserTurn` request is now `Option<ReasoningSummaryConfig>`. When `None`, the session keeps its current setting (which lets core fall back to the model's default for new sessions). The TUI and `exec` driver pass `None` instead of forcing `Auto`, which restores the prior behavior of letting the model's default control summary visibility. (`Op::UserTurn` in `protocol/src/protocol.rs`; `chatwidget.rs`/`exec/src/lib.rs` callers updated.)


### Pending requests cancelled on turn transitions

`apply_bespoke_event_handling()` now calls `outgoing.abort_pending_server_requests()` on `TurnStarted`, `TurnComplete`, and `TurnAborted`. Cancelled requests resolve with a JSON‑RPC error containing `data: { reason: "turnTransition" }`, and the request callback table is cleared so memory does not grow across long sessions. The matching `serverRequest/resolved` notification is emitted so subscribed clients can update their UI. (`outgoing_message.rs::ThreadScopedOutgoingMessageSender::abort_pending_server_requests`; `bespoke_event_handling.rs`.)


### Non‑blocking `thread/start`

`CodexMessageProcessor::thread_start` now spawns a `thread_start_task` rather than running the full pipeline inline. Thread creation, dynamic tool validation, listener auto‑attach, and notification emission all happen on a background task, so the message processor does not block other connection traffic while a thread bootstraps. (`thread_start_task()` and `ListenerTaskContext` in `app-server/src/codex_message_processor.rs`.)


### Connection liveness tracking and safe auto‑subscribe

`ThreadStateManager` is now an `Arc<Mutex<ThreadStateManagerInner>>` with explicit per‑thread `connection_ids`, plus a `live_connections` set populated on `connection_initialized()` and cleared on `remove_connection()`. `ensure_conversation_listener()` returns a tri‑valued result (`Attached` / `ConnectionClosed` / `Err`) instead of erroring, so attempts to attach listeners for already‑disconnected clients are silently dropped (`tracing::debug!` only) instead of warning. A regression test (`closed_connection_cannot_be_reintroduced_by_auto_subscribe`) covers the case where a closed connection used to be re‑introduced by `ensure_connection_subscribed`.


### Replay outstanding server requests on resume

When a client re‑attaches via `thread/resume`, the server now calls `outgoing.replay_requests_to_connection_for_thread(connection_id, conversation_id)` before adding the connection to the thread's subscriber set. The reattaching connection therefore receives any still‑outstanding approval/user‑input requests it missed while disconnected. (`handle_pending_thread_resume_request()` in `app-server/src/codex_message_processor.rs`.)


### `app_server_client_name` propagation

The `initialize` request's client `name` is now stored on the connection session and threaded through to `thread.set_app_server_client_name()` on `turn/start`, `sendUserMessage`, and `sendUserTurn`. This lets core (and notification hooks) know which client originated a turn — for example, the TUI now self‑identifies as `"codex-tui"` when spawning agents. (`ConnectionSessionState::app_server_client_name`; `set_app_server_client_name()` in `core/src/codex.rs`; `chatwidget/agent.rs::initialize_app_server_client_name()`.)


### Apply‑patch approval rendered into thread history

`ThreadHistoryBuilder` now responds to `EventMsg::ApplyPatchApprovalRequest` by upserting a `ThreadItem::FileChange` (status `InProgress`) into the active turn so resume snapshots include the proposed file change immediately, not only after `PatchApplyBegin`. Two new unit tests in `protocol/thread_history.rs::tests` cover the active‑turn snapshot.


### Subagents listed in `environment_context`

`AgentControl::format_environment_context_subagents()` produces a sorted list of running sub‑agents (filtered by `parent_thread_id`) which is rendered into a `<subagents>` block inside the parent's `<environment_context>`. Snapshot tests exercise both one‑agent and two‑agent layouts. (`core/src/agent/control.rs`; new snapshots under `core/tests/suite/snapshots/`.)


### App list emits interim notifications during load

`list_apps_emits_updates_and_returns_after_both_lists_load` was rewritten as `list_apps_waits_for_accessible_data_before_emitting_directory_updates`. The processor now sends an `app/list/updated` notification as soon as accessible (or cached) connectors are available, then again when accessible/all loads complete and content actually changed (`should_send_app_list_updated_notification`, `last_notified_apps` deduping). This avoids long blank UI states when one of the two backends is slow.


### Cloud‑requirements cache: shorter TTL + background refresh

`CLOUD_REQUIREMENTS_CACHE_TTL` was reduced from 60 minutes to 30 minutes, and a new background task refreshes the cache every 5 minutes for ChatGPT Business/Enterprise users. `CloudRequirementsService` is now `Clone`, and `cloud_requirements_loader()` aborts any prior refresher task before installing a new one. New tests cover the refresh path. (`cloud-requirements/src/lib.rs`.)


### ChatGPT auth: missing plan claim → `Unknown`

`CodexAuth::account_plan_type()` was rewritten so a token without a `chatgpt_plan_type` claim now returns `Some(AccountPlanType::Unknown)` instead of `None`. Code paths that treated `None` as "not ChatGPT" (e.g., `get_account` and downstream business/enterprise gating) therefore behave correctly when the token is otherwise valid. New unit test `missing_plan_type_maps_to_unknown` and an MCP integration test (`get_account_with_chatgpt_missing_plan_claim_returns_unknown`) cover this. (`core/src/auth.rs`.)


### Realtime websocket: structured logging at every step

The realtime websocket pump in `codex-api` now logs at `trace`/`debug`/`info`/`error` levels for sends, receives, pings/pongs, close frames, parse failures, and connection lifecycle. Useful for diagnosing realtime voice connection issues. (`codex-api/src/endpoint/realtime_websocket/methods.rs`.)


### Voice capture/output always 24 kHz mono

`VoiceCapture::start_realtime` now selects the device using the new `audio_device` module, and `send_realtime_audio_chunk` always converts captured PCM to 24 kHz mono (`MODEL_AUDIO_SAMPLE_RATE` / `MODEL_AUDIO_CHANNELS`) before encoding so the model receives the format it expects regardless of mic capabilities. `encode_wav_normalized()` does the same downmix/resample pass before normalization, and `RealtimeAudioPlayer::start()` honors the configured speaker. The transcription model also changed from `gpt-4o-transcribe` to `gpt-4o-mini-transcribe`. (`tui/src/voice.rs`.)


### Diff renderer reads theme scope colors and bundles render context

A new `DiffRenderStyleContext` is captured once per render frame in `current_diff_render_style_context()` and threaded through every line, so theme picker live previews and inline‑diff cells stay consistent within a frame. Diff insert/delete backgrounds now prefer `markup.inserted` / `markup.deleted` (and fall back to `diff.inserted` / `diff.deleted`) from the syntax theme, falling back to the previous hardcoded palette only when the theme defines no scope. ANSI‑16 sessions now leave the diff line background unset so the terminal default shows through (snapshot test `ansi16_insert_delete_no_background.snap`). Windows Terminal sessions (detected via `WT_SESSION` or `terminal_info()`) are promoted to truecolor unconditionally unless `FORCE_COLOR` is set. (`tui/src/diff_render.rs`; `tui/src/render/highlight.rs::diff_scope_background_rgbs()`.)


### Resume/fork picker is sturdier

- `SessionSelection::Resume(SessionTarget)` / `Fork(SessionTarget)` carries both the rollout `path` and `thread_id`, so the picker / CLI flags can resolve the SQLite‑backed `cwd` directly. `resolve_session_thread_id()` reads the `SessionMeta` line when needed.
- The picker shows an inline error in the search line ("Failed to read session metadata from …") rather than panicking when `Enter` selects a row whose metadata cannot be read.
- `read_session_cwd()` now prefers the SQLite `threads.cwd` value when the SQLite feature is enabled, falling back to the latest `TurnContext` from the rollout, and finally to the `SessionMeta`. New test: `read_session_cwd_prefers_sqlite_when_thread_id_present`.


### `features list` output is sorted

`codex features list` now sorts its rows alphabetically by feature name. New CLI test `features_list_is_sorted_alphabetically_by_feature_name`. (`cli/src/main.rs`.)


### File completion preserves large‑paste placeholders

Tab‑accepting an `@token` path completion in the chat composer no longer rebuilds the textarea with `set_text_clearing_elements`. Instead it uses `replace_range` so adjacent large‑paste placeholders survive and still expand correctly on submit. Test: `file_completion_preserves_large_paste_placeholder_elements`.


### Windows sandbox: USERPROFILE excludes credential directories

The Windows sandbox setup orchestrator no longer adds the entire `USERPROFILE` as a single read root. Instead, `profile_read_roots()` enumerates the profile and skips a curated denylist of credential/state directories: `.ssh`, `.gnupg`, `.aws`, `.azure`, `.kube`, `.docker`, `.config`, `.npm`, `.pki`, `.terraform.d` (case‑insensitive). If enumeration fails, it falls back to the old behavior of granting the entire profile. (`windows-sandbox-rs/src/setup_orchestrator.rs`.)


### `fork_context` infrastructure: parent rollout flushed before snapshot

When `fork_context = true` is requested, `spawn_agent_with_options()` calls `parent_thread.codex.session.ensure_rollout_materialized().await` and then `flush_rollout().await` before reading the rollout history. This guarantees the snapshot reflects every queued in‑memory write. Tests `spawn_agent_can_fork_parent_thread_history`, `spawn_agent_fork_injects_output_for_parent_spawn_call`, and `spawn_agent_fork_flushes_parent_rollout_before_loading_history` cover the path.


### Reserialize shell outputs unifies function/custom call paths

`reserialize_shell_outputs()` now matches `ResponseItem::FunctionCallOutput { … }` and `ResponseItem::CustomToolCallOutput { … }` in a single arm, so structured shell output is correctly converted into the human‑readable "Exit code / Wall time / Output" form for both. New test `reserializes_shell_outputs_for_function_and_custom_tool_calls`. (`core/src/client_common.rs`.)


### Session info tooltip override

`new_session_info()` (TUI history cell) now takes a `tooltip_override: Option<String>` so the model availability NUX can replace the default plan tooltip. Suppressed when `is_first_event` is true or `show_tooltips = false`. New snapshot `session_info_availability_nux_tooltip_snapshot.snap`.


### Documentation refresh

`app-server/README.md` documents the new `serverRequest/resolved` flow for command, file‑change, and `request_user_input` approvals; `model/list` now mentions `upgradeInfo` and `availabilityNux`; `thread.ephemeral` semantics are spelled out. `execpolicy/README.md` documents `host_executable()` and `--resolve-host-executables`.


### Approval policy prompt: sandbox‑related network failures

The on‑request approval prompt instructs the model to re‑request escalation not only on outright sandbox failures but also "with a likely sandbox‑related network error (for example DNS/host resolution, registry/index access, or dependency download failure)". (`protocol/src/prompts/permissions/approval_policy/on_request_rule.md`.)

### Closed connections can no longer be re‑subscribed

Before this release, calling `ensure_connection_subscribed` for a connection that had already been removed would silently re‑populate the per‑thread subscriber set. The new `try_ensure_connection_subscribed` returns `None` when `!live_connections.contains(&connection_id)`, and `try_add_connection_to_thread` likewise refuses, preventing the in‑memory state from referencing dead connections. Regression test: `closed_connection_cannot_be_reintroduced_by_auto_subscribe` in `codex_message_processor.rs::tests`.


### Custom tool call output truncation actually applies

Because `ResponseItem::CustomToolCallOutput.output` was a plain `String`, the previous truncation path stored the raw string back unchanged — the new test `record_items_truncates_custom_tool_call_output_content` would have failed. Switching the field to `FunctionCallOutputPayload` and routing through `truncate_function_output_payload()` ensures the same byte/token policy used for shell calls is applied to custom tool calls. (`core/src/context_manager/history.rs`.)


### Resume picker no longer aborts on missing metadata

Previously, pressing Enter on a row whose `SessionMeta` could not be read would propagate an error and tear down the picker. The picker now sets `inline_error` on the state and re‑renders the search line in red, leaving the picker open. Test: `enter_on_row_without_resolvable_thread_id_shows_inline_error`. (`tui/src/resume_picker.rs`.)


### `--fork-last` / `--resume-last` exit cleanly when metadata is missing

When `cli.fork_last` or `cli.resume_last` finds the latest rollout but its `SessionMeta` cannot be parsed, Codex now restores the terminal and exits with `ExitReason::Fatal("Found latest saved session at …, but failed to read its metadata. Run `codex resume`/`codex fork` to choose from existing sessions.")` instead of falling through into a confused start‑fresh state. (`tui/src/lib.rs::run_ratatui_app`.)


### Pending interrupt cleanup uses async lock correctly

`ThreadStateManager::thread_state` and several other accessors are now `async` and lock the inner `Mutex` on demand. Earlier code held a `&mut self` borrow, which is incompatible with the new `Arc<Mutex<…>>` design and would have prevented multiple concurrent listener tasks from sharing the manager safely.


### Subagent `awaiter` role temporarily disabled

The hard‑coded `awaiter` agent role config in `core/src/agent/role.rs` is commented out (with a `// Awaiter is temp removed` marker). Existing configurations that referenced `awaiter` will no longer have it auto‑declared.
