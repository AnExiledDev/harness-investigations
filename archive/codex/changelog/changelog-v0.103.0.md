# Changelog for version 0.103.0

## Highlights

This release introduces configurable git commit attribution, allowing Codex to automatically append `Co-authored-by:` trailers to commits it writes. The remote-models feature graduates from a gated flag to an always-on capability, simplifying configuration and removing a layer of plumbing throughout the codebase. App metadata returned by the `app/list` API is significantly enriched with new branding, store-listing, and labeling fields to support richer app directory experiences.

### Configurable Git Commit Attribution

**What:** Codex can now instruct the model to automatically append a `Co-authored-by:` trailer to git commit messages it writes or edits, with the attribution string fully configurable through a new top-level `commit_attribution` setting in `config.toml`.

**Details:**
- Controlled by a new experimental feature flag, `codex_git_commit` (stage: UnderDevelopment, default: disabled). Enable it under the `[features]` table to activate the behavior.
- Without any configuration, the trailer defaults to `Co-authored-by: Codex <noreply@openai.com>`.
- Setting `commit_attribution` to a custom string (e.g., `commit_attribution = "MyAgent <me@example.com>"`) uses it verbatim in the trailer.
- Setting `commit_attribution = ""` (empty or whitespace-only) disables the trailer prompt entirely, even when the feature is on.
- The instruction injected into the developer prompt explicitly tells the model to append the trailer exactly once, preserve any other trailers, and keep one blank line between the body and the trailer block — preventing duplication on edits to existing commit messages.

**Configuration example:**
```toml
commit_attribution = "Acme Bot <bot@acme.example>"

[features]
codex_git_commit = true
```

**Code references:** `commit_message_trailer_instruction()` in `core/src/commit_attribution.rs`; injection happens in `Session::build_initial_history()` in `core/src/codex.rs`. The feature is registered in `core/src/features.rs` and the config field is parsed in `core/src/config/mod.rs`.


### Expanded App Metadata in `app/list` API (Experimental)

**What:** The `AppInfo` payload returned by `app/list` and emitted via `app/list/updated` notifications now carries three new optional fields — `branding`, `appMetadata`, and `labels` — that surface much richer information about each connector/app pulled from the ChatGPT app directory.

**Details:**
- `branding` (`AppBranding`): includes `category`, `developer`, `website`, `privacyPolicy`, `termsOfService`, and an `isDiscoverableApp` boolean for store-listing UI.
- `appMetadata` (`AppMetadata`): includes `review.status`, `categories`, `subCategories`, `seoDescription`, `screenshots[]` (each with `url`, `fileId`, `userPrompt`), `developer`, `version`, `versionId`, `versionNotes`, `firstPartyType`, `firstPartyRequiresInstall`, and `showInComposerWhenUnlinked`.
- `labels` (`Map<String, String>`): arbitrary key/value tags attached to the app (e.g. `{"feature": "beta", "source": "directory"}`).
- TypeScript bindings are generated for clients: new files `AppBranding.ts`, `AppMetadata.ts`, `AppReview.ts`, and `AppScreenshot.ts` are exported from the v2 schema package.
- Directory snapshot merging now folds these new fields together when the same app appears in multiple sources, taking the first non-null value field-by-field for branding/metadata, and keeping the first non-null `labels` map.

**Example response fragment:**
```json
{
  "id": "alpha",
  "name": "Alpha",
  "branding": {
    "category": "PRODUCTIVITY",
    "developer": "Acme",
    "website": "https://acme.example",
    "privacyPolicy": "https://acme.example/privacy",
    "termsOfService": "https://acme.example/terms",
    "isDiscoverableApp": true
  },
  "appMetadata": {
    "review": { "status": "APPROVED" },
    "categories": ["PRODUCTIVITY"],
    "version": "1.2.3",
    "screenshots": [{ "url": "...", "userPrompt": "Summarize this draft" }]
  },
  "labels": { "feature": "beta", "source": "directory" }
}
```

**Code references:** Type definitions in `app-server-protocol/src/protocol/v2.rs`; merge logic in `merge_directory_app()` in `chatgpt/src/connectors.rs`; conversion in `directory_app_to_app_info()` in the same file. Schema artifacts updated under `app-server-protocol/schema/json/` and `app-server-protocol/schema/typescript/v2/`.

### `remote_models` Is Now Always On

The `remote_models` feature flag has been promoted from a `Stable`-stage opt-out gate to a `Removed` stage marker, meaning remote model fetching always runs (when ChatGPT auth is present) and the flag is no longer consulted to enable/disable it.

User-visible effects:
- The `[features] remote_models = ...` line in `config.toml` no longer has any effect; setting it false will not suppress remote model lookups.
- The `Feature::RemoteModels` enum variant is retained for backward compatibility (so existing config files still parse), but its documentation is updated to "Legacy remote models flag kept for backward compatibility."
- Internal APIs simplified: `ModelsManager::list_models()`, `try_list_models()`, `get_default_model()`, `refresh_if_new_etag()`, `refresh_available_models()`, `get_remote_models()`, and `try_get_remote_models()` no longer accept a `&Config` parameter, since they no longer need to check the feature flag. This is a breaking change for any third-party integrators calling these APIs.
- The same simplification cascades to `ThreadManager::list_models()` and call-sites in `app-server`, `exec`, and `tui` (e.g. `App::run()`, `ChatWidget::lower_cost_preset()`, `current_model_supports_personality()`, `current_model_supports_images()`).

**Code references:** `Feature::RemoteModels` spec in `core/src/features.rs` (now `stage: Stage::Removed, default_enabled: false`); call-site cleanups in `core/src/codex.rs`, `core/src/models_manager/manager.rs`, `core/src/thread_manager.rs`, `app-server/src/codex_message_processor.rs::list_models()`, `app-server/src/models.rs::supported_models()`, `exec/src/lib.rs::run_main()`, and `tui/src/app.rs`.


### Additional Connector Blocklist Entries

The `DISALLOWED_CONNECTOR_IDS` list (used to hide certain connectors from the apps UI) gained two new entries: `connector_68e004f14af881919eb50893d3d9f523` and `connector_69272cb413a081919685ec3c88d1744e`. Users who previously saw these connectors offered in the app picker will no longer see them.

**Code references:** `DISALLOWED_CONNECTOR_IDS` constant in `chatgpt/src/connectors.rs`.


### App Server README Updated for New Fields

The `app-server/README.md` `Apps` section now documents the new `branding`, `appMetadata`, and `labels` fields in its example `app/list` and `app/list/updated` payloads, so integrators wiring against the protocol have an up-to-date reference of the expected shape.

**Code references:** `app-server/README.md` — `Apps` section.


### Dependency Refresh

- `arc-swap` upgraded from 1.8.0 to 1.8.2.
- `clap` and `clap_builder` upgraded from 4.5.56 to 4.5.58, and `clap_lex` upgraded from 0.7.7 to 1.0.0.
- `env_logger` workspace pin bumped from 0.11.5 to 0.11.9 (with `env_filter` advancing from 0.1.4 to 1.0.0 transitively).
- Various `windows-sys` transitive pins down-revved to align dependency graphs (e.g. 0.61.2 → 0.52.0 / 0.59.0 / 0.48.0 / 0.45.0 in different paths).

These are dependency hygiene updates with no expected user-facing behavior change beyond bug fixes shipped by upstream.

## Bug Fixes

No standalone user-facing bug fixes were identified in this release outside of the behavior changes documented above (the `remote_models` simplification removes a class of misconfiguration where the flag could disable remote model lookups unexpectedly).
