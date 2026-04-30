# Changelog for version 0.114.0

## Highlights

This release introduces a **Claude-style hooks system** that lets Codex run shell commands at well-defined session and turn lifecycle events, **session-scoped permission grants** so users no longer have to re-approve operations every turn, and **streaming transcript deltas** for the realtime API. The app-server's WebSocket transport was rebuilt on `axum` and now exposes `/healthz` and `/readyz` HTTP probes, an experimental **Code Mode** JavaScript runner was added behind a feature flag, and several important sandbox-translation and concurrency bugs were fixed.

### Lifecycle Hooks System (Claude-Compatible)

**What:** A brand-new lifecycle-hooks engine that runs shell commands at well-defined points in a session — modeled directly after Claude Code's hooks contract.

**Details:**
- Gated behind a new feature flag `codex_hooks` (`Feature::CodexHooks`, `Stage::UnderDevelopment`, off by default), defined in `codex-rs/core/src/features.rs`.
- Two event types are supported in this release: **`SessionStart`** (fires when a new session is created, resumed, or forked) and **`Stop`** (fires before each turn completes — and can block the turn from completing).
- Configuration lives in `hooks.json` files alongside any Codex config layer (project, user, or system). Example:
  ```json
  {
    "hooks": {
      "SessionStart": [
        {
          "matcher": "*",
          "hooks": [
            {
              "type": "command",
              "command": "/usr/local/bin/log-session-start.sh",
              "timeout": 600,
              "async": false,
              "statusMessage": "Recording session start"
            }
          ]
        }
      ],
      "Stop": [ ... ]
    }
  }
  ```
- Hook commands receive event JSON on stdin. `SessionStart` payloads include `session_id`, `transcript_path`, `cwd`, `model`, and `permission_mode`. `Stop` payloads add a `stop_hook_active` flag (used to prevent infinite loops where a Stop hook blocks itself).
- Hook stdout is parsed for control flags: `continue`, `stopReason`, `suppressOutput`, `systemMessage`, `decision: "block"` (Stop only — the model is re-prompted with the block reason and the turn does not complete), and `hookSpecificOutput.additionalContext` (SessionStart — injected as a developer message into the conversation).
- Three handler types are recognized in the schema: `command` (fully implemented), `prompt`, and `agent` (declared but currently produce a warning when invoked). Hooks declared `async: true` are also currently skipped with a warning.
- Default per-hook timeout is 600 seconds, minimum 1 second.
- TUI users see inline history cells like "Running SessionStart hook: ..." plus per-entry breakdowns labelled `warning:`, `stop:`, `feedback:`, `hook context:`, and `error:`. Non-interactive `codex exec` users see a compact stderr render that stays silent for successful no-output runs.
- Hook events also surface on the wire: new `EventMsg::HookStarted` / `EventMsg::HookCompleted` events for the legacy protocol and `hook/started` / `hook/completed` server notifications for v2.
- The pre-existing `notify` mechanism still works — it was simply moved to `codex-rs/hooks/src/legacy_notify.rs`.

**Code references:** `discover_handlers()` in `codex-rs/hooks/src/engine/discovery.rs`; `run_turn()` and the SessionStart/Stop integration points in `codex-rs/core/src/codex.rs`; `on_hook_started()` / `on_hook_completed()` in `codex-rs/tui/src/chatwidget.rs`; `render_hook_started()` / `render_hook_completed()` in `codex-rs/exec/src/event_processor_with_human_output.rs`; protocol types `HookRunSummary`, `HookEventName`, `HookHandlerType`, `HookExecutionMode`, `HookScope`, `HookRunStatus`, `HookOutputEntryKind` in `codex-rs/protocol/src/protocol.rs`.


### Session-Scoped Permission Grants

**What:** The TUI permission approval prompt now offers a third option: grant the requested permissions for the entire session (not just the current turn).

**Details:**
- The approval overlay now shows three choices instead of two:
  - **`y`** — "Yes, grant these permissions" (turn-scoped, unchanged behavior)
  - **`a`** — "Yes, grant these permissions for this session" (**new**)
  - **`n`** — "No, continue without permissions"
- A new protocol type `PermissionGrantScope { Turn, Session }` (defaulting to `Turn` for backward compatibility) is added to `RequestPermissionsResponse`.
- Session-scoped grants are stored on `Session::state` and are reapplied on every subsequent turn, including by the apply-patch handler.
- The `request_permissions` tool description was updated to mention session scope: "or for the rest of the session if the client approves them at session scope".
- After approving at session scope, the TUI shows the confirmation banner: "You granted additional permissions for this session".

