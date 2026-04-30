# Changelog for version 0.106.0

## Highlights

This release introduces a **realtime voice/text conversation API** for the v2 app server, **reference-counted thread lifecycle management** with `thread/unsubscribe` and `thread/closed`, and a **1 MiB hard cap on user-message input**. The skill approval flow has been retired in favor of a generalized session-scoped approval cache, the JavaScript REPL is now toggleable from the `/experimental` menu, and the network proxy now emits structured OTEL audit events for every policy decision.

### Realtime conversation (voice + text) over the v2 protocol

**What:** A new family of `thread/realtime/*` JSON-RPC requests and notifications lets clients stream audio and text into a Codex thread and receive live audio output and transcript updates.

**Details:**
- Requests:
  - `thread/realtime/start` — opens the realtime websocket session for an existing thread (`ThreadRealtimeStartParams` with `prompt`, `session_id`).
  - `thread/realtime/appendAudio` — pushes an audio chunk (`ThreadRealtimeAudioChunk` with `data`, `sampleRate`, `numChannels`, `samplesPerChannel`).
  - `thread/realtime/appendText` — sends a text turn into the realtime session.
  - `thread/realtime/stop` — closes the realtime transport.
- Notifications:
  - `thread/realtime/started` (with optional `sessionId`)
  - `thread/realtime/itemAdded` (raw non-audio item from backend)
  - `thread/realtime/outputAudio/delta` (streamed PCM frames)
  - `thread/realtime/error`
  - `thread/realtime/closed` (with optional `reason`, e.g. `"requested"` / `"transport_closed"`)
- Gated behind the `realtime_conversation` feature flag plus a configured `experimental_realtime_ws_base_url`. Requests against threads without the feature return `"thread {id} does not support realtime conversation"`.

**Code references:** `prepare_realtime_conversation_thread()`, `thread_realtime_start()`, `thread_realtime_append_audio()`, `thread_realtime_append_text()`, `thread_realtime_stop()` in `app-server/src/codex_message_processor.rs`; new schemas under `app-server-protocol/schema/json/v2/ThreadRealtime*`; integration tests in `app-server/tests/suite/v2/realtime_conversation.rs`.


### `thread/unsubscribe` with reference-counted thread lifecycle

**What:** Clients can now release their interest in a loaded thread; the thread is gracefully shut down only when the last subscriber leaves, after which a `thread/closed` notification is emitted.

**Details:**
- New `ThreadUnsubscribeParams { threadId }` request returning `ThreadUnsubscribeStatus` (`unsubscribed` | `notSubscribed` | `notLoaded`).
- When the unsubscribing connection is the last subscriber, the app server submits `Op::Shutdown`, polls `agent_status()` until it reaches `Shutdown` (10 s timeout), removes the thread from the manager, cancels any in-flight server→client requests scoped to that thread, and broadcasts `thread/closed`.
- A new `pending_thread_unloads` set rejects `thread/resume` requests for threads that are mid-shutdown with: `"thread {id} is closing; retry thread/resume after the thread is closed"`.
- `OutgoingMessageSender` now tags each pending callback with its `thread_id`, enabling `cancel_requests_for_thread()` to drop stale callbacks deterministically.
- `ThreadStateManager::unsubscribe_connection_from_thread()` and `has_subscribers()` are the new bookkeeping primitives.

**Code references:** `thread_unsubscribe()`, `wait_for_thread_shutdown()`, `finalize_thread_teardown()` in `app-server/src/codex_message_processor.rs`; `unsubscribe_connection_from_thread()` in `app-server/src/thread_state.rs`; `cancel_requests_for_thread()` in `app-server/src/outgoing_message.rs`.


### `dynamic_tool_call_response` event and `DynamicToolCallThreadItem`

**What:** Dynamic tool calls now emit a paired response event in addition to the existing request event, giving clients a single place to observe tool outcomes, durations, and errors.

**Details:**
- New `EventMsg::DynamicToolCallResponse(DynamicToolCallResponseEvent)` with `call_id`, `turn_id`, `tool`, `arguments`, `content_items`, `success`, optional `error`, and `duration`.
- The v2 thread item stream gains `DynamicToolCallThreadItem` (`tool`, `arguments`, `contentItems`, `durationMs`, `status` ∈ `inProgress|completed|failed`, `success`).
- If a request is cancelled before producing a response, the new event still fires with `success: false`, `error: "dynamic tool call was cancelled before receiving a response"`, and the elapsed `duration`.
- Decoded fallbacks (`"dynamic tool request failed"`, `"dynamic tool response was invalid"`) now flow through `decode_response()` / `fallback_response()` helpers in `app-server/src/dynamic_tools.rs`.

