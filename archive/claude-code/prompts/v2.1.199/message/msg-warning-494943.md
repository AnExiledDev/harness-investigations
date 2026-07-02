---
id: msg-warning-494943
name: Warning Message
category: message
subcategory: warning
source_line: 494943
---


    );
  }
  return null;
}
function PZn(e) {
  for (let t = e.length - 1; t >= 0; t--) {
    let n = e[t];
    if (n.type !== "assistant") continue;
    if (n.isApiErrorMessage) continue;
    let r = _l(
      n.message.content,
      
