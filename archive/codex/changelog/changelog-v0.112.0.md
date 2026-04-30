# Changelog for version 0.112.0

## Highlights

Version 0.112.0 introduces the **GPT-5.4** model with refreshed migration guidance, an **explicit `@plugin` mention system** that lets users pull a plugin's skills, MCP servers, and connector apps into a single turn by name, and a substantially **stricter, typed sandbox permission model** that replaces the old loose boolean/string macOS permission shapes. The release also adds **SIGTERM-aware graceful shutdown**, refines the **JavaScript REPL** so failed cells no longer wipe out earlier bindings, and updates the **base instructions** that power Codex's pragmatic personality.

### GPT-5.4 Model Available

**What:** A new flagship model `gpt-5.4` is registered alongside the existing `gpt-5.3-codex`, `gpt-5.2-codex`, `gpt-5.1-codex-max`, and `gpt-5.1-codex` entries.

**Details:**
- `gpt-5.4` ships with a `display_name` of `gpt-5.4`, the description "Latest frontier agentic coding model.", `default_reasoning_level: medium`, support for low/medium/high/xhigh effort levels, `context_window: 272000`, parallel tool calls, image input, verbosity controls, and `apply_patch_tool_type: freeform`.
- The model is available across the `business`, `edu`, `education`, `enterprise`, `finserv`, `go`, `hc`, `plus`, `pro`, and `team` plans.
- A new `Introducing GPT-5.4` migration markdown is registered as the upgrade target for `gpt-5.3-codex`, `gpt-5.2-codex`, and `gpt-5.1-codex-max`. The previous `Codex just got an upgrade. Introducing {model_to}.` template that pointed at GPT-5.3 is replaced.
- The TUI model picker now surfaces `gpt-5.4` as the second option in the list (after the default `gpt-5.3-codex`).

**Code references:** new entries in `codex-rs/core/models.json` and `codex-rs/core/model_db.json`; snapshot in `codex_tui__chatwidget__tests__model_selection_popup.snap`.


### Explicit `@plugin` Mentions

**What:** Users can now type `@plugin display name` in chat to dynamically pull in a plugin's tools, MCP servers, and connector apps for that turn — without permanently enabling the plugin.

**Details:**
- A new parser, `collect_explicit_plugin_mentions()`, recognizes `@<plugin display name>` mentions in plain text. Matching is case-insensitive, prefers the longest plugin-name match at each position, and accepts identifiers consisting of alphanumerics plus `_`, `-`, and `:`. Mentions embedded inside emails or other tokens are ignored.
- For each matched plugin, the new `build_plugin_injections()` and `render_explicit_plugin_instructions()` helpers emit a `DeveloperInstructions` `ResponseItem` listing the plugin's skill prefix, its visible MCP servers, and the apps it enables.
- Mentioning `@plugin` automatically enables that plugin's apps as connectors **for the duration of the turn only** (tracked via a new `turn_enabled_connectors` set in `run_turn`). The user's persistent connector configuration is left untouched.
- Even when the Apps feature is otherwise off, an `@plugin` mention raises the underlying MCP/app inventory so the model can reach the plugin's tools.

**Example:**
```text
@DeployBot please push the latest staging build
```
Codex will, for that turn, inject `DeployBot`'s skill prefix and enabled apps into the developer instructions and route any of the plugin's tools through normally.

**Code references:** `collect_explicit_plugin_mentions()` in `codex-rs/core/src/mentions.rs`; `build_plugin_injections()` in `codex-rs/core/src/plugins/injection.rs`; `render_explicit_plugin_instructions()` in `codex-rs/core/src/plugins/render.rs`; `turn_enabled_connectors` in `codex-rs/core/src/codex.rs::run_turn`. New end-to-end test `explicit_plugin_mentions_inject_plugin_guidance` in `codex-rs/core/tests/suite/plugins.rs`.


### Plugin Provenance on Tools and Apps

**What:** Tools and apps now expose which plugins they belong to, so the model and downstream UIs can disambiguate similarly named tools.

**Details:**
- New `ToolPluginProvenance` struct, surfaced via `McpManager::tool_plugin_provenance()`, attaches plugin identity to each MCP tool.
- Tool descriptions are appended with `This tool is part of plugin \`xxx\`.` (single plugin) or `This tool is part of plugins \`a\`, \`b\`.` (multiple). The annotation is appended in `listed_tools` in `codex-rs/core/src/mcp_connection_manager.rs`.
- The wire-level `AppInfo` (and TypeScript `AppInfo` type) gains a new `pluginDisplayNames: Array<string>` field, propagated through every channel that emits app lists (`AppListUpdatedNotification`, `AppsListResponse`, ChatGPT connector responses).
- A new `search_tool_results_match_plugin_names_and_annotate_descriptions` test confirms BM25 tool search ranks results by plugin name and includes the provenance annotation.

