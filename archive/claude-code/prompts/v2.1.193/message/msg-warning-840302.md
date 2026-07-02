---
id: msg-warning-840302
name: Warning Message
category: message
subcategory: warning
source_line: 840302
---

);
}
async function mV(e) {
  (await Promise.race([
    Promise.all([zhe(), nye()]),
    Nn(500, void 0, { unref: !0 }),
  ]).catch(() => {}),
    process.exit(e));
}
async function qym(e) {
  if ((await art(), e.includes("--help") || e.includes("-h"))) {
    if (!Xhe()) return xIe("daemon");
    Dy(NDc());
    return;
  }
  let t = jDc(e),
    { jsonPath: n, logPath: r, origin: o, spawnedBy: s, rest: i } = t,
    a = t.sub === "hub" && !Nae() ? "status" : t.sub;
  if (!Gym.has(a)) {
    let l = await Jor();
    if (l)
      (process.stderr.write(
