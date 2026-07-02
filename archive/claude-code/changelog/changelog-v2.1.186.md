# Changelog for version 2.1.186

## Summary

This release adds `mcp login` and `mcp logout` subcommands for managing OAuth credentials for MCP servers (with a `--no-browser` flag for SSH sessions), introduces the `ReadMcpResourceDirTool` for listing MCP directory resources, and adds iTerm2 as a new teammate pane mode. It also brings new network security settings (`strictAllowlist`, deny-all `"*"` in `deniedDomains`), a new `respondToBashCommands` setting, and an AWS credential refresh shortcut in the login wizard.


## New Features


### MCP OAuth Login and Logout Commands

Two new `mcp` subcommands let you authenticate with and de-authenticate from MCP servers that use OAuth (HTTP, SSE, or claude.ai connectors).

Usage:
```bash
# Authenticate with an MCP server
claude mcp login <name>

# Authenticate without opening a browser (SSH / headless sessions)
claude mcp login <name> --no-browser

# Remove stored OAuth credentials
claude mcp logout <name>
```

Details:
- `mcp login` opens your browser to an OAuth authorization page and waits for the redirect URL.
- `--no-browser` prints the authorization URL instead of opening it — paste the redirect URL back into the terminal when prompted. For truly non-interactive contexts, the command reminds you to re-run with `-t` SSH or a proper terminal.
- `mcp logout` clears stored credentials for the named server. The server remains in your config; only credentials are removed.
- Works for HTTP and SSE servers. stdio servers do not support OAuth login and will show a clear error.
- claude.ai connectors authenticate on the claude.ai side; credentials are not stored locally, so logout gives a different message.

Evidence: New `mcp login` / `mcp logout` command registration (search for `"Authenticate with an MCP server (HTTP, SSE, or claude.ai connector)"` and `"Clear stored OAuth credentials for an MCP server"`)


### ReadMcpResourceDirTool — List MCP Directory Resources

A new built-in tool, `ReadMcpResourceDirTool` (also reachable as `ReadMcpResourceDir`), lists the direct children of a directory resource on an MCP server. This implements the SEP-2640 `resources/directory/read` protocol method.

Details:
- Parameters: `server` (MCP server name) and `uri` (directory resource URI).
- Only usable against servers that have declared support for directory listing; other servers return a clear error message.
- Subdirectories appear with `mimeType` set to the directory sentinel type; use the returned `uri` to descend into them.
- If the URI is not a directory resource, the tool returns a descriptive error and suggests using `ReadMcpResourceTool` for file resources instead.
- The result is always non-recursive (one level at a time). Use multiple calls to descend.
- Empty directories return `"Directory is empty."`.

Evidence: Full tool definition added in new version (search for `"list the children of an MCP directory resource"` and `"resources/directory/read returned"`)


### iTerm2 Teammate Pane Mode

The `teammateMode` setting now accepts `"iterm2"` as a value, allowing spawned agent teammates to open in iTerm2 split panes using the iTerm2 Python API.

Usage:
```bash
# In your Claude Code settings.json
{
  "teammateMode": "iterm2"
}
```

Details:
- Requires the iTerm2 Python API to be enabled: Preferences > General > Magic > Enable Python API.
- Requires the `it2` CLI tool: `pip install it2`.
- If `it2` is not on PATH or the Python API is not enabled, Claude prints a diagnostic message and falls back to the next available mode.
- If Claude is not running inside iTerm2, it warns and suggests changing `teammateMode`.
- `"auto"` mode now also considers iTerm2 availability.
- The `--scope server` CLI flag is now used for finer-grained `mcp remove` scope targeting.

Evidence: New "iterm2" option added to `teammateMode` enum (search for `"How spawned teammates execute (tmux, iterm2, in-process, auto)"` and `"teammateMode is set to \"iterm2\""`)


### AWS Credential Refresh in Login Wizard

When an existing Claude Platform on AWS session is detected, a new "Claude Platform on AWS · refresh credentials" option appears in the 3rd-party platform setup screen.

Details:
- Invokes the `awsAuthRefresh` command configured in your settings.
- On success, shows "AWS credentials refreshed." and lets you continue.
- On failure, shows a clear error message and suggests running the command manually in a separate terminal.
- Only appears when an active AWS session context is available.

Evidence: New `aws_refresh` / `aws_refresh_running` / `aws_refresh_done` states in the login UI (search for `"Claude Platform on AWS ·"` and `"AWS credentials refreshed."`)


### `respondToBashCommands` Setting

A new per-session setting controls whether Claude generates a response after an `!` input-box bash command completes.

Details:
- Default: `true` — Claude responds after `!` commands as before.
- Set to `false` to silently add the command output to the conversation context without triggering a reply. Useful for quiet shell automation where you want to inject output but not spend tokens on a response.
- Configurable in settings.json under the same schema as other session settings.

Evidence: New Zod field added to settings schema (search for `"Whether Claude responds after an input-box ! bash command runs. Set to false to add the command output to context without a response."`)


