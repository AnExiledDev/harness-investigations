# Changelog for version 0.128.0

## Highlights

This release introduces **persisted thread goals** — a new `/goal` command and `get_goal`/`create_goal`/`update_goal` model tools that let Codex pursue a long-running objective with a token budget and automatic continuation. It also ships a **`codex update` subcommand** for self-updating the CLI, a **fully customizable TUI keymap** with a guided `/keymap` editor, **terminal resize reflow** that rebuilds wrapped scrollback when the terminal width changes, and a new **Agent Identity login** flow alongside several backend protocol additions (`hooks/list`, `modelProvider/capabilities/read`, `remoteControl/status/changed`).

Note that several legacy features have been **removed**, including the `js_repl` JavaScript REPL tool, the `/undo` ghost-commit feature, the hidden `codex responses` debug subcommand, and the `--full-auto` flag from `codex sandbox` subcommands.

### Persisted Thread Goals (`/goal`)

**What:** A first-class concept of a *thread goal* — a single long-running objective with status tracking, a token budget, time-spent accounting, and automatic continuation across turns. Goals are persisted in the SQLite state DB so they survive resume.

**Details:**
- New SQL migration `0029_thread_goals.sql` creates a `thread_goals` table keyed by thread, recording `objective`, `status` (`active` / `paused` / `budget_limited` / `complete`), `token_budget`, `tokens_used`, `time_used_seconds`, and creation/update timestamps.
- A new `/goal` slash command opens a goal menu in the TUI (or shows usage help if no thread is active). It is gated on the new `goals` feature flag (`Feature::Goals`).
- Three new model-visible tools are registered when the feature is on:
  - `get_goal` — returns the active goal's status, budgets, token and elapsed-time usage, and remaining tokens.
  - `create_goal` — creates a new goal with a required `objective` and optional positive `token_budget`. Fails if a goal already exists on the thread.
  - `update_goal` — accepts only `status: "complete"`; the model uses it to mark completion after running an explicit completion audit.
- Two new prompt templates ship with the model: `core/templates/goals/continuation.md` (used to nudge the model to continue working toward the goal between turns) and `core/templates/goals/budget_limit.md` (used when the token budget is exhausted, asking the model to wrap up rather than start new substantive work).
- Two new server notifications are emitted to clients whenever the goal moves: `thread/goal/updated` (`ThreadGoalUpdatedNotification`) and `thread/goal/cleared` (`ThreadGoalClearedNotification`). The TUI listens to these to update a live goal-status indicator on the composer.
- Status indicators include compact elapsed-time formatting (`s` / `m` / `h Xm`) implemented in `format_goal_elapsed_seconds()` in `tui/src/goal_display.rs`.
- After thread resume, the app-server emits a goal snapshot and then asks core to `continue_active_goal_if_idle()` so the model can pick up where it left off.

**Code references:** `goals.rs` in `core/src/goals.rs`, `goal_tool.rs` in `tools/src/goal_tool.rs`, `thread_goal_handlers.rs` in `app-server/src/codex_message_processor/thread_goal_handlers.rs`, `goal_menu.rs` and `goal_status.rs` in `tui/src/chatwidget/`, and the migration `0029_thread_goals.sql` in `state/migrations/`.


### `codex update` Subcommand

**What:** A built-in `codex update` command that detects how the CLI was installed (npm, etc.) and runs the appropriate update action.

**Details:**
- Available as a top-level subcommand: `codex update`.
- In debug builds, the command exits early with the message `` `codex update` is not available in debug builds. Install a release build of Codex to use this command. ``
- In release builds, it calls `codex_tui::get_update_action()` to detect the installation method; if detection fails, it prints a manual-update URL.
- The TUI's update detection is now backed by a new `npm_registry.rs` module that fetches package metadata from `https://registry.npmjs.org/@openai%2fcodex` and validates that the desired version's tarball/integrity is present.
- A new `update_versions.rs` module implements semver comparison helpers (`is_newer()`, `extract_version_from_latest_tag()`, `is_source_build_version()`).
- A test (`update_does_not_start_interactive_prompt`) confirms the command exits cleanly without entering interactive mode.

