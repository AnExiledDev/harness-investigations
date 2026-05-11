# Changelog for version 0.130.0

### Plugin Details and Sharing Metadata

What: Plugin surfaces now expose more of what users and clients need to inspect and share plugins: bundled hooks appear in plugin details, share contexts can include link metadata and principals, and share-target updates now carry discoverability.

Usage:
```json
{"method": "plugin/read", "params": {"marketplacePath": "/path/to/marketplace", "pluginName": "plugin-name"}}
```

```json
{
  "method": "plugin/share/updateTargets",
  "params": {
    "remotePluginId": "plugins~Plugin_...",
    "discoverability": "UNLISTED",
    "shareTargets": []
  }
}
```

Details:
- `PluginDetail` now includes `hooks: Vec<PluginHookSummary>`, where each hook has a stable `key` and `eventName`.
- `PluginShareContext` can now include nullable `shareUrl` and `shareTargets`.
- `PluginShareUpdateTargetsParams` adds `discoverability`, with update values `UNLISTED` and `PRIVATE`.
- The TUI plugin detail popup now displays a Hooks row for bundled hook declarations.

Code references:
- `PluginHookSummary`, `PluginShareUpdateDiscoverability`, `PluginShareContext`, and `PluginDetail` in `codex-rs/app-server-protocol/src/protocol/v2/plugin.rs`
- `plugin_hook_declarations` in `codex-rs/hooks/src/declarations.rs`
- `PluginProcessor::plugin_read_response_inner` hook projection in `codex-rs/app-server/src/request_processors/plugins.rs`
- `plugin_hook_summary` in `codex-rs/tui/src/chatwidget/plugins.rs`


### Remote-Control CLI Entrypoint [Experimental]

What: `codex remote-control` is a top-level shortcut for starting a headless app-server with remote control enabled.

Usage:
```bash
codex remote-control
```

Details:
- The command rejects root `--remote` mode, enables `features.remote_control=true` for that invocation, and starts the app-server with normal CLI session source settings.
- This is a simpler entrypoint than manually composing app-server flags for the remote-control path.

Code references:
- `Subcommand::RemoteControl` in `codex-rs/cli/src/main.rs`
- `REMOTE_CONTROL_FEATURE_OVERRIDE` and `enable_remote_control_for_invocation` in `codex-rs/cli/src/main.rs`
- `codex_app_server::run_main_with_transport` invocation in `codex-rs/cli/src/main.rs`


### Thread Pagination for App-Server Clients

What: App-server clients can page stored thread turns without resuming the thread, and can choose how much item detail each turn includes.

Usage:
```json
{
  "method": "thread/turns/list",
  "params": {
    "threadId": "thr_123",
    "limit": 25,
    "sortDirection": "desc",
    "itemsView": "summary"
  }
}
```

Details:
- `ThreadTurnsListParams` now accepts `itemsView`; the protocol comment says it controls how much item detail is returned and defaults to summary.
- The backing `thread-store` contract adds `StoredTurnItemsView` with `notLoaded`, `summary`, and `full`.
- The new `thread/turns/items/list` method shape also exists, but app-server currently returns `-32601`; it is covered under In Development below.

Code references:
- `ThreadTurnsListParams.items_view` in `codex-rs/app-server-protocol/src/protocol/v2/thread.rs`
- `StoredTurnItemsView`, `ListTurnsParams`, and `TurnPage` in `codex-rs/thread-store/src/types.rs`
- `ThreadProcessor::thread_turns_list` in `codex-rs/app-server/src/request_processors/thread_processor.rs`


### Bedrock Credential Support and Header Handling

What: Bedrock auth can use AWS SDK console-login credentials, and Bedrock Mantle SigV4 signing now strips all snake_case compatibility headers that the Mantle front door does not preserve.

Usage:
```toml
[model_providers.bedrock.aws]
region = "us-east-1"
```

Details:
- The `codex-rs/aws-auth` crate now enables the AWS SDK `credentials-login` feature, which is the code-level support for AWS login credential loading.
- Bedrock Mantle signing previously stripped only `session_id`; it now removes any header whose name contains `_`, covering `thread_id` and future OpenAI compatibility identity headers before signing.

Code references:
- `aws-config = { features = ["credentials-login"] }` in `codex-rs/aws-auth/Cargo.toml`
- `remove_headers_not_preserved_by_bedrock_mantle` in `codex-rs/model-provider/src/amazon_bedrock/auth.rs`


### Environment-Aware `view_image`

What: In sessions with selected environments, `view_image` can target a specific environment instead of always resolving paths through the primary local environment.

