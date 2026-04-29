# Changelog for version 2.1.123

## Summary

This is a minimal patch release from v2.1.122 with 100.0% structural similarity. The only behavioral change is a minor internal refactoring that narrows the scope of the `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` environment variable: certain API betas are now always enabled for first-party provider users regardless of that setting.

### Reduced scope of `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` for certain API betas

The internal function that checks whether a user is on a first-party provider (Anthropic direct, Anthropic AWS, or Foundry) was split into two: a pure provider check and a combined provider-plus-env-var check. Two code paths were updated to use the provider-only check, meaning:

- One specific SDK beta flag (used in API request construction) is now always included for first-party provider sessions, even when `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` is set.
- The SDK beta filter function, which decides whether to pass all beta strings through or restrict to a known set, now passes all betas for first-party providers regardless of the env var.

Other uses of `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` (e.g., gating thinking summaries, context management beta, tool schema betas) remain unchanged and continue to respect the environment variable.

Evidence: Provider check refactoring — `an8()` at line ~148770 no longer includes `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`; new `bp()` at line ~148774 preserves the old combined behavior for other call sites (search for `"CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS"`)
