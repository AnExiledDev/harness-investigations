# Changelog for version 0.121.0

## Highlights

Codex 0.121.0 lands two of the most-requested chat-composer ergonomics — a true **Ctrl+R reverse history search** and a dedicated **`/memories` settings popup** — alongside a new **`codex marketplace add`** command for installing plugin marketplaces from GitHub or local paths. Under the hood the release introduces a **typed `ToolName` (with namespace) across every tool dispatch path**, a **filesystem-sandbox stack in `exec-server`** with new `fs/*` JSON-RPC methods, **agent-identity registration backed by Ed25519 keypairs**, and a redesigned **apply_patch runtime that no longer re-invokes `codex` as a subprocess**. Several long-standing rough edges around guardian review timeouts, WSL1 detection, and ChatGPT plan rendering are also fixed.

### Reverse history search in the chat composer (Ctrl+R)

**What:** Press **Ctrl+R** in the composer to open a reverse-incremental search over your prompt history, just like the bash/zsh shortcut. Type to filter; **Ctrl+S** steps forward to newer matches; **Up/Down** also navigate matches. **Enter** accepts the preview as an editable draft, and **Esc/Ctrl+C** restores the original draft.

**Details:**
- New footer mode `FooterMode::HistorySearch` shows a `reverse-i-search:` prompt while the search is active.
- The shortcut overlay (opened with `?`) gains a new "ctrl + r search history" row so the binding is discoverable.
- Implemented in the new `bottom_pane/chat_composer/history_search.rs` module (~958 lines); plain `Ctrl+R` is also recognized via the raw `\u{0012}` byte for terminals that send the control character directly.

**Code references:** new file `bottom_pane/chat_composer/history_search.rs`; `FooterMode::HistorySearch` in `bottom_pane/footer.rs`; `ShortcutId::HistorySearch` registration in the same file.


### `/memories` slash command and Memories Settings popup

**What:** A new hidden `/memories` slash command opens a settings popup that lets you toggle **Use memories** and **Generate memories** independently, with a separate **Reset all memories** action.

**Details:**
- The popup includes a header line ("Choose how Codex uses and creates memories. Changes are saved to config.toml") and a docs link ("Learn more: https://developers.openai.com/codex/memories").
- Space toggles a row, Enter saves; Reset opens an inline confirmation step ("Reset all memories" / "Go back").
- New events `AppEvent::UpdateMemorySettings { use_memories, generate_memories }` and `AppEvent::ResetMemories` carry the change to the app server.
- If the `MemoryTool` feature is disabled, the command instead opens an enable-prompt ("Enable memories?" / "Yes, enable" / "Not now").

**Example:**
```
/memories       # opens the settings popup (or enable-prompt if disabled)
```

**Code references:** new file `bottom_pane/memories_settings_view.rs` (~477 lines); `open_memories_enable_prompt()` in `chatwidget.rs`; new `SlashCommand::Memories` variant in `tui/src/slash_command.rs`.


### `codex marketplace add` — install plugin marketplaces

**What:** A new top-level subcommand to register plugin marketplaces.

**Usage:**
```
codex marketplace add owner/repo
codex marketplace add owner/repo@v1.2.3
codex marketplace add https://github.com/owner/repo
codex marketplace add git@github.com:owner/repo.git --ref main
codex marketplace add ./local/path
codex marketplace add owner/repo --sparse plugins/foo --sparse plugins/bar
```

**Details:**
- Source specs may be `owner/repo[@ref]`, an HTTP(S)/SSH git URL, or a local directory.
- The command stages clones via tempdir, supports git sparse-checkout via repeated `--sparse PATH` flags, computes a safe directory name, swaps the install in atomically, and writes a new `[marketplaces.*]` table into `config.toml` (last_updated, source_type, source, ref, sparse_paths).
- A matching JSON-RPC method `MarketplaceAdd` (`MarketplaceAddParams`/`MarketplaceAddResponse`) is exposed from the app server, returning `installedRoot`, `marketplaceName`, and `alreadyAdded`.

**Code references:** new file `cli/src/marketplace_cmd.rs`; new modules `core/src/plugins/marketplace_add.rs` (with `install.rs`, `metadata.rs`, `source.rs`); `record_user_marketplace()` in `config/src/marketplace_edit.rs`; new schema files under `app-server-protocol/schema/json/v2/MarketplaceAdd*`.


### `codex responses` — streamed Responses API passthrough

