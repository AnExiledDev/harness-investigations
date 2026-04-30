# Changelog for version 0.123.0

## Highlights

This release lays down the protocol surface for **hardware-backed device identity** that future Codex clients will use to authenticate to OpenAI's remote-control service. It also ships a streaming **patch-update notification** so app-server clients can render apply_patch progress in real time, and refines the TUI's `/status-line` and `/title` setup popups to preview against your **actual live runtime values** (branch, model, thread title) instead of hardcoded placeholders. Under the hood, a new `codex-uds` crate consolidates Unix Domain Socket plumbing, the chat composer gains a dedicated **bash mode** for `!`-prefixed shell commands, and remote-control transport gains FedRAMP-aware authentication.

### Device key protocol surface (`device/key/{create, public, sign}`)
**What:** A new family of v2 app-server JSON-RPC methods for managing a hardware-backed cryptographic device identity. The keys are intended to live in a secure store (Apple Secure Enclave, TPM, or OS-protected non-extractable fallback) and sign structured proofs that authenticate the Codex client to the remote-control service.

**Details:**
- Three methods are added in `protocol/v2.rs`: `device/key/create` (generate a new key), `device/key/public` (export the SubjectPublicKeyInfo DER + algorithm + protection class), and `device/key/sign` (sign a structured payload).
- `DeviceKeyAlgorithm` is currently fixed to `ecdsa_p256_sha256` (P-256 ECDSA over SHA-256).
- `DeviceKeyProtectionClass` enumerates `hardware_secure_enclave` (key-id prefix `dk_hse_`), `hardware_tpm` (`dk_tpm_`), and `os_protected_nonextractable` (`dk_osn_`, marked degraded).
- `DeviceKeyProtectionPolicy` lets callers pick `hardware_only` (rejects degraded classes) or `allow_os_protected_nonextractable` (accepts all three).
- The signer refuses arbitrary bytes — only the `DeviceKeySignPayload` enum is accepted, with two variants: `RemoteControlClientConnection` (for opening the remote-control websocket) and `RemoteControlClientEnrollment` (for the initial enrollment handshake). All signed bytes are wrapped in a `codex-device-key-sign-payload/v1` JSON envelope before reaching the platform signer.
- Allowed websocket and enrollment paths are pinned (`/api/codex/remote/control/client[/enroll]` and `/wham/remote/control/client[/enroll]`); the proof TTL is capped at 15 minutes (`MAX_REMOTE_CONTROL_DEVICE_KEY_PROOF_TTL_SECONDS`).
- **Caveat:** `codex-rs/device-key/src/platform.rs` ships only `UnsupportedDeviceKeyProvider`, which returns `HardwareBackedKeysUnavailable`/`KeyNotFound` for everything. This release is the protocol/schema surface plus a `MemoryProvider` test double — no production platform binding is wired up yet.

**Code references:** new crate in `codex-rs/device-key/src/lib.rs` and `device-key/src/platform.rs`; protocol surface in `protocol/v2.rs` (`device_key_create_request`, `device_key_public_request`, `device_key_sign_request`); message routing stub in `app_server/src/codex_message_processor.rs`.


### `item/fileChange/patchUpdated` streaming notification
**What:** A new server-to-client notification that emits incremental snapshots of the file-change set as `apply_patch` is being processed, letting clients render live patch progress between `PatchApplyBegin` and `PatchApplyEnd`.

**Details:**
- New `FileChangePatchUpdatedNotification { thread_id, turn_id, item_id, changes: Vec<FileUpdateChange> }` notification, dispatched on `EventMsg::PatchApplyUpdated`.
- Gated by the existing feature flag `features.apply_patch_streaming_events`. When enabled, clients receive structured file-change snapshots parsed from the model-generated patch before it finishes executing.
- The original tool `call_id` is reused as the `item_id` so clients can correlate updates to the originating tool call.

**Code references:** `FileChangePatchUpdatedNotification` in `app-server-protocol/src/protocol/v2.rs`; emit site mapped through `app-server/src/bespoke_event_handling.rs` for `EventMsg::PatchApplyUpdated`; schemas in `schema/json/v2/FileChangePatchUpdatedNotification.json` and `schema/typescript/v2/FileChangePatchUpdatedNotification.ts`.


### Bash mode in the chat composer (`!` prefix)
**What:** The TUI chat composer now treats a leading `!` as a dedicated bash-mode prompt indicator rather than a literal character — much like a shell REPL. When you start a line with `!`, the bang becomes a prompt-state marker, the slash-command popup is suppressed, and the rest of the buffer is treated as a shell command.

