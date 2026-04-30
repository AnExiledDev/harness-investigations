# Changelog for version 0.111.0

## Highlights

This release builds out two major capabilities for the v2 protocol: **structured MCP server elicitations** (servers can pop up form or URL-based prompts to clients during a turn) and **end-to-end image generation tracking** (new turn item, history cell, and event lifecycle for `image_generation_begin`/`image_generation_end`). It also promotes **Fast mode** to a Stable, default-on feature (now advertised as "2x plan usage" instead of 3x), reworks the **artifacts runtime** so it can self-install from GitHub Releases (and fall back to a system Node, Electron, or the bundled Codex desktop app), and teaches `js_repl` to load local `.js`/`.mjs` files via dynamic `import()`.

### MCP server elicitation requests (v2 protocol)

**What:** MCP servers running inside Codex can now interrupt a turn and request structured input from the client through a new `mcpServer/elicitation/request` server-to-client request. Two elicitation modes are supported: a **form** mode that ships a JSON Schema describing the expected response, and a **url** mode that asks the client to drive an out-of-band flow (e.g. a sign-in page) identified by an `elicitationId`. The client replies with one of three actions — `accept` (with structured `content`), `decline`, or `cancel`.

**Details:**
- New protocol types: `McpServerElicitationRequestParams`, `McpServerElicitationRequest` (`Form`/`Url`), `McpServerElicitationRequestResponse`, and `McpServerElicitationAction` — see `codex-rs/app-server-protocol/src/protocol/v2.rs`.
- The protocol-level `ElicitationRequestEvent` now carries a tagged `request: ElicitationRequest` (Form or Url) instead of the previous flat `message: String`. New `ElicitationRequest` enum lives in `codex-rs/protocol/src/approvals.rs`.
- Params include `threadId`, an optional `turnId` (best-effort correlation; nullable because MCP elicitations are protocol-level standalone requests), and `serverName`.
- Responses can carry an arbitrary `content` JSON value mirroring `rmcp::CreateElicitationResult`. Decline/cancel responses set `content: null`.
- The app-server forwards core `EventMsg::ElicitationRequest` events as `ServerRequest::McpServerElicitationRequest` (only when `ApiVersion::V2` is in use), spawns a follow-up task to await the response, and submits an `Op::ResolveElicitation { server_name, request_id, decision, content }` back into core.
- Client errors caused by turn transitions (the request being cleared by `turnTransition`) automatically map to `cancel`; deserialization or transport failures default to `decline`.
- Documented in `codex-rs/app-server/README.md` under "MCP server elicitations".

**Code references:**
- `EscalateServer::start_session()` and request flow in `codex-rs/app-server/src/bespoke_event_handling.rs` (`apply_bespoke_event_handling`, `on_mcp_server_elicitation_response`, `mcp_server_elicitation_response_from_client_result`).
- Protocol definitions in `codex-rs/app-server-protocol/src/protocol/v2.rs` and `codex-rs/protocol/src/approvals.rs`.
- Core handler `handlers::resolve_elicitation()` in `codex-rs/core/src/codex.rs` now accepts a `content: Option<Value>` and forwards it (rather than always sending `{}` on Accept).
- End-to-end test: `codex-rs/app-server/tests/suite/v2/mcp_server_elicitation.rs`.


### Image generation lifecycle events and turn item

**What:** Image generation calls produced by the model are now first-class items in the protocol, history, and TUI. New `ImageGenerationBegin` and `ImageGenerationEnd` event variants stream alongside execution; a new `TurnItem::ImageGeneration` (and v2 `ThreadItem::ImageGeneration`) records the call's `id`, `status`, optional `revisedPrompt`, and `result` payload.

