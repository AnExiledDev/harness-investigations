# Changelog for version 0.125.0

## Highlights

This release introduces a **`marketplace/upgrade` RPC** that pulls the latest revisions of Git-backed plugin marketplaces in place, **first-class Amazon Bedrock model provider support** with a bundled catalog of `openai.gpt-*` models, and a **redesigned `PermissionProfile`** that distinguishes between Codex-managed, externally enforced, and disabled sandbox enforcement. Additional infrastructure work brings a **Unix-socket transport** to the app-server, an **`excludeTurns` flag** for cheaper thread fork/resume, an **experimental remote thread-config endpoint** (gRPC) for centrally controlling per-thread model/provider/feature defaults, and persistence of **device-key bindings in SQLite**.

### Marketplace Upgrade Endpoint

**What:** A new `marketplace/upgrade` JSON-RPC method lets a client refresh one or all Git-backed plugin marketplaces to their latest upstream revisions without the user having to remove and re-add them.

**Details:**
- Pass `{}` (or `{"marketplaceName": null}`) to upgrade every Git marketplace in `config.toml`; pass `{"marketplaceName": "<name>"}` to target just one.
- Returns the set of `selectedMarketplaces` it tried to upgrade, the `upgradedRoots` (absolute paths to roots that actually changed), and a list of per-marketplace `errors` so a single broken source does not abort the rest.
- The reported `upgradedRoots` is empty if every selected marketplace was already at the latest revision; the `last_revision` value in `config.toml` is updated on success.
- Errors carry both `marketplaceName` and a `message`, so clients can surface partial failures in their UI.

**Code references:**
- New types `MarketplaceUpgradeParams`, `MarketplaceUpgradeResponse`, and `MarketplaceUpgradeErrorInfo` in `codex-rs/app-server-protocol/src/protocol/v2.rs`
- New file `codex-rs/core-plugins/src/marketplace_upgrade/git.rs`
- End-to-end coverage in `codex-rs/app-server/tests/suite/v2/marketplace_upgrade.rs`
- New JSON schemas under `codex-rs/app-server-protocol/schema/json/v2/MarketplaceUpgrade*.json`


### Amazon Bedrock Model Provider

**What:** Codex now ships an `AmazonBedrockModelProvider` with a hardcoded catalog of three OpenAI models hosted on AWS Bedrock, and a corresponding `Account::AmazonBedrock` variant that surfaces in the account API.

**Details:**
- Bundled catalog includes `openai.gpt-5.4-cmb` (priority 0 / default), `openai.gpt-oss-120b`, and `openai.gpt-oss-20b`, all with a 128K-token context window.
- Each catalog entry advertises Low / Medium / High reasoning effort, text-only input, and parallel tool calls.
- Bedrock uses AWS auth instead of an OpenAI-style bearer token, so the provider returns a dedicated `ProviderAccount::AmazonBedrock` with no OpenAI credentials required.
- A `StaticModelsManager` exposes the bundled list when no remote `/models` endpoint is configured, so the catalog ships out of the box.

**Code references:**
- `codex-rs/model-provider/src/amazon_bedrock/catalog.rs` — hardcoded model entries and capabilities
- `AmazonBedrockModelProvider::new()` in `codex-rs/model-provider/src/amazon_bedrock/mod.rs`
- New `Account::AmazonBedrock {}` enum case in `codex-rs/app-server-protocol/src/protocol/v2.rs`
- Schema additions in `codex-rs/app-server-protocol/schema/json/v2/GetAccountResponse.json`


### `excludeTurns` Flag for Thread Fork and Resume

**What:** `thread/fork` and `thread/resume` now accept an `excludeTurns` boolean that returns thread metadata and live state without populating `thread.turns`.

**Details:**
- When `excludeTurns: true`, the response omits the (potentially large) ordered turn list and skips replaying restored `thread/tokenUsage/updated` events.
- Designed for clients that page history through `thread/turns/list` immediately after resuming or forking — those clients now avoid paying for turn rehydration twice.
- Fully backward compatible: defaults to `false`, preserving today's behavior.

**Example use:**
```json
{
  "method": "thread/resume",
  "params": {
    "threadId": "abc123",
    "excludeTurns": true
  }
}
```
…then call `thread/turns/list` with paging parameters.

**Code references:**
- `ThreadResumeParams` and `ThreadForkParams` in `codex-rs/app-server-protocol/src/protocol/v2.rs`
- Token-usage replay suppression covered in `codex-rs/app-server/src/codex_message_processor/token_usage_replay.rs` and `codex-rs/app-server/tests/suite/v2/thread_resume.rs`


### Experimental Remote Thread Config Endpoint