**Code references:** `DynamicToolCallResponseEvent` in `protocol/src/protocol.rs`; `request_dynamic_tool()` in `core/src/tools/handlers/dynamic.rs`; updated event-routing match arms across `event_processor_with_human_output.rs`, `mcp-server/src/codex_tool_runner.rs`, and `tui/src/chatwidget.rs`.


### Server-driven `available_decisions` for command approvals

**What:** `ExecApprovalRequestEvent` gained an optional `available_decisions: Vec<ReviewDecision>` field that lets the agent dictate exactly which approval options the client should render, instead of the client deriving them locally from the request shape.

**Details:**
- For shell command approvals, the core now builds the available list inline:
  - Always includes `Approved` and `Abort`.
  - Adds `ApprovedForSession` only for skill-script approvals (where session caching is honored).
  - Adds `ApprovedExecpolicyAmendment` and/or `NetworkPolicyAmendment` (allow / deny) variants when the decision is contextually applicable.
- A new `ReviewDecision::Denied` value powers the new "No, and block this host in the future" approval option.
- `effective_available_decisions()` and `default_available_decisions()` on `ExecApprovalRequestEvent` give older clients (where the field is absent) the legacy default set, preserving backward compatibility.
- The TUI approval overlay was refactored to consume the wire field directly: `ApprovalRequest::Exec` now carries `available_decisions: Vec<ReviewDecision>`, and `exec_options()` simply maps each decision to a human-readable button.

**Code references:** `ExecApprovalRequestEvent::effective_available_decisions()` / `default_available_decisions()` in `protocol/src/approvals.rs`; `exec_options()` in `tui/src/bottom_pane/approval_overlay.rs`; `process_decision()` in `core/src/tools/runtimes/shell/unix_escalation.rs`.


### Network proxy OTEL audit events

**What:** The embedded network proxy emits a structured `codex.network_proxy.policy_decision` tracing event for every allow/deny/ask decision, with metadata fields for downstream OTEL consumers.

**Details:**
- Two scopes:
  - `network.policy.scope = "domain"` — host-policy evaluations (`evaluate_host_policy`).
  - `network.policy.scope = "non_domain"` — mode-guard / proxy-state checks, including unix-socket allow/deny paths.
- Fields include `network.policy.decision` (`allow|deny|ask`), `network.policy.source` (`baseline_policy|mode_guard|proxy_state|decider`), `network.policy.reason`, `network.transport.protocol`, `server.address`/`server.port`, `http.request.method` (defaulting to `"none"`), `client.address` (defaulting to `"unknown"`), and `network.policy.override = true` only when a decider overrides a `not_allowed` baseline.
- New `NetworkProxyAuditMetadata` carries optional contextual fields — `conversation_id`, `app_version`, `user_account_id`, `auth_mode`, `originator`, `user_email`, `terminal_type`, `model`, `slug` — into every event.
- Unix-socket block-path audits use sentinel endpoint values (`server.address = "unix-socket"`, `server.port = 0`).
- Audit events intentionally avoid logging full URL / path / query data.

**Code references:** `emit_block_decision_audit_event()`, `emit_allow_decision_audit_event()`, `emit_policy_audit_event()` in `network-proxy/src/network_policy.rs`; new section "OTEL Audit Events (embedded/managed)" in `network-proxy/README.md`; `NetworkProxyAuditMetadata` in `network-proxy/src/runtime.rs`.


### `default_mode_request_user_input` feature flag

**What:** A new feature flag lets `request_user_input` be available in **Default** mode, not just **Plan** mode.

**Details:**
- Add the flag in `~/.codex/config.toml`:
  ```toml
  [features]
  default_mode_request_user_input = true
  ```
- The tool description is rewritten dynamically based on the flag: "*This tool is only available in Plan mode.*" when off, vs. "*This tool is only available in Default or Plan mode.*" when on.
- This replaces the prior `collaboration_modes` gate for tool-availability. `collaboration_modes` is now a legacy/no-op flag (always on) for config back-compat.