**Code references:** `run_update_command()` in `cli/src/main.rs`, `npm_registry.rs` and `update_versions.rs` in `tui/src/`, `cli/tests/update.rs`.


### Customizable TUI Keymap with `/keymap` Editor

**What:** A complete keybinding configuration system for the TUI, exposed via `[tui.keymap]` in `config.toml` and a guided `/keymap` slash command for in-app remapping.

**Details:**
- New on-disk schema: `tui.keymap` with strongly-typed sections for each focus context — `global`, `chat`, `composer`, `editor`, `pager`, `list`, and `approval`. Each section exposes named actions (e.g. `submit`, `queue`, `move_up`, `delete_backward_word`, `approve_for_session`, `open_thread`).
- Bindings are written as canonical key specs (e.g. `ctrl-a`, `alt-shift-f`, `page-up`). The parser accepts a small alias set (`escape` → `esc`, `pageup` → `page-up`, etc.) and rejects malformed bindings up front with config-path-aware diagnostics.
- Precedence is deterministic: context bindings override `global`, which overrides built-in defaults. Uniqueness is enforced per focus surface so one key cannot trigger two actions on the same input path.
- New `/keymap` command opens a guided picker to pick an action, set or remove a binding, validate it, and persist changes back into `config.toml` while updating the live runtime keymap and bottom-pane bindings together.
- Onboarding screens still use a small fixed shortcut set (`onboarding/keys.rs`) so users can navigate the welcome flow before any custom keymap exists.

**Example `config.toml`:**
```toml
[tui.keymap.global]
copy = "ctrl-shift-c"
open_external_editor = "ctrl-x ctrl-e"

[tui.keymap.composer]
submit = "ctrl-s"
queue = "alt-enter"

[tui.keymap.approval]
approve = "y"
deny = "n"
approve_for_session = "shift-y"
```

**Code references:** `tui_keymap.rs` in `config/src/`, `keymap.rs` and `keymap_setup.rs` (and `keymap_setup/actions.rs`, `keymap_setup/picker.rs`) in `tui/src/`, `keymap_picker.rs` in `tui/src/chatwidget/`.


### Terminal Resize Reflow

**What:** When the terminal width changes, Codex now rebuilds its owned transcript scrollback from in-memory `HistoryCell`s and re-emits it at the new width, instead of leaving wrapped output stuck at the old size.

**Details:**
- New `TerminalResizeReflow` experimental feature, on by default.
- New `tui.terminal_resize_reflow_max_rows` config option caps how many of the most recently rendered rows are replayed during resize. Omit to use Codex's terminal-specific default; set to `0` to keep all rendered rows.
- Per-terminal default caps are encoded in `resize_reflow_cap.rs`: VS Code (1,000), WezTerm (3,500), Windows Terminal (9,001), Alacritty (10,000), with a fallback for unrecognized terminals. These mirror documented scrollback defaults so Codex doesn't replay more rows than the terminal would retain anyway.
- A separate `transcript_reflow.rs` module debounces reflow requests (`TRANSCRIPT_REFLOW_DEBOUNCE = 75 ms`) and tracks the difference between the last *observed* width and the last *rebuilt* width so a final repaint always lands after a drag-resize settles.
- Streaming output is correctly handled: if a stream is mid-flight when the user resizes, the reflow scheduler marks the work as stream-time and forces one final source-backed rebuild after consolidation completes.
- New `width.rs` helper (`usable_content_width`) centralizes "subtract reserved gutter columns" math and returns `None` rather than zero when fixed prefixes consume the entire terminal width, so very narrow terminals fall back to prefix-only rendering instead of producing empty/unstable output.

**Code references:** `resize_reflow.rs` in `tui/src/app/`, `transcript_reflow.rs` and `resize_reflow_cap.rs` and `width.rs` in `tui/src/`, `Feature::TerminalResizeReflow` in `features/src/lib.rs`.


### `codex login --with-agent-identity`

**What:** A new login mode that authenticates Codex using an Agent Identity JWT instead of a ChatGPT session or API key.