**Details:**
- New event types `ImageGenerationBeginEvent { call_id }` and `ImageGenerationEndEvent { call_id, status, revised_prompt, result }` in `codex-rs/protocol/src/protocol.rs`.
- New `ImageGenerationItem` in `codex-rs/protocol/src/items.rs` with `as_legacy_event()` mapping to the corresponding `EventMsg`.
- `parse_turn_item()` (in `codex-rs/core/src/event_mapping.rs`) recognizes `ResponseItem::ImageGenerationCall` and converts it into the new turn item.
- `ThreadHistoryBuilder` in `codex-rs/app-server-protocol/src/protocol/thread_history.rs` upserts a placeholder item on `begin` and fills it in on `end`.
- The streaming dispatcher initializes the started item with `status: "in_progress"` and clears `revised_prompt`/`result` until the final event arrives — see `handle_output_item_done()` in `codex-rs/core/src/stream_events_utils.rs`.
- TUI: `codex-rs/tui/src/chatwidget.rs` adds `on_image_generation_begin`/`on_image_generation_end`, and `history_cell.rs` introduces `new_image_generation_call()` which renders a "Generated Image" cell with a `status: revised_prompt` summary line. Snapshot test: `image_generation_call_history_snapshot`.
- Exec output: `event_processor_with_human_output.rs` now prints `image generation started <call_id>` and `generated image <call_id>` lines.
- Persistence: `ImageGenerationEnd` is recorded by `event_msg_persistence_mode()` in `codex-rs/core/src/rollout/policy.rs`; the begin event is intentionally non-persistent.
- Schemas regenerated for both v1 and v2 (`EventMsg.json`, `ServerNotification.json`, `ThreadStartedNotification.json`, etc.) and TS bindings (`ImageGenerationBeginEvent.ts`, `ImageGenerationEndEvent.ts`, `ImageGenerationItem.ts`).

**Code references:** `on_image_generation_end()` in `codex-rs/tui/src/chatwidget.rs`, `new_image_generation_call()` in `codex-rs/tui/src/history_cell.rs`, integration test `image_generation_call_event_is_emitted` in `codex-rs/core/tests/suite/items.rs`.


### Self-installing artifacts runtime

**What:** The artifacts tool no longer requires the runtime to be pre-staged on disk. Codex can now download, verify, extract, and cache the pinned runtime release (`artifact-runtime-v2.4.0`) from the default `https://github.com/openai/codex/releases/download/` location on first use, and it will additionally fall back to a system `node`, system `electron`, or the bundled Codex desktop application when the managed runtime is unavailable.

**Details:**
- The previous monolithic `codex-rs/artifacts/src/runtime.rs` was split into a module tree: `runtime/manager.rs`, `runtime/installed.rs`, `runtime/manifest.rs`, `runtime/error.rs`, and a new `runtime/js_runtime.rs` that resolves which JS executable to use.
- New `JsRuntime`/`JsRuntimeKind` types with platform-aware fallback. `ArtifactsClient` now calls `runtime.resolve_js_runtime()` and sets `ELECTRON_RUN_AS_NODE=1` automatically when running through Electron.
- `ArtifactsClient::from_runtime_manager()` is the new lazy entry point; the old "must already be installed" path was removed and the artifacts tool handler now constructs an `ArtifactRuntimeManager` with `with_default_release(...)`.
- New helpers `is_js_runtime_available()` and `can_manage_artifact_runtime()` let callers gate feature registration on platform capability rather than a cache hit. Tool-spec registration uses `can_manage_artifact_runtime()` so the artifacts tool only appears on supported platforms (see `codex-rs/core/src/tools/spec.rs`).
- Codex app discovery enumerates several product names — `Codex`, `Codex (Dev)`, `Codex (Agent)`, `Codex (Nightly)`, `Codex (Alpha)`, `Codex (Beta)` — across macOS, Windows, and Linux install roots.
- The artifacts tool description was updated from "preinstalled Codex @oai/artifact-tool runtime" to "preinstalled Codex @oai/artifact-tool runtime ... a local Node-compatible runtime."

**Code references:** `JsRuntime` in `codex-rs/artifacts/src/runtime/js_runtime.rs`, `ArtifactsClient::execute_build()`/`execute_render()` in `codex-rs/artifacts/src/client.rs`, `default_runtime_manager()` in `codex-rs/core/src/tools/handlers/artifacts.rs`. New documentation in `codex-rs/artifacts/README.md`.


### `codex-package-manager` crate (shared package installer)

