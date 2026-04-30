# Changelog for version 0.122.0

## Highlights

This release expands Codex from a coding-only tool into a more general agentic
assistant: a brand-new **Side Conversations** feature lets you fork off
throwaway questions without polluting the main thread, **Plan mode** can now
implement an approved plan in a fresh context, and the **realtime voice
assistant** has been re-prompted to handle browsing, documents, and research
rather than only coding tasks. The plugin/marketplace system gains long-missing
**`marketplace remove`**, **`marketplace upgrade`** (with automatic startup
sync), and Git-hosted marketplace sources, plus a tabbed plugins popup. New
authentication primitives — task-scoped **AgentAssertion** headers and
server-side **token revocation on logout** — strengthen agent-identity
workflows. Lower-profile but impactful: streaming `apply_patch` events that
let UIs render diffs as they're being written, glob-based filesystem deny
patterns that block reads of `**/.env*`-style paths, an `install-context`
crate that lets standalone installs use their bundled `rg`, and a
`/side`-aware TUI with `Ctrl+P/Ctrl+N` navigation in the resume picker.

### Side Conversations (`/side`)

**What:** A new slash command `/side` opens an ephemeral fork thread that
inherits the parent's history as read-only context. You can ask exploratory
questions or run scratch work without affecting the main thread; pressing
`Esc` returns to the parent unchanged.

**Details:**
- A boundary prompt and developer instructions in the side thread block the
  agent from mutating files or shared state.
- The composer placeholder, footer label, and slash-command set switch into
  side mode; only `Copy / Diff / Mention / Status` slash commands are
  available while a side conversation is active.
- New keyboard flow integrates with the existing approval/queue system —
  side mode is tracked alongside the normal thread.

**Code references:** `tui/src/app/side.rs` (new, ~405 lines),
`tui/src/chatwidget/side.rs` (new), `request_empty_side_conversation()` in
`tui/src/chatwidget/slash_dispatch.rs`, `available_in_side_conversation()` in
`tui/src/slash_command.rs`, `side_conversation_context_line()` in
`tui/src/bottom_pane/footer.rs`.


### External Agent Config Migration