**Code references:** `request_user_input_is_available()`, `request_user_input_tool_description()` in `core/src/tools/handlers/request_user_input.rs`; `Feature::DefaultModeRequestUserInput` registration in `core/src/features.rs`; `CollaborationModesConfig` plumbed through `ThreadManager::new()`, `MessageProcessor`, exec/MCP/TUI entry points.


### `max_unused_days` for memory consolidation

**What:** A new memory-config knob excludes never-touched memories from phase-2 consolidation after a configurable freshness window.

**Details:**
- Configure in `~/.codex/config.toml`:
  ```toml
  [memories]
  max_unused_days = 30   # default; clamped 0..=365
  ```
- Phase-2 selection now requires either `last_usage >= cutoff` or (for never-used memories) `source_updated_at >= cutoff`, where `cutoff = now - max_unused_days`.
- Eligible rows are ranked by `usage_count DESC, COALESCE(last_usage, source_updated_at) DESC, source_updated_at DESC, thread_id DESC`.
- A new SQL migration (`0018_phase2_selection_snapshot.sql`) adds `selected_for_phase2_source_updated_at` to `stage1_outputs` and a `memory_mode TEXT NOT NULL DEFAULT 'enabled'` column to `threads`.

**Code references:** `MemoriesConfig::max_unused_days` in `core/src/config/types.rs`; `get_phase2_input_selection()` in `state/src/runtime/memories.rs`; `state/migrations/0018_phase2_selection_snapshot.sql`.


### Memory consolidation now uses `Phase2InputSelection` diffs

**What:** The memory phase-2 prompt now contains a deterministic diff of the current Phase-1 inputs against the last successful Phase-2 selection, with explicit `added`, `retained`, and `removed` queues.

**Details:**
- `Phase2InputSelection { selected, previous_selected, retained_thread_ids, removed }` is computed atomically in SQL: `mark_global_phase2_job_succeeded()` rewrites the `selected_for_phase2` baseline transactionally so the next run can compute a clean diff.
- The consolidation prompt explicitly instructs the agent how to handle each diff slice (e.g. ingest "added", surgically delete from `MEMORY.md` for "removed", split mixed blocks rather than dropping them entirely).
- Local artifact sync now writes the union of current + previous selection to `rollout_summaries/` so removed-thread evidence stays available during forgetting.
- Memory consolidation prompts are now rendered through Askama-typed templates rather than string substitution; `CARGO_MANIFEST_DIR` is anchored explicitly in `core/BUILD.bazel` so Bazel builds can resolve the templates.

**Code references:** `Phase2InputSelection` in `state/src/model/memories.rs`; `mark_global_phase2_job_succeeded()` in `state/src/runtime/memories.rs`; `ConsolidationPromptTemplate` and friends in `core/src/memories/prompts.rs`; updated text in `core/templates/memories/consolidation.md`.


### Network policy "Block this host" decision

**What:** The TUI approval overlay can now offer a persistent **Deny** option for network-policy amendments alongside the existing **Allow**.

**Details:** When the agent emits `ReviewDecision::NetworkPolicyAmendment { network_policy_amendment: { action: Deny } }` in `available_decisions`, the overlay renders "*No, and block this host in the future*" bound to `d`.

**Code references:** `exec_options()` in `tui/src/bottom_pane/approval_overlay.rs`.


### Smart file-link rendering in the TUI markdown

**What:** Markdown links to local paths are now rendered as concise inline-code labels with a normalized `:line[:column][-line[:column]]` suffix, instead of expanding to noisy `(file:///…)` parentheticals.

**Details:**
- Local destinations (`file://`, absolute paths, `~/`, `./`, `../`, Windows drive letters, UNC paths) hide the URL and only render the label, styled as inline code.
- Hash-style fragments such as `#L74C3-L76C9` are normalized to `:74:3-76:9` and appended to the label only if the label doesn't already include a location suffix.
- Colon ranges such as `:74:3-76:9` are detected with `COLON_LOCATION_SUFFIX_RE` and reused in the same way.
- Web URLs continue to render with the existing `label (url)` style.

Examples (rendered in the chat history):
- `[markdown_render.rs](/abs/path/markdown_render.rs:74)` → `markdown_render.rs:74`
- `[markdown_render.rs](file:///abs/path/markdown_render.rs#L74C3-L76C9)` → `markdown_render.rs:74:3-76:9`
- `[docs](https://example.com/docs)` → `docs (https://example.com/docs)`

