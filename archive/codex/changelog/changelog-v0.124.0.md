# Changelog for version 0.124.0

## Highlights

This release replaces the legacy `sandbox` enum with a richer `permissionProfile` model that flows through every thread, turn, and `command/exec` call, ships a brand-new agent-bound auth scheme (`agentIdentity`) and AWS SigV4 stack for Amazon Bedrock, and renames the Guardian subagent to `auto_review` with a circuit-breaker, denial-approval flow, and per-turn strict re-review. New protocol surfaces include `model/verification` (cyber-policy account checks), `guardianWarning`, `thread/approveGuardianDeniedAction`, multi-cwd thread filters, declarative managed hooks requirements, and a new `rollout-trace` crate that records a deterministic raw-trace bundle alongside every rollout.

### `permissionProfile` overrides for threads, turns, and one-off commands
**What:** Threads, resumes, forks, turns, and the v2 `command/exec` request now accept a `permissionProfile` object that describes file-system entries (with absolute paths, special paths like `cwd`/`tmpdir`/`project_roots`, and per-entry access mode) and a network-permission toggle, replacing the binary `sandbox` enum where richer overrides are needed.

**Details:**
- `permissionProfile` cannot be combined with the legacy `sandbox` (or `sandboxPolicy` for `command/exec`) — sending both returns an `InvalidRequest` JSON-RPC error with the message ``permissionProfile` cannot be combined with `sandbox`/`sandboxPolicy``.
- `ThreadStartResponse`, `ThreadResumeResponse`, and `ThreadForkResponse` now return both the legacy `sandbox` field and a canonical `permissionProfile`. The new field is `null` for external sandbox enforcement that cannot round-trip into a profile.
- The shape includes `PermissionProfileFileSystemPermissions { entries, globScanMaxDepth }` and `PermissionProfileNetworkPermissions { enabled }`. Entries reference `FileSystemSandboxEntry` / `FileSystemPath` (with new `kind`s like `root`, `minimal`, `current_working_directory`, `project_roots`, `tmpdir`, `slash_tmp`, and `unknown`) and a `FileSystemAccessMode` of `read`, `write`, or `none`.
- For `command/exec`, the request's `cwd` becomes the effective sandbox cwd when a `permissionProfile` is supplied (otherwise the configured server cwd is used), and the runtime preserves any pre-configured deny-read entries that the override didn't already include.

**Code references:** `permissionProfile` field in `app-server-protocol/src/protocol/v2.rs`, `command_exec()` and `preserve_configured_deny_read_restrictions()` in `app-server/src/codex_message_processor.rs`, `from_legacy_sandbox_policy()` and `to_legacy_sandbox_policy()` on `PermissionProfile` in `protocol/src/models.rs`.


### `agentIdentity` auth mode and the `codex-agent-identity` crate
**What:** A new authentication mode lets Codex authenticate to ChatGPT as a registered agent identity using ed25519 signed `AgentAssertion` headers and a per-task registration handshake, suitable for programmatic Codex deployments.

**Details:**
- Added a new top-level `agent-identity` workspace crate with key generation (`generate_agent_key_material()`), assertion building (`authorization_header_for_agent_task()`), task registration (`register_agent_task()`), and request-id helpers.
- Keys are stored as PKCS#8 base64 strings and signed assertions are URL-safe base64 envelopes containing `agent_runtime_id`, `task_id`, `timestamp`, and a base64 signature; mismatched runtime/task pairs are rejected explicitly.
- Encrypted task IDs returned from the registration endpoint are decrypted in-process with a Curve25519 secret derived from the signing key (`decrypt_task_id_response()`).
- `AuthMode` (and `CoreAuthMode`) gain an `AgentIdentity` variant; `getAuthStatus` and `account/read` now return `agentIdentity` accounts and avoid surfacing access tokens for them.
- The `chatgpt_base_url` is normalized so that suffixes like `/wham/remote/control/server[/enroll]` and `/codex` are stripped before appending `/backend-api`, making the same configuration usable for OAuth, agent identity, and remote-control flows.

**Code references:** new crate `codex-rs/agent-identity/src/lib.rs` (`AgentIdentityKey`, `authorization_header_for_agent_task()`, `register_agent_task()`, `normalize_chatgpt_base_url()`); `AuthMode::AgentIdentity` in `app-server-protocol/src/protocol/v2.rs`; agent-identity wiring in `login/src/auth/agent_assertion.rs` and `login/src/auth/agent_identity.rs`.


