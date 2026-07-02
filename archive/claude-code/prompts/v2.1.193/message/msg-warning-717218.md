---
id: msg-warning-717218
name: Warning Message
category: message
subcategory: warning
source_line: 717218
---

),
        );
    }
    (process.chdir(_.worktreePath),
      Yy(_.worktreePath),
      BL(Mt()),
      qfe(Mt()),
      h5(_),
      Lx(),
      FIe(),
      Zc("setup_worktree_ms", performance.now() - d, d));
  }
  if ((Cn("info", "setup_background_jobs_starting"), !cd()))
    try {
      Atc();
    } catch (g) {
      ke(g);
    }
  (cVe(),
    Cn("info", "setup_background_jobs_launched"),
    ia("setup_before_prefetch"),
    Cn("info", "setup_prefetch_starting"));
  let p = (Tr() && Be.CLAUDE_CODE_SYNC_PLUGIN_INSTALL) || cd() || Sl();
  if (!p) GE(Ec());
  if (
    (Promise.resolve()
      .then(() => (Q3e(), cto))
      .then((g) => {
        if (!p) (g.loadPluginHooks(), g.setupPluginHookHotReload());
      }),
    !cd())
  ) {
    if (
      (Promise.resolve()
        .then(() => (IIo(), Qhl))
        .then((g) => g.registerSessionFileAccessHooks()),
      !sa() && td())
    )
      Promise.resolve()
        .then(() => (vKn(), TKn))
        .then((g) => g.startMemoryWatcher());
  }
  (FBo(), V("tengu_started", {}), U3r(Tr()));
  let f = (jo() || {}).proxyAuthHelper;
  if (
    (PRr({
      helper: f,
      fromProjectOrLocal:
        _n("projectSettings")?.proxyAuthHelper === f ||
        _n("localSettings")?.proxyAuthHelper === f,
      trustAccepted: td,
    }),
    $Rr(),
    ia("setup_after_prefetch"),
    !cd())
  ) {
    let g = performance.now();
    (await $Ol(Lt().lastReleaseNotesSeen),
      Zc("setup_release_notes_ms", performance.now() - g, g));
  }
  if (t === "bypassPermissions" || n) {
    if (
      typeof process.getuid === "function" &&
      process.getuid() === 0 &&
      process.env.IS_SANDBOX !== "1" &&
      !Be.CLAUDE_CODE_BUBBLEWRAP
    )
      (console.error(
        "--dangerously-skip-permissions cannot be used with root/sudo privileges for security reasons",
      ),
        process.exit(1));
  }
  let m = mg();
  if (m.lastCost !== void 0 && m.lastDuration !== void 0)
    V("tengu_exit", {
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
      last_session_id: Ar(m.lastSessionId),
      ...m.lastSessionMetrics,
    });
}
function t9f(e) {
  return !1;
}
var bsr = E(() => {
  su();
  It();
  kb();
  Do();
  A6e();
  OM();
  tze();
  ut();
  Uf();
  jz();
  c3o();
  fS();
  PE();
  $zr();
  ro();
  Lw();
  er();
  Ge();
  Sm();
  Uk();
  kr();
  Kq();
  un();
  St();
  ea();
  IFt();
  mje();
  eM();
  xtc();
  Tn();
  NX();
  gI();
  y_();
  ha();
  gr();
  l3();
  s4();
  I0();
});
var Rtc = {};
gt(Rtc, { startMCPServer: () => r9f, createMCPServer: () => ktc });
async function r9f(e, t, n) {
  Yy(e);
  let r = ktc(t, n),
    o = new jNe();
  await r.connect(o);
}
function ktc(e, t) {
  qml(GCo());
  let n = lF(p1),
    r = new Nme(
      {
        name: "claude/tengu",
        version: {
          ISSUES_EXPLAINER:
            "report the issue at https://github.com/anthropics/claude-code/issues",
          PACKAGE_URL: "@anthropic-ai/claude-code",
          README_URL: "https://code.claude.com/docs/en/overview",
          VERSION: "2.1.193",
          FEEDBACK_CHANNEL: "https://github.com/anthropics/claude-code/issues",
          BUILD_TIME: "2026-06-25T18:18:11Z",
          GIT_SHA: "a1938d2a07a2e4fecbef4eeac813221929e97d22",
        }.VERSION,
      },
      { capabilities: { tools: {} } },
    );
  return (
    r.setRequestHandler(Jz, async () => {
      let o = FO(),
        s = a$(o);
      return {
        tools: await Promise.all(
          s.map(async (i) => ({
            ...i,
            description: await i.prompt({
              getToolPermissionContext: async () => o,
              tools: s,
              agents: [],
            }),
            inputSchema: mMe(i.inputSchema),
            outputSchema: void 0,
          })),
        ),
      };
    }),
    r.setRequestHandler(VV, async ({ params: { name: o, arguments: s } }) => {
      let i = FO(),
        a = a$(i),
        l = gl(a, o);
      if (!l) throw Error(
