---
id: msg-warning-895312
name: Warning Message
category: message
subcategory: warning
source_line: 895312
---

);
}
async function T9(e) {
  (await Promise.race([
    Promise.all([ySe(), wSe()]),
    $n(500, void 0, { unref: !0 }),
  ]).catch(() => {}),
    process.exit(e));
}
async function oZm(e) {
  if ((await Jlt(), e.includes("--help") || e.includes("-h"))) {
    if (!ESe()) return wRe("daemon");
    s_(uru());
    return;
  }
  let t = mru(e),
    { jsonPath: n, logPath: r, origin: o, spawnedBy: s, rest: i } = t,
    a = t.sub === "hub" && !Rue() ? "status" : t.sub;
  if (!tZm.has(a)) {
    let l = await Jgr();
    if (l)
      (process.stderr.write(
