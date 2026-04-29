# Changelog for version 2.1.107

## Summary

This release optimizes Opus 4.6 response latency through a new thinking guidance system that reduces unnecessary extended thinking on straightforward tasks, auto-upgrades Opus 4.6 subagents to 1M context windows, and makes "still thinking" progress messages appear much sooner during long operations.


## Improvements


### Thinking Guidance for Opus 4.6 [Gradual Rollout]

What: A new system-level optimization for Opus 4.6 that tunes the model's extended thinking behavior, reducing unnecessary reasoning overhead on simple follow-up messages while preserving full thinking on complex tasks.

Details:
- Adds a `thinking_guidance` section to the system prompt instructing Opus 4.6 to calibrate thinking frequency based on task complexity
- On follow-up turns (after the first assistant response), appends a `<system-reminder>` tag hinting the model to skip thinking blocks for straightforward actions
- Only activates when: using Opus 4.6, thinking is not disabled, and no custom system prompt is set
- Gated by server-side flag `loud_sugary_rock` — rolling out gradually

This should result in noticeably faster responses on simple follow-up requests (e.g., "run the tests", "fix that typo") while maintaining full reasoning depth for complex tasks that need it.

Evidence: Thinking frequency tuning system (search for `"tune your thinking frequency"`) — gated by `loud_sugary_rock` in `clientDataCache`, system reminder at `meK` (search for `"without a thinking block"`)


### Subagent Opus 4.6 Auto-Upgrade to 1M Context

What: Subagents using Opus 4.6 now automatically use the 1M context window when the feature is available, matching the behavior already offered in main conversation model selection.

Details:
- When 1M context is available and the resolved subagent model is Opus 4.6, the `[1m]` suffix is automatically appended
- Applied in both the explicit model override and default model code paths of subagent model resolution
- Does not apply if the model string already includes `[1m]`

Evidence: Auto-upgrade function `nc4` (search for `"opus-4-6"` near `"[1m]"`) applied in subagent model resolution function `Eh6`


### Faster "Still Thinking" Progress Messages

What: The progress messages shown during long-running operations now appear much sooner, reducing the time users wait before seeing reassurance that the model is still working.

Details:
- "Thinking a bit longer… still working on it…" — now at 10s (was 30s)
- "Hang tight… really working through this one…" — now at 30s (was 60s)
- "This is a harder one… it might take another minute…" — now at 50s (was 90s)
- "Still going… thanks for hanging in there…" — now at 80s (was 150s)
- "Taking the time to get this right… thanks for your patience…" — now at 120s (was 240s)

The first progress indicator now appears 3x faster than before (10s vs 30s), providing much quicker feedback during complex reasoning.

Evidence: Timing thresholds in progress message array (search for `"Thinking a bit longer"`)