### `codex-rollout-trace` crate and trace-bundle recording
**What:** A new workspace crate records a deterministic, append-only trace bundle for every rollout — raw inference attempts, compaction checkpoints, raw payload refs, and replay-ready reduced models — so semantic replay and viewer projections live outside `codex-core`.

**Details:**
- Hot-path hooks (`InferenceTraceContext`, `InferenceTraceAttempt`, `CompactionTraceContext`, `CompactionCheckpointTracePayload`) record events without blocking the chat loop; the `RolloutTraceRecorder` is a no-op when disabled.
- Local recording is gated by the `CODEX_ROLLOUT_TRACE_ROOT_ENV` environment variable (`CODEX_ROLLOUT_TRACE_ROOT`). When set, every rollout writes a `trace.jsonl` bundle plus a conventional reduced-state cache file (`REDUCED_STATE_FILE_NAME`).
- The reducer (`replay_bundle()`) produces a `RolloutTrace` with first-class types for conversation items (`ConversationItem`, `ConversationRole`, `ConversationChannel`, `ConversationItemKind`), inference calls (`InferenceCall` with `TokenUsage`), code cells, tool calls, and runtime-vs-model-visible separation.
- New session and runtime models distinguish reasoning summaries from raw reasoning, preserve encrypted reasoning blobs as `Encoded` parts, and surface `code-mode` runtime tool calls with stable IDs.

**Code references:** crate root `codex-rs/rollout-trace/src/lib.rs`; reducer in `codex-rs/rollout-trace/src/reducer/mod.rs`; recorder in `codex-rs/rollout-trace/src/recorder.rs`; downstream wiring in `core/src/session/session.rs` (`inherited_rollout_trace`).


### Amazon Bedrock SigV4 auth and configurable region
**What:** A new `aws-auth` crate provides AWS SigV4 request signing with credential resolution, and the built-in `amazon-bedrock` provider now accepts an `aws.region` override in addition to `aws.profile`.

**Details:**
- `AwsAuthContext::load(AwsAuthConfig { profile, region, service })` resolves the SDK credential chain (including the `AWS_PROFILE` and explicit profile overrides) and signs outbound requests via `AwsAuthContext::sign(AwsRequestToSign)`, returning `AwsSignedRequest` with `Authorization`, `X-Amz-Date`, and friends populated.
- The Bedrock provider now uses the bearer token from `AWS_BEARER_TOKEN_BEDROCK` when present and falls back to SigV4 signing through the AWS SDK; the runtime resolves the configured region via `region_from_config()` and routes to `bedrock-mantle.<region>.api.aws/v1`.
- The merge logic for the built-in Bedrock provider is now ``aws.profile` and `aws.region`; other non-default provider fields are not supported`, so additional fields still error out.
- The `[model_providers.amazon-bedrock.aws]` TOML table accepts a new optional `region = "us-west-2"` key.

**Code references:** new crate `codex-rs/aws-auth/src/lib.rs` (with `config.rs` and `signing.rs`); provider modules `model-provider/src/amazon_bedrock/{auth,mantle,mod}.rs`; `merge_configured_model_providers()` in `model-provider-info/src/lib.rs`.


### `model/verification` notification (cyber trusted-access)
**What:** The v2 server can now emit a `model/verification` notification when the backend flags additional account verification, such as `trustedAccessForCyber`, so clients can prompt the user out-of-band.

**Details:**
- New types `ModelVerification` (currently the single value `trustedAccessForCyber`) and `ModelVerificationNotification { threadId, turnId, verifications }`.
- The notification is forwarded to the client when `EventMsg::ModelVerification` arrives; a corresponding `cyberPolicy` variant was added to `CodexErrorInfo` so unverified accounts surface a structured error.
- The bundled cyber-policy error event renders in the TUI with a dedicated narrow- and wide-terminal snapshot (`cyber_policy_error_event_*`).

**Code references:** `ModelVerificationNotification` in `app-server-protocol/src/protocol/v2.rs`; routing in `apply_bespoke_event_handling()` in `app-server/src/bespoke_event_handling.rs`; TUI rendering in `tui/src/history_cell.rs`.


### `guardianWarning` notification and `thread/approveGuardianDeniedAction` request
**What:** The v2 protocol gained a notification for concise guardian warnings ("guardian flagged that …") and a new client-initiated request that lets the user override a guardian denial.

