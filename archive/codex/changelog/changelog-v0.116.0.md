# Changelog for version 0.116.0

## Highlights

This release introduces the **app-server-backed TUI** as a new experimental code path, complete with a new `--remote` flag that lets the TUI connect to a remote app-server over a WebSocket. It also adds the long-awaited **`UserPromptSubmit` hook event** for intercepting and augmenting user prompts, structured **memory citations** on agent messages, **device-code ("headless") ChatGPT sign-in** for remote machines, and remote-synced plugin install/uninstall that pushes state to your ChatGPT account. On the cleanup side, the experimental `skills/remote/*` API and the `responses_websockets` / `responses_websockets_v2` feature flags have been retired.

### App-server-backed TUI (`tui_app_server` feature)
**What:** A complete rewrite of the interactive TUI as a separate `codex-tui-app-server` crate that drives the UI through the app-server JSON-RPC protocol instead of calling into core in-process. The legacy in-process TUI continues to exist; the new one is opt-in.

**Details:**
- Added a new top-level `tui_app_server` crate (~150+ source files) that mirrors the legacy `tui` crate but talks to either an in-process or remote app-server.
- Gated behind a new experimental feature `tui_app_server` (default off). Enable with `codex features enable tui_app_server`.
- When the feature is enabled, `codex` (interactive) routes through `codex_tui_app_server::run_main` instead of `codex_tui::run_main`. See `should_use_app_server_tui()` in `codex-rs/tui/src/app_server_tui_dispatch.rs`.
- The new TUI can run against either an embedded in-process app-server or a remote one (see `--remote` below).

**Code references:** New crate `codex-rs/tui_app_server/`, `Feature::TuiAppServer` in `codex-rs/core/src/features.rs`, dispatch in `codex-rs/tui/src/app_server_tui_dispatch.rs`.


### `--remote <ws://…>` flag for connecting to a remote app-server
**What:** A new top-level CLI flag that lets the interactive TUI connect to an app-server running on another machine (or container) over WebSocket instead of starting an in-process one.

**Details:**
- Accepts only `ws://` and `wss://` URLs *with an explicit port* — bare `host:port` shortcuts and `https://` URLs are rejected.
- Only valid for the interactive TUI; passing `--remote` with `apply`, `responses-api-proxy`, `stdio-to-uds`, `features list/enable/disable`, etc. fails with a clear error message.
- Requires `tui_app_server` to be enabled — passing `--remote` without the feature flag returns a fatal error: `` `--remote` requires the `tui_app_server` feature flag to be enabled. ``

**Usage example:**
```sh
codex features enable tui_app_server
codex --remote ws://10.0.0.5:4500
```

**Code references:** `normalize_remote_addr()` in `codex-rs/tui_app_server/src/cli.rs`, gating in `run_interactive_tui()` in `codex-rs/cli/src/main.rs`, transport in `codex-rs/app-server-client/src/remote.rs`.


### `RemoteAppServerClient` (WebSocket app-server client)
**What:** A new public type in the `codex-app-server-client` crate that connects to an app-server over WebSocket, sends typed `ClientRequest`s, receives notifications, and answers `ServerRequest`s — feature-equivalent to the existing `InProcessAppServerClient`.

**Details:**
- Exposed as `RemoteAppServerClient` and `RemoteAppServerConnectArgs`.
- 10-second connect and initialize timeouts, bounded channel capacity for backpressure.
- New unified `AppServerClient` enum (`InProcess` / `Remote`) and `AppServerEvent` enum so callers can be transport-agnostic.
- Pulls in `tokio-tungstenite`, `futures`, and `url` as new dependencies.

**Code references:** `codex-rs/app-server-client/src/remote.rs` (new file), `RemoteAppServerClient::connect()` and `RemoteAppServerRequestHandle`.


### `UserPromptSubmit` hook event
**What:** A new hook event that fires every time the user submits a prompt, in parallel to the existing `SessionStart` and `Stop` hooks. Hooks can inject additional context into the conversation or block the prompt entirely.

**Details:**
- New `HookEventName::UserPromptSubmit` variant with `"user-prompt-submit"` matcher label.
- Hook output schema supports `decision: "block"` with a `reason` to stop the prompt, plus `additionalContext` to inject extra context for the model.
- When a hook blocks, the contributed `additional_contexts` are persisted and replayed on the next turn so the user's intent is not silently dropped.
- New JSON schemas published at `codex-rs/hooks/schema/generated/user-prompt-submit.command.{input,output}.schema.json`.