**Details:**
- A new `is_bash_mode: bool` flag on `ChatComposer` is synced from the canonical text via `sync_bash_mode_from_text`. Slash-command popups and dispatch are disabled while bash mode is active (`if !self.slash_commands_enabled() || self.is_bash_mode`).
- `current_text()` re-prepends the `!` for canonical serialization, but the textarea itself doesn't store it — so cursor positions, history rehydration, and import flows transparently absorb/restore the prefix via `imported_text_for_textarea` and `shift_text_element`.
- Verified by the new snapshot `codex_tui__bottom_pane__chat_composer__tests__footer_mode_shell_command_absorbs_bang.snap`.

**Code references:** `is_bash_mode`, `imported_text_for_textarea()`, `current_text()`, `try_dispatch_bare_slash_command()` in `tui/src/bottom_pane/chat_composer.rs`.


### `/mcp verbose` subcommand
**What:** The existing `/mcp` slash command grew a `verbose` modifier that requests the full MCP inventory from the app-server instead of the default summary view.

**Details:**
- The `/mcp` help text now reads "list configured MCP tools; use /mcp verbose for details".
- New routing in chat-widget slash-dispatch: `SlashCommand::Mcp` matches a trailing `verbose` argument and triggers a verbose inventory render path.
- New rendered snapshot `codex_tui__history_cell__tests__mcp_tools_output_from_statuses_renders_verbose_inventory.snap` shows the full per-tool output.

**Code references:** `SlashCommand::Mcp` arm in `tui/src/chatwidget/slash_dispatch.rs`; description in `tui/src/slash_command.rs`.


### `codex-uds` crate (cross-platform Unix Domain Socket helpers)
**What:** A new internal crate that consolidates UDS plumbing across Unix and Windows backends so binaries like `stdio-to-uds` no longer maintain their own `cfg(unix)`/`cfg(windows)` shims.

**Details:**
- Crate name `codex-uds` (lib `codex_uds`).
- Public API: `prepare_private_socket_directory` (enforces 0o700 directory permissions), `is_stale_socket_path`, `UnixListener::bind`/`accept`, `UnixStream::connect` — all implementing tokio `AsyncRead`/`AsyncWrite`.
- Unix uses `tokio::net::Unix{Listener,Stream}` directly. Windows uses `uds_windows` + `async-io` + `tokio-util::compat` for AFUNIX-on-Windows.

**Code references:** new crate in `codex-rs/uds/Cargo.toml` and `uds/src/lib.rs`. Consumed by `stdio-to-uds/src/lib.rs`, which was rewritten to be `async fn run` (replacing a sync `thread::spawn` + std `UnixStream` implementation) and uses `tokio::try_join!` for bidirectional copy.


### Streaming HTTP body responses through exec-server
**What:** A new client module that consumes streaming HTTP response bodies through the exec-server protocol — useful for proxying long-running HTTP requests where the body arrives in chunks.

**Details:**
- New `HttpResponseBodyStream` reads from an `mpsc::Receiver<HttpRequestBodyDeltaNotification>`, detects sequence-number gaps, handles a terminal `done` frame, and surfaces failures via `take_http_body_stream_failure`.
- Channel capacity is fixed to `HTTP_BODY_DELTA_CHANNEL_CAPACITY = 256`.
- Implements EOF semantics so callers can use it as an `AsyncRead`-compatible stream.

**Code references:** new file `exec-server/src/client/http_client.rs`; built on existing `HttpRequestParams` / `HttpRequestResponse` / `HttpRequestBodyDeltaNotification` protocol items.


### Dynamic tool namespaces
**What:** Dynamic tool calls now carry an optional `namespace` so the system can disambiguate tools that share names across plugins or MCP servers.

**Details:**
- `DynamicToolCallParams` and `ThreadItem::DynamicToolCall` both gain `namespace: Option<String>`.
- Persisted via the new state migration `0026_thread_dynamic_tools_namespace.sql`, which adds `namespace TEXT` to the `thread_dynamic_tools` table.

**Code references:** `DynamicToolCallParams` in `protocol/src/dynamic_tools.rs`; migration `state/migrations/0026_thread_dynamic_tools_namespace.sql`; schema `app-server-protocol/schema/json/DynamicToolCallParams.json`.


### Background agent identity (Ed25519)
**What:** A new `BackgroundAgentTaskManager` in the login crate registers an Ed25519 agent identity with ChatGPT and mints "human biscuit" assertion tokens used as the `Authorization` header for background tasks (including remote-control connections).

