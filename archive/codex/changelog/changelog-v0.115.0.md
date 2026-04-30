# Changelog for version 0.115.0

## Highlights

This is a substantial release centered on three big ideas. First, a brand-new **Guardian** subsystem lets a separate subagent automatically review approval requests with a risk score and rationale, rather than always interrupting you. Second, the app-server protocol grows a real **filesystem API** (read/write/copy/remove/getMetadata/readDirectory/createDirectory) and a **plugin/read** RPC, plus a redesigned **Code Mode** tool runtime. Third, the Linux sandbox **defaults to bubblewrap** (Landlock is now opt-in via `use_legacy_landlock`), and corporate users get **custom CA support** for TLS via `CODEX_CA_CERTIFICATE` / `SSL_CERT_FILE`.

### Guardian — automatic approval reviewer

**What:** A new approvals-review pipeline where a subagent assesses each escalation request (sandbox escape, blocked network, MCP elicitation, ARC) and produces a risk verdict, so simple requests can be auto-approved or auto-denied without human intervention.

**Details:**
- Enabled by setting the new `approvals_reviewer` config to `guardian_subagent` (default remains `user`). Gated behind the `guardian_approval` feature flag.
- Emits a new `GuardianAssessment` event carrying `id`, `turn_id`, `status` (`in_progress` / `approved` / `denied` / `aborted`), `risk_score` (0–100), `risk_level` (`low` / `medium` / `high`), and a free-text `rationale`.
- The TUI renders new history cells: `✔ Auto-reviewer approved codex to run …`, `⚠ Automatic approval review denied (risk: high): …`, and an aggregate `• Reviewing N approval requests` line.
- Surfaced over the app-server protocol via two new notifications: `item/autoApprovalReview/started` and `item/autoApprovalReview/completed`.

**Code references:**
- `codex-rs/protocol/src/approvals.rs` (`GuardianAssessmentEvent`, `GuardianRiskLevel`, `GuardianAssessmentStatus`)
- `codex-rs/core/src/guardian/{mod,approval_request,prompt,review,review_session}.rs` (replaces the old single-file `core/src/guardian.rs`)
- `codex-rs/core/src/guardian/policy.md` (policy doc bundled with binary)
- `codex-rs/protocol/src/config_types.rs` (`ApprovalsReviewer` enum)
- `codex-rs/tui/src/history_cell.rs` (`ApprovalDecisionActor::User|Guardian`, `new_guardian_denied_patch_request()`, `new_guardian_denied_action_request()`, `new_guardian_approved_action_request()`)
- `codex-rs/app-server-protocol/schema/json/v2/ItemGuardianApprovalReview{Started,Completed}Notification.json`


### Filesystem RPCs in the app-server protocol (v2)

**What:** The app-server now exposes a complete filesystem API to clients, so an embedding host (e.g. the IDE / TUI) can read, write, copy, remove, list, stat, and create directories without proxying through a shell tool.

**Details:**
- Seven new RPC methods: `fs/readFile`, `fs/writeFile`, `fs/copy`, `fs/remove`, `fs/createDirectory`, `fs/readDirectory`, `fs/getMetadata`.
- Each has its own `Params` and `Response` schema in `schema/json/v2/`.
- Used by the TUI's new `app_server_adapter` so the TUI now talks to the app-server instead of operating directly against `AuthManager`.

**Code references:**
- `codex-rs/app-server/src/fs_api.rs` (new module — implementation)
- `codex-rs/app-server-protocol/schema/json/v2/Fs{Copy,CreateDirectory,GetMetadata,ReadDirectory,ReadFile,Remove,WriteFile}{Params,Response}.json`
- Tests: `codex-rs/app-server/tests/suite/v2/fs.rs`


### Code Mode tool runtime

**What:** A redesigned tool subsystem where the model can write JavaScript that orchestrates other tools through a single shell, replacing the old single-file Code Mode handler.

**Details:**
- Splits Code Mode into `execute_handler` (kicks off the worker) and `wait_handler` (retrieves output later) — i.e. a deferred-output / async tool surface.
- Bundled assets `runner.cjs` and `bridge.js` are shipped under `core/src/tools/code_mode/` with companion `description.md` and `wait_description.md` markdown the model reads.
- Old files `core/src/tools/code_mode.rs`, `code_mode_bridge.js`, `code_mode_runner.cjs`, and `handlers/code_mode.rs` are removed in favor of this directory layout.