**Details:**
- Usage: `printenv CODEX_AGENT_IDENTITY | codex login --with-agent-identity`. The token is read from stdin.
- Cannot be combined with `--with-api-key` — passing both prints `Choose one login credential source: --with-api-key or --with-agent-identity.` and exits with code 1.
- The `agent-identity` crate now decodes and validates JWTs against a JWKS, with a 10-second timeout, fixed audience `codex-app-server`, and issuer `https://chatgpt.com/codex-backend/agent-identity`. Claims include `agent_runtime_id`, `agent_private_key`, `account_id`, `chatgpt_user_id`, `email`, and `plan_type`.
- A new `AGENT_IDENTITY_LOGIN_DISABLED_MESSAGE` is shown when the deployment forces API-key login.

**Code references:** `run_login_with_agent_identity()` in `cli/src/login.rs`, `agent-identity/src/lib.rs`, login dispatch in `cli/src/main.rs`.


### `hooks/list` and `modelProvider/capabilities/read` App-Server RPCs

**What:** Two new v2 protocol methods for clients to introspect the active configuration.

**Details:**
- `hooks/list` (`HooksListParams` → `HooksListResponse`): lists every configured hook with `HookMetadata` describing the event name, handler type, source (`User` / `Project` / `Plugin`), source path on disk, plugin id, display order, enabled flag, and managed status. The integration test in `app-server/tests/suite/v2/hooks_list.rs` shows hooks contributed by both user config and plugin manifests.
- `modelProvider/capabilities/read` (`ModelProviderCapabilitiesReadParams` → `ModelProviderCapabilitiesReadResponse`): returns the active model provider's capability flags. Builders include `with_namespace_tools_capability()`, `with_image_generation_capability()`, and `with_web_search_capability()` for clients that need to compose a synthetic response.

**Code references:** Protocol definitions in `app-server-protocol/schema/json/v2/HooksListParams.json`, `HooksListResponse.json`, `ModelProviderCapabilitiesReadParams.json`, `ModelProviderCapabilitiesReadResponse.json`; tests in `app-server/tests/suite/v2/hooks_list.rs` and `app-server/tests/suite/v2/model_provider_capabilities_read.rs`.


### `remoteControl/status/changed` Notification

**What:** App-server clients can now observe the live state of the optional remote-control websocket connection.

**Details:**
- New notification `remoteControl/status/changed` with payload `RemoteControlStatusChangedNotification { status, environmentId }`.
- `RemoteControlConnectionStatus` enum: `disabled`, `connecting`, `connected`, `errored`.
- `RemoteControlHandle::set_enabled()` now refuses to enable remote control when the SQLite state DB is unavailable and logs a warning, since enrollment cache writes need persistence to function correctly.
- Clients that subscribe receive an immediate snapshot of the current status when they connect.

**Code references:** `transport/remote_control/mod.rs` and `transport/remote_control/websocket.rs` in `app-server/src/`, `RemoteControlStatusChangedNotification.json`.


### Plugin-Bundled Hooks (`plugin_hooks` feature)

**What:** A new feature flag (`plugin_hooks`) that lets installed plugins contribute lifecycle hooks declared in their bundle.

**Details:**
- When enabled, the plugin loader reads `hooks/hooks.json` from each active plugin and exposes those hooks via `effective_plugin_hook_sources()`.
- Hooks contributed by plugins show up in the new `hooks/list` RPC with `source: "Plugin"` and the originating `plugin_id`.
- The `[plugins.<id>]` config section now also supports a `mcp_servers` map — a `PluginMcpServerConfig` overlay per server with `enabled`, `default_tools_approval_mode`, `enabled_tools` allow-list, `disabled_tools` deny-list, and per-tool approval settings keyed by tool name. Transport settings remain owned by the plugin manifest.

**Code references:** `Feature::PluginHooks` in `features/src/lib.rs`, `load_plugin_hooks()` in core-plugins, schema additions in `core/config.schema.json`.


### `enable_mcp_apps` and `apps_mcp_path_override` Features

**What:** Two new feature gates around the built-in apps MCP server.

**Details:**
- `enable_mcp_apps` (under-development, default off) toggles whether the apps MCP server runs.
- `apps_mcp_path_override` allows pointing the apps MCP server at a custom executable path. The TOML schema accepts a boolean shorthand or a full table:
  ```toml
  [features.apps_mcp_path_override]
  enabled = true
  path = "/usr/local/bin/codex-apps-mcp"
  ```