**What:** A new `experimental_thread_config_endpoint` config option lets Codex fetch per-thread model / provider / feature configuration from a remote gRPC service at session start, rather than from the local `config.toml`.

**Details:**
- The remote service implements the `codex.thread_config.v1.ThreadConfigLoader/Load` RPC; the new client uses `tonic` with a 5-second timeout.
- When the option is set, the in-process app-server swaps `NoopThreadConfigLoader` for `RemoteThreadConfigLoader::new(endpoint)`; otherwise behavior is unchanged.
- The remote can return either a `SessionThreadConfig` (model provider, model, features) for the active session, or signal that the default `UserThreadConfig` should be used.
- Marked experimental — the endpoint URL, schema, and protobuf message shapes may change.

**Example `config.toml`:**
```toml
experimental_thread_config_endpoint = "http://localhost:50051"
```

**Code references:**
- New `RemoteThreadConfigLoader` in `codex-rs/config/src/thread_config/remote.rs`
- Wired into `configured_thread_config_loader()` in `codex-rs/app-server-client/src/lib.rs`
- New protobuf at `codex-rs/config/src/thread_config/proto/codex.thread_config.v1.proto`
- Config field added in `codex-rs/core/src/config/mod.rs` and surfaced in `codex-rs/core/config.schema.json`


### Unix-Socket Transport for the App-Server

**What:** The `codex app-server` command now supports a `unix://` listen URI in addition to `stdio://`, `ws://`, and `off`, and a new `codex app-server proxy` subcommand connects stdio to a running app-server's Unix domain socket.

**Details:**
- `--listen unix://[/path]` opens a Unix socket (mode `0o600`) and serves WebSocket-framed JSON-RPC over it. Stale socket files are cleaned up on startup, and the server's own socket is removed on shutdown.
- An empty `unix://` (no path) falls back to a default control-socket path under `CODEX_HOME`.
- `codex app-server proxy [--sock <path>]` proxies the calling stdio to the running server's socket — useful when an editor or tool wants stdio I/O against a long-running daemon.

**Example:**
```bash
codex app-server --listen unix:///tmp/codex.sock
codex app-server proxy --sock /tmp/codex.sock
```

**Code references:**
- New `codex-rs/app-server/src/transport/unix_socket.rs` (with framing reused via `from_raw_socket(..., Role::Server)`)
- `AppServerProxyCommand` in `codex-rs/cli/src/main.rs`
- Listen-URI parsing extended in `codex-rs/app-server/src/main.rs`


### `codex debug trace-reduce` Subcommand

**What:** A new (hidden) debug command replays a rollout-trace bundle and writes a reduced JSON state file alongside it.

**Details:**
- Invocation: `codex debug trace-reduce <bundle> [--out <path>]`. The default output path is `<bundle>/state.json`.
- Pairs with the existing `replay_bundle()` Rust API now documented in the rollout-trace README.

**Code references:**
- Subcommand wiring in `codex-rs/cli/src/main.rs`
- README updates in `codex-rs/rollout-trace/README.md`


### First-Class Code Cell Tracing

**What:** A new `CodeCellTraceContext` records each Code Mode runtime cell — when it starts, the initial response, and when it ends — into the rollout trace.

**Code references:**
- New `codex-rs/rollout-trace/src/code_cell.rs`
- Wired through `ThreadTraceContext` in `codex-rs/rollout-trace/src/lib.rs`

### `PermissionProfile` Redesigned as a Tagged Union

**What changed:** Previously, `PermissionProfile` was a single struct with `Option<network>` and `Option<file_system>` fields. It is now a discriminated union with three explicit variants:

- `managed` — Codex constructs and enforces the sandbox itself (carries `fileSystem` and `network`).
- `disabled` — no outer sandbox is applied (replacement for the old "danger full access" path).
- `external` — a caller (for example, a cloud-agent shell) enforces filesystem isolation; Codex still tracks `network` policy.

**Why it matters for users:**
- The active permission view in `thread/start`, `thread/fork`, and `thread/resume` responses is no longer `null` for externally enforced sandboxes — clients can finally render the active policy in all cases (the schema description is now simply "Canonical active permissions view for this thread.").
- Per-command requests use a separate `AdditionalPermissionProfile` partial-overlay type, eliminating the previous overload of one struct meaning two different things.
- `Op::OverrideTurnContext` now carries the new `permission_profile` as the canonical view, with the legacy `sandbox_policy` retained as a projection so older clients keep working.
- Replacing the allow side of a policy no longer drops explicit `:none` deny rules — `preserve_deny_read_restrictions_from()` carries them forward.