**Configuration example (`~/.codex/settings.json`):**
```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "/path/to/check_prompt.py"
      }]
    }]
  }
}
```

**Code references:** `run_user_prompt_submit_hooks()` in `codex-rs/core/src/hook_runtime.rs`, `UserPromptSubmitRequest`/`UserPromptSubmitOutcome` in `codex-rs/hooks/src/events/user_prompt_submit.rs`.


### `[tool_suggest]` config section
**What:** A new top-level config section that lets users curate which connectors and plugins are surfaced as discoverable tool suggestions to the model.

**Details:**
- Each entry has a `type` (`connector` or `plugin`) and an `id`. Whitespace-only IDs are dropped during loading.
- Curated allowlist of the OpenAI-curated plugins eligible for tool-suggest (github, notion, slack, gmail, google-calendar, google-docs, google-drive, google-sheets, google-slides) is enforced in `list_tool_suggest_discoverable_plugins()`.

**Configuration example (`~/.codex/config.toml`):**
```toml
[tool_suggest]
discoverables = [
  { type = "connector", id = "connector_alpha" },
  { type = "plugin",    id = "github@openai-curated" },
]
```

**Code references:** `ToolSuggestConfig` / `ToolSuggestDiscoverable` / `ToolSuggestDiscoverableType` in `codex-rs/core/src/config/types.rs`, `resolve_tool_suggest_config()` in `codex-rs/core/src/config/mod.rs`, `list_tool_suggest_discoverable_plugins()` in `codex-rs/core/src/plugins/discoverable.rs`.


### Memory citations on agent messages
**What:** Agent messages can now carry a structured `MemoryCitation` containing concrete `path:line-range|note=[…]` entries plus the source rollout/thread IDs, surfaced through the v2 `ThreadItem` schema.

**Details:**
- New `MemoryCitation { entries, thread_ids }` and `MemoryCitationEntry { path, line_start, line_end, note }` types in both `codex-protocol` and `codex-app-server-protocol/v2`.
- New parser `parse_memory_citation()` understands `<citation_entries>…</citation_entries>` blocks emitted by the model in addition to the existing `<thread_ids>` / `<rollout_ids>` blocks. It is duplicate-aware (rollout IDs deduplicated in insertion order).
- The `agentMessage` thread item now exposes an optional `memoryCitation` field for clients.

**Code references:** `codex-rs/protocol/src/memory_citation.rs` (new file), `parse_memory_citation()` in `codex-rs/core/src/memories/citations.rs`, `MemoryCitation` in `codex-rs/app-server-protocol/src/protocol/v2.rs`.


### Headless ChatGPT sign-in (device code)
**What:** A new sign-in option in the onboarding flow that lets you authenticate to ChatGPT from another device using a one-time code — useful when the box running Codex has no browser (SSH, container, headless server).

**Details:**
- New `SignInOption::DeviceCode` and `SignInState::ChatGptDeviceCode(ContinueWithDeviceCodeState)` variants in the new TUI's onboarding screen.
- Description in the picker reads: *"Sign in from another device with a one-time code"*.
- Implementation lives in `codex-rs/tui_app_server/src/onboarding/auth/headless_chatgpt_login.rs`.

**Code references:** `start_device_code_login()` in `codex-rs/tui_app_server/src/onboarding/auth.rs`, `start_headless_chatgpt_login()` in `codex-rs/tui_app_server/src/onboarding/auth/headless_chatgpt_login.rs`.


### `force_remote_sync` for plugin install/uninstall
**What:** `plugin/install` and `plugin/uninstall` JSON-RPC methods now accept an optional `forceRemoteSync` boolean that pushes the change to the ChatGPT account's remote plugin state before applying it locally.

**Details:**
- Backed by new `enable_remote_plugin()` and `uninstall_remote_plugin()` HTTP calls to `/plugins/list`, `/plugins/{id}/enable`, `/plugins/{id}/uninstall` on the ChatGPT base URL.
- ChatGPT auth is required; API-key auth returns `UnsupportedAuthMode`.
- New error variant `CorePluginInstallError::Remote` / `CorePluginUninstallError::Remote` for surfaced remote-side failures, with messages like `"failed to enable remote plugin: …"`.
- 30-second timeout for the mutation; verifies that the response's plugin id and enabled state match what was requested.

