---
id: msg-warning-260661
name: Warning Message
category: message
subcategory: warning
source_line: 260661
---

), []);
  }
}
function Ibp() {
  let e = ["flagSettings", "policySettings"];
  for (let t of e) {
    let n = Rn(t);
    if (
      n?.sandbox?.enabled !== void 0 ||
      n?.sandbox?.autoAllowBashIfSandboxed !== void 0 ||
      n?.sandbox?.allowUnsandboxedCommands !== void 0
    )
      return !0;
  }
  return !1;
}
async function xbp(e) {
  (await _f("localSettings", (t) => {
    let n = {
      ...(e.enabled !== void 0 &&
        t?.sandbox?.enabled !== e.enabled && { enabled: e.enabled }),
      ...(e.autoAllowBashIfSandboxed !== void 0 &&
        t?.sandbox?.autoAllowBashIfSandboxed !== e.autoAllowBashIfSandboxed && {
          autoAllowBashIfSandboxed: e.autoAllowBashIfSandboxed,
        }),
      ...(e.allowUnsandboxedCommands !== void 0 &&
        t?.sandbox?.allowUnsandboxedCommands !== e.allowUnsandboxedCommands && {
          allowUnsandboxedCommands: e.allowUnsandboxedCommands,
        }),
    };
    if (Object.keys(n).length === 0) return null;
    return { sandbox: n };
  }),
    xe("sandbox_set_settings"));
}
function kbp() {
  return ts()?.sandbox?.excludedCommands ?? [];
}
async function Rbp(e, t, n, r) {
  if (SUn()) {
    if (!Vde) (St("sandbox_exec", "sandbox_exec_lazy_init"), await Qfa());
    if (Vde) await Vde;
    if (!Vde) {
      Ie("sandbox_exec", "sandbox_exec_not_initialized");
      let o = w3t ? 
