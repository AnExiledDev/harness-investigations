# Changelog for version 0.110.0

## Highlights

This release introduces three substantial new building blocks: a **Plugins** system that bundles MCP servers, skills, and app connectors into installable units; a native **Artifacts** tool for generating PowerPoint and spreadsheet files via a managed JS runtime; and a redesigned **Realtime voice/websocket** stack with handoff back to the typed-text agent. It also adds a new **Fast / Flex service tier** with a `/fast` slash command, **cross-thread approvals** in the multi-agent UI, **pending steers** during running turns, **fail-closed cloud requirements** for ChatGPT Business/Enterprise workspaces, and renames several user-visible memory configuration keys.

### Plugins system (under-development feature flag: `plugins`)

**What:** Codex now supports installing and enabling **plugins** — directories that bundle skills, MCP servers, and app-connector ids into a single unit, sourced from a marketplace file.

**Details:**
- A plugin is a directory containing a `.codex-plugin/plugin.json` manifest plus optional `skills/` (SKILL.md files), `.mcp.json` (bundled MCP servers), and `.app.json` (declared app-connector ids).
- A "marketplace" is a `marketplace.json` that lives at `.agents/plugins/marketplace.json` in your repo or `~/.agents/plugins/marketplace.json` in your home — repo entries take precedence.
- Install via the new V2 protocol method `plugin/install` with `{ pluginName, marketplaceName, cwd? }`. Installation copies the plugin into `<codex_home>/plugins/cache/<marketplace>/<plugin>/local/` and writes `plugins."<plugin>@<marketplace>" = { enabled = true }` into `config.toml`.
- When enabled, a plugin's skills, MCP servers, and connectors are folded into the active session. Plugin MCP `cwd` paths are resolved relative to the plugin root; the OAuth `callbackPort` is intentionally ignored (the global setting wins).
- The `mcp.add_mcp_output` empty-state check now uses `McpManager::effective_servers`, so plugin-provided servers count too.

**Configuration:**
```toml
plugins."my-plugin@my-marketplace" = { enabled = true }
```

**Code references:** `PluginsManager::install_plugin()`, `plugins_for_config()`, `effective_skill_roots()`, `effective_mcp_servers()`, `effective_apps()` in `core/src/plugins/manager.rs`; `load_plugin_manifest()` in `core/src/plugins/manifest.rs`; `resolve_marketplace_plugin()`, `discover_marketplace_paths()` in `core/src/plugins/marketplace.rs`; `PluginStore::install()` in `core/src/plugins/store.rs`; `plugin_install` request handler in `app-server/src/codex_message_processor.rs`.


### Artifacts: native PowerPoint and spreadsheet authoring (under-development feature flag: `artifact`)

**What:** A new built-in `artifacts` freeform tool lets the model author and edit `.pptx` and `.xlsx` files inside a thread by running JavaScript against a managed Node-based runtime.

**Details:**
- Accepts raw JavaScript with an optional `// codex-artifacts: timeout_ms=...` pragma.
- Supports `create`, `import_pptx`, `export_pptx`, `export_preview`, plus slide/layout/placeholder/table/chart/image/text/comment manipulation, and undo/redo via a stateful per-thread `artifact_id`.
- A separate render path produces preview images (`pptx render --slide N` for slides, `xlsx render --sheet X` for sheets).
- The runtime (currently pinned at `2.4.0`) is downloaded as a tarball/zip with SHA-256 verification and cached under `<codex_home>/packages/artifacts/<version>/<platform>/`.
- Tool prompt is shipped with Codex at `core/templates/tools/presentation_artifact.md`.

**Code references:** `ArtifactsClient::execute_build()`, `execute_render()`, `ArtifactRenderTarget::Presentation/Spreadsheet` in `artifacts/src/client.rs`; `ArtifactRuntimeManager::ensure_installed()`, `ArtifactRuntimeReleaseLocator`, `ReleaseManifest` in `artifacts/src/runtime.rs`; `ArtifactsHandler` and `PINNED_ARTIFACT_RUNTIME_VERSION` in `core/src/tools/handlers/artifacts.rs`.


