# Changelog for version 0.120.0

## Highlights

Codex 0.120.0 brings hooks support to Windows, a polished live-running TUI for hook execution, and renames the realtime delegation tool from `codex` to `background_agent` with proper steering and progress updates while a task is in flight. Guardian automatic-approval reviews gained a stable `reviewId` (separate from `targetItemId`), incremental delta-only follow-up prompts, and a new completion `decisionSource` field. Under the hood, the rollout writer now retries on I/O failure, the exec-server can resume detached sessions across reconnects, the elevated Windows sandbox handles split filesystem policies, and symlinked working directories are now preserved end-to-end instead of being canonicalized away.

### Hooks now run on Windows

**What:** Lifecycle hooks (`hooks.json`) are no longer disabled on Windows.

**Details:**
- Previously, the engine returned an empty handler list on Windows with a warning ("Disabled `codex_hooks` for this session because `hooks.json` lifecycle hooks are not supported on Windows yet.").
- That platform gate has been removed in `ClaudeHooksEngine` so the standard discovery and dispatch path runs on every OS.
- Existing `PreToolUse`, `PostToolUse`, `SessionStart`, `UserPromptSubmit`, and `Stop` hooks now fire on Windows.

**Code references:** `ClaudeHooksEngine` in `hooks/src/engine/mod.rs`.


### Live hook execution cell in the TUI

**What:** A dedicated live "hook" cell renders running hooks alongside any active tool call, with carefully tuned reveal, linger, and persistence rules.

**Details:**
- Brand-new `HookCell` (in `tui/src/history_cell/hook_cell.rs`) renders running hooks underneath the active tool cell instead of as a one-off `info` line in scrollback.
- A reveal delay (300 ms) hides instant hooks; a quiet-linger window (600 ms) prevents successful hooks from flashing and disappearing in the same frame.
- Adjacent running hooks with the same event/status message are coalesced into a single "Running N PostToolUse hooks" line.
- Quiet successes (status `Completed` with no entries) leave no transcript artifact at all; failures, blocked/stopped hooks, and hooks with output are persisted as a normal history cell.
- Animations match the rest of the TUI (shimmer + spinner) when `config.animations` is enabled.

**Code references:** `HookCell`, `new_active_hook_cell()`, `new_completed_hook_cell()` in `tui/src/history_cell/hook_cell.rs`; `on_hook_started()` / `on_hook_completed()` / `flush_completed_hook_output()` in `tui/src/chatwidget.rs`.


### `sessionStartSource` parameter on `thread/start`

**What:** `thread/start` accepts a new optional `sessionStartSource: "startup" | "clear"` field so app-server clients can mark replacement threads created via `/clear` distinctly from the initial startup thread.

**Details:**
- Added `ThreadStartSource` enum (`Startup`, `Clear`) to the v2 protocol; default is `Startup` when omitted.
- The TUI now sends `sessionStartSource: "clear"` from its `/clear` shortcut and `Startup` from `New session`.
- `SessionStart` hooks receive `source: "clear"` (in addition to the existing `startup` and `resume`) so per-event hooks can distinguish a `/clear`-triggered fresh thread.
- Internally `InitialHistory` gained a `Cleared` variant that is treated like `New` for rollout/state purposes but is plumbed through to hooks.

**Code references:** `ThreadStartSource` in `app-server-protocol/src/protocol/v2.rs`; `start_fresh_session_with_summary_hint()` and `App::handle_event_with_dispatcher()` in `tui/src/app.rs`; `SessionStartSource::Clear` in `hooks/src/events/session_start.rs`; `InitialHistory::Cleared` in `protocol/src/protocol.rs`.

**Example (raw JSON-RPC):**

```json
{ "method": "thread/start", "params": {
    "model": "gpt-5",
    "sessionStartSource": "clear"
}}
```


### Realtime delegation tool renamed to `background_agent` with steering

**What:** The realtime function tool that delegates to Codex was renamed from `codex` to `background_agent`, and Realtime V2 now supports steering an in-flight background-agent task with a follow-up tool call.

