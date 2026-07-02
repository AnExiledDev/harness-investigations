# Changelog for version 2.1.185

## Summary

This is a small patch release with two user-facing messaging improvements for slow or stalled API connections, a thinking-budget UI change that restricts an advanced display to first-party accounts, and an internal constant doubling that likely raises a timeout or buffer ceiling.

## Improvements


### Clearer messaging when the API is slow to respond

The status message shown during a stalled request has been reworded to be less alarming and more accurate. Previously the UI displayed "No response from API" in red, which implied a hard failure. It now reads "Waiting for API response", better reflecting that the client is still actively waiting rather than having given up.

The companion retry hint was also made lowercase for consistency: " · Retrying in " is now " · will retry in ".

Evidence: stalled-state component (search for `"Waiting for API response"` and `"will retry in"`)


### Thinking-budget display now restricted to first-party accounts

A UI element related to thinking-budget visualization (internally `Tun`, associated with the "Chert Bezel" feature) was previously gated behind the server-side feature flag `tengu_chert_bezel`. It is now shown only when the session auth mode resolves to `"firstParty"` — meaning direct Anthropic accounts — instead of being flag-controlled.

This effectively removes the server-side toggle in favour of a hard auth-tier check, so Bedrock and Vertex users will not see this component regardless of any flag state.

Evidence: model-feature array assembly (search for `"firstParty"` adjacent to the `Tun` push; previously searched for `"tengu_chert_bezel"`)


### Internal constant doubled (10 000 → 20 000)

A numeric constant was raised from `10000` to `20000`. Given its context in the build, this is most likely a timeout value (in milliseconds) or a maximum buffer/retry ceiling somewhere in the daemon or update subsystem. Users would observe this as the tool waiting longer before surfacing a timeout error in affected code paths, rather than any explicit UI change.

Evidence: removed constant `$lc = 1e4`, added `Woc = 20000` (search for `Woc` in v2.1.185 source)

---

Generated with:
- tool: `harness-investigations@66416d2-dirty`
- provider: `claude`
- model: `claude-sonnet-4-6`
- primary diff: `archive\claude-code\changes\changes-v2.1.185.md` (filtered astdiff)
- string diff: `archive\claude-code\changes\string-diff-v2.1.185.txt`
