# Changelog for version 2.1.138

## Summary
Version 2.1.138 is a very small CLI release. The filtered AST diff shows no added or removed declarations and the string-literal diff contains only build metadata, but one existing advanced beta path changed: `CLAUDE_CODE_MID_CONVERSATION_SYSTEM` can now override the normal Anthropic base URL check for the mid-conversation system beta.

### Advanced Mid-Conversation System Beta Override
What: Claude Code now allows the `CLAUDE_CODE_MID_CONVERSATION_SYSTEM` environment override to enable the `mid-conversation-system-2026-04-07` beta even when `ANTHROPIC_BASE_URL` is set to a non-default host.

Usage:
```bash
ANTHROPIC_BASE_URL=https://your-compatible-endpoint.example \
CLAUDE_CODE_MID_CONVERSATION_SYSTEM=claude-sonnet-4-5 \
claude
```

Details:
- This is not a new public command or setting; the environment variable already existed in 2.1.137.
- In 2.1.137, the mid-conversation beta check returned false whenever the base URL was not `api.anthropic.com`.
- In 2.1.138, that base URL check is bypassed when `CLAUDE_CODE_MID_CONVERSATION_SYSTEM` is present.
- The beta is still constrained by the surrounding provider and model checks, and `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` can still disable experimental betas.

Evidence: Mid-conversation beta gate now checks `(!If() && !process.env.CLAUDE_CODE_MID_CONVERSATION_SYSTEM)` before adding `mid-conversation-system-2026-04-07` (search for `"CLAUDE_CODE_MID_CONVERSATION_SYSTEM"` and `"mid-conversation-system-2026-04-07"`).

## Notes
No new slash commands, CLI flags, settings descriptions, tips, permission syntax, hook types, or user-facing messages were detected in the provided CLI diff.

The only added string literals in the AST-extracted string diff are the build timestamp `"2026-05-09T04:04:51Z"` and git SHA `"d6d494651eb469be2ff763ef8d1b882aba8ca635"`. There is no migration guidance for this release.


Generated with:
- tool: `harness-investigations@1ed3002-dirty`
- provider: `codex`
- model: `gpt-5.5`
- reasoning effort: `medium`
- primary diff: `archive/claude-code/changes/changes-v2.1.138.md` (filtered astdiff)
- string diff: `archive/claude-code/changes/string-diff-v2.1.138.txt`
