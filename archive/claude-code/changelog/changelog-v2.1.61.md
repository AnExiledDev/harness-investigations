# Changelog for version 2.1.61


## Summary

This is a minor release that disables usage-based tool deferral for built-in tools by default, ensuring all built-in tools are always immediately available without needing to be discovered via ToolSearch first. It also includes an internal optimization to client data caching.

### Built-in tools no longer deferred by default

What: Built-in tools marked as deferrable (e.g., Bash, Read, WebFetch, Task tools, etc.) are no longer automatically deferred based on usage frequency. Previously, if you hadn't used a tool recently (usage score below a threshold), it could be hidden and require discovery through the ToolSearch tool before use. Now all built-in tools are loaded and available immediately.

Details:
- The `tengu_coral_whistle` feature flag default was changed from enabled (`!0`) to disabled (`!1`) in the tool deferral check
- MCP (Model Context Protocol) tools remain always deferred — they still require ToolSearch to discover and load
- Tool usage tracking remains active (the usage recording path is unchanged), suggesting data is still being collected for future improvements
- The server can still enable usage-based deferral via the feature flag if needed

Evidence: Tool deferral gate function `WG()` (search for `"tengu_coral_whistle"`) — default changed from `!0` to `!1` at line ~246691


### Smarter client data cache updates

What: The client data cache (used for fetching configuration from the API) now performs a deep equality check before updating state, avoiding unnecessary state propagation when the fetched data hasn't changed.

Details:
- Previously, every fetch from the OAuth client data endpoint would overwrite the cache with a new object, even if the data was identical
- Now uses `isDeepStrictEqual` to compare fresh data against cached data and only triggers a state update when something actually changed
- This reduces unnecessary re-renders and state propagation in the UI

Evidence: Client data fetch function `sQK()` (search for `"clientDataCache"`) — added deep equality check via `$Q()` before cache write at line ~69394