**Code references:** `should_render_link_destination()`, `is_local_path_like_link()`, `LinkState`, `pop_link()` in `tui/src/markdown_render.rs`; `normalize_markdown_hash_location_suffix()` in `utils/string/src/lib.rs`.


### Input-size limit (`MAX_USER_INPUT_TEXT_CHARS = 1 MiB`)

**What:** User messages are now capped at 1,048,576 characters (1 MiB). Oversized inputs are rejected with a structured error before being sent.

**Details:**
- App-server: validates v1 (`SendUserMessage` / `SendUserTurn`) and v2 (`turn/start`, `turn/steer`) inputs and returns JSON-RPC error code `-32602` (`INVALID_PARAMS`) with `input_error_code: "input_too_large"`, plus `max_chars` and `actual_chars` data fields.
- TUI composer: pre-checks the expanded text length on `Enter`, displays an error history cell ("*Message exceeds the maximum length of 1048576 characters (N provided).*"), and restores the original draft, attachments, and cursor so the user can edit instead of losing their input.
- Custom-prompt expansion is checked too: oversized expansions roll back to the typed `/prompts:…` invocation rather than partially submitting.

**Code references:** `MAX_USER_INPUT_TEXT_CHARS` in `protocol/src/user_input.rs`; `validate_v1_input_limit()` / `validate_v2_input_limit()` in `app-server/src/codex_message_processor.rs`; `user_input_too_large_message()` in `tui/src/bottom_pane/chat_composer.rs`; new error codes `INPUT_TOO_LARGE_ERROR_CODE` and `INVALID_PARAMS_ERROR_CODE` in `app-server/src/error_code.rs`.


### JavaScript REPL is now an experimental, user-toggleable feature

**What:** The Node-backed JavaScript REPL feature graduated from `UnderDevelopment` (hidden) to `Experimental`, so users can enable it from `/experimental` in the TUI.

**Details:**
- Menu name: "*JavaScript REPL*". Description: "*Enable a persistent Node-backed JavaScript REPL for interactive website debugging and other inline JavaScript execution capabilities. Requires Node ≥ v22.22.0 installed.*"
- Announcement banner: "*NEW: JavaScript REPL is now available in /experimental. Enable it, then start a new chat or restart Codex to use it.*"
- Codex now performs a startup preflight: if `js_repl` is enabled but the configured Node is missing or below 22.22.0, both `js_repl` and `js_repl_tools_only` are auto-disabled for the session and a startup warning is recorded ("*Disabled `js_repl` for this session because the configured Node runtime is unavailable or incompatible.*").
- The bundled `codex-rs/node-version.txt` was lowered from `24.13.1` to `22.22.0` to match the new minimum.

**Code references:** `Feature::JsRepl` registration in `core/src/features.rs`; `resolve_compatible_node()` in `core/src/tools/js_repl/mod.rs`; preflight in `Codex::spawn` (`core/src/codex.rs`).


### Login: `--device-auth` hint and updated security URL

**What:** `codex login` now points users at device-auth flow when they're on a remote/headless host, and the onboarding security link points to the official docs site.

**Details:**
- Login banner now appends: "*On a remote or headless machine? Use `codex login --device-auth` instead.*"
- Onboarding "Codex docs" hyperlink target changed from `https://github.com/openai/codex` to `https://developers.openai.com/codex/security`.

**Code references:** `print_login_server_start()` in `cli/src/login.rs`; `AuthModeWidget` in `tui/src/onboarding/auth.rs`.


### `gpt-5.3-codex` is the default model in the model picker

**What:** `gpt-5.3-codex` ("*Latest frontier agentic coding model.*") is now the default model surfaced in the TUI model selection popup.

**Details:** Updated ordering: 1) gpt-5.3-codex (default), 2) gpt-5.2-codex, 3) gpt-5.1-codex-max, 4) gpt-5.2, 5) gpt-5.1-codex-mini.

**Code references:** snapshot `tui/src/chatwidget/snapshots/codex_tui__chatwidget__tests__model_selection_popup.snap`.


### `auto` is the new default `reasoning.summary` value

**What:** `Config::model_reasoning_summary` is now `Option<ReasoningSummary>`. When unset, Codex falls back to the new per-model `default_reasoning_summary` field on `ModelInfo`.

