---
id: msg-warning-131626
name: Warning Message
category: message
subcategory: warning
source_line: 131626
---

);
    return;
  }
}
function jZu(e, t) {
  try {
    if (
      (e.setStatus({ status: "error", error: aSn(t) ? t : void 0 }),
      HLt(t) && t.statusCode)
    )
      e.setAttribute("http.status_code", t.statusCode);
    e.end();
  } catch (n) {
    Zge.warning(
