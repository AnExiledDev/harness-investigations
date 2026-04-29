# Changelog for version 2.1.109

## Summary

This release redesigns the thinking progress indicator that appears while Claude is processing a response. The new indicator starts showing feedback much sooner (1 second vs 10 seconds), features an animated spinner with a "Thinking" heading, and cycles through a larger set of playful, whimsical status messages over a longer time window.

### Redesigned Thinking Progress Indicator

What: The progress messages shown while Claude is thinking have been completely overhauled with a new visual design, faster initial feedback, and more personality.

Details:
- The indicator now appears after just **1 second** of thinking, down from 10 seconds previously
- Features a proper animated spinner with a "Thinking" heading, replacing the old dim `›` pointer style
- The message set expanded from 5 to 14 messages, covering up to 2 minutes 45 seconds of thinking time (previously capped at 2 minutes)
- Messages have a more playful, lighthearted tone compared to the old apologetic style
- The indicator is now rendered as a dedicated component within the message list area, rather than appended below the conversation

The new message progression:

| Time | Message |
|------|---------|
| 1s | "Hmm…" |
| 6s | "This one needs a moment…" |
| 12s | "Working through it…" |
| 20s | "Untangling some thoughts…" |
| 28s | "Weighing a few approaches…" |
| 36s | "Consulting the rubber duck…" |
| 48s | "Cross-referencing seventeen theories…" |
| 60s | "Double-checking the double-checks…" |
| 80s | "Almost there…" |
| 108s | "Pacing in small circles…" |
| 120s | "Reticulating splines…" |
| 135s | "Hmm…?" |
| 150s | "Staring thoughtfully into the middle distance…" |
| 165s | "Still here, still at it…" |

Previously, only 5 messages were shown starting at 10 seconds, with text like "Thinking a bit longer… still working on it…" and "Taking the time to get this right… thanks for your patience…"

Evidence: Thinking hint component with animated spinner (search for `"Consulting the rubber duck"` or `"Reticulating splines"`). The component is passed via the new `showThinkingHint` prop and renders with a `Thinking` heading and animated spinner indicator.
