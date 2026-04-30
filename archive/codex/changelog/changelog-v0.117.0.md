# Changelog for version 0.117.0

## Highlights

Codex 0.117.0 graduates Apps, Plugins, and tool suggestion to stable, ships a major rewrite of the JavaScript "code-mode" tool around an embedded V8 runtime, and lays the groundwork for a new path-based multi-agent system (Multi-Agent V2). The app-server protocol gains filesystem watching (`fs/watch`), an unsandboxed `thread/shellCommand` that mirrors the TUI `!` workflow, runtime experimental-feature toggling, real-time transcript deltas, MCP startup status updates, and a websocket authentication story for non-loopback listeners. Configuration adds per-tool MCP approval overrides and a customizable terminal title via the new `/title` slash command.

### V8-based "code-mode" JavaScript runtime (`exec` / `wait`)

**What:** The `exec` and `wait` tools now run user-supplied JavaScript inside an in-process V8 isolate instead of a Node.js subprocess. Code-mode lets the model write a script that calls every other available tool through a `tools.*` global, accumulate text/image output, persist values across calls with `store(key, value)` / `load(key)`, and yield results incrementally with `yield_control()`.

**Details:**

- The runtime lives in a new dedicated crate (`codex-rs/code-mode/`) alongside its V8 binding code, module loader, callbacks, and value marshalling.
- Default budgets: scripts yield after 10s (`DEFAULT_EXEC_YIELD_TIME_MS`) and the result is truncated to 10 000 tokens (`DEFAULT_MAX_OUTPUT_TOKENS_PER_EXEC_CALL`).
- Override per-call by starting the script with a pragma, e.g. `// @exec: {"yield_time_ms": 30000, "max_output_tokens": 4000}`.
- Tool inputs/outputs are now type-described to the model: `augment_tool_definition` appends a TypeScript-style declaration (`declare const tools: { foo(args: { city: string; }): Promise<{ ok: boolean; }>; };`) generated from each tool's JSON schema (`render_json_schema_to_typescript`).
- Identifiers with hyphens or other invalid JS characters are normalized via `normalize_code_mode_identifier` (e.g. `hidden-dynamic-tool` → `hidden_dynamic_tool`).
- New global helpers: `exit()`, `text(value)`, `image(urlOrItem)`, `store(key, value)`, `load(key)`, `notify(value)`, `ALL_TOOLS`, and `yield_control()`.

**Code references:** `parse_exec_source()`, `build_exec_tool_description()`, `augment_tool_definition()` in `code-mode/src/description.rs`; runtime entry points `ExecuteRequest`, `WaitRequest`, `RuntimeResponse` in `code-mode/src/runtime/mod.rs`.


### `/title` slash command and terminal-title customization

**What:** A new `/title` command opens an interactive picker that lets you choose which items appear in the terminal window/tab title and reorder them with the arrow keys. The selection persists via the `tui.terminal_title` config key.

**Details:**

- Available items: `app-name`, `project`, `spinner`, `status`, `thread`, `git-branch`, `model`, `task-progress`.
- Defaults to `[spinner, project]` when unset.
- Live preview updates while reordering (the picker shows a sample title like `my-project ⠋ Working | Investigate flaky test`).
- Items render with an animated spinner separator for the spinner item and ` | ` between others.

**Code references:** `TerminalTitleSetupView`, `TerminalTitleItem` in `tui/src/bottom_pane/title_setup.rs`; `SlashCommand::Title` in `tui/src/slash_command.rs`.


### `/plugins` slash command and plugin marketplace browser

**What:** A new `/plugins` slash command (gated by the now-stable `plugins` feature) opens a TUI browser for discovering, installing, and managing plugins from configured marketplaces, including the ChatGPT-curated marketplace.

**Details:**

- The plugin detail popup shows skills, apps, and MCP servers bundled by the plugin and includes `Install plugin`/`Uninstall plugin` actions.
- `plugin/list` now returns `marketplaceLoadErrors` (a fail-open list of marketplace files that could not be parsed) and `featuredPluginIds` for the curated marketplace.
- `plugin/read` returns each skill's current `enabled` state after local config filtering and adds `needsAuth` to app summaries when the server can determine connector accessibility.
- `plugin/install` now installs any bundled MCP servers in addition to skills/apps.

