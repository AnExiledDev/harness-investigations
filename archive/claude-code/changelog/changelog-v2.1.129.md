# Changelog for version 2.1.129

## Summary
Claude Code 2.1.129 adds URL-loaded session plugins, opt-in package-manager auto-updates, and stronger Remote Control enrollment handling for organizations that require Trusted Devices. This release also improves plugin author diagnostics, skill-listing context-budget warnings, update guidance, and several failure messages around daemon startup, symlink writes, and third-party provider limitations.

### Session Plugins from URLs
What: You can now load a session-only plugin directly from a remote `.zip` URL.

Usage:
```bash
claude --plugin-url https://example.com/my-plugin.zip
claude --plugin-url https://example.com/a.zip --plugin-url https://example.com/b.zip
```

Details:
- `--plugin-url` is repeatable, like `--plugin-dir`.
- Claude Code fetches the plugin archive, enforces a maximum archive size, extracts it, and loads it only for the current session.
- If re-fetching fails but a cached copy exists, Claude Code can reuse the cached archive.
- `/doctor` now labels these as `Session-only plugins (--plugin-dir / --plugin-url)`.

Evidence: New CLI option and help text (search for `"Fetch a plugin .zip from a URL for this session only (repeatable: --plugin-url A --plugin-url B)"`)


### Opt-In Package Manager Auto-Updates
What: Claude Code can now automatically run supported package-manager updates when a newer version is available.

Usage:
```bash
CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE=1 claude
```

Details:
- When enabled, Claude Code can run update commands for supported package managers instead of only telling you what command to run.
- Homebrew uses `brew upgrade --cask ...`.
- Windows winget uses `winget.exe upgrade --id Anthropic.ClaudeCode --exact --silent --disable-interactivity`.
- The UI reports progress with messages like `Updating via ...`, success with `✓ Update installed · Restart to apply`, and falls back to manual instructions if auto-update fails.
- Manual update guidance now also recognizes `mise upgrade claude`.

Evidence: Auto-update gate and commands (search for `"CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE"`, `"--disable-interactivity"`, and `"✓ Update installed"`)


### Trusted Device Enrollment for Remote Control
What: Remote Control now has a first-run enrollment path for organizations that require Trusted Devices.

Usage:
```bash
claude remote-control
# or inside a session:
/remote-control
```

Details:
- If Remote Control preflight finds that the device must be enrolled, Claude Code starts a sign-in flow instead of only reporting that the device is blocked.
- If sign-in is canceled or enrollment does not complete, Claude Code now gives specific next steps.
- Organizations can temporarily disable proactive enrollment with a feature flag, in which case users see an explicit administrator-facing message.

Evidence: Trusted Device enrollment flow (search for `"Sign in to enroll this device for Remote Control."` and `"Your organization requires Trusted Devices for Remote Control, but enrollment is temporarily disabled"`)

### Better Plugin Authoring Diagnostics
Claude Code now warns plugin authors about several manifest and packaging mistakes that previously could be confusing.

Details:
- Experimental plugin components should be declared under `experimental.<component>` instead of at the top level.
- Invalid `experimental` values are ignored with a clearer warning.
- `claude.md` and `claude.local.md` at a plugin root now produce guidance because they are not loaded as project context.
- Plugin root context should move into a skill at `skills/<name>/SKILL.md`.

Evidence: Plugin validation warnings (search for `"is an experimental component; declare it under 'experimental."`, `"'experimental' must be an object containing component declarations"`, and `"To ship context with your plugin, use a skill (skills/<name>/SKILL.md) instead."`)


### Skill Listing Context Budget Warnings
Claude Code now surfaces when the skill listing sent to Claude is being shortened or truncated to fit the context budget.

Details:
- The UI can show whether descriptions exceed the per-entry cap.
- It suggests `/skills` to disable skills or `skillListingBudgetFraction` to allocate more context.
- It estimates the extra token cost of opting into a larger skill listing.

Evidence: Skill budget warning UI (search for `"Skill listing will be truncated"`, `"skillListingBudgetFraction"`, and `"Opting in would cost ~"`)


