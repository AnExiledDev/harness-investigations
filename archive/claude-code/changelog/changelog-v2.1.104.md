# Changelog for version 2.1.104

## Summary

This is a focused reliability release that adds byte-level stream idle timeout detection to catch stalled API connections more quickly. It also includes a minor refinement to the internal system prompt heading for clarity.


## Improvements


### Byte-level stream idle timeout detection

What: API streaming responses are now monitored at the byte level for idle connections, catching stalled streams that the existing chunk-level timeout might miss.

Details:
- A new `StreamIdleTimeoutError` class and `TransformStream` wrapper monitor the raw byte stream from the API. If no bytes arrive within the timeout window, the stream is aborted and retried.
- The timeout is controlled by the existing `CLAUDE_STREAM_IDLE_TIMEOUT_MS` environment variable (default: 90 seconds, minimum: 15 seconds).
- This is layered on top of the pre-existing chunk-level idle timeout, providing defense-in-depth: the byte-level check catches low-level TCP stalls, while the chunk-level check handles higher-level protocol issues.
- Error reporting is now more granular — when a stream times out after receiving partial data, the error message distinguishes "Stream idle timeout - partial response received" from "Stream idle timeout - no chunks received", which should improve diagnostics.
- Only applies to first-party and Anthropic AWS streaming connections (SSE `text/event-stream` responses).

Usage:
```bash
# Override the default 90s idle timeout (minimum 15s)
CLAUDE_STREAM_IDLE_TIMEOUT_MS=60000 claude
```

Evidence: New `StreamIdleTimeoutError` class (search for `"stream idle: no bytes for"`) and TransformStream wrapper in fetch middleware (search for `"Streaming idle timeout (byte-level)"`)


### Refined system prompt for text output guidelines

What: The internal system prompt section heading "Communication style" was renamed to "Text output (does not apply to tool calls)" to clarify that the communication guidelines apply only to text output shown to the user.

Details:
- The body of the prompt is unchanged — the same guidance about brief updates, no narration, and clear communication still applies.
- The heading clarification may result in slightly improved model behavior when making tool calls, as the model has a clearer signal that the style guidelines do not constrain tool call formatting.
- This prompt is only active for Opus 4.6 sessions with the `quiet_salted_ember` flag enabled.

Evidence: Heading change from `"# Communication style"` to `"# Text output (does not apply to tool calls)"` (search for `"Text output (does not apply to tool calls)"`)