**Code references:** `SlashCommand::Plugins` in `tui/src/slash_command.rs`; plugin marketplace logic in `core/src/plugins/marketplace.rs`, `core/src/plugins/curated_repo.rs`, `core/src/plugins/manager.rs`; new shared `codex-plugin` crate in `plugin/src/lib.rs`.


### `thread/shellCommand` (TUI `!` over the wire)

**What:** A new JSON-RPC method exposes the TUI `!` shell-command workflow to app-server clients. The command runs unsandboxed with full access — it does not inherit the thread's sandbox policy.

**Details:**

- If the thread already has an active turn, output streams as `item/started` / `item/commandExecution/outputDelta` / `item/completed` on that turn (with `commandExecution.source = "userShell"`) and the formatted output is injected into the turn's message stream.
- If no turn is active, the server starts a standalone turn that emits the standard `turn/started` … `turn/completed` envelope around the command execution.
- Returns `{}` immediately; progress arrives through the streaming notifications.

**Code references:** `ThreadShellCommandParams` in `app-server-protocol/src/protocol/v2.rs`; example in `app-server/README.md`.


### Filesystem watching (`fs/watch`, `fs/unwatch`, `fs/changed`)

**What:** Clients can subscribe to filesystem change notifications for an absolute file or directory path and unsubscribe later by `watchId`.

**Details:**

- `fs/watch` returns `{ watchId, path }` (canonicalized), where `path` is the path that will be reported back in change events.
- File watches survive replace/rename operations (the watcher reports updates delivered through atomic-replace patterns).
- `fs/changed` is server-pushed and contains `{ watchId, changedPaths }`.
- `fs/unwatch` returns `{}` and stops further notifications for that watch.

**Code references:** `FsWatchParams`, `FsUnwatchParams`, `FsChangedNotification` in `app-server-protocol/src/protocol/v2.rs`; `fs_watch.rs` in `app-server/src/`.


### `experimentalFeature/enablement/set` runtime feature toggle

**What:** Clients can patch the in-memory, process-wide runtime feature enablement for currently supported feature keys (`apps`, `plugins`) without restarting the server.

**Details:**

- Send `{ enablement: { apps: true, plugins: false } }`. Omitted features are left unchanged; an empty map is a no-op.
- Precedence order is now: cloud requirements > `--enable <feature_name>` > `config.toml` > `experimentalFeature/enablement/set` > built-in default.

**Code references:** `apply_runtime_feature_enablement()` in `app-server/src/config_api.rs`; `ExperimentalFeatureEnablementSetParams` in the protocol schemas.


### MCP server startup status notifications

**What:** A new `mcpServer/startupStatus/updated` notification streams MCP server lifecycle transitions to the client for any loaded thread.

**Details:**

- `status` is one of `starting`, `ready`, `failed`, or `cancelled`.
- `error` is `null` except when `status` is `failed`.
- Lets clients render real-time MCP startup progress instead of polling `mcpServerStatus/list`.

**Code references:** `McpServerStatusUpdatedNotification`, `McpServerStartupState` in `app-server-protocol/src/protocol/v2.rs`; emitter in `app-server/src/bespoke_event_handling.rs`.


### Per-tool MCP approval overrides

**What:** `config.toml` now accepts a `[mcp_servers.<name>.tools.<tool_name>]` table where you can override approval mode per individual tool.

**Details:**

- Example:
  ```toml
  [mcp_servers.docs]
  command = "docs-server"

  [mcp_servers.docs.tools.search]
  approval_mode = "approve"
  ```
- Reserved names like `command` are still accepted as tool names under `tools`, so you can override approval for any actual MCP tool the server exposes.
- Approval-elicitation `meta` now carries `codex_approval_kind: "mcp_tool_call"` and may advertise `persist: "session"`, `persist: "always"`, or `persist: ["session", "always"]` so the client can offer session-scoped or persistent approval choices.

**Code references:** `McpServerToolConfig` in `core/src/config/types.rs`; new schema in `core/config.schema.json`.


### App-server websocket authentication

