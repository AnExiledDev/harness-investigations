---
id: msg-warning-809498
name: Warning Message
category: message
subcategory: warning
source_line: 809498
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
var OHt,
  Hqo,
  Sum = 1000,
  Hum;
var Fvc = E(() => {
  It();
  Ge();
  kr();
  ws();
  ((OHt = require("path")), (Hqo = require("util")));
  Hum = [
    /MaxListenersExceededWarning.*AbortSignal/,
    /MaxListenersExceededWarning.*EventTarget/,
  ];
});
function Uvc(e) {
  let t = {},
    n = xt();
  return {
    unsubscribe: KQ((o, s) => {
      if (o === n) return;
      let i = n;
      ((n = o),
        V("tengu_session_start", {
          previous_session_id: Ar(i),
          source: $e(s),
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
var jvc = E(() => {
  ut();
  It();
  kb();
});
function Tum() {
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
function vum() {
  if (
    process.env.CLAUDE_BG_MEMORY_TOGGLED_OFF === "1" &&
    process.env.CLAUDE_CODE_SESSION_KIND === "bg"
  )
    fTt(!0);
}
async function Wvc(e) {
  vum();
  let t = await Sjo({
      allowedToolsCli: e.allowedTools,
      disallowedToolsCli: e.disallowedTools,
      baseToolsCli: e.baseTools,
      permissionMode: e.permissionMode,
      allowDangerouslySkipPermissions: e.allowDangerouslySkipPermissions,
      addDirs: e.addDirs,
      bgSessionPermissionRules: Tum(),
    }),
    n = t.toolPermissionContext,
    { warnings: r, dangerousPermissions: o, overlyBroadBashPermissions: s } = t;
  if (e.permissionMode === "auto") n = sV(n);
  return {
    toolPermissionContext: n,
    warnings: r,
    dangerousPermissions: o,
    overlyBroadBashPermissions: s,
  };
}
var Vvc = E(() => {
  ut();
  I_();
  lr();
});
async function qvc({
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
  let c = a$(t);
  if (n && !0 && gv()) {
    let { applyCoordinatorToolFilter: y } = await Promise.resolve().then(
      () => (lYt(), Y3l),
    );
    c = y(c);
  }
  (l?.(), s?.catch(() => {}), i?.catch(() => {}));
  let u = s ?? GE(e);
  if (a) u.catch(() => {});
  let [d, p] = await Promise.all([a ? Promise.resolve([]) : u, i ?? KD(e)]),
    f = [];
  if (r && !cc("agents", { explicitlyRequested: !0 }))
    try {
      let y = Ca(r);
      if (y) f = I6t(y, "flagSettings");
    } catch (y) {
      ke(y);
    }
  else if (r)
    T(
      "--agents: ignored in safe mode (user-supplied custom agents are disabled)",
      { level: "warn" },
    );
  let m = [...p.allAgents, ...f],
    g = { ...p, allAgents: m, activeAgents: rU(m) },
    h = Aqo(g.activeAgents, o);
  return (
    Rz(h?.agentType),
    {
      tools: c,
      commands: d,
      agentDefinitions: g,
      mainThreadAgentDefinition: h,
      cliAgents: f,
      deferredCommandsPromise: a ? u : void 0,
    }
  );
}
function zvc(e) {
  return e && Be.CLAUDE_CODE_SYNC_PLUGIN_INSTALL;
}
function Aqo(e, t) {
  if (!t) return;
  let n =
    e.find((r) => r.agentType === t) ??
    e.find((r) => r.agentType.endsWith(
