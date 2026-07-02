---
id: msg-warning-370945
name: Warning Message
category: message
subcategory: warning
source_line: 370945
---

, { level: "warn" });
  let l = ts().pluginConfigs?.[e]?.options ?? {},
    c = Object.keys(l).filter((u) => s.has(u));
  if (Object.keys(r).length > 0 || c.length > 0) {
    let u = Object.fromEntries(c.map((p) => [p, void 0])),
      d = await Qo("userSettings", {
        pluginConfigs: { [e]: { options: { ...r, ...u } } },
      });
    if (d.error)
      throw (
        T(
          