**Details:**
- The `/status` and sandbox-summary panels show `"auto"` (TUI) or `"none"` (sandbox) when the field is unset rather than the old hard-coded default.
- Model catalog entries can now ship a per-model default (e.g. `Detailed` for some `gpt-5.1` variants) that is applied automatically.

**Code references:** `Config::model_reasoning_summary` in `core/src/config/mod.rs`; `ModelInfo::default_reasoning_summary` in `protocol/src/openai_models.rs`; `StatusHistoryCell` in `tui/src/status/card.rs`.

### Skill approval flow replaced by generalized session-scoped cache

The dedicated skill-approval prompt has been removed end-to-end:
- Removed: `Feature::SkillApproval`, `Op::SkillApproval`, `EventMsg::SkillRequestApproval`, `SkillRequestApprovalEvent`, `SkillApprovalDecision`, `SkillApprovalResponse`, the `skill/requestApproval` server request, and the matching JSON/TS schemas.
- The `protocol::skill_approval` module is gone; `SkillApprovalCacheKey` and `ensure_skill_approval_for_command()` are gone too.
- Replacement: when a user picks `Approved-for-session` for a skill-script approval, the program path is recorded in `execve_session_approvals` (now keyed by `ExecveSessionApproval { skill }` instead of a bare `HashSet<AbsolutePathBuf>`), and subsequent invocations of the same `program` are auto-approved without a prompt.
- `ApprovedForSession` is only offered as a button when the prompt was triggered by a skill-script invocation; for other shell prompts it is omitted from `available_decisions`.

**Code references:** `ExecveSessionApproval` in `core/src/tools/runtimes/mod.rs`; `EscalationPolicy::resolve_decision()` in `core/src/tools/runtimes/shell/unix_escalation.rs`; deleted `protocol/src/skill_approval.rs`.


### `Feature::Steer` removed; "submit on Enter" is now always-on

The `steer` feature flag has been marked `Stage::Removed`. The previous queuing-by-default fallback has been deleted: pressing **Enter** always submits (or queues during an active turn), and **Tab** always submits the queued input. `set_steer_enabled()` survives only as a no-op test compatibility shim.

**Code references:** `Feature::Steer` in `core/src/features.rs`; `handle_key_event()` and `set_steer_enabled()` in `tui/src/bottom_pane/chat_composer.rs`.


### Resume-by-cwd reads the latest `TurnContext`

When picking the most recent rollout matching a `cwd` filter, Codex now also inspects the rollout file's latest `TurnContext.cwd` (and falls back to full metadata extraction) — so a session that moved its working directory mid-run can still match when you `resume --last` from the new cwd.

**Code references:** `select_resume_path()`, `resume_candidate_matches_cwd()` in `core/src/rollout/recorder.rs`; updated comment in `exec/tests/suite/resume.rs`.


### `TurnContext` no longer overrides session-level `cwd`

Forked threads kept inheriting their parent's working directory after the session-meta line was processed. `apply_turn_context()` now updates `metadata.cwd` only if it was empty, so child-worktree sessions retain their own cwd.

**Code references:** `apply_turn_context()` in `state/src/extract.rs`.


### `thread/status/changed` notification on thread removal

Removing a thread from the watch manager now emits `ThreadStatusChangedNotification { status: NotLoaded }` instead of silently dropping state — keeping client-side loaded-status indicators consistent with the source of truth.

**Code references:** `ThreadWatchState::remove_thread()` in `app-server/src/thread_status.rs`.


### WebSocket `connection_limit_reached` errors are now retryable

When the OpenAI Responses websocket returns the 60-minute connection-limit-reached error, Codex now maps it to `ApiError::Retryable { message, delay: None }` so the client transparently reconnects, instead of failing the turn with an HTTP transport error.

**Code references:** `WEBSOCKET_CONNECTION_LIMIT_REACHED_CODE`, `map_wrapped_websocket_error_event()` in `codex-api/src/endpoint/responses_websocket.rs`.


### Compact requests carry a conversation header

`ModelClient::compact_input()` now sets the conversation-id header in addition to the subagent header, improving server-side prompt-cache locality across compact attempts in the same thread.

**Code references:** `core/src/client.rs`.


### `prefer_websockets` defaults to V2