**Code references:**
- New enum in `codex-rs/protocol/src/models.rs` (`PermissionProfile`, `ManagedPermissionProfile`, `ExternalPermissionProfile`, `SandboxEnforcement`)
- `AdditionalPermissionProfile` extracted into `codex-rs/protocol/src/models.rs`
- Round-trip helpers `from_legacy_sandbox_policy` / `to_legacy_sandbox_policy`
- `LegacyPermissionProfile` deserializer keeps old rollouts loadable
- TypeScript schema regenerated under `codex-rs/app-server-protocol/schema/typescript/v2/`


### Authentication Refactor for Backend Calls

**What changed:** Analytics, remote-control enrollment, WebSocket connect, the core HTTP client, and the plugin remote module all replaced ad-hoc `is_chatgpt_auth()` + bearer-token construction with a shared `auth.uses_codex_backend()` check and an `auth_provider.add_auth_headers()` / `to_auth_headers()` helper.

**Why it matters:**
- `uses_codex_backend()` now also accepts `AgentIdentity` and `ChatgptAuthTokens`, so analytics events, remote-control enrollment, and other backend calls work for those auth modes (previously they silently returned early for non-ChatGPT sessions).
- Auth headers are produced in one place, paving the way for richer auth schemes (signed authorization headers, agent identity) without touching every call site.

**Code references:**
- `codex-rs/login/src/auth/manager.rs` — `uses_codex_backend()`
- `codex-rs/analytics/src/client.rs:send_track_events()`
- `codex-rs/app-server/src/transport/remote_control/enroll.rs` and `websocket.rs`
- `codex-rs/core-plugins/src/remote.rs`, `codex-rs/core/src/client.rs`


### Device-Key Bindings Persisted in SQLite

**What changed:** Device-key ↔ account bindings are now stored in a new SQLite table instead of (or alongside) the platform key provider, and `DeviceKeyApi` operations are async.

**Details:**
- New migration creates `device_key_bindings(key_id, account_user_id, client_id, created_at, updated_at)`.
- `DeviceKeyStore::create()` writes the binding atomically and rolls back the platform key on binding-write failure.
- Provider operations now run via `spawn_blocking`, so platform-keychain access can no longer block the async runtime.
- A new `DeviceKeyBindingStore` async trait abstracts the storage backend.

**Code references:**
- `codex-rs/state/migrations/0028_device_key_bindings.sql`
- `codex-rs/device-key/src/lib.rs` (new async `DeviceKeyStore`)
- `StateDeviceKeyBindingStore` in `codex-rs/app-server/src/device_key_api.rs`


### Reasoning Token Counts in JSONL Exec Output

**What changed:** The `Usage` struct emitted by `codex exec --output-jsonl` and related event processors now includes `reasoning_output_tokens` per turn.

**Why it matters:** Tools that scrape exec output for token accounting can now break out reasoning tokens separately from total output tokens.

**Code reference:** `codex-rs/exec/src/exec_events.rs`


### Per-Turn Environments Survive Subagent Forks

**What changed:** `Op::UserInput` now accepts an `environments` field, and `TurnStartParams.environments` semantics are clarified — omitted means sticky, empty disables environments, non-empty selects environments for the turn (first wins).

**Why it matters:** Per-turn environment selections are now correctly carried through subagent spawns and other turn-context propagations.

**Code references:**
- `codex-rs/core/src/agent/control.rs`
- `TurnStartParams` in `codex-rs/app-server-protocol/src/protocol/v2.rs`


### Curated Plugin Cache Version Stability

**What changed:** Curated plugin cache versions now use the first 8 characters of a Git SHA rather than the full 40, reducing churn in version-derived paths and metadata.

**Code reference:** `curated_plugin_cache_version()` in `codex-rs/core-plugins/src/`


### CLI `--help` Now Reflects the Real Command Path

**What changed:** Plugin marketplace subcommands now declare `bin_name = "codex plugin marketplace …"`, so the rendered `--help` text matches the actual invocation path.

**Code reference:** `codex-rs/cli/src/marketplace_cmd.rs`


### TUI: Default Model Bumped to `gpt-5.5`

**What changed:** The default model surfaced in TUI status, picker, and snapshots moves from `gpt-5.4` to `gpt-5.5`.

**Why it matters:** New sessions started without an explicit model selection now default to the newer model.

**Code reference:** Snapshots under `codex-rs/tui/src/chatwidget/snapshots/`


### TUI: Permission Profile Threaded Through Session State

**What changed:** On `SessionConfigured`, the TUI now derives runtime filesystem and network policies from `event.permission_profile` (with the legacy `sandbox_policy` as a fallback). `set_sandbox_policy()` keeps the new fields in sync, and `ThreadSessionState` carries the permission profile so resume/fork preserves managed/external/disabled enforcement and `:none` deny rules.

