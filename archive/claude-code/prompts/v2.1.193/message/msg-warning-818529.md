---
id: msg-warning-818529
name: Warning Message
category: message
subcategory: warning
source_line: 818529
---

 entry, e.g. workspace-level suppression notices) describe content that did NOT load. The key is omitted when there are no warnings.",
          ),
        fast_mode_state: GQt().optional(),
        analytics_disabled: A.boolean()
          .optional()
          .describe(
            "@internal True when the CLI has analytics/telemetry disabled (privacy level, DO_NOT_TRACK, or 3P provider). IDE clients use this to hide per-message thumbs feedback UI since the rating event would be a no-op.",
          ),
        product_feedback_disabled: A.boolean()
          .optional()
          .describe(
            "@internal True when the org's allow_product_feedback policy is false (ZDR/HIPAA). IDE clients use this to hide feedback surfaces (thumbs, session survey) whose events the CLI would drop at the proxy boundary anyway.",
          ),
        memory_paths: A.object({
          auto: A.string().optional(),
          team: A.string().optional(),
        })
          .optional()
          .describe(
            "@internal Absolute directory paths for the auto-memory and team-memory stores. Lets SDK renderers classify Read/Write/Edit tool calls on these paths as memory operations without re-implementing CLI path detection.",
          ),
        uuid: _a(),
        session_id: A.string(),
      }),
    )),
    (smm = Ce(() =>
      A.object({
        type: A.literal("stream_event"),
        event: Kfm(),
        parent_tool_use_id: A.string().nullable(),
        uuid: _a(),
        session_id: A.string(),
        ttft_ms: A.number().optional(),
      }),
    )),
    (imm = Ce(() =>
      A.object({
        type: A.literal("system"),
        subtype: A.literal("compact_boundary"),
        compact_metadata: A.object({
          trigger: A.enum(["manual", "auto"]),
          pre_tokens: A.number(),
          post_tokens: A.number().optional(),
          duration_ms: A.number().optional(),
          user_context: A.string()
            .optional()
            .describe(
              '@internal User-provided focus text for manual "summarize from here".',
            ),
          messages_summarized: A.number()
            .optional()
            .describe("@internal Count of messages the compaction summarized."),
          precomputed: A.boolean()
            .optional()
            .describe(
              "@internal The summary was generated in the background at the autocompact threshold and swapped in when prompt-too-long fired; duration_ms measures user-wait from that point.",
            ),
          pre_compact_discovered_tools: A.array(A.string())
            .optional()
            .describe(
              "@internal Deferred-tool names discovered before this compaction. extractDiscoveredToolNames reads this back on the next turn so the tool-schema filter keeps including them after the tool_reference-carrying messages were summarized away.",
            ),
          preserved_segment: A.object({
            head_uuid: _a(),
            anchor_uuid: _a(),
            tail_uuid: _a(),
          })
            .optional()
            .describe(
              "Relink info for messagesToKeep. Loaders splice the preserved segment at anchor_uuid (summary for suffix-preserving, boundary for prefix-preserving partial compact) so resume includes preserved content. Unset when compaction summarizes everything (no messagesToKeep).",
            ),
          preserved_messages: A.object({
            anchor_uuid: _a(),
            uuids: A.array(_a()),
            all_uuids: A.array(_a())
              .optional()
              .describe(
                "@internal Unfiltered messagesToKeep UUIDs. uuids is the on-disk subset (messages recordTranscript writes); all_uuids is the in-memory superset including non-loggable messages an in-process surface still holds for the next turn's API input. Absent from older producers.",
              ),
          })
            .optional()
            .describe(
              "Ordered messagesToKeep UUIDs. Supersedes preserved_segment \u2014 " +
                "readers look up each UUID directly and relink uuids[i] to uuids[i-1] (uuids[0] to anchor_uuid) instead of walking the parentUuid chain. Unset when compaction summarizes everything.",
            ),
        }),
        logical_parent_uuid: _a()
          .nullable()
          .optional()
          .describe(
            "@internal uuid of the last pre-compact message \u2014 the backpointer " +
              "forkSession follows across the compaction break. Distinct from the session-file chain parent (which is the post-compact summary). Absent from older producers.",
          ),
        uuid: _a(),
        session_id: A.string(),
      }),
    )),
    (amm = Ce(() =>
      A.object({
        type: A.literal("system"),
        subtype: A.literal("status"),
        status: Yfm(),
        permissionMode: SAe().optional(),
        compact_result: A.enum(["success", "failed"]).optional(),
        compact_error: A.string().optional(),
        uuid: _a(),
        session_id: A.string(),
      }),
    )),
    (b9o = Ce(() =>
      A.object({
        type: A.literal("system"),
        subtype: A.literal("post_turn_summary"),
        summarizes_uuid: A.string(),
        status_category: A.string(),
        status_detail: A.string(),
        needs_action: A.string(),
        uuid: _a(),
        session_id: A.string(),
      }).describe(
        "@internal Background post-turn summary emitted after each assistant turn. summarizes_uuid points to the assistant message this summarizes.",
      ),
    )),
    (S9o = Ce(() =>
      A.object({
        type: A.literal("system"),
        subtype: A.literal("task_summary"),
        detail: A.string().nullable(),
        uuid: _a(),
        session_id: A.string(),
      }).describe(
        "@internal Mid-turn progress line from the debounced classifier. Mirrors external_metadata.task_summary so non-CCR consumers (desktop LocalSessionManager) see the same live phrase. detail is null on the idle clear.",
      ),
    )),
    (lmm = Ce(() =>
      A.object({
        type: A.literal("system"),
        subtype: A.literal("informational"),
        content: A.string(),
        level: A.enum(["info", "notice", "suggestion", "warning"]).describe(
          "Render level. 'info' shows only in transcript mode; 'notice' renders in inactive gray; 'suggestion' and 'warning' are more prominent.",
        ),
        tool_use_id: A.string()
          .optional()
          .describe("Dedupes progress messages for the same tool use."),
        prevent_continuation: A.boolean()
          .optional()
          .describe(
            "When true, execution stops after this message (e.g. a Stop hook denied continuation).",
          ),
        uuid: _a(),
        session_id: A.string(),
      }).describe(
        "Generic text banner emitted by the loop \u2014 non-error status lines, hook feedback (e.g. a UserPromptSubmit hook's block reason), slash-command output. Hosts render 