When a model only opts into websockets via `model_info.prefer_websockets` (and no explicit feature flag), Codex now selects `ResponsesWebsocketVersion::V2` instead of `V1`.

**Code references:** `ModelClient::active_ws_version()` in `core/src/client.rs`.


### Realtime audio observability

Both inbound (`thread/realtime/appendText`) and outbound (`response.output_audio.delta`) text frames now emit `tracing::debug!` events tagged `[realtime-text]`, making it easier to debug realtime sessions without adding `println!`s.

**Code references:** `handle_text()` and `handle_start()` in `core/src/realtime_conversation.rs`.


### `extract_shell_script` handles wrapped argv prefixes

The zsh-fork escalation path no longer assumes the shell is the first argv entry. `extract_shell_script()` now scans for the first `-c` / `-lc` triple anywhere in argv, so wrapper prefixes like `/usr/bin/env CODEX_EXECVE_WRAPPER=1 /bin/zsh -lc …` and `sandbox-exec -p policy /bin/zsh -c …` parse correctly.

**Code references:** `extract_shell_script()` in `core/src/tools/runtimes/shell/unix_escalation.rs`.


### AGENTS.md context-fragment detection consolidated

Detection of session-prefix and contextual user-message fragments (AGENTS.md instructions, `<environment_context>`, `<skill>`, `<user_shell_command>`, `<turn_aborted>`, `<subagent_notification>`) is now centralized in a new `contextual_user_message` module with a uniform `ContextualUserFragmentDefinition`. As part of this, the **legacy `<user_instructions>…</user_instructions>` form is no longer recognized**; AGENTS.md instructions are emitted only in the `# AGENTS.md instructions for <dir>\n\n<INSTRUCTIONS>\n…\n</INSTRUCTIONS>` format.

**Code references:** new `core/src/contextual_user_message.rs`; updated `core/src/instructions/user_instructions.rs`; updated `core/src/session_prefix.rs`.


### Memory consolidation agent renamed

The internal sub-agent that performs memory consolidation is now called **"Morpheus"** (capitalized) instead of "morpheus".

**Code references:** `SessionSource::agent_nickname()` in `protocol/src/protocol.rs`.


### Agent name pool refreshed

The default sub-agent name pool was replaced from tree/plant names (Ash, Elm, Yew, …) with mathematicians/scientists/philosophers (Euclid, Archimedes, Ptolemy, Hypatia, Avicenna, Newton, Turing, Curie, …).

**Code references:** `core/src/agent/agent_names.txt`.


### `awaiter` agent description tightened

The system description now warns the model to "*be patient with the awaiter*" and to "*close the awaiter when you're done with it*", reducing premature timeouts.

**Code references:** `core/src/agent/role.rs`.


### Subagents skip history-metadata loading

`Session::start()` now short-circuits the history-metadata read for subagent sources, eliminating an unnecessary disk hit at sub-agent boot.

**Code references:** `core/src/codex.rs`.


### Memory `read_path` template documents `rollout_path` lookup

The memory-tool developer instructions now describe how `rollout_path` annotations relate to `rollout_summaries/*.md` and recommend matching by `session_meta.payload.id` rather than full-content scans.

**Code references:** `core/templates/memories/read_path.md`.


### `models.json`: legacy model becomes visible

A previously hidden model entry's `"visibility"` flipped from `"hide"` to `"list"`, restoring it to the model picker.

**Code references:** `core/models.json`.


### Skill manager: `extra_user_roots` skips system skills

When extra user skill roots are passed in, system skills are stripped before caching, preventing duplicate or conflicting skills from leaking into per-session configurations.

**Code references:** `SkillsManager` in `core/src/skills/manager.rs`.


### Implicit skill emission moved earlier in shell handling

`maybe_emit_implicit_skill_invocation()` now fires immediately on `ShellCommandHandler` entry, so skill telemetry is captured even when the command is later short-circuited by a cached approval.

**Code references:** `ShellCommandHandler::ToolHandler::handle()` in `core/src/tools/handlers/shell.rs`.


### Compact prompt no longer strips trailing model-switch updates

`run_remote_compact_task` previously stripped trailing model-switch updates from the compaction request and reattached them afterwards; the new injection logic threads `previous_user_turn_model` through `process_compacted_history()` and re-emits the switch as a regular developer-instructions block, simplifying the snapshot shapes.

**Code references:** `core/src/compact_remote.rs`, `core/src/compact.rs`.