**What:** Two new authentication modes for the `--listen ws://…` app-server transport, configured via CLI flags. Loopback listeners (`ws://127.0.0.1:PORT`) remain unauthenticated; non-loopback listeners can now require a credential before `initialize`.

**Details:**

- Capability-token mode: `--ws-auth capability-token --ws-token-file /absolute/path/token.txt`.
- Signed-bearer mode: `--ws-auth signed-bearer-token --ws-shared-secret-file /absolute/path/secret.bin` (HMAC-signed JWT/JWS) plus optional `--ws-issuer`, `--ws-audience`, `--ws-max-clock-skew-seconds`.
- Clients present the credential as `Authorization: Bearer <token>` during the websocket handshake.
- The server prints a startup warning when a non-loopback listener is started without auth, since unauthenticated remote use will become a hard error in a future release.
- The CLI gains `--remote-auth-token-env <ENV_VAR>` so a remote-mode TUI/Resume can read its bearer token out of an environment variable instead of hard-coding it.

**Code references:** `AppServerWebsocketAuthArgs` in `app-server/src/transport/auth.rs`; `--ws-auth*` flags in `app-server/src/main.rs`; root `--remote-auth-token-env` in `cli/src/main.rs`.


### Multi-Agent V2 (under development)

**What:** A new `multi_agent_v2` feature flag introduces a path-based multi-agent collaboration layer with first-class `AgentPath` identifiers and a fresh tool surface (`spawn`, `assign_task`, `send_message`, `wait`, `close_agent`, `list_agents`).

**Details:**

- `AgentPath` is now a shared protocol type (`export type AgentPath = string;`) included in `SubAgentSource::ThreadSpawn` and `SessionMeta`.
- A new `Op::InterAgentCommunication` variant carries structured `{ author, recipient, other_recipients, content, trigger_turn }` records that get persisted as assistant messages in history.
- `list_agents` accepts an optional `path_prefix` for hierarchical agent navigation.
- `assign_task` triggers a turn on the target agent; `send_message` delivers without triggering a turn.
- The feature is currently `Stage::UnderDevelopment` and disabled by default; it remains opt-in while the path/registry semantics stabilize.

**Code references:** `AgentPath` in `protocol/src/lib.rs`; `Feature::MultiAgentV2`, `Op::InterAgentCommunication` in `protocol/src/protocol.rs`; tool handlers in `core/src/tools/handlers/multi_agents_v2/`.


### Standalone `codex-exec-server` binary

**What:** A new narrowly-scoped JSON-RPC server crate (`exec-server`) provides a standalone way to spawn and control PTY-backed subprocesses through `codex-utils-pty`.

**Details:**

- Ships as `codex-exec-server` with a `--listen ws://IP:PORT` flag.
- Speaks the shared `codex-app-server-protocol` envelope: `initialize` → `initialized` → `command/exec` / `command/exec/write` / `command/exec/terminate`, with `command/exec/outputDelta` and `command/exec/exited` notifications.
- Stdin is base64-encoded; outputs are streamed as base64 deltas with a `stream: "stdout" | "stderr"` discriminator.
- Pipe-backed processes (`tty: false`) launch with stdin closed and reject `command/exec/write`.
- Closing the websocket terminates any remaining managed processes for that connection.

**Code references:** `exec-server/README.md`; transport, server, and `ExecServerClient` in `exec-server/src/`.


### Real-time conversation transcript notifications

**What:** Realtime conversations now stream live transcript deltas as a typed app-server notification, in addition to the audio output already supported.

**Details:**

- `thread/realtime/transcriptUpdated` is emitted with `{ threadId, role, text }` whenever transcript text changes (input or output role). The `text` is the live delta from the upstream realtime event, not the full accumulated transcript.
- `thread/realtime/itemAdded` continues to forward raw non-audio realtime items (including `handoff_request`) for which there is no dedicated typed notification yet.

**Code references:** `ThreadRealtimeTranscriptUpdatedNotification` in `app-server-protocol/src/protocol/v2.rs`; emitter in `app-server/src/bespoke_event_handling.rs`.


### Skills config write by name

**What:** `skills/config/write` now accepts a name-based selector in addition to an absolute-path selector, so clients can flip a skill's enabled state without first resolving its `SKILL.md` path.