**Details:**
- `GuardianWarningNotification { threadId, message }` is emitted on `EventMsg::GuardianWarning` and surfaced in v2 clients.
- `thread/approveGuardianDeniedAction` accepts the original serialized `GuardianAssessmentEvent` plus the target `threadId`; the server submits an `Op::ApproveGuardianDeniedAction` so the previously denied action is allowed to proceed.
- The guardian also got a per-turn circuit breaker: after `MAX_CONSECUTIVE_GUARDIAN_DENIALS_PER_TURN` (3) consecutive denials or `MAX_TOTAL_GUARDIAN_DENIALS_PER_TURN` (10) total denials it interrupts the turn instead of fighting the model indefinitely.

**Code references:** `GuardianWarningNotification` and `ThreadApproveGuardianDeniedActionParams` in `app-server-protocol/src/protocol/v2.rs`; `thread_approve_guardian_denied_action()` in `app-server/src/codex_message_processor.rs`; `GuardianRejectionCircuitBreaker` in `core/src/guardian/mod.rs`.


### Strict auto-review (`strictAutoReview`) per-turn flag
**What:** Permissions request approvals can now opt every subsequent command in the same turn into a forced auto-review pass, so the guardian re-evaluates each command before it runs sandboxed.

**Details:**
- `PermissionsRequestApprovalResponse` and the v2 `command/exec` family added a `strictAutoReview: boolean` field.
- The server only honors `strictAutoReview = true` for **turn-scoped** grants; combining it with `Session` scope falls back to a default empty turn-scoped grant and logs an error (`strict auto review is only supported for turn-scoped permission grants`).
- The same field is mirrored across `CoreRequestPermissionsResponse` and analytics so dashboards can see when strict auto-review was active.

**Code references:** `strict_auto_review` field in `protocol/src/request_permissions.rs`; validation in `request_permissions_response_from_client_result()` in `app-server/src/bespoke_event_handling.rs`.


### `auto_review.policy` config option
**What:** `~/.codex/config.toml` accepts a new `[auto_review]` table whose `policy` string is appended into the guardian prompt to customize the auto-reviewer's risk posture.

**Details:**
- Schema-validated by `AutoReviewToml` (single optional `policy` field).
- The string flows through the resolved config, the guardian prompt builder, and the guardian-prompt snapshot tests so updates are visible immediately.

**Code references:** `AutoReviewToml` in `config/src/config_toml.rs`; schema entry in `core/config.schema.json`; merge in `core/src/config/mod.rs`.


### Multi-cwd `thread/list` filter and `useStateDbOnly`
**What:** `thread/list` now accepts either a single string or an array of strings for `cwd`, plus a new `useStateDbOnly` flag to skip JSONL rollout repair.

**Details:**
- The `cwd` parameter is now `ThreadListCwdFilter` — `string | string[] | null`. When an array is provided, only threads whose session cwd exactly matches one of the listed paths are returned.
- `useStateDbOnly: true` returns rows directly from the local state DB without scanning JSONL rollouts to repair thread metadata. Default is `false`, preserving the existing scan-and-repair behavior.
- Backed by two new SQLite indexes (migration `0027_threads_cwd_sort_indexes.sql`): `idx_threads_archived_cwd_created_at_ms` and `idx_threads_archived_cwd_updated_at_ms`, both over `(archived, cwd, *_at_ms DESC, id DESC)` for fast cwd-filtered list paging.

**Code references:** `ThreadListCwdFilter` and `ThreadListParams.useStateDbOnly` in `app-server-protocol/src/protocol/v2.rs`; `normalize_thread_list_cwd_filters()` in `app-server/src/codex_message_processor.rs`; new migration `state/migrations/0027_threads_cwd_sort_indexes.sql`.


### Declarative `managed_hooks` requirements (`configRequirements/read.hooks`)
**What:** The new experimental `hooks` field on `ConfigRequirements` exposes the directory layout and matcher groups Codex expects so external tooling can configure managed hooks correctly.

