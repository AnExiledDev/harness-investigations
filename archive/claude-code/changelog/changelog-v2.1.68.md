# Changelog for version 2.1.68


## Summary

This release re-enables the "ultrathink" keyword as a way to boost reasoning effort to high for the current turn, complete with a new rainbow shimmer visual effect. It also adds a `CLAUDE_CODE_DISABLE_LEGACY_MODEL_REMAP` environment variable to let users opt out of automatic model remapping to Opus 4.6, and introduces a redesigned server-controlled effort selection dialog.


### Ultrathink keyword re-enabled as effort boost

What: Typing "ultrathink" in a message now sets reasoning effort to "high" for that turn. In the previous version, ultrathink was deprecated and showed a dismissive message — it now has real functionality again.

Usage:
```
ultrathink about the architecture of this codebase and suggest improvements
```

Details:
- When "ultrathink" appears anywhere in your message, effort is automatically set to high for that turn
- A notification briefly displays: "Effort set to high for this turn"
- The word "ultrathink" is rendered with a rainbow color shimmer effect in the terminal (cycling through red, orange, yellow, green, blue, indigo, and violet)
- Controlled by the `tengu_turtle_carbon` feature flag (defaults to enabled)
- Replaces the old "Ultrathink no longer does anything. Thinking budget is now max by default." deprecation message

Evidence: Ultrathink effort injection (search for `"ultrathink_effort"`) — `rqY()` at line ~290076 checks `jd()` (`"tengu_turtle_carbon"`) and `Vf7()` (`/\bultrathink\b/i`)


### Legacy model remap opt-out

What: Users who were automatically migrated from legacy Opus models to Opus 4.6 can now opt out by setting an environment variable.

Usage:
```bash
export CLAUDE_CODE_DISABLE_LEGACY_MODEL_REMAP=1
```

Details:
- When your model is auto-remapped to Opus 4.6, the notification now reads: "Model updated to Opus 4.6 · Set CLAUDE_CODE_DISABLE_LEGACY_MODEL_REMAP=1 to opt out"
- The notification displays for 8 seconds (up from 3) when the opt-out message is shown, giving you time to read the instructions
- Setting the environment variable to `1` disables the automatic model remapping entirely
- The remap behavior is also gated by the `tengu_grey_wool` feature flag (defaults to enabled)

Evidence: Model remap opt-out (search for `"CLAUDE_CODE_DISABLE_LEGACY_MODEL_REMAP"`) — `gy1()` at line ~535228


### Effort selection dialog redesigned

The effort callout dialog for Opus 4.6 users has been redesigned with server-configurable content and a simplified option set.

Details:
- Dialog title and description are now fetched from the server (via `tengu_grey_step2` feature flag) instead of being hardcoded
- Options are simplified to three clear choices:
  - "Use medium effort (recommended)"
  - "Use high effort"
  - "Use low effort" (new — previously only medium and high were offered)
- Removed verbose per-option descriptions and the "(current)" suffix labeling
- Uses a separate dismiss state (`effortCalloutV2Dismissed`) so users who dismissed the old dialog may see the new one

Evidence: Server-controlled effort dialog (search for `"tengu_grey_step2"`) — `zb6()` at line ~162660, dialog at `ohq()` line ~588325


### Removed silent medium-effort auto-migration

The automatic migration that silently set Opus 4.6 effort to "medium" has been removed.

Details:
- Previously, on startup, the app would set `opus46EffortMediumMigrationTimestamp` and briefly flash "Opus 4.6 effort updated to medium"
- This silent migration has been completely removed — effort is no longer changed behind the scenes
- Default effort for Opus 4.6 is now determined by feature flags (`tengu_quartz_falcon`, `tengu_grey_step2`) rather than a one-time migration

Evidence: Removed migration function (search for `"opus46EffortMediumMigrationTimestamp"` — present in v2.1.67, absent in v2.1.68)


### Server-controlled effort dialog [Gradual Rollout]

What: The redesigned effort dialog described above is gated behind the `tengu_grey_step2` feature flag, which defaults to `{ enabled: false }`.

Status: Feature-flagged (disabled by default, server-controlled rollout)

Details:
- The `tengu_grey_step2` flag controls whether the dialog appears and provides its title and description text
- A separate `tengu_quartz_falcon` flag also influences the default effort level for Opus 4.6
- First-party users who previously dismissed the old effort dialog won't see the new one until `tengu_grey_step2` is enabled server-side
- API users (`By()` or `wb6()`) can also be enrolled via the same flag

Evidence: Dialog visibility (search for `"effortCalloutV2Dismissed"`) — `zIq()` at line ~588370 checks `zb6().enabled`
