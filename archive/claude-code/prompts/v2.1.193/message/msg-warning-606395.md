---
id: msg-warning-606395
name: Warning Message
category: message
subcategory: warning
source_line: 606395
---

 : O,
      pluginId: e,
      newVersion: b,
      oldVersion: c,
      scope: s,
    };
  } finally {
    let C = rN(e, b);
    if (S && y !== C && !loe.resolve(C).startsWith(loe.resolve(y) + loe.sep))
      await l.rm(y, { recursive: !0, force: !0 });
  }
}
var loe, abt, _L, d$e, g6e;
var gbt = E(() => {
  ut();
  Pst();
  Ge();
  un();
  St();
  bs();
  Tu();
  C5();
  Jye();
  Gx();
  OS();
  l$e();
  s1();
  _g();
  epe();
  Dh();
  pW();
  lI();
  f6e();
  E6t();
  ax();
  gr();
  lr();
  A9();
  ((loe = require("path")), (abt = L(K2(), 1)));
  ((_L = ["user", "project", "local"]),
    (d$e = { user: 0, project: 1, local: 2 }),
    (g6e = ["user", "project", "local", "managed"]));
});
function JDl(e) {
  if (((GQn = e), eKt !== null)) (e(eKt.updated, eKt.blocked), (eKt = null));
  return () => {
    GQn = null;
  };
}
async function cAf() {
  let e = await qf(),
    t = A4(),
    n = new Set();
  for (let [r, o] of Object.entries(e)) {
    if (!XH(o.source)) continue;
    if (ege(r, o, t[r]?.autoUpdate)) n.add(r.toLowerCase());
  }
  return n;
}
async function uAf(e, t, n) {
  let r = !1,
    o = !1,
    s = null;
  for (let { scope: i } of t)
    try {
      let a = await mbt(e, i);
      if (a.success && !a.alreadyUpToDate && !a.skipped)
        ((r = !0),
          T(
            
