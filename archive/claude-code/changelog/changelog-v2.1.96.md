# Changelog for version 2.1.96

## Summary

This is a minor maintenance release that refactors how Claude Code handles AWS Bedrock authentication internally. The changes modernize bearer token handling to use the SDK's standard `apiKey` parameter instead of a manual `skipAuth` + `Authorization` header workaround, and improve handling of custom authorization headers passed via default headers configuration.

## Improvements

### Bedrock bearer token authentication streamlined

What: Bearer token authentication for AWS Bedrock has been refactored to use the SDK's native `apiKey` parameter instead of manually setting `skipAuth: true` and injecting an `Authorization` header.

Details:
- Previously, when using `AWS_BEARER_TOKEN_BEDROCK`, Claude Code would set `skipAuth: !0` and manually add `Authorization: Bearer <token>` to the request headers. This has been simplified to pass the token directly as `apiKey`, which is the SDK's standard mechanism.
- When `CLAUDE_CODE_SKIP_BEDROCK_AUTH` is enabled, the code now properly extracts and preserves any existing `Authorization` header from `defaultHeaders` configuration. Previously, custom authorization headers in `defaultHeaders` could be ignored in certain code paths.
- The `skipAuth` flag is now only set when `CLAUDE_CODE_SKIP_BEDROCK_AUTH` is enabled *and* no bearer token is available (previously it was set whenever either the skip flag or a bearer token was present).

Evidence: Bedrock client construction refactored across three code paths (search for `apiKey: Y.token`, `apiKey: process.env.AWS_BEARER_TOKEN_BEDROCK`, and the new `pq_` helper that extracts authorization headers)

## Bug Fixes

- When using `CLAUDE_CODE_SKIP_BEDROCK_AUTH=true` with a custom `Authorization` header already set in default headers, that header is now properly extracted and forwarded to the Bedrock client. Previously this header could be silently dropped. (search for `pq_` helper function and `Z.rest` / `Z.value` pattern)

## Notes

- No new environment variables, commands, or configuration options were added in this release.
- Users of `AWS_BEARER_TOKEN_BEDROCK` and `CLAUDE_CODE_SKIP_BEDROCK_AUTH` do not need to change their configuration; existing setups will continue to work as before.
