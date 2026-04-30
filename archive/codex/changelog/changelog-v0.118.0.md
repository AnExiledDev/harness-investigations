# Changelog for version 0.118.0

## Highlights

This release is dominated by a structural reorganization: the long-lived `tui_app_server` and `package-manager` crates are gone, and a brand-new `codex-tools` crate now houses every tool builder (shell, agents, MCP, code-mode, view-image, etc.) that core used to own. On the user-visible side, `codex exec` learned to combine a prompt argument with piped stdin into a tagged `<stdin>` block, ChatGPT login gained a device-code flow, and custom model providers can now produce bearer tokens by running an external command. Several features were retired in this release — voice/spacebar-hold-to-talk, user-prompt (`/prompts:*`) slash commands, per-skill permission overrides, and macOS-specific seatbelt extensions — so users relying on those should plan accordingly.

### `codex exec` accepts a prompt argument *and* piped stdin together
**What:** Previously you had to choose: pass a prompt as an argument, or pipe it on stdin. Now you can do both — Codex appends the piped stdin to the prompt as a `<stdin>` block.

**Details:**
- Introduces `StdinPromptBehavior::{RequiredIfPiped, Forced, OptionalAppend}` to model the three modes.
- When both are provided, the constructed prompt is `prompt\n\n<stdin>\n…stdin contents…\n</stdin>`.
- Bare `codex exec` (no prompt argument) and `codex exec -` retain the prior "stdin *is* the prompt" behavior.
- A new stderr message — "Reading additional input from stdin..." — signals when stdin is being consumed.

**Example:**
```sh
echo "this is the file output" | codex exec "Summarize this concisely"
# Codex sees:
# Summarize this concisely
# # <stdin>
# this is the file output
# </stdin>
```

**Code references:** `read_prompt_from_stdin()`, `prompt_with_stdin_context()`, `resolve_root_prompt()` in `codex-rs/exec/src/lib.rs`; updated docs in `codex-rs/exec/src/cli.rs` and `codex-rs/README.md`. Tests added at `codex-rs/exec/tests/suite/prompt_stdin.rs`.


### Device-code login flow for ChatGPT
**What:** A new login path for environments where the browser-based redirect flow is awkward (remote sessions, headless boxes). The server returns a short user code and a verification URL; the user opens the URL on any device and enters the code.

**Details:**
- New `chatgptDeviceCode` variant on both `LoginAccountParams` and `LoginAccountResponse` (v1 and v2 of the app-server protocol).
- The response carries `loginId`, `verificationUrl`, and `userCode`.
- The verification page lives at `auth.openai.com/codex/device`.
- Device-code can be requested in tests via the new `--device-code` flag on `app-server-test-client`'s `TestLogin` subcommand.

**Code references:** new variant in `LoginAccountParams`/`LoginAccountResponse` in `codex-rs/app-server-protocol/src/protocol/v2.rs`; handler additions in `codex-rs/app-server/`; documented in `codex-rs/app-server/README.md`. Backing tests in `codex-rs/login/tests/suite/device_code_login.rs`.


### External bearer auth for custom model providers
**What:** Custom providers configured in `~/.codex/config.toml` can now obtain access tokens by invoking a user-supplied command at runtime, instead of requiring a token to be hard-coded in config.

**Details:**
- New `ModelProviderAuthInfo` config section: `command`, `args`, `cwd`, `refresh_interval_ms` (default `300000`), `timeout_ms` (default `5000`).
- Codex re-runs the command on cache expiry and on 401 (`UnauthorizedRecovery`).
- New `AuthManager::external_bearer_only(config)` constructor and an `external_auth: RwLock<Option<ExternalAuth>>` field that holds either a `Bearer(...)` or `ChatgptRefresher(...)` variant.
- `ExternalAuthTokens` was restructured: ChatGPT-specific fields (`account_id`, `plan_type`) moved into a nested `ExternalAuthChatgptMetadata`; new constructors `ExternalAuthTokens::access_token_only(...)` and `ExternalAuthTokens::chatgpt(...)`.

