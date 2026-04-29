# Changelog for version 2.1.113

## Summary

Version 2.1.113 introduces deep linking support with base64url-encoded CLI parameters, a new event-driven trigger system for GitHub and Slack integrations, a structured `where` clause predicate language for filtering, and a daemon backend option for background agents. The release also ships as a Linux-only build with all platform detection hardcoded, disabling Windows and macOS code paths, and removes large bundled libraries (undici, ws, Fetch/URL polyfills, YAML parser) in favor of native Node.js modules.


### Deep Linking with Base64url Parameters

What: New CLI flags for launching Claude Code via deep links with shell-safe, base64url-encoded parameters. This enables external applications (such as IDE extensions or web UIs) to open Claude Code with a prefilled prompt and working directory without worrying about shell escaping.

Usage:
```bash
claude --prefill-b64 <base64url-encoded-prompt> --deep-link-cwd-b64 <base64url-encoded-cwd>
claude --deep-link-repo=<repo> --deep-link-origin=<origin> --deep-link-last-fetch=<timestamp>
```

Details:
- `--prefill-b64`: Base64url-encoded text to prefill into the prompt
- `--deep-link-cwd-b64`: Base64url-encoded working directory path
- `--deep-link-repo`: Repository identifier for the deep link
- `--deep-link-origin`: Origin identifier for deep-link launches
- `--deep-link-last-fetch`: Timestamp of last fetch for deep-link context
- Includes extensive validation: rejects Unicode bidirectional control characters, UNC/network paths, and paths with un-quotable characters (single quotes, backslashes, exclamation marks, dollar signs, newlines)
- Error messages guide users to reinstall to a safe path if their Claude binary path contains shell metacharacters

Evidence: Deep link argument construction (search for `"--deep-link-cwd-b64"` and `"--prefill-b64"`)


### Event-Driven Trigger System for GitHub and Slack

What: New structured trigger types for scheduling agent workflows based on external events from GitHub pull requests and Slack messages, replacing the older string-based format.

Details:
- `github.pull_request.opened` — triggers when a PR is opened (replaces deprecated `github:pull-request-opened`)
- `github.pull_request.merged` — triggers when a PR is merged (replaces deprecated `github:pull-request-merged`)
- `slack.message` — triggers on Slack messages, with channel filtering via the `where` clause
- Deprecated formats produce helpful migration messages: e.g., `'; use 'on: github.pull_request.opened'`
- Trigger definitions use the new `on:` entry format and support structured event objects like `{event: slack.message, channel: #channel}`
- Includes comprehensive validation with error messages for invalid triggers, cron expressions, and event formats

Evidence: Trigger definitions (search for `"github.pull_request.merged"` and `"slack.message"`)


### Where Clause Predicate Language

What: A new structured filtering syntax for specifying conditions on event triggers and data queries, supporting a rich set of comparison operators.

Details:
- Operators: `is`, `is_not` (single values), `one_of`, `none_of` (list values), `starts_with`, `contains`, `matches`
- Provides clear error messages for malformed predicates:
  - `where: empty list for "field"` — when a list operator receives an empty array
  - `where: unknown op "op"` — for unrecognized operators
  - `where: "field" takes a single value; use one_of/none_of for a list` — for type mismatches
  - `where: must be a map of field→predicate, or a list of single-field maps` — for structural errors
- Scalars and objects cannot be mixed: `where: "field" mixes scalars and objects; use {one_of: [...]} or an op object`

Evidence: Predicate operator definitions (search for `"one_of"` and `"none_of"`)


### Daemon Backend for Background Agents

What: A new `backend` configuration option that lets background agents run via a daemon process instead of tmux.

Usage:
Configure in settings:
```json
{
  "backend": "daemon"
}
```

Details:
- Two supported values: `"tmux"` (default) and `"daemon"`
- When set to `"daemon"`, background agent sessions use a detached daemon process instead of creating tmux panes
- Tmux remains the default; the daemon option provides an alternative for environments where tmux is not available or not desired
- Related: new `autoAddRemoteControlDaemonWorker` setting for automatically configuring daemon workers