**Details:**

- The request now takes `{ path: AbsolutePath | null, name: string | null, enabled: bool }`.
- One of `path` or `name` must be set. Names like `github:yeet` work for namespaced skills.

**Code references:** `SkillsConfigWriteParams` in `app-server-protocol/src/protocol/v2.rs`; example in `app-server/README.md`.


### `tool_search` feature flag

**What:** A new `tool_search` feature key gates the previously-implicit `tool_search` tool that lazy-loads MCP tools for installed apps.

**Details:**

- When disabled (default), the apps preface no longer mentions `tool_search`, and tool-suggest output drops the `tool_search` reference for the "no good match" guidance.
- When enabled, the model is told it can call `tool_search` to discover apps' tools on demand.

**Code references:** `Feature::ToolSearch` in `features/src/lib.rs`; tool wiring in `core/src/tools/mod.rs`.


### `PreToolUse` and `PostToolUse` hook events

**What:** Hook configuration now supports `pre_tool_use` and `post_tool_use` event names alongside the existing `session_start`, `user_prompt_submit`, and `stop` events.

**Details:**

- New JSON schema generators emit `pre-tool-use.command.input.schema.json` / `pre-tool-use.command.output.schema.json` (and matching `post-tool-use` schemas) under `hooks/schema/generated/`.
- The `RawResponseItem` event mapping recognizes hook prompts and emits an `item/completed` notification with a `HookPrompt` thread item containing the prompt fragments.

**Code references:** `HookEventName::{PreToolUse, PostToolUse}` in `protocol/src/protocol.rs`; `parse_hook_prompt_message`, `HookPromptFragment` in `protocol/src/items.rs`.


### `--include-non-interactive` for `codex resume`

**What:** `codex resume` (and the resume picker) now accepts `--include-non-interactive`, which adds non-interactive sessions (e.g. `exec`, `appServer`, sub-agent threads) to the candidate list and the `--last` selection.

**Details:**

- Without the flag, `resume` continues to default to interactive sources (`cli`, `vscode`).
- The protocol-level `ThreadSourceKind::Custom` discriminator was removed (custom session sources are no longer separately enumerable here).

**Code references:** `ResumeCommand::include_non_interactive` in `cli/src/main.rs`.


### `codexHome` returned in `initialize`

**What:** The `initialize` response now includes a `codexHome` field — the absolute path of the server's `$CODEX_HOME` directory — so clients no longer have to derive it independently.

**Code references:** `InitializeResponse` in `app-server-protocol/schema/typescript/InitializeResponse.ts`.


### `FuzzyFileSearchResult.match_type`

**What:** Fuzzy file-search results now include a `match_type: "file" | "directory"` field, enabling clients to render directories and files differently or filter to one or the other.

**Code references:** `FuzzyFileSearchMatchType` in `app-server-protocol/schema/typescript/FuzzyFileSearchMatchType.ts`.


### `CommandExecutionSource` on command-execution items

**What:** Command-execution thread items now carry a `source` discriminator so clients can tell agent commands apart from `!`-shell commands and unified-exec startup vs. interaction.

**Details:** `source` is one of `agent`, `userShell`, `unifiedExecStartup`, or `unifiedExecInteraction`.

**Code references:** `CommandExecutionSource` in `app-server-protocol/schema/typescript/v2/CommandExecutionSource.ts`.

### Apps, Plugins, ToolSuggest, ToolCallMcpElicitation, and TuiAppServer graduated to stable

The following features are now `Stage::Stable` and `default_enabled = true` (they were either Experimental or UnderDevelopment in 0.116):

- `apps` — ChatGPT Apps / Connectors via `$app-name` mentions
- `plugins` — plugin marketplace and `/plugins` slash command
- `tool_suggest` — discoverable tool suggestions for apps
- `tool_call_mcp_elicitation` — MCP elicitation during tool calls
- `tui_app_server` — the app-server-backed TUI implementation

The Experimental "Apps" announcement banner is gone; use the new `experimentalFeature/enablement/set` API or `--enable <feature>` to toggle them per-process if needed.

**Code references:** `FEATURES` table in `features/src/lib.rs`.


