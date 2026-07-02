---
id: msg-warning-747221
name: Warning Message
category: message
subcategory: warning
source_line: 747221
---

),
        );
    }
    (process.chdir(b.worktreePath),
      qy(b.worktreePath),
      v0(Pt()),
      iye(Pt()),
      TV(b),
      Mk(),
      BRe(),
      lu("setup_worktree_ms", performance.now() - d, d));
  }
  if ((vn("info", "setup_background_jobs_starting"), !Dd())) {
    try {
      QTc();
    } catch (g) {
      Re(g);
    }
    try {
      YNl();
    } catch (g) {
      Re(g);
    }
  }
  (sKe(),
    vn("info", "setup_background_jobs_launched"),
    Ea("setup_before_prefetch"),
    vn("info", "setup_prefetch_starting"));
  let p = (yr() && De.CLAUDE_CODE_SYNC_PLUGIN_INSTALL) || Dd() || sc();
  if (!p) LA(ol());
  if (
    (Promise.resolve()
      .then(() => (zVe(), Qmo))
      .then((g) => {
        if (!p) (g.loadPluginHooks(), g.setupPluginHookHotReload());
      }),
    !Dd())
  ) {
    if (
      (Promise.resolve()
        .then(() => (bwo(), kza))
        .then((g) => g.registerSessionFileAccessHooks()),
      !ta() && Ad())
    )
      Promise.resolve()
        .then(() => (yWn(), hWn))
        .then((g) => g.startMemoryWatcher());
  }
  (oYo(), q("tengu_started", {}), XXr(yr()));
  let f = (ts() || {}).proxyAuthHelper;
  if (
    (Njr({
      helper: f,
      fromProjectOrLocal:
        Rn("projectSettings")?.proxyAuthHelper === f ||
        Rn("localSettings")?.proxyAuthHelper === f,
      trustAccepted: Ad,
    }),
    Fjr(),
    Ea("setup_after_prefetch"),
    !Dd())
  ) {
    let g = performance.now();
    (await cZl(Dt().lastReleaseNotesSeen),
      lu("setup_release_notes_ms", performance.now() - g, g));
  }
  if (t === "bypassPermissions" || n) {
    if (
      typeof process.getuid === "function" &&
      process.getuid() === 0 &&
      process.env.IS_SANDBOX !== "1" &&
      !De.CLAUDE_CODE_BUBBLEWRAP
    )
      (console.error(
        "--dangerously-skip-permissions cannot be used with root/sudo privileges for security reasons",
      ),
        process.exit(1));
  }
  let m = Kg();
  if (m.lastCost !== void 0 && m.lastDuration !== void 0)
    q("tengu_exit", {
      last_session_cost: m.lastCost,
      last_session_api_duration: m.lastAPIDuration,
      last_session_tool_duration: m.lastToolDuration,
      last_session_duration: m.lastDuration,
      last_session_lines_added: m.lastLinesAdded,
      last_session_lines_removed: m.lastLinesRemoved,
      last_session_total_input_tokens: m.lastTotalInputTokens,
      last_session_total_output_tokens: m.lastTotalOutputTokens,
      last_session_total_cache_creation_input_tokens:
        m.lastTotalCacheCreationInputTokens,
      last_session_total_cache_read_input_tokens:
        m.lastTotalCacheReadInputTokens,
      last_session_fps_average: m.lastFpsAverage,
      last_session_fps_low_1_pct: m.lastFpsLow1Pct,
      last_session_graceful_shutdown: m.lastGracefulShutdown ?? !1,
      last_session_version_base: m.lastVersionBase ?? "unknown",
      last_session_id: mr(m.lastSessionId),
      ...m.lastSessionMetrics,
    });
}
function Pwm(e) {
  return !1;
}
function Mwm(e) {
  return !1;
}
var Ehr = E(() => {
  wu();
  Lt();
  Y_();
  Ho();
  UXe();
  sO();
  wJe();
  dt();
  Uf();
  h7();
  OQo();
  Hy();
  Ior();
  vA();
  oio();
  oo();
  MC();
  Jn();
  We();
  nm();
  lk();
  dr();
  d5();
  gn();
  ut();
  na();
  a5t();
  i5e();
  w$();
  ovc();
  Cn();
  TZ();
  WC();
  Wg();
  ya();
  fr();
  nW();
  VG();
  HR();
});
var ivc = {};
lt(ivc, { startMCPServer: () => Owm, createMCPServer: () => svc });
async function Owm(e, t, n) {
  qy(e);
  let r = svc(t, n),
    o = new Sje();
  await r.connect(o);
}
function svc(e, t) {
  q6a(two());
  let n = $U(lG),
    r = new Qye(
      {
        name: "claude/tengu",
        version: {
          ISSUES_EXPLAINER:
            "report the issue at https://github.com/anthropics/claude-code/issues",
          PACKAGE_URL: "@anthropic-ai/claude-code",
          README_URL: "https://code.claude.com/docs/en/overview",
          VERSION: "2.1.199",
          FEEDBACK_CHANNEL: "https://github.com/anthropics/claude-code/issues",
          BUILD_TIME: "2026-07-02T01:14:04Z",
          GIT_SHA: "968b0c4118bde7c998acd97511e68daecacd8507",
          DD_SOURCEMAP_GROUP: "default",
        }.VERSION,
      },
      { capabilities: { tools: {} } },
    );
  return (
    r.setRequestHandler(v7, async () => {
      let o = H4(),
        s = N2(o);
      return {
        tools: await Promise.all(
          s.map(async (i) => ({
            ...i,
            description: await i.prompt({
              getToolPermissionContext: async () => o,
              tools: s,
              agents: [],
            }),
            inputSchema: vNe(i.inputSchema),
            outputSchema: void 0,
          })),
        ),
      };
    }),
    r.setRequestHandler(r8, async ({ params: { name: o, arguments: s } }) => {
      let i = H4(),
        a = N2(i),
        l = Ll(a, o);
      if (!l) throw Error(