**Code references:** `PermissionGrantScope` in `codex-rs/protocol/src/request_permissions.rs`; `permissions_options()` in `codex-rs/tui/src/bottom_pane/approval_overlay.rs`; `notify_request_permissions_response()` and `granted_session_permissions()` in `codex-rs/core/src/codex.rs`; `apply_patch.rs` in `codex-rs/core/src/tools/handlers/`.


### `Reject.request_permissions` Approval Sub-Flag

**What:** A new boolean on `AskForApproval::Reject` that auto-denies the built-in `request_permissions` tool without prompting the user — useful for non-interactive harnesses that want to keep the model on-rails without surfacing permission prompts.

**Details:**
- When `request_permissions: true` is set under `Reject`, the harness immediately returns an empty granted profile (`PermissionGrantScope::Turn`) without sending an `item/permissions/requestApproval` notification to the client.
- Defaults to `false` for full backward compatibility with older clients.
- Documented in the app-server README: "If the session approval policy uses `Reject` with `request_permissions: true`, the server does not send `item/permissions/requestApproval` to the client."

**Code references:** `RejectConfig` in `codex-rs/protocol/src/protocol.rs`; `Session::request_permissions()` in `codex-rs/core/src/codex.rs`; v2 `AskForApproval::Reject` shape in `codex-rs/app-server-protocol/src/protocol/v2.rs`.


### Realtime API Transcript Deltas

**What:** The realtime websocket API now streams transcript text incrementally for both user input and model output, and accumulates an "active transcript" that gets attached to handoff requests.

**Details:**
- Two new realtime events:
  - **`InputTranscriptDelta`** — incremental text from user microphone transcription (`conversation.input_transcript.delta` on the wire).
  - **`OutputTranscriptDelta`** — incremental text from the model's audio output transcription (`conversation.output_transcript.delta` on the wire).
- The handoff payload was reshaped: `RealtimeHandoffMessage` was renamed to `RealtimeTranscriptEntry`, and `RealtimeHandoffRequested.messages` became `active_transcript` — a `Vec<{role, text}>` that is built up from the delta stream as the conversation progresses.
- This lets clients render a live transcript in the UI and ensures handoff messages contain the accumulated dialogue rather than a single role/text pair.

**Code references:** `RealtimeEvent` and `RealtimeTranscriptDelta` in `codex-rs/protocol/src/protocol.rs`; `RealtimeWebsocketEvents` and `update_active_transcript()` in `codex-rs/codex-api/src/endpoint/realtime_websocket/methods.rs`; protocol parsing in `codex-rs/codex-api/src/endpoint/realtime_websocket/protocol.rs`.


### WebSocket App-Server HTTP Health Endpoints

**What:** The `--listen ws://...` app-server transport was rebuilt on `axum`, and the same listener now serves HTTP health probes alongside the WebSocket endpoint.

**Details:**
- `GET /readyz` returns `200 OK` once the listener is accepting connections — useful for k8s readiness probes.
- `GET /healthz` returns `200 OK` for liveness checks.
- The startup banner now prints both URLs in addition to the WebSocket URL.
- Underlying transport switched from raw `tokio-tungstenite` to `axum::extract::ws`, which also unifies the upgrade and request-handling stacks.

**Code references:** `start_websocket_acceptor()` in `codex-rs/app-server/src/transport.rs`; updated documentation in `codex-rs/app-server/README.md`.


### Out-of-Band Elicitation Pause API (Experimental)

**What:** New v2 RPC methods that let external helpers pause unified-exec timeouts while a user-approval is pending outside the normal app-server request flow.

**Details:**
- New v2 methods:
  - **`thread/increment_elicitation`** — pauses unified-exec deadline timers. Returns `{count, paused}`.
  - **`thread/decrement_elicitation`** — decrements; once the count returns to 0, deadlines resume.
- While paused, both yield and post-exit deadlines are extended in unified exec, preventing the default 10-second yield from killing helpers (e.g. a sudo prompt) that are waiting on user interaction.
- New CLI test commands `thread-increment-elicitation`, `thread-decrement-elicitation`, and `live-elicitation-timeout-pause` make it easy to exercise the API end-to-end.

**Code references:** `CodexThread::increment_out_of_band_elicitation_count()` / `decrement_out_of_band_elicitation_count()` in `codex-rs/core/src/codex_thread.rs`; `extend_deadlines_while_paused()` and `wait_for_pause_change()` in `codex-rs/core/src/unified_exec/process_manager.rs`; CLI commands in `codex-rs/app-server-test-client/src/lib.rs`; demo script `codex-rs/app-server-test-client/scripts/live_elicitation_hold.sh`.


