# Changelog for version 2.1.132

## Summary
This release adds Linux sandbox configuration for custom `bwrap` and `socat` binaries, improves MCP startup handling with a new wait tool behind a rollout flag, and makes WebFetch failures more actionable by returning HTTP status details instead of opaque fetch errors. It also includes several terminal and background-session refinements, plus dark-launched `/goal` infrastructure that is present in the build but not enabled.


### Custom Linux Sandbox Binary Paths
What: Linux users can now configure exact `bwrap` and `socat` binary paths for sandbox and proxy bridge setup.

Usage:
```json
{
  "sandbox": {
    "bwrapPath": "/usr/bin/bwrap",
    "socatPath": "/usr/bin/socat"
  }
}
```

Details:
- `bwrapPath` controls the bubblewrap executable used for Linux sandboxing.
- `socatPath` controls the executable used for HTTP/SOCKS bridge processes.
- Claude Code validates that configured paths are executable and reports clearer errors if not.
- This is useful on systems where these tools are installed outside `PATH`, or where a managed environment pins exact binary locations.

Evidence: Sandbox schema adds `bwrapPath` and `socatPath` settings (search for `"Linux only: absolute path to the bwrap"` and `"Linux only: absolute path to the socat binary"`)


### MCP Wait For Servers [Gradual Rollout]
What: Claude can wait briefly for MCP servers that are still connecting, then continue once their tools are available.

Usage:
```text
Claude calls WaitForMcpServers when an MCP server is still connecting.
```

Details:
- The new `WaitForMcpServers` tool waits for all pending servers, or for specific server names.
- Results distinguish connected, failed, still pending, needs-auth, disabled, and unknown servers.
- Missing-tool guidance now tells Claude when a requested MCP tool belongs to a server that is still connecting.
- The tool is gated by `tengu_ashen_kelp`, so it may not be visible for every user yet.

Evidence: MCP wait tool and gated enablement (search for `"WaitForMcpServers"` and `"The MCP server '"`)


### WebFetch HTTP Error Results
WebFetch now returns structured HTTP failure information when a server responds with an error status, including status text and `Retry-After` when present. This should help users distinguish an authentication-required page, a rate limit, and a normal fetch failure without guessing from a generic exception.

Evidence: WebFetch HTTP error result text (search for `"The server returned HTTP"` and `"The response body was not retrieved"`)


### Fullscreen Renderer Controls
Terminal fullscreen behavior is more conservative and easier to override. Claude Code now recognizes `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN` as an explicit opt-out, and it auto-disables fullscreen on Windows-over-SSH ConPTY sessions unless `CLAUDE_CODE_NO_FLICKER=1` is set.

Evidence: Fullscreen environment handling (search for `"CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN"` and `"fullscreen disabled: Windows over SSH"`)


### Background Session Detach Key
Background session instructions now consistently use `Ctrl+Z` to detach, replacing older `Ctrl+B then d` and `Ctrl+Q` guidance in redraw/startup messages.

Evidence: Background session prompts (search for `"Ctrl+Z to detach"`)


### MCP Connection Resilience
Remote MCP retry behavior now logs recovery and stops retrying once failed remote servers recover. MCP stdio transports also detect excessive non-protocol stdout and disconnect before unbounded memory growth.

Evidence: MCP retry and stdout overflow handling (search for `"[MCP] Retry: all remote servers recovered, stopping"` and `"StdoutOverflowError"`)


### Bash Safety Detection
Read-only command validation gained additional shell-edge-case detection, especially around zsh recursive evaluation, array subscripts, assignment side effects, redirect expansion, and escaped brace handling. These checks reduce cases where a command that looks harmless can still execute dynamic shell code.

Evidence: Shell safety reasons (search for `"zsh $name[expr]"`, `"assignment alters command lookup/execution"`, and `"Redirect target starts with ="`)


### Long-Running Command Guidance
The Bash tool description now explains `run_in_background` more directly and removes stale advice to read output later immediately. Claude Code also includes stronger guidance to avoid foreground `sleep` and use background commands or Monitor for waiting.

Evidence: Background command guidance (search for `"`run_in_background` runs the command detached"` and `"Foreground `sleep` is blocked"`)


### Policy Limit Cache Handling
When policy limits are fetched and no restrictions apply, Claude Code now preserves an explicit cached empty result instead of treating it like a deleted cache file. This should reduce noisy policy-limit cache churn in environments with no active restrictions.

Evidence: Policy limit cache message (search for `"Policy limits: No restrictions (cached empty)"`)


### Service Availability Messages
Daemon/service messages now distinguish unsupported installation from on-demand operation, making platform limitations clearer.

Evidence: Service messaging (search for `"service install not available on this platform"` and `"service uninstall not available on linux"`)


## Bug Fixes

- WebFetch now reports HTTP status responses as tool results instead of falling through to less-informative request failures (search for `"The server returned HTTP"`)

- MCP stdio servers that write too much non-JSON data to stdout are disconnected with a clear overflow error instead of allowing unbounded buffering (search for `"wrote >"` and `"without a JSON-RPC message boundary"`)

- Fullscreen mode is now disabled automatically for Windows-over-SSH ConPTY sessions where the alternate-screen renderer is known to misbehave (search for `"fullscreen disabled: Windows over SSH"`)

- Policy-limit fetches with no restrictions now cache the empty state instead of deleting the cache on the old 404 path (search for `"Policy limits: No restrictions (cached empty)"`)


## In Development

Features with infrastructure added but not yet enabled. These are shipped "dark" and may become available in future versions.


### Goal Command [In Development]
What: A new `/goal` command is being prepared to set a session-scoped stopping condition so Claude keeps working until a stated goal is met.

Status: Disabled/stubbed

Details:
- The implementation adds `/goal <condition>`, `/goal clear`, status rendering, and a session-scoped Stop hook.
- Goal state records the condition, iteration count, and set time.
- The command currently has `isEnabled: () => !1`, so users cannot invoke it in this build.
- The existing `/loops` UI can see and manipulate related Stop-hook entries, but `/goal` itself remains unavailable.

Evidence: Disabled goal command implementation (search for `"Set a goal — keep working until the condition is met"` and `"No goal set. Usage: `/goal <condition>`"`)