**Code references:** `ToolPluginProvenance` in `codex-rs/core/src/mcp/mod.rs`; `tool_plugin_provenance()` and `listed_tools()` in `codex-rs/core/src/mcp_connection_manager.rs`; `plugin_display_names` field on `AppInfo` in `codex-rs/app-server-protocol/src/protocol/v2.rs`.


### Graceful Shutdown on SIGTERM

**What:** The app-server now treats `SIGTERM` the same as `Ctrl-C` (`SIGINT`) for graceful restart drains, so process supervisors and container orchestrators can request a clean shutdown.

**Details:**
- A new `shutdown_signal()` async helper waits on either `tokio::signal::ctrl_c()` or a new `SignalKind::terminate()` listener (Unix only; Windows continues to listen for Ctrl-C alone).
- The previously named `on_ctrl_c()` method on `ShutdownState` is renamed `on_signal()`, and the surrounding feature flag `graceful_ctrl_c_restart_enabled` is renamed `graceful_signal_restart_enabled`. Log lines have been retitled from "received Ctrl-C" / "Ctrl-C restart" to "received shutdown signal" / "shutdown signal restart" so they are accurate regardless of which signal arrived.
- A first signal enters the drain phase (still accepting requests until running assistant turns finish); a second signal forces an immediate exit. Two new integration tests, `websocket_transport_sigterm_waits_for_running_turn_before_exit` and `websocket_transport_second_sigterm_forces_exit_while_turn_running`, exercise the new path. The test helper `send_sigint` was generalized into `send_signal(process, signal)` with a thin `send_sigterm` wrapper.

**Code references:** `shutdown_signal()` and `ShutdownState::on_signal()` in `codex-rs/app-server/src/lib.rs`; new tests in `codex-rs/app-server/tests/suite/v2/connection_handling_websocket_unix.rs`.


### Trace IDs in Turn Context

**What:** Codex now captures the active OpenTelemetry trace ID for each turn and stores it on `TurnContext`, making it possible to correlate rollout entries with backend traces.

**Details:**
- A new `current_span_trace_id()` helper lives in `codex-rs/otel/src/trace_context.rs`.
- `TurnContext` (core) and `TurnContextItem` (protocol) gain an `Option<String> trace_id` field that is populated when a span is in scope and is persisted in rollout files.

**Code references:** `current_span_trace_id()` in `codex-rs/otel/src/trace_context.rs`; `trace_id` field on `TurnContext` in core and `TurnContextItem` in `codex-rs/protocol`.

### Stricter, Typed macOS Sandbox Permissions

The schema for macOS sandbox extensions has been overhauled to remove ambiguous "either-this-or-that" types in favor of clear sums.

- The old `MacOsPermissions` struct is renamed `MacOsSeatbeltProfileExtensions`, and its fields are renamed from `preferences`/`automations`/`accessibility`/`calendar` to `macos_preferences`/`macos_automation`/`macos_accessibility`/`macos_calendar`. All four fields are now **required** and **non-nullable**.
- `MacOsPreferencesValue` (formerly `boolean | string`) becomes a typed enum `MacOsPreferencesPermission` with three variants: `"none"`, `"read_only"`, `"read_write"`.
- `MacOsAutomationValue` (formerly `boolean | Array<string>`) becomes `MacOsAutomationPermission` with the variants `"none"`, `"all"`, or `{ "bundle_ids": [...] }`. A new `MacOsAutomationPermissionDe` deserializer accepts each form.
- `PermissionProfile.macos` is now `Option<MacOsSeatbeltProfileExtensions>`, and `is_empty()` simplifies to "all four sub-fields are None".
- The TypeScript bindings drop `MacOsPermissions.ts`, `MacOsAutomationValue.ts`, and `MacOsPreferencesValue.ts` and add `MacOsSeatbeltProfileExtensions.ts`, `MacOsAutomationPermission.ts`, and `MacOsPreferencesPermission.ts`.
- Skill YAML manifests and shell-tool `additional_permissions` blocks adopt the same renamed keys (`macos_preferences`, `macos_automation`, `macos_accessibility`, `macos_calendar`).