- A new dedicated `codex-mcp/src/codex_apps.rs` module owns the unique parts of the ChatGPT-hosted Codex Apps connector: cache scoping by authenticated user (`account_id`, `chatgpt_user_id`, workspace flag), disk cache with schema version `2`, and connector allow-list filtering.

**Code references:** `Feature::EnableMcpApps`, `Feature::AppsMcpPathOverride`, `AppsMcpPathOverrideConfigToml` in `features/src/feature_configs.rs`; `codex_apps.rs` in `codex-mcp/src/`.


### MCP Elicitation Tracking

**What:** A new tracker for MCP server elicitation requests — when an MCP server asks Codex to elicit data from the user, Codex now decides whether to auto-approve, deny by policy, or surface a Codex protocol event to be answered later.

**Details:**
- The new `elicitation.rs` module owns an `ElicitationRequestManager` with a stored responder map. RMCP clients call into it for each `CreateElicitationRequestParams`.
- Auto-approval reuses `mcp_permission_prompt_is_auto_approved()`; otherwise the request becomes a `Codex` `EventMsg::ElicitationRequest` with an `ElicitationAction` resolved through the stored responder.

**Code references:** `elicitation.rs` in `codex-mcp/src/`.


### `codex-core-api` Crate and `thread-manager-sample`

**What:** A new public facade crate (`codex-core-api`) that re-exports the `ThreadManager` API, plus a sample binary (`codex-thread-manager-sample`) that demonstrates how to embed Codex.

**Details:**
- `codex-core-api` re-exports `ThreadManager`, `CodexThread`, `StartThreadOptions`, `ThreadShutdownReport`, `ForkSnapshot`, `McpManager`, plus selected types from `codex-config` and `codex-analytics`. The crate is declared `#![deny(private_bounds, private_interfaces, unreachable_pub)]` to keep the surface clean.
- The sample binary lets you start a thread, submit a single user turn, and print the assistant's final reply:
  ```sh
  cargo run -p codex-thread-manager-sample -- "Say hello"
  cargo run -p codex-thread-manager-sample -- --model gpt-5.2 "Say hello"
  printf 'Say hello\n' | cargo run -p codex-thread-manager-sample
  ```

**Code references:** `core-api/src/lib.rs`, `thread-manager-sample/README.md` and `thread-manager-sample/src/main.rs`.


### Other New Crates

The workspace gained several new crates that split out previously embedded functionality:

- **`codex-memories-read` and `codex-memories-write`** — Memory injection, citation parsing, and read-side telemetry are now in `memories/read`; the startup memory pipeline, file-backed artifact helpers, Phase 1/Phase 2 prompt rendering, extension pruning, and workspace diffing live in `memories/write`. `clear_memory_roots_contents()` moved out of `codex-core` and into `codex-memories-write`.
- **`codex-agent-graph-store`** — Storage-neutral persistence for spawned-thread parent/child topology, with an `AgentGraphStore` trait and a `ThreadSpawnEdgeStatus` (`Open` / `Closed`) lifecycle marker.
- **`codex-external-agent-sessions`** — Detects up to 50 recent external-agent (e.g. Claude) `*.jsonl` session files in `~/.claude/projects/...`, summarizes them, and tracks which have already been imported using a per-codex-home ledger. Sessions older than 30 days are skipped.
- **`codex-external-agent-migration`** — Imports an external agent's MCP config, hooks (subdirectory `hooks/`), and slash commands as Codex skills (with `source-command` prefix and length-bounded names/descriptions).
- **`codex-file-system`** — The `FileSystem` abstraction was moved out of `exec-server` into a standalone crate so callers can depend on it without pulling in the rest of exec-server.

**Code references:** `Cargo.toml` workspace members list, individual crate `lib.rs` files.


### Goal-Aware Multi-Agent Hints

**What:** The MultiAgent v2 feature now distinguishes between root-agent and sub-agent usage hints.

**Details:**
- New TOML keys `root_agent_usage_hint_text` and `subagent_usage_hint_text` in `[features.multi_agent_v2]`.
- Sessions sourced from `SubAgent(ThreadSpawn { .. })` get the subagent hint; CLI/VSCode/Exec/MCP sessions get the root hint.
- Two more knobs were added: `max_concurrent_threads_per_session` (min 1) and `min_wait_timeout_ms` (1–3,600,000).