### Safer File Writes Around Symlinks
Claude Code now refuses more unsafe write paths involving symlinks unless the caller explicitly allows symlink writes.

Details:
- Writes through symlinked files can now fail fast with guidance to resolve the symlink and pass the real path.
- Writes into symlinked parent directories are rejected.
- The fallback non-atomic write path also checks `O_NOFOLLOW`.

Evidence: Symlink write protections (search for `"Refusing to write through symlink:"` and `"Refusing to write into symlinked directory:"`)


### Clearer Remote Control and Provider Messages
Remote Control and third-party-provider messages are more specific.

Details:
- Remote session creation failures now surface as `Remote session create failed: ...`.
- Remote Control diagnostics include clearer hints when OAuth token or organization UUID state is missing in a CCR environment.
- `/feedback` now explicitly reports that it is unavailable for Claude Platform on AWS and Amazon Bedrock Mantle.
- Channel support now reports `Channels are not available on third-party providers` instead of listing only specific providers.

Evidence: Provider and Remote Control messages (search for `"Remote session create failed:"`, `"/feedback is not available when using Claude Platform on AWS"`, and `"Channels are not available on third-party providers"`)


### Fast Mode Model Text is Now Dynamic
Fast Mode descriptions no longer hardcode Opus 4.6 in all paths. The displayed Fast Mode model can now be generated dynamically.

Evidence: Dynamic Fast Mode copy (search for `"Fast mode for Claude Code uses Claude"` and `"CLAUDE_CODE_ENABLE_OPUS_4_7_FAST_MODE"`)

## Bug Fixes

- Daemon startup failures now fall back to transient spawn with a repair command instead of leaving the user at a dead daemon state. Evidence: search for `"daemon service did not become reachable within 5s"` and `"falling back to transient spawn. Run 'claude daemon install' to repair."`

- Renaming a non-responsive remote/background session now shows a specific error instead of silently reverting or using only the generic local state-file failure. Evidence: search for `"Couldn't rename — that session isn't responding"`

- Background startup can now mark a session as blocked when it appears stuck on a startup dialog, with the user-facing action `open this session to continue setup`. Evidence: search for `"stuck on a startup dialog"` and `"CLAUDE_BG_STARTUP_WEDGE_MS"`

- Background worktree cleanup now distinguishes a worktree kept because it is on a different branch from one kept because it has uncommitted changes. Evidence: search for `"Worktree is on a different branch — kept at"`

## In Development

Features with infrastructure added but not yet broadly enabled. These are shipped behind environment variables or feature flags and may become available in future versions.


### Opus 4.7 Fast Mode [In Development]
What: Claude Code has infrastructure to switch Fast Mode labeling and model selection from Opus 4.6 to Opus 4.7.

Status: Environment-gated

Details:
- The new gate is `CLAUDE_CODE_ENABLE_OPUS_4_7_FAST_MODE`.
- When enabled, Fast Mode text can report `Opus 4.7`; otherwise it remains on `Opus 4.6`.
- Because this is gated by an environment variable and existing docs elsewhere still mention Opus 4.6 Fast behavior, treat this as experimental rather than broadly available.

Evidence: Environment-gated model switch (search for `"CLAUDE_CODE_ENABLE_OPUS_4_7_FAST_MODE"` and `"Opus 4.7"`)


### Persistent Autonomous Loop Instructions [In Development]
What: Claude Code includes new autonomous loop behavior that keeps timer-invoked work alive more persistently when there is still useful work to pursue.

Status: Feature-flagged

Details:
- The behavior is enabled by `CLAUDE_CODE_LOOP_PERSISTENT` or the `tengu_kairos_loop_persistent` feature flag.
- The new instructions tell the loop to broaden once before stopping when work appears quiet.
- This affects background/autonomous operation rather than normal interactive CLI usage.

Evidence: Persistent loop gate (search for `"CLAUDE_CODE_LOOP_PERSISTENT"` and `"tengu_kairos_loop_persistent"`)
