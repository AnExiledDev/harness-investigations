---
id: msg-warning-256522
name: Warning Message
category: message
subcategory: warning
source_line: 256522
---

), []);
  }
}
function wWd() {
  let e = ["flagSettings", "policySettings"];
  for (let t of e) {
    let n = _n(t);
    if (
      n?.sandbox?.enabled !== void 0 ||
      n?.sandbox?.autoAllowBashIfSandboxed !== void 0 ||
      n?.sandbox?.allowUnsandboxedCommands !== void 0
    )
      return !0;
  }
  return !1;
}
async function CWd(e) {
  let t = _n("localSettings");
  (co("localSettings", {
    sandbox: {
      ...t?.sandbox,
      ...(e.enabled !== void 0 && { enabled: e.enabled }),
      ...(e.autoAllowBashIfSandboxed !== void 0 && {
        autoAllowBashIfSandboxed: e.autoAllowBashIfSandboxed,
      }),
      ...(e.allowUnsandboxedCommands !== void 0 && {
        allowUnsandboxedCommands: e.allowUnsandboxedCommands,
      }),
    },
  }),
    Ie("sandbox_set_settings"));
}
function IWd() {
  return jo()?.sandbox?.excludedCommands ?? [];
}
async function xWd(e, t, n, r) {
  if (WLn()) {
    if (!Qle) (Ct("sandbox_exec", "sandbox_exec_lazy_init"), await gKi());
    if (Qle) await Qle;
    if (!Qle) {
      Re("sandbox_exec", "sandbox_exec_not_initialized");
      let o = ZNt ? 