Usage:
```json
{
  "path": "/workspace/screenshot.png",
  "environment_id": "remote"
}
```

Details:
- `ViewImageArgs` now carries `environment_id`.
- The tool schema includes `environment_id` only when multiple selected environments are active.
- The handler resolves the requested environment before reading the image, so remote or alternate local environment files can be viewed correctly.

Code references:
- `ViewImageArgs.environment_id` and `resolve_tool_environment` usage in `codex-rs/core/src/tools/handlers/view_image.rs`
- `ViewImageToolOptions.include_environment_id` in `codex-rs/core/src/tools/handlers/view_image_spec.rs`
- `view_image_routes_to_selected_remote_environment` in `codex-rs/core/tests/suite/view_image.rs`


### CODEX_HOME Environment Profiles [Experimental]

What: Codex can now read environment definitions from `CODEX_HOME/environments.toml`, supporting both WebSocket exec-server URLs and command-backed stdio exec-server environments.

Usage:
```toml
default = "ssh-dev"

[[environments]]
id = "devbox"
url = "ws://127.0.0.1:4512"

[[environments]]
id = "ssh-dev"
program = "ssh"
args = ["dev", "codex exec-server --listen stdio"]
cwd = "/tmp"

[environments.env]
CODEX_LOG = "debug"
```

Details:
- If `environments.toml` exists, it defines configured environments; otherwise Codex preserves legacy `CODEX_EXEC_SERVER_URL` behavior.
- Environment ids reject `local`, `none`, whitespace, unsupported characters, duplicates, and overlong names.
- Each configured environment must set exactly one transport: `url` for WebSocket or `program` for stdio command startup.

Code references:
- `EnvironmentManager::from_codex_home` in `codex-rs/exec-server/src/environment.rs`
- `environment_provider_from_codex_home`, `EnvironmentToml`, and `ENVIRONMENTS_TOML_FILE` in `codex-rs/exec-server/src/environment_toml.rs`
- `StdioExecServerCommand` and `ExecServerTransportParams` in `codex-rs/exec-server/src/client_api.rs`
- `ExecServerClient::connect_stdio_command` in `codex-rs/exec-server/src/client_transport.rs`


### OpenTelemetry Span and Tracestate Configuration

What: Config files can now attach custom OpenTelemetry span attributes and configured W3C tracestate member fields.

Usage:
```toml
[otel.span_attributes]
deployment = "staging"

[otel.tracestate.example]
alpha = "one"
beta = "two"
```

Details:
- Invalid span attributes or tracestate entries are filtered with startup warnings instead of silently producing unsafe trace headers.
- Configured tracestate fields are merged into propagated trace context.

Code references:
- `OtelToml.span_attributes` and `OtelToml.tracestate` in `codex-rs/config/src/types.rs`
- `resolve_span_attributes` and `resolve_tracestate` in `codex-rs/core/src/config/otel.rs`
- `validate_span_attributes`, `validate_tracestate_entries`, and `validate_tracestate_member` in `codex-rs/otel/src/config.rs` and `codex-rs/otel/src/trace_context.rs`


### Live App-Server Threads Refresh Runtime Config

Live app-server threads now receive refreshed runtime config after config mutations, instead of requiring a restart for updates to take effect. This includes refreshable runtime state while preserving session-static settings.

Code references:
- `ConfigProcessor::refresh_live_threads_from_latest_config_snapshot` in `codex-rs/app-server/src/request_processors/config_processor.rs`
- `CodexThread::refresh_runtime_config` in `codex-rs/core/src/codex_thread.rs`
- `Session::refresh_runtime_config` in `codex-rs/core/src/session/mod.rs`


### More Accurate Turn Diffs After Patch Operations

Turn diff tracking is now operation-backed by committed apply-patch deltas. This keeps turn diffs accurate even when a patch partially applies and then fails.

Code references:
- `AppliedPatchDelta`, `AppliedPatchChange`, `AppliedPatchFileChange`, and `ApplyPatchFailure::delta` in `codex-rs/apply-patch/src/lib.rs`
- `TurnDiffTracker::track_delta` in `codex-rs/core/src/turn_diff_tracker.rs`
- `ApplyPatchRuntimeOutput.delta` in `codex-rs/core/src/tools/runtimes/apply_patch.rs`


### ThreadStore-Backed Thread Summary, Rename, Resume, and Fork Paths

Thread management paths now lean more consistently on `ThreadStore` rather than rollout paths. This improves stored-thread operations for threads that do not have a local rollout path.