**Code references:** `multi_agents.rs` in `core/src/session/`, `MultiAgentV2ConfigToml` in `features/src/feature_configs.rs`.


### Agent Interrupt Message Toggle

**What:** A new `[agents] interrupt_message = false` setting suppresses the model-visible "this turn was interrupted" message that Codex normally records when an agent turn is cut short.

**Code references:** `interrupt_message` field on the agents schema in `core/config.schema.json` and `config/src/types.rs`.


### `tool_suggest.disabled_tools`

**What:** The tool-suggest discoverability list can now be balanced with an explicit deny-list.

**Details:**
- New `disabled_tools` array in `[tool_suggest]`, each entry typed as either `{ type = "plugin", id = "..." }` or `{ type = "connector", id = "..." }`.
- Helper constructors `ToolSuggestDisabledTool::plugin(id)` and `ToolSuggestDisabledTool::connector(id)` plus a `normalized()` form that trims whitespace.

**Code references:** `ToolSuggestDisabledTool` in `config/src/types.rs`.


### `experimental_thread_store` Now Supports `local`, `remote`, and Debug `in_memory`

**What:** Thread persistence selection is now a tagged union instead of a single endpoint string.

**Details:**
- New TOML shape:
  ```toml
  experimental_thread_store = { type = "local" }
  experimental_thread_store = { type = "remote", endpoint = "https://..." }
  # debug builds only
  experimental_thread_store = { type = "in_memory", id = "test-store-id" }
  ```
- The legacy string-form `experimental_thread_store_endpoint` continues to parse for backwards compatibility, but the new tagged form is preferred and is what tests use.
- A new test `remote_thread_store.rs` verifies that, when a non-local store is configured, the temporary `codex_home` does not accumulate rollout session files or sqlite state files — i.e. no accidental local persistence.

**Code references:** `thread_store_from_config()` in app-server, `ThreadStoreToml` in `core/config.schema.json`, `app-server/tests/suite/v2/remote_thread_store.rs`.


### `--permissions-profile` for `codex sandbox`

**What:** The `codex sandbox` debug subcommands (`macos`, `linux`, `windows`, plus the legacy `seatbelt` / `landlock` aliases) accept a `--permissions-profile <NAME>` flag pointing at a profile defined in `[permissions.<name>]` or one of the built-ins (e.g. `:workspace`).

**Details:** Also adds a `-C, --cwd <PATH>` option for sandbox profile resolution.

**Code references:** `cli/src/debug_sandbox.rs`.


### `CODEX_THREAD_ID` Environment Variable

**What:** Shell environments built by Codex now include a `CODEX_THREAD_ID` variable (when a thread id is available) so child commands can correlate themselves with the active Codex thread.

**Code references:** `CODEX_THREAD_ID_ENV_VAR` and `create_env()` in the new `protocol/src/shell_environment.rs`.


### `connection_rpc_gate` and Related Connection Hardening

**What:** A per-connection RPC gate (`ConnectionRpcGate`) coordinates queued handler execution so that closing a connection prevents new handlers from starting while still allowing in-flight handlers to finish.

**Code references:** `connection_rpc_gate.rs` in `app-server/src/`.

### Auto-Review Recent Denials List

The TUI now keeps a rolling list of the last 10 denied guardian assessments via `RecentAutoReviewDenials` so the user can quickly review what was just blocked, deduplicating by event id and keeping the freshest entry first.

**Code references:** `auto_review_denials.rs` in `tui/src/`.


### Activity-Based Terminal Title

The default terminal title items now include `activity` (a spinner that switches into an "[ ! ] Action Required" indicator while Codex is blocked on user input), instead of the prior `spinner`. The title format is composed from `TerminalTitleItem`s via the new `build_action_required_title_text()` helper.

**Code references:** `action_required_title.rs` in `tui/src/bottom_pane/`.


### Cloud Requirements Eligibility Helper

The cloud-requirements check is now centralized in a `cloud_requirements_eligible_auth(auth)` helper, which only proceeds when the auth uses the Codex backend AND the plan is business-like or `Enterprise`. This replaces two duplicate inline checks in `CloudRequirementsService`.

