# Changelog for version 2.1.131

## Summary
Claude Code 2.1.131 is a small maintenance release with no new CLI commands, flags, settings, or visible tips detected in the diff from 2.1.129. The user-facing changes are concentrated in API plumbing: bundled file operations now target stable Files API paths, and API-client authentication errors now describe the supported auth inputs more directly.

### Stable Files API Paths
What: Bundled Anthropic file operations now call the stable `/v1/files` endpoints instead of beta-suffixed file URLs.

Usage:
```bash
claude
```

Details:
- This affects internal/API-backed file list, upload, download, metadata, and delete calls.
- Existing Claude Code workflows should not need new flags or settings.
- The old implementation used `/v1/files?beta=true` and `/v1/files/{id}/content?beta=true`; the new implementation uses `/v1/files` and `/v1/files/{id}/content`.

Evidence: Files API client paths changed from beta URLs to stable URLs (search for `"/v1/files"` and `"/v1/files?beta=true"`).


### Clearer API Authentication Error
What: When the bundled Anthropic API client cannot resolve credentials, the error now says it expects either `apiKey` or `authToken`, instead of listing removed credential/profile/config options.

Usage:
```bash
ANTHROPIC_API_KEY=... claude
```

Details:
- This makes auth failures less misleading for users who hit lower-level API-client errors.
- The new message points users toward API key or bearer-token authentication.
- The previous message referenced `credentials`, `config`, and `profile`; those are no longer listed in the failure text.

Evidence: Authentication validation message changed (search for `"Could not resolve authentication method. Expected either apiKey or authToken to be set"`).

### Bundled Beta SDK Surface Cleanup
Several bundled beta Anthropic SDK resources were removed from the CLI package, including generated client bindings for managed agents, sessions, environments, vaults, memory stores, and user profiles. This appears to be cleanup of packaged SDK internals rather than a new Claude Code CLI workflow: no corresponding new slash command, flag, setting, or tip was added in this release.

Evidence: Removed beta client routes include `"/v1/agents?beta=true"`, `"/v1/sessions?beta=true"`, `"/v1/vaults?beta=true"`, `"/v1/memory_stores?beta=true"`, and `"/v1/user_profiles?beta=true"`.
