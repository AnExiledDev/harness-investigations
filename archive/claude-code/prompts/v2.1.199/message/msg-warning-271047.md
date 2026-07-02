---
id: msg-warning-271047
name: Warning Message
category: message
subcategory: warning
source_line: 271047
---

;
}
function Sga() {
  let e = [opo.join(ol(), ".claude", "loop.md"), opo.join(tr(), "loop.md")];
  for (let t of e) {
    let n;
    try {
      n = hga.readFileSync(t, "utf-8");
    } catch (o) {
      if (Do(o) || rn(o) === "EISDIR") continue;
      throw o;
    }
    let r = n.trim();
    if (r.length === 0) continue;
    return { path: t, content: IEp(r) };
  }
  return null;
}
function upo(e) {
  return e === bga || e === oWt;
}
function Ega(e) {
  if (!upo(e)) return null;
  if (!lpo()) return null;
  let t = e === oWt,
    n = Sga();
  if (n) {
    let o = t ? wEp() : vEp();
    if (qpt === n.content) return o;
    return (
      (qpt = n.content),
      