**Why it matters:** Sandbox-policy overrides made via the TUI are now correctly preserved across forks and resumes; auto-review and feature-flag changes capture the live runtime sandbox.

**Code references:**
- `sync_runtime_permissions_from_legacy_sandbox_policy()` in `codex-rs/tui/src/app/config_persistence.rs`
- Session-state plumbing in `codex-rs/tui/src/app/thread_session_state.rs`
- New regression test `permission_settings_sync_preserves_active_profile_only_rules`


### TUI: Bounded Shutdown Round-Trip

**What changed:** Ctrl-C now bounds the app-server unsubscribe round-trip to 2 seconds before the TUI exits, so a misbehaving server can no longer hang shutdown.

**Code reference:** `codex-rs/tui/src/app/event_dispatch.rs`


### TUI: Updated Cyber-Safety Messaging

**What changed:** The cyber-safety warning copy was rewritten to point users to the new "Trusted Access for Cyber" program at `chatgpt.com/cyber`.

**Code reference:** `codex-rs/tui/src/chatwidget.rs`


### Windows-Friendly Marketplace Git Operations

**What changed:** A new `git_path_arg` / `strip_windows_verbatim_path_prefix` helper strips `\\?\` and `\\?\UNC\` prefixes from canonicalized Windows paths before they are passed to `git -C`, `git clone`, and friends.

**Why it matters:** Marketplace add / remove / upgrade now works reliably on Windows even when the path comes back from `canonicalize` with a verbatim prefix that Git cannot parse.

**Code reference:** `codex-rs/core-plugins/src/marketplace_upgrade/git.rs`


### Rollout-Trace README and Architecture

**What changed:** The rollout-trace README now contains a stronger privacy warning ("can contain prompts, responses, tool inputs/outputs, terminal output, and paths"), documents the move from a single `RolloutTraceRecorder` to a tree-aware `ThreadTraceContext` (with disabled contexts no-oping), and references the new `replay_bundle()` API and `codex debug trace-reduce` CLI.

**Code reference:** `codex-rs/rollout-trace/README.md`

### Permission View No Longer Lost for External Sandboxes

The "active permissions" view returned in `thread/start`, `thread/fork`, and `thread/resume` responses was previously documented as `null` for externally enforced sandboxes because external policies could not round-trip as a `PermissionProfile`. With the new tagged-union `PermissionProfile` (including the explicit `external` variant), the canonical view now round-trips correctly and clients can render it in all cases. (See the schema description change from "…null for external sandbox policies because external enforcement cannot be round-tripped…" to "Canonical active permissions view for this thread.")


### Deny-Read Restrictions Preserved Across Sandbox Resyncs

When the TUI updated the active sandbox policy (for example after a feature-flag change or auto-review), explicit `:none` deny entries on the file-system policy could be silently dropped. The new `preserve_deny_read_restrictions_from()` helper carries those entries forward when the allow side of a policy is replaced, and a regression test (`permission_settings_sync_preserves_active_profile_only_rules`) guards the behavior.

**Code references:**
- `codex-rs/protocol/src/permissions.rs`
- `codex-rs/tui/src/app/thread_session_state.rs`


### Analytics Events Now Sent for All Codex-Backend Auth Modes

Analytics tracking previously bailed out unless `auth.is_chatgpt_auth()` returned true and an account ID was present, which excluded `ChatgptAuthTokens` and `AgentIdentity` sessions even though they share the same backend. The new `uses_codex_backend()` check correctly admits those modes, and the bearer + account-id headers are produced uniformly via `auth_provider.to_auth_headers()`.

**Code reference:** `codex-rs/analytics/src/client.rs`


### Async Device-Key Operations Stop Blocking the Tokio Runtime

Platform-keychain calls invoked from `DeviceKeyStore` previously ran on the async executor; they are now wrapped in `spawn_blocking`, eliminating a class of stalls when the keychain or HSM was slow to respond. Binding writes are also rolled back atomically if the platform key creation succeeded but the SQLite binding write failed, removing a window where a bound key could exist without a binding row.

**Code reference:** `codex-rs/device-key/src/lib.rs`


### Marketplace Git Operations Work on Windows Verbatim Paths

`git` rejects paths with `\\?\` or `\\?\UNC\` verbatim prefixes. Codex now strips those prefixes before invoking Git for marketplace add / remove / upgrade, fixing a Windows-only failure mode where canonicalized paths could not be passed to Git.

**Code reference:** `codex-rs/core-plugins/src/marketplace_upgrade/git.rs`