**What:** A new internal `codex-package-manager` crate centralizes the install-cache plumbing previously embedded in the artifacts runtime. It owns platform detection, manifest fetching, archive validation, extraction (`.zip` and `.tar.gz`), staging, promotion, and cross-process locking. Future cached runtimes are expected to plug into the `ManagedPackage` trait.

**Details:**
- Public surface: `PackageManager`, `PackageManagerConfig`, `ManagedPackage`, `PackageReleaseArchive`, `ArchiveFormat`, `PackagePlatform`, `PackageManagerError`.
- Cross-process locking is backed by the new `fd-lock = 4.0.4` workspace dependency.
- Extraction is hardened: zip entries that escape the destination root are rejected; tar.gz extraction refuses symlinks, hard links, sparse files, device files, and FIFOs; archive SHA-256 and (when present) `size_bytes` are verified.
- Default cache root is `<codex_home>/<package_default>/`; callers can override via `PackageManagerConfig::with_cache_root(...)`.
- New documentation in `codex-rs/package-manager/README.md` describes the model, contract, and security/extraction rules.

**Code references:** `codex-rs/package-manager/src/{archive,config,error,lib,manager,package,platform}.rs`.


### `js_repl` supports local file imports via dynamic `import()`

**What:** Within `js_repl`, dynamic `import()` now accepts relative (`./foo.js`), absolute (`/abs/path.mjs`), and `file://` specifiers in addition to bare package specifiers. Imported local files run inside the same persistent REPL VM context, so they can see `codex`, `tmpDir`, and other REPL globals, and they reload between exec cells while top-level bindings persist across cells.

**Details:**
- New resolver helpers in `codex-rs/core/src/tools/js_repl/kernel.js`: `resolvePathSpecifier()`, `isPathSpecifier()`, `isFileUrlSpecifier()`, `loadLinkedFileModule()`, `loadLinkedNativeModule()`, `loadLinkedModule()`, and a unified async `importResolved()`.
- Local file modules are linked using `vm.SourceTextModule` with the REPL's shared `context`. Static imports from a local file may only target other local `.js`/`.mjs` files; package and Node builtin imports from local files must remain dynamic.
- `import.meta.resolve()` now returns importable strings: `file://...` for local paths, bare package names for resolvable packages, and `node:...` for builtins. `import.meta.url`/`.filename`/`.dirname`/`.main` are populated for both REPL cells and imported files.
- Bare package imports always resolve from the REPL-global search roots (`CODEX_JS_REPL_NODE_MODULE_DIRS`, then cwd) — they do **not** resolve relative to the importing local file. Local files cannot escape the configured node_modules search roots (verified by `js_repl_local_files_do_not_escape_node_module_search_roots`).
- Directory imports and non-`.js`/`.mjs` extensions are explicitly rejected with helpful error messages.
- The `js_repl` user-instructions section in `project_doc.rs` was updated to describe these rules in detail.

**Code references:** `kernel.js` in `codex-rs/core/src/tools/js_repl/`, new tests `js_repl_supports_relative_file_imports`, `js_repl_supports_absolute_file_imports`, `js_repl_imported_local_files_can_access_repl_globals`, and others in `codex-rs/core/src/tools/js_repl/mod.rs`.


### Plugins instructions section

**What:** When plugins are loaded, Codex now adds a `## Plugins` section to the user-instructions sent to the model, listing the active, non-empty plugins by display name and explaining trigger/preference/missing-plugin rules. This sits between the project-doc/JS REPL section and the `## Skills` section.

**Details:**
- New `PluginCapabilitySummary` type in `codex-rs/core/src/plugins/manager.rs` filters out inactive and zero-capability plugins (only plugins with at least one of skills, MCP servers, or app connectors are surfaced).
- `PluginLoadOutcome` now exposes both `plugins()` and `capability_summaries()`.
- `get_user_instructions()` in `codex-rs/core/src/project_doc.rs` takes a new `plugins: Option<&[PluginCapabilitySummary]>` argument and inserts the section via the new `render_plugins_section()` helper (`codex-rs/core/src/plugins/render.rs`).
- App connector ID lists are deduplicated when loaded from plugin app config files.
- Test coverage in `core/tests/suite/plugins.rs` now asserts the plugins section appears before the skills section.