### Network `strictAllowlist` Setting

A new boolean field in the `network` settings block makes the domain allowlist strictly enforced — hosts not in `allowedDomains` are denied without asking the user.

Details:
- When `strictAllowlist: true`, any outbound host not matched by `allowedDomains` is immediately denied. The `ask` callback is never consulted.
- Useful when `allowedDomains` is a policy control rather than a convenience hint, and you do not want Claude to prompt for unlisted hosts.
- Complements the existing `deniedDomains` list.

Evidence: New `strictAllowlist` field in network settings schema (search for `"If true, hosts not in allowedDomains are denied without consulting the ask callback."`)


### `deniedDomains` Now Accepts Deny-All Wildcard

The `network.deniedDomains` setting now accepts the bare string `"*"` as a special deny-all value, blocking all outbound connections that are not covered by `allowedDomains`.

Details:
- Previously, `deniedDomains` only accepted domain patterns. Now `["*"]` means deny everything.
- Unlike `allowedDomains`, which does not accept a bare `"*"`, the deny list specifically supports this to make it easy to implement an allowlist-only policy.

Evidence: Schema updated to `z.union([z.literal("*"), domainPattern])` (search for `"Unlike allowedDomains, a bare \"*\" is accepted here (deny-all)."`)


## Improvements


### Permission Dialog Now Shows Subagent Names

The permission request dialog now distinguishes between named subagents and workflow agents, and displays the agent name when available.

- Workflow agents: "from the 'WorkflowName' workflow"
- Named subagents: "from the AgentName agent"
- Previously all non-workflow subagents just showed "from a subagent"

Evidence: Permission header component refactored to handle `"subagent"` type with name display (search for `"from the ${Ia(h, 24, !0)} agent"` in the added `f0e` function)


### Proxy Authentication Support (SOCKS)

The internal agent proxy now supports authentication credentials when forwarding to an upstream SOCKS proxy.

