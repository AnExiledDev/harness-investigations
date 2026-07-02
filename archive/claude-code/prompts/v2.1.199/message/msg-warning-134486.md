---
id: msg-warning-134486
name: Warning Message
category: message
subcategory: warning
source_line: 134486
---

);
    return;
  }
}
function hLd(e, t) {
  try {
    if (
      (e.setStatus({ status: "error", error: dxn(t) ? t : void 0 }),
      NNt(t) && t.statusCode)
    )
      e.setAttribute("http.status_code", t.statusCode);
    e.end();
  } catch (n) {
    bbe.warning(
