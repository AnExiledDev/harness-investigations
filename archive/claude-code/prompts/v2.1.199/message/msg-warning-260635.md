---
id: msg-warning-260635
name: Warning Message
category: message
subcategory: warning
source_line: 260635
---

);
    return;
  }
}
function Cbp() {
  let e = Wt();
  if (e !== "linux" && e !== "wsl") return [];
  try {
    if (!$De()) return [];
    let n = ts()?.permissions || {},
      r = [],
      o = (s) => {
        let i = s.replace(/\/\*\*$/, "");
        return /[*?[\]]/.test(i);
      };
    for (let s of [...(n.allow || []), ...(n.deny || [])]) {
      let i = aVe(s);
      if (
        (i.toolName === Aa || i.toolName === Os) &&
        i.ruleContent &&
        o(i.ruleContent)
      )
        r.push(s);
    }
    return r;
  } catch (t) {
    return (T(
