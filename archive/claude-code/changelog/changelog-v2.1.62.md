# Changelog for version 2.1.62


## Summary

This is a minimal maintenance release with no user-facing changes. The only functional modification is an internal optimization to prompt cache breakpoint placement, which may improve API cache hit rates.

### Optimized prompt cache breakpoint placement

What: Cache breakpoints are now applied to the last two messages in a conversation instead of only the final message, potentially improving cache hit rates with the Anthropic API.

Details:
- Previously, only the very last message in a conversation received a cache breakpoint marker
- Now the last two messages both receive cache breakpoints, increasing the likelihood of cache reuse when new messages are appended
- The `skipCacheWrite` flag now only suppresses the breakpoint on the final message, leaving the second-to-last message always cached
- This is an internal optimization; users may experience marginally faster response times due to improved cache utilization, but no action is required

Evidence: Cache breakpoint logic in message preparation (search for `"tengu_api_cache_breakpoints"`) — `K$z()` at line ~519758

## Notes

This release contains no new features, no bug fixes, no new CLI flags, no new slash commands, and no new feature flags. The `tengu_` flag count remains unchanged at 938. Structural similarity between v2.1.61 and v2.1.62 is 99.9%, with the remaining differences being import style changes (default imports converted to named imports) and the single cache breakpoint adjustment described above.
