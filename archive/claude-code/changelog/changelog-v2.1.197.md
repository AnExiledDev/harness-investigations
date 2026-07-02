# Changelog for version 2.1.197

## Summary

This release promotes Claude Sonnet 5 to the default model across all first-party surfaces, replacing Claude Sonnet 4.6. The model picker gains two new schema fields (`resolvedModel` and `promoListPrice`) that expose canonical model IDs and launch-promo pricing to rich clients. A small fix normalizes an internal entrypoint identifier that could cause routing issues in local-agent mode.


## New Features


### Claude Sonnet 5 is now the default model

What: `claude-sonnet-5` replaces `claude-sonnet-4-6` as the default sonnet-tier model for first-party Anthropic API users. Claude Sonnet 4.6 moves to the "previous Sonnet" slot and remains available.

Details:
- Default for first-party API: `claude-sonnet-5`
- Default for Bedrock, Vertex, Foundry, Mantle: unchanged (`claude-sonnet-4-5` or `claude-sonnet-4-6` depending on provider)
- Bedrock gateway and `anthropic_aws` provider defaults updated to `claude-sonnet-4-6` (one version behind first-party, as usual)
- `latest_per_family.sonnet` updated to `claude-sonnet-5`
- Sonnet 4.6 is now labeled "Sonnet 4.6 · Previous Sonnet version" in the model picker

Evidence: default sonnet alias updated in model registry (search for `"claude-sonnet-5"` in model config's `sonnet.default` field)


### Claude Sonnet 5 full model entry

What: A complete model definition for `claude-sonnet-5` is now in the registry, including context limits, capability flags, Vertex region support, and provider IDs.

Details:
- 1M context window with `native_1m: true` and `native_1m_3p: { bedrock: true, vertex: true, foundry: true }`
- Output/extended limits: 64k / 128k tokens (same as Fable 5, Opus 4.8)
- Capabilities: `effort`, `max_effort`, `xhigh_effort`, `adaptive_thinking`, `mid_conv_system`, `context_management`
- Default effort: `high`
- Image limits: 2000x2000 px
- Provider IDs cover first-party, Bedrock (`us.anthropic.claude-sonnet-5`), Vertex, Foundry, Mantle (`anthropic.claude-sonnet-5`), Gateway, and `anthropic_aws`
- Knowledge cutoff: January 2026
- New Vertex region env var: `VERTEX_REGION_CLAUDE_5_SONNET`

Evidence: full model entry in model database (search for `"claude-sonnet-5"` near `knowledge_cutoff: "January 2026"`)


### Launch promo pricing shown in model picker

What: While a launch promotion is active, the Sonnet 5 model picker entry shows the promo price (`$2/$10 per Mtok`) alongside an expiry date. Rich clients (those that read the new `promoListPrice` field) can additionally display the regular list price (`$3/$15`) struck through.

Details:
- Promo price shown in the `description` field: `Sonnet 5 · <price> · $2/$10 per Mtok · promo through <date>`
- List price exposed in the new `promoListPrice` field: `"$3/$15"`
- When no promo is active, the field is absent and the description shows the normal price string
- The 1M-context Sonnet 5 entry follows the same pattern

Evidence: promo formatting logic (search for `"$2/$10 per Mtok"` and `"promo through"`)


### New model schema fields: `resolvedModel` and `promoListPrice`

What: The model info schema (used by the `/api/models` endpoint and the model picker) gains two optional fields.

`resolvedModel`: the canonical wire model ID that an alias row's `value` resolves to. Example: a row with `value: "sonnet"` now carries `resolvedModel: "claude-sonnet-5"`. Hosts can use this to match a persisted explicit model ID against the alias row that covers it without doing alias expansion themselves.

`promoListPrice`: the regular list price for a model currently on a launch promo. Present only when a promo is active; absent otherwise. The `description` field carries the promo price so plain-text consumers always see an unambiguous price; rich pickers prepend the struck-through list price.

Evidence: both fields added to the model info Zod schema (search for `"Canonical wire model id this row"` and `"List price (e.g. \`$3/$15\`)"`)


## Improvements


### Hook config examples updated to Sonnet 5

What: The `.describe()` strings on the `model` field for both agent hooks and prompt hooks now reference `claude-sonnet-5` as the example model ID instead of `claude-sonnet-4-6`.

Before: `Model to use for this agent hook (e.g., "claude-sonnet-4-6"). If not specified, uses Haiku.`
After: `Model to use for this agent hook (e.g., "claude-sonnet-5"). If not specified, uses Haiku.`

This is documentation only -- the schema behavior is unchanged. If you have `claude-sonnet-4-6` hardcoded in a hook `model` field it will keep working.

Evidence: hook schema `.describe()` strings (search for `"Model to use for this agent hook (e.g., \"claude-sonnet-5\")"`)


### 1M context availability check updated for Sonnet 5

What: The check that decides whether the 1M context variant is available now includes `claude-sonnet-5` alongside the existing set of models that natively support 1M on third-party providers. When your account lacks 1M access, the error message now mentions "Sonnet 5 with 1M context" instead of the previous generic wording.

Evidence: `FIi = new Set(["claude-sonnet-5"])` (search for `"Sonnet with 1M context is not available for your account"`)


### Model compatibility lists updated for Sonnet 5

What: Several internal lists that track which models support features like extended output, third-party streaming, and cost classification now include `claude-sonnet-5`. This ensures that billing, effort-level controls, and eager input streaming behave correctly with the new model.

Evidence: model identifier added to feature-support sets (search for `"claude-sonnet-5"` near `"claude-sonnet-4-6"` in model capability arrays)


## Bug Fixes

- Fixed `CLAUDE_CODE_ENTRYPOINT=local_agent` (underscore) not being recognized as the `local-agent` (hyphen) entrypoint. The entrypoint normalizer now rewrites the underscore form to the canonical hyphen form on startup, so SDK integrations that set the underscore variant will no longer be routed incorrectly. (search for `"local_agent"` near `"local-agent"`)

---

Generated with:
- tool: `harness-investigations@0c752ef-dirty`
- provider: `claude`
- model: `claude-sonnet-4-6`
- primary diff: `archive/claude-code/changes/changes-v2.1.197.md` (filtered astdiff)
- string diff: `archive/claude-code/changes/string-diff-v2.1.197.txt`