**Code references:**
- `codex-rs/core/src/tools/code_mode/{mod,execute_handler,wait_handler,worker,service,process,protocol}.rs`
- `codex-rs/core/src/tools/code_mode/{runner.cjs,bridge.js,description.md,wait_description.md}`


### `tool_search` and `tool_suggest` discovery tools

**What:** Two new built-in tools the model can call when many MCP tools are available — `tool_search` performs BM25-style ranking, and `tool_suggest` proposes candidates given a description.

**Details:**
- Replaces the previous internal `search_tool_bm25.rs` handler with a public, model-callable surface.
- Driven by a new `discoverable` registry (`tools/discoverable.rs`) and a `ModelInfo.supports_search_tool` flag so search is only injected when the model can use it.
- New `ResponseItem` variants `ToolSearchCall` / `ToolSearchOutput` flow over the protocol.
- Description templates live in `core/templates/search_tool/tool_suggest_description.md`.

**Code references:**
- `codex-rs/core/src/tools/handlers/tool_search.rs` (`ToolSearchHandler`)
- `codex-rs/core/src/tools/handlers/tool_suggest.rs` (`ToolSuggestHandler`)
- `codex-rs/core/src/tools/discoverable.rs`
- `codex-rs/protocol/src/openai_models.rs` (`ModelInfo.supports_search_tool`)
- `codex-rs/protocol/src/models.rs` (`ResponseItem::ToolSearchCall`, `ResponseItem::ToolSearchOutput`)


### Custom CA support for corporate / proxied environments

**What:** The HTTP client now respects two new environment variables for additional trust roots, so users behind corporate proxies and TLS-terminating firewalls can run Codex without disabling certificate validation.

**Details:**
- `CODEX_CA_CERTIFICATE` — Codex-specific cert bundle.
- `SSL_CERT_FILE` — standard OpenSSL-style override (also honored).
- Wired into the OAuth / device-code login server, the realtime websocket client, and (importantly) **voice transcription**, which previously created a vanilla `reqwest::Client` and ignored corporate CAs.

**Code references:**
- `codex-rs/codex-client/src/custom_ca.rs` (`CODEX_CA_CERT_ENV`, `SSL_CERT_FILE_ENV`, `build_reqwest_client_with_custom_ca()`, `maybe_build_rustls_client_config_with_custom_ca()`)
- `codex-rs/codex-client/src/bin/custom_ca_probe.rs` (diagnostic binary)
- `codex-rs/codex-client/tests/ca_env.rs`
- `codex-rs/login/src/server.rs` (token exchange / `obtain_api_key` use the custom-CA client)
- `codex-rs/tui/src/voice.rs` (`transcribe_bytes`)


### Plugin / app discovery RPC + plugin install policies

**What:** A new `plugin/read` RPC returns full plugin detail (apps, skills, install policy, auth policy) so clients can render plugin/app marketplaces without depending on private internals.

**Details:**
- Adds two enums: `PluginInstallPolicy` (`automatic` / `always_prompt`) and `PluginAuthPolicy` (`ON_INSTALL` / `ON_USE`).
- Backed by new server-side helpers `apps_list_helpers.rs` and `plugin_app_helpers.rs` and a plugin-toggle module.

**Code references:**
- `codex-rs/app-server-protocol/schema/json/v2/PluginRead{Params,Response}.json`
- `codex-rs/app-server/src/codex_message_processor/{apps_list_helpers,plugin_app_helpers}.rs`
- `codex-rs/core/src/plugins/toggles.rs`


### Multi-agent navigation, status, and spawn metadata

**What:** Several user-visible upgrades to the multi-agent TUI surface introduced in earlier releases.

**Details:**
- **Alt+Left / Alt+Right** now switch between agents (and Option+B / Option+F on macOS when the composer is empty).
- The footer shows the **active agent label** (e.g. `Robie [explorer]`), either alone or appended to the status line with ` · `.
- Agent spawn rows in history now show **model + reasoning effort** in magenta, e.g. `(gpt-5 high)`.
- A new **`Interrupted`** agent status renders in yellow, distinguishing "stopped mid-turn but resumable" from "completed" or "errored".
- `CollabAgentSpawnBegin/End` events carry `model` and `reasoning_effort` for IDE clients.