**Code references:** `render_plugins_section()` in `codex-rs/core/src/plugins/render.rs`, `PluginCapabilitySummary::from_plugin()` in `codex-rs/core/src/plugins/manager.rs`.


### Web search tool: `text_and_image` content type

**What:** Models that advertise the new `web_search_tool_type: text_and_image` capability will now receive a `search_content_types: ["text", "image"]` argument on their web search tool spec, opting them into image results in addition to text.

**Details:**
- New `WebSearchToolType` enum (`Text` (default) / `TextAndImage`) in `codex-rs/protocol/src/openai_models.rs`.
- New field on `ModelInfo` (`#[serde(default)]`, so existing model JSON keeps working).
- `ToolSpec::WebSearch` gained an `external_web_access: Option<bool>` plus `search_content_types: Option<Vec<String>>` field — see `codex-rs/core/src/client_common.rs`.
- `build_specs()` in `codex-rs/core/src/tools/spec.rs` populates the new field based on `config.web_search_tool_type`.

**Code references:** `web_search_tool_type_text_and_image_sets_search_content_types` test in `codex-rs/core/src/tools/spec.rs`.


### Zsh-fork backend for `unified_exec`

**What:** When both `Feature::ShellTool` and `Feature::ShellZshFork` are enabled (zsh-only), unified exec sessions can now run through the zsh-fork escalation backend instead of the direct spawn path. This lets persistent PTY sessions participate in the same execve-wrapper escalation flow as one-shot shell commands.

