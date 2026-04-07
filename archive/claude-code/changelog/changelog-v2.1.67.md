# Changelog for version 2.1.67


## Summary
This is a model lifecycle management release. Users configured with Sonnet 4.5 are automatically migrated to Sonnet 4.6, and users with legacy Opus model strings are migrated to the canonical "opus" alias. Opus 4.6's default medium effort level is now extended to Max and Team plan users, not just Pro.

### Automatic Sonnet 4.5 → Sonnet 4.6 Migration
What: Users whose model setting references `claude-sonnet-4-5-20250929` (or its `[1m]` extended-thinking variant) are automatically migrated to `sonnet` (or `sonnet[1m]`). A notification "Model updated to Sonnet 4.6" is shown briefly after the migration.

Details:
- Applies only to first-party (claude.ai-authenticated) users on Pro, Max, or Team plans
- Extended thinking mode (`[1m]`) is preserved during migration
- Users who have already started at least one session will see the notification; brand-new users will not

Evidence: Sonnet 4.5 to 4.6 migration (search for `"tengu_sonnet45_to_46_migration"` and `"Model updated to Sonnet 4.6"`)


### Automatic Legacy Opus Model String Migration
What: Users configured with explicit old-format Opus model IDs (`claude-opus-4-20250514`, `claude-opus-4-1-20250805`, `claude-opus-4-0`, `claude-opus-4-1`) are automatically migrated to the canonical `opus` alias. A notification "Model updated to Opus 4.6" is shown briefly after the migration.

Details:
- Applies to first-party users only
- A new allowlist (`fXz`) defines the four legacy Opus model strings subject to migration
- The previous Opus 4.5 → Pro migration notification ("Model updated to Opus 4.5") has been replaced by this updated path

Evidence: Legacy Opus migration (search for `"tengu_legacy_opus_migration"` and `"legacyOpusMigrationTimestamp"`)


### Opus 4.6 Medium Effort Default Extended to Max and Team Plans
What: The automatic "medium" effort level default for Opus 4.6 previously applied only to Pro plan users. It now also applies to Max plan users and eligible Team plan users.

Details:
- The previous condition checked only for `plan === "pro"` (via `Yb6()`)
- The new condition checks `LK6() || my() || By()`, which covers Pro, Max, and qualifying Team plans
- A new notification "Opus 4.6 effort updated to medium" is displayed when the effort migration occurs for existing users

Evidence: Expanded plan check in effort default — `BX6()` function (search for `"opus-4-6"` near `"medium"` and `"Opus 4.6 effort updated to medium"`)


### Effort Callout Suppressed for First-Time Users
What: The effort level information callout for Opus 4.6 is now automatically dismissed on a user's very first session, avoiding unnecessary friction for new users.

Details:
- When `numStartups <= 1`, the callout is skipped and `effortCalloutDismissed` is set to `true` immediately
- Existing users who have had multiple sessions will continue to see the callout as before (if not previously dismissed)

Evidence: First-startup guard in effort callout — `ahq()` function (search for `"effortCalloutDismissed"` near `"numStartups"`)