**Details:**
- New shapes: `ManagedHooksRequirements { managedDir, windowsManagedDir, PreToolUse, PermissionRequest, PostToolUse, SessionStart, UserPromptSubmit, Stop }`, `ConfiguredHookMatcherGroup { matcher, hooks }`, and `ConfiguredHookHandler` (a tagged union of `command { command, timeoutSec, async, statusMessage }`, `prompt`, and `agent`).
- The TOML config now accepts a top-level `[hooks]` table or a separate `hooks.toml` file, parsed via `HookEventsToml` / `HooksFile`.
- Hooks pulled from managed directories are validated against the requirement set; drift between the constraint manifest and the active config is rejected (`managed_hooks_constraint_rejects_drift` test).

**Code references:** `ManagedHooksRequirements`, `ConfiguredHookMatcherGroup`, `ConfiguredHookHandler` in `app-server-protocol/src/protocol/v2.rs`; `HookEventsToml` in `config/src/hook_config.rs`; `map_hooks_requirements_to_api()` in `app-server/src/config_api.rs`.


### TurnEnvironment / multi-environment exec
**What:** The exec-server now models multiple named environments (`local`, `remote`) under one manager, and `turn/start` accepts a per-turn `environments` list (`{ environmentId, cwd }`) so a single turn can target a non-default execution environment.

**Details:**
- Replaced the single-environment `EnvironmentManager::new(exec_server_url)` with `EnvironmentManager::new(EnvironmentManagerArgs { exec_server_url, local_runtime_paths })`. The manager always exposes `LOCAL_ENVIRONMENT_ID = "local"` and adds `REMOTE_ENVIRONMENT_ID = "remote"` when `CODEX_EXEC_SERVER_URL` is set.
- `TurnStartParams.environments: Vec<TurnEnvironmentParams>` is gated by the experimental key `turn/start.environments` and round-trips through `experimental_reason()`.
- `Environment` now bundles `exec_backend`, `filesystem`, and `http_client` for clean per-environment swapping; tests use the new `EnvironmentManager::default_for_tests()`.

**Code references:** `EnvironmentManagerArgs` and `Environment::{local, remote, default_for_tests}` in `exec-server/src/environment.rs`; `TurnEnvironmentParams` in `app-server-protocol/src/protocol/v2.rs`.


### `device/key/sign` payload variants for remote-control flows
**What:** A new device-key API (`codex-device-key`) backs `device/key/{create, public, sign}` requests with hardware-protected signing for remote-control client connection and enrollment payloads.

**Details:**
- Hardware-only protection is the default; clients can request `AllowOsProtectedNonextractable` to fall back to OS-protected non-extractable keys (which then error with `DegradedProtectionNotAllowed` if the policy disallows it).
- Sign payloads currently include `RemoteControlClientConnection` (binds an existing websocket challenge to the enrolled device without signing the bearer token) and `RemoteControlClientEnrollment` (binds an enrollment challenge); both validate the `audience` enum and surface granular error codes.
- The signing API is intentionally not an arbitrary-byte signer.

**Code references:** `DeviceKeyApi` in `app-server/src/device_key_api.rs`; `DeviceKeySignPayload` and `DeviceKeyProtectionPolicy` in `app-server-protocol/src/protocol/v2.rs`; remote-control wiring in `app-server/src/transport/remote_control/`.


### `imagegen` skill: built-in transparent-image workflow
**What:** The bundled `imagegen` skill grew a "built-in first" transparent-output workflow with a new local helper that strips a flat chroma-key background to alpha, plus updated guidance for when to ask before falling back to CLI `gpt-image-1.5`.

**Details:**
- Added `scripts/remove_chroma_key.py` (440 lines) that auto-samples the key color from image borders, soft-mattes the alpha, and applies despill for antialiased edges.
- Updated `SKILL.md`, `references/cli.md`, `references/image-api.md`, and `references/sample-prompts.md` to describe the chroma-key workflow, document that `gpt-image-2` does not support `background=transparent`, and require explicit confirmation before silently downgrading to `gpt-image-1.5`.
- Added a `default_prompt: "Use $imagegen to make or edit an image for this project."` to `agents/openai.yaml`.

**Code references:** new `skills/src/assets/samples/imagegen/scripts/remove_chroma_key.py`; updated `skills/src/assets/samples/imagegen/SKILL.md`.


### Terminal-title and status-line setup tokens
**What:** The terminal-title and status-line setup popups support many more variables, with stable canonical IDs that accept the older short aliases for compatibility.