**Details:**
- The realtime backend now advertises a tool named `background_agent` with a description tailored to a background-agent mental model: "Send a user request to the background agent. Use this as the default action. If the background agent is idle, this starts a new task and returns the final result to the user. If the background agent is already working on a task, this sends the request as guidance to steer that previous task..."
- When the model issues a second `background_agent` call while a task is still running, app-server sends a fixed acknowledgement (`This was sent to steer the previous background agent task.`) back to realtime as the function-call output and follows up with `response.create` so realtime can speak that acknowledgement. The steering text is also threaded into the active Codex task's next Responses request.
- Progress updates from the running task are now forwarded to realtime as conversation items (`<text>\n\nUpdate from background agent (task hasn't finished yet):`) instead of being suppressed in V2.
- After a `background_agent` task finishes, app-server sends the final function-call output and a fresh `response.create` so realtime can react.
- The realtime backend prompt now nudges the model to delegate by default ("Usually, when {{ user }} asks you to do something, they are asking you to delegate work to the backend coding agent.").

**Code references:** `REALTIME_V2_BACKGROUND_AGENT_TOOL_NAME` and `session_update_session()` in `codex-api/src/endpoint/realtime_websocket/methods_v2.rs`; `parse_handoff_requested_event()` in `codex-api/src/endpoint/realtime_websocket/protocol_v2.rs`; `handle_handoff_output()`, `handle_realtime_server_event()`, and `RealtimeResponseCreateQueue` in `core/src/realtime_conversation.rs`; `core/templates/realtime/backend_prompt.md`.


### Guardian review identity separated from reviewed item identity

**What:** Guardian automatic-approval review notifications now include a stable `reviewId` distinct from the target tool item, and the target itself becomes optional.