### Generic package manager crate

**What:** A new `codex-package-manager` crate that downloads, verifies, and caches platform-specific binary releases — used initially by the artifacts runtime.

**Details:**
- Trait-based `ManagedPackage` lets a caller describe a release locator. The manager downloads a release manifest, picks the entry for one of six platforms (`darwin-arm64`, `darwin-x64`, `linux-arm64`, `linux-x64`, `windows-arm64`, `windows-x64`), verifies SHA-256, extracts (`tar.gz` or `zip`) into a staging dir, then atomically promotes it.
- Two entry points: `ensure_installed()` (download if missing) and `resolve_cached()` (no-op if already up-to-date).

**Code references:** `PackageManager::ensure_installed()`, `resolve_cached()`, `ManagedPackage` trait, `PackagePlatform` enum, `verify_sha256()`, `extract_archive()` in `package-manager/src/lib.rs`.


### Fast / Flex service tier and `/fast` slash command (under-development feature flag: `fast_mode`)

**What:** A new `service_tier` configuration value (`fast` or `flex`) and a `/fast` slash command that lets users opt into ChatGPT's "priority" or "flex" inference tiers.

**Details:**
- `/fast` toggles Fast mode; subcommands `/fast on`, `/fast off`, `/fast status` are accepted.
- Description string in the TUI: *"toggle Fast mode to enable fastest inference at 3X plan usage"*.
- When Fast is on (and `Feature::FastMode` is enabled), turn requests are sent with `service_tier: "priority"`. When set to `Flex`, the literal `"flex"` is sent.
- Selection persists via `ConfigEditsBuilder::set_service_tier`, written either to the active profile or the global `service_tier` key.
- `Op::UserTurn`, turn/start, and turn/update protocol params all gained a tri-state `service_tier: Option<Option<ServiceTier>>` (`Some(Some(_))` to set, `Some(None)` to clear, `None` to keep current).

**Configuration:**
```toml
service_tier = "fast"   # or "flex"
```

**Code references:** `ServiceTier` enum in `protocol/src/config_types.rs`; `SlashCommand::Fast` in `tui/src/slash_command.rs`; `set_service_tier_selection()` in `tui/src/chatwidget.rs`; `AppEvent::PersistServiceTierSelection` in `tui/src/app.rs`; `ConfigEdit::SetServiceTier` in `core/src/config/edit.rs`.


### `/multi-agents` slash command alias

**What:** A new alias `/multi-agents` was added for the existing `/agent` command. Both route to `AppEvent::OpenAgentPicker` via `dispatch_command` in `tui/src/chatwidget.rs`.


### Realtime voice protocol redesign with handoff to typed agent

**What:** The realtime voice conversation mode (`/realtime`) was rewired onto OpenAI's `/v1/realtime` "quicksilver" websocket protocol with an explicit handoff mechanism, so audio chat with Codex can hand control back to the typed-text agent for actual coding work.

**Details:**
- Voice sessions use a low-latency real-time model with PCM 24 kHz audio and the voice "mundo".
- When the realtime model needs backend help, it emits a new `conversation.handoff.requested` event; the typed-text Codex agent then acts as the "intermediary's backend executor."
- New system prompts are injected at realtime start and end (`protocol/src/prompts/realtime/realtime_start.md`, `realtime_end.md`) telling the typed agent it is now responding to a transcript that may be unpunctuated and contain recognition errors, and to keep responses concise.
- New experimental config `experimental_realtime_ws_model` selects the realtime snapshot. The existing `experimental_realtime_ws_base_url` and `experimental_realtime_ws_backend_prompt` keys had their descriptions updated to reflect the new protocol shape (now session.update instructions on `/v1/realtime`).
- New protocol event `RealtimeEvent::HandoffRequested { handoff_id, item_id, input_transcript, messages }` plus `ConversationItemDone` and `SessionUpdated` variants. `RealtimeHandoffMessage = { role, text }` carries the running transcript so the regular Codex session can continue seamlessly.
- New TS schema `RealtimeHandoffRequested.ts` is exported from the app-server protocol.

