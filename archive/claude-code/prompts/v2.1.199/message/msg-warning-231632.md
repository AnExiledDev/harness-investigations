---
id: msg-warning-231632
name: Warning Message
category: message
subcategory: warning
source_line: 231632
---

;
}
function Zoa(e, t) {
  let n = new Map(t.map((c) => [c.source, c])),
    r = new Map(t.map((c) => [c.name, c])),
    o = (c) => {
      let u = n.get(c);
      if (u) return u;
      return c.includes("@") ? void 0 : r.get(c);
    },
    s = [],
    i = [],
    a = new Set([e]),
    l = (o(e)?.manifest.dependencies ?? []).map((c) => ({
      id: c,
      declaringId: e,
    }));
  while (l.length > 0) {
    let c = l.shift();
    if (!c) break;
    let u = j$(c.id, c.declaringId),
      d = o(u);
    if (!d) {
      if (!a.has(u)) (a.add(u), i.push(u));
      continue;
    }
    if (a.has(d.source)) continue;
    (a.add(d.source), s.push(d.source));
    for (let p of d.manifest.dependencies ?? [])
      l.push({ id: p, declaringId: d.source });
  }
  return { closure: s, missing: i };
}
var UJ,
  tBn = 1024,
  Woa = 4096,
  Mao = 200,
  Kup;
var AEe = E(() => {
  We();
  fr();
  Qn();
  eg();
  UJ = D(k4(), 1);
  Kup = /[\x00-\x08\x0b-\x1f\x7f]/g;
});
var Bdt,
  lx = "claude-plugins-official";
var Rqe = E(() => {
  Bdt = { source: "github", repo: "anthropics/claude-plugins-official" };
});
function Xup(e) {
  let t,
    n = /^[^@/]+@([^:/]+):/.exec(e);
  if (n) t = n[1];
  else
    try {
      t = new URL(e).hostname;
    } catch {
      return "unknown";
    }
  let r = t.toLowerCase();
  return Yup.has(r) ? r : "other";
}
function Jup(e) {
  return e.includes(
