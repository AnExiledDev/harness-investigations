# Changelog for version 0.101.0

## Highlights

This release tightens up the memory consolidation pipeline: stage-1 memories now carry the rollout's working directory (`cwd`) all the way through to `MEMORY.md` annotations, and the consolidation agent is required to use that metadata when describing rollout clusters. The remote-model lookup now preserves the requested model slug (so the exact slug, including a more specific suffix, reaches the API), and developer-role messages are no longer persisted into the memory extraction pipeline. Internal throughput was also rebalanced — fewer rollouts processed per startup, with a longer phase-2 heartbeat — to make the background pipeline more stable on large session histories.

### Rollout `cwd` is preserved through the memory pipeline

Stage-1 memory outputs now include the rollout's working directory (`cwd`) and propagate it into every downstream artifact. Before this release, `raw_memories.md` and the per-thread `rollout_summaries/*.md` files only carried `thread_id` and `source_updated_at`; the consolidation agent had no reliable way to attribute a memory to the project it came from.

**What changed:**
- `Stage1Output` (in `codex-rs/state/src/model/memories.rs`) gained a `cwd: PathBuf` field, populated from the `threads.cwd` column via a new `LEFT JOIN` in `list_stage1_outputs_for_global()` (`codex-rs/state/src/runtime/memories.rs`).
- `rebuild_raw_memories_file()` and `write_rollout_summary_for_thread()` in `codex-rs/core/src/memories/storage.rs` now emit a `cwd: <path>` header line alongside `thread_id` and `source_updated_at`.
- The consolidation prompt template (`codex-rs/core/templates/memories/consolidation.md`) was updated to require each `rollout_summary_files` annotation to include `cwd=<path>` and `updated_at=<timestamp>` (recovered from `raw_memories.md` if a per-rollout summary is missing them).

**User impact:** Consolidated `MEMORY.md` clusters now carry per-rollout `cwd` and `updated_at` annotations, so when Codex retrieves memories it can tell which project (e.g. `cwd=/repo/path`) and how recent each one is. Example annotation produced by the new template:

```
rollout_summary_files:
  - <file1.md> (success, most useful architecture walkthrough,
                cwd=/repo/path, updated_at=2026-02-12T10:30:00Z)
```


### Remote model slug is preserved when a prefix match is used

The remote-models lookup previously rewrote the user's requested slug to whatever prefix matched in the remote registry. For example, asking for `gpt-5.3-codex-test` when the registry only listed `gpt-5.3-codex` would cause the request body sent to the API to use `gpt-5.3-codex` as the model name, dropping the more specific suffix.

`ModelsManager::get_model_info()` in `codex-rs/core/src/models_manager/manager.rs` now keeps the originally requested slug while inheriting all other policy fields (reasoning level, truncation policy, etc.) from the matched remote entry:

```rust
let model = if let Some(remote) = remote {
    ModelInfo {
        slug: model.to_string(),  // preserve the caller's requested slug
        ..remote                  // inherit everything else from the prefix match
    }
} else {
    model_info::model_info_from_slug(model)
};
```

The new test `remote_models_long_model_slug_is_sent_with_high_reasoning` in `codex-rs/core/tests/suite/remote_models.rs` confirms that `gpt-5.3-codex-test` reaches the API as `gpt-5.3-codex-test` (not `gpt-5.3-codex`) while still receiving the prefix's `default_reasoning_level = High`.

**User impact:** If you configure remote model entries with broad prefixes and rely on more specific slugs (suffixes for variants, A/B tests, etc.), those specific slugs now actually appear on the wire — while you still get the prefix's reasoning effort, truncation, and other policy settings.


### Developer-role messages excluded from memory extraction

`should_persist_response_item_for_memories()` in `codex-rs/core/src/rollout/policy.rs` now filters out `Message` items whose role is `"developer"`:

```rust
ResponseItem::Message { role, .. } => role != "developer",
```

Previously every `Message` item was kept regardless of role. Developer-injected instructions tend to be templated boilerplate (system prompts, harness scaffolding) that pollute the stage-1 input without representing real conversational content, so they are now skipped before being shipped to the stage-1 model.

**User impact:** Cleaner stage-1 prompts, less noise in extracted raw memories, and lower token usage for the memory pipeline — without affecting the live conversation or the rollout files themselves.


### Memory pipeline throughput rebalanced for stability

Several constants in `codex-rs/core/src/memories/mod.rs` were retuned:

| Constant | Old | New |
| --- | --- | --- |
| `phase_one::MAX_ROLLOUTS_PER_STARTUP` | 64 | **8** |
| `phase_one::CONCURRENCY_LIMIT` | 64 | **8** |
| `phase_two::JOB_HEARTBEAT_SECONDS` | 30 | **90** |

Phase 1 now claims and processes at most 8 rollouts per startup pass (down from 64) with concurrency capped at 8 in-flight stage-1 requests. Phase 2's heartbeat for the consolidation lock was tripled from 30s to 90s.

**User impact:** Less aggressive bursts of background model traffic at startup, lower contention on the state DB, and longer, more forgiving phase-2 leases (consolidation work running on slower hardware is less likely to lose its lock to a heartbeat timeout). Sessions with very large rollout backlogs will now process them across more startups instead of attempting 64 at once.


### Centralized secret-redaction utility

The secret-scrubbing logic (`OPENAI_KEY_REGEX`, `AWS_ACCESS_KEY_ID_REGEX`, `BEARER_TOKEN_REGEX`, and the generic `api_key/token/secret/password` assignment regex) was extracted out of `codex-rs/core/src/memories/stage_one.rs` and into a new dedicated workspace crate `codex-utils-sanitizer`. The memory pipeline now imports it via `use codex_utils_sanitizer::redact_secrets;` (see `codex-rs/core/src/memories/phase1.rs`), and the `regex` dependency was dropped from `codex-rs/core/Cargo.toml` in favor of `regex-lite` (the new sanitizer crate now owns the heavier `regex` dependency).

**User impact:** No behavior change at the memory level — extracted memories are still redacted for OpenAI keys, AWS access key IDs, bearer tokens, and assignments to fields named `api_key`/`token`/`secret`/`password`. The change makes the same redaction primitive available to other parts of the codebase that may need it.

### Specific remote-model slug no longer rewritten to its registry prefix

See "Remote model slug is preserved when a prefix match is used" above. The previous behavior would have caused the API to receive (and bill against) the prefix slug, which could produce confusing telemetry, mismatched logs, or the wrong model being routed to on providers that distinguish between a prefix and its suffixed variants. The fix is contained in `ModelsManager::get_model_info()` in `codex-rs/core/src/models_manager/manager.rs`, with a new regression test in `codex-rs/core/tests/suite/remote_models.rs`.
