---
id: msg-warning-639234
name: Warning Message
category: message
subcategory: warning
source_line: 639234
---

 : M,
      pluginId: e,
      newVersion: _,
      oldVersion: c,
      scope: s,
    };
  } finally {
    let I = bB(e, _);
    if (S && y !== I && !Qie.resolve(I).startsWith(Qie.resolve(y) + Qie.sep))
      await l.rm(y, { recursive: !0, force: !0 });
  }
}
var Qie, wvt, HD, vBe, LXe;
var Pvt = E(() => {
  dt();
  Rdt();
  We();
  gn();
  ut();
  vs();
  Cu();
  RV();
  AEe();
  gx();
  vE();
  ABe();
  Y$();
  eg();
  Bie();
  Bh();
  vq();
  mx();
  kXe();
  hZt();
  Ov();
  fr();
  Qn();
  j6();
  ((Qie = require("path")), (wvt = D(k4(), 1)));
  ((HD = ["user", "project", "local"]),
    (vBe = { user: 0, project: 1, local: 2 }),
    (LXe = ["user", "project", "local", "managed"]));
});
function T7l(e) {
  if (((Gcr = e), Zen !== null)) (e(Zen.updated, Zen.blocked), (Zen = null));
  return () => {
    Gcr = null;
  };
}
async function CXf() {
  let e = await hm(),
    t = r3(),
    n = new Set();
  for (let [r, o] of Object.entries(e)) {
    if (!DH(o.source)) continue;
    if (b_e(r, o, t[r]?.autoUpdate)) n.add(r.toLowerCase());
  }
  return n;
}
async function IXf(e, t, n) {
  let r = !1,
    o = !1,
    s = null;
  for (let { scope: i } of t)
    try {
      let a = await Dvt(e, i);
      if (a.success && !a.alreadyUpToDate && !a.skipped)
        ((r = !0),
          T(
            
