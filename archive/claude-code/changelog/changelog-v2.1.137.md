# Changelog for version 2.1.137

## Summary
Version 2.1.137 appears to be a build-only CLI release. The filtered AST diff shows 100.0% structural similarity with no added or removed declarations, and the AST-extracted string diff contains only the new build timestamp and git SHA.

Evidence: Version metadata changed from `2.1.136` to `2.1.137`; the only added string literals are `"2026-05-08T23:01:55Z"` and `"88a017e5d1d4c7de4e6de6a496ac08c9c1b77d79"`.

## Notes
No user-facing changes were detected in the provided CLI diff. I found no new slash commands, CLI flags, settings descriptions, `CLAUDE_CODE_*` environment variables, `tengu_*` feature flags, tips, permission syntax, hook types, or user-facing messages beyond version/build metadata.

There is no migration guidance for this release.


Generated with:
- tool: `harness-investigations@1ed3002-dirty`
- provider: `codex`
- model: `gpt-5.5`
- reasoning effort: `medium`
- primary diff: `archive/claude-code/changes/changes-v2.1.137.md` (filtered astdiff)
- string diff: `archive/claude-code/changes/string-diff-v2.1.137.txt`