**What:** When Codex starts and detects a competing agent's configuration
(notably Claude's `~/.claude/`), it now offers to import settings, enabled
plugins, and instruction files into the equivalent Codex locations.

**Details:**
- An interactive selection screen lets you pick which items to migrate:
  - `[x] Migrate /Users/.../.claude/settings.json into ...codex/...`
  - `[ ] Migrate enabled plugins from ...`
  - `[ ] Migrate CLAUDE.md to AGENTS.md`
- Three actions: **Proceed**, **Skip for now**, or **Don't ask again**.
- Plugin imports complete in the background and fire a new
  `ExternalAgentConfigImportCompleted` notification when done.

**Code references:** `tui/src/external_agent_config_migration.rs` (new, 1024
lines), `tui/src/external_agent_config_migration_startup.rs` (new),
`v2/ExternalAgentConfigImportCompletedNotification.json`,
`message_processor.rs::external_agent_config_import` async branch.


### Plan-Mode "Implement Plan" Workflow

**What:** After the model produces a plan in Plan mode, the popup now offers
three actions instead of two:

1. **Yes, implement this plan** — execute it in the current thread.
2. **Yes, clear context and implement** — *new* — start a fresh thread with
   only the plan markdown injected so the implementer isn't pre-biased by
   exploratory turns.
3. **No, stay in Plan mode** — keep iterating.

The popup also displays a context-usage label (e.g. `Context: 89% used`) so
you can decide whether a fresh thread is warranted.

**Code references:** `tui/src/chatwidget/plan_implementation.rs` (new, 114
lines), `latest_proposed_plan_markdown` field on `ChatWidget`.


### `PermissionRequest` Hook Event

**What:** A brand-new hook event type lets you script approval decisions for
tool invocations (currently shell-command approvals). The hook's verdict —
`allow` or `deny` — takes precedence over both the auto-reviewer and the user
prompt.

**Details:**
- Multiple matching handlers run; **deny wins**.
- Hooks fail closed if they try to set reserved fields (`updatedInput`,
  `updatedPermissions`, `interrupt: true`).
- Configured under `hooks.permission_request` in your hook config; emits the
  same `HookStartedNotification`/`HookCompletedNotification` flow.

Example hook config:

```toml
[[hooks.permission_request]]
matcher = "Bash"
command = "/usr/local/bin/policy-gate"
```

The hook receives a `PermissionRequestCommandInput` JSON document on stdin
and returns `{ "decision": "allow" | "deny", "reason": "..." }`.

**Code references:** `hooks/src/events/permission_request.rs` (new, 331
lines), `parse_permission_request()` in `hooks/src/engine/output_parser.rs`,
`run_permission_request_hooks()` in `core/src/hook_runtime.rs`,
`PermissionRequestCommandInput`/`Output` schemas in `hooks/src/schema.rs`,
wiring in `tools/orchestrator.rs::request_approval` and
`tools/network_approval.rs`.


### `codex plugin marketplace remove`

**What:** New CLI subcommand to fully uninstall a marketplace — both the
`config.toml` entry and the installed-plugin contents on disk.

**Usage:**
```
codex plugin marketplace remove openai-curated
```

**Details:**
- Validates the marketplace name (case-mismatched names produce a distinct
  `NameCaseMismatch` outcome rather than silently failing).
- Removes the entry from both table and inline-table TOML forms; drops an
  empty `[marketplaces]` parent.
- Exposed as a v2 RPC: `marketplace/remove` with `MarketplaceRemoveParams`
  and `MarketplaceRemoveResponse` carrying the deleted `installedRoot`.

**Code references:** `core/src/plugins/marketplace_remove.rs` (new),
`remove_user_marketplace()` in `config/src/marketplace_edit.rs`,
`run_remove()` in `cli/src/marketplace_cmd.rs`,
`v2/MarketplaceRemoveParams.json`, `cli/tests/marketplace_remove.rs`.


### `codex plugin marketplace upgrade` & Auto-Upgrade

**What:** New CLI subcommand and background worker that refresh Git-hosted
marketplaces in place. Run on demand, or let Codex sync them at startup.

**Usage:**
```
codex plugin marketplace upgrade            # all configured marketplaces
codex plugin marketplace upgrade my-team    # a specific one
```

**Details:**
- Uses `git ls-remote` to detect drift, clones into
  `<codex_home>/.tmp/marketplaces/.staging/`, validates the marketplace root,
  and atomically swaps it into place with rollback on failure.
- Records `last_revision` per marketplace in `config.toml` so future upgrades
  know what changed.
- Forces a non-curated cache reinstall after upgrade so installed plugins
  pick up new manifest versions.
- A startup thread (`plugins-marketplace-auto-upgrade`) runs the same flow
  asynchronously when the `Plugins` feature is enabled.

**Code references:** `core-plugins/src/marketplace_upgrade.rs` (new) plus
`marketplace_upgrade/activation.rs`, `marketplace_upgrade/git.rs`,
`upgrade_configured_marketplaces_for_config()` in `core/src/plugins/manager.rs`,
`run_upgrade()` in `cli/src/marketplace_cmd.rs`,
`cli/tests/marketplace_upgrade.rs`.


### Git-Hosted Marketplaces

**What:** Marketplaces can now be defined as Git repositories in
`config.toml`. Codex will clone them, optionally pinning to a `ref` or `sha`
and using sparse-checkout when only a `path` is needed.

**Supported source forms:**
- Bare path string: `"./local-marketplace"`
- Local table: `{ source = "local", path = "..." }`
- URL: `{ source = "url", url = "...", path = "subdir", ref = "main" }`
- Git subdir: `{ source = "git-subdir", url = "...", path = "...", sha = "..." }`
- GitHub shorthand: `owner/repo` is auto-expanded to a full HTTPS URL.

URLs are normalized (`.git` suffix added/stripped), and `ssh://`,
`git@host:`, and `file://` are accepted. Relative paths are validated to
prevent escape.

**Code references:** `MarketplacePluginSource::Git { url, path, ref_name, sha }`
in `core-plugins/src/marketplace.rs`, `materialize_marketplace_plugin_source()`
in `core-plugins/src/loader.rs`.


### `core-plugins` Crate (Plugin System Refactor)

**What:** The plugin/marketplace logic was extracted from `core` into a new
standalone `core-plugins` crate. Most of `core/src/plugins/` (manifest,
remote, store, toggles, marketplace, loader) now lives in `core-plugins`,
decoupled from the full `Config` type.

**User-visible upshot:** No behavior changes for end users *per se*, but
the new layout enables Git marketplaces, marketplace upgrade, the Claude
manifest discovery (below), and lighter rebuilds for tooling that doesn't
need the full `core` crate.

**Code references:** `core-plugins/src/{lib,loader,manifest,marketplace,marketplace_upgrade,remote,store,toggles}.rs`.


### Claude-Format Manifest Discovery

**What:** Codex now reads `.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json` in addition to the native
`.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`. Claude
plugins drop in without renaming.

**Code references:** `find_plugin_manifest_path()` in
`utils/plugins/src/plugin_namespace.rs`, marketplace manifest search in
`core-plugins/src/marketplace.rs`.


### `account/sendAddCreditsNudgeEmail` API

**What:** A new app-server v2 RPC lets clients trigger a backend email to the
workspace owner when credits are depleted or a usage limit is hit.

**Details:**
- Params include `creditType` (`Credits` or `UsageLimit`).
- Response is `{ status: "Sent" | "CooldownActive" }` — backend rate-limits
  by returning HTTP 429, which the handler maps to the cooldown response.
- Accompanies new typed rate-limit signals (see *Improvements* below).

**Code references:** `send_add_credits_nudge_email()` in
`app-server/src/codex_message_processor.rs`, `BackendClient::from_auth()`,
`v2/SendAddCreditsNudgeEmailParams.json`/`Response.json`.


### `thread/turns/list` Endpoint

**What:** New v2 RPC paginates the turns of a single thread. Supports
forward and backward cursors and an explicit `sortDirection`.

**Params/Response:**
- Params: `{ threadId, cursor?, limit?, sortDirection? }`
- Response: `{ data[], nextCursor?, backwardsCursor? }`

**Code references:** `v2/ThreadTurnsListParams.json`/`Response.json`,
handler dispatch in `app-server/src/codex_message_processor.rs`.


### `warning` Notification

**What:** A generic `warning` server notification (`{ message, threadId? }`)
gives clients a uniform channel for transient, non-fatal issues that
previously had no place to surface.

**Code references:** `v2/WarningNotification.json`, `WarningNotification.ts`.


### Per-Task `AgentAssertion` Auth Headers

**What:** ChatGPT-authenticated agents can now mint task-scoped signed
authorization headers. Each header is bound to a specific
`(agent_runtime_id, task_id)` pair and signed with the agent's stored
Ed25519 private key.

**Details:**
- New `agent_assertion.rs` module assembles a JSON payload
  `{agent_runtime_id, task_id, timestamp, signature}` and base64url-encodes
  it as `AgentAssertion <…>`.
- Used by `mcp_openai_file.rs` when uploading local files, replacing raw
  bearer tokens.
- New `register_task()` on the agent identity manager calls
  `POST /v1/agent/{agent_runtime_id}/task/register` and decrypts the
  returned `encrypted_task_id` via Curve25519 sealed-box.

**Code references:** `login/src/auth/agent_assertion.rs` (new, 172 lines),
`agent_identity/task_registration.rs` (new, 466 lines),
`AuthManager::chatgpt_agent_task_authorization_header_for_auth()`.


### OAuth Token Revocation on Logout

**What:** `codex logout` now actively revokes credentials server-side rather
than just deleting them locally. Refresh tokens are revoked first (with
`client_id`); access tokens fall back if refresh-token revocation fails.

**Details:**
- New URL: `https://auth.openai.com/oauth/revoke`, overridable with
  `CODEX_REVOKE_TOKEN_URL_OVERRIDE_ENV_VAR`.
- Revocation is best-effort; logout always proceeds.

**Code references:** `login/src/auth/revoke.rs` (new, 209 lines),
`logout_with_revoke()` in `login/src/auth/manager.rs`, wired through
`cli/src/login.rs` and `app-server/src/codex_message_processor.rs::logout`.


### Remote Thread Store (gRPC)

**What:** A new `RemoteThreadStore` lets Codex offload thread storage to a
remote service over gRPC (tonic). Currently `list_threads` is implemented;
other operations return `not_implemented`.

**Details:**
- New protobuf service `codex.thread_store.v1.ThreadStore` with
  `ListThreads` RPC, `StoredThread`, `SessionSource`, and `GitInfo` messages.
- Build tooling: `examples/generate-proto.rs`, `scripts/generate-proto.sh`.

**Code references:** `thread-store/src/remote/{mod,helpers,list_threads}.rs`,
`thread-store/src/remote/proto/codex.thread_store.v1.proto`,
new dependencies `tonic = "0.14.3"`, `tonic-prost = "0.14.3"` in workspace
`Cargo.toml`.


### `install-context` Crate (Install-Method Detection)

**What:** A new crate detects how the running `codex` binary was installed
— `Standalone`, `Npm`, `Bun`, `Brew`, or `Other` — and exposes
helpers that take advantage of bundled resources.

**Details:**
- Detection inputs: `current_exe`, `CODEX_MANAGED_BY_NPM` /
  `CODEX_MANAGED_BY_BUN` env vars, the `packages/standalone/releases/...`
  layout under `codex_home`, and macOS Homebrew prefixes.
- New `rg_command()` prefers a bundled `rg`/`rg.exe` from
  `codex-resources/` for Standalone installs and falls back to PATH lookup
  otherwise.

**User benefit:** Standalone installs use the ripgrep they ship with,
removing a hidden PATH dependency. The TUI update prompt also adapts to the
install method (see *Improvements*).

**Code references:** `install-context/src/lib.rs` (new, 258 lines), used by
`tui/src/update_action.rs`.


### `codex debug models`

**What:** A new debug command dumps the raw model catalog as JSON.

**Usage:**
```
codex debug models                # current installation's catalog
codex debug models --bundled      # bundled-only catalog
```

Useful for verifying which models the local config sees and what
`max_context_window` they advertise.

**Code references:** `cli/src/main.rs` debug subcommand,
`models-manager/src/manager.rs::raw_model_catalog()`,
`cli/tests/debug_models.rs`.


### Windows Desktop App Support

**What:** `codex app` now works on Windows: install / launch the desktop
app via `Get-StartApps`, falling back to a Microsoft Store URL if the app
isn't installed.

**Code references:** `cli/src/desktop_app/windows.rs` (new, 132 lines).


### Streaming `apply_patch` Updates

**What:** When the new `Feature::ApplyPatchStreamingEvents` feature is
enabled, the partial argument stream of an `apply_patch` tool call is
parsed on every delta, emitting `PatchApplyUpdated` events with a
progressively populated `changes: HashMap<PathBuf, FileChange>` map. UIs
can render the diff *while the model is still writing the patch*.

**Code references:** `parse_patch_streaming()` and `ParseMode::Streaming`
in `apply-patch/src/parser.rs`, `ApplyPatchArgumentDiffConsumer` in
`core/src/tools/handlers/apply_patch.rs`, `PatchApplyUpdatedEvent` in
`protocol/src/protocol.rs`, `ResponseEvent::ToolCallInputDelta` in
`codex-api/src/common.rs`.


### Filesystem Glob Deny Patterns

**What:** The filesystem-sandbox policy now supports git-style glob entries
(in addition to literal paths) for deny rules. Patterns like `**/.env*` or
`secrets/**` block the model's read tool from touching matched files even
when the read is invoked directly.

**Details:**
- New `FileSystemPath::GlobPattern { pattern: String }` variant (currently
  supports `FileSystemAccessMode::None`, i.e. deny-by-glob).
- Compiled once into a `ReadDenyMatcher` that fails closed on malformed
  patterns.
- New `glob_scan_max_depth: Option<usize>` cap.
- Convenience constructors: `unrestricted()`, `external_sandbox()`,
  `restricted(entries)`.
- Migration helper `from_legacy_sandbox_policy_preserving_deny_entries(...)`
  for upgrading existing configs.

**Code references:** `protocol/src/permissions.rs` (~+200 lines incl.
`ReadDenyMatcher`), new `globset` workspace dependency.


### YOLO Mode Indicator

**What:** When you run with `AskForApproval::Never` *and*
`DangerFullAccess`, the session header now displays
`permissions: YOLO mode` so it's unmistakable that approval gating is off.

**Code references:** `is_yolo_mode()` in `tui/src/history_cell.rs`.


### Image-Detail Control in Code Mode & JS REPL

**What:** Code-mode JS callbacks can now request a specific image-detail
level when emitting images:

```js
codex.emitImage(url, "high");   // also: "auto" | "low" | "high" | "original"
```

Previously only `"original"` was accepted, forcing the agent to pay
full-resolution token costs even for thumbnails. MCP image blocks can also
carry `_meta["codex/imageDetail"]` and Codex propagates it through.

**Code references:** `image_callback` in `code-mode/src/runtime/callbacks.rs`,
`DEFAULT_IMAGE_DETAIL = ImageDetail::High` in `code-mode/src/response.rs`,
`parseMcpImageDetail()` in `core/src/tools/js_repl/kernel.js`.


### Tabbed Plugins Popup

**What:** The `/plugins` popup is now organised into tabs — `All plugins`,
`Installed`, and per-marketplace tabs like `marketplace:openai-curated` —
with a per-plugin enable/disable toggle alongside the row.

**Code references:** `tui/src/bottom_pane/selection_tabs.rs` (new, 103
lines), `tui/src/chatwidget/plugins.rs` tab IDs (`ALL_PLUGINS_TAB_ID`,
`INSTALLED_PLUGINS_TAB_ID`, `OPENAI_CURATED_TAB_ID`), `on_plugin_enabled_set`
callback.

### Realtime Voice Assistant Reframed as General-Purpose

The realtime backend prompt (`core/templates/realtime/backend_prompt.md`)
was rewritten end-to-end. The realtime model is now positioned as a
general-purpose agentic assistant covering coding, browsing, apps,
documents, and research — not just coding tasks. It always passes work to
the backend, never refuses, and never reveals the two-tier
realtime/backend split. New `[USER]` / `[BACKEND]` text prefixes
(`REALTIME_USER_TEXT_PREFIX`, `REALTIME_BACKEND_TEXT_PREFIX`) help the
realtime model distinguish message sources during V2 sessions, and the
handoff completion message is more direct: *"Background agent finished.
Use the preceding [BACKEND] messages as the result."* Token budget bumped
from 5000 to 5300.


### Remote Compaction on Non-OpenAI Providers

`should_use_remote_compact_task()` now consults
`provider.supports_remote_compaction()` instead of hard-coding
`provider.is_openai()`. Azure providers (and others advertising support)
now get remote compaction. Verified by the new test
`should_use_remote_compact_task_for_azure_provider` in
`core/src/compact_tests.rs`.


### Restored Token Usage on `thread/fork` and `thread/resume`

After a fork or resume, Codex now sends a token-usage snapshot
(`send_thread_token_usage_update_to_connection`) before the next turn so
client status lines populate immediately. New tests
`thread_fork_emits_restored_token_usage_before_next_turn` and
`thread_resume_emits_restored_token_usage_before_next_turn` enforce this.
The new `core/src/codex_thread.rs::token_usage_info()` accessor exposes
the full `TokenUsageInfo` snapshot used for the notification.


### Plugin Install Without Local Marketplace Path

`PluginInstallParams.marketplacePath` is now optional and gains a
`remoteMarketplaceName: string | null` companion field. You can install
from a remote-only marketplace catalog without first checking out a local
path. `forceRemoteSync` was removed from install/uninstall/list — the
feature was effectively superseded by the new upgrade flow.

`PluginInterface` also adds `composerIconUrl`, `logoUrl`, and
`screenshotUrls` (remote URLs from the catalog) alongside the existing
locally-resolved versions, so listings render with branding before
installation. `PluginSource` (TS) is now a discriminated union of
`local | git | remote`.

Reading an uninstalled Git plugin returns a `PluginDetail` with the new
`details_unavailable_reason: Some(InstallRequiredForRemoteSource)` and a
synthetic description, rather than failing.


### Models: `max_context_window` and 1M Window for `gpt-5.4`

Every entry in `models-manager/models.json` gained a `max_context_window`
field. Notably, `gpt-5.4` advertises `max_context_window: 1000000` —
users can opt into the 1M-token window by overriding
`model_context_window` in config; the override is now clamped via
`min(user_override, max_context_window)` rather than applied blindly. No
new model slugs were added.


### Cross-Platform `marketplace add`

- `--sparse` is now rejected with a clear error (`InvalidRequest("--sparse
  is only supported for git marketplace sources")`) when used against
  non-Git sources.
- Windows absolute paths (`C:\...`, `\\server\share\...`) and `.\` / `..\`
  are now recognised as local sources, fixing cross-platform `marketplace
  add` behavior.
- A `last_revision` field is recorded on add to feed the upgrade flow.


### Hook Source Attribution & Hook Analytics

- `HookRunSummary` and the `HookStarted`/`HookCompleted` notifications now
  include a `source` field (`HookSource`) so clients can see whether a
  hook came from `system`, `user`, `project`, `mdm`, `sessionFlags`, or
  legacy managed-config layers. Surfaced in the TUI's hook cell with
  per-source styling.
- A new `codex_hook_run` analytics event captures
  `{event_name, hook_source, status}` per hook execution, plus OTEL
  `HOOK_RUN_METRIC` and `HOOK_RUN_DURATION_METRIC`. Stuck `Running` status
  is normalized to `Failed` defensively before send.


### Guardian → "Auto-Reviewer" Naming

User-facing strings throughout the guardian system were renamed: rejection
copy now reads *"Auto-reviewer denied…"* instead of *"Guardian denied…"*,
and the schema descriptions on `GuardianApprovalReview*`,
`GuardianRiskLevel`, `GuardianUserAuthorization`, and the related
notifications use *"approval auto-review"* in place of *"guardian approval
review"*. The model slug also changed from `gpt-5.4` to
`codex-auto-review`. Skill prompt context is now suppressed in
auto-review sessions (`include_skill_instructions = false`) so leaks
don't pollute the reviewer.


### Resume Picker Keyboard Navigation

`Ctrl+P` / `Ctrl+N` (and the matching raw bytes `^P` / `^N`) now act as
Up/Down aliases in the resume picker, matching readline-style muscle
memory. Listing now uses `codex_rollout::SortDirection::Desc` explicitly,
and the cursor display was simplified.


### Onboarding & Trust Prompt

`OnboardingScreen::new` is now async and resolves the git project root for
the trust target during construction (so trust applies to the project, not
the cwd). The trust prompt copy was expanded to call out what's actually
allowed: *"Trusting the directory allows project-local config, hooks, and
exec policies to load."*


### Custom Prompt Pre-Fill & Dismiss/Submit Distinction

`bottom_pane/custom_prompt_view.rs` gains an `initial_text` parameter so a
prompt can be pre-filled (e.g. when re-opened after a queued input). The
return type changed from `bool` to `ViewCompletion::{Accepted, Cancelled}`
so callers can finally distinguish a dismiss from an empty submit.


### `update_action` Detects Standalone Installs

`tui/src/update_action.rs` now detects `StandaloneUnix` (suggests
`curl … install.sh | sh`) and `StandaloneWindows` (`irm … install.ps1 | iex`)
in addition to npm/bun/brew, using the new `codex_install_context::InstallContext`.


### Mac Desktop App Architecture Auto-Detect

`cli/src/desktop_app/mac.rs` now auto-detects Apple Silicon vs x86_64 and
picks the correct DMG URL. The `--download-url` CLI flag was renamed to
`--download-url-override` (still optional) to reflect that auto-detection
is the default.


### `thread/list` Bidirectional Pagination

`thread/list` now accepts a `sortDirection` parameter and returns a new
`backwardsCursor` field, enabling reverse-paging without skipping
same-second updates. The `LocalThreadStore` exposes a real archive /
unarchive / list / read implementation (previously `unsupported`) — see
`thread-store/src/local/{archive_thread,unarchive_thread,list_threads,read_thread}.rs`.
The shared `SortDirection` enum (`Asc`/`Desc`) is also threaded through
the rollout listing pipeline (`rollout/src/list.rs`,
`rollout/src/recorder.rs`).


### Typed Rate-Limit Reasons

`RateLimitSnapshot` and `account/rateLimits/updated` notifications now
include a `rateLimitReachedType` field with values like
`rate_limit_reached`, `workspace_owner_credits_depleted`,
`workspace_member_credits_depleted`, and the corresponding
`workspace_*_usage_limit_reached` variants. Pairs with the new
add-credits-nudge endpoint above.


### Pluggable Auth in the API Crate

All `codex-api` endpoint clients (`compact`, `memories`, `models`,
`realtime_call`, `realtime_websocket`, `responses`, `responses_websocket`,
`session`) lost their generic `<A: AuthProvider>` type parameter and now
take `auth: SharedAuthProvider = Arc<dyn AuthProvider>` directly. Cleaner
type plumbing, fewer monomorphisations, and runtime-swappable auth.


### `model-provider` Crate

A new `codex-model-provider` workspace crate provides a `ModelProvider`
trait, `SharedModelProvider = Arc<dyn ModelProvider>`, and a
`create_model_provider(provider_info, auth_manager)` factory that
encapsulates the previously scattered logic for building API clients,
attaching auth headers, and handling command-auth providers.
`models-manager` and downstream API consumers now use it instead of
juggling `AuthManager` + `ModelProviderInfo` separately.


### Memory-Clearing CLI Hook

`clear_memory_roots_contents(codex_home)` now publicly clears both
`memories/` and `memories_extensions/` (previously single-root,
internal-only). Exercised by the new `cli/tests/debug_clear_memories.rs`.


### Sandbox-Denied Processes Surface Real Output

Unified-exec now classifies sandbox denials as
`UnifiedExecError::sandbox_denied(...)` carrying the captured stdout/stderr,
instead of flattening the failure into a generic `create_process` error.
The agent gets the real error message instead of an opaque one.


### Pushed Process Events in `exec-server`

`exec-server` processes now expose a streaming event API
(`ExecProcessEvent::{Output, Exited, Closed, Failed}` with replay buffer
+ broadcast). `subscribe_events()` lets callers consume out-of-order
notifications via a sequenced `BTreeMap` — failures publish a synthesized
`Failed` event so the client never hangs. New `pipe_stdin: bool` on
`ExecParams` allows stdin without a TTY.


### Side-Conversation-Aware Slash Command UI

- `Memories` slash command is no longer permanently disabled.
- `/fast` description tweaked from "2X plan usage" to "increased plan
  usage".
- New `/side` tooltip; `tooltips.txt` updated.
- `selection_popup_common.rs` adds a `ColumnWidthConfig` and a
  `name_column_width` so different selection lists can share aligned
  columns.


### Global Status Line Cleanup

`bottom_pane/status_line_setup.rs` removed the redundant
`ContextRemainingPercent` variant — folded into `ContextRemaining` —
fixing duplicated representations of the same datum.


### `morpheus` Agent Path

`AgentPath` now accepts a special root-equivalent `/morpheus` in addition
to `/root`. New `AgentPath::MORPHEUS` constant and
`AgentPath::morpheus()` constructor in `protocol/src/agent_path.rs`.

### Remote-Control Mutex Held Across `await`

`app-server/src/transport/remote_control/websocket.rs` was holding a mutex
across an `await` while sending serialized envelopes, occasionally
deadlocking under load. Envelopes are now cloned out of the lock before
the send. Windows CI timeout extended to 30s, and the
`connection_handling_websocket` test bumped `DEFAULT_READ_TIMEOUT` to 60s
on macOS/Windows to match Bazel start-up cost.


### Remote Control No Longer Requires Pre-Configured Auth

`validate_remote_control_auth` was removed from the remote-control
startup path; remote control now starts even when ChatGPT auth isn't yet
available. New regression test:
`remote_control_start_allows_missing_auth_when_enabled`.


### Logout Race in TUI

The TUI now routes logout through `AppEvent::Logout` rather than calling
the auth manager directly, fixing a race where `codex-login`'s state
could lag the UI's state.


### Network-Approval Records Originating Command

`tools/network_approval.rs::register_call` now takes the originating
command, fixing a case where retried approvals couldn't be matched to
the right pending request.


### Per-Marketplace `last_revision` Reset on Add

`marketplace add` now writes `last_revision: None` so the upgrade flow
correctly recognises a fresh marketplace as needing an initial sync
rather than skipping it.


### Cursor Format Change in `rollout` Listing

`rollout/src/list.rs` simplified the pagination `Cursor` from
`(timestamp, uuid)` to a plain RFC3339 timestamp; `parse_cursor` now
rejects tokens containing `|`. This is technically a wire-format change —
clients that persisted cursors with the old format will need to re-fetch
the first page.


### Realtime Conversation Source Disambiguation

V2 realtime sessions tag user vs backend turns with `[USER]` / `[BACKEND]`
prefixes so the realtime model can correctly attribute prior context, a
class of confusion that previously led to the model treating its own
backend output as user input.

## Notes for Implementers

This release also performs a substantial internal restructure: the
`core/src/codex.rs` module was split into
`core/src/session/{session, turn, turn_context, handlers, mcp, review,
agent_task_lifecycle, mod}.rs`. All `crate::codex::Session/TurnContext/...`
references are now `crate::session::session::Session`, etc. No behavior
change, but downstream forks consuming `core` internals will need to
update imports.