**Code references:** `send_session_update()`, `send_conversation_handoff_append()`, `websocket_url_from_api_url()`, `with_session_id_header()` in `codex-api/src/endpoint/realtime_websocket/methods.rs`; `RealtimeOutboundMessage`, `SessionUpdateSession { kind: "quicksilver" }`, `parse_realtime_event()` in `codex-api/src/endpoint/realtime_websocket/protocol.rs`; `RealtimeEvent` in `protocol/src/protocol.rs`.


### Cross-thread approval prompts

**What:** Approval prompts (Exec, ApplyPatch, MCP Elicitation) raised by sub-agents now show which thread they belong to and let the user jump to that thread to approve in context.

**Details:**
- `ApprovalRequest` variants (`Exec`, `ApplyPatch`, `McpElicitation`) now carry `thread_id: ThreadId` and `thread_label: Option<String>`.
- When `thread_label` is set, the overlay renders a "Thread: <name>" header and a new "or `o` to open thread" shortcut hint. Pressing `o` fires `AppEvent::SelectAgentThread(thread_id)` and switches the user to the originating sub-agent thread.
- Approval ops are now dispatched as `AppEvent::SubmitThreadOp { thread_id, op }` rather than a plain `CodexOp`, so the response is correctly scoped to the requesting thread.
- New snapshot: `approval_overlay_cross_thread_prompt.snap` shows the "Thread: Robie [explorer]" header and the "open thread" hint.

**Code references:** `ApprovalRequest` in `tui/src/bottom_pane/approval_overlay.rs`; thread routing in `tui/src/chatwidget.rs`.


### Pending steers — see in-flight messages above the composer

**What:** When you type and send a message during a running agent turn, it is now sent to core as a "steer" (live message-during-turn) and shown in a new "pending steer" preview row above the composer until the agent acknowledges it.

**Details:**
- The previous `queued_user_messages.rs` widget was generalized into `pending_input_preview.rs` with two stacked sections:
  - **Pending steers** (dim, prefixed with `! `) — already submitted but not yet committed back as `ItemCompleted(UserMessage)`.
  - **Queued messages** (italic, prefixed with `↳`) — drafts queued for after the current turn.
- The `⌥ + ↑ edit` hint only renders when there are actual queued messages.
- `should_submit_now` no longer requires `stream_controller.is_none()`, so submissions during streaming are now permitted (and round-trip through pending steers if a turn is running). This removes a long-standing race that stranded queued input.
- New snapshots: `render_one_pending_steer.snap`, `render_pending_steers_above_queued_messages.snap`.

**Code references:** `pending_steers: VecDeque<PendingSteer>`, `refresh_pending_input_preview()`, `PendingSteerCompareKey`, `pending_steer_compare_key_from_items()`, `suppress_queue_autosend` in `tui/src/chatwidget.rs` and `tui/src/chatwidget/realtime.rs`.


### Multi-agent enable prompt

**What:** When the user invokes a multi-agent feature while `Feature::Collab` is disabled, a new selection popup appears titled *"Enable multi-agent?"* with subtitle *"Multi-agent is currently disabled in your config."* and two options: *"Yes, enable"* (saves the flag and inserts a history note "Multi-agent will be enabled in the next session.") or *"Not now."*

**Code references:** `ChatWidget::open_multi_agent_enable_prompt()` in `tui/src/chatwidget.rs`; snapshot `multi_agent_enable_prompt.snap`.


### Thread-input state preservation across thread switches

**What:** Switching between agent threads in the multi-agent picker no longer drops in-progress input.

**Details:** New `capture_thread_input_state()` / `restore_thread_input_state()` methods in `tui/src/chatwidget.rs` preserve composer text, pending steers, queued messages, collaboration mode, mention bindings, and pending pastes per thread.