**What:** A new (hidden from `--help`) `codex responses` subcommand reads a single Responses-API JSON payload from stdin and prints each streaming event as JSON, using your Codex auth.

**Details:**
- The payload must include `"stream": true`.
- Useful for debugging models, tools, or auth wiring without leaving the Codex CLI.

**Code references:** new file `cli/src/responses_cmd.rs`; subcommand wired in `cli/src/main.rs`.


### Agent identity (Ed25519 + ABOM) for ChatGPT-bound runs

**What:** A new "agent identity" subsystem registers an Ed25519 keypair with the ChatGPT backend and uses short-lived "biscuit" tokens (15s) for agent calls when `Feature::UseAgentIdentity` is on.

**Details:**
- `AgentIdentityManager` persists a `StoredAgentIdentity` containing the binding ID, ChatGPT account/user, agent runtime ID, PKCS8 private key, SSH-format public key, and an "Agent Bill of Materials" (`agent_version`, `agent_harness_id`, `running_location`).
- The identity is preserved across token refreshes via a new `AgentIdentityAuthRecord` field on `auth.json`, and `AuthManager` exposes `get_agent_identity(workspace_id)` / `set_agent_identity(record)` / `remove_agent_identity()`.
- A new `AuthManager::subscribe_auth_state() -> watch::Receiver<()>` lets components react when the stored auth or workspace identity changes.

**Code references:** new file `core/src/agent_identity.rs` (~766 lines); record type in `login/src/auth/storage.rs`; manager APIs in `login/src/auth/manager.rs`.


### Filesystem RPC + sandboxed FS in `exec-server`

**What:** The `exec-server` crate adds a full filesystem JSON-RPC surface (`fs/readFile`, `fs/writeFile`, `fs/createDirectory`, `fs/getMetadata`, `fs/readDirectory`, `fs/remove`, `fs/copy`) and a sandboxed-helper backend that re-enters Codex as a subprocess to execute each FS request under the requested sandbox policy.

