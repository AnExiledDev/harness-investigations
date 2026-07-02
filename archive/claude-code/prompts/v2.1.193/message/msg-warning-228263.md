---
id: msg-warning-228263
name: Warning Message
category: message
subcategory: warning
source_line: 228263
---

;
}
function wGi(e, t) {
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
    let u = mM(c.id, c.declaringId),
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
var a7,
  L0n = 1024,
  yGi = 4096,
  lYr = 200,
  KNd;
var Jye = E(() => {
  Ge();
  gr();
  lr();
  _g();
  a7 = L(K2(), 1);
  KNd = /[\x00-\x08\x0b-\x1f\x7f]/g;
});
var Ust,
  KC = "claude-plugins-official";
var $4e = E(() => {
  Ust = { source: "github", repo: "anthropics/claude-plugins-official" };
});
function XNd(e) {
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
  return YNd.has(r) ? r : "other";
}
function JNd(e) {
  return e.includes(
