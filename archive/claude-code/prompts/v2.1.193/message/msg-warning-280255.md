---
id: msg-warning-280255
name: Warning Message
category: message
subcategory: warning
source_line: 280255
---

,
        { level: "warn" },
      );
    }
  for await (let o of LFt(e, void 0, void 0, t)) {
    if (o.message) n.push(o.message);
    if (o.additionalContexts && o.additionalContexts.length > 0)
      r.push(...o.additionalContexts);
  }
  if (r.length > 0) {
    let o = ei({
      type: "hook_additional_context",
      content: r,
      hookName: "Setup",
      toolUseID: "Setup",
      hookEvent: "Setup",
    });
    n.push(o);
  }
  return n;
}
var uto, dto;
var I0e = E(() => {
  ut();
  Uf();
  ln();
  _v();
  Y_();
  Ge();
  Sm();
  un();
  IFt();
  eM();
  Qd();
  Q3e();
  Zq();
  C0e();
});
function Lzd(e) {
  let t = e,
    n = "";
  try {
    n = YZi.homedir();
  } catch {}
  if (n) t = t.replaceAll(n + "/", "~/").replaceAll(n + "\\", "~\\");
  let r = (o, s) => /https?:\/\/[^\s'",;|()]*$/i.test(o.slice(0, s));
  return (
    (t = t
      .replace(/([/\\](?:Users|home)[/\\])[^/\\\n]+/gi, (o, s, i, a) =>
        r(a, i) ? o : 