**Details:**
- Each FS request accepts an optional `sandbox` parameter; ReadOnly/WorkspaceWrite operations route through the new helper subprocess (`fs_helper.rs`, `fs_helper_main.rs`, `sandboxed_file_system.rs`).
- A new `FileSystemSandboxContext` carries the policy plus a Windows-sandbox level and a `use_legacy_landlock` flag.
- `FileMetadata` gains a new `is_symlink` field (also reflected in the v2 protocol's `FsGetMetadataResponse`).
- The standalone `codex-exec-server` binary was removed; the crate is now a library backing `codex exec-server`, started with a new `ExecServerRuntimePaths::new(codex_self_exe, codex_linux_sandbox_exe)`.

**Code references:** new files `exec-server/src/fs_helper.rs`, `fs_helper_main.rs`, `fs_sandbox.rs`, `sandboxed_file_system.rs`, `runtime_paths.rs`; deletion of `exec-server/src/bin/codex-exec-server.rs`.


### Direct MCP-tool invocation RPC

**What:** A new `McpServerToolCall` JSON-RPC method (and matching `McpServerToolCallParams`/`Response`) lets clients call an MCP tool directly by `(threadId, server, tool, arguments)` and receive `content`, `isError`, `structuredContent`, and `_meta`.

**Code references:** new schema files `app-server-protocol/schema/json/v2/McpServerToolCall{Params,Response}.json`.


### Inject items into a thread (`ThreadInjectItems`)

**What:** A new RPC appends raw Responses-API items into a thread's model-visible history without going through a regular turn.

**Code references:** new schema files `app-server-protocol/schema/json/v2/ThreadInjectItems{Params,Response}.json`.


### Thread-level memory mode toggle

**What:** A new `ThreadMemoryModeSet` request and matching `ThreadMemoryMode` enum let a single thread opt out of memories independently of the global setting. The companion `MemoryReset` response type accompanies the existing reset path.

**Code references:** new schema files `ThreadMemoryMode.ts`, `ThreadMemoryModeSetParams/Response`; `MemoryResetResponse` schema.


### Realtime transcript split into Delta + Done events

**What:** The single `ThreadRealtimeTranscriptUpdated` notification is replaced by two events: `ThreadRealtimeTranscriptDeltaNotification` (incremental transcript chunks) and `ThreadRealtimeTranscriptDoneNotification` (final result). `ThreadRealtimeStartParams.output_modality: RealtimeOutputModality` is now a required field.

**Code references:** new schema files under `app-server-protocol/schema/json/v2/`.


### `codex debug seatbelt --allow-unix-socket PATH`

**What:** A new repeatable flag on `codex debug seatbelt` lets you pre-allow specific AF_UNIX sockets inside the sandbox-exec policy.

**Details:**
- The flag accepts absolute paths and may be passed multiple times.
- Backed by a new `CreateSeatbeltCommandArgsParams` struct that replaces the prior positional `create_seatbelt_command_args_for_policies(...)`.
- The restricted seatbelt policy now permits the listed unix sockets plus DNS (`*:53`) when `allow_local_binding` is set, and the local-binding allow rule was widened from `localhost:*` to `*:*`.

**Code references:** `cli/src/debug_sandbox.rs`; `sandboxing/src/seatbelt.rs`.


### Marketplace plugins migration in CLAUDE.md import

**What:** The "import external agent config" flow (Claude Code → Codex) gains plugin awareness.

**Details:**
- A new `ExternalAgentConfigMigrationItemType::Plugins` variant and `MigrationDetails { plugins: Vec<PluginsMigration> }` carry plugin data through the detection step.
- The detector now scans the source `settings.json` for enabled plugins (`extract_plugin_migration_details`).
- The importer downloads each marketplace via `add_marketplace`/`PluginsManager::install_plugin`, tracking succeeded/failed marketplaces and plugin IDs. The `import` API is now async.

**Code references:** `core/src/external_agent_config.rs` (renamed `claude_home` → `external_agent_home`).


### MCP `supports_parallel_tool_calls` advertisement

**What:** MCP server entries in `config.toml` accept a new optional `supports_parallel_tool_calls` boolean so a server can declare that its tool calls are safe to run in parallel.

**Code references:** `config/src/mcp_types.rs`, `config/src/mcp_edit.rs`; honored by the v2 `mcp` add command in `cli/src/mcp_cmd.rs`.


### Guardian "review timed out" status

**What:** When a guardian review exceeds its timeout, Codex now reports a distinct **timed-out** outcome instead of silently treating it as a denial.

**Details:**
- New `ReviewDecision::TimedOut`, `GuardianAssessmentStatus::TimedOut`, `GuardianApprovalReviewStatus::TimedOut`, and `GuardianReviewOutcome::TimedOut` variants.
- New TUI history cells `new_guardian_timed_out_patch_request` and `new_guardian_timed_out_action_request` plus a `TimedOut` arm in `new_approval_decision_cell` render messages like *"Review timed out before codex could run/apply…"*.
- Network approvals (`tools/network_approval.rs`) and the orchestrator (`tools/orchestrator.rs`) treat timeouts as denial but surface a dedicated message via `guardian_timeout_message()`.
- MCP tool approvals map the timeout to `McpToolApprovalDecision::Decline`.
- For unified-exec guardian timeouts, app-server reporting was promoted from "Declined" to `CommandExecutionStatus::Failed` so the UI shows the failure plainly.

**Code references:** `protocol/src/protocol.rs`; `core/src/guardian/*`; `tui/src/history_cell.rs`; `bottom_pane/approval_overlay.rs`.


### `code-mode` JS REPL: ICU data and namespace-aware tool dispatch

**What:** Codex's embedded JavaScript runtime now ships ICU locale data, so `Date.toLocaleString` and `Intl.DateTimeFormat` produce correct localized output.

**Details:**
- The runtime calls `v8::icu::set_common_data_77(deno_core_icudata::ICU_DATA)` at platform startup; new tests cover `Intl` behavior.
- Tool callbacks switched from string tool names to numeric tool indices, looked up against `RuntimeState::enabled_tools` — needed so namespaced tools resolve unambiguously.
- `ToolDefinition`, `EnabledToolMetadata`, and `CodeModeTurnHost::invoke_tool` now carry a typed `ToolName` (with namespace), and namespace-description grouping is rekeyed by namespace prefix instead of per-tool name.

**Code references:** `code-mode/src/runtime/mod.rs`, `service.rs`, `description.rs`, `runtime/{callbacks,globals}.rs`; new workspace dependency `deno_core_icudata = "0.77.0"`.


### Memory-extension retention pruning

**What:** Memory extensions now have a 7-day retention policy applied to per-extension resource files.

**Details:**
- A new `core/src/memories/extensions.rs` prunes resources under `memories_extensions/<name>/resources/*.md` older than 7 days.
- Phase-2 consolidation collects pending removals first, hands them to the consolidation prompt as a new `removed_extension_resources: &[RemovedExtensionResource]` slice (rendered under "Memory extension resources removed by retention pruning"), and only deletes the files after `mark_global_phase2_job_succeeded` returns true.
- Phase-1 rollouts are now redacted via `redact_secrets` before being written (e.g. an `sk-...` literal becomes `[REDACTED_SECRET]`).
- The default model for phase-2 consolidation moves from `gpt-5.3-codex` to `gpt-5.4`.

**Code references:** new file `core/src/memories/extensions.rs`; updated `core/src/memories/{phase1,phase2,prompts}.rs`.


### Public `shell_environment` module + `CODEX_THREAD_ID`

**What:** Shell-environment construction is now a public, reusable module exporting `create_env`, `create_env_from_vars`, `populate_env`, and a new constant `CODEX_THREAD_ID_ENV_VAR = "CODEX_THREAD_ID"` so spawned shells can see the active thread id.

**Details:**
- The default-exclude pattern set still strips variables matching `*KEY*`, `*SECRET*`, `*TOKEN*`.

**Code references:** new file `config/src/shell_environment.rs`; constant re-exported from the protocol crate.


### `tool_search`: special-case for the `computer-use` MCP server

**What:** When `tool_search` is called with the default limit and a result is from the `computer-use` MCP server, the limit is automatically expanded to 20 (`COMPUTER_USE_TOOL_SEARCH_LIMIT`) so common UI-driving toolsets aren't truncated. A per-server cap is enforced via `limit_results_per_server`.

**Code references:** `core/src/tools/handlers/tool_search.rs`; helper in `tools/src/tool_discovery.rs` falls back to `default_namespace_description("Tools in the {namespace} namespace.")` instead of the older "Tools from the {server} MCP server." string.


### State migration for millisecond thread timestamps

**What:** A new SQL migration `0025_thread_timestamps_millis.sql` upgrades thread timestamps to millisecond precision.

**Code references:** `state/migrations/0025_thread_timestamps_millis.sql`.


### Pro Lite plan support

**What:** Codex now recognizes a new `Pro Lite` ChatGPT plan throughout login, plan-name rendering, and the status card.

**Details:**
- `KnownPlan::ProLite` and `AccountPlanType::ProLite` are treated as personal (not workspace) accounts.
- The status card renders the plan as "Pro Lite" and adds it to the plan-name tooltip allowlist.

**Code references:** `login/src/auth/manager.rs`; `tui/src/status/card.rs`.


### Auto-unloading of idle threads in the app server

**What:** The app server now unloads a thread that has had no subscribers for 30 minutes, freeing memory in long-running daemons.

**Details:**
- New `UnloadingState` machinery and a `THREAD_UNLOADING_DELAY = 30 minutes` constant.
- Sessions are now `Arc`-shared, with `OnceLock<InitializedConnectionSessionState>` replacing the old mutable bool flags. Accessor methods include `initialized()`, `experimental_api_enabled()`, and `app_server_client_name()`.

**Code references:** `app-server/src/message_processor.rs`; `app-server/src/thread_state.rs`.

### `apply_patch` no longer re-execs `codex` to apply files

`tools/runtimes/apply_patch.rs` and `tools/handlers/apply_patch.rs` were rewritten. The previous flow built a sandbox command and spawned `codex apply_patch` as a subprocess (paths like `build_sandbox_command`, `resolve_apply_patch_program`, and the `CODEX_CORE_APPLY_PATCH_ARG1` env var were used). The new flow resolves a `FileSystemSandboxContext` from the active `SandboxAttempt` and calls `codex_apply_patch::apply_patch` directly, emitting stdout/stderr as `ExecCommandOutputDelta` events. The internal enum variant `DelegateToExec` was renamed `DelegateToRuntime`, and `MaybeApplyPatchVerified::Body` now threads the `sandbox` argument through.


### Typed `ToolName` everywhere

A new `protocol/src/tool_name.rs` introduces `ToolName { name, namespace }`, re-exported from `codex_tools`. It replaces the prior `tool_name: String` + `tool_namespace: Option<String>` pair across `ToolInvocation`, `ToolCall`, the router, the parallel runtime, and every handler (`js_repl`, `mcp`, `mcp_resource`, `unified_exec`, `agent_jobs`, `apply_patch`, `shell`, …). `Display` is `format!("{namespace}{name}")`. Practical effect: namespaced shadow tools no longer silently collide with built-ins because matches now compare `tool_name.name` rather than the raw concatenated string.


### MCP results now show wall time

`tools/handlers/mcp.rs` and `tools/context.rs` introduce `McpToolOutput { result: CallToolResult, wall_time: Duration }`. The serialized response prefixes `Wall time: {secs:.4} seconds\nOutput:` ahead of the existing text/content items, so the model and user can see how long the call took.


### Multi-agent fork rules: full forks inherit role

`tools/handlers/multi_agents/spawn.rs`, `multi_agents_v2/spawn.rs`, and `multi_agents_common.rs` add `reject_full_fork_spawn_overrides`, which rejects `agent_type`, `model`, and `reasoning_effort` overrides when a child spawn uses `fork_context=true` (v1) or `fork_turns=all` (v2). The error message reads *"Full-history forked agents inherit the parent agent type, model, and reasoning effort..."* Partial forks (e.g. `fork_turns=1`) still permit role overrides. `build_agent_shared_config` now also falls back to `model_info.default_reasoning_level` when the spawn omits an effort.


### `view_image` capability gating

`tools/handlers/view_image.rs` now reads file metadata and contents through a `FileSystemSandboxContext` when the file is remote, and `can_request_original_image_detail` no longer reads `Feature::ImageDetailOriginal` — it is now gated solely on the model's capability. The legacy feature flag is silently accepted by the CLI for backward compatibility.


### Slash-command history recall

The new `chatwidget/slash_dispatch.rs` (~522 lines) extracts slash-command dispatch from `chatwidget.rs`. Slash-command text is now staged for Up-arrow recall before the input is cleared, then committed after dispatch via `record_pending_slash_command_history`, so commands like `/diff` (not the partial `/di`) appear in history. Inline-arg helpers (`/fast`, `/plan`, `/rename`, `/review`, `/resume`, `/sandbox-add-read-dir`) all pipe through `prepare_inline_args_submission(record_history=false)` to avoid double-recording.


### Status-line context display

`bottom_pane/status_line_setup.rs` and `chatwidget/status_surfaces.rs` replace the single `StatusLineItem::ContextUsage` (which rendered a bracketed visual meter `[     ]`) with three explicit items: `context-remaining` ("Context X% left"), `context-remaining-percent` (an alias rendering the same), and `context-used` ("Context X% used"). Legacy IDs (`context-usage`, `context-remaining`, `context-used`) still parse so existing config files keep working. The setup view now iterates `StatusLineItem::iter()` instead of a hardcoded list.


### Status card readability on narrow terminals

`status/card.rs` and `status/helpers.rs`: when the terminal is too narrow, rate-limit rows now drop the progress bar and keep just the percentage; reset timestamps wrap onto continuation lines instead of being truncated. The async `discover_agents_summary` path was removed in favor of passing `agents_summary` in directly.


### Notifications: user-input requests reuse plan-mode prompt

`Notification::UserInputRequested` was replaced with a reuse of `Notification::PlanModePrompt { title }`. When multiple questions are pending, the title becomes `"{N} questions requested"`.


### Feedback uploads: arbitrary client tags

`feedback::upload_feedback()` was replaced by a `FeedbackUploadOptions` struct that accepts a new `tags: Option<&BTreeMap<String, String>>` map. Server-reserved tag names (`thread_id`, `classification`, `cli_version`, `session_source`, `reason`) cannot be overridden by clients. The v2 `FeedbackUploadParams` schema gains the same field. `FeedbackNoteView` now records `last_turn_id` and includes it as `turn_id` in `AppEvent::SubmitFeedback`.


### Cloud-managed config error messages

`cloud-requirements/src/lib.rs` now produces a user-facing error when the workspace-managed config TOML is invalid: *"workspace-managed config is invalid... contact your workspace admin"*, with the underlying TOML error appended.


### Bespoke event handling for v2 clients

`apply_bespoke_event_handling` now takes an `AnalyticsEventsClient` and emits TurnStarted/TurnCompleted/TurnAborted events into analytics. `CommandExecutionSource::UnifiedExecInteraction` events are suppressed for v2 clients to avoid duplicate items, and the legacy `ContextCompacted` notification is suppressed for v2 (which uses the canonical `ContextCompaction` item).


### Hooks types

Hook payload structs (`HookPayload`, `PreToolUseRequest`, `PostToolUseRequest`, `SessionStartRequest`, `StopRequest`, `UserPromptSubmitRequest`, `ConfiguredHandler`) migrated `cwd` and `source_path` fields from `PathBuf` to `AbsolutePathBuf`. Hook IDs and notification JSON now stringify via `AbsolutePathBuf::display`.


### Protocol-wide path-type tightening

Many app-server-protocol fields and core types switched from raw string paths to `AbsolutePathBuf`, including `installedRoot`, `iconLarge`/`iconSmall`, plugin/skill `path`, `cwd` on `Thread`/`SessionConfiguredEvent`/`SkillMetadata`/`SkillSummary`/`ThreadItem::ImageView/ImageGeneration/Exec`, and a new `instruction_sources: Vec<AbsolutePathBuf>` on Thread responses. This eliminates a category of "path-handled-as-string" bugs.


### Workspace-write deny path consolidation (Windows sandbox)

`windows-sandbox-rs/src/setup_orchestrator.rs` adds `build_payload_deny_write_paths()` that merges explicit deny-write paths with policy-computed deny paths (e.g. `.git`, `.codex`, `.agents`) at startup. The previous workspace ACL helpers (`protect_workspace_codex_dir`, `protect_workspace_agents_dir`) were removed in favor of this single deny-list approach.


### Image-generation `Saved to:` URL

The `Saved to:` link emitted after image generation now constructs its `file://` URL inside `history_cell.rs` instead of `chatwidget.rs`, keeping URL rendering in one place.

### WSL1 detection: fail fast instead of crashing under bubblewrap

Codex now detects WSL1 from `/proc/version` and returns a new `SandboxTransformError::Wsl1UnsupportedForBubblewrap` with the message *"not supported on WSL1... Use WSL2"* before attempting to invoke bubblewrap, which doesn't work on WSL1. The `linux-sandbox/README.md` documents this explicitly. WSL2 continues to follow the normal Linux path.

**Code references:** `sandboxing/src/bwrap.rs`, `sandboxing/src/manager.rs`.


### `network_proxy_spec`: removed broken denylist-only mode

`config/src/network_proxy_spec.rs` removes the `danger_full_access_denylist_only` mode entirely (and the `*` global allowlist pattern). `DangerFullAccess` now flows through the standard managed allowlist/denylist logic, and `unix_sockets` are always honored when present. The cloud-managed `NetworkRequirementsToml`/`NetworkConstraints` field is gone.


### Windows firewall: don't override remote ports unless requested

`windows-sandbox-rs/src/firewall.rs` only calls `SetRemotePorts` when explicitly specified (previously it was always set to `*`, blocking some legitimate outbound traffic). Refactored into a new `configure_rule_network_scope()`.


### `codex debug clear-memories` fully clears

`cli/src/main.rs` now calls `clear_memory_data()` instead of `reset_memory_data_for_fresh_start()`, removing the "fresh start" residue that previously remained.


### Tool-search server descriptions

`tools/src/tool_discovery.rs` now trims and ignores blank `connector_description` strings and falls back to a namespace-prefixed default ("Tools in the {namespace} namespace.") instead of the older "Tools from the {server} MCP server." This fixes confusing or empty headings in the tool-search output for namespaces where the connector description is absent.


### Realtime conversation snapshots and pending input

Several core test snapshots were updated for `pending_input`, `realtime_conversation` cap-when-mirrored behavior, and conversation-startup context selection — reflecting fixes to how user text turns are mirrored to the realtime channel and how startup context picks turns by budget.

**Code references:** updated `core/tests/suite/snapshots/all__suite__pending_input__*` and `all__suite__realtime_conversation__*`.


### Plan-name allowlist for tooltips

`PlanType::ProLite` was added to the tooltip allowlist (in addition to being recognized as a `KnownPlan` everywhere else), so users on the new plan no longer see a generic placeholder in the status tooltip.


### Apply-patch plumbing: proper sandbox propagation

The `MaybeApplyPatchVerified::Body` path now carries the `sandbox` argument through, so verified apply_patch bodies executed by the new in-process runtime are correctly sandboxed (previously the sandbox context could be lost on the `Body` branch).


### Realtime `output_modality` is now required

`ThreadRealtimeStartParams.output_modality` is no longer optional in the v2 schema, eliminating ambiguous realtime starts where the modality silently defaulted.
