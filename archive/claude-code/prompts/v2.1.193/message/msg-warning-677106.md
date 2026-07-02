---
id: msg-warning-677106
name: Warning Message
category: message
subcategory: warning
source_line: 677106
---

],
      };
    let r = [],
      o = h7t(e.branches);
    if (o.length > 0) r.push({ field: "ref", op: "in", values: o });
    let s = h7t(e.paths);
    if (s.length > 0) r.push({ field: "paths", op: "glob_any", values: s });
    let i = h7t(e.labels);
    if (i.length > 0) r.push({ field: "labels", op: "in", values: i });
    if (typeof e.channel === "string" && e.channel.trim() !== "")
      r.push({ field: "channel", op: "eq", values: [XUf(e.channel)] });
    r.push(...WUf(e.where, t));
    for (let a of FFo(e.filter)) {
      let l = YUf(a);
      if (l) r.push(l);
    }
    return { trigger: g7t(n, r), warnings: t };
  }
  return {
    trigger: null,
    warnings: ["on: entry must be a string or {event: ...} mapping"],
  };
}
function WUf(e, t) {
  if (e === void 0) return [];
  if (Array.isArray(e)) {
    let n = [];
    for (let r of e) {
      if (!y7t(r) || Object.keys(r).length !== 1) {
        t.push(
          "where: list element must be a single-field map {field: predicate}",
        );
        continue;
      }
      n.push(...kKl(r, t));
    }
    return n;
  }
  if (y7t(e)) return kKl(e, t);
  return (
    t.push(
      "where: must be a map of field\u2192predicate, or a list of single-field maps",
    ),
    []
  );
}
function kKl(e, t) {
  let n = [];
  for (let [r, o] of Object.entries(e))
    if (o === null || o === void 0)
      t.push(
