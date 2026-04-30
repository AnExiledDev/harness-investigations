# Changelog for version 0.104.0

## Highlights

This release adds new server-side notifications for thread archive/unarchive operations and introduces a richer approval-id mechanism that lets clients route subcommand approvals (e.g. zsh-exec-bridge / execve interception) independently from their parent command. The TUI's "resume/fork" workflow now lets users actually exit at the cwd-selection prompt instead of being forced into a session, the network proxy understands websocket-specific environment variables, and the model-mismatch warning is now case-insensitive so capitalization-only differences in `OpenAI-Model` headers no longer trigger spurious reroute warnings.

### Thread Archive/Unarchive Notifications

**What:** The app server now emits `thread/archived` and `thread/unarchived` server-to-client notifications whenever a thread changes archival state. Previously, callers received only the JSON-RPC response to their `thread/archive` or `thread/unarchive` request — there was no broadcast event for other interested clients (or for the same client's UI to react to in the notification stream).

**Details:**
- New `ThreadArchivedNotification { threadId }` type is dispatched after a successful `thread/archive` request.
- New `ThreadUnarchivedNotification { threadId }` type is dispatched after a successful `thread/unarchive` request.
- Both notifications are part of the v2 protocol and listed in the server's union of notification methods alongside `thread/started`, `thread/name/updated`, and others.
- TypeScript bindings and JSON schemas are generated for both new notification types.

**Example wire flow:**
```json
{ "method": "thread/archive", "id": 21, "params": { "threadId": "thr_b" } }
{ "id": 21, "result": {} }
{ "method": "thread/archived", "params": { "threadId": "thr_b" } }
```

```json
{ "method": "thread/unarchive", "id": 24, "params": { "threadId": "thr_b" } }
{ "id": 24, "result": { "thread": { "id": "thr_b" } } }
{ "method": "thread/unarchived", "params": { "threadId": "thr_b" } }
```

**Code references:**
- `ThreadArchivedNotification` / `ThreadUnarchivedNotification` in `app-server-protocol/src/protocol/v2.rs`
- Notification dispatch in `archive_thread` and `unarchive_thread` handlers in `app-server/src/codex_message_processor.rs`
- New tests `thread_archive_requires_materialized_rollout` and `thread_unarchive_moves_rollout_back_into_sessions_directory` in `app-server/tests/suite/v2/thread_archive.rs` and `thread_unarchive.rs` assert the notification is emitted.


### Distinct `approvalId` Field for Subcommand Approvals

**What:** Approval requests now carry a separate optional `approvalId` (a UUID) in addition to the parent `callId` / `itemId`. This lets a single command item produce multiple independent approval callbacks — necessary for the zsh-exec-bridge and execve-intercept paths where a single shell invocation may issue several subcommand approvals.

**Details:**
- For ordinary shell / unified_exec approvals, `approvalId` is `null` (unchanged behavior; clients keep using `callId`).
- For subcommand approvals via execve interception, `approvalId` is a distinct opaque UUID. Multiple callbacks may share one parent `itemId` and are routed by `approvalId`.
- Added to `ExecCommandApprovalParams` (v1), `CommandExecutionRequestApprovalParams` (v2), and the `ExecApprovalRequestEvent`.
- A new helper `effective_approval_id()` returns `approval_id` if set, otherwise falls back to `call_id`, so existing call sites can compute the right key without branching.
- When an approval response arrives for a subcommand whose parent command is already running (`command_execution_started` set), the app server now suppresses emitting a duplicate completion `item/completed` for that callback — only the parent's completion item is authoritative.

**Example v2 request payload:**
```json
{
  "method": "item/commandExecution/requestApproval",
  "params": {
    "threadId": "thr_a",
    "turnId": "turn_3",
    "itemId": "call_42",
    "approvalId": "9f1c…UUID",
    "command": "rm -rf node_modules",
    "cwd": "/repo",
    "reason": "subcommand intercepted"
  }
}
```

**Code references:**
- `ExecApprovalRequestEvent::effective_approval_id()` in `protocol/src/approvals.rs`
- `request_command_approval()` signature change (now takes `approval_id: Option<String>`) in `core/src/codex.rs`
- Subcommand-completion suppression logic via `TurnSummary::command_execution_started` in `app-server/src/thread_state.rs` and `app-server/src/bespoke_event_handling.rs`
- `handle_exec_approval` plumbing in `core/src/codex_delegate.rs` and `mcp-server/src/codex_tool_runner.rs`


### Websocket Proxy Environment Variables

**What:** The Codex network proxy now sets and recognizes `WS_PROXY` / `WSS_PROXY` (and lowercase variants) in addition to `HTTP_PROXY` / `HTTPS_PROXY`. Tools that consult dedicated websocket-proxy variables — instead of falling back to the HTTP(S) settings — will now be routed through the managed proxy automatically.

**Details:**
- `WS_PROXY` and `WSS_PROXY` were added to `PROXY_URL_ENV_KEYS`, so detection of pre-existing proxy config considers them.
- `apply_proxy_env_overrides()` now writes the same managed-proxy URL to `WS_PROXY`, `WSS_PROXY`, `ws_proxy`, and `wss_proxy` whenever it sets `HTTP_PROXY`/`HTTPS_PROXY`.
- The README is updated with the recommended export block:

```bash
export HTTP_PROXY="http://127.0.0.1:3128"
export HTTPS_PROXY="http://127.0.0.1:3128"
export WS_PROXY="http://127.0.0.1:3128"
export WSS_PROXY="http://127.0.0.1:3128"
```

- The README also clarifies that websocket clients tunneling `wss://` through HTTPS `CONNECT` still go through the host allowlist/denylist checks.

**Code references:**
- `WEBSOCKET_PROXY_ENV_KEYS` constant in `network-proxy/src/proxy.rs`
- New tests `has_proxy_url_env_vars_detects_websocket_proxy_keys` and additional assertions in `apply_proxy_env_overrides_sets_common_tool_vars`
- Documentation in `network-proxy/README.md`

### Case-Insensitive Server-Model Comparison

The server-vs-requested model check in `Session::should_warn_for_model_mismatch` now lowercases both sides before comparing. Previously, an `OpenAI-Model` response header that differed only in capitalization (e.g. `GPT-5-Codex` vs `gpt-5-codex`) would be treated as a mismatch and trigger a `ModelReroute` event plus a "potentially high-risk cyber activity" warning. Now those responses match silently.

A new test `openai_model_header_casing_only_mismatch_does_not_warn` in `core/tests/suite/safety_check_downgrade.rs` asserts no reroute or warning is emitted when only casing differs. See `should_warn_for_model_mismatch()` in `core/src/codex.rs`.


### Server-Model Field Removed in Favor of Headers

`ResponsesStreamEvent::response_model()` no longer reads the `response.model` field at all. It now only inspects headers — first `response.headers["openai-model"]`, then top-level `headers["openai-model"]` for websocket metadata events such as `codex.response.metadata`. The previous `extract_server_model()` helper that fell back to `response.model` has been deleted. Tests that previously asserted a `ServerModel` event was emitted from the `response.model` payload now assert the field is ignored (e.g. `process_sse_ignores_response_model_field_in_payload`).

This unifies how server-side model identity is reported and aligns with the new header-only assertions throughout the safety-check suite, where mock responses now place the model under `response.headers["OpenAI-Model"]` instead of the now-ignored `response.model`. See `response_model()` in `codex-api/src/sse/responses.rs`.


### Ctrl-C / Ctrl-D in the Resume/Fork CWD Prompt Now Exits

When you resume or fork a session whose recorded cwd differs from your current directory, the TUI shows a prompt asking which cwd to use. Previously, pressing `Ctrl-C` or `Ctrl-D` at this prompt silently fell back to the session cwd and proceeded into the session. Now those keys properly cancel the operation and exit the app with `ExitReason::UserRequested`.

A new outcome enum `CwdPromptOutcome { Selection, Exit }` is returned from `run_cwd_selection_prompt`, and the call site in `tui/src/lib.rs` and `tui/src/app.rs` propagates the `Exit` variant out as an app-exit. A new unit test `cwd_prompt_ctrl_c_exits_instead_of_selecting` covers the new behavior. See `CwdPromptScreen::handle_key()` in `tui/src/cwd_prompt.rs` and `ResolveCwdOutcome` in `tui/src/lib.rs`.


### MCP Server No Longer Drops `ModelReroute` Events

In `mcp-server/src/codex_tool_runner.rs`, the explicit `EventMsg::ModelReroute(_) => continue;` short-circuit was removed. `ModelReroute` events are now handled like other "structured but not bespoke" events, falling through to the catch-all branch alongside `ContextCompacted`, `RequestUserInput`, and others. Clients of the MCP-mode tool will now see model-reroute notifications instead of having them silently swallowed.


### HTTP CONNECT Allowlist/Denylist Test Coverage

The HTTP proxy gained two new tests for the `CONNECT` accept path (`http_connect_accept_allows_allowlisted_host_in_full_mode` and `http_connect_accept_denies_denylisted_host`) confirming that allowlisted hosts get `200 OK` and denylisted hosts get `403 Forbidden` with `x-proxy-error: blocked-by-denylist`. This codifies the existing behavior — that websocket `CONNECT` targets are subject to the same allow/deny rules — under test.


### Remote Compaction Test Helpers Match Server Behavior

A new `mount_compact_user_history_with_summary_once` / `…_sequence` helper in `core/tests/common/responses.rs` mirrors the actual remote-compaction shape: it filters the request's input to only user/developer messages and appends a synthetic summary user message. Existing remote-compaction tests in `compact_remote.rs` migrate to this helper, removing hand-built `compacted_history` arrays and the now-obsolete `ENCRYPTED_COMPACTION_SUMMARY` references. New regression-snapshot tests cover:
- pre-turn compaction stripping incoming `<model_switch>` items (local and remote)
- mid-turn remote compaction where the compact output is summary-only
- mid-turn remote compaction after a prior summary compaction (multi-summary reinjection)

These changes do not alter user-visible behavior on their own but anchor existing compaction semantics under tests so future regressions surface quickly.


### Documentation Updates

- The `app-server/README.md` is updated to mention the new `thread/archived` and `thread/unarchived` notifications in the events overview, the archive/unarchive examples, and the approval flow's `approvalId`.
- `docs/codex_mcp_interface.md` updates the `execCommandApproval` schema line to include `approvalId?`.
- The `network-proxy/README.md` documents websocket proxy variables and the `wss://` CONNECT-through-allowlist behavior.

### Spurious Model-Reroute Warnings on Header Casing

When a provider returned an `OpenAI-Model` response header with different capitalization than the requested model slug, Codex would emit a `ModelReroute` event and a security warning ("flagged for potentially high-risk cyber activity"). This was a false positive on every casing-only difference. The fix lowercases both server and requested model strings before comparison in `Session::should_warn_for_model_mismatch()` (`core/src/codex.rs`), and a regression test asserts no reroute and no warning are produced. Previously valid mismatches (different model names) still warn.


### Resume/Fork Cwd Prompt Could Not Be Cancelled

The cwd-selection prompt shown when resuming or forking into a different cwd had no way to back out — `Ctrl-C` and `Ctrl-D` silently selected `Session` and continued. Users who hit the prompt by mistake had no escape hatch. The fix routes those key combos to a new `should_exit` flag that propagates up through `CwdPromptOutcome::Exit` → `ResolveCwdOutcome::Exit` → `AppRunControl::Exit(ExitReason::UserRequested)`, restoring the terminal and ending the session cleanly. Coverage in `cwd_prompt.rs` tests.


### Subcommand Approvals Producing Duplicate Completion Items

Before this release, accepting/declining a subcommand approval whose parent command was already executing could emit a stray `item/completed` for the callback, in addition to the parent's eventual completion. This created confusing duplicate items in the v2 stream. The new logic in `on_command_execution_request_approval_response()` in `app-server/src/bespoke_event_handling.rs` checks whether `approval_id` is present (i.e. this is a subcommand callback) and whether the parent `item_id` is in the `command_execution_started` set; when both are true, the redundant completion-item emission is suppressed while still submitting the `Op::ExecApproval` to the core.