**Code references:** `cloud-requirements/src/lib.rs`.


### `ThreadFork` and `ThreadResume` Path Routing

The serialization scope for `thread/fork` and `thread/resume` now resolves to a thread id when one is provided and to a rollout *path* otherwise. This lets app-server clients reuse path-only resume/fork against rollout files without having a thread id yet.

**Code references:** `thread_or_path` macro in `app-server/src/request_serialization.rs`.


### Permission Profile Compatibility Layer

A new `legacy_compatible_permission_profile()` projects new-style `PermissionProfile` values into shapes still required by older or remote app-server APIs. When a profile cannot round-trip to the legacy sandbox policy directly, it falls back to a synthesized `workspace-write`-style profile based on the actual file-system and network policies.

**Code references:** `permission_compat.rs` in `tui/src/`.


### Active Permission Profile in V2 Protocol

The v2 protocol now exposes `ActivePermissionProfile` (with `id`, `extends`, and bounded `modifications`) and a new `ActivePermissionProfileModification::AdditionalWritableRoot { path }` variant that replaces the prior `ReadOnlyAccess` shape. This makes the user-applied permissions modifications explicit and machine-readable.

**Code references:** `ActivePermissionProfile.ts` and `ActivePermissionProfileModification.ts` in `app-server-protocol/schema/typescript/v2/`.


### Remote Control Enrollment Now Surfaces Errors

`load_persisted_remote_control_enrollment()` returns `io::Result<Option<...>>` instead of swallowing missing-state-DB and load failures as `None`. Callers now distinguish "no enrollment cached" from "the cache is unavailable", and surface a real `io::Error` upstream when SQLite is disabled.

**Code references:** `transport/remote_control/enroll.rs` in `app-server/src/`.


### Feedback Attachments Can Override Filenames

`FeedbackAttachmentPath { path, attachment_filename_override }` lets feedback uploaders provide a custom attachment filename instead of inheriting the basename from the path. Useful for redacted or generated attachments.

**Code references:** `feedback/src/lib.rs`.


### MCP Connection Manager Refactor

`McpConnectionManager` was reorganized into focused modules: `connection_manager.rs` aggregates running RMCP clients, owns startup status events and origin metadata, and routes tool calls; `runtime.rs` describes per-caller placement (sandbox state, runtime paths, working directory) so status snapshots and real sessions make the same local-vs-remote decision; the old `mcp_tool_names.rs` was renamed to `tools.rs`. This is primarily an internal restructure but the new `SandboxState` payload is now sent to capable MCP servers and includes the `permission_profile`, `sandbox_policy`, `codex_linux_sandbox_exe`, `sandbox_cwd`, and `use_legacy_landlock` flag.

**Code references:** `connection_manager.rs`, `runtime.rs`, and `tools.rs` in `codex-mcp/src/`.


### Network Proxy Connect Policy

A new `TargetCheckedTcpConnector` enforces "no non-public IPs as proxy targets" before opening TCP connections out of the proxy. This hardens the network-proxy crate's connect path against accidental SSRF-style targeting of internal addresses.

**Code references:** `connect_policy.rs` in `network-proxy/src/`.


### Keyboard Enhancement Setup Hardened

The TUI keyboard-enhancement push/pop now lives in a dedicated `tui/keyboard_modes.rs` module and respects a `CODEX_TUI_DISABLE_KEYBOARD_ENHANCEMENT` environment variable plus auto-detection for WSL+VS Code, so terminals that don't survive the normal stack pop (notably WSL inside the VS Code integrated terminal) won't leave a parent shell with enhanced key reporting after Codex exits.

**Code references:** `tui/keyboard_modes.rs` in `tui/src/`.


### Resume Continues an Active Goal

When a thread is resumed and the `goals` feature is enabled, the app-server emits a `thread/goal/updated` snapshot to the client *before* asking core to call `continue_active_goal_if_idle()`. This guarantees the client sees the goal state before any model output that the continuation produces.

**Code references:** `app-server/src/codex_message_processor/thread_goal_handlers.rs`.


### Cleaner JSON-RPC Error Helpers