**Code references:**
- `codex-rs/tui/src/multi_agents.rs` (`previous_agent_shortcut()`, `next_agent_shortcut()`, `SpawnRequestSummary`, `spawn_request_spans()`, `status_summary_spans()`)
- `codex-rs/tui/src/app/agent_navigation.rs` (new module)
- `codex-rs/tui/src/bottom_pane/footer.rs` (`passive_footer_status_line`, `shows_passive_footer_line`)
- `codex-rs/exec/src/exec_events.rs` (`CollabAgentStatus::Interrupted`)
- `codex-rs/protocol/src/protocol.rs` (`AgentStatus::Interrupted`)
- Per-action multi-agent handlers split across `core/src/tools/handlers/multi_agents/{spawn,wait,send_input,resume_agent,close_agent}.rs`


### macOS permission expansion

**What:** Three additional macOS-specific permission scopes the user can grant or deny: Reminders, Contacts (with read-only / read-write granularity), and LaunchServices.

**Details:**
- Surfaces as new lines in the approval overlay ("macOS reminders", "macOS contacts readonly/readwrite", "macOS launch services").
- Backed by new fields on `MacOsSeatbeltProfileExtensions` and a `MacOsContactsPermission` enum (`none`, `read_only`, `read_write`).

**Code references:**
- `codex-rs/protocol/src/models.rs` (`MacOsSeatbeltProfileExtensions`, `MacOsContactsPermission`)
- `codex-rs/tui/src/bottom_pane/approval_overlay.rs` (`format_additional_permissions_rule()`, `RequestPermissionProfile`)


### App-link suggestion overlay (MCP elicitation)

**What:** The app-link bottom-pane view can now act as an MCP elicitation responder, prompting the user to install or enable an app and feeding the answer back into the in-flight elicitation.

**Details:**
- New fields: `suggest_reason`, `suggestion_type` (`Install` / `Enable`), `elicitation_target` (`AppLinkElicitationTarget`).
- Lets a tool call ask the user "you need app X to do this — install it?" without leaving the chat.

**Code references:**
- `codex-rs/tui/src/bottom_pane/app_link_view.rs`


### App enablement requirements (cloud / MDM)

**What:** Organizations can now ship a `requirements.toml` that explicitly disables specific Codex apps; a `false` value at any precedence layer wins.

**Details:**
- Pairs with the existing cloud-requirements layering (per-machine / per-org / global).
- Enables fleet-wide gating of features without rebuilding the binary.

**Code references:**
- `codex-rs/config/src/config_requirements.rs` (`AppRequirementToml`, `AppsRequirementsToml`, `merge_enablement_settings_descending()`)
- `codex-rs/config/src/lib.rs` (`CloudRequirementsLoadErrorCode` exported)


### Connectors crate + realtime websocket protocol versioning

**What:** A new top-level `connectors` crate factors out third-party connector logic, and the realtime websocket endpoint now ships v1 and v2 protocol variants side-by-side.

**Code references:**
- `codex-rs/connectors/{Cargo.toml,BUILD.bazel,src/lib.rs}`
- `codex-rs/codex-api/src/endpoint/realtime_websocket/{protocol_common,protocol_v1,protocol_v2}.rs`


### Custom-CA OAuth probe binary

**What:** A standalone diagnostic tool (`custom_ca_probe`) for verifying a corporate cert bundle resolves the right login endpoints.

**Code references:**
- `codex-rs/codex-client/src/bin/custom_ca_probe.rs`


### `codex.turn.network_proxy` telemetry metric

**What:** A new OTEL counter records when a turn used the network proxy, so deployments can quantify fallback / mediated traffic.

**Code references:**
- `codex-rs/otel/src/metrics/names.rs` (`TURN_NETWORK_PROXY_METRIC`)
- `codex-rs/otel/src/trace_context.rs` (`span_w3c_trace_context()` helper for W3C trace propagation)


### Skill sample: OpenAI docs / skill-creator

**What:** Two new sample skills ship inside the binary: an OpenAI-docs skill (with prompting and upgrade-guide references) and a `skill-creator` boilerplate.

**Code references:**
- `codex-rs/skills/src/assets/samples/openai-docs/{LICENSE.txt, agents/openai.yaml, …}`
- `codex-rs/skills/src/assets/samples/skill-creator/scripts/init_skill.py`

### Linux sandbox: bubblewrap is now the default

The Linux sandbox now defaults to **bubblewrap**, with Landlock available as legacy opt-in via the new `use_legacy_landlock` config (the previous `use_linux_sandbox_bwrap` flag is still accepted as an alias for backward compatibility). The `codex sandbox linux` and `codex landlock` help text is updated accordingly. Practical effect: most users will get a stricter, more portable sandbox out of the box.