**Code references:** `MacOsSeatbeltProfileExtensions`, `MacOsPreferencesPermission`, `MacOsAutomationPermission` in `codex-rs/protocol/src/models.rs`; merge logic in new `codex-rs/core/src/sandboxing/macos_permissions.rs` (`merge_macos_seatbelt_profile_extensions`, `union_macos_preferences_permission`, `union_macos_automation_permission`).


### Network and macOS Permissions in `additional_permissions`

The `apply_patch` and shell tools' `with_additional_permissions` schema now lets a single tool call request both network and macOS escalations, not just file-system access.

- New `network.enabled` field declares whether the call needs network access.
- New `macos.preferences`, `macos.automations`, `macos.accessibility`, `macos.calendar` fields request the matching macOS extensions.
- The required-fields constraint has been relaxed: a request no longer has to include `file_system` if it only wants network or macOS extensions.
- Error messages and the model-facing prompt at `codex-rs/protocol/src/prompts/permissions/approval_policy/on_request_rule_request_permission.md` were updated to teach the model about the new shape.
- A new `EffectiveSandboxPermissions` struct merges the turn-level profile with skill- and request-level additions on macOS so the seatbelt policy reflects the union.

**Code references:** schema in `codex-rs/core/src/tools/spec.rs` and `codex-rs/core/src/tools/handlers/mod.rs`; `EffectiveSandboxPermissions` in `codex-rs/core/src/sandboxing/mod.rs`.


### Approval Overlay Surfaces macOS Permission Details

When a tool requests macOS extensions, the approval overlay now spells the request out in plain English — for example "macOS preferences readwrite", "macOS automation com.apple.X, com.apple.Y", "macOS accessibility", "macOS calendar" — instead of just hinting at booleans. A new snapshot, `approval_overlay_additional_permissions_macos_prompt.snap`, locks the layout in.

**Code references:** `codex-rs/tui/src/bottom_pane/approval_overlay.rs`.


### Refined Seatbelt UNIX Socket Policy

The macOS seatbelt profile drops the broad `(allow network* ...)` rule for UNIX sockets in favor of three narrower rules: `(allow system-socket (socket-domain AF_UNIX))`, `(allow network-bind (local unix-socket ...))`, and `(allow network-outbound (remote unix-socket ...))`. Tools that need to talk over UNIX sockets continue to work, but TCP/UDP traffic is no longer accidentally permitted.

**Code references:** `codex-rs/core/src/seatbelt.rs`.


### Linux Sandbox Adds `--unshare-user`

`codex-rs/linux-sandbox/src/bwrap.rs` now passes `--unshare-user` in addition to `--unshare-pid` when invoking `bwrap`. This fixes sandboxing inside containers where the process runs as root but does not hold ambient `CAP_SYS_ADMIN`, so it can still create the necessary namespaces. The sandbox README was updated accordingly.


### JavaScript REPL: Failed Cells Preserve Earlier Bindings

The `js_repl` kernel previously discarded all bindings created in a cell when any later statement threw, forcing users to redefine variables they had already initialized. The kernel now instruments JavaScript source so that each successfully-completed lexical binding is committed to the kernel's persistent scope before the failing statement executes, while skipping unreached hoisted `var`/function bindings.

- New helpers include `instrumentVariableDeclarationSource`, `instrumentLoopBody`, `collectFutureVarWriteReplacements`, `collectCommittedBindings`, and `collectHoistedVarDeclarationStarts`.
- Internal commit functions are namespaced with a thread-id-salted name (`__codex_internal_commit_<salt>_N`) accessed through `import.meta` so they can't collide with user code or be observed by `globalThis` enumeration.
- New tests cover the recovery path: `js_repl_failed_cells_*`, `js_repl_link_failures_keep_prior_module_state`, `js_repl_keeps_function_to_string_stable`, and `js_repl_allows_globalthis_shadowing_with_instrumented_bindings`.

**Code references:** `codex-rs/core/src/tools/js_repl/kernel.js`.


### `codex.emitImage` Restricted to Data URLs

`codex.emitImage` now rejects any URL whose scheme is not `data:` (case-insensitive), with a clear error: "codex.emitImage only accepts data URLs". Validation runs both inside the JS kernel and host-side via a new `validate_emitted_image_url()` helper. Multiple emissions per cell are still allowed — call `codex.emitImage` repeatedly to surface several images. The `js_repl` system prompt was rewritten to drop the obsolete `ImageDetailOriginal` feature gate, recommend JPEG quality ≈85 for photos vs. PNG for diagrams, and reassure the model that prior bindings usually survive cell errors.

