---
id: msg-warning-266725
name: Warning Message
category: message
subcategory: warning
source_line: 266725
---

;
}
function $Yi() {
  let e = [SQr.join(Ec(), ".claude", "loop.md"), SQr.join(nr(), "loop.md")];
  for (let t of e) {
    let n;
    try {
      n = LYi.readFileSync(t, "utf-8");
    } catch (o) {
      if (Vo(o) || an(o) === "EISDIR") continue;
      throw o;
    }
    let r = n.trim();
    if (r.length === 0) continue;
    return { path: t, content: vVd(r) };
  }
  return null;
}
function wQr(e) {
  return e === MYi || e === xBt;
}
function OYi(e) {
  if (!wQr(e)) return null;
  if (!TQr()) return null;
  let t = e === xBt,
    n = $Yi();
  if (n) {
    let o = t ? AVd() : HVd();
    if (Yit === n.content) return o;
    return (
      (Yit = n.content),
      