### `thread/fork` snapshots running turns instead of inheriting partial state

When forking a thread that has an active in-flight turn, the fork now records the same interruption marker as `turn/interrupt` would, instead of inheriting an unmarked partial-turn suffix. This prevents resumed forks from looking like they were silently truncated.

**Code references:** `thread/fork` description in `app-server/README.md`; fork logic in `core/src/agent/control.rs`.


### `thread/resume` falls back to persisted model and reasoning effort

By default, `thread/resume` now uses the latest persisted `model` and `reasoningEffort` values associated with the thread. Supplying any of `model`, `modelProvider`, `config.model`, or `config.model_reasoning_effort` disables that fallback and uses the explicit overrides plus normal config resolution instead. Previously a resume always re-resolved from current config.


### `turn/steer` rejects non-steerable turns with a typed error

`turn/start` and `turn/steer` now fail with the new `activeTurnNotSteerable` error variant (carrying `turnKind: "review" | "compact"`) when a `/review` or manual `/compact` turn is currently active. Steering still works on regular turns.

**Code references:** `CodexErrorInfo::ActiveTurnNotSteerable`, `NonSteerableTurnKind` in `protocol/src/protocol.rs`.


### Lossless transcript and completion delivery under backpressure

The in-process app-server transport now blocks instead of dropping these notifications when the consumer queue is full: `TurnCompleted`, `ItemCompleted`, `AgentMessageDelta`, `PlanDelta`, `ReasoningSummaryTextDelta`, `ReasoningTextDelta`. Best-effort events (e.g. `CommandExecutionOutputDelta`) still drop with a `Lagged { skipped }` marker, but visible assistant output and completion signals are no longer corruptible by a slow consumer.

**Code references:** `server_notification_requires_delivery()` in `app-server-client/src/lib.rs`.


### Linux sandbox: bubblewrap `--argv0` compatibility fallback

If `/usr/bin/bwrap` is present but too old to support `--argv0`, the Linux sandbox helper now keeps using the system bubblewrap and switches to a no-`--argv0` compatibility path for the inner re-exec, instead of falling back to the vendored bubblewrap. Missing `/usr/bin/bwrap` still falls back to the vendored binary and surfaces a startup warning through Codex's normal notification path.

**Code references:** `linux-sandbox/README.md`; sandbox runner code in `linux-sandbox/src/`.


### Windows sandbox: WorkspaceWrite-compatible split policies

The unelevated restricted-token Windows backend now supports a narrow split-filesystem subset on top of the existing legacy `ReadOnly`/`WorkspaceWrite` modes: full-read split policies whose writable roots still match the legacy WorkspaceWrite root set, plus extra read-only carveouts under those writable roots. Richer split-only carveouts (different writable root sets, explicit unreadable carveouts, reopened writable descendants under read-only carveouts) still fail closed instead of running with weaker enforcement.

**Code references:** `core/README.md`; sandbox dispatch in `core/src/sandboxing/`, `windows-sandbox-rs/src/`.


### `on_request` approval prompt: clearer rule guidance

The on-request approval prompt now documents that commands using shell features (redirection `>`, `<`, command substitution `$(...)`, env var prefixes `FOO=bar`, glob `*`/`?`) are not evaluated against approved prefix rules, to limit the scope of an approved rule. The "banned prefix_rules" example was clarified to call out that prefixes enabling arbitrary scripting (e.g. `python -`) are still off-limits, and the misleading `pytest` example was removed.

**Code references:** `protocol/src/prompts/permissions/approval_policy/on_request.md` (renamed from `on_request_rule.md`).


### Custom prompts deprecation notice

The TUI now displays a startup banner — `⚠ Custom prompts are deprecated and will soon be removed.` — when `$CODEX_HOME/prompts` contains custom prompts. The banner instructs users to convert each custom prompt into a skill via the `$skill-creator` skill.

**Code references:** snapshot `tui/src/snapshots/codex_tui__app__tests__startup_custom_prompt_deprecation_notice.snap`.


### Pending steers shown above queued messages

The chat composer's pending-input preview gained a new section, "Messages to be submitted at end of turn", rendered above "Queued follow-up messages". This visualizes steer messages that were rejected by the active turn (e.g. during `/compact`) and will be retried automatically.