- `codex-rs/cli/src/main.rs`, `codex-rs/cli/src/lib.rs`, `codex-rs/cli/src/debug_sandbox.rs`
- `codex-rs/utils/cli/src/config_override.rs` (`canonicalize_override_key()` — handles the legacy alias)


### `/clean` slash command renamed to `/stop`

The TUI command for stopping all background terminals is now `/stop` (description: "stop all background terminals"). `/clean` continues to work as an alias. This frees up `/clean` for future use and reads better as an action verb.

- `codex-rs/tui/src/slash_command.rs` (`SlashCommand::Stop`)
- `codex-rs/tui/src/bottom_pane/slash_commands.rs`


### `/multi-agents` accepts `/subagents` as an alias

The `/multi-agents` command can now also be typed as `/subagents`, matching the terminology many users already prefer.

- `codex-rs/tui/src/slash_command.rs` (`SlashCommand::MultiAgents` with `#[strum(serialize = "subagents")]`)


### MCP login auto-retries without scopes

When `codex mcp add` or `codex mcp login` initiates an OAuth flow and the provider rejects the discovered scopes, the CLI now prints `OAuth provider rejected discovered scopes. Retrying without scopes…` and retries once more. This removes a common dead-end where servers advertised scopes they didn't actually accept.

- `codex-rs/cli/src/mcp_cmd.rs` (`perform_oauth_login_retry_without_scopes()`, `discover_supported_scopes()`, `resolve_oauth_scopes()`)


### `Reject` approval mode renamed to `Granular` with inverted semantics

The `AskForApproval::Reject` variant is now `AskForApproval::Granular`. Its fields are now **allow-flags** rather than reject-flags — `allows_sandbox_approval`, `allows_rules_approval`, `allows_mcp_elicitations` — which reads more naturally as "what's permitted" instead of "what's blocked". `RejectConfig` becomes `GranularApprovalConfig`. A new `skill_approval` field controls whether skill-script execution prompts the user.

- `codex-rs/protocol/src/protocol.rs` (`GranularApprovalConfig`)


### `Op::Interrupt` no longer terminates background terminals

Interrupt is now a focused signal — it no longer collaterally tears down background terminals. A new dedicated `Op::CleanBackgroundTerminals` handles that case, which is what `/stop` invokes. There's also a new `Op::kind()` helper for telemetry / dispatch, and the snapshot file rename `interrupt_clears_unified_exec_wait_streak.snap` → `interrupt_preserves_unified_exec_wait_streak.snap` reflects the new behavior: interrupting does not clear the unified-exec wait streak.

- `codex-rs/protocol/src/protocol.rs` (`Op::Interrupt`, `Op::CleanBackgroundTerminals`, `Op::kind()`)
- `codex-rs/tui/src/chatwidget/snapshots/`


### Markdown links resolve relative to session cwd

When the model emits a relative file link like `[note](src/foo.rs)`, the TUI now resolves it against the session's working directory. `append_markdown` takes an optional `cwd` argument so streamed and non-streamed output produce identical paths.

- `codex-rs/tui/src/markdown.rs` (`append_markdown()`)


### TUI starts an embedded app-server in-process

The TUI now boots an embedded app-server (`InProcessAppServerClient`) and talks to core through it, rather than operating against `AuthManager` directly. This unifies the TUI and external-client code paths and is what enables the new `app_server_adapter` and `agent_navigation` modules.

- `codex-rs/tui/src/lib.rs` (`start_embedded_app_server()`, `run_main(LoaderOverrides, …)`)
- `codex-rs/tui/src/app/app_server_adapter.rs` (new)


### `default_exec_approval_requirement` keys off filesystem policy

Approval is no longer required just because sandboxing isn't `DangerFullAccess` — it's required when the **filesystem** is `Restricted`. This removes a class of false-positive prompts in network-sandboxed setups that nonetheless have full filesystem access.

- `codex-rs/core/src/tools/sandboxing.rs`


### `request_permissions` tool uses a dedicated profile

The `request_permissions` tool now operates on a `RequestPermissionProfile` (network + filesystem only, no macOS-specific scopes). This separates the runtime permission-request surface from the broader profile system.

- `codex-rs/protocol/src/request_permissions.rs`


### Filesystem permission resolution is now order-aware