### Default-mode template uses an `{{ASKING_QUESTIONS_GUIDANCE}}` placeholder

The Default collaboration-mode prompt now substitutes the question-asking guidance via a placeholder, allowing it to swap in different copy depending on whether `default_mode_request_user_input` is enabled.

**Code references:** `core/templates/collaboration_mode/default.md`.


### Composer footer always shows the queue hint when a task runs

With Steer no longer toggleable, the queue hint at the bottom of the composer now only depends on `is_task_running`. The "queue-hint-disabled" snapshot test was removed.

**Code references:** `FooterProps` in `tui/src/bottom_pane/footer.rs`.


### Status panel renders explicit "auto" reasoning summary

When `model_reasoning_summary` is unset, the `/status` card and `sandbox-summary` config dump now render `"auto"` and `"none"` respectively, instead of an arbitrary derived value.

**Code references:** `tui/src/status/card.rs`; `utils/sandbox-summary/src/config_summary.rs`.


### Build: ARM64 Windows MSVC link arg

Cargo now passes `/arm64hazardfree` for the `aarch64-pc-windows-msvc` target to silence the Cortex-A53 MPCore #843419 warning on a platform that's not affected.

**Code references:** `codex-rs/.cargo/config.toml`.

### `windows-sandbox-setup-completed` notification scoped to caller

`run_windows_sandbox_setup` previously routed its completion notification through `ThreadScopedOutgoingMessageSender`, which now requires a `thread_id`. The completion path now delivers the notification directly to the originating connection via `send_server_notification_to_connections(&[connection_id], …)`.

**Code references:** `app-server/src/codex_message_processor.rs`.


### `thread/archive` reuses the centralized teardown path

Archiving a loaded thread now goes through `wait_for_thread_shutdown()` + `finalize_thread_teardown()` instead of duplicating polling/cleanup logic. This also cancels in-flight server→client requests for the thread before the underlying `Codex` is dropped.

**Code references:** `archive_thread_common()` in `app-server/src/codex_message_processor.rs`.


### `ExecParams` no longer carries `original_command`

The redundant `original_command: String` field was removed; `command: Vec<String>` is the single source of truth. All shell handlers, sandbox runners, exec tests, and the `network-proxy` audit path were updated to recompute the joined string locally when needed.

**Code references:** `ExecParams` in `core/src/exec.rs`; updates in `core/src/tools/handlers/shell.rs`, `linux-sandbox/tests/suite/landlock.rs`, `app-server/src/codex_message_processor.rs`.


### `is_user_turn_boundary` no longer mis-classifies `<user_shell_command>` blocks

The user-turn detector previously had ad-hoc checks for each session-prefix marker. It now delegates to `is_contextual_user_message_content()`, which catches the new `<user_shell_command>` and other contextual markers correctly.

**Code references:** `is_user_turn_boundary()` in `core/src/context_manager/history.rs`.


### TUI exit returns immediately if shutdown submission fails

Before, requesting a "shutdown then exit" while the chat widget could not accept ops would silently leave the app running. The flow now checks `submit_op(Op::Shutdown)`'s return value: if submission fails, the app exits immediately with `ExitReason::UserRequested`; if it succeeds, the app continues until shutdown completion.

**Code references:** `App::handle_exit_mode()` in `tui/src/app.rs`.


### `app-server/src/outgoing_message.rs` correctly cancels per-thread callbacks

Previously, in-flight callbacks (like a pending `request_user_input`) for an unloaded thread could deadlock the client. Each callback is now associated with a `thread_id`, and `cancel_requests_for_thread()` drops every matching entry as part of teardown.

**Code references:** `PendingCallbackEntry`, `cancel_requests_for_thread()` in `app-server/src/outgoing_message.rs`.


### `select_resume_path` no longer misses sessions whose cached cwd is stale

See the corresponding improvement above; sessions that materialized with one cwd but later issued `TurnContext` items with a different cwd are now correctly matched, eliminating false negatives in `resume --last`.

**Code references:** `core/src/rollout/recorder.rs`.


### `extract_shell_script` accepts wrapped invocations

See the corresponding improvement above; a regression where `sandbox-exec`/`/usr/bin/env`-prefixed argvs broke zsh-fork is fixed.

**Code references:** `core/src/tools/runtimes/shell/unix_escalation.rs`.