Code references:
- `StoredThreadHistory` and `ReadThreadByRolloutPathParams` in `codex-rs/thread-store/src/types.rs`
- `ThreadManager` changes in `codex-rs/core/src/thread_manager.rs`
- Thread summary handling in `codex-rs/app-server/src/request_processors/thread_summary.rs`


### Approval and Guardian Timing in Protocol Events

Approval and guardian review protocol payloads now include millisecond timestamps for start and completion timing.

Code references:
- `ItemGuardianApprovalReviewStartedNotification.started_at_ms` in `codex-rs/app-server-protocol/src/protocol/v2/item.rs`
- `ItemGuardianApprovalReviewCompletedNotification.started_at_ms` and `completed_at_ms` in `codex-rs/app-server-protocol/src/protocol/v2/item.rs`
- `CommandExecutionRequestApprovalParams.started_at_ms`, `FileChangeRequestApprovalParams.started_at_ms`, and `PermissionsRequestApprovalParams.started_at_ms` in `codex-rs/app-server-protocol/src/protocol/v2/item.rs` and `codex-rs/app-server-protocol/src/protocol/v2/permissions.rs`


## Bug Fixes

- Remote compaction v2 now sends `response.processed` after successful compaction output processing (`run_remote_compact_task_inner_impl` in `codex-rs/core/src/compact_remote_v2.rs`).
- API-key remote `/responses/compact` requests omit `service_tier`, while ChatGPT-auth compaction can still reuse it (`run_remote_compact_task_inner_impl` in `codex-rs/core/src/compact_remote.rs`; `remote_manual_compact_api_auth_omits_service_tier_and_reuses_prompt_cache_key` in `codex-rs/core/tests/suite/compact_remote.rs`).
- Windows sandbox setup now ensures sandbox users can read the desktop runtime binary cache (`ensure_codex_app_runtime_bin_readable` in `codex-rs/windows-sandbox-rs/src/setup_runtime_bin.rs`).
- `codex exec` no longer prints the stale “research preview” wording in its startup banner (`codex-rs/exec/src/event_processor_with_human_output.rs`).
- Bedrock Mantle requests no longer sign snake_case OpenAI compatibility headers that Mantle drops before SigV4 verification (`remove_headers_not_preserved_by_bedrock_mantle` in `codex-rs/model-provider/src/amazon_bedrock/auth.rs`).


### Turn Item Hydration API [In Development]

What: The protocol now defines a future `thread/turns/items/list` API for paging full items inside a single stored turn.

Usage:
```json
{
  "method": "thread/turns/items/list",
  "params": {
    "threadId": "thr_123",
    "turnId": "turn_456",
    "limit": 100,
    "sortDirection": "asc"
  }
}
```

Status: The request and response types are present, but app-server currently returns JSON-RPC `-32601` with `thread/turns/items/list is not supported yet`.

Code references:
- `ThreadTurnsItemsListParams` and `ThreadTurnsItemsListResponse` in `codex-rs/app-server-protocol/src/protocol/v2/thread.rs`
- Experimental method registration `"thread/turns/items/list"` in `codex-rs/app-server-protocol/src/protocol/common.rs`
- Unsupported implementation in `ThreadProcessor::thread_turns_items_list` in `codex-rs/app-server/src/request_processors/thread_processor.rs`


## Notes

Breaking protocol changes:
- The v2 app-server device-key RPCs were removed: `"device/key/create"`, `"device/key/public"`, and `"device/key/sign"`. Their protocol types and JSON/TypeScript schemas are also gone. Clients still calling these methods must stop relying on app-server-local device-key creation/signing.
- `SkillsListParams.perCwdExtraUserRoots` and `SkillsListExtraRootsForCwd` were removed. Clients should no longer send `perCwdExtraUserRoots` to `skills/list`.

Code references:
- Removed device-key method registrations in `codex-rs/app-server-protocol/src/protocol/common.rs`
- Removed `codex-rs/app-server-protocol/src/protocol/v2/device_key.rs`
- Removed `codex-rs/app-server/src/request_processors/device_key_processor.rs`
- Removed `SkillsListParams.per_cwd_extra_user_roots` in `codex-rs/app-server-protocol/src/protocol/v2/plugin.rs`


Generated with:
- tool: `harness-investigations@1ed3002-dirty`
- provider: `codex`
- model: `gpt-5.5`
- reasoning effort: `medium`
- primary diff: `archive/codex/diff/v0.130.0.diff` (raw diff)
- official release notes: `archive/codex/changes/release-notes-v0.130.0.md`