### `thread/metadata/update` V2 protocol method

**What:** Clients (IDE wrappers, app-server consumers) can now patch a thread's stored Git metadata (`sha`, `branch`, `originUrl`) without resuming the conversation.

**Details:**
- Each Git field is tri-state: omit (leave unchanged), `null` (clear), or string (replace).
- An empty patch is rejected with `"gitInfo must include at least one field"`.
- The update repairs missing SQLite rows for stored threads — verified by `thread_metadata_update_repairs_missing_sqlite_row_for_stored_thread`.

**Code references:** Schemas `ThreadMetadataUpdateParams.json`, `ThreadMetadataUpdateResponse.json`; tests in `app-server/tests/suite/v2/thread_metadata_update.rs`.


### Plugin install protocol method

**What:** New V2 method `plugin/install` to install a plugin by name from a configured marketplace. See the Plugins section above for full behavior.

**Code references:** Schemas `PluginInstallParams.json`, `PluginInstallResponse.json`; handler in `app-server/src/codex_message_processor.rs`.


### `SkillsChangedNotification` server notification

**What:** A new V2 server notification is emitted when the active skill set changes (for example because plugins were installed/enabled or skill files on disk changed). Combined with the file-watcher integration below, clients can hot-reload their skill list without restarting.

**Code references:** `SkillsChangedNotification.json` schema; `tests/suite/v2/skills_list.rs`.


### Connectivity diagnostics in the bug-report flow

**What:** The `/feedback` (bug report) view now renders a *"Connectivity diagnostics"* section above the textarea when relevant environment variables are detected.

**Details:**
- For any non-`GoodResult` category that has diagnostics, lines like *"Proxy environment variables are set and may affect connectivity. — `HTTP_PROXY = http://proxy.example.com:8080`"* and *"`OPENAI_BASE_URL` is set …"* are surfaced.
- The upload-consent popup now lists `codex-connectivity-diagnostics.txt` as an additional attachment when diagnostics are present (controlled by the new `include_connectivity_diagnostics_attachment` parameter).
- `CodexLogSnapshot` was renamed to `FeedbackSnapshot` and now carries the diagnostics payload.
- New snapshots: `feedback_view_with_connectivity_diagnostics.snap`, `feedback_good_result_consent_popup.snap`.
- The bug-report URL switched from the `2-bug-report.yml` template to `3-cli.yml`.

**Code references:** `feedback_diagnostics.rs` (new) in `feedback/src/`; `should_show_feedback_connectivity_details()` in `tui/src/bottom_pane/feedback_view.rs`.


### ANSI-family theme support for syntax highlighting

**What:** Bundled `ansi`, `base16`, and `base16-256` themes now use the user's terminal palette colors instead of fixed RGB.

**Details:**
- New helpers `convert_syntect_color()` and `ansi_palette_color()` decode bat's alpha-channel encoding:
  - `a == 0x00`: `r` byte holds an ANSI palette index (0–7 → named ratatui colors `Black/Red/Green/Yellow/Blue/Magenta/Cyan/Gray`, 8–255 → `Indexed(n)`).
  - `a == 0x01`: terminal default foreground (no override).
  - `a == 0xFF`: standard RGB.
- Set `tui.theme.name = "ansi"` (or `base16`, `base16-256`) and your terminal scheme will govern syntax colors.
- Snapshot `ansi_family_foreground_palette.snap` documents the resulting palette per theme.

**Code references:** `convert_syntect_color()`, `ansi_palette_color()` in `tui/src/render/highlight.rs`.


### Notification types for plan-mode prompts and user-input requests

**What:** The TUI's `Notification` enum gained `PlanModePrompt { title }` and `UserInputRequested { question_count, summary }` variants, with priority handling so high-priority prompts (approvals, plan-mode prompts, user-input questions) are not overwritten by a pending `AgentTurnComplete`.

**Details:** Two new TUI notification keys are subscribable via `tui.notifications`: `plan-mode-prompt` and `user-input-requested`. Plan-mode prompts now fire a `PlanModePrompt` notification.

