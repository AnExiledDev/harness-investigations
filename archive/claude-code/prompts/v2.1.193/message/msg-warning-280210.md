---
id: msg-warning-280210
name: Warning Message
category: message
subcategory: warning
source_line: 280210
---

,
        { level: "error" },
      );
    }
  let d = r ?? W$();
  for await (let p of RFt(e, t, n, d, o, void 0, void 0, s)) {
    if (p.message) i.push(p.message);
    if (p.additionalContexts && p.additionalContexts.length > 0)
      a.push(...p.additionalContexts);
    if (p.initialUserMessage) uto = p.initialUserMessage;
    if (p.sessionTitle) c = p.sessionTitle;
    if (p.watchPaths && p.watchPaths.length > 0) l.push(...p.watchPaths);
    if (p.reloadSkills) u = !0;
  }
  if (u) (d0(), tW(), pF.emit(), Ie("hook_session_start_reload_skills"));
  if (((dto = e === "startup" || e === "resume" ? c : void 0), l.length > 0))
    GZi(l);
  if (a.length > 0) {
    let p = ei({
      type: "hook_additional_context",
      content: a,
      hookName: "SessionStart",
      toolUseID: "SessionStart",
      hookEvent: "SessionStart",
    });
    i.push(p);
  }
  return i;
}
async function zZi(e, { forceSyncExecution: t } = {}) {
  if (cc("hooks")) return [];
  let n = [],
    r = [];
  if (E_() && (Sl() || xY() === null))
    T(
      Sl()
        ? "Skipping plugin hooks - safe mode disables plugins (managed settings-file hooks still run)"
        : "Skipping plugin hooks - allowManagedHooksOnly is enabled and no managed plugins",
    );
  else
    try {
      await W_e();
    } catch (o) {
      let s = o instanceof Error ? o.message : String(o);
      T(
        