**Example config:**
```toml
[model_providers.my-provider]
name = "My Provider"
base_url = "https://api.example.com/v1"

[model_providers.my-provider.auth]
command = "/usr/local/bin/get-token.sh"
args = ["--audience", "my-provider"]
refresh_interval_ms = 600000
```

**Code references:** new file `codex-rs/login/src/auth/external_bearer.rs` (`ExternalBearerAuth`); new `ModelProviderAuthInfo` definition in `codex-rs/core/config.schema.json`; rename of `set_external_auth_refresher` → `set_external_chatgpt_auth_refresher` and friends in `codex-rs/login/src/manager.rs`.


### `codex-tools` crate (extracted reusable tool primitives)
**What:** A new top-level crate that holds every tool definition Codex exposes to the model. Previously these lived inline in `codex-core`. The split makes it easier for downstream crates (cloud-tasks, MCP server, etc.) to depend on tool definitions without pulling in the entire core.

**Details — what's now in `codex-rs/tools/`:**
- `json_schema.rs` — `JsonSchema`, `parse_tool_input_schema`
- `tool_definition.rs`, `tool_spec.rs` — `ToolDefinition`, `ToolSpec`, `ConfiguredToolSpec`, `create_tools_json_for_responses_api`
- `responses_api.rs` — `ResponsesApiTool`, `FreeformTool[Format]`, `ToolSearchOutputTool`, namespace types
- `agent_tool.rs`, `agent_job_tool.rs` — `spawn`/`send`/`wait`/`close`/`list`/`resume` agent tool builders, plus CSV-driven `create_spawn_agents_on_csv_tool`
- `code_mode.rs` — `create_code_mode_tool`, `create_wait_tool`, `augment_tool_spec_for_code_mode`
- `dynamic_tool.rs`, `js_repl_tool.rs` — `parse_dynamic_tool`, `create_js_repl_tool`, `create_js_repl_reset_tool`
- `local_tool.rs` — `create_shell_tool`, `create_shell_command_tool`, `create_exec_command_tool`, `create_write_stdin_tool`, `create_request_permissions_tool`, `ShellToolOptions`, `CommandToolOptions`
- `mcp_resource_tool.rs`, `mcp_tool.rs` — list/read MCP resources, `parse_mcp_tool`, `mcp_call_tool_result_output_schema`
- `request_user_input_tool.rs`, `tool_discovery.rs`, `utility_tool.rs`, `view_image.rs`

**Code references:** new crate at `codex-rs/tools/src/*.rs`; workspace member added in `codex-rs/Cargo.toml`. `codex-core`, `codex-app-server`, and `codex-cloud-tasks` now depend on `codex-tools`.


### `codex app-server` startup banner over WebSockets
**What:** Running `codex app-server` with WebSocket transport now prints a friendly banner showing where to connect.

**Details:** The banner identifies the transport as `codex app-server (WebSockets)` and lists `listening on:`, `readyz:`, and `healthz:` URLs, plus a localhost-binding note or a `--ws-auth` warning when the auth token is missing. Origin-header requests are explicitly rejected.

**Code references:** new transport modules `codex-rs/app-server/src/transport/{stdio,websocket,auth,mod}.rs`.


### Two new ChatGPT plan types
**What:** Codex now recognizes `self_serve_business_usage_based` and `enterprise_cbp_usage_based` plan types, which receive business-tier cloud-requirements treatment.

**Code references:** `KnownPlan::SelfServeBusinessUsageBased`, `KnownPlan::EnterpriseCbpUsageBased` in `codex-rs/codex-backend-openapi-models/src/models/rate_limit_status_payload.rs`; mapped through `Client::map_plan_type` in `codex-rs/backend-client/src/client.rs`; surfaced in `codex-rs/cloud-requirements/src/lib.rs` and the `PlanType` TypeScript export.


### Login error pages use the Template engine
**What:** The browser-served login error page (`assets/error.html`) is now rendered through `codex_utils_template::Template` instead of `String::replace`, with proper HTML escaping. A new "missing_codex_entitlement" copy displays "You do not have access to Codex / Contact your workspace administrator" when a user without entitlement tries to log in.