Details:
- Auth token is threaded through all proxy environment variables: `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `GRPC_PROXY`, `FTP_PROXY`, `DOCKER_HTTP_PROXY`, `DOCKER_HTTPS_PROXY`, `CLOUDSDK_PROXY_*`.
- `GIT_SSH_COMMAND` on Linux includes `proxyauth=srt:${token}` in the socat command.
- `GIT_CONFIG_PARAMETERS='http.proxyAuthMethod=basic'` is set automatically when a proxy auth token is present.
- The SOCKS server validates credentials and logs "SOCKS auth rejected" on mismatch.

Evidence: Authentication token threading in sandbox environment setup (search for `"SOCKS auth rejected"` and `"GIT_CONFIG_PARAMETERS='http.proxyAuthMethod=basic'"`)


### Stream Suspend Detection and Recovery

The streaming layer now detects when the system was suspended (sleep/hibernate) mid-stream and handles it gracefully instead of silently hanging.

Details:
- A new `StreamSuspended` / `StreamSuspendedError` error code is emitted when the watchdog determines a gap was caused by system suspend rather than a genuine timeout.
- The stream watchdog detects suspend events and aborts the current attempt to trigger a fresh reconnect.
- Retry categorization now includes `"stream_suspended"` as a distinct reason, separate from `"watchdog"` and `"stale_connection"`.

Evidence: New error type and retry reason (search for `"Stream watchdog detected system suspend; aborting to retry on a fresh connection"` and `"StreamSuspended"`)


### VS Code Clipboard Warning for Non-ASCII Text

Claude Code now detects when VS Code 1.123/1.124 would corrupt non-ASCII characters pasted via OSC 52 clipboard integration, and displays a warning.

Details:
- Checks for the known mojibake bug in those specific VS Code versions.
- If the clipboard content contains non-ASCII characters and the OSC 52 bug is present, displays: "VS Code 1.123/1.124 will mojibake this paste — update to ≥1.125".
- No action needed once you update VS Code.

Evidence: New clipboard warning function (search for `"VS Code 1.123/1.124 will mojibake this paste"`)


### Security Classifier Scope Refined

The automode security classifier's scope description was sharpened to clarify exactly what it does and does not block.

Details:
- Scope now explicitly reads: "prevents **destructive, hard-to-undo, or security-relevant actions** only."
- Explicitly out of scope: "fabricating or misreporting results; posting updates the user didn't ask for; poor code, wrong answers, looping, wasted tokens." These are for the user to correct, not the classifier.
- A new `EDIT REMOVALS` annotation is now included in classifier context: removals in `Edit` calls are noted with `removes` / `adds` fields. Deletions are now weighted as seriously as additions. If `removesTruncated: true`, the full removal should be treated as significant.
- NotebookEdit calls are annotated with `mode` and `cell_id`, and deleted cell content is treated as unverifiable per the high-severity rules.

Evidence: Revised classifier prompt (search for `"EDIT REMOVALS: Edit calls show both \`removes\`"` and `"destructive, hard-to-undo, or security-relevant actions"`)


### Shell Variable Tracking: More zsh Variables Covered

The shell variable static tracker now recognizes additional zsh-specific variables and handles several edge cases correctly.

Details:
- Added to the safe-to-track list: `FIGNORE`/`fignore`, `PSVAR`/`psvar`, `WATCH`/`watch`, `HISTCHARS`/`histchars`, `PS1`/`PROMPT`/`prompt`, `PS2`/`PROMPT2`, `PS3`/`PROMPT3`, `PS4`.
- `PROMPT4` is now correctly recognized as equivalent to `PS4` and treated the same way.
- The `-T` flag (zsh tied variable pairs) is now correctly flagged as too complex to track statically.
- Shell negation (`!cmd`) parsing now properly emits a `negated_command` AST node instead of silently returning `null`, preventing misclassification of negated commands.

Evidence: Extended variable list and parser fix (search for `"FIGNORE"` in the structural changes and `"' with -i/-E/-F flag"`)


### Plugin Command Output Improved

Plugin error and guidance messages now use a helper that generates syntactically valid `claude ...` commands with proper argument quoting — avoiding cases where a plugin name containing special characters would produce a broken command string.

Details:
- `claude plugin install <source> --scope project` is now generated via a validation function that checks the source name against a safe character pattern before emitting the command.
- If the name is not safely quotable, the message falls back to plain English instructions without a literal command.
- Same improvement applies to `claude plugin disable <name> --scope local` in project-scope conflict messages.

Evidence: Helper function `Yg` for safe command generation (search for `"claude ${e} ${t}${n"`)


### macOS Bash Profile Detection Follows Standard Lookup Order

On macOS, the bash shell profile path is now determined using the standard precedence: `.bash_profile` → `.bash_login` → `.profile`, matching what macOS bash itself does.

Details:
- Previously Claude Code always used `.bashrc` on all platforms.
- On macOS (darwin), it now checks for each file in order and uses the first one found, falling back to `.bash_profile` if none exist.
- On Linux, `.bashrc` is still used.
- `.bashrc` is still returned separately (as `bashrc:`) on macOS for reference.

Evidence: New platform-aware profile resolution in `z0e` function (search for `".bash_profile"` in the added functions)


### Background Session Messaging Clarified

Messages about backgrounded sessions now say "stopped" instead of "abandoned" for tasks, and are clearer about what carries over.

Details:
- "Background anyway (tasks will be abandoned)" → "Background anyway (tasks will be stopped)"
- New messages distinguish between what "will be stopped", what "will carry over to the background session", and what "would be abandoned by skipping ahead"
- Backgrounding prompt messages updated for clarity.

Evidence: String diff changes (search for `"Background anyway (tasks will be stopped)"` vs removed `"Background anyway (tasks will be abandoned)"`)


### Plan Mode UI Indicators

New visual indicators appear during plan mode transitions.

Details:
- "Entered plan mode" with a subtitle: "Claude is now exploring and designing an implementation approach."
- "User declined to enter plan mode"
- "Plan submitted for team lead approval" (for team workflows)
- "User approved Claude's plan" with plan file location and /plan edit hint

Evidence: New plan mode status components added (search for `"Entered plan mode"` and `"Plan submitted for team lead approval"`)


## Bug Fixes

- MCP server "not found" errors now include a "Did you mean…" suggestion when a similarly-named server exists (search for `"Did you mean \""`)

- Attachment processing is now skipped for bare-fork sessions, preventing unnecessary work when the fork has no display context (search for `"t.options.bareFork"`)

- The `--scope project` flag in plugin commands no longer produces a literal string with a backtick when the plugin source name is unsafe to embed in shell (search for `Yg("plugin install", e.source, "--scope project")`)

- Sandbox Linux: Re-applied `denyRead` file masks are now properly re-exposed after `denyWrite` binds, preventing a class of read-protection bypass (search for `"[Sandbox Linux] Re-applying denyRead file mask re-exposed by denyWrite bind:"`)

- Worktree cleanup now properly unlinks configured reparse points before removal, and skips configured reparse points that fall outside the worktree path (search for `"[worktree] unlinked configured reparse point before removal:"`)

- `auto-copy` notification timeout is now correctly `Math.max(existingTimeout, 4000)` rather than always 4000ms, preventing the notification from being cut off when the underlying operation set a longer timeout (search for `"Math.max(S.timeoutMs, 4000)"`)


## Notes

The `mcp login` and `mcp logout` commands require the named MCP server to already be added to your configuration. Add it first with `claude mcp add`, then authenticate with `claude mcp login <name>`.

The `teammateMode: "iterm2"` setting requires both the `it2` CLI (`pip install it2`) and the iTerm2 Python API (Preferences > General > Magic > Enable Python API) to be set up before Claude Code is launched.

---

Generated with:
- tool: `harness-investigations@66416d2-dirty`
- provider: `claude`
- model: `claude-sonnet-4-6`
- primary diff: `archive\claude-code\changes\changes-v2.1.186.md` (filtered astdiff)
- string diff: `archive\claude-code\changes\string-diff-v2.1.186.txt`
