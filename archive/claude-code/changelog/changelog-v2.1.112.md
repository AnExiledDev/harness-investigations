# Changelog for version 2.1.112

## Summary

A minimal patch release that fixes temperature parameter handling for Claude Opus 4-7 in internal side queries. No new features or user-facing UI changes.

## Bug Fixes

- **Temperature parameter no longer sent for Opus 4-7 side queries**: Internal side queries (used for background model calls like tool descriptions and context summarization) previously sent the `temperature` parameter to all models. Opus 4-7 may not support custom temperature, so the parameter is now excluded for that model. This prevents potential API errors or unexpected behavior when Opus 4-7 is used for side queries. The main conversation API call path is unchanged. Evidence: New model check function `WV8()` (search for `"claude-opus-4-7"` near the `temperature` spread in the `dR` side-query function at line ~593235)

## Notes

- The Haiku model selector descriptions ("Haiku 3.5" and "Haiku 4.5") appear swapped between two internal functions compared to the prior version, but both strings exist with identical counts in both versions (6 occurrences of "Haiku 3.5", 16 of "Haiku 4.5"). This is internal code reorganization with no user-visible effect.
- Import style was refactored from default imports to named/destructured imports for several Node.js built-in modules (`child_process`, `crypto`, `node:os`, etc.). This is purely internal cleanup with no behavioral change.