Evidence: Backend schema definition (search for `backend: E.enum(["tmux", "daemon"])`)


### Custom Session Titles via SDK Protocol

What: The SDK initialize protocol now accepts a `title` parameter, allowing programmatic callers to set a custom session title at launch.

Details:
- When provided, the session uses the custom title and skips automatic title generation
- Has no effect on the persisted title when resuming an existing session
- Also adds a `customTitle` field to the session schema for user-set titles via `/rename`
- The `/rename` command description now mentions that the title appears in the "prompt box, /resume picker, and terminal title" (previously only "/resume and terminal title")

Evidence: SDK protocol schema (search for `"Custom session title. When provided"`)


### Network Denied Domains Configuration

What: Expanded network security with a new `deniedDomains` field that blocks specific domains even if they match `allowedDomains` rules.

Details:
- Accepts an array of domain strings with wildcard support (same syntax as `allowedDomains`)
- Merged from all settings sources regardless of `allowManagedDomainsOnly` — meaning organization policies can always enforce domain blocking
- Takes priority over `allowedDomains`: a domain matched by both lists is blocked
- Logs denials with the specific domain and port for debugging

Evidence: Schema definition (search for `"Domains that are always blocked, even if matched by allowedDomains"`)


### In-App Feedback Submission

What: Users can now submit feedback directly from the CLI, with clear success and error messaging.

Details:
- New success message: "Feedback sent"
- Error messages provide actionable guidance:
  - "Couldn't send feedback: not signed in. Run /login, then retry."
  - "Couldn't send feedback. If it keeps failing, you can file at [URL]"
- UI includes "Press any key to close" prompt after submission

Evidence: Feedback messaging (search for `"Feedback sent"` and `"Couldn't send feedback"`)


### Update Safety Guards

What: New validation prevents `/update` when it could cause problems.

Details:
- "Cannot /update while background tasks are running — wait for them to finish, then try again." — prevents mid-task updates that could disrupt running agents
- "Cannot /update — session transcript is in a different project directory than the child would resolve. Exit the worktree or restart manually." — prevents update failures in worktree contexts

Evidence: Update guard messages (search for `"Cannot /update while background tasks"`)


### Team Onboarding Guide Generator

What: A new system for generating personalized team onboarding guides based on usage analytics.

Details:
- Generates a "Welcome to [Team Name]" document with:
  - Work type breakdown (build features, fix bugs, refactor, etc.) with ASCII bar charts
  - Top skills and commands with usage frequency
  - Top MCP servers with call counts
  - Setup checklist for new team members
- Powered by an LLM prompt that analyzes session descriptors and derives work-type percentages
- Complements the existing Insights dashboard feature

Evidence: Onboarding template (search for `"# Welcome to [Team Name]"`)


### Agent Stall Detection

The stream watchdog now detects when agents make no progress for an extended period and surfaces an actionable error: "Agent stalled: no progress for Ns (stream watchdog did not recover)". Previously, stalled agents could hang silently.

Evidence: Stall detection (search for `"Agent stalled: no progress for"`)


### Unclean Session Recovery

A new message "Prior session exited uncleanly" notifies users when resuming a session that didn't terminate gracefully, helping them understand potential context gaps.

Evidence: Recovery notification (search for `"Prior session exited uncleanly"`)


### Improved Effort Level Messaging

The effort level notification changed from "Effort level set to auto" to "Effort level set to max", providing clearer feedback when effort is maximized. The "ultrathink" keyword now triggers a system prompt explaining that deeper reasoning is being applied.

Evidence: Effort messaging (search for `"Effort level set to max"`)


### Enhanced /loop Tick Prompts

The autonomous loop tick prompts were significantly rewritten to provide clearer numbered steps and better explain dynamic pacing behavior. The prompt header changed from "# Autonomous loop tick" to "# /loop tick", and scheduled task prompts now include explicit step-by-step instructions.

Evidence: Loop prompt changes (search for `"/loop tick"`)


### CJK Punctuation Support in Mentions