### Code Mode JavaScript Runner (Experimental)

**What:** A new freeform tool called `code_mode` that lets the model write and execute JavaScript directly using Node's built-in `node:vm`, intended as a leaner alternative to `js_repl`.

**Details:**
- Gated behind the new `code_mode` feature flag (`Feature::CodeMode`, `Stage::UnderDevelopment`, default off).
- The model writes raw JavaScript (no JSON wrapping, no fences). Within the script, helpers such as `await tools.exec_command({...})` and `add_content(value)` are exposed — only values passed to `add_content` are surfaced back to the model.
- Auto-disables itself with a startup warning if Node is unavailable or incompatible. Reuses the existing `js_repl_node_path` config knob.
- Adds a developer-instructions section so the model knows how to use the tool.
- Exec output for nested tool calls is structured (`ExecCommandToolOutput`) so the JS bridge can consume it.

**Code references:** `codex-rs/core/src/tools/code_mode.rs`, `codex-rs/core/src/tools/code_mode_bridge.js`, `codex-rs/core/src/tools/code_mode_runner.cjs`; tool handler `codex-rs/core/src/tools/handlers/code_mode.rs`; `Feature::CodeMode` in `codex-rs/core/src/features.rs`; startup auto-disable check in `codex-rs/core/src/codex.rs`.


### Bundled Skills On/Off Switch

**What:** A new configuration option to disable Codex's bundled (system-scope) skills entirely.

**Details:**
- Add to `config.toml`:
  ```toml
  [skills.bundled]
  enabled = false
  ```
- When disabled, `SkillsManager::new` calls `uninstall_system_skills()` and excludes the `SkillScope::System` root from skill discovery — so users see only their own/project skills.
- Defaults to `true`; existing setups are unaffected.
- The flag is also serializable from `ConfigProfile`.

**Code references:** `BundledSkillsConfig` in `codex-rs/core/src/config/types.rs`; `Config::bundled_skills_enabled()` in `codex-rs/core/src/config/mod.rs`; `SkillsManager::new()` in `codex-rs/core/src/skills/manager.rs`; schema entry in `codex-rs/core/config.schema.json`.

### Apps / ChatGPT Connectors Gated on ChatGPT Auth

The `Apps` feature is no longer enabled merely by the feature flag — it now also requires the user to be signed in with ChatGPT auth. Users authenticated via API key will not see Apps surfaced in the TUI mention popup, MCP inventory, or BM25 search description, regardless of `features.apps`.

**Code references:** `Features::apps_enabled()`, `apps_enabled_cached()`, `apps_enabled_for_auth()` in `codex-rs/core/src/features.rs`; new `CodexAuth::is_api_key_auth()` and `get_chatgpt_user_id()` helpers in `codex-rs/core/src/auth.rs`; call-site updates in `codex-rs/core/src/codex.rs`, `codex-rs/chatgpt/src/connectors.rs`, `codex-rs/core/src/connectors.rs`, `codex-rs/core/src/mcp/mod.rs`, `codex-rs/app-server/src/codex_message_processor.rs`, and `codex-rs/tui/src/chatwidget.rs`.


### Apps Popup Loading State and Selection Preservation

The "Apps" mention popup now shows a dedicated loading state ("Loading installed and available apps...") on first open instead of the old "Apps are still loading." info line. Refreshes preserve cursor/selection: if you had an app highlighted, it stays highlighted after the connectors snapshot updates. Partial snapshots are kept around so a failed final fetch falls back to whatever was loaded so far.

**Code references:** `open_connectors_loading_popup()`, `connectors_popup_params()`, and `connectors_partial_snapshot` in `codex-rs/tui/src/chatwidget.rs`; new `BottomPaneView::selected_index()` and updated `list_selection_view.rs` in `codex-rs/tui/src/bottom_pane/`; snapshot `apps_popup_loading_state.snap`.


### Mention Popup Type Prefixes

Every mention in the TUI popup is now categorized with a `[Plugin]`, `[Skill]`, or `[App]` prefix in its description, instead of conditionally hiding the type. Mentions are sorted by `sort_rank` so plugins appear first, then skills/apps. This makes it easier to scan a long list and tell at a glance what kind of thing you're about to mention.

**Code references:** `codex-rs/tui/src/bottom_pane/chat_composer.rs` and `skill_popup.rs`; snapshot `mention_popup_type_prefixes.snap`.


### Stricter "Fast" Status-Line Indicator