**Details:**
- Lives in `codex-rs/login/src/agent_identity.rs` (new file).
- Produces the `authorization_header_value` consumed by remote-control transport, replacing the previous raw `bearer_token` plumbing.

**Code references:** new file `login/src/agent_identity.rs`; consumed by `app-server/src/transport/remote_control/{enroll,websocket}.rs` via `AuthManager::chatgpt_authorization_header_for_auth`.

### Live-data preview in `/status-line` and `/title` setup popups
The existing `/status-line` and `/title` multi-select popups previously rendered with hardcoded example strings (`my-project`, `feat/awesome-feature`, etc.). They now use real-time runtime data — your actual current model, branch, thread title, project root, and so on — falling back to placeholders only for items that have no live value yet (e.g. plan progress before any plan exists, thread title before naming).

A shared `StatusSurfacePreviewItem` enum (21 variants) consolidates the two surfaces: status-line items include `app-name`, `project-name`, `project-root`, `current-dir`, `status`, `thread-title`, `git-branch`, `context-remaining`, `context-used`, `five-hour-limit`, `weekly-limit`, `codex-version`, `context-window-size`, `used-tokens`, `total-input-tokens`, `total-output-tokens`, `session-id`, `fast-mode`, `model-name`, `model-with-reasoning`, and `task-progress`. Terminal-title items reuse the same enum.

`StatusSurfacePreviewData::set_live` overrides placeholders, and `set_placeholder` won't clobber an already-live value. The new test/snapshot suite splits the popups into `*_hardcoded_only`, `*_live_only`, and `*_mixed` modes so regressions in the live-vs-placeholder logic are caught.

**Code references:** new file `tui/src/bottom_pane/status_surface_preview.rs`; modifications to `tui/src/bottom_pane/status_line_setup.rs` (now takes `StatusSurfacePreviewData`), `tui/src/bottom_pane/title_setup.rs` (gains `preview_data` parameter, replaces `preview_example()` with `preview_item()`), and `tui/src/chatwidget/status_surfaces.rs` (`status_surface_preview_value_for_item`).


### `request_permissions` tool is now cancellable mid-flight
The `request_permissions` tool handler now receives the turn's `cancellation_token` and threads it through to `session.request_permissions(&turn, call_id, args, cancellation_token)`. Previously, an in-flight permission prompt could not be cleanly aborted when the turn was cancelled.

`RequestPermissionsEvent` also gained an optional `cwd: Option<AbsolutePathBuf>` field so the approving UI can show the working directory against which paths in the request are relative. The `PermissionsRequestApprovalParams` schema gained a required top-level `cwd`.

**Code references:** `request_permissions` handler in `core/src/tools/handlers/request_permissions.rs`; `RequestPermissionsEvent` in `protocol/src/request_permissions.rs`; schema `PermissionsRequestApprovalParams.json`.


### Richer filesystem permission shapes (`entries`, `globScanMaxDepth`)
`AdditionalFileSystemPermissions` was extended beyond its prior `{ read, write }` shape to support:

- `entries: Option<Vec<FileSystemSandboxEntry>>` — structured `(path, access_mode)` pairs where `access_mode` is `read`/`write`/`none` and `path` can be a literal `path`, a `glob_pattern`, or a `special` token (`root`, `minimal`, `current_working_directory`, `project_roots { subpath? }`, `tmpdir`, `slash_tmp`, or `unknown { path, subpath? }`).
- `glob_scan_max_depth: Option<NonZeroUsize>` — caps recursion depth when expanding glob patterns to roots.

The corresponding `FileSystem*` types were also exposed at the v2 app-server protocol boundary (`FileSystemAccessMode`, `FileSystemPath`, `FileSystemSandboxEntry`, `FileSystemSpecialPath`) so external clients can negotiate the richer shape directly. The Rust types in `protocol/src/permissions.rs` gained `Hash` derives.

**Code references:** `AdditionalFileSystemPermissions` in `app-server-protocol/src/protocol/v2.rs`; new TypeScript schemas under `schema/typescript/v2/FileSystem*.ts` and matching JSON schemas; conversions in `From<CoreFileSystemPermissions>` / `From<AdditionalFileSystemPermissions>` impls.


### Stricter `FileSystemSandboxPolicy` legacy coercion
`FileSystemSandboxPolicy::to_legacy_sandbox_policy` was tightened so a write permission against `FileSystemSpecialPath::Root` no longer silently coerces into the legacy `SandboxPolicy::DangerFullAccess` flag. Instead, an `unbridgeable_root_write` flag is set during precomputation and the conversion returns `InvalidInput`. Read on `Root` continues to work but now pushes `absolute_root_path_for_cwd(cwd)` into `readable_roots` rather than flipping a global "read all" bit.

