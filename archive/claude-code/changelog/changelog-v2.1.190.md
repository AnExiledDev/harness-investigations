# Changelog for version 2.1.190

## Summary

This release introduces a new "Fable 5 included" rate limit tier that tracks weekly Fable 5 usage separately from the main weekly limit, with tailored messaging when that included allocation runs out. Model-scoped rate limit data is now returned by the `/status` endpoint, and in-app announcements can be targeted to specific active models.

## Improvements


### Fable 5 Included-Usage Limit — New Rate Limit Category

A new rate limit type, `seven_day_overage_included`, tracks weekly Fable 5 usage for accounts where a defined amount is bundled into the plan. When this limit is exhausted, Claude Code now displays a specific message instead of the generic overage prompt:

- "You've reached your Fable 5 limit" — shown in the model picker and notifications
- "You've used your included Fable 5 usage for this week. Continuing on Fable 5 uses usage credits" — explains exactly what happens next

Previously, hitting any Fable 5 limit while on an account with usage credits would show the generic model-switch / credits dialog. Users on the new included-usage tier now see a distinct, accurate message. The model-switch prompt is suppressed when this limit type is active, since the appropriate next step is purchasing credits rather than switching models.

Evidence: new rate limit type and display label (search for `"seven_day_overage_included"` and `"Fable 5 limit"`)


### Model Picker Description Simplified for Fable 5

The Fable 5 entry in the model picker no longer shows the older "Draws from usage credits" / "Uses your limits ~2× faster than Opus" / "Included with your plan until …" annotation strings. These have been replaced with a single concise label:

- "· Requires usage credits"

The new label applies whenever Fable 5 requires credits on the current account type, and is omitted when it does not.

Evidence: removed strings (search for `"Draws from usage credits"` / `"· Uses your limits ~2× faster than Opus"` — absent from new version); added string (search for `"· Requires usage credits"`)


### Model-Scoped Rate Limits Returned by `/status`

The internal status endpoint (used by the IDE extensions and the API `get_init_params` call) now includes a `model_scoped` array inside the `rate_limits` object when the server emits per-model windows. Each entry has:

- `display_name` — server-supplied label for the model bucket (e.g. "Fable")
- `utilization` — fraction of the weekly window consumed, or null
- `resets_at` — ISO-8601 timestamp of window reset, or null

This field is additive: it appears only when the server returns per-model data and the list is non-empty. It gives integrators visibility into Fable 5 usage separate from the aggregate weekly limit.

Evidence: new schema field (search for `"Per-model weekly windows from the server limits[] array"` or `"model_scoped projection failed:"`)


### Overage-Disabled Reason Now Read from Error Body

Previously, when a `credits_required` error was returned, the overage-disabled reason was read only from the `anthropic-ratelimit-unified-overage-disabled-reason` response header or from a cached value. The parser now also extracts `disabled_reason` from the error body JSON, providing a more reliable source of the reason and reducing cases where the wrong message was shown.

Evidence: new field extraction (search for `"credits_required"` in the 429 error handler and the `overageDisabledReason` property)


### Credits Balance API: Graceful Handling When Amount is Missing

The prepaid credits balance fetch now checks whether the `amount` field in the API response is a number before using it. If the field is absent (for example, on accounts or regions where the endpoint is not supported), the fetch returns null and records a `not_supported` telemetry event rather than passing undefined through to the balance display.

Evidence: guard added before `ke("api_prepaid_balance_fetch")` (search for `"not_supported"` in prepaid balance fetch context)


### Announcements Now Filter by Active Model

In-app announcements (the tip-bar messages shown at startup) can now declare a `requiresModel` field. An announcement with this field set is only shown when the currently active model matches. Previously all eligible announcements were candidates regardless of the selected model.

The `startup_announcement` value is also now included in the init info payload sent to extensions, allowing the IDE to display the same announcement that the CLI would show.

Evidence: `qCl()` filter function (search for `"requiresModel"` in announcement filter logic) and `startupAnnouncement` in init payload (search for `"startup_announcement"`)


### Credits-Only Tier Detection for Enterprise

A new feature flag `tengu_saffron_credits_only_tiers` (defaulting to `["enterprise"]`) specifies which subscription tiers must always pay usage credits for Fable 5. Enterprise accounts without the overage tier are automatically treated as credits-only. A companion flag `tengu_saffron_picker_dim` allows the model picker entry to be dimmed for these accounts.

The overage consent check (`yae`) was also updated to respect an `enabled: false` field in the saffron plan config, allowing the server to explicitly disable the consent gate.

Evidence: feature flag (search for `"tengu_saffron_credits_only_tiers"`) and consent gate (search for `"tengu_saffron_picker_dim"`)

---

Generated with:
- tool: `harness-investigations@66416d2-dirty`
- provider: `claude`
- model: `claude-sonnet-4-6`
- primary diff: `archive\claude-code\changes\changes-v2.1.190.md` (filtered astdiff)
- string diff: `archive\claude-code\changes\string-diff-v2.1.190.txt`