The @-mention detection regex now recognizes CJK punctuation marks (。、？！) as valid word boundaries, improving mention detection in Chinese, Japanese, and Korean text. Previously, typing `@file。` wouldn't trigger autocomplete, but now it does.

Evidence: CJK regex patterns (search for `"\u3002\u3001\uFF1F\uFF01"`)


### ANSI Color Output on Windows

Removed a Windows platform check that was blocking ANSI color output, enabling colored terminal output regardless of detected platform.

Evidence: Color enablement (search for `K6K` in the annotations — removed `if (process.platform === "win32") return !1`)


### Improved Plugin Configuration Error Messages

Plugin option validation now provides more actionable guidance: `Plugin option "..." isn't set. Open /plugin manage to configure it, or check that the plugin's userConfig schema declares "..."`. This helps users quickly fix misconfigured plugins.

Evidence: Plugin error message (search for `"isn't set. Open /plugin manage to configure it"`)


### Permission Denial Context in Don't-Ask Mode

When a tool permission is denied in "don't ask" mode, the denial message now explicitly explains: "Permission to use [tool] has been denied because Claude Code is running in don't ask mode." This provides clearer context for why an action was blocked.

Evidence: Denial messaging (search for `"denied because C"` in the annotations for `PL7`)


### Improved Bash Tool Instructions

The Bash tool help text now explicitly instructs the model to never prepend `cd <current-directory>` before commands, reducing unnecessary directory changes in generated commands.

Evidence: Bash tool help (search for `"never prepend"`)


### CLI Terminology Update

"Exit the REPL" has been renamed to "Exit the CLI" throughout the interface, reflecting the product's evolution from a simple read-eval-print loop to a full CLI application.

Evidence: Terminology change (search for `"Exit the CLI"`)


### Sandbox Override Permission Support

The permission decision system now supports a `sandboxOverride` reason type, allowing sandbox-level permission overrides to be distinguished from regular permission grants in the UI and telemetry.

Evidence: Sandbox override (search for `"sandboxOverride"`)


### Concurrent Session Detection

New session lifecycle management detects concurrent CLI sessions across multiple process types (interactive, background, loop) and validates via Zod schema, helping prevent resource conflicts.

Evidence: Session detection (search for `xZ$` in annotations)


### Improved API Error Formatting

API errors that contain JSON-formatted messages are now detected and parsed for better display, rather than showing raw JSON strings to users.

Evidence: JSON error parsing (search for `JMH` in annotations — `if (H.message.includes('{"'))`)


### Telemetry Request ID Tracking

New `clientRequestId` and `requestId` fields are now tracked in telemetry payloads, enabling better request correlation for debugging and support.

Evidence: Request ID fields (search for `"clientRequestId"`)


## Bug Fixes

- Fixed ANSI escape sequence handling to include the CSI alternate sequence (`\x9B`), resolving potential display issues in some terminals (search for `"uwK"` in annotations)
- Fixed string truncation returning incorrect length by changing the return to use the length parameter variable instead of a different variable (search for `VK` in annotations — `return z + "…" → return K + "\u2026"`)
- Fixed DEL character (`\x7F`) handling in interactive text input — previously the DEL character was treated as empty string, now it's correctly recognized as a delete action (search for `"c4$"` in annotations)
- Fixed backspace key handling to recognize the `\x7F` (DEL) character code alongside `\b` (search for `"c4$"` — `O === '' || O === '\b' → A === '\x7F' || A === '\b'`)
- Fixed Ctrl+U (delete to line start) to use proper `deleteToLineStart()` method instead of dispatching a raw text replacement (search for `"qI"` in annotations)
- Improved Unicode normalization throughout the CLI — hundreds of literal Unicode characters (middle dots, em dashes, ellipses, arrows, box-drawing characters) are now consistently represented as escape sequences, preventing rendering issues in terminals that handle raw Unicode differently


## In Development

Features with infrastructure added but not yet enabled. These are shipped "dark" and may become available in future versions.


### Message Timestamps [In Development]

What: Shows a timestamp above each assistant message, giving users a clear timeline of the conversation.

Status: Feature-flagged — gated by `tengu_silk_hinge` (disabled by default)