**Code references:** `Notification` enum and `priority()` in `tui/src/chatwidget.rs`.


### `image_detail_original` and `image_generation` features

**What:** Two new under-development feature flags expand the model's image capabilities.

**Details:**
- `image_detail_original`: when enabled and the active model advertises `supports_image_detail_original = true` in `models.json`, `view_image` and `js_repl` image emit pass `detail: "original"` so the model receives full-resolution input rather than a resized copy. Models marked supporting this in 0.110.0: `gpt-5.3-codex` (only). The js_repl tool prompt also got JPEG-quality guidance.
- `image_generation`: when enabled and the model supports image input, the `image_generation_call` built-in tool is exposed. The `ResponseItem::ImageGenerationCall { id, status, revised_prompt?, result }` variant is now stripped from compacted history so image-generation calls don't bloat post-compact context.

**Code references:** `Feature::ImageDetailOriginal`, `Feature::ImageGeneration` in `core/src/features.rs`; `supports_image_generation` and tool gating in `core/src/tools/spec.rs`.


### File watcher + skill hot-reload

**What:** A new file watcher integrates with `SkillsManager::skill_roots_for_config(config)` to deduplicate and watch every directory containing `SKILL.md`/`SKILLS` files (project, user, and plugin sources). Changes emit `FileWatcherEvent`s, so the running session can hot-reload skills without restarting.

**Code references:** `register_config()` in `core/src/file_watcher.rs`.


### Cloud requirements: fail-closed for ChatGPT Business / Enterprise

**What:** Cloud requirements (org-managed config from the backend) now fail-closed for ChatGPT Business and Enterprise accounts.

**Details:**
- `CloudRequirementsLoader::get` now returns `Result<Option<...>, CloudRequirementsLoadError>`. Failures are no longer silently swallowed.
- For Business/Enterprise accounts, failure to fetch requirements aborts config loading with messages like *"timed out waiting for cloud requirements after Ns"* or *"failed to load your workspace-managed config"*.
- New OTel counter `codex.cloud_requirements.load_failure` (with `trigger=startup|refresh`).
- New `feature_requirements` (alias `[features]`) section in cloud-requirements TOML — orgs can pin features on/off (e.g. `apps = false`, `personality = true`). Enforced by the new `ManagedFeatures` wrapper, which normalizes user-set features against pinned values; setting a pinned feature returns `ConstraintError::InvalidValue` citing the requirement source.

**Code references:** `CloudRequirementsLoadError`, `CloudRequirementsLoader::get()` in `cloud-requirements/src/lib.rs` and `config/src/cloud_requirements.rs`; `ManagedFeatures` in `core/src/config/managed_features.rs`.


### Role-specific agent nicknames

**What:** Agent roles can now declare their own pool of candidate nicknames in `config.toml`.

**Configuration:**
```toml
[agent_roles.researcher]
description = "Research role"
nickname_candidates = ["Atlas", "Orion", "Sirius"]
```

**Details:**
- When a sub-agent is spawned with a role that defines `nickname_candidates`, those names are used instead of the default global pool.
- Falls back to the bundled list if a role doesn't declare its own.

**Code references:** `agent_nickname_candidates()`, `default_agent_nickname_list()` in `core/src/agent/control.rs`; `nickname_candidates: Option<Vec<String>>` in `AgentRoleConfig`.


### Skill permission profiles: explicit network sub-object

**What:** Skill permission manifests can now declare network access independently of filesystem access.

**Details:**
- `compile_permission_profile` now interprets `PermissionProfile.network: Option<NetworkPermissions>` (where `NetworkPermissions { enabled: Option<bool> }`) instead of a plain `Option<bool>`.
- A skill that requests network access but no filesystem permissions is now compiled to `SandboxPolicy::ReadOnly { access: FullAccess, network_access: true }` instead of being silently denied.

**Configuration:**
```toml
[permissions.network]
enabled = true
```

**Code references:** `compile_permission_profile()` in `core/src/skills/permissions.rs`.