**Details:**
- New `UnifiedExecBackendConfig` (`Direct` or `ZshFork`) on `ToolsConfig`.
- New module `codex-rs/core/src/tools/runtimes/shell/zsh_fork_backend.rs` exposes `maybe_run_shell_command()` (one-shot path) and `maybe_prepare_unified_exec()` (PTY path), with Unix and non-Unix imp split.
- New `EscalationSession` type in `codex-rs/shell-escalation/src/unix/escalate_server.rs` (`start_session()`, `env()`, `close_client_socket()`, `Drop`) lets callers own the shell process while only consuming the wrapper/socket env overlay.
- `UnifiedExecProcess` and `UnifiedExecProcessManager::open_session_with_exec_env()` now take a `SpawnLifecycleHandle` so backends can run cleanup hooks (e.g. closing the parent's copy of the escalation socket) immediately after spawn. A `NoopSpawnLifecycle` is provided for the direct path.
- The escalation server now propagates parent and session cancellation tokens through the entire request handling path and uses `kill_on_drop(true)` on spawned children so cancellation cleanly tears down the sub-shell.
- The `ShellCommandExecutor::run` trait method gained `after_spawn: Option<Box<dyn FnOnce() + Send>>`; the executor's documentation now notes that `env_overlay` is a wrapper-only overlay rather than a full child environment.

**Code references:** `zsh_fork_backend::maybe_prepare_unified_exec()`, `EscalationSession` in `codex-rs/shell-escalation/src/unix/escalate_server.rs`, `start_session_exposes_wrapper_env_overlay` test.


### Service tier override detection on thread resume

**What:** Resuming a thread now reports a mismatch when the requested `service_tier` differs from the active session's service tier, alongside the existing `model`/`model_provider`/`cwd` checks.

**Details:**
- `collect_resume_override_mismatches()` in `codex-rs/app-server/src/codex_message_processor.rs` now compares `request.service_tier` against `config_snapshot.service_tier`.
- Mismatch text format: `service_tier requested=Some(Fast) active=Some(Flex)` (covered by the new `collect_resume_override_mismatches_includes_service_tier` test).


### Persisted Git metadata preferred when resuming local threads

**What:** When resuming a thread that has been running locally (with the `sqlite` feature on), Codex now reads mutable metadata such as the current Git branch from the state DB rather than re-reading the live working tree. This keeps long-running sessions stable when the user has switched branches outside of Codex.

**Details:**
- New helper `load_thread_summary_for_rollout()` merges persisted thread metadata over the rollout-derived summary, copying `git_info` from the state DB summary when available.
- New helper `merge_mutable_thread_metadata()` and `preview_from_rollout_items()` for resume preview text.
- Thread resume responses are now built from the in-memory `CodexThread` snapshot when available, avoiding extra rollout reads.

**Code references:** `load_thread_summary_for_rollout()` and `load_thread_from_resume_source_or_send_internal()` in `codex-rs/app-server/src/codex_message_processor.rs`. New end-to-end test `thread_resume_prefers_persisted_git_metadata_for_local_threads` in `codex-rs/app-server/tests/suite/v2/thread_resume.rs`.

### Fast mode is now stable and on by default

`Feature::FastMode` was previously `Stage::UnderDevelopment` with `default_enabled: false`. It is now `Stage::Stable` with `default_enabled: true` (see `codex-rs/core/src/features.rs`). The `/fast` slash-command description was updated from "fastest inference at 3X plan usage" to **"fastest inference at 2X plan usage"** (`codex-rs/tui/src/slash_command.rs`).

A companion `FAST_TOOLTIP` was added to the paid-tooltip rotation: paid plans (`Plus`/`Team`/`Enterprise`/`Pro`) now see either the existing app-promo tooltip or a new "Use **/fast** to enable our fastest inference at 2X plan usage" tooltip, with the Fast promo suppressed when Fast mode is already enabled (`pick_paid_tooltip()` in `codex-rs/tui/src/tooltips.rs`).


### `fast` indicator in the TUI session header

When the session is running in Fast service tier and the user is signed in via ChatGPT auth, the TUI session header now appends a magenta `fast` badge after the model/reasoning effort line:

```
model: gpt-4o high   fast   /model to change ...
```

Implemented via `ChatWidget::should_show_fast_status()` (in `codex-rs/tui/src/chatwidget.rs`) and a new `show_fast_status` parameter threaded through `SessionHeaderHistoryCell::new()` and `new_session_info()` (`codex-rs/tui/src/history_cell.rs`). New tests `fast_status_indicator_requires_chatgpt_auth` and `fast_status_indicator_is_hidden_when_fast_mode_is_off` cover the behavior.


### Codex App promo tooltip on Windows

Windows users now see an updated paid tooltip that announces availability on Windows: `*New* Try the **Codex App**, now available on **Windows**, with 2x rate limits until *April 2nd*. Run 'codex app' or visit ...`. Linux users still see the non-mac short form. Implemented via `paid_app_tooltip()` and a new `IS_WINDOWS` const in `codex-rs/tui/src/tooltips.rs`. The tooltip pool filter now keeps "codex app" lines on either macOS or Windows.


### Realtime conversation logging

- `realtime_conversation::handle_start()` now logs realtime events at `info!` level (skipping `RealtimeEvent::AudioOut(_)` to avoid spam) instead of the previous `debug!`. This makes realtime debugging visible without raising the global log level.
- Conversely, `submission_dispatch_span()` in `codex-rs/core/src/codex.rs` now uses `debug_span!` for `Op::RealtimeConversationAudio` (verified by the new `submission_dispatch_span_uses_debug_for_realtime_audio` test) so high-frequency audio frames don't pollute info traces.


### Approval/elicitation acceptance preserves user content

When a user accepts an MCP elicitation that supplies structured input, that input is now forwarded back to the MCP server. Previously, the core elicitation handler always sent `{}` on Accept, dropping any content the client provided. The new signature is `resolve_elicitation(..., content: Option<Value>)`; if the client sends `None`, the legacy `{}` fallback is still used (`codex-rs/core/src/codex.rs`).


### Plugin app connectors deduplicated

`load_apps_from_file()` (in `codex-rs/core/src/plugins/manager.rs`) now deduplicates connector IDs after sorting, preventing duplicate app entries when a config repeats the same connector ID.


### Schema cleanup: camelCase for `ResidencyRequirement` and `ProductSurface`

Both `ResidencyRequirement` (`Us`/`Eu`/...) and `ProductSurface` (`Chatgpt`/...) in `codex-rs/app-server-protocol/src/protocol/v2.rs` were switched from `rename_all = "lowercase"` to `rename_all = "camelCase"` for consistency with the rest of the v2 protocol's serialization style.


### Exec/sandbox plumbing accepts an `after_spawn` hook

`execute_exec_env()` was renamed `execute_exec_request()` and now takes an `after_spawn: Option<Box<dyn FnOnce() + Send>>` callback that fires immediately after the child process has been spawned. A new convenience wrapper `execute_exec_request_with_after_spawn()` lives in `codex-rs/core/src/sandboxing/mod.rs`. This is used by the new zsh-fork unified-exec backend to release the parent's copy of the escalation socket fd so EOF behavior is correct on the child side.


### Documentation

- New `codex-rs/artifacts/README.md` and `codex-rs/package-manager/README.md` describe runtime/package-manager responsibilities and security rules.
- `codex-rs/app-server/README.md` documents the new `mcpServer/elicitation/request` flow.
- The bundled artifacts skills now ship richer guidance: `codex-rs/skills/src/assets/samples/slides/SKILL.md`, `references/auto-layout.md`, `references/presentation.md`, the spreadsheets analogues, and `agents/openai.yaml` were updated.

### Elicitation request payload no longer flattens form/url shape

The `ElicitationRequestEvent` previously exposed only `message: String`, which silently lost the structured schema or URL parameters that MCP servers sent. The event now carries an `ElicitationRequest` enum (`Form { message, requested_schema }` or `Url { message, url, elicitation_id }`), and `mcp_connection_manager::ElicitationRequestManager` constructs the correct variant from the rmcp `CreateElicitationRequestParams`. TUI sites that needed the legacy plain message extract it via the new `ElicitationRequest::message()` accessor (`codex-rs/tui/src/chatwidget.rs`, `codex-rs/tui/src/app.rs`).


### Escalation server only exports wrapper/socket env overlay

`EscalateServer::exec()` previously inserted the escalation environment by snapshotting the entire process environment (`std::env::vars().collect()`), which meant arbitrary parent-process variables could leak into the child shell. `start_session()` now returns a minimal `EscalationSession::env()` containing only `CODEX_ESCALATE_SOCKET`, `EXEC_WRAPPER`, and the legacy `BASH_EXEC_WRAPPER`; callers merge that overlay into their own base environment (`codex-rs/shell-escalation/src/unix/escalate_server.rs`, with the new `start_session_exposes_wrapper_env_overlay` test).


### Escalation session correctly cancels in-flight tasks

`escalate_task` and `handle_escalate_session_with_policy` now propagate two cancellation tokens (parent and per-session) through every `await` point — receiving FDs, policy decisions, child wait, super-exec messaging — so a cancelled or dropped session no longer leaks tasks. Spawned escalated children get `kill_on_drop(true)`. A new `EscalationSession::Drop` impl cancels the token, aborts the task, and closes the client socket.


### `js_repl` import error message is now actionable

When a static top-level `import "specifier"` declaration is used in a `js_repl` cell, the kernel now emits the explicit message:

```
Top-level static import "<specifier>" is not supported in js_repl. Use await import("<specifier>") instead.
```

Previously the kernel attempted to resolve the specifier and surfaced a less obvious "Unsupported import specifier" error. The user-instructions text was rewritten to spell out the supported specifier shapes and the cross-cell behavior of imported local files.


### Artifacts feature gating reflects actual platform support

`ToolsConfig::new()` now combines `Feature::Artifact` with `codex_artifacts::can_manage_artifact_runtime()` (a platform capability check) before registering the artifacts tool. Previously the tool would be registered on platforms where the runtime could never be installed, leading to user-visible failures only at call time.


### Realtime audio submissions no longer flood info logs

`submission_dispatch_span()` now uses `debug_span!` specifically for `Op::RealtimeConversationAudio`, while continuing to use `info_span!` for all other submissions. Without this fix, every audio frame produced an info-level span entry.