Details:
- New `showMessageTimestamps` setting (boolean, global scope)
- Description: "Show a timestamp above each assistant message"
- Setting is hidden from the settings UI when the feature flag is off
- Full implementation exists: the timestamp rendering, state management, and cache key integration are all in place
- When enabled, timestamps appear above assistant messages in the chat transcript

Evidence: Feature flag disabled (search for `C$("tengu_silk_hinge", !1)`)


### tengu_amber_lynx [In Development]

What: Purpose unknown — the feature flag is defined but its associated functionality is not clearly documented in user-facing strings.

Status: Feature-flagged — gated by `tengu_amber_lynx` (disabled by default)

Details:
- Used in a component related to git/terminal state rendering
- Single reference: `Z = C$("tengu_amber_lynx", !1)`
- No user-facing strings or tips associated with this flag

Evidence: Feature flag disabled (search for `C$("tengu_amber_lynx", !1)`)


### Linux-Only Build

This version is built as a Linux-only binary. All `process.platform` detection has been replaced with hardcoded `"linux"` values (via `switch ("linux")` replacing `switch (process.platform)`). The Windows and macOS code paths remain in the bundle as dead code but are unreachable. Specific impacts:

- Computer use is restricted: "createCliExecutor called on linux. Computer control is macOS-only."
- Windows PowerShell process introspection has been removed
- macOS-specific clipboard image handling has been removed
- Platform-specific update URLs will only return Linux paths
- Voice mode's Windows-specific check has been removed (the feature itself still requires the native audio module)
- The native installer reports "Unsupported architecture: x64" because architecture detection is also hardcoded

This is a build-time artifact of the npm package targeting Linux. macOS and Windows users should use the native installer for their platform rather than the npm package.


### Massive Internal Refactoring: Native Node.js Modules

The most significant internal change in this release is a wholesale migration from bundled polyfills and custom wrappers to native Node.js built-in modules:

- **Removed bundled libraries**: WebSocket (`ws` client/server), undici HTTP client, Fetch API polyfill, URL/URLSearchParams polyfill, YAML parser, FormData implementation, Bidirectional Text Algorithm, HTTP/1.1 and HTTP/2 protocol handlers
- **Replaced with**: Direct `require()` calls to Node.js built-ins (`fs`, `fs/promises`, `path`, `crypto`, `os`, `url`, `http`, `http2`, `stream`, `child_process`, `net`, `events`, `buffer`, `util`, `vm`, `module`)
- **Custom file system wrappers removed**: The 40+ method `kv5` filesystem abstraction layer was removed in favor of direct `fs` and `fs/promises` calls throughout the codebase
- Over 100 scattered module imports were consolidated into centralized initialization blocks
- Custom UUID generation replaced with `crypto.randomUUID()` across dozens of call sites
- Custom path utilities replaced with `path.join()`, `path.resolve()`, `path.basename()`, etc.

This results in a smaller bundle size and better alignment with the Node.js runtime.


### AWS Bedrock SDK Integration

A complete AWS SDK v3 integration for Bedrock Runtime has been added, including:
- Bedrock Runtime client with full middleware stack
- AWS Signature Version 4 (SigV4) request signing
- OAuth2 credential provider for AWS login flows
- ECS/EKS container credentials support
- Assume Role with MFA support
- 30+ Bedrock API command definitions (guardrails, inference profiles, model management)
- AWS STS client for credential operations
- EventStream marshalling for real-time bidirectional communication

This replaces the previous Bedrock integration approach with a more complete, standards-compliant AWS SDK implementation.


### Embedded Documentation Refresh

SDK documentation embedded in the CLI has been refreshed with updated guides for:
- Python (Files API, Streaming, Tool Use, Managed Agents, Core API)
- TypeScript (Messages, Batches, Files, Prompt Caching, Tool Use)
- Ruby (Installation, Client initialization, Messages)
- C# (Client initialization, Messages)
- Model migration guide for upgrading to newer Claude models
- Verification guides for CLI and server/API changes

Several older documentation blocks were removed and replaced with updated versions reflecting current API patterns.