**Code references:** `codex-rs/core/src/plugins/remote.rs` (new file: `enable_remote_plugin`, `uninstall_remote_plugin`, `fetch_remote_plugin_status`), `install_plugin_with_remote_sync()` / `uninstall_plugin_with_remote_sync()` in `codex-rs/core/src/plugins/manager.rs`.


### `Custom` `SessionSource` and `--session-source` flag for the app-server
**What:** Embedders can now stamp threads with an arbitrary session source label, in addition to the built-ins (`vscode`, `cli`, `exec`, `mcp`).

**Details:**
- New `SessionSource::Custom(String)` variant, plus a matching `ThreadSourceKind::Custom` and v2 protocol variant.
- New `--session-source <SOURCE>` CLI flag on `codex app-server` (default `vscode`). Unknown non-empty values are recorded as custom sources via `SessionSource::from_startup_arg()`.
- Threads are now filtered by session source when listing skills/plugins (`filter_skills_for_session_source`, `filter_skill_load_outcome_for_session_source`).

**Usage example:**
```sh
codex app-server --session-source atlas --listen 127.0.0.1:4500
```

**Code references:** `SessionSource::Custom` in `codex-rs/protocol/src/protocol.rs`, `from_startup_arg()` and CLI parsing in `codex-rs/app-server/src/main.rs`.


### `[config_requirements] guardian_developer_instructions`
**What:** Workspace-managed config requirements files can now override the developer-facing portion of the guardian policy text by setting `guardian_developer_instructions`.

**Details:**
- Whitespace-only values are normalized to `None`.
- The trimmed value flows through into `Config::guardian_developer_instructions` and overrides the default guardian prompt.

**Configuration example:**
```toml
# In a config requirements file
guardian_developer_instructions = "Use the workspace-managed guardian policy."
```

**Code references:** `ConfigRequirementsToml::guardian_developer_instructions` in `codex-rs/core/src/config/state.rs`, threaded through `ConfigRequirementsWithSources`.


### Realtime conversation v1/v2 protocol split
**What:** The Codex realtime websocket endpoint has been split into versioned protocol modules (v1 and v2), and clients are told which version is active via a new `version` field on `ThreadRealtimeStartedNotification`.

**Details:**
- New `RealtimeConversationVersion` enum (`"v1"` | `"v2"`) in `codex-protocol`.
- New files `codex-rs/codex-api/src/endpoint/realtime_websocket/methods_common.rs`, `methods_v1.rs`, `methods_v2.rs`, plus `protocol_v1.rs` / `protocol_v2.rs`.
- Realtime audio chunks now also carry an optional `item_id` so clients can attribute audio frames to specific response items.

**Code references:** `RealtimeConversationVersion` in `codex-rs/protocol/src/protocol.rs`, dispatch helpers in `codex-rs/codex-api/src/endpoint/realtime_websocket/methods_common.rs`.


### Plugin marketplace `interface.displayName`
**What:** Plugin marketplace entries can now declare a `MarketplaceInterface { displayName }` so the UI can render a human-friendly name distinct from the marketplace's internal name.

**Code references:** `MarketplaceInterface` in `codex-rs/app-server-protocol/src/protocol/v2.rs`, used by `PluginMarketplaceEntry`.


### `Environment` / `ExecutorFileSystem` abstraction (new `environment` crate)
**What:** A new `codex-environment` workspace crate factors filesystem access behind an `ExecutorFileSystem` trait, replacing direct `tokio::fs` calls in the app-server's `fs/*` API surface.

**Details:**
- Public API: `Environment`, `ExecutorFileSystem`, `FileMetadata`, `FileSystemResult`, `ReadDirectoryEntry`, `CopyOptions`, `CreateDirectoryOptions`, `RemoveOptions`.
- App-server's `FsApi` is now generic over the trait, paving the way for sandboxed/virtualized file backends.

**Code references:** `codex-rs/environment/src/lib.rs` and `codex-rs/environment/src/fs.rs` (new crate), uses in `codex-rs/app-server/src/fs_api.rs`.


