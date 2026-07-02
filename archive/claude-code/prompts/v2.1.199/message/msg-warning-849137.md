---
id: msg-warning-849137
name: Warning Message
category: message
subcategory: warning
source_line: 849137
---

, {
          level: "warn",
        });
    } catch {}
  };
  return (
    process.on("warning", n),
    {
      uninstall() {
        process.removeListener("warning", n);
      },
    }
  );
}
var lxt,
  Dos,
  N5m = 1000,
  F5m;
var Gqc = E(() => {
  Lt();
  We();
  dr();
  ws();
  ((lxt = require("path")), (Dos = require("util")));
  F5m = [
    /MaxListenersExceededWarning.*AbortSignal/,
    /MaxListenersExceededWarning.*EventTarget/,
  ];
});
function Wqc(e) {
  let t = {},
    n = Rt();
  return {
    unsubscribe: Mte((o, s) => {
      if (o === n) return;
      let i = n;
      ((n = o),
        q("tengu_session_start", {
          previous_session_id: mr(i),
          source: Me(s),
          permissionMode: e.permissionMode,
          dangerouslySkipPermissionsPassed: e.dangerouslySkipPermissionsPassed,
          modeIsBypass: e.modeIsBypass,
          print: e.print,
          ...t,
        }));
    }),
    updateContext(o) {
      t = { ...t, ...o };
    },
  };
}
var qqc = E(() => {
  dt();
  Lt();
  Y_();
});
function j5m() {
  let e = process.env.CLAUDE_BG_SESSION_PERMISSION_RULES;
  if (!e || process.env.CLAUDE_CODE_SESSION_KIND !== "bg") return;
  try {
    let t = JSON.parse(e);
    return Array.isArray(t.allow) && Array.isArray(t.deny)
      ? { allow: t.allow, deny: t.deny }
      : void 0;
  } catch {
    return;
  }
}
function G5m() {
  if (
    process.env.CLAUDE_BG_MEMORY_TOGGLED_OFF === "1" &&
    process.env.CLAUDE_CODE_SESSION_KIND === "bg"
  )
    p2e(!0);
}
async function zqc(e) {
  G5m();
  let t = await QXo({
      allowedToolsCli: e.allowedTools,
      disallowedToolsCli: e.disallowedTools,
      baseToolsCli: e.baseTools,
      permissionMode: e.permissionMode,
      allowDangerouslySkipPermissions: e.allowDangerouslySkipPermissions,
      addDirs: e.addDirs,
      bgSessionPermissionRules: j5m(),
    }),
    n = t.toolPermissionContext,
    { warnings: r, dangerousPermissions: o, overlyBroadBashPermissions: s } = t;
  if (e.permissionMode === "auto") n = l9(n);
  if (e.permissionMode === "plan") {
    let i = jrn(n);
    if (i) n = { ...i, prePlanMode: "default" };
  }
  return {
    toolPermissionContext: n,
    warnings: r,
    dangerousPermissions: o,
    overlyBroadBashPermissions: s,
  };
}
var Kqc = E(() => {
  dt();
  w_();
  Qn();
});
async function Yqc({
  cwd: e,
  toolPermissionContext: t,
  applyCoordinatorFilter: n,
  agentsJson: r,
  agentSetting: o,
  commandsPromise: s,
  agentDefsPromise: i,
  deferCommands: a,
  onToolsLoaded: l,
}) {
  let c = N2(t);
  if (n && !0 && yw()) {
    let { applyCoordinatorToolFilter: h } = await Promise.resolve().then(
      () => (jsn(), UMc),
    );
    c = h(c);
  }
  (l?.(), s?.catch(() => {}), i?.catch(() => {}));
  let u = s ?? LA(e);
  if (a) u.catch(() => {});
  let [d, p] = await Promise.all([a ? Promise.resolve([]) : u, i ?? iM(e)]),
    f = [];
  if (r && !Dc("agents", { explicitlyRequested: !0 }))
    try {
      let h = Ga(r);
      if (h) f = TZt(h, "flagSettings");
    } catch (h) {
      Re(h);
    }
  else if (r)
    T(
      "--agents: ignored in safe mode (user-supplied custom agents are disabled)",
      { level: "warn" },
    );
  let m = V7e(p, [...p.allAgents, ...f]),
    g = Pos(m.activeAgents, o);
  return (
    a7(g?.agentType),
    {
      tools: c,
      commands: d,
      agentDefinitions: m,
      mainThreadAgentDefinition: g,
      cliAgents: f,
      deferredCommandsPromise: a ? u : void 0,
    }
  );
}
function Xqc(e) {
  return e && De.CLAUDE_CODE_SYNC_PLUGIN_INSTALL;
}
function Pos(e, t) {
  if (!t) return;
  let n =
    e.find((r) => r.agentType === t) ??
    e.find((r) => r.agentType.endsWith(