### Memories config keys renamed to user-meaningful names

The memory pipeline keys were renamed from internal "phase" names to descriptive names:

- `memories.phase_1_model` → `memories.extract_model` (model that summarises a single thread).
- `memories.phase_2_model` → `memories.consolidation_model` (model that merges raw memories into the global memory).
- `memories.max_raw_memories_for_global` → `memories.max_raw_memories_for_consolidation`.
- New `memories.no_memories_if_mcp_or_web_search` (bool, default `false`): when `true`, any MCP tool call or web search marks the current thread's `memory_mode` as `"polluted"`, so consolidation skips it. This prevents external content from contaminating long-term memory.

Defaults still resolve to `gpt-5-mini` (extract) and `gpt-5` (consolidation). Code references: `MemoriesToml`/`MemoriesConfig` in `core/src/config/types.rs`; `clear_memory_root_contents()` in `core/src/memories/control.rs`; `maybe_mark_thread_memory_mode_polluted()` in `core/src/mcp_tool_call.rs` and `core/src/codex.rs`.


### Plan mode produces shorter, behavior-focused plans

The plan-mode template (`core/templates/collaboration_mode/plan.md`) now instructs the planner to be *"concise by default,"* prefer a 3–5 section compact structure (Summary, Key Changes, Test Plan, Assumptions), avoid file-by-file inventories, mention at most 3 paths, omit branch-by-branch logic and "unaffected behavior" lists, and not invent schema/validation/precedence policy unless explicitly requested. Users who want a detailed plan must ask for one.


### Multi-agent picker readability

Agent picker visuals were retoned in `tui/src/multi_agents.rs`:
- Closed-status dot is now plain (was `dark_gray`); active dot stays green.
- Agent nicknames switched from `LightBlue.bold` to `Cyan.bold`.
- Thread IDs and the "agent" placeholder switched from dim to plain `cyan`.
- `[role]` brackets, "Pending init", "Shutdown", "No agents completed yet", and error preview text are no longer dimmed.


### Footer prioritization between status line and queue hint

The composer footer in `tui/src/bottom_pane/footer.rs` now does the right thing when both a status line and a queue hint are competing for the same row:
- If a status line is configured AND the user has a draft AND a task is running, the queue hint *"tab to queue message … 100% context left"* wins.
- If `show_queue_hint` is false but `show_shortcuts_hint` is true, the shortcuts hint is now shown (was previously dropped).
- New snapshots: `footer_status_line_overrides_draft_idle.snap`, `footer_status_line_yields_to_queue_hint.snap`.


### Permission-rule formatting includes network

`format_additional_permissions_rule` in `tui/src/bottom_pane/approval_overlay.rs` now prepends `network` to the rule string when `additional_permissions.network.enabled` is true. Example: *"Permission rule: network; read /tmp/readme.txt; write /tmp/out.txt."*


### Theme warning copy

User-facing warnings around custom syntax themes were reworded: *"auto-detection"* became *"default theme"*; an invalid `.tmTheme` now reads *"could not be loaded (invalid .tmTheme format)"*; the duplicate-override warning was downgraded to a debug log so it no longer surfaces a banner.


### ChatGPT plan name update in onboarding

The ChatGPT login description on the onboarding/auth screen now reads *"Usage included with Plus, Pro, **Business**, and Enterprise plans"* (was *"Plus, Pro, **Team**, and Enterprise plans"*), reflecting OpenAI's plan rename.


### Inherited shell snapshot when spawning sub-agents

`AgentControl::spawn_agent` now propagates the parent thread's `ShellSnapshot` to spawned sub-agents via a new `inherited_shell_snapshot: Option<Arc<ShellSnapshot>>` parameter (`core/src/agent/control.rs`, `core/src/codex_thread.rs`, `core/src/thread_manager.rs`). Forked threads inherit the same shell environment as their parent.


### Agent nickname pool reset adds ordinal suffix

