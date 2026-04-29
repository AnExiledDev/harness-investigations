# Changelog for version 2.1.100

## Summary

This release adds reassuring status messages during extended thinking periods, relaxes the stall detection thresholds so the spinner no longer shows a "stalled" state prematurely, and tightens several system prompt sections to produce more concise responses. Opus 4.6 users with a server-side flag may also see stricter word-count limits on responses.


## New Features


### Extended Thinking Status Messages

What: During long thinking periods, Claude Code now displays timed reassurance messages so you know it's still working.

Details:
- After 30 seconds of thinking: "Thinking a bit longer… still working on it…"
- After 90 seconds: "This is a harder one… it might take a few more minutes…"
- After 270 seconds (~4.5 minutes): "Hang tight… really working through this one…"
- Messages appear as dimmed text below the spinner and disappear when thinking ends
- Only displays when the model is in the "thinking" state (extended thinking / chain-of-thought)

Evidence: Thinking status message array with `afterMs` timings (search for `"Thinking a bit longer"`)


### Numeric Length Anchors for Opus 4.6 [Gradual Rollout]

What: A new system prompt section that enforces strict word-count limits on Claude's text output when using Opus 4.6.

Details:
- Text between tool calls is limited to ≤25 words
- Final responses are limited to ≤100 words unless the task requires more detail
- Only active when using the Opus 4.6 model AND the server-side `quiet_salted_ember` flag is set to `"true"`
- Injected as a `numeric_length_anchors` prompt section in the system prompt

Evidence: Length anchor prompt section (search for `"numeric_length_anchors"` and `"≤25 words"`)


## Improvements


### Relaxed Stall Detection During Thinking

The stall detection threshold was increased from 3 seconds to 10 seconds, and the intensity ramp-up period was extended from 2 seconds to 10 seconds. Additionally, the thinking state is now explicitly treated as an active state for stall detection purposes. Together, these changes mean the spinner no longer incorrectly indicates a "stalled" connection during legitimately long thinking periods.

Evidence: Stall threshold change from `3000` / `2000` to `1e4` / `1e4` (search for `j > 1e4` in the stall detection function `k87`), and added `q === "thinking"` condition in the calling code


### More Concise End-of-Turn Summaries

The system prompt guidance for end-of-turn summaries was simplified from "state what changed and what's next. That's it — no recapping the journey, no restating the problem, no listing everything you considered" to the more direct "one or two sentences. What changed and what's next. Nothing else."

Evidence: Updated summary instruction (search for `"End-of-turn summary: one or two sentences"`)


### Shorter Exploratory Question Responses

When the user asks an open-ended or exploratory question, Claude is now instructed to respond in 2–3 sentences with a recommendation and the main tradeoff, rather than providing extended analysis with multiple options and tradeoffs. This makes exploratory exchanges snappier while still waiting for user agreement before implementing.

Evidence: Updated exploratory question prompt (search for `"respond in 2-3 sentences with a recommendation"`)


### Removed Verbose Communication / Output Efficiency Prompt Section

The standalone "# Communicating with the user" prompt section (for Opus 4.6 users) and the "# Output efficiency" prompt section (for other users) were both removed from the system prompt assembly. Their guidance is now covered by the tighter communication style instructions and the new numeric length anchors.

Evidence: Both `"Communicating with the user"` and `"Output efficiency"` strings are absent from v2.1.100 (confirmed via search)