**Details:**
- `ItemGuardianApprovalReviewStartedNotification` and `ItemGuardianApprovalReviewCompletedNotification` add `reviewId: string` and change `targetItemId` from required string to nullable string.
- `targetItemId` is now `null` for network-policy reviews (which are triggered by a `CommandExecution` item but aren't reviewing the command itself) and for `execve` reviews when no concrete tool item exists.
- `ItemGuardianApprovalReviewCompletedNotification` also gains a required `decisionSource` field (currently `"agent"`) so clients can tell whether the terminal decision came from the guardian agent versus a future user/policy source.
- `GuardianAssessmentEvent` (rollout-level) gained `target_item_id: Option<String>` and `decision_source: Option<GuardianAssessmentDecisionSource>` for the same reason.
- Internally, every guardian review now generates its own UUID via `new_guardian_review_id()`, so cancellation, rejection-message lookup, and OTel tracking all key off the review ID instead of the tool call ID.

**Code references:** `AutoReviewDecisionSource` and notification structs in `app-server-protocol/src/protocol/v2.rs`; `new_guardian_review_id()` and `guardian_request_target_item_id()` in `core/src/guardian/`; `review_approval_request()` callers across `core/src/codex_delegate.rs`, `core/src/mcp_tool_call.rs`, `core/src/tools/network_approval.rs`, `core/src/tools/orchestrator.rs`, `core/src/tools/runtimes/`.


### Guardian delta-only follow-up prompts

**What:** When the same Codex parent thread issues a follow-up guardian review, the prompt now sends only the new transcript entries since the last review instead of the entire transcript.

**Details:**
- New `GuardianPromptMode` (`Full` or `Delta { cursor }`) chooses between the original full prompt and a "TRANSCRIPT DELTA START / END" prompt that continues the prior review conversation.
- A `GuardianTranscriptCursor` (parent history version + entry count) tracks what the guardian already saw; if the parent history was rewritten (e.g., compaction), the prompt automatically falls back to a full transcript.
- Numbering of transcript entries is preserved across deltas (e.g., the delta starts at `[5]` if the prior prompt ended at `[4]`).
- The follow-up reminder is now sent only on the very first follow-up; later follow-ups omit it.
- The follow-up reminder text changed: it now says "set outcome to \"allow\" unless the policy explicitly disallows user overwrites in such cases" instead of "set user_authorization to high and derive outcome from policy".
- Guardian prompts also now embed a `Reviewed Codex session id: <uuid>` line right after the transcript end so reviewers can trace the parent session.

**Code references:** `GuardianPromptItems`, `GuardianPromptMode`, `GuardianTranscriptCursor`, `build_guardian_prompt_items()` in `core/src/guardian/prompt.rs`; `GuardianReviewState`, `run_review_on_session()` in `core/src/guardian/review_session.rs`; updated reminder constant `GUARDIAN_FOLLOWUP_REVIEW_REMINDER` in `core/src/guardian/review_session.rs`.


### Compaction analytics events

**What:** Codex now emits a `codex_compaction_event` analytics event for every compaction attempt, capturing trigger, reason, phase, strategy, status, and active-context token deltas.

**Details:**
- New `CodexCompactionEvent` fact and `track_compaction()` client method in `codex-analytics`.
- Captured dimensions: `trigger` (`manual`/`auto`), `reason` (`user_requested`/`context_limit`/`model_downshift`), `implementation` (`responses`/`responses_compact`), `phase` (`standalone_turn`/`pre_turn`/`mid_turn`), `strategy` (`memento`/`prefix_compaction`), `status` (`completed`/`failed`/`interrupted`), optional `error`, `active_context_tokens_before`/`after`, `started_at`/`completed_at`, and `duration_ms`.
- Fired automatically by both `run_inline_auto_compact_task()` (local memento compaction) and `run_remote_compact_task_inner()` (remote `/responses/compact`). Manual compactions and pre-turn/model-downshift compactions emit distinct event shapes.
- Only emitted when the `GeneralAnalytics` feature is enabled.

**Code references:** `CompactionAnalyticsAttempt` in `core/src/compact.rs`; `track_compaction()` in `analytics/src/client.rs`; `ingest_compaction()` in `analytics/src/reducer.rs`; `CodexCompactionEvent` and friends in `analytics/src/facts.rs`.


### TUI status-line: current thread title

**What:** The customizable status line gains a `ThreadTitle` item that surfaces the user-renamed thread name when set.

**Details:**
- Available in the status-line setup view; description: "Current thread title (omitted unless changed by user)".
- Renders alongside other status segments (e.g., `gpt-5 · Roadmap cleanup`).

**Code references:** `StatusLineItem::ThreadTitle` in `tui/src/bottom_pane/status_line_setup.rs`.


### Exec-server session resume

**What:** The standalone `codex-exec-server` now hands back a `sessionId` from `initialize` and accepts `resumeSessionId` on subsequent connections so an interrupted client can reconnect without losing in-flight processes.

**Details:**
- `InitializeResponse` now carries `session_id: String` (a UUID); `InitializeParams` adds optional `resume_session_id`.
- A new `SessionRegistry` tracks attached sessions with a 10s detached-session TTL; while a session is detached, processes keep running and stdout/stderr keeps buffering, so a reconnect can resume reading where it left off.
- Resuming with a session id that's still attached to another connection returns `session <id> is already attached to another connection`.
- A long-poll `process/read` from the original connection is evicted with `session has been resumed by another connection` after a successful resume.
- Existing background processes (`process/start`/`process/read`/`process/terminate`) are preserved across the reconnect.

**Code references:** `SessionRegistry`, `SessionHandle` in `exec-server/src/server/session_registry.rs`; `ExecServerHandler::initialize()` in `exec-server/src/server/handler.rs`; `ExecServerClient::connect()` in `exec-server/src/client.rs`.


### Code-mode emits a shared `CallToolResult<T>` typedef for MCP tools

**What:** When the exec/code-mode tool description is built and any included tool exposes an MCP-shaped output schema, code-mode now writes the standard MCP `CallToolResult` types once at the top of the description and uses `Promise<CallToolResult<{...}>>` (or `Promise<CallToolResult>`) for individual tool declarations.

**Details:**
- Replaces the verbose inlined return type (e.g., `Promise<{ _meta?: unknown; content: Array<unknown>; isError?: boolean; structuredContent?: unknown; }>`) with `Promise<CallToolResult<{ ... structuredContent fields ... }>>`.
- Adds a single shared TypeScript preamble defining `Annotations`, `TextContent`, `ImageContent`, `AudioContent`, `ResourceLink`, `EmbeddedResource`, `ContentBlock`, and `CallToolResult<TStructured>` based on the [MCP spec](https://modelcontextprotocol.io/specification/draft/schema#calltoolresult).
- Saves substantial prompt tokens when many MCP tools are enabled, and gives the model an accurate type for the wrapper around `structuredContent`.
- Section headers also drop the redundant `(<global_name>)` suffix when the global identifier matches the raw tool name (e.g., `### \`update_plan\`` instead of `### \`update_plan\` (\`update_plan\`)`).

**Code references:** `MCP_TYPESCRIPT_PREAMBLE`, `mcp_structured_content_schema()`, `render_code_mode_sample_for_definition()`, `render_tool_heading()` in `code-mode/src/description.rs`; `collect_code_mode_exec_prompt_tool_definitions()` in `tools/src/code_mode.rs`.

### Realtime V2 `response.create` queueing fixes "active response in progress"

The realtime input task now consistently queues a `response.create` whenever a default response is already active and flushes the queued create after the server emits `response.done` or `response.cancelled`. Previously, the parser conflated `response.created`/`response.done` with generic `ConversationItemAdded` events and could send a `response.create` while one was still running, producing the upstream error `Conversation already has an active response in progress: ...`. New `RealtimeResponseCreated` and `RealtimeResponseDone` realtime events make state transitions explicit, and a small `RealtimeResponseCreateQueue` helper centralizes queuing/flushing.

**Code references:** `RealtimeResponseCreateQueue`, `handle_realtime_server_event()` in `core/src/realtime_conversation.rs`; `parse_realtime_event_v2()` in `codex-api/src/endpoint/realtime_websocket/protocol_v2.rs`; `RealtimeResponseCreated` / `RealtimeResponseDone` in `protocol/src/protocol.rs`.


### Rollout writer retries failed writes and surfaces real I/O errors

The rollout recorder's writer task no longer drops items on a transient I/O error. It now keeps unwritten items buffered, drops the file handle, reopens it on the next persist/flush/shutdown, and retries — so a temporary failure (e.g., a session-dir race) surfaces an error to the caller but the items can still flush successfully on retry.

- `Session::flush_rollout()` now returns `std::io::Result<()>` so callers can react instead of swallowing the error.
- New `RolloutWriterTask` struct exposes a terminal-failure state; if the background writer task itself crashes, subsequent recorder API calls return that error rather than waiting forever.
- Codex emits a `Warning` event with the underlying error if rollback marker flush or end-of-turn flush fails (e.g., "Rolled the thread back, but failed to save the rollback marker. Codex will continue retrying. Error: ...").

**Code references:** `RolloutWriterTask`, `RolloutWriterState`, `write_pending_with_recovery()` in `rollout/src/recorder.rs`; `Session::flush_rollout()` in `core/src/codex.rs`.


### Symlinked working directories are preserved instead of canonicalized away

Codex now keeps the user's logical (symlinked) absolute path for the workspace cwd and sandbox roots whenever the path passes through a non-system symlink, while still canonicalizing top-level system aliases (e.g., macOS `/var → /private/var`).

- New helpers `canonicalize_preserving_symlinks()` and `canonicalize_existing_preserving_symlinks()` in `codex-utils-absolute-path` implement this policy and avoid Windows verbatim (`\\?\`) prefixes.
- TUI startup, `codex exec` startup, sandbox policy normalization, and additional-permission normalization all use the new helpers, so configs that reference `~/work-link/repo` keep that name in error messages, hooks, and the rollout instead of being rewritten to the canonical real path.
- Embedded CLI cwd that doesn't exist now returns `NotFound` early instead of silently using `current_dir()`.

**Code references:** `canonicalize_preserving_symlinks()` and `canonicalize_existing_preserving_symlinks()` in `utils/absolute-path/src/lib.rs`; `config_cwd_for_app_server_target()` in `tui/src/lib.rs`; `run_main()` in `exec/src/lib.rs`.


### Linux bwrap sandbox handles symlinked writable roots

When a writable root is reached through a symlink (e.g., `~/code-link → ~/code-real`), bubblewrap now binds the canonical real target rather than the symlink path itself, and remaps any read-only carveouts and unreadable subpaths to the canonical target. This blocks symlink-replacement attacks (a writable root can't be remounted to a different real target mid-session) while still letting users specify a symlinked workspace root in their config.

- Plain read-only roots are still bound logically (so Bazel runfiles helpers continue to work).
- Protected symlinked-directory carveouts are now remounted at their canonical target with the same path on both sides of `--ro-bind`, instead of being masked with `/dev/null` (which produced file-vs-directory errors).
- Nested unreadable carveouts that resolve outside the writable root are masked at the resolved target with a `--perms 000 --tmpfs --remount-ro` chain.

**Code references:** `canonical_target_if_symlinked_path()`, `remap_paths_for_symlink_target()`, `append_existing_unreadable_path_args()`, `canonical_target_for_symlink_in_path()` in `linux-sandbox/src/bwrap.rs`.


### Windows elevated sandbox supports split filesystem policies

The elevated Windows sandbox backend used to fail closed on any split filesystem policy. It now supports:

- Legacy `ReadOnly` / `WorkspaceWrite` policies (unchanged).
- Restricted-read split policies that pin the readable set to specific roots (e.g., the workspace plus `~/docs` only).
- Split write policies that include extra read-only carveouts under writable roots.
- Proxy-enforced sessions automatically use the elevated backend (firewall enforcement requires the logon-user identity).

The elevated setup payload gains `deny_write_paths`, and the setup-orchestrator binary applies a deny ACE per carveout (creating the directory if missing so the deny ACL exists before the sandboxed command starts). Unsupported scenarios (e.g., explicit unreadable carveouts, reopened writable descendants under read-only carveouts) still fail closed with a precise reason.

**Code references:** `windows_sandbox_uses_elevated_backend()`, `resolve_windows_elevated_filesystem_overrides()`, `WindowsSandboxFilesystemOverrides` in `core/src/exec.rs`; `run_setup_full()` deny-ACE block in `windows-sandbox-rs/src/setup_main_win.rs`; `build_payload_roots()` in `windows-sandbox-rs/src/setup_orchestrator.rs`.


### App-server unloads threads when the last subscriber disconnects

Previously, when a websocket client disconnected without explicitly calling `thread/unsubscribe`, the app-server kept the thread loaded and the listener alive forever. The thread is now torn down (with a `ThreadClosedNotification` to any remaining subscribers) using the same path as `thread/unsubscribe`, freeing memory and the underlying Codex worker. New websocket regression test (`websocket_disconnect_unloads_last_subscribed_thread`) verifies that a fresh connection sees zero loaded threads after the previous owner disconnects.

**Code references:** `unload_thread_without_subscribers()`, `connection_closed()` in `app-server/src/codex_message_processor.rs`; updated `ThreadStateManager::remove_connection()` returning `Vec<ThreadId>` in `app-server/src/thread_state.rs`.


### Hook run IDs include `tool_use_id`

Pre/post-tool-use hook runs now generate run IDs of the form `pre-tool-use:<idx>:<source>:<tool_use_id>` (e.g., `post-tool-use:0:/tmp/hooks.json:tool-call-456`). This lets the TUI and analytics distinguish parallel hook executions of the same handler against different tool calls — important for the new live hook cell, which dedupes runs by ID.

**Code references:** `hook_run_for_tool_use()` and `hook_completed_for_tool_use()` in `hooks/src/events/common.rs`; `preview()` and `run()` in `hooks/src/events/pre_tool_use.rs` and `hooks/src/events/post_tool_use.rs`.


### Spawn-agent / send-message / followup-task / wait-agent / list-agents tool docs

The MultiAgent V2 tool descriptions were rewritten to be concrete and example-driven:

- `spawn_agent` (V2) now describes canonical task names with an example ("If your current task is `/root/task1` and you spawn_agent with task_name \"task_3\" the agent will have canonical task name `/root/task1/task_3`"), explains tool inheritance, and clarifies that the new agent's canonical task name is provided to it along with the message. Replaces the old generic two-sentence summary.
- `send_message` is now described as "Send a string message to an existing agent without triggering a new turn." (no longer mentions MultiAgentV2-text-only caveat).
- `followup_task` clarifies that with `interrupt=false`, "if the target is already running, it starts the target's next turn after the current turn completes."
- `wait_agent` is explicit that it "Does not return the content; returns either a summary of which agents have updates (if any), or a timeout summary if no mailbox update arrives before the deadline." Stops recommending "longer waits (minutes) to avoid busy polling" in favor of just listing min/default/max.
- `list_agents` clarifies that `path_prefix` should not end with a trailing slash.
- `fork_turns` parameter docs now say "Defaults to `all`" so callers know what they get when the field is omitted.

**Code references:** `spawn_agent_tool_description_v2()`, `create_send_message_tool()`, `create_followup_task_tool()`, `create_wait_agent_tool_v2()`, `create_list_agents_tool()` in `tools/src/agent_tool.rs`.


### Tool-search results preserve discovery order

`collect_tool_search_output_tools()` now groups by namespace while preserving insertion order from the underlying ranking, so the tool-search response matches the order tools were actually discovered (e.g., a high-relevance Gmail tool stays before lower-ranked Calendar tools when grouped by namespace).

**Code references:** `collect_tool_search_output_tools()` in `tools/src/tool_discovery.rs`.


### MCP tool-result schema uses concrete object types

The output schema generator for MCP tools (`mcp_call_tool_result_output_schema`) now declares `content.items` and `_meta` as `{"type": "object"}` instead of empty schemas, so JSON-Schema validators and the code-mode TS renderer can recognize them as the structured MCP content shape.

**Code references:** `mcp_call_tool_result_output_schema()` in `tools/src/mcp_tool.rs`.


### Realtime app-server-client uses rustls correctly

`RemoteAppServerClient::connect()` now calls `ensure_rustls_crypto_provider()` before attempting the websocket TLS handshake, fixing remote app-server TLS connections that previously failed because no default rustls crypto provider was installed.

**Code references:** `RemoteAppServerClient::connect()` in `app-server-client/src/remote.rs`.


### Config write/read pipelining is observable

`thread/start` followed immediately by `config/read` now reliably observes the just-written value. Verified by a new test (`config_read_after_pipelined_write_sees_written_value`) that pipelines a `config/value/write` followed by a `config/read` without waiting for the write response.

**Code references:** new test in `app-server/tests/suite/v2/config_rpc.rs`.

### Realtime V2 audio mute on `response.cancelled`

Realtime V2 used to leak `output_audio_state` when a response was cancelled, which could leave the next response truncating against the wrong item id. Both `response.cancelled` and `response.done` now clear `output_audio_state` and flush any queued `response.create`, so cancelled-then-resumed sessions speak again.

**Code references:** `handle_realtime_server_event()` `RealtimeEvent::ResponseCancelled` / `RealtimeEvent::ResponseDone` arms in `core/src/realtime_conversation.rs`.


### Guardian rationale lookup keyed off the right id

Guardian rejection messages used to be cached under the tool call id, which collided across reviews of the same call (e.g., a sandbox retry of the same shell command). They are now keyed by `review_id`, so each review's rationale is reported independently and cleared on success.

**Code references:** `guardian_rejection_message()` in `core/src/guardian/review.rs`; `mcp_tool_approval_decision_from_guardian()` in `core/src/mcp_tool_call.rs`; `network_approval` and `orchestrator` consumers.


### exec-server `LocalProcess` initialization no longer panics in tests

`Environment::default()` previously called `LocalProcess::initialize()` and `LocalProcess::initialized()` eagerly, which panicked if the same Environment was constructed twice (e.g., in test harnesses) because initialization could only run once. The default now constructs an uninitialized `LocalProcess`, and the new `SessionRegistry` handles per-session lifecycle properly.

**Code references:** `Environment::default()` and `Environment::from_environment()` in `exec-server/src/environment.rs`; `LocalProcess::set_notification_sender()` in `exec-server/src/local_process.rs`.


### `thread_history` test fixture matches the new GuardianAssessmentEvent shape

The protocol-level fixtures for guardian assessments now exercise `target_item_id`, `decision_source`, and the new "review-prefixed" id format end-to-end, so future protocol changes can't silently drift from the wire format.

**Code references:** `app-server-protocol/src/protocol/thread_history.rs`.


### `command_cwd` failure surfaces from CLI startup

Both the TUI (`config_cwd_for_app_server_target`) and `codex exec` (`run_main`) now propagate "no such directory" errors via `canonicalize_existing_preserving_symlinks()` instead of falling back to `std::env::current_dir()` when the user passed an explicit but missing `--cwd`. New test: `config_cwd_for_app_server_target_errors_for_missing_embedded_cli_cwd`.

**Code references:** `config_cwd_for_app_server_target()` in `tui/src/lib.rs`; `run_main()` in `exec/src/lib.rs`.


### Rollout file is materialized when flush has pending items

A deferred (in-memory) rollout used to skip materialization on `flush()` and only honor `persist()`. The writer now opens and writes the file when `flush()` is called with pending items, matching the new "retry writes through reopen" recovery model. Existing test renamed and updated: `recorder_materializes_on_flush_with_pending_items`.

**Code references:** `RolloutWriterState::flush()` and `write_pending_with_recovery()` in `rollout/src/recorder.rs`; updated test in `rollout/src/recorder_tests.rs`.