When the agent nickname pool is exhausted and reset, names now get an ordinal suffix instead of being silently re-used. After the first reset you get *"Plato the 2nd"*, then *"Plato the 3rd"*, etc., with proper suffix handling for 11/12/13. Implemented by `format_agent_nickname()` in `core/src/agent/guards.rs`.


### Compact pipeline preserves previous-turn settings (model + realtime status)

The remote-compact code (`core/src/compact_remote.rs`, `core/src/compact.rs`) replaced the `previous_user_turn_model: Option<&str>` argument plumbing with `Session::set_previous_turn_settings(Option<PreviousTurnSettings>)`, where `PreviousTurnSettings { model, realtime_active }`. `Session::build_initial_context` reads from session state directly. Net effect: when a turn rolls back from a realtime/voice handoff or a different model, the compact pipeline now picks up both the previous model AND realtime status.


### Models cache: `supports_image_detail_original`

The `ModelInfo` struct gained a `supports_image_detail_original: bool` field. `ModelsManager` overlays it from the remote `/models` response so the server can declare *"this model can accept images at original detail level"* and Codex won't downscale before sending. Verified by the new test `namespaced_remote_model_inherits_supports_image_detail_original`.


### `SessionConfiguration` and `OverrideTurnContextParams` carry `service_tier`

These structs picked up parallel `service_tier: Option<ServiceTier>` slots so the active service tier can be read and overridden mid-session via `Op::OverrideTurnContext`.


### Personality migration: `memory_mode` field

`SessionMeta` (the rollout/state DB metadata structure) gained `memory_mode: Option<String>` (`"enabled"` | `"disabled"` | `"polluted"`). Combined with `reconcile_rollout`, opening an old rollout will populate the per-thread memory mode from its rollout history into the state DB.


### App-server protocol: typescript schema cleanup

A large chunk of the v1 typescript protocol files were removed (e.g. `AddConversationListenerParams.ts`, `ArchiveConversationParams.ts`, `AuthStatusChangeNotification.ts`, `ExecOneOffCommand*.ts`, `ForkConversation*.ts`, `GetUserSavedConfigResponse.ts`, `InputItem.ts`, `Interrupt*.ts`, `ListConversations*.ts`, `Login*.ts`, `NewConversation*.ts`, `Profile.ts`, `Resume*.ts`, `SandboxMode.ts`, `SandboxSettings.ts`, etc.) in favor of the consolidated v2 schemas. The remaining v1 types (`ClientRequest.ts`, `ResponseItem.ts`, `SandboxPolicy.ts`, `RealtimeEvent.ts`, etc.) were updated, and new v2 helpers (`PluginInstallParams.ts`, `SkillsChangedNotification.ts`, `ThreadMetadataGitInfoUpdateParams.ts`, `ThreadMetadataUpdateParams.ts`) were added.

### Completion watcher notifies parent when child thread is missing

If a sub-agent's thread can't be subscribed to (e.g. it was already cleaned up), the multi-agent completion watcher now still issues a final notification to the parent thread instead of silently exiting. The parent's history correctly reports `"status":"not_found"` along with the child's `agent_id`. Verified by `completion_watcher_notifies_parent_when_child_is_missing` in `core/src/agent/control.rs`.


### Agent role config preserves caller-owned model selection

`apply_role_to_config` in `core/src/agent/role.rs` no longer rebuilds the config in a way that silently drops the caller's `profile` and `model_provider`. The role layer is inserted at session-flag precedence so it can override persisted config, but the caller's current profile and provider remain sticky unless the role explicitly takes ownership of model selection.


### Submitting during streaming no longer strands input

`should_submit_now` in `tui/src/chatwidget.rs` no longer requires `stream_controller.is_none()`. Submissions during streaming are now permitted (and round-trip through pending steers if a turn is running). This removes a long-standing race that stranded queued input.


### Plan-implementation prompt skipped when steers are pending

`maybe_prompt_plan_implementation` is now skipped when there are pending steers (not just queued messages), preventing the prompt from racing live in-flight user input.