**Code references:** `codex.emitImage` validation in `codex-rs/core/src/tools/js_repl/kernel.js`; `validate_emitted_image_url()` and updated guidance in `codex-rs/core/src/project_doc.rs`.


### Refreshed Base Instructions for `gpt-5.3-codex` and `gpt-5.4`

The base instructions for the GPT-5.3 and 5.4 Codex models were rewritten with several user-facing implications:

- A new opening reframes Codex as an "expert coding agent" whose primary focus is "writing code, answering questions, and helping the user complete their task in the current environment", with explicit guidance to build context by examining the codebase first.
- Editing is locked down: "Always use apply_patch for manual code edits. Do not use cat or any other commands when creating or editing files." Bulk/auto-generated changes are exempted.
- Model is told to never chain bash commands with separators like `echo "===="` because they render poorly in the user's terminal.
- The "Final answer instructions" were reorganized to emphasise short prose for simple tasks, banning lists for opinions/explanations and suggesting at most 2–4 high-level sections for larger tasks. New negative examples ban openers such as "You're right to call that out".
- Update cadence in the `commentary` channel relaxed from "every 20s" to "every 30s".
- The instruction template now exposes a `personality` placeholder with three personalities — `personality_default` (empty), `personality_friendly`, and `personality_pragmatic` — selectable via `instructions_variables`.

**Code references:** `base_instructions` and `model_messages` for `gpt-5.3-codex` and `gpt-5.4` in `codex-rs/core/models.json`.


### Default Reasoning Summary Made Per-Model

Each model now declares a `default_reasoning_summary`. `gpt-5.3-codex` and `gpt-5.4` default to `"none"`; `gpt-5.2-codex`, `gpt-5.1-codex-max`, and `gpt-5.1-codex` default to `"auto"`. Models also gain an `availability_nux: null` slot for future onboarding hints, and `supports_image_detail_original` / `supports_reasoning_summaries` were reordered for consistency across entries.

**Code references:** every model entry in `codex-rs/core/models.json` and `codex-rs/core/model_db.json`.


### Feedback Diagnostics Show Real Values, Connectivity Moves to Consent Popup

`codex-rs/feedback/src/feedback_diagnostics.rs` no longer scrubs proxy URLs through `sanitize_url_for_display`/`sanitize_proxy_value` or filters out the `DEFAULT_OPENAI_BASE_URL`. Proxy and `OPENAI_BASE_URL` values, including credentials, query strings, and any whitespace, are reported verbatim — so support staff see exactly what the user has configured. The `url` crate was dropped as a dependency (visible in `Cargo.lock`).

In the TUI, connectivity diagnostics are no longer prepended to the in-progress text area's `intro_lines`; they now appear in the **upload-consent popup** header instead. The helper `feedback_upload_consent_params` now takes `feedback_diagnostics: &FeedbackDiagnostics` directly rather than a boolean `include_connectivity_diagnostics_attachment`.


### `apply_patch` / Shell Tool Skill Escalation Refactor

The skill-permission compilation layer (`codex-rs/core/src/skills/permissions.rs`, ~454 lines, including `compile_permission_profile`) has been removed in favor of passing `PermissionProfile` directly into `EscalationPermissions::PermissionProfile`. Shell escalation goes through `CoreShellActionProvider::skill_escalation_execution` in `codex-rs/core/src/tools/runtimes/shell/unix_escalation.rs`, and `prepare_sandboxed_exec` was refactored to take a `PrepareSandboxedExecParams` struct, simplifying call sites.

**Code references:** `EscalationPermissions::PermissionProfile`, `CoreShellActionProvider::skill_escalation_execution`, and `PrepareSandboxedExecParams`.

### Restricted Network Policy Preserved When No Proxy Endpoints Are Reachable

When the dynamic network policy code path could not find a usable proxy endpoint (for example, a managed-network setup with all endpoints temporarily down), it previously returned an empty policy that effectively allowed everything through. It now preserves the restricted policy — failing closed — so users on managed networks don't silently leak traffic.

**Code references:** `dynamic_network_policy` path in the network policy module touched alongside `codex-rs/core/src/seatbelt.rs`.


### Plugins Manager Cache No Longer Polluted When Plugins Are Disabled

The plugins manager previously populated its internal cache even when the plugins feature was turned off, which could produce ghost entries on subsequent toggles. The cache is now skipped entirely while plugins are disabled.

**Code references:** `codex-rs/core/src/plugins/manager.rs`.


### Theme Picker Comment Typo

A trivial cleanup: the "pre-select" comment in the theme picker was fixed to "preselect".

**Code references:** `codex-rs/tui/src/theme_picker.rs`.