**Code references:** `codex-rs/login/src/server.rs`; `codex-utils-template` added as a dependency in `codex-rs/login/Cargo.toml`.

### Network permissions config: structured maps replace flat lists
**What:** The TOML schema for declaring network policy in `config.toml` and skill metadata moved from three flat string lists to two structured permission maps with explicit verdicts.

**Before:**
```toml
[permissions.network]
allowed_domains = ["example.com", "*.openai.com"]
denied_domains = ["evil.com"]
allow_unix_sockets = ["/var/run/docker.sock"]
```

**After:**
```toml
[permissions.workspace.network.domains]
"example.com" = "allow"
"*.openai.com" = "allow"
"evil.com" = "deny"

[permissions.workspace.network.unix_sockets]
"/var/run/docker.sock" = "allow"
```

**Details:**
- New types `NetworkDomainPermission` (`Allow`/`Deny`/`None`) and `NetworkUnixSocketPermission` (`Allow`/`None`) with deny-wins ordering.
- `NetworkRequirements` (v2 protocol) gains `domains`, `unix_sockets`, and `managed_allowed_domains_only` fields. The legacy `allowed_domains`/`denied_domains`/`allow_unix_sockets` keys remain as a "Legacy compatibility view" but are no longer the canonical form.
- Global `*` wildcard rejected during allowlist compilation unless explicitly enabled.

**Code references:** `codex-rs/core/src/config/permissions.rs`; `codex-rs/network-proxy/src/config.rs`; updated `codex-rs/core/config.schema.json` and `codex-rs/app-server-protocol/schema/json/v2/ConfigRequirementsReadResponse.json`.


### Bubblewrap discovery searches `PATH`
**What:** The Linux sandbox no longer hard-codes `/usr/bin/bwrap`. It now walks `PATH` (excluding the current working directory for safety) and emits a clearer warning if `bwrap` isn't found.

**Code references:** new `find_system_bwrap_in_path()` and `system_bwrap_warning()` in `codex-rs/sandboxing/src/bwrap.rs`; updated `codex-rs/linux-sandbox/README.md`.


### PowerShell parser uses a long-lived process pool (Windows perf)
**What:** On Windows, command-safety analysis previously spawned a fresh PowerShell process per parse. v0.118.0 keeps a per-executable child alive and talks to it over a JSON line protocol on stdin/stdout, amortizing PowerShell startup across many invocations. The script `powershell_parser.ps1` was rewritten as a long-running loop.

**Code references:** new `codex-rs/shell-command/src/command_safety/powershell_parser.rs`; `parse_with_powershell_ast()`, `PowershellParseOutcome`. The previous inline parser in `windows_safe_commands.rs` was removed.


### `code-mode` exec tool description clarified
**What:** The instructions shown to the model when it has access to the JS-orchestration tool now lead with the purpose ("Run JavaScript code to orchestrate/compose tool calls"), explicitly document that the `tools` global object exposes nested tools as normalized JS identifiers (e.g. `tools.mcp__ologs__get_profile(...)`), notes that nested tools accept either string or object input, and warns that unawaited promises are silently discarded when the isolate ends.

**Code references:** `EXEC_DESCRIPTION_TEMPLATE` in `codex-rs/code-mode/src/description.rs`.


### `codex-chatgpt` aligns on `codex-login` for token data
**What:** The `chatgpt` crate now imports `TokenData` from `codex_login::token_data` instead of `codex_core::token_data`, removing a layering dependency on the heavier `codex-core` crate.

**Code references:** `codex-rs/chatgpt/Cargo.toml` (added `codex-login` dep), `codex-rs/chatgpt/src/chatgpt_token.rs`, `codex-rs/chatgpt/src/connectors.rs`.


### Workspace-aware connector listing
**What:** When listing connectors for a workspace ChatGPT account, Codex now hits the `/connectors/directory/list_workspace` endpoint instead of the generic listing, returning the workspace's curated connector set.