The app-server's resume path now uses small `internal_error()` / `invalid_request()` helpers and propagates `Result<bool, JSONRPCErrorError>` from `resume_running_thread()` rather than constructing `JSONRPCErrorError` ad-hoc and short-circuiting through booleans. This is a small ergonomic cleanup that reduces duplicated code at error sites.

### `codex login` Refuses Conflicting Credential Sources

Previously, supplying both `--with-api-key` and `--with-agent-identity` would silently take whichever check came first. Now the login command exits with code 1 and prints a clear message: `Choose one login credential source: --with-api-key or --with-agent-identity.`

**Code references:** `cli/src/main.rs` login dispatch.


### Width Underflow in Narrow Terminals

Several rendering paths reserved fixed columns for bullets, gutters, or labels and then attempted wrapped layout at zero or negative content width when the terminal got too narrow. This produced empty or unstable output. The new `usable_content_width()` helper enforces a strict-positive contract (`Some(n)` where `n > 0`, or `None`), and callers now fall back to prefix-only rendering instead of wrapping at 0 columns.

**Code references:** `width.rs` in `tui/src/`.


### Streaming-Aware Resize Reflow

If a stream was active when a terminal resize landed, the previous behaviour could leave the transcript wedged with stale wrapped lines because the reflow happened before the stream consolidated. The new resize-reflow scheduler explicitly marks reflow work as stream-time, holds it until the stream becomes source-backed history, and then issues one final source-backed rebuild.

**Code references:** `resize_reflow.rs` in `tui/src/app/`, `transcript_reflow.rs` in `tui/src/`.


### Remote Control Won't Enable Without State DB

Previously, enabling remote control with the SQLite state DB disabled would cause enrollment cache reads to silently fail (returning `None`). Now `RemoteControlHandle::set_enabled(true)` is rejected with a logged warning when the state DB is unavailable, and the persisted-enrollment loader returns a real `io::Error` upstream.

**Code references:** `transport/remote_control/mod.rs` and `transport/remote_control/enroll.rs` in `app-server/src/`.

### `js_repl` JavaScript REPL

The persistent Node.js–backed JavaScript REPL (and its `js_repl_tools_only` companion) has been removed. Both feature keys are now `Stage::Removed`; existing configs that set them are silently ignored (a regression test confirms this). The newer `code_mode` feature, which uses an in-process V8 runtime, replaces it.

**Code references:** `Feature::JsRepl` and `Feature::JsReplToolsOnly` in `features/src/lib.rs`. The `js_repl_node_module_dirs` and `js_repl_node_path` config keys are also gone.


### `/undo` and Ghost Commits

The `undo` feature (which created a ghost commit at every turn so users could roll back) has been removed. The `Feature::GhostCommit` enum value is kept only so old configs that set `undo = true` still parse without erroring. The `[ghost_snapshot]` settings (`disable_warnings`, `ignore_large_untracked_dirs`, `ignore_large_untracked_files`) are now documented as legacy no-ops retained for compatibility, and `compact_remote.rs` no longer preserves `GhostSnapshot` items across compaction.

**Code references:** `Feature::GhostCommit` in `features/src/lib.rs`, `compact_remote.rs` in `core/src/`.


### Hidden `codex responses` Subcommand

The internal `codex responses` debug subcommand (which sent a single raw Responses API payload through Codex auth) has been removed. A regression test verifies the subcommand is no longer registered. The `responses_cmd.rs` source file was deleted.

**Code references:** `cli/src/main.rs` test `responses_subcommand_is_not_registered`.


### `--full-auto` on `codex sandbox`

The `--full-auto` flag was removed from `codex sandbox macos`, `codex sandbox linux`, `codex sandbox windows`, and the legacy `codex debug seatbelt` / `codex debug landlock` aliases. The README now suggests passing `-c 'sandbox_mode="workspace-write"'` when you want a writable legacy sandbox mode for these commands.

**Code references:** `cli/src/debug_sandbox.rs`, `codex-rs/README.md`.


### `general_analytics` Feature

The `general_analytics` boolean feature flag has been removed; thread lifecycle analytics emitted via the app-server analytics pipeline are no longer gated.

**Code references:** removal of `Feature::GeneralAnalytics` in `features/src/lib.rs`.