### One more agent codename
The pool of generated agent codenames now includes **Jason** alongside Erdos, Ramanujan, etc. (`codex-rs/core/src/agent/agent_names.txt`).

### Linux sandbox prefers system bubblewrap
The bubblewrap pipeline now prefers `/usr/bin/bwrap` whenever it's installed and only falls back to the vendored bubblewrap binary when the system one is missing. When the fallback path is taken, Codex now emits a startup warning through the standard config-warning channel (visible in the TUI/IDE) instead of printing from the sandbox helper. Documented in `codex-rs/linux-sandbox/README.md` and implemented as the new `BubblewrapLauncher` enum in `codex-rs/linux-sandbox/src/launcher.rs`.


### Windows sandbox: elevated backend supports restricted read-only roots
The elevated Windows setup/runner backend now honors legacy `ReadOnlyAccess::Restricted` for `read-only` and `workspace-write` policies — restricted reads honor explicit readable roots plus the command `cwd`, and writable roots stay readable when `workspace-write` is used. When `include_platform_defaults = true`, the elevated backend also adds backend-managed system read roots (`C:\Windows`, `C:\Program Files`, `C:\Program Files (x86)`, `C:\ProgramData`). Documented in `codex-rs/core/README.md`. The unelevated restricted-token backend keeps the existing fail-closed behavior. Internally, the windows-sandbox crate has been reorganized into `elevated/` (command_runner, ipc_framed, runner_pipe, cwd_junction) and `conpty/` submodules.


### Memory stage-1 sanitization filters AGENTS.md and skill payloads
Memory stage-1 generation now sanitizes user messages before persisting them: injected `AGENTS.md` blocks (`# AGENTS.md instructions for …`) and `<skill>…</skill>` payloads are stripped because they're prompt scaffolding rather than conversation content, while environment context and subagent notifications are kept. Developer-role messages are dropped entirely. See `is_memory_excluded_contextual_user_fragment()` in `codex-rs/core/src/contextual_user_message.rs` and `sanitize_response_item_for_memories()` in `codex-rs/core/src/memories/phase1.rs`.


### Clipboard: OSC 52 fallback for SSH / WSL
Copy-to-clipboard now detects SSH sessions (via `SSH_CONNECTION` / `SSH_TTY`) and emits an OSC 52 escape sequence so the user's local terminal owns the copy, instead of writing into the remote machine's clipboard. WSL also gets the OSC 52 fallback when `arboard` cannot reach a clipboard daemon. The new TUI also surfaces a Ctrl+Alt+V hint in the footer when running under WSL because terminals frequently intercept plain Ctrl+V there.


### Agent jobs use status subscriptions instead of polling
The agent-job loop now subscribes to per-thread `AgentStatus` watch channels (`subscribe_status`) and waits on status changes via a `FuturesUnordered` selector, replacing the previous fixed `STATUS_POLL_INTERVAL` sleep. This lowers idle CPU use and reduces latency between an agent finishing and the orchestrator emitting progress events. See `wait_for_status_change()` in `codex-rs/core/src/tools/handlers/agent_jobs.rs`.


### Plugin curated repo sync is session-source-aware
`maybe_start_curated_repo_sync_for_config()` now takes a `&SessionSource` argument so curated marketplace sync only runs for sources that should see it, avoiding unwanted background work for `Custom` sources or non-VSCode embedders.


### Tool-suggest filters out plugins for codex-tui clients
When the app-server detects an `app_server_client_name` of `"codex-tui"`, it now filters `Plugin` discoverable suggestions out of the tool-suggest results (only `Connector` suggestions are shown). See `filter_tool_suggest_discoverable_tools_for_client()` in `codex-rs/core/src/tools/discoverable.rs`.


### Discoverable connectors expose `install_url`
`DiscoverableTool::Connector` now exposes its `install_url` (when present) so UIs can deep-link into the connector marketplace. See `DiscoverableTool::install_url()`.


### Memory excludes developer-role messages from stage-1
In `serialize_filtered_rollout_response_items()`, messages with `role == "developer"` are now omitted entirely instead of being passed to memory generation.


### Sub-agents inherit the parent's exec policy
When spawning a sub-agent via `ThreadSpawn`, the orchestrator now also inherits the parent thread's `ExecPolicyManager` (when `child_uses_parent_exec_policy()` allows it), in addition to the existing shell-snapshot inheritance, so child agents see the same allow/deny exec rules. See `inherited_exec_policy_for_source()` in `codex-rs/core/src/agent/control.rs`.