`FileSystemAccessMode` implements `Ord` so equally-specific entries resolve by priority (`none > write > read`). New helpers (`resolve_access_with_cwd()`, `can_read_path_with_cwd()`, `can_write_path_with_cwd()`, `needs_direct_runtime_enforcement()`) make permission lookups cwd-aware. The old `has_explicit_deny_entries()` is replaced by `has_write_narrowing_entries()` to better describe what it actually computes.

- `codex-rs/protocol/src/permissions.rs`


### Dynamic tools support deferred loading

`DynamicToolSpec` gains a `defer_loading` field (replacing the legacy `expose_to_context`). It is persisted in the SQLite thread store via a new migration, so re-attaching to a thread restores the original deferred-loading state.

- `codex-rs/protocol/src/dynamic_tools.rs`
- `codex-rs/state/migrations/0019_thread_dynamic_tools_defer_loading.sql`


### Stop-hook contract is clearer

The Stop hook output now uses `continuation_prompt` instead of `block_message_for_model`, and adds an `invalid_block_reason` failure path so misuse is reported back instead of silently failing.

- `codex-rs/hooks/src/events/stop.rs` (`StopOutcome`)
- `codex-rs/hooks/schema/generated/stop.command.output.schema.json`


### `unified_exec` process IDs are now integers

Process IDs in unified_exec are typed as `i32` instead of `String` end-to-end, matching OS semantics and removing parse-back gymnastics. There's also a new `ZshForkConfig` + `zsh_fork_backend` that escalates sandboxed shells via socket-FD inheritance.

- `codex-rs/core/src/unified_exec/{mod,async_watcher,process_manager}.rs`
- `codex-rs/core/src/tools/runtimes/shell/zsh_fork_backend.rs`
- `codex-rs/core/src/tools/spec.rs` (`ZshForkConfig`)


### Thread start / fork / resume now carry `approvals_reviewer` and `config`

`ThreadStartParams`, `ThreadForkParams`, and `ThreadResumeParams` propagate the active approvals reviewer and config-overrides set, so resuming or forking a thread doesn't drop the user's review-mode preference or model overrides.

- `codex-rs/exec/src/lib.rs` (`thread_start_params_from_config()`, `approvals_reviewer_override_from_config()`, `config_request_overrides_from_config()`)


### Function calls and MCP results carry namespacing / structured shape

`FunctionCall` gains a `namespace` field, and MCP tool output is delivered as `CallToolResult` instead of the looser `McpToolOutput`. This lets clients route by namespace and parse structured tool results without ad-hoc decoding.

- `codex-rs/protocol/src/models.rs`


### Prompt assembly carries explicit instruction tags

The system prompt now wraps tool/skill/plugin instructions in named tag blocks (`<apps_instructions>`, `<skills_instructions>`, `<plugins_instructions>`) so the model can disambiguate the source of guidance.

- `codex-rs/protocol/src/protocol.rs`


### Tooltip copy update

The "free" tooltip now reads "For a limited time, Codex is included in your plan for free" instead of the old "Free through March 2nd" line.

- `codex-rs/tui/src/tooltips.rs` (`FREE_GO_TOOLTIP`)

### Voice transcription respects custom CAs

Previously, the voice-input transcription path constructed a fresh `reqwest::Client::new()` and bypassed any configured custom-CA bundle. Users behind corporate TLS-terminating proxies would see voice transcription fail while every other network call worked. The transcription HTTP client now goes through the same `build_reqwest_client_with_custom_ca()` factory as the rest of the binary.

- `codex-rs/tui/src/voice.rs` (`transcribe_bytes()`)


### Interrupt preserves the unified-exec wait streak

The unified-exec "wait streak" (consecutive wait calls without progress, used for backoff / livelock detection) was being inadvertently reset on `Op::Interrupt`. It is now preserved across interrupts so the streak counter reflects actual process behavior. (See the snapshot rename `interrupt_clears_unified_exec_wait_streak.snap` → `interrupt_preserves_unified_exec_wait_streak.snap`.)

- `codex-rs/tui/src/chatwidget/snapshots/`
- Related: `codex-rs/protocol/src/protocol.rs` (`Op::Interrupt`, `Op::CleanBackgroundTerminals`)


### MCP OAuth login no longer dies on rejected scopes

If the OAuth provider rejects the scopes Codex discovered from its metadata, login now retries once without scopes instead of returning an error. Previously, mis-advertised scopes were a hard failure for `codex mcp add` / `codex mcp login`.

- `codex-rs/cli/src/mcp_cmd.rs` (`perform_oauth_login_retry_without_scopes()`)