**Details:**
- New tokens: `current-dir`, `context-remaining`, `context-used` (alias `context-usage`), `five-hour-limit`, `weekly-limit`, `codex-version`, `used-tokens`, `total-input-tokens`, `total-output-tokens`, `session-id`, `fast-mode`, and `model-with-reasoning`.
- Existing tokens were renamed to canonical forms with legacy aliases: `project` → `project-name`, `status` → `run-state`, `thread` → `thread-title`, `model` → `model-name`. Old configurations continue to parse.

**Code references:** `TerminalTitleItem` and `parse_terminal_title_items()` in `tui/src/bottom_pane/title_setup.rs`.

### `ApprovalsReviewer::guardian_subagent` renamed to `auto_review`
The TOML/JSON value for the guardian reviewer is now `auto_review`. The legacy `guardian_subagent` value is still accepted as an alias on input, but new schemas, telemetry, and prompts emit `auto_review`. Analytics fact `approvals_reviewer` correspondingly serializes as `"auto_review"`. The user-facing description for the reviewer was updated everywhere it appears in the JSON-RPC schemas.


### Backend client centralizes auth header construction
`BackendClient` gained `from_auth(base_url, &auth)` which assembles the authorization header, account ID, fedramp routing flag, and user agent in one place. The `AuthorizationHeaderAuthProvider` shim was removed; analytics and rate-limit calls now go through the same helper, so AgentIdentity, ChatGPT OAuth, ChatGPT auth tokens, and FedRAMP all funnel through one path. Analytics events now use `bearer_auth(access_token)` directly instead of pre-built header strings.


### `model_providers.amazon-bedrock.aws.region` is honored end-to-end
Region selection now flows from the `[aws]` TOML table → `ModelProviderAwsAuthInfo.region` → SigV4 signing context → endpoint URL. Setting a region without a profile is supported, and the merged-error message was updated to reflect both supported keys.


### Plugin/marketplace remote sources
`PluginDetail.marketplacePath` and `SkillSummary.path` are now `Option`-typed because plugins can be served from a remote marketplace. `marketplace/add` and `plugin/{read, install}` accept `marketplaceName` (remote) in addition to `marketplacePath`, and there is a new `remote_plugin` experimental feature flag for opting in.


### Approval overlay snapshots, footer hints, and chat composer
Snapshots covering the approval overlay permissions prompt, footer mode shortcuts, the status-line setup popup, and the terminal-title setup popup were refreshed for the new tokens, the renamed reviewer, and the new permission profile fields.


### `codex-rmcp-client` HTTP client adapter
A new `StreamableHttpClientAdapter` lets the rmcp client run over the shared `codex-exec-server` `HttpClient`, removing the inline SSE plumbing from `rmcp_client.rs` and unblocking remote-resource and streamable-HTTP recovery tests. `program_resolver::resolve()` now takes the `cwd` as an explicit argument instead of probing `std::env::current_dir()`, which matters on Windows where launchers like `npx`/`pnpm`/`yarn` resolved paths against the wrong directory.


### `AdditionalFileSystemPermissions.read`/`write` deprecated in favor of `entries`
The `read` and `write` arrays are now annotated `"This will be removed in favor of `entries`."` in every schema. The runtime conversion to `CoreFileSystemPermissions` populates `entries` automatically when only the legacy fields are present, so existing clients continue to work while migrating to the entry-based shape.


### `getAuthStatus`, `account/read`, and rate-limits routing for AgentIdentity
- `getAuthStatus` returns `(authMethod: agentIdentity, token: None)` when an agent identity is active, since access tokens for agent identities are not surfaced.
- `account/read` now treats `Chatgpt`, `ChatgptAuthTokens`, and `AgentIdentity` together so plan-type and email lookups apply to all ChatGPT-style credentials.
- The rate-limits read path was reworked to use `BackendClient::from_auth`, eliminating manual header construction.


### Personality & GPT‑5.4 / "openai-docs" skill rewrite
The bundled `openai-docs` skill was rewritten around fetching `https://developers.openai.com/api/docs/guides/latest-model.md` and a new `references/upgrade-guide.md` (renamed from `upgrading-to-gpt-5p4.md`). It now distinguishes general docs lookup, model-selection, model-string upgrades, prompt-upgrade guidance, and broader migrations; bundles `references/prompting-guide.md` and `scripts/resolve-latest-model-info.js` as offline fallbacks; and explicitly forbids SDK/auth/provider-environment migrations during a model-and-prompt upgrade.