### Image-generation history: link to saved file

Generated-image history cells now show `Saved to: file:///tmp/ig-1.png` (a clickable file URL) instead of just `Saved to: /tmp`.


### Account display recognises ChatGPT auth-tokens mode

The status pane now displays the ChatGPT email/plan correctly for both `Chatgpt` and `ChatgptAuthTokens` auth modes; previously the auth-tokens variant fell through to the API-key display path.

**Code references:** `compose_account_display()` in `tui/src/status/helpers.rs`.


### Architectural split into focused crates

A large reorganization extracted reusable code into dedicated crates so they can be consumed without pulling in `codex-core`:

- New: `codex-analytics`, `codex-code-mode`, `codex-core-skills`, `codex-exec-server`, `codex-features`, `codex-git-utils` (renamed from `utils/git`), `codex-instructions`, `codex-plugin`, `codex-rollout`, `codex-sandboxing`, `codex-terminal-detection`, `codex-utils-output-truncation`, `codex-utils-path`, `codex-utils-plugins`, `codex-utils-template`, `codex-v8-poc`.
- Removed/folded: `codex-environment`, `codex-artifacts`, `codex-test-macros`.

End-user effects: imports from older third-party scripts that referenced `codex_core::features::*`, `codex_core::skills::*`, or `codex_core::analytics_client::*` need to switch to the new crate paths (`codex_features`, `codex_core_skills`, `codex_analytics`). The CLI was updated accordingly (`codex_features::Stage`, `codex_terminal_detection::TerminalName`).

### `PowershellUtf8` feature removed

The `powershell_utf8` feature was removed from the registry. It had previously been auto-enabled on Windows and a no-op everywhere else; the per-platform behavior is now handled directly by the shell layer without a user-visible toggle.

**Code references:** removed `Feature::PowershellUtf8` entry in `features/src/lib.rs`.


### `--session-source` flag removed from `app-server`

The `codex app-server --session-source <SOURCE>` argument was removed; the standalone app-server now always stamps new threads with `SessionSource::VSCode`. The `SessionSource::Custom("…")` variant was correspondingly removed from the protocol's `ThreadSourceKind` enumeration. Embedders that were passing custom session sources should switch to building the in-process app-server directly.

**Code references:** `cli/src/main.rs` (removed `session_source` field on `AppServerCommand`).


### `archived` thread resume no longer reports "thread not found"

`AgentControl::resume_agent_from_rollout` now also looks up archived rollouts via `find_archived_thread_path_by_id_str` before returning `ThreadNotFound`. Previously, resuming an archived thread by id failed even though `thread/unarchive` would have been able to find it.

**Code references:** `resume_single_agent_from_rollout()` in `core/src/agent/control.rs`.


### Hook prompt messages emit `item/completed`

Raw response items that are recognized as hook prompts (via `parse_hook_prompt_message`) now emit an `item/completed` notification with a `HookPrompt` thread item carrying the prompt fragments and per-fragment `hook_run_id`s. Previously these arrived only as raw user-role messages, leaving clients without a typed hook-completion signal.

**Code references:** `maybe_emit_hook_prompt_item_completed()` in `app-server/src/bespoke_event_handling.rs`.


### `SubAgentSource::ThreadSpawn` carries `agent_path`

`SubAgentSource::ThreadSpawn` now includes an optional `agent_path` field alongside `parent_thread_id`, `depth`, `agent_nickname`, and `agent_role`. Resume flows hydrate the path from the persisted state DB, so descendants of multi-agent threads are now correctly re-attached on resume instead of losing their place in the agent tree.

**Code references:** `SubAgentSource::ThreadSpawn` in `protocol/src/protocol.rs`; resume logic in `core/src/agent/control.rs`.


### `Op::UserTurn` accepts an `approvals_reviewer` override

`Op::UserTurn` now carries an optional `approvals_reviewer: Option<ApprovalsReviewer>`. When omitted, the session keeps the current setting; when present, the value is applied to approval requests raised during that turn. This brings turn-scoped reviewer configuration into parity with the other per-turn fields.

**Code references:** `Op::UserTurn` in `protocol/src/protocol.rs`.
