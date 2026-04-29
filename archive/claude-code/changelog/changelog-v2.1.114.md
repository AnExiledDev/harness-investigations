# Changelog for version 2.1.114

## Summary

This is a minimal patch release (from v2.1.113) containing a single bug fix that adds null-safety when accessing application state during tool permission requests, preventing a potential crash.

## Bug Fixes

- Fix potential crash during tool permission prompts: added optional chaining (`?.`) when accessing `getAppState()` and `toolPermissionContext.mode` in the permission request handler. Previously, if `getAppState` returned `null` or `undefined` (e.g., during teardown or an edge-case race condition), the application could throw a `TypeError`. The fix changes `getAppState().toolPermissionContext.mode` to `getAppState?.()?.toolPermissionContext.mode`, gracefully handling the null case. (search for `"tengu_tool_use_show_permission_request"` in function `Qy` at line ~573815)
