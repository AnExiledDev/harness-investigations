# Changelog for version 2.1.196

## Summary

This release introduces a structured `ReportFindings` tool for code review output, adds support for a "Claude Preview" MCP integration, and delivers org-level default model settings. The sandbox networking layer was rearchitected from two separate proxies into a single multiplexed proxy. Several security improvements land in the shell analyzer, including new checks for dangerous awk patterns and better Windows sandbox constraints.


## New Features


### ReportFindings: structured code review output

What: Code reviews now report findings through a dedicated typed tool rather than as free-form text. The tool produces a structured list the UI can render with colored severity indicators, file and line anchors, and per-finding outcome tracking.

Usage:
```
/code-review
```
(No change to how you invoke a review — the output format changes automatically.)

Details:
- Each finding carries `file`, `line`, `summary`, `failure_scenario`, `verdict` (CONFIRMED/PLAUSIBLE), and optionally `outcome` (fixed/skipped/no_change_needed) when applying fixes
- Findings are capped at 32 and ranked most-severe first
- The UI renders confirmed findings with a red dot, plausible with yellow, and fixed with a green checkmark
- When a review runs in workflow mode, the description changed from "one finder agent per review angle" to "one finder per correctness angle plus one finder covering all cleanup angles" — correctness and cleanup finders are now explicitly split

Evidence: New tool named `"ReportFindings"` (search for `"ReportFindings"` and `"report code-review findings as a structured list"`)


### Claude Preview MCP integration

What: Claude Preview is now a recognized MCP server type, alongside the existing Claude in Chrome integration. Tools exposed by a Claude Preview server share a distinct permission category and require explicit user permission before they can be used.

Details:
- Tools served by Claude Preview servers have the prefix `mcp__Claude_Preview__`
- The tool requires permission with the message "Claude Preview requires permission."
- The integration is added to the same internal set as "claude-in-chrome" and "Claude in Chrome"

Evidence: New constant `"Claude Preview"` and permission check (search for `"mcp__Claude_Preview__"`)


### Org default model setting

What: Organization administrators can now set a default model that applies to all members. When an org default is present, the status bar shows "· Org default" next to the model name, and the org's preference is applied unless overridden by policy or the user has explicitly selected a model.

Details:
- Org defaults are delivered via a cached `orgModelDefaultCache` field in session state
- The default respects an `override_user_selection` flag: if true, the user cannot override it; if false, a user's explicit choice takes precedence
- When the org default is updated, any user-level model override in settings is cleared automatically
- Non-firstParty providers (Bedrock, Vertex, etc.) are not affected by org defaults

Evidence: New function `C4r()` reading `orgModelDefaultCache`, UI label (search for `"· Org default"`)


### SendUserFile gains a `display` parameter

What: The `SendUserFile` tool now accepts a `display` field that controls how the client presents the file. Previously presentation was entirely automatic.

Usage:
```
SendUserFile({ files: ["chart.html"], caption: "Here's the chart.", status: "normal", display: "render" })
SendUserFile({ files: ["data.csv"], caption: "Here's the export.", status: "normal", display: "attach" })
```

Details:
- `"render"`: opens the file inline in the side panel; intended for HTML, SVG, Mermaid diagrams, images, and PDFs the user wants to see immediately
- `"attach"`: shows a download card only; intended for source code, spreadsheets, or documents the user will open elsewhere
- Omitting the field lets the client decide by file type (existing behavior)

Evidence: Updated tool description now includes the `display` parameter (search for `"Set \`display\` to choose how the file is presented"`)


## Improvements


### Unified mux proxy replaces separate HTTP and SOCKS proxies

What: The sandbox networking layer was redesigned. A single multiplexed proxy (listening on one port) now handles both HTTP CONNECT and SOCKS5 traffic, routing each connection by inspecting the first byte. Previously the sandbox started two separate servers and tracked two ports.

Details:
- The new proxy logs `"Mux proxy (HTTP+SOCKS) listening on localhost:<port>"` (replacing the old separate "HTTP proxy listening on..." and "SOCKS proxy listening on..." lines)
- On Linux and macOS, the HTTP backend now listens on a Unix domain socket (under `srt-mux-<pid>-N.sock`) rather than an ephemeral TCP port; on Windows it falls back to a TCP port
- `GIT_SSH_COMMAND` is now set once with the combined mux proxy address; the old separate `nc`/`socat` invocations per-protocol are gone

Evidence: Startup log string (search for `"Mux proxy (HTTP+SOCKS) listening on localhost:"`)


### Awk security analysis

What: The shell command analyzer now inspects awk programs for dangerous constructs and blocks or warns on them in the same way it does for other risky shell patterns.