**Code references:** `is_workspace_account: bool` plumbed through `list_all_connectors_with_options` in `codex-rs/chatgpt/src/connectors.rs`; `KnownPlan::is_workspace_account()` helper.


### `KnownPlan` is now `Copy` and exposes display helpers
**What:** Plan-type enum gains `display_name()`, `raw_value()`, `is_workspace_account()`, and is now `Copy`, simplifying call sites that previously had to clone or pattern-match.

**Code references:** `codex-rs/codex-backend-openapi-models/src/models/rate_limit_status_payload.rs`; new `IdTokenInfo::get_chatgpt_plan_type_raw()`.


### `--remote` TUI no longer routes through a feature flag
**What:** The `--remote <url>` flag on the interactive TUI used to be gated behind the `tui_app_server` feature/binary; it's now a first-class option on `codex_tui::run_main`, removing the `into_app_server_tui_cli`/`into_legacy_*` shims.

**Code references:** `run_interactive_tui()` in `codex-rs/cli/src/main.rs`; `normalize_remote_addr`, `validate_remote_auth_token_transport`, `start_embedded_app_server`, `AppServerTarget` re-exported from `codex_tui` (`codex-rs/tui/src/lib.rs`).


### Sandbox arguments preserve non-UTF-8 bytes
**What:** `SandboxCommand::program` is now an `OsString` (was `String`), and new `os_argv_to_strings` / `os_string_to_command_component` helpers are used when building sandbox commands. Filenames containing non-UTF-8 bytes — common on older Linux filesystems — are no longer corrupted on the way into the sandbox.

**Code references:** `codex-rs/sandboxing/src/manager.rs`.

### Login error page no longer breaks on special characters in messages
**Before:** Error messages embedded into the HTML template via `String::replace` could break the page if they contained `<`, `>`, or quotes.

**After:** The template engine HTML-escapes substituted values; new tests in `codex-rs/login/src/server.rs` cover this and the `missing_codex_entitlement` copy.


### Connector listing for workspace accounts
**Before:** Workspace ChatGPT accounts saw the same generic connector list as personal accounts.

**After:** Workspace accounts now retrieve their workspace-curated list via `/connectors/directory/list_workspace`.

**Code references:** `list_all_connectors_with_options` in `codex-rs/chatgpt/src/connectors.rs`.

### Voice transcription / spacebar hold-to-talk
**What:** The "hold space to dictate a message" voice-input feature has been entirely removed from the TUI.

**Details:**
- Removed: `VoiceState`, `set_voice_transcription_enabled`, `voice_transcription_enabled`, `space_hold_started_at`, `space_hold_element_id`, `space_hold_trigger`, `space_hold_repeat_seen`, `handle_voice_space_key_event`, `handle_key_event_while_recording`, `stop_all_transcription_spinners`, `spinner_stop_flags`.
- The `voice_transcription` boolean key is gone from `config.schema.json` (top-level and feature-toggles).
- Stub types `RecordedAudio`, `RealtimeInputBehavior`, `transcribe_async`, `VoiceCapture::start`/`stop`/`data_arc`/`sample_rate`/`channels` were also removed from the no-build-feature stub.

**Code references:** `codex-rs/tui/src/bottom_pane/chat_composer.rs`; `codex-rs/tui/src/lib.rs`; `codex-rs/core/config.schema.json`.


### Custom user-prompt slash commands (`/prompts:<name>`)
**What:** The ability to define custom prompt expansions in user config and invoke them as `/prompts:<name>` (with positional or numeric argument substitution) is no longer available.

**Details:**
- Removed: `CommandItem::UserPrompt`, `CommandPopup::set_prompts`, `prompt`, the `custom_prompts: Vec<CustomPrompt>` field, and the helpers `expand_custom_prompt`, `expand_if_numeric_with_positional_args`, `prompt_argument_names`, `prompt_command_with_arg_placeholders`, `prompt_has_numeric_placeholders`, `PromptSelectionMode`, `PromptSelectionAction`.
- The MCP server no longer surfaces `EventMsg::ListCustomPromptsResponse`.