The TUI's "Fast" indicator in the status line now requires the active model to be `gpt-5.4` (a new `FAST_STATUS_MODEL` constant) in addition to `service_tier=Fast` and ChatGPT auth. Previously any model running on the Fast tier showed the indicator, which could be misleading.

**Code references:** `should_show_fast_status(model, service_tier)` and `FAST_STATUS_MODEL` in `codex-rs/tui/src/chatwidget.rs`.


### Forward-Compatible Filesystem `:special_path` Tokens

Codex 0.113.0 rejected unknown `:foo`-style filesystem tokens at config load, which made config files written for newer versions unusable. Codex 0.114.0 now accepts them, ignores the matching path at runtime, and emits a startup warning instead:

> Configured filesystem path `:future_special_path` is not recognized by this version of Codex and will be ignored. Upgrade Codex if this path is required.

Empty/missing `[permissions.X.filesystem]` tables are likewise treated as a fully restricted profile with a warning, instead of being a hard error.

**Code references:** `FileSystemSpecialPath::Unknown` in `codex-rs/protocol/src/permissions.rs`; `parse_special_path()` in `codex-rs/core/src/config/permissions.rs`.


### Structured Exec Tool Output

`exec_command` and `write_stdin` now publish a JSON output schema in their tool spec and return structured output (`ExecCommandToolOutput`) with explicit Chunk ID, Wall time, Process, and Original token count sections. Nested tool calls (e.g. from Code Mode) consume the structured form directly instead of re-parsing free-form text.

**Code references:** `ExecCommandToolOutput` impl in `codex-rs/core/src/tools/context.rs`; output-schema fields in `codex-rs/core/src/tools/spec.rs`; `ToolHandler` generic over `Output: ToolOutput` in `codex-rs/core/src/tools/registry.rs`.


### BM25 Search Tool Description

When no apps are enabled, the `search` tool description now reads `(None currently enabled)` instead of producing a confusing empty parenthetical from an unsubstituted `({{app_names}})` template.

**Code references:** `create_search_tool_bm25_tool()` in `codex-rs/core/src/tools/spec.rs`.

### WorkspaceWrite + Readable-Roots Sandbox Translation

When translating the legacy `WorkspaceWrite` sandbox policy into the new split filesystem policy used by seatbelt/landlock, readable roots that fell underneath an already-writable root were being kept and turned into spurious read-only carve-outs — effectively downgrading writable areas to read-only. The new `FileSystemSandboxPolicy::from_legacy_sandbox_policy(policy, cwd)` strips redundant readable roots before producing the split policy. A `SessionConfiguration::apply` regression where a cwd-only update could clobber a richer split policy with a re-derived legacy one was also fixed.

**Code references:** `FileSystemSandboxPolicy::from_legacy_sandbox_policy()` in `codex-rs/protocol/src/permissions.rs`; new test `seatbelt_legacy_workspace_write_nested_readable_root_stays_writable` in `codex-rs/core/src/seatbelt.rs`; `SessionConfiguration::apply()` in `codex-rs/core/src/codex.rs`.


### Concurrent `getpwuid` Crash on musl

Parallel callers of `get_user_shell_path` could segfault on the musl static build of the CLI because of a shared internal buffer in `getpwuid`. The function now uses `getpwuid_r` with caller-owned storage and retries on `ERANGE` up to 1 MB. (Also fixes a typo: `finds_poweshell` → `finds_powershell`.)

**Code references:** `get_user_shell_path()` in `codex-rs/core/src/shell.rs`.


### Stale `InProgress` Turn Status After Reconnect

When a `thread/read` or thread resume reported a non-Active thread status but the persisted turn list still had turns marked `InProgress`, those turns are now flipped to `Interrupted`. The fix also factors in live agent status (`agent_status() == Running`), so genuinely-running turns aren't mis-flagged as interrupted.

**Code references:** `set_thread_status_and_interrupt_stale_turns()` and `has_live_in_progress_turn()` in `codex-rs/app-server/src/codex_message_processor.rs`.


### Reject Auto-Deny Response Default

The Reject reasons returned to the client when the harness auto-denies a permission request now include the new `scope` field defaulting to `Turn`. Without this default, older clients hitting a server with the new field would fail to deserialize the response.

**Code references:** `codex-rs/app-server/src/bespoke_event_handling.rs`; `codex-rs/core/src/codex_delegate.rs`.


### Shell-Escalation Socket Cleanup Tests

`shell-escalation` tests now actually verify the after-spawn hook runs by checking the `client_socket` lock instead of relying on raw FD assertions, which were flaky.

**Code references:** `codex-rs/shell-escalation/src/unix/escalate_server.rs`.