### Threads database tracks model and reasoning effort
A new SQL migration `0020_threads_model_reasoning_effort.sql` adds `model TEXT` and `reasoning_effort TEXT` columns to the `threads` table so resumed threads can re-establish the correct model/effort instead of falling back to the current default.


### Pinned artifact runtime version bumped to 2.5.6
The pinned artifact-runtime version used for package-manager-backed installs has been bumped from `0.1.0` to `2.5.6` (`ARTIFACT_RUNTIME` in the new `codex-rs/core/src/packages/versions.rs`).


### Session startup prewarm is now an explicit handle
The startup websocket prewarm has been refactored from an implicit scheduled task into an explicit `SessionStartupPrewarmHandle` that's set on the session and taken by the regular task. This lets `regular_turn_emits_turn_started_without_waiting_for_startup_prewarm` ship a turn-started event without blocking on prewarm completion, and lets a turn interrupt cleanly abort the prewarm. See `codex-rs/core/src/session_startup_prewarm.rs` and the `Session::set_session_startup_prewarm` / `take_session_startup_prewarm` APIs.


### Auth env telemetry
A new `AuthEnvTelemetry` struct collects metadata about which auth env vars are in effect (provider env-key name, codex-api-key env enabled, etc.) and threads it through clients and metrics emission. See `codex-rs/core/src/auth_env_telemetry.rs`.

### Blocked `UserPromptSubmit` hooks no longer drop additional context
When a `UserPromptSubmit` hook returns `decision: "block"`, the `additionalContext` strings produced by other hooks in the same run are now persisted and replayed on the next user prompt, instead of being silently discarded. Verified by `blocked_user_prompt_submit_persists_additional_context_for_next_turn` in the test suite.


### Bubblewrap startup warning routed through normal notification channel
Previously, when `/usr/bin/bwrap` was missing, the sandbox helper printed a warning directly. It now flows through `missing_system_bwrap_warning()` and is delivered as a `ConfigWarningNotification`, so embedders (TUI, IDE) actually see it.


### Memory citation parsing handles duplicate rollout IDs
`get_thread_id_from_citations()` (and the new `parse_memory_citation()`) now deduplicate rollout IDs across multiple citation blocks, preventing duplicate `ThreadId`s from leaking into the resolved citation list.


### Plugin install/uninstall protocol responses correctly surface remote errors
The new `Remote(_)` variants of `CorePluginInstallError` and `CorePluginUninstallError` are now mapped to specific `internal_error` responses (`"failed to enable remote plugin: …"`, `"failed to uninstall remote plugin: …"`) instead of being absorbed into the generic error path, so clients can distinguish a local install failure from a ChatGPT-side mutation failure.

### Experimental remote-skills API removed
The under-development `skills/remote/list` and `skills/remote/export` JSON-RPC methods have been removed, along with their schemas (`SkillsRemoteReadParams`, `SkillsRemoteReadResponse`, `SkillsRemoteWriteParams`, `SkillsRemoteWriteResponse`), the `RemoteSkillSummary` type, and the `ListRemoteSkillsResponse` / `RemoteSkillDownloaded` events. Clients that were polling these endpoints will need to be updated.


### `responses_websockets` and `responses_websockets_v2` features retired
Both feature flags have moved from `Stage::UnderDevelopment` to `Stage::Removed` and their gating logic has been deleted. They are no longer toggleable; the production behavior is now fixed.


### `GrantedMacOsPermissions` removed from permission profiles
The `macos` field has been dropped from `GrantedPermissionProfile`. Any client code reading `grantedProfile.macos` will need to be updated.


### `FunctionCallOutputPayload` schema export removed
The standalone TypeScript export `FunctionCallOutputPayload.ts` has been deleted from the schema artifacts. The shape is still defined inline where needed but is no longer a top-level exported type.


### `--remote` is incompatible with non-interactive subcommands
Passing `--remote` together with any of `apply`, `responses-api-proxy`, `stdio-to-uds`, or `features list/enable/disable` now fails fast with: `` `--remote <addr>` is only supported for interactive TUI commands, not `codex <subcommand>` ``.
