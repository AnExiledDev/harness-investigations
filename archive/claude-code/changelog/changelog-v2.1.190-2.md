# Changelog for version 2.1.190

## Summary

This release focuses on Fable 5 rate-limit handling, adding a new "overage-included" quota tier for plans that bundle Fable 5 usage, improved limit messaging that distinguishes included-quota exhaustion from credit depletion, and per-model weekly usage data in the `/usage` API response. A startup announcement system that filters by required model is also wired in.


## New Features


### Fable 5 Overage-Included Limit Tier

What: Plans that include a fixed weekly quota of Fable 5 usage now have their own rate-limit type (`seven_day_overage_included`), distinct from the general weekly limit and from the pure credits-required state. When users exhaust this included quota, the UI tells them clearly that further Fable 5 usage will draw from usage credits rather than showing a generic rate-limit error.

Details:
- New rate limit type `seven_day_overage_included` is mapped to the label "Fable 5 limit" in all UI surfaces.
- When this limit triggers, users see: "You've reached your Fable 5 limit" and "You've used your included Fable 5 usage for this week. Continuing on Fable 5 uses usage credits"
- The upgrade/switch prompt adjusts its heading to "You've reached your Fable 5 limit" (mid-session, without a credits plan) rather than the generic "Fable 5 now uses usage credits".
- The overage-UI is suppressed for this limit type — users in the overage-included tier no longer see the extra-usage dialog; instead they get the credit-purchase flow directly.
- Rate limit header parsing now recognises the `7d_oi` server header suffix and maps it to `seven_day_overage_included`.

Evidence: New rate limit type label (search for `"Fable 5 limit"`) and header abbreviation (search for `"7d_oi"`)


### Model-Scoped Rate Limit Data in Usage API

What: The `/usage` API endpoint (used by the SDK and the daemon's `get_context_usage` subtype) now includes a `model_scoped` field containing per-model weekly usage windows derived from the server's `limits[]` array.

Details:
- Each entry has `display_name` (e.g. "Fable"), `utilization` (0–1 or null), and `resets_at` (ISO-8601 timestamp or null).
- The field is additive — it is present only when the server emits compatible limit objects.
- The list is filtered by an allowlist of overage-included model buckets before being returned.
- If projection fails at runtime it logs `model_scoped projection failed:` and omits the field rather than breaking the response.

Evidence: New schema field (search for `"Per-model weekly windows from the server limits[] array"`) and error log (search for `"model_scoped projection failed:"`)


### Startup Announcements Filtered by Required Model

What: The in-app announcement system (which surfaces one-time notices at startup) now supports a `requiresModel` field. An announcement is only shown to users whose active model satisfies the requirement, preventing model-specific notices from appearing to users on unrelated models.

Details:
- A new helper checks `requiresModel` against the currently active model before including an announcement in the candidate list.
- The highest-priority eligible announcement is serialised and passed as `startupAnnouncement` in the initial startup data.
- This is wired into the telemetry startup payload as `startup_announcement`.

Evidence: New model filter for announcements (search for `"requiresModel"`) and startup data key (search for `"startupAnnouncement"`)


## Improvements


### Clearer Fable 5 Model Picker Description

The description shown next to Fable 5 in the model picker has been updated. Previously it alternated between "Draws from usage credits" (for credits users) and "Uses your limits ~2× faster than Opus" (for limits users). It now uniformly shows "· Requires usage credits" for users on credits-only plans, and is omitted entirely for other users.

Evidence: Picker description change (search for `"Requires usage credits"`) — old strings `"Draws from usage credits"` and `"Uses your limits ~2× faster than Opus"` are removed.


### Credits-Only Tier Detection via Feature Flag

A new server-controlled flag `tengu_saffron_credits_only_tiers` specifies which subscription tier strings (e.g. `"enterprise"`) are treated as requiring usage credits for Fable 5. Enterprise accounts without Fable 5 included in their plan are automatically placed in this group regardless of the flag. A companion flag `tengu_saffron_picker_dim` controls whether the Fable 5 entry in the model picker is visually dimmed.

Evidence: New feature flag (search for `"tengu_saffron_credits_only_tiers"`) and dim flag (search for `"tengu_saffron_picker_dim"`)


### Overage Disabled Reason Extracted from Server Response

The error handler for 429 rate-limit responses now extracts `disabled_reason` directly from the server's error JSON body and surfaces it as `overageDisabledReason`. Previously this value was only read from a response header or a cached field. Having it in the parsed error object allows more accurate messaging without a round-trip or stale cache.

Evidence: New extraction path (search for `"disabled_reason"` in the rate-limit error parser)


### Saffron (Fable 5 Credits) Eligibility Refined

The check for whether a user is on a usage-credits plan now respects an `enabled: false` flag from the server's saffron configuration, immediately returning `false` if the server has explicitly disabled the feature for the account. It also no longer falls back to the `hir()` hire-mode check. This makes the credits-plan detection more precise and server-authoritative.

Evidence: New `enabled` field guard (search for `"e.enabled === !1"` in the saffron eligibility function)


## Bug Fixes

- Fable 5 extra-usage prompt no longer appears when the rate-limit type is `seven_day_overage_included`. Users in this tier were previously shown the extra-usage upgrade dialog before being redirected to the credit-purchase flow, creating a confusing double-prompt. (search for `"seven_day_overage_included"` in the rate-limit UI component)

- Prepaid credit balance fetch now returns `null` gracefully (tracked as `not_supported`) when the API endpoint returns a non-numeric amount field, instead of propagating an unexpected value downstream. (search for `"api_prepaid_balance_fetch"` and `"not_supported"`)

- After a successful usage-credit purchase, the session's Fable-5 eligibility state is now refreshed immediately alongside recording the purchase. Previously the state update was missing from the post-purchase callback, which could cause the model picker to still show Fable 5 as unavailable until the next full reload. (search for `"buy_success"` in the usage-credits flow)

- Overage-in-use notifications are suppressed for users in the `seven_day_overage_included` tier who are already drawing from their included quota (`isUsingOverage === true`), preventing a spurious "you're using extra usage" notification from firing for that case. (search for `"seven_day_overage_included"` in the rate-limit notification handler)

---

Generated with:
- tool: `harness-investigations@66416d2-dirty`
- provider: `claude`
- model: `claude-sonnet-4-6`
- primary diff: `archive\claude-code\changes\changes-v2.1.190-2.md` (filtered astdiff)
- string diff: `archive\claude-code\changes\string-diff-v2.1.190.txt`