### Remote control transport refactor
`start_remote_control_with_options` was renamed to `start_remote_control` with positional arguments, and a new `ConnectionOrigin` enum (with a `WebSocket` variant) lets request handlers reject device-key signing when the origin is a remote websocket connection. Connection tracking, enrollment, and protocol modules were reorganized under `transport/remote_control/` accordingly.


### Guardian network-access trigger context
`GuardianApprovalRequest::NetworkAccess` now carries an optional `GuardianNetworkAccessTrigger` with the originating call ID, tool name, command, cwd, sandbox permissions, additional permissions, justification, and tty flag. The serialized approval action and the analytics fact (`GuardianReviewedAction::NetworkAccess`) include this trigger so reviewers can see the originating tool call. `format_guardian_action_pretty()` now returns `FormattedGuardianAction { text, truncated }` so the UI can flag truncated actions.


### `fast_default_opt_out` notice
`UserNotices.fast_default_opt_out` (also exposed as `SetNoticeFastDefaultOptOut(bool)` config edit) records when the user opted out of Codex-managed fast defaults; setting `service_tier = null` explicitly toggles the opt-out so subsequent runs respect the choice.


### Experimental feature flags expanded
`experimentalFeature/list` and `ExperimentalFeaturesConfig` learned new flags: `browser_use`, `computer_use`, `in_app_browser`, and `remote_plugin`. The `use_agent_identity` flag was removed because agent identity is now first-class auth rather than an experiment toggle.


### `command/exec` honors deny-read entries from the configured policy
When a request supplies an explicit `permissionProfile`, the server now layers in any `FileSystemAccessMode::None` (deny-read) entries from the configured sandbox policy that the override didn't already include, so per-command overrides cannot accidentally unblock paths the user globally denied (`preserve_configured_deny_read_restrictions()` in `app-server/src/codex_message_processor.rs`).


### Analytics: track guardian review with separate context vs. result
`AnalyticsEventsClient::track_guardian_review` now takes a `(GuardianReviewTrackContext, GuardianReviewAnalyticsResult)` pair; the context can be reused across the lifecycle of a review without rebuilding event params, and the resulting events match the new `auto_review` reviewer name.

### Strict auto-review combined with session scope no longer leaks Session permissions
If a client sent `strictAutoReview: true` with `scope: Session`, the previous behavior would have silently honored the session-wide grant. The server now returns a default turn-scoped, empty grant and logs `strict auto review is only supported for turn-scoped permission grants`, preventing accidental long-lived auto-approvals (`request_permissions_response_from_client_result()` in `app-server/src/bespoke_event_handling.rs`).


### `program_resolver::resolve` uses the caller's cwd on Windows
Previously the resolver called `std::env::current_dir()` directly, which races against directory changes elsewhere in the process. It now takes an explicit `cwd: &Path`, so `which::which_in` always searches relative to the caller-supplied directory (`program_resolver::resolve()` in `rmcp-client/src/program_resolver.rs`).


### Bedrock provider validates `aws.region` before merging
Configured Bedrock providers that set non-default fields beyond `aws.profile` and `aws.region` now produce the explicit error ``model_providers.amazon-bedrock only supports changing `aws.profile` and `aws.region`; other non-default provider fields are not supported`` instead of silently accepting profile-only overrides (`merge_configured_model_providers()` in `model-provider-info/src/lib.rs`).


### Cyber-policy errors render correctly in narrow terminals
The TUI history-cell now has dedicated snapshots for `cyber_policy_error_event` in both narrow and wide widths, ensuring the new `cyberPolicy` `CodexErrorInfo` variant doesn't truncate or wrap incorrectly (`tui/src/history_cell.rs` and the matching `.snap` files).


### `RolloutItem::SessionState` removed from rollout extraction paths
The rollout extractor and dynamic-tool reader no longer match a stale `RolloutItem::SessionState` arm; thread-metadata calculations now correctly fall through to the catch-all `false` branch and dynamic tools are read from `SessionMeta` only (`apply_rollout_item()` and `extract_dynamic_tools()` in `state/src/extract.rs` and `state/src/runtime/threads.rs`).


### Permission grants normalize `cwd_filters` plumbing
Memory and thread runtime queries now thread `cwd_filters: None` through the request shape, eliminating an inconsistency where the SQL builder expected the field but the in-memory paths skipped it (`state/src/runtime/threads.rs`, `state/src/runtime/memories.rs`).