**Code references:** `FileSystemSandboxPolicy::to_legacy_sandbox_policy` and `has_full_disk_read_access`/`has_full_disk_write_access` helpers in `protocol/src/permissions.rs`.


### FedRAMP-aware remote control authentication
The `RemoteControlConnectionAuth` struct in the app-server transport replaced its plain `bearer_token: String` with a richer `{ authorization_header_value, account_id, is_fedramp_account }` shape. When the account is FedRAMP, requests now add an `X-OpenAI-Fedramp: true` header (`REMOTE_CONTROL_FEDRAMP_HEADER`). A new `start_remote_control_with_options` entrypoint (with `RemoteControlWebsocketOptions` / `RemoteControlStartOptions` parameter structs) replaces the previous `start_remote_control` function.

**Code references:** `RemoteControlConnectionAuth`, `start_remote_control_with_options`, `REMOTE_CONTROL_FEDRAMP_HEADER` in `app-server/src/transport/remote_control/{mod,enroll,websocket}.rs`; new audience enums in `schema/typescript/v2/RemoteControlClient{Connection,Enrollment}Audience.ts`.


### OSC 9 desktop notifications now work inside tmux
OSC 9 ("desktop notification") sequences are now wrapped in a tmux DCS passthrough envelope (`\ePtmux;\e\e]9;<message>\x07\e\\`) when terminal detection reports that we're running inside tmux. Inner ESC bytes in the message are escaped (doubled). Outside tmux the sequence is unchanged.

This unblocks notifications for users who attach Codex to a tmux session — previously OSC 9 was silently swallowed by tmux because the inner sequence wasn't passthrough-quoted.

**Code references:** `tui/src/notifications/osc9.rs` — `dcs_passthrough` flag derived from `terminal_info().multiplexer == Some(Multiplexer::Tmux)`; `escape_tmux_dcs_passthrough_payload`; new tests `post_notification_writes_tmux_dcs_wrapped_osc9_sequence` and `post_notification_escapes_escape_bytes_inside_tmux_payload`.


### `host_name()` for sandbox host classification
A new `host_name()` helper in `config/src/host_name.rs` returns the canonical FQDN of the current machine via `getaddrinfo` on Unix and `winapi_util::sysinfo::get_computer_name` on Windows. Used internally for remote-sandbox host classification.

**Code references:** new file `config/src/host_name.rs`.


### `ThreadConfigLoader` extension point
A new trait-based extension point (`ThreadConfigLoader`, `SessionThreadConfig { model_provider, model_providers, features }`, `UserThreadConfig`, `NoopThreadConfigLoader`, `StaticThreadConfigLoader`) lets an embedding app server inject session-scoped config layers. Errors flow through a typed `ThreadConfigLoadError` with codes `Auth`, `Timeout`, `Parse`, `RequestFailed`, and `Internal`.

This is primarily an integration surface for app-server consumers rather than an end-user feature, but it enables per-thread provider/model-list overrides that were previously global.

**Code references:** new file `config/src/thread_config.rs`.


### Plugin marketplace source check exposed
`is_local_marketplace_source` in `core/src/plugins/marketplace_add.rs` was promoted from `pub(crate)` to `pub` (and re-exported from `plugins/mod.rs`), letting external crates query whether a marketplace source string points to a local path. The previously re-exported `parse_marketplace_source` was removed from the public surface in the same change.

**Code references:** `is_local_marketplace_source` in `core/src/plugins/marketplace_add.rs` and `core/src/plugins/mod.rs`.

### Slash-command popup no longer fires while in bash mode
With the new bash-mode flag described above, `try_dispatch_bare_slash_command` and `try_dispatch_slash_command_with_args` now early-return when `is_bash_mode` is true. Previously, typing `!/something` could trigger spurious slash-command parsing because the leading `!` was just text. Both dispatch paths now treat `!`-prefixed buffers as shell input only.

**Code references:** `try_dispatch_bare_slash_command()` and `try_dispatch_slash_command_with_args()` in `tui/src/bottom_pane/chat_composer.rs`.


### `clear_for_ctrl_c` and `text_elements()` use canonical text
Both helpers now go through `current_text_elements()` instead of reading `textarea.text_elements()` directly, so they include the synthetic `!` prefix in bash mode and shift element offsets correctly. Previously, history capture and copy operations would drop the bang prefix in bash-mode buffers.

**Code references:** `clear_for_ctrl_c()` and `text_elements()` in `tui/src/bottom_pane/chat_composer.rs`.