**Code references:** `codex-rs/tui/src/bottom_pane/command_popup.rs`, `codex-rs/tui/src/bottom_pane/chat_composer.rs`, `codex-rs/mcp-server/src/codex_tool_runner.rs`.


### Per-skill permission overrides
**What:** Skills (under `core-skills/`) can no longer declare `permissions:`, `permission_profile`, or `managed_network_override` blocks in their TOML to override network/filesystem/macOS sandbox permissions.

**Details:** Removed types `SkillManagedNetworkOverride`, `SkillPermissionProfile`, `SkillNetworkPermissions`, `SkillMetadata::permission_profile`, `SkillMetadata::managed_network_override`, plus the `normalize_permissions()` helper. Skills now run under whatever permissions the surrounding session grants.

**Code references:** `codex-rs/core-skills/src/loader.rs`, `codex-rs/core-skills/src/model.rs`.


### macOS-specific permission profiles
**What:** Approval overlays and configuration no longer carry separate macOS-specific permission profiles (Automation, Contacts, Preferences, Accessibility, Calendar, Reminders).

**Details:**
- TypeScript types `MacOsAutomationPermission`, `MacOsContactsPermission`, `MacOsPreferencesPermission`, `AdditionalMacOsPermissions` deleted.
- `AdditionalPermissionProfile.macos` field removed (now just `network` and `fileSystem`).
- `permissions.macos_seatbelt_profile_extensions` removed from `Permissions` in `codex-rs/core/src/config/mod.rs`.
- `merge_macos_seatbelt_profile_extensions` helper and `create_seatbelt_command_args_for_policies_with_extensions` removed; replaced by `create_seatbelt_command_args_for_policies`.
- `format_additional_permissions_rule` (approval overlay) no longer prints these macOS rows.

**Code references:** `codex-rs/sandboxing/src/macos_permissions.rs` and `seatbelt_permissions.rs` deleted; `codex-rs/tui/src/bottom_pane/approval_overlay.rs`.


### `CommandExecutionRequestApprovalSkillMetadata`
**What:** The `skill_metadata` field on command-execution approval requests is gone; approvals no longer carry information about which skill triggered them.

**Code references:** removed TS type at `codex-rs/app-server-protocol/schema/typescript/v2/CommandExecutionRequestApprovalSkillMetadata.ts`; field removed from `CommandExecutionRequestApprovalParams` in `v2.rs`.


### `codex-package-manager` and `codex-tui-app-server` crates
**What:** Both workspace crates are deleted entirely.

**Details:**
- `codex-package-manager` (and its types `PackageManager`, `PackageManagerConfig`, `PackageManagerError`, `ManagedPackage`, `PackageReleaseArchive`, `PackagePlatform`) is removed with no replacement crate in this diff. Workspace deps `fd-lock`, `flate2`, and `tar` go with it.
- `codex-tui-app-server` is folded back into `codex-rs/app-server/` and `codex-rs/tui/`. New transport modules under `codex-rs/app-server/src/transport/` (`stdio.rs`, `websocket.rs`, `auth.rs`, `mod.rs`) absorb its responsibilities, plus new `bespoke_event_handling.rs`, `codex_message_processor/plugin_app_helpers.rs`, `config_api.rs`, `filters.rs`, `in_process.rs`, `thread_status.rs`, `outgoing_message.rs`, and a sizable v2 test suite.

**Code references:** `codex-rs/Cargo.toml` (members list); deletions throughout `codex-rs/package-manager/` and `codex-rs/tui_app_server/`.


### `/debug-m-drop` and `/debug-m-update` reduced to stubs
**What:** The two memory-maintenance debug slash commands no longer issue `Op::DropMemories` / `Op::UpdateMemories` — they now emit a stub message ("Memory maintenance") instead. Useful to know if you have automation that depended on these.

**Code references:** `SlashCommand::MemoryDrop` / `SlashCommand::MemoryUpdate` in `codex-rs/tui/src/chatwidget.rs` (now call `self.add_app_server_stub_message("Memory maintenance")`).
