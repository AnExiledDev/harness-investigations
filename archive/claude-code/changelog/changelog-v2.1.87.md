# Changelog for version 2.1.87


## Summary

This is a maintenance release with no user-facing changes. The only modifications are internal refactoring of how the BriefTool (SendUserMessage) is registered in the tool list, along with minor variable renames from the minification process.

## Notes

No user-facing features, improvements, or bug fixes were identified in this release. The structural similarity between v2.1.86 and v2.1.87 is 99.9%, with only 13 additions, 13 removals, and minor structural adjustments.

The sole meaningful code change is an internal refactoring of the BriefTool registration: it was previously conditionally included in the tool list via a lazy-loaded variable (`...(BHK ? [BHK] : [])`), and is now included directly as a module-level reference (`os1`). The tool's `isEnabled()` gate remains unchanged, so this has no effect on behavior. The BriefTool itself (renamed internally to "SendUserMessage") continues to function identically — its entitlement check (`isBriefEntitled`), enablement check (`isBriefEnabled`), schema, and implementation are all unchanged.

Evidence: BriefTool direct inclusion (search for `BriefTool: () => os1` in new version vs `BriefTool: () => h8z` in old version; registration change visible at the `KK6()` tool list function)
