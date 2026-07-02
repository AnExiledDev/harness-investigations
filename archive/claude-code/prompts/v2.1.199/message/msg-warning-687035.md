---
id: msg-warning-687035
name: Warning Message
category: message
subcategory: warning
source_line: 687035
---

],
      };
    let r = [],
      o = Inn(e.branches);
    if (o.length > 0) r.push({ field: "ref", op: "in", values: o });
    let s = Inn(e.paths);
    if (s.length > 0) r.push({ field: "paths", op: "glob_any", values: s });
    let i = Inn(e.labels);
    if (i.length > 0) r.push({ field: "labels", op: "in", values: i });
    if (typeof e.channel === "string" && e.channel.trim() !== "")
      r.push({ field: "channel", op: "eq", values: [Gum(e.channel)] });
    r.push(...Oum(e.where, t));
    for (let a of hzo(e.filter)) {
      let l = jum(a);
      if (l) r.push(l);
    }
    return { trigger: Cnn(n, r), warnings: t };
  }
  return {
    trigger: null,
    warnings: ["on: entry must be a string or {event: ...} mapping"],
  };
}
function Oum(e, t) {
  if (e === void 0) return [];
  if (Array.isArray(e)) {
    let n = [];
    for (let r of e) {
      if (!xnn(r) || Object.keys(r).length !== 1) {
        t.push(
          "where: list element must be a single-field map {field: predicate}",
        );
        continue;
      }
      n.push(...Yuc(r, t));
    }
    return n;
  }
  if (xnn(e)) return Yuc(e, t);
  return (
    t.push(
      "where: must be a map of field\u2192predicate, or a list of single-field maps",
    ),
    []
  );
}
function Yuc(e, t) {
  let n = [];
  for (let [r, o] of Object.entries(e))
    if (o === null || o === void 0)
      t.push(