Details:
- `system()` calls inside awk programs are flagged ("awk program contains system() which executes arbitrary commands")
- Command pipes (`| "cmd"` or `| getline`) are flagged
- `@load`, `@include`, and `@indirect` calls are flagged (can execute arbitrary code)
- `extension()` calls are flagged (loads arbitrary native code in legacy gawk)
- gawk `/inet/` network sockets are flagged (potential data exfiltration)
- Unquoted glob characters in the awk command line are flagged (could glob-expand before awk runs)
- Runtime-determined awk arguments (shell substitutions in the argument) are flagged as unable to be statically analyzed
- Flags that read programs from files (`-f`, etc.) are flagged

Evidence: New analyzer function (search for `"awk program contains system() which executes arbitrary commands"`)


### Cumulative compaction token tracking

What: Context compaction now tracks the total tokens dropped across all compaction events in a session, not just the most recent one. The `cumulativeDroppedTokens` field is updated each time a compaction runs.

Details:
- Each contribution is approximately `pre_tokens − post_tokens` for that compaction pass
- Downstream displays that show "tokens saved by compaction" will now reflect the full session total, not just the last pass

Evidence: New field and accumulator function (search for `"@internal Running total of context tokens compaction has removed so far, across this and every earlier compaction"`)


### Skill tool description A/B test

What: An experimental, shorter description of the Skill tool is being tested under feature flag `tengu_russet_linnet`. The new description is more concise, leading with "packaged instructions" framing instead of the longer paragraph.

Details:
- Controlled by `CLAUDE_CODE_SKILL_DESC_REFRAME` env var or the `tengu_russet_linnet` flag
- The shorter version omits several of the original rules-list items and leads with: "A skill is a packaged set of instructions the user or project has set up for a particular kind of task..."
- The original description is still the default

Evidence: Feature flag check (search for `"skill_desc_reframe_arm_active source="`)


### Prompt ID added to hook system

What: The hook event schema gained a `prompt_id` field — a UUID that correlates a user prompt with all subsequent events until the next prompt. The same UUID is emitted as the `prompt.id` attribute on OpenTelemetry events, making it possible to join hook output to OTel traces.

Details:
- Present on hook dispatch payloads, not just OTel
- Optional field; absent on non-prompt-triggered events

Evidence: Schema description string (search for `"UUID correlating a user prompt with all subsequent events until the next prompt"`)


### CLAUDE_RUNNER_ACTIVITY_FD environment variable

What: A new environment variable `CLAUDE_RUNNER_ACTIVITY_FD` is recognized for signaling activity in runner/non-interactive mode.

Evidence: Added to env var handling (search for `"CLAUDE_RUNNER_ACTIVITY_FD"`)


## Bug Fixes

- Fixed the "confirm" back-arrow prompt so it shows a single `←` arrow instead of the double `←←` that was displayed in earlier builds. (search for `"Press ← again to confirm"`)

- Fixed file-type validation to correctly distinguish regular files, directories, FIFOs, and sockets, and surface a specific `ERR_NOT_REGULAR_FILE` error code when the path is not a plain file. Previously some non-regular-file paths produced generic errors. (search for `"Not a regular file (device, FIFO, or socket)"`)

- Fixed credential-mask logic to skip and warn on binary credential files rather than failing silently, and to reject entries that resolve to directories. (search for `"Skipping masked file with non-UTF-8 content"`)


## In Development


### Monitoring notice in org policy

What: The organization policy schema has a new `monitoring_notice` field that can carry a plain-text notice and an optional HTTPS URL. This would let an organization display a monitoring disclosure to users when they open a session.

Status: Field is in the schema and validated, but no UI rendering of the notice was found in this diff.

Details:
- `text` is limited to 500 characters and has control characters stripped
- `url` must be an `https://` URL; invalid values coerce to null
- The field is nullable with a default of null

Evidence: Schema definition (search for `"monitoring_notice"`)


### Artifact auto-open analytics

What: Infrastructure to track when artifacts are auto-opened was added, posting to a new `/api/frame/track` endpoint. The tracker records the event name, slug, via-channel, and mode.

Status: Infrastructure in place; disabled paths log at trace level only.

Evidence: New tracking function (search for `"[artifact] /track"`)


## Notes

The model catalog was internally refactored from a hardcoded JavaScript object to a data-driven loader that reads entries from a separate catalog and derives provider IDs from it. The display names previously hardcoded in a switch statement now come from a `display_name` field in the catalog. This is purely internal with no behavior change for users.

The "Claude Code Insights" HTML dashboard (the usage analysis report with project areas, friction categories, impressive workflows, and "on the horizon" opportunities) was removed in this release.

---

Generated with:
- tool: `harness-investigations@0c752ef-dirty`
- provider: `claude`
- model: `claude-sonnet-4-6`
- primary diff: `archive/claude-code/changes/changes-v2.1.196.md` (filtered astdiff)
- string diff: `archive/claude-code/changes/string-diff-v2.1.196.txt`
